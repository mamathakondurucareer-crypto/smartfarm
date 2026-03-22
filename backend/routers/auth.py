"""Authentication and user management endpoints."""

import time
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database import get_db
from backend.models.user import User, Role
from backend.schemas import UserCreate, UserOut, TokenResponse, RoleOut
from backend.services.activity_log_service import log_activity
from backend.services.auth_service import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    decode_token,
)

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# ── Brute-force protection (in-memory, per IP) ─────────────────────────────
_failed: dict[str, list[float]] = defaultdict(list)
_failed_lock = Lock()


def _check_lockout(ip: str) -> None:
    now = time.time()
    window = settings.login_lockout_seconds
    with _failed_lock:
        attempts = [t for t in _failed[ip] if now - t < window]
        # Prune expired entries to prevent unbounded dict growth
        if attempts:
            _failed[ip] = attempts
        else:
            _failed.pop(ip, None)
        if len(attempts) >= settings.login_max_attempts:
            wait = int(window - (now - attempts[0]))
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed login attempts. Try again in {wait}s.",
                headers={"Retry-After": str(wait)},
            )


def _record_failure(ip: str) -> None:
    with _failed_lock:
        _failed[ip].append(time.time())


def _clear_failures(ip: str) -> None:
    with _failed_lock:
        _failed.pop(ip, None)


# ── Inline schemas ──────────────────────────────────────────────────────────
class UserAdminOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role_id: int
    role_name: Optional[str] = None
    is_active: bool
    must_change_password: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdateAdmin(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role_id: Optional[int] = None


class UserStatusUpdate(BaseModel):
    is_active: bool


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str
    must_change_password: bool = False


# ── Auth helpers ────────────────────────────────────────────────────────────
def _get_user(token: str, db: Session) -> User:
    if not token:
        raise HTTPException(401, "Not authenticated")
    payload = decode_token(token, expected_type="access")
    if not payload:
        raise HTTPException(401, "Invalid or expired token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    return _get_user(token, db)


def require_roles(*role_names: str):
    def _dep(current_user: User = Depends(get_current_user)):
        if current_user.role.name not in role_names:
            raise HTTPException(403, f"Requires one of: {', '.join(role_names)}")
        return current_user
    return _dep


def _user_to_admin_out(u: User) -> dict:
    return {
        "id": u.id, "username": u.username, "email": u.email,
        "full_name": u.full_name, "phone": u.phone,
        "role_id": u.role_id, "role_name": u.role.name if u.role else None,
        "is_active": u.is_active, "must_change_password": u.must_change_password,
        "created_at": u.created_at,
    }


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        validate_password_strength(data.password)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username already exists")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(400, "Invalid role_id")
    user = User(
        username=data.username, email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name, phone=data.phone, role_id=data.role_id,
    )
    db.add(user)
    log_activity(db, "REGISTER", "auth", username=data.username,
                 description=f"New user '{data.username}' self-registered")
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    _check_lockout(client_ip)

    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        _record_failure(client_ip)
        log_activity(db, "LOGIN_FAILED", "auth", username=form.username,
                     description=f"Failed login attempt for '{form.username}'", ip=client_ip)
        db.commit()
        # Uniform error for both "not found" and "wrong password"
        raise HTTPException(401, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(403, "Account disabled")

    _clear_failures(client_ip)
    user.last_login = datetime.now(timezone.utc)
    log_activity(db, "LOGIN", "auth", username=user.username, user_id=user.id,
                 description=f"User '{user.username}' logged in", ip=client_ip)
    db.commit()

    payload = {"sub": str(user.id), "role": user.role.name}
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        user_id=user.id,
        username=user.username,
        role=user.role.name,
        must_change_password=user.must_change_password,
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token, expected_type="refresh")
    if not payload:
        raise HTTPException(401, "Invalid or expired refresh token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    new_payload = {"sub": str(user.id), "role": user.role.name}
    return TokenPair(
        access_token=create_access_token(new_payload),
        refresh_token=create_refresh_token(new_payload),
        user_id=user.id,
        username=user.username,
        role=user.role.name,
    )


@router.get("/me", response_model=UserAdminOut)
def me(user: User = Depends(get_current_user)):
    return _user_to_admin_out(user)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password", status_code=204)
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")
    try:
        validate_password_strength(body.new_password)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    current_user.hashed_password = hash_password(body.new_password)
    current_user.must_change_password = False
    log_activity(db, "CHANGE_PASSWORD", "auth", username=current_user.username,
                 user_id=current_user.id,
                 description=f"User '{current_user.username}' changed their password")
    db.commit()


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Role).all()


# ── User management (admin / manager) ──────────────────────────────────────

@router.get("/users", response_model=List[UserAdminOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ("admin", "manager"):
        raise HTTPException(403, "Admin or Manager role required")
    users = db.query(User).order_by(User.id).all()
    return [_user_to_admin_out(u) for u in users]


@router.post("/admin/users", response_model=UserAdminOut, status_code=201)
def create_user_admin(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name not in ("admin", "manager"):
        raise HTTPException(403, "Admin or Manager role required")
    try:
        validate_password_strength(data.password)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username already exists")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(400, "Invalid role_id")
    user = User(
        username=data.username, email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name, phone=data.phone, role_id=data.role_id,
    )
    db.add(user)
    log_activity(db, "CREATE_USER", "auth", username=current_user.username,
                 user_id=current_user.id,
                 description=f"Admin '{current_user.username}' created user '{data.username}'")
    db.commit()
    db.refresh(user)
    return _user_to_admin_out(user)


@router.put("/users/{user_id}", response_model=UserAdminOut)
def update_user(
    user_id: int,
    data: UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name != "admin":
        raise HTTPException(403, "Admin role required")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    # Explicitly update only allowed fields — no bulk setattr
    updates = data.model_dump(exclude_none=True)
    if "full_name" in updates:
        user.full_name = updates["full_name"]
    if "email" in updates:
        if db.query(User).filter(User.email == updates["email"], User.id != user_id).first():
            raise HTTPException(400, "Email already in use")
        user.email = updates["email"]
    if "phone" in updates:
        user.phone = updates["phone"]
    if "role_id" in updates:
        role = db.query(Role).filter(Role.id == updates["role_id"]).first()
        if not role:
            raise HTTPException(400, "Invalid role_id")
        user.role_id = updates["role_id"]
    log_activity(db, "UPDATE_USER", "auth", username=current_user.username,
                 user_id=current_user.id, entity_type="User", entity_id=user_id,
                 description=f"Admin '{current_user.username}' updated user '{user.username}'")
    db.commit()
    db.refresh(user)
    return _user_to_admin_out(user)


@router.patch("/users/{user_id}/status", response_model=UserAdminOut)
def set_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.name != "admin":
        raise HTTPException(403, "Admin role required")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.id == current_user.id:
        raise HTTPException(400, "Cannot change your own status")
    user.is_active = data.is_active
    action = "ACTIVATE_USER" if data.is_active else "DEACTIVATE_USER"
    log_activity(db, action, "auth", username=current_user.username,
                 user_id=current_user.id, entity_type="User", entity_id=user_id,
                 description=f"Admin '{current_user.username}' {'activated' if data.is_active else 'deactivated'} user '{user.username}'")
    db.commit()
    db.refresh(user)
    return _user_to_admin_out(user)
