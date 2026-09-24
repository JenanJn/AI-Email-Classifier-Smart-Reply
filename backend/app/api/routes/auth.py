"""Authentication routes — register and login."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenOut

router = APIRouter()


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check duplicate
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password in thread pool (blocking CPU operation)
    import asyncio
    loop = asyncio.get_event_loop()
    hashed = await loop.run_in_executor(None, hash_password, payload.password)

    user = User(
        email=payload.email,
        name=payload.name,
        hashed_password=hashed,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": user.id})
    return TokenOut(access_token=token, user_id=user.id, name=user.name, email=user.email)


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Run bcrypt verification in thread pool (blocking CPU operation)
    import asyncio
    loop = asyncio.get_event_loop()
    password_ok = await loop.run_in_executor(
        None, verify_password, payload.password, user.hashed_password
    )

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": user.id})
    return TokenOut(access_token=token, user_id=user.id, name=user.name, email=user.email)
