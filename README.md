# Media Backup Backend

## Overview

The backend is responsible for storing all media files, user accounts and acting as an API for clients.

This repository is part of the [Media Backup Project](https://github.com/LewisSSmith/MediaBackup)

## Setup (Debian/Ubuntu)

1. Clone repository to a directory of your choice

### 1. Setup Python Virtual Environment

1. Ensure to use python version 3.11 or later
2. Create a python virtual environment in this directory: e.g. `python3 -m venv .venv`
3. Activate the virtual envirnoment: e.g. `source .venv\bin\activate`
4. Install required packages: `pip install -r requirements-linux.txt`

### 2. Setup PostgreSQL

1. Install PostgreSQL: `sudo apt install postgresql`
2. Install PostGIS extension: `sudo apt install postgresql-16-postgis-3`, replace 16 with your postgresql major version `psql --version`
3. Open PostgreSQL command line: `sudo -u postgres psql`
4. Create user (replace myuser and mypass with a username and password): `CREATE USER myuser WITH PASSWORD 'mypass';`
5. Create database (replace mydb with a name for your database): `CREATE DATABASE mydb OWNER myuser;`
6. Connect to your database: `\c mydb`
7. Enable extension in database: `CREATE EXTENSION postgis;`
8. Create media and users tables:
```sql
CREATE TABLE media
(
    id uuid PRIMARY KEY,
    owner_id uuid NOT NULL,
    filename text NOT NULL,
    hash text,
    filetype text NOT NULL,
    basename text NOT NULL,
    mime_type text,
    magic_type text,
    size integer,
    date_uploaded timestamp with time zone,
    file_metadata json,
    date_created timestamp with time zone,
    naturally_viewable boolean,
    viewable_name text,
    location geography,
    date_last_modified timestamp with time zone
);
```
```sql
CREATE TABLE users
(
    id uuid PRIMARY KEY,
    username text NOT NULL,
    email text NOT NULL,
    password_hash text NOT NULL
);
```
9. Change owners of tables so python scripts have permission to access them. (The spatial_ref_sys table was created by PostGIS extension)
```sql
ALTER TABLE media OWNER TO myuser;
ALTER TABLE spatial_ref_sys OWNER TO myuser;
ALTER TABLE users OWNER TO myuser;
```

### 3. Install ExifTool and ffmpeg

1. `sudo apt install libimage-exiftool-perl`
2. `sudo apt install ffmpeg`

### 4. Final Steps
1. Run main.py: `python3 main.py`

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

7. Create table called 'users' with the following columns:

| Name | Data Type | Not NULL? | Primary Key? |
|------|-----------|-----------|--------------|
| id | uuid | Y | Y |
| username | text | Y |
| email | text | Y |
| password_hash | text | Y |

8. Return to project directory and rename .env.example to .env and set password in .env to your PostgreSQL password

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
