# Media Backup Backend

## Overview

The backend is responsible for storing all media files, user accounts and acting as an API for clients.

## Setup (Windows)

Note: Ensure to restart computer if you encounter an issue during setup

1. Clone repository to a directory of your choice

### 1. Setup Python Virtual Environment

1. Ensure to use python version 3.11 or later
2. Create a python virtual environment in this directory: e.g. `python -m venv .venv`
3. Activate the virtual envirnoment: e.g. `.venv\Scripts\activate` if using Command Prompt
4. Install required packages: `pip install -r requirements-windows.txt`

### 2. Setup PostgreSQL

1. [Download PostgreSQL](https://www.postgresql.org/download/windows/)
2. Follow install instructions. When prompted, install PostGIS extension under Spatial Extensions in Stack Builder
3. Launch pgAdmin 4 to setup database
4. Enable PostGIS extension: open query tool (right click postgres menu in sidebar) type: `CREATE EXTENSION postgis`. Run it. Restart pgAdmin 4
5. Create table (navigate to servers > postgreSQL > databases > postgres > schemas > public > tables), right click on tables and select create table
6. Create table called 'media' with the following columns:

| Name | Data Type | Not NULL? | Primary Key? |
|------|-----------|-----------|--------------|
| id | uuid | Y | Y |
| owner_id | uuid |
| filename | text |
| hash | text |
| filetype | text | Y |
| basename | text | Y |
| mime_type | text |
| magic_type | text |
| size | integer |
| date_uploaded | timestamp with time zone |
| file_metadata | json |
| date_created | timestamp with time zone |
| naturally_viewable | boolean |
| viewable_name | text |
| location | geography |
| date_last_modified | timestamp with time zone |

7. Return to project directory and rename .env.example to .env and set password in .env to your PostgreSQL password

### 3. Install ExifTool

1. [Install ExifTool](https://exiftool.org/)
2. Extract contents to permanent directory, e.g. C:\ExifTool\
3. Rename exiftool(-k).exe to exiftool.exe
4. Add directory to Windows PATH

### 4. Install ffmpeg

1. [Install ffmpeg](https://ffmpeg.org/download.html)
2. Extract contents to permanent directory, e.g. C:\ffmpeg\
3. Add directory to Windows PATH

### 5. Final Steps

1. Restart Computer
2. Run main.py: `python main.py`