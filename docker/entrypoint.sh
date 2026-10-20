#!/bin/sh
set -eu

if [ -z "${SOURCE_COMMIT:-}" ] || [ -z "${CEMETERY_IMAGE_COMMIT:-}" ] || [ "$SOURCE_COMMIT" != "$CEMETERY_IMAGE_COMMIT" ]; then
    echo "Selected source commit does not match this application image." >&2
    exit 1
fi

mkdir -p "$(dirname "$SQLITE_PATH")" "$MEDIA_ROOT"
PRIVATE_MEDIA_ROOT="${PRIVATE_MEDIA_ROOT:-$(dirname "$MEDIA_ROOT")/$(basename "$MEDIA_ROOT")-private}"
export PRIVATE_MEDIA_ROOT
mkdir -p "$PRIVATE_MEDIA_ROOT"

# Seed reviewed demo assets only on the first empty persistent-media startup.
# Runtime uploads under /app/media are excluded from source and image contexts.
if [ -d /app/seed-media ] && [ -z "$(find "$MEDIA_ROOT" -mindepth 1 -print -quit)" ]; then
    cp -a /app/seed-media/. "$MEDIA_ROOT/"
fi

chown django:django "$(dirname "$SQLITE_PATH")" "$MEDIA_ROOT" "$PRIVATE_MEDIA_ROOT"
if [ -f "$SQLITE_PATH" ]; then
    chown django:django "$SQLITE_PATH"
fi

gosu django python manage.py migrate --noinput
gosu django python manage.py cleanup_public_grave_images
exec gosu django gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -
