from pathlib import Path
import uuid

from fastapi import Depends, UploadFile, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

import media_manager
from endpoints.models import Message
from auth import get_current_user
from database import get_db, get_path_by_id, get_view_data_by_id, get_basename_by_id, get_file_data, \
    get_file_data_single, User


router = APIRouter(
    tags=["Media"],
)

UNAUTHORIZED_RESPONSE = {401: {"model": Message, "description": "Unauthorized"}}
FILE_NOT_FOUND_RESPONSE = {404: {"model": Message, "description": "File not found"}}
UNSUPPORTED_MEDIA_TYPE_RESPONSE = {415: {"model": Message, "description": "Unsupported media type"}}

FILE_NOT_FOUND_EXCEPTION = HTTPException(status_code=404, detail="File not found")

ORIGINALS_PATH = Path("uploads") / "originals"
VIEWABLES_PATH = Path("uploads") / "viewables"
THUMBNAILS_PATH = Path("uploads") / "thumbnails"

THUMBNAIL_EXTENSION = ".jpg"


@router.post("/upload",
             responses={**UNAUTHORIZED_RESPONSE, **UNSUPPORTED_MEDIA_TYPE_RESPONSE})
async def upload(file: UploadFile, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await media_manager.upload_media(db, file, current_user.id)


@router.get("/download/{file_id}",
            response_class=FileResponse,
            responses={**UNAUTHORIZED_RESPONSE, **FILE_NOT_FOUND_RESPONSE})
async def download_file(file_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_path = await get_path_by_id(db, current_user.id, file_id)
    if not file_path:
        raise FILE_NOT_FOUND_EXCEPTION

    path_to_file = ORIGINALS_PATH / file_path
    return FileResponse(path_to_file)


@router.get("/media/{file_id}",
            response_class=FileResponse,
            responses={**UNAUTHORIZED_RESPONSE, **FILE_NOT_FOUND_RESPONSE})
async def view_file(file_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    filename, naturally_viewable = await get_view_data_by_id(db, current_user.id, file_id)

    if not filename:
        raise FILE_NOT_FOUND_EXCEPTION

    if naturally_viewable:
        path_to_file = ORIGINALS_PATH / filename
    else:
        path_to_file = VIEWABLES_PATH / filename

    return FileResponse(path_to_file)


@router.get("/thumbnail/{file_id}",
            response_class=FileResponse,
            responses={**UNAUTHORIZED_RESPONSE, **FILE_NOT_FOUND_RESPONSE})
async def view_thumbnail(file_id, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    basename = await get_basename_by_id(db, current_user.id, file_id)
    if not basename:
        raise FILE_NOT_FOUND_EXCEPTION

    path_to_file = (THUMBNAILS_PATH / basename).with_suffix(THUMBNAIL_EXTENSION)
    if path_to_file.is_file():
        return FileResponse(path_to_file)
    else:
        raise FILE_NOT_FOUND_EXCEPTION


@router.delete("/delete/{file_id}",
               status_code=204,
               responses={**UNAUTHORIZED_RESPONSE, **FILE_NOT_FOUND_RESPONSE})
async def delete_file(file_id, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await media_manager.delete_media(db, current_user.id, file_id)


@router.get("/file-request")
async def file_request(limit: int = 10, sort: str = "uploaded", direction: str = "asc", db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_file_data(db, current_user.id, limit, sort, direction)


@router.get("/file-request/{file_id}")
async def file_request(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_file_data_single(db, current_user.id)


@router.get("/locations")
async def get_locations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_locations(db, current_user.id)

