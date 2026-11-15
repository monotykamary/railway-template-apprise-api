# Test-only HTTPS edge receiver

This original MIT-licensed validation fixture is not part of the Apprise template.
Use this directory as the Railway service root, with `/health` as health check.
The server speaks HTTP on `$PORT`; Railway must terminate public HTTPS.
No external dependencies, shell invocation, URL fetching, access logs, or body logs.
The official CPython base is a stable 3.13.5 release pinned to its linux/amd64
manifest digest; CPython retains its upstream PSF licensing in the base image.
The repository LICENSE and upstream Apprise attribution remain unchanged.

Provide distinct random alphanumeric secrets (at least 32 characters each) as
`NOTIFICATION_NONCE` and `RECEIPT_CONTROL_TOKEN`. Do not commit real values.
POST JSON objects to `/<nonce>` (Apprise destination `jsons://host/<nonce>`).
Read `GET /receipts` with `Authorization: Bearer <control-token>`. `/health`
returns only `{"ok":true}`. No receipt, identity or count is public.

Bodies are capped at 64KiB with a three-second body-read deadline and socket
read timeout. Unsupported framing, content types and invalid JSON are rejected.
The single-threaded server serializes counter/receipt updates; at most 32 exact
JSON payload receipts are retained, then further POSTs fail closed with 503.
`accepted` counts successful persisted-in-memory receipts; `rejected` counts
POSTs reaching the notification handler but rejected there. HTTP parser errors
and unsupported methods are not notification attempts. `control_denied` counts
unauthorized reads separately. Records include canonical JSON SHA-256 hashes.

A random process identity and all receipts remain in memory for the whole live
three-phase application test. Never redeploy/restart this receiver between phases.
A changed identity or missing receipt fails validation; do not reset/reseed it.
This is a tiny trusted-test fixture, not a general-purpose Internet webhook service.
