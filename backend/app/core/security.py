"""
Password hashing and JWT issuance/verification.

Uses the bcrypt library directly rather than through passlib's
CryptContext wrapper. passlib's bcrypt backend reads bcrypt's internal
version string to detect the installed backend, and this detection
breaks against bcrypt>=4.1 (a passlib bug, unfixed upstream) -
producing hashes that passlib then can't verify against, with a
confusing "hash could not be identified" error. Calling bcrypt
directly sidesteps that entirely and is simpler besides.
"""
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
