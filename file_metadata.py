import json
import subprocess
from datetime import datetime

image_ext = [".jpg", ".jpeg", ".dng"]
video_ext = [".mp4"]


def get_metadata(path: str, ext: str) -> dict:
    meta = {}

    if ext:
        if ext in image_ext:
            meta = get_image_metadata(path)
        elif ext in video_ext:
            meta = get_video_metadata(path)

    return meta


def get_gps_metadata(path: str) -> dict | None:
    tags = [
        '-GPSLatitude', '-GPSLongitude'
    ]
    result = subprocess.run(
        ['exiftool', '-json', "-n"] + tags + [path],
        capture_output=True, text=True
    )

    data = json.loads(result.stdout)[0]

    latitude = data.get("GPSLatitude")
    longitude = data.get("GPSLongitude")

    if latitude and longitude:
        location_data = {
            "latitude": latitude,
            "longitude": longitude
        }
    else:
        location_data = None

    return location_data


def get_image_metadata(path: str) -> dict:
    meta = {}

    tags = [
        '-DateTimeOriginal', '-CreateDate',
        '-Make', '-Model', '-LensModel',
        '-ExposureTime', '-FNumber', '-ISO', '-FocalLength',
        '-ImageWidth', '-ImageHeight',
        '-GPSLatitude', '-GPSLongitude',
        '-Orientation'
    ]
    result = subprocess.run(
        ['exiftool', '-json', path],
        capture_output=True, text=True
    )

    data = json.loads(result.stdout)[0]
    data.pop("SourceFile") # remove any information about the local storage of the file on the server

    date_created = data.get("DateTimeOriginal")
    if date_created:
        date_created = datetime.strptime(date_created, "%Y:%m:%d %H:%M:%S")

    meta["date_created"] = date_created
    meta["gps"] = get_gps_metadata(path)
    meta["data"] = data

    return meta


def get_video_metadata(video_path: str) -> dict:
    meta = {}

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ],
        capture_output=True,
        text=True
    )

    data = json.loads(result.stdout)
    meta["data"] = data

    return meta

