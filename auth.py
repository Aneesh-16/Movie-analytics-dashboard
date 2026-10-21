"""Editor authentication: scrypt password hashes + HMAC-signed, expiring bearer tokens (standard library only)."""
import base64
import hashlib
import hmac
import json
import os
import time
from typing import NamedTuple

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from config import SECRET_KEY, TOKEN_TTL_SECONDS
from database import get_session
from models import AppUser, Editor

bearer = HTTPBearer(auto_error=False)   # also gives Swagger an "Authorize" button


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, digest = stored.split("$")
        test = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2 ** 14, r=8, p=1, dklen=32)
        return hmac.compare_digest(test.hex(), digest)
    except ValueError:
        return False


def _sign(payload: str) -> str:
    return hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()


class Principal(NamedTuple):
    username: str
    role: str            # "editor" (may edit the catalogue) or "user" (interactions only)


def make_token(username: str, role: str = "editor") -> str:
    payload = {"u": username, "r": role, "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    return f"{body}.{_sign(body)}"


def read_token(token: str) -> tuple[str, str] | None:
    """Return (username, role) if the token is genuine and not expired, else None."""
    try:
        body, sig = token.split(".")
        if not hmac.compare_digest(sig, _sign(body)):
            return None
        data = json.loads(base64.urlsafe_b64decode(body))
        return (data["u"], data.get("r", "editor")) if data["exp"] > time.time() else None
    except (ValueError, KeyError, TypeError):
        return None


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer),
                 session: Session = Depends(get_session)) -> Principal:
    """Any logged-in account (editor or registered user)."""
    if creds is not None:
        parsed = read_token(creds.credentials)
        if parsed:
            username, role = parsed
            model = Editor if role == "editor" else AppUser
            if session.scalar(select(model.id).where(model.username == username)) is not None:
                return Principal(username, role)
    raise HTTPException(401, "Login required" if creds is None else "Invalid or expired token",
                        headers={"WWW-Authenticate": "Bearer"})


def current_editor(user: Principal = Depends(current_user)) -> Principal:
    """Protects catalogue writes and exports: editors only."""
    if user.role != "editor":
        raise HTTPException(403, "Editor permission required")
    return user
