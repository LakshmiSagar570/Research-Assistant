"""
Password hashing and JWT issuance/verification.

Kept intentionally simple (FR7: authentication + roles) - this is a
college-project auth layer, not a hardened production system. It still
does the fundamentals correctly: bcrypt hashing, short-lived signed
tokens, server-side role checks (see core/deps.py).
"""
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from jose import jwt, JWTError

from app.core.config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2_sha256$200000$" + salt.hex() + "$" + digest.hex()


def verify_password(plain: str, hashed: str) -> bool:
    if not hashed.startswith("pbkdf2_sha256$"):
        return False
    try:
        _, iterations, salt_hex, digest_hex = hashed.split("$", 3)
        iterations = int(iterations)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, iterations)
        return secrets.compare_digest(actual, expected)
    except ValueError:
        return False


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
