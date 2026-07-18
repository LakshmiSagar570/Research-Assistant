import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import AsyncSessionLocal
from app.models.orm import User
from sqlalchemy import select
from app.core.security import hash_password


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == 'demo@college.edu'))
        user = result.scalar_one_or_none()
        if user:
            user.password_hash = hash_password('demo1234')
            await db.commit()
            print('updated demo user password hash')
        else:
            print('demo user not found')


asyncio.run(main())
