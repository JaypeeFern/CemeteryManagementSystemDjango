# Surigao Memorial Park Cemetery Management System
Previous repo no longer accessible for some reason. Re-added here in new GitHub Account

# SHORT DEMO
https://github.com/JaypeeFern/CemeteryManagementSystem/assets/103358200/3d543b32-0c8a-45b6-8fa8-d5ddd6a84e26

## Features
1. Dynamic Search Based on Search Input 
2. Grave Location Viewer for Deceased (Powered by leaflet and OpenStreetMaps)
3. Lot Reservation.

## Docker deployment (Coolify)

Coolify uses `docker-compose.yml` to pull the exact GHCR manifest digest
published by `.github/workflows/build-images.yml`. CI verifies the digest,
sets and reads back the digest-pinned `IMAGE_REFERENCE` in Coolify, pins the
resource to that Git commit, then triggers its deploy webhook. Commit-SHA tags
and `latest` are published for lookup but are not used by production Compose.
The container checks its embedded build commit against Coolify's selected
source commit before migrations or serving requests.

Configure these values in the Coolify resource environment:

- `DJANGO_SECRET_KEY`: a newly generated Django secret key.
- `DJANGO_ALLOWED_HOSTS`: comma-separated public host names, without schemes.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: comma-separated full HTTPS origins.
- `DJANGO_CORS_ALLOWED_ORIGINS`: optional comma-separated origins for a
  separate browser frontend. It defaults to empty; configure only origins that
  are registered and controlled by the deployment owner.
- `GOOGLE_RECAPTCHA_SECRET_KEY` and `GOOGLE_RECAPTCHA_SITE_KEY`: the reCAPTCHA
  key pair used by the login form. Revoke and replace the previously exposed
  key pair.
- `AXES_IPWARE_PROXY_COUNT`: number of trusted reverse proxies before Django.
  Set this explicitly to the actual trusted proxy count; production Compose
  refuses to start without it. Ensure the edge proxy overwrites or validates
  `X-Forwarded-For` before using that header for login throttling.
- `APP_DATA_PATH`: persistent host directory for SQLite and media. The default
  is `/data/coolify/persistent/cemetery-management`.
- `IMAGE_REFERENCE`: set and verified by the deployment workflow before each
  deploy. For a manual deployment, use the full GHCR image name with a verified
  `@sha256:` manifest digest.

Add GitHub Actions secrets `COOLIFY_WEBHOOK_URL`, `COOLIFY_TOKEN`, and
`COOLIFY_API_TOKEN` for automatic deployment. If the GHCR package is private,
configure GHCR image-pull credentials in Coolify as well.

Before the first production deployment, copy the existing SQLite database to
`$APP_DATA_PATH/db.sqlite3` and existing user uploads to `$APP_DATA_PATH/media/`
on the Coolify host. These files are persisted outside the image and are not
overwritten during later deployments. When migrating from a different host,
set `APP_DATA_PATH` to its prepared persistent directory.

Use only a verified, current production backup as the database source. Do not
restore a SQLite file from a repository checkout or Git history: the previously
tracked database artifacts were removed because they contained user and
session data. Treat historical copies as exposed and handle credential resets
and any required incident response separately.

The first deployment of the security update clears existing Django sessions
once, forcing every account to sign in again. CAPTCHA verification requests are
limited to 60 per source IP per minute; successful account creations are
limited to 5 per source IP per hour. Requests without a CAPTCHA token are
rejected before consuming the verification quota. Confirm the configured
reverse proxy count and that the proxy sanitizes `X-Forwarded-For`; incorrect
proxy trust settings can weaken per-IP throttling and login lockouts. If a
forwarded client address cannot be resolved, the application uses the network
peer address, which may apply the limit to all visitors behind the proxy.

For a local source build, copy `.env.example` to `.env`, then run:

```powershell
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

The local override publishes the app at `http://localhost:8000`.

## Dependencies 
1. Python
2. Venv (Package)

Install all packages by using this command pip install -r requirements.txt











