from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import LoginRequest, TokenResponse, RegisterRequest
from app.schemas.user import UserOut
from app.core.security import verify_password, hash_password, create_access_token
from app.services.activity_service import log_activity


router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == payload.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        payload.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.name
    })

    log_activity(
        db,
        user.id,
        "LOGIN",
        f"{user.email} logged in"
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.name,
        user_id=user.id,
        name=user.name
    )



@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    # Check whether email already exists
    existing = db.query(User).filter(
        User.email == payload.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Find role
    role = db.query(Role).filter(
        Role.name == payload.role
    ).first()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown role '{payload.role}'"
        )

    # Create user
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=role.id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        role=role.name
    )



@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return [
        UserOut(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role.name
        )
        for u in users
    ]