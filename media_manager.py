import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

import PIL.Image
import magic
import rawpy
from PIL import Image
from geoalchemy2 import WKTElement

import file_metadata
import thumbnail
from filetypes import is_image, is_video, is_supported

PIL.Image.MAX_IMAGE_PIXELS = 199756800 #REMOVE THIS BEFORE PRODUCTION
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import Media

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ORIGINAL_DIR = UPLOAD_DIR / "originals"
ORIGINAL_DIR.mkdir(exist_ok=True)
THUMBNAIL_DIR = UPLOAD_DIR / "thumbnails"
THUMBNAIL_DIR.mkdir(exist_ok=True)
VIEWABLES_DIR = UPLOAD_DIR / "viewables"
VIEWABLES_DIR.mkdir(exist_ok=True)

viewable_mimes = {"image/jpg", "image/jpeg", "image/png", "video/mp4"}

def sha256_file(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def save_raw_thumbnail(path: str, output: str):
    try:
        with rawpy.imread(path) as raw:
            try:
                print("extracting thumbnail")
                thumb = raw.extract_thumb()

                if thumb.format == rawpy.ThumbFormat.JPEG:
                    print("saving as jpeg")
                    with open(output, "wb") as f:
                        f.write(thumb.data)

                elif thumb.format == rawpy.ThumbFormat.BITMAP:
                    print("saving as bmp")
                    Image.fromarray(thumb.data).save(output)

                return output

            except rawpy.LibRawNoThumbnailError:
                print("no thumbnail")
                rgb = raw.postprocess()
                Image.fromarray(rgb).save(output)
                return output

    except rawpy.LibRawFileUnsupportedError:
        return None

async def upload_media(db: AsyncSession, data: UploadFile, user_id: uuid.UUID):
    #TODO add logic to prevent storing same file twice

    # --- SAVE FILE TO DISK ---
    ext = Path(data.filename).suffix

    if not is_supported(data.content_type, ext):
        if ext:
            msg = ext
        elif data.content_type:
            msg = data.content_type
        else:
            msg = "Unknown"
        raise HTTPException(status_code=415, detail="Unsupported file type '{}'".format(msg))

    basename = str(uuid.uuid4())
    path = ORIGINAL_DIR / (basename + ext)

    with open(path, "wb") as f:
        while chunk := await data.read(1024 * 1024):  # 1 MB chunks
            f.write(chunk)

    await data.close()

    magic_type = magic.from_file(str(path), mime=True)

    if magic_type not in viewable_mimes:
        # --- SAVE VIEWABLE FORMAT ---
        naturally_viewable = False
        viewable_name = basename + ".jpg"
        output_path = VIEWABLES_DIR / viewable_name

        try:
            image = Image.open(path)
            image.convert("RGB")
            image.save(output_path)
            success = True
        except Exception:
            result = save_raw_thumbnail(str(path), str(output_path))
            if result:
                success = True
            else:
                success = False

        if not success:
            viewable_name = None
    else:
        naturally_viewable = True
        viewable_name = basename + ext


    # --- SAVE METADATA ---
    meta = file_metadata.get_metadata(str(path), ext)
    date_created = meta.get("date_created")
    date_last_modified = meta.get("date_last_modified")

    location_data = meta.get("gps")
    if location_data:
        location_point = WKTElement(f"POINT({location_data['longitude']} {location_data['latitude']})", srid=4326)
    else:
        print("no location info")
        location_point = None

    # --- SAVE THUMBNAIL ---
    thumbnail_path = (THUMBNAIL_DIR / basename).with_suffix(".jpg")
    if is_image(magic_type):
        thumbnail_saved = thumbnail.save_image(str(path), str(thumbnail_path))
    elif is_video(magic_type):
        thumbnail_saved = thumbnail.save_video(str(path), str(thumbnail_path))
    else:
        print("Unsupported file type for generating thumbnail")
        thumbnail_saved = False

    if thumbnail_saved:
        print("saved thumbnail")
    else:
        print("failed to save thumbnail")

    # --- SAVE TO DATABASE ---
    file = Media(
        id=uuid.uuid4(),
        owner_id=user_id,
        filename=data.filename,
        hash=sha256_file(path),
        filetype=ext,
        basename=basename,
        mime_type=data.content_type,
        magic_type=magic_type,
        size=data.size,
        date_uploaded=datetime.now(timezone.utc),
        date_created=date_created,
        date_last_modified=date_last_modified,
        file_metadata=meta.get("data"),
        naturally_viewable=naturally_viewable,
        viewable_name=viewable_name,
        location=location_point,
    )
    db.add(file)
    await db.commit()


async def delete_media(db: AsyncSession, user_id: uuid.UUID, file_id: uuid.UUID):
    result = (await db.execute(select(Media).where(Media.id == file_id, Media.owner_id == user_id))).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="File not found")

    # --- DELETE THUMBNAIL ---
    thumbnail_path = THUMBNAIL_DIR / (result.basename + ".jpg")
    thumbnail_path.unlink()
    # --- DELETE ORIGINAL ---
    original_path = ORIGINAL_DIR / (result.basename + result.filetype)
    original_path.unlink()

    await db.delete(result)
    await db.commit()

