# Surigao Memorial Park Cemetery Management System
Previous repo no longer accessible for some reason. Re-added here in new GitHub Account

# SHORT DEMO
https://github.com/JaypeeFern/CemeteryManagementSystem/assets/103358200/3d543b32-0c8a-45b6-8fa8-d5ddd6a84e26

## Features
1. Dynamic Search Based on Search Input 
2. Grave Location Viewer for Deceased (Powered by leaflet and OpenStreetMaps)
3. Lot Reservation.

## Docker deployment (Coolify)

Coolify uses `docker-compose.yml` to pull the immutable image published to
GHCR by `.github/workflows/build-images.yml`. CI tags each image with the full
Git commit SHA, verifies that tag exists, pins the Coolify resource to that
commit, then triggers its deploy webhook. `latest` is published for convenience
but is not used by production Compose.

Configure these values in the Coolify resource environment:

- `DJANGO_SECRET_KEY`: a newly generated Django secret key.
- `DJANGO_ALLOWED_HOSTS`: comma-separated public host names, without schemes.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated full HTTPS origins.
- `GOOGLE_RECAPTCHA_SECRET_KEY` and `GOOGLE_RECAPTCHA_SITE_KEY`: the reCAPTCHA
  key pair used by the login form. Replace the previously committed key pair.
- `APP_DATA_PATH`: persistent host directory for SQLite and media. The default
  is `/data/coolify/persistent/cemetery-management`.
- `SOURCE_COMMIT`: Coolify's source commit value, supplied when deploying the
  matching repository revision.

Add GitHub Actions secrets `COOLIFY_WEBHOOK_URL`, `COOLIFY_TOKEN`, and
`COOLIFY_API_TOKEN` for automatic deployment. If the GHCR package is private,
configure GHCR image-pull credentials in Coolify as well.

Before the first production deployment, copy the existing SQLite database to
`$APP_DATA_PATH/db.sqlite3` and existing user uploads to `$APP_DATA_PATH/media/`
on the Coolify host. These files are persisted outside the image and are not
overwritten during later deployments. When migrating from a different host,
set `APP_DATA_PATH` to its prepared persistent directory.

For a local source build, copy `.env.example` to `.env`, set `SOURCE_COMMIT` to
the checked-out full Git SHA, then run:

```powershell
$env:SOURCE_COMMIT = (git rev-parse --verify HEAD).Trim()
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

The local override publishes the app at `http://localhost:8000`.

## Dependencies 
1. Python
2. Venv (Package)

Install all packages by using this command pip install -r requirements.txt











