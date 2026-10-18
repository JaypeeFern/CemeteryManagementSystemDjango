#!/bin/sh
set -eu

mkdir -p "$(dirname "$SQLITE_PATH")" "$MEDIA_ROOT"

# Seed bundled media only on the first empty persistent-media startup. Future
# uploads remain in the host-mounted directory across image deployments.
if [ -d /app/media ] && [ -z "$(find "$MEDIA_ROOT" -mindepth 1 -print -quit)" ]; then
    cp -a /app/media/. "$MEDIA_ROOT/"
fi

chown django:django "$(dirname "$SQLITE_PATH")" "$MEDIA_ROOT"
if [ -f "$SQLITE_PATH" ]; then
    chown django:django "$SQLITE_PATH"
fi

gosu django python manage.py migrate --noinput
exec gosu django gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -
