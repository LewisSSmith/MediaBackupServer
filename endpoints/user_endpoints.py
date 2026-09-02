from typing import Annotated

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from endpoints.models import Message
from auth import create_access_token
from database import get_db, get_user_by_username, get_user_by_email, create_user, get_user_by_username_and_password
from schemas import UserRegister, TokenResponse

router = APIRouter(
    tags=["User"],
)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, responses={400: {"model": Message, "description": "Credentials already taken"}})
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):
    if await get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if await get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, user)
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse, responses={401: {"model": Message, "description": "Invalid credentials"}})
async def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username_and_password(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)

