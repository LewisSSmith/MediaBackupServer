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


def get_date(field: str, data: dict) -> datetime | None:
    date = data.get(field)
    if date:
        try:
            date = datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            print("Unable to parse date:", date)
            date = None

    return date


def get_image_metadata(path: str) -> dict:
    meta = {}

    result = subprocess.run(
        ['exiftool', '-json', path],
        capture_output=True, text=True
    )

    data = json.loads(result.stdout)[0]
    data.pop("SourceFile") # remove any information about the local storage of the file on the server

    meta["date_created"] = get_date("DateTimeOriginal", data)
    meta["date_last_modified"] = get_date("ModifyDate", data)
    meta["gps"] = get_gps_metadata(path)
    meta["data"] = data

    return meta


def get_video_metadata(video_path: str) -> dict:
    meta = {}

    result = subprocess.run(
        ['exiftool', '-json', video_path],
        capture_output=True, text=True
    )

    data = json.loads(result.stdout)[0]
    data.pop("SourceFile")  # remove any information about the local storage of the file on the server

    meta["date_created"] = get_date('MediaCreateDate', data)
    meta["date_last_modified"] = get_date("ModifyDate", data)
    meta["gps"] = get_gps_metadata(video_path)

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

