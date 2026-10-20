# Build pinned application dependencies once, then keep compilers out of the
# image that Coolify runs.
FROM python:3.13-slim-bookworm@sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641 AS dependencies

WORKDIR /build
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN python -m pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.13-slim-bookworm@sha256:a1165e272e578941b84abc79e4ab38a0305cd12803a5c4247979ac7655f4d641 AS runtime

ARG SOURCE_COMMIT
RUN test -n "$SOURCE_COMMIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SQLITE_PATH=/data/db.sqlite3 \
    MEDIA_ROOT=/data/media \
    CEMETERY_IMAGE_COMMIT=$SOURCE_COMMIT

RUN apt-get update \
    && apt-get install --no-install-recommends -y gosu libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /usr/sbin/nologin django \
    && mkdir -p /app /data \
    && chown django:django /data

WORKDIR /app
COPY --from=dependencies /wheels /wheels
COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY . .
COPY docker/entrypoint.sh /usr/local/bin/cemetery-entrypoint
RUN DJANGO_DEBUG=true python manage.py collectstatic --noinput \
    && chmod 755 /usr/local/bin/cemetery-entrypoint

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/cemetery-entrypoint"]
