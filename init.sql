CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS media
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

CREATE TABLE IF NOT EXISTS users
(
    id uuid PRIMARY KEY,
    username text NOT NULL,
    email text NOT NULL,
    password_hash text NOT NULL
);