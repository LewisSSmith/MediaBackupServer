import uuid

from pydantic import BaseModel, field_validator


# --- User Schemas ---

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str

    model_config = {"from_attributes": True}


class FileDataResponse(BaseModel):
    limit: int | None = 10
    sort: str | None = "data_asc"

