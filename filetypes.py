supported_images = [".jpg", ".jpeg", ".dng"]
supported_videos = [".mp4"]

supported_image_mimes = ["image/jpeg"]
supported_video_mimes = ["video/mp4"]


def is_supported(mime: str, extension: str) -> bool:
    if extension:
        return extension in supported_images + supported_videos
    elif mime:
        return mime in supported_image_mimes + supported_video_mimes
    else:
        return False


def is_image(mime: str) -> bool:
    kind, subtype = mime.split("/")
    return kind == "image"


def is_video(mime: str) -> bool:
    kind, subtype = mime.split("/")
    return kind == "video"

