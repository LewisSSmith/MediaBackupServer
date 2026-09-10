import hashlib
import os
import uuid
from datetime import datetime

import bcrypt
from dotenv import load_dotenv
from geoalchemy2 import Geography, WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy import Text, Uuid, Integer, DateTime, JSON, Boolean
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

from dtos import FileDataDTO, LocationDTO
from schemas import UserRegister

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)


class Media(Base):
    __tablename__ = "media"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    filename: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    filetype: Mapped[str] = mapped_column(Text, nullable=False)
    basename: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(Text)
    magic_type: Mapped[str] = mapped_column(Text)
    size: Mapped[int] = mapped_column(Integer)
    date_uploaded: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    date_last_modified: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    file_metadata: Mapped[dict] = mapped_column(JSON)
    naturally_viewable: Mapped[bool] = mapped_column(Boolean)
    viewable_name: Mapped[str] = mapped_column(Text)
    location: Mapped[WKBElement] = mapped_column(Geography(geometry_type="POINT", srid=4326))


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password, bcrypt.gensalt())


async def get_user_by_username_and_password(db: AsyncSession, username: str, password: str) -> User | None:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    
    if bcrypt.checkpw(password, user.password_hash):
        return None
    return user


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserRegister) -> User:
    user = User(
        id=uuid.uuid4(),
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_basename_by_id(db: AsyncSession, user_id: uuid.UUID, file_id: uuid.UUID) -> str | None:
    result = await db.execute(select(Media.basename).where(Media.id == file_id, Media.owner_id == user_id))
    return result.scalar_one_or_none()


async def get_path_by_id(db: AsyncSession, user_id: uuid.UUID, file_id: uuid.UUID) -> str | None:
    result = await db.execute(select(Media.basename, Media.filetype).where(Media.id == file_id, Media.owner_id == user_id))
    result = result.one_or_none()
    return result.basename + result.filetype


async def get_view_data_by_id(db: AsyncSession, user_id: uuid.UUID, file_id: uuid.UUID) -> str | None:
    result = await db.execute(select(Media.viewable_name, Media.naturally_viewable).where(Media.id == file_id, Media.owner_id == user_id))
    result = result.one_or_none()
    return result


async def get_filename_by_id(db: AsyncSession, user_id: uuid.UUID, file_id: uuid.UUID) -> str | None:
    result = await db.execute(select(Media.filename).where(Media.id == file_id, Media.owner_id == user_id))
    return result.scalar_one_or_none()


async def get_file_data(db: AsyncSession, user_id: uuid.UUID, limit : int, sort_by: str, sort_direction: str) -> list[FileDataDTO]:
    if sort_by == "uploaded":
        order = Media.date_uploaded
    elif sort_by == "created":
        order = Media.date_created
    elif sort_by == "last_modified":
        order = Media.date_last_modified
    elif sort_by == "size":
        order = Media.size
    else:
        order = Media.date_uploaded

    if sort_direction == "asc":
        order = order.asc()
    else:
        order = order.desc()

    rows = await db.execute(select(
        Media.id,
        Media.hash,
        Media.filename,
        Media.mime_type,
        Media.size,
        Media.date_uploaded,
        Media.file_metadata,
        Media.date_created,
        Media.date_last_modified,
    ).where(Media.owner_id == user_id).order_by(order))

    results = [
        FileDataDTO(
            id=row.id,
            hash=row.hash,
            filename=row.filename,
            mime=row.mime_type,
            size=row.size,
            date_uploaded=row.date_uploaded,
            date_created=row.date_created,
            date_last_modified=row.date_last_modified,
            metadata=row.file_metadata,
        )
        for row in rows
    ]

    return results


async def get_file_data_single(db: AsyncSession, user_id: uuid.UUID) -> FileDataDTO:
    row = await db.execute(select(
        Media.id,
        Media.hash,
        Media.filename,
        Media.mime_type,
        Media.size,
        Media.date_uploaded,
        Media.file_metadata,
        Media.date_created,
        Media.date_last_modified,
    ).where(Media.owner_id == user_id))

    row = row.one_or_none()

    result = FileDataDTO(
        id=row.id,
        hash=row.hash,
        filename=row.filename,
        mime=row.mime_type,
        size=row.size,
        date_uploaded=row.date_uploaded,
        date_created=row.date_created,
        date_last_modified=row.date_last_modified,
        metadata=row.file_metadata,
        #date_created=row.date_created,
    )

    return result


async def get_locations(db: AsyncSession, user_id: uuid.UUID)-> list[LocationDTO]:
    rows = await db.execute(select(
        Media.id,
        Media.location,
    ).where(Media.owner_id == user_id, Media.location.is_not(None)))

    results = [
        LocationDTO(
            id=row.id,
            latitude=shape.y,
            longitude=shape.x,
        )
        for row in rows
        if (shape := to_shape(row.location))
    ]

    return results

