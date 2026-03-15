"""Authentication and user management endpoints."""

from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User, Role
from backend.schemas import UserCreate, UserOut, TokenResponse, RoleOut
from backend.services.auth_service import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# ─── Extra schemas (inline to avoid touching shared schemas file) ──
class UserAdminOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    role_id: int
    role_name: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdateAdmin(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None


class UserStatusUpdate(BaseModel):
    is_active: bool


# ─── Role guard helper ────────────────────────────────────────────
def require_roles(*role_names: str):
    def _dep(current_user: User = Depends(lambda token=Depends(oauth2_scheme), db=Depends(get_db): _get_user(token, db))):
        if current_user.role.name not in role_names:
            raise HTTPException(403, f"Requires one of: {', '.join(role_names)}")
        return current_user
    return _dep


def _get_user(token: str, db: Session) -> User:
    if not token:
        raise HTTPException(401, "Not authenticated")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:  # noqa: E302
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
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
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(403, "Account disabled")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    token = create_access_token({"sub": str(user.id), "role": user.role.name})
    return TokenResponse(
        access_token=token, user_id=user.id,
        username=user.username, role=user.role.name,
    )


@router.get("/me", response_model=UserAdminOut)
def me(user: User = Depends(get_current_user)):
    return _user_to_admin_out(user)


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


# ─── User management (admin / manager) ───────────────────────────

def _user_to_admin_out(u: User) -> dict:
    return {
        "id": u.id, "username": u.username, "email": u.email,
        "full_name": u.full_name, "phone": u.phone,
        "role_id": u.role_id, "role_name": u.role.name if u.role else None,
        "is_active": u.is_active, "created_at": u.created_at,
    }


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
    """Admin / Manager creates a user and can assign any role."""
    if current_user.role.name not in ("admin", "manager"):
        raise HTTPException(403, "Admin or Manager role required")
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
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
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
    db.commit()
    db.refresh(user)
    return _user_to_admin_out(user)
