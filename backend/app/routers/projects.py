"""
Faculty Research Project & Student Management Router.

Enforces role permissions server-side:
  - Faculty/Admin: Create projects, list available students, pull students into research, remove students.
  - Students: View projects they are enrolled in, but rejected with HTTP 403 Forbidden if attempting management actions.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.orm import User, UserRole, ResearchProject, ResearchMember
from app.models.schemas import (
    ResearchProjectCreate,
    ResearchProjectOut,
    AddStudentRequest,
    StudentOut,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ResearchProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ResearchProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.faculty, UserRole.admin)),
):
    """Faculty/Admin only: create a new research project."""
    project = ResearchProject(
        title=payload.title,
        description=payload.description,
        faculty_id=current_user.id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ResearchProjectOut(
        id=project.id,
        title=project.title,
        description=project.description,
        faculty_id=project.faculty_id,
        faculty_name=current_user.name,
        created_at=project.created_at,
        members=[],
    )


@router.get("", response_model=list[ResearchProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List research projects.

    - Faculty: sees projects created by them.
    - Admin: sees all projects.
    - Student: sees projects they have been pulled into by Faculty.
    """
    if current_user.role == UserRole.admin:
        query = select(ResearchProject).options(
            selectinload(ResearchProject.faculty),
            selectinload(ResearchProject.members).selectinload(ResearchMember.student),
        )
    elif current_user.role == UserRole.faculty:
        query = select(ResearchProject).where(
            ResearchProject.faculty_id == current_user.id
        ).options(
            selectinload(ResearchProject.faculty),
            selectinload(ResearchProject.members).selectinload(ResearchMember.student),
        )
    else:  # Student
        query = (
            select(ResearchProject)
            .join(ResearchMember, ResearchMember.project_id == ResearchProject.id)
            .where(ResearchMember.student_id == current_user.id)
            .options(
                selectinload(ResearchProject.faculty),
                selectinload(ResearchProject.members).selectinload(ResearchMember.student),
            )
        )

    result = await db.execute(query)
    projects = result.scalars().all()

    out = []
    for p in projects:
        members_out = [
            StudentOut(id=m.student.id, name=m.student.name, email=m.student.email)
            for m in p.members
            if m.student
        ]
        out.append(
            ResearchProjectOut(
                id=p.id,
                title=p.title,
                description=p.description,
                faculty_id=p.faculty_id,
                faculty_name=p.faculty.name if p.faculty else "Unknown Faculty",
                created_at=p.created_at,
                members=members_out,
            )
        )
    return out


@router.get("/students", response_model=list[StudentOut])
async def list_available_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.faculty, UserRole.admin)),
):
    """Faculty/Admin only: list registered students available to be pulled into research."""
    result = await db.execute(
        select(User).where(User.role == UserRole.student).order_by(User.name)
    )
    students = result.scalars().all()
    return [StudentOut(id=s.id, name=s.name, email=s.email) for s in students]


@router.post("/{project_id}/students", response_model=ResearchProjectOut)
async def add_student_to_project(
    project_id: str,
    payload: AddStudentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.faculty, UserRole.admin)),
):
    """Faculty/Admin only: pull a student into research project by email."""
    # Verify project existence & ownership
    result = await db.execute(
        select(ResearchProject)
        .where(ResearchProject.id == project_id)
        .options(
            selectinload(ResearchProject.faculty),
            selectinload(ResearchProject.members).selectinload(ResearchMember.student),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    if current_user.role != UserRole.admin and project.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this research project")

    # Find target student
    s_result = await db.execute(select(User).where(User.email == payload.student_email))
    student = s_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail=f"No user found with email {payload.student_email}")

    # Check if already a member
    existing = any(m.student_id == student.id for m in project.members)
    if existing:
        raise HTTPException(status_code=400, detail="Student is already added to this research project")

    # Add student to project
    member = ResearchMember(project_id=project.id, student_id=student.id)
    db.add(member)
    await db.commit()

    # Re-fetch project to return updated response
    result = await db.execute(
        select(ResearchProject)
        .where(ResearchProject.id == project_id)
        .options(
            selectinload(ResearchProject.faculty),
            selectinload(ResearchProject.members).selectinload(ResearchMember.student),
        )
    )
    project = result.scalar_one_or_none()

    members_out = [
        StudentOut(id=m.student.id, name=m.student.name, email=m.student.email)
        for m in project.members
        if m.student
    ]

    return ResearchProjectOut(
        id=project.id,
        title=project.title,
        description=project.description,
        faculty_id=project.faculty_id,
        faculty_name=project.faculty.name if project.faculty else "Unknown Faculty",
        created_at=project.created_at,
        members=members_out,
    )


@router.delete("/{project_id}/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_student_from_project(
    project_id: str,
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.faculty, UserRole.admin)),
):
    """Faculty/Admin only: remove a student from research project."""
    result = await db.execute(select(ResearchProject).where(ResearchProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    if current_user.role != UserRole.admin and project.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not own this research project")

    m_result = await db.execute(
        select(ResearchMember).where(
            ResearchMember.project_id == project_id,
            ResearchMember.student_id == student_id,
        )
    )
    member = m_result.scalar_one_or_none()
    if member:
        await db.delete(member)
        await db.commit()
