# Deploy and Host Apprise API on Railway

## About Hosting Apprise API

Apprise API wraps the Apprise notification library in a web UI and REST API supporting many chat, email, push, incident, and webhook services. This template deploys stable version 1.5.1 with generated Basic Auth and durable configuration storage.

Authenticate with `APPRISE_AUTH_USER` and the generated `APPRISE_AUTH_PASSWORD` service variable.

## Common Use Cases

- Centralize notification delivery for scripts and applications
- Save named notification configurations and target groups
- Send attachments and fan out alerts across multiple services

## Dependencies for Apprise API Hosting

### Deployment Dependencies

- One Apprise API service with a daily-backed-up persistent volume
- Railway managed HTTPS
- Downstream notification-service URLs supplied by the deployer

### Implementation Details

The adapter protects every UI and API route with generated Nginx Basic Auth, except the read-only `/status` health endpoint. It maps configuration, attachment, plugin, and cache data into one persistent volume and runs simple stateful mode with one worker.

Saved Apprise URLs can contain downstream credentials. Use high-entropy config keys, least-privilege downstream tokens, and off-platform backups.

## Why Deploy Apprise API on Railway?

Railway provides managed HTTPS, generated access credentials, persistent storage with backups, health checks, and Git-driven rollouts for a centralized notification gateway.
