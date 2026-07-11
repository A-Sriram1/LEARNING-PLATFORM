"""Verifies Supabase-issued JWTs on incoming requests.

Auth itself (signup/login/OAuth) is handled by Supabase Auth on the
frontend. The backend only ever verifies the JWT Supabase already issued --
it never re-implements auth or stores passwords.
"""
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import get_settings

settings = get_settings()
bearer_scheme = HTTPBearer()


class CurrentUser:
    def __init__(self, id: uuid.UUID, email: str, role: str):
        self.id = id
        self.email = email
        self.role = role


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> CurrentUser:
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    return CurrentUser(
        id=uuid.UUID(payload["sub"]),
        email=payload.get("email", ""),
        role=payload.get("user_metadata", {}).get("role", "student"),
    )


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user
