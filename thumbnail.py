import ffmpeg
import rawpy
from PIL import Image, ImageOps

MAX_SIZE = (300, 300) # max reso

# Determines appropriate method of saving thumbnail
# Returns true if saved successfully
def save(path: str, output_path: str, handlers) -> bool:
    """Try each handler in turn; move to the next on failure."""
    for handler in handlers:
        if handler(path, output_path):
            return True

    return False

def save_image(path: str, output_path: str) -> bool:
    return save(path, output_path, image_handlers)

def save_video(path: str, output_path: str) -> bool:
    return save(path, output_path, video_handlers)

def save_image_pil(path, output_path: str) -> bool:
    try:
        image = Image.open(path)
        image = ImageOps.exif_transpose(image)  # fixes rotation

        image.thumbnail(MAX_SIZE)
        image = image.convert("RGB")

        print("saving thumbnail to " + str(output_path))
        image.save(output_path)
        return True
    except Exception as e:
        print("failed saving thumbnail to " + str(output_path))
        print(e)
        return False

def save_raw(path: str, output_path: str) -> bool:
    try:
        with rawpy.imread(path) as raw:
            try:
                print("extracting thumbnail")
                thumb = raw.extract_thumb()

                if thumb.format == rawpy.ThumbFormat.JPEG:
                    print("saving as jpeg")
                    with open(output_path, "wb") as f:
                        f.write(thumb.data)

                elif thumb.format == rawpy.ThumbFormat.BITMAP:
                    print("saving as bmp")
                    Image.fromarray(thumb.data).save(output_path)

                return True

            except rawpy.LibRawNoThumbnailError:
                print("no thumbnail")
                rgb = raw.postprocess()
                Image.fromarray(rgb).save(output_path)
                return True

    except rawpy.LibRawFileUnsupportedError:
        return False

def save_video_ffmpeg(path: str, output_path: str) -> bool:
    try:
        (
            ffmpeg
            .input(str(path))  # seek to timestamp
            .filter("scale", 320, -1)  # -1 preserves aspect ratio
            .output(str(output_path), vframes=1)  # grab 1 frame
            .run(quiet=True)
        )
    except Exception:
        return False

    return True

image_handlers = [save_image_pil, save_raw]
video_handlers = [save_video_ffmpeg]
