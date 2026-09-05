# Apprise API on Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/apprise-api-secure?referralCode=ZqgrJ0)

Deploy Apprise API 1.5.4 as a password-protected notification gateway with persistent configurations, attachments, plugins, and storage cache.

The Deploy on Railway button is added after the published route is verified.

## What this deploys

- Official Apprise API `v1.5.4`, pinned to its Linux/AMD64 image digest
- Nginx Basic Auth with a generated password
- Simple stateful mode and one worker
- One daily-backed-up volume for `/config`, `/attach`, and `/plugin`
- Unauthenticated `/status` only, for Railway health checks

## Credentials and API

Use `APPRISE_AUTH_USER` and generated `APPRISE_AUTH_PASSWORD` as HTTP Basic Auth for the UI and API. The health route intentionally exposes only status metadata. Store notification URLs through `/add/{KEY}` and trigger them through `/notify/{KEY}`.

Apprise notification URLs contain downstream credentials. Keep the generated Basic Auth password private, use high-entropy configuration keys, restrict downstream tokens, and rotate secrets after suspected exposure.

## Updating

Update the pinned release and digest deliberately, back up the volume, review upstream changes, and repeat authenticated configuration CRUD, notification delivery to a controlled receiver, persistence, and redeploy soak tests.

## Validation

```bash
npm test
BASE_URL=https://your-domain.example AUTH_USER=apprise AUTH_PASSWORD=... python3 scripts/smoke.py
```

## Upstream

- Source: https://github.com/caronc/apprise-api/tree/v1.5.4
- Release: https://github.com/caronc/apprise-api/releases/tag/v1.5.4
- License: MIT

This repository contains Railway adapters and documentation. Apprise API remains copyright Chris Caron and contributors and is not affiliated with Railway.
