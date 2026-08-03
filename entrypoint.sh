#!/bin/sh
set -eu
: "${APPRISE_AUTH_USER:?APPRISE_AUTH_USER is required}"
: "${APPRISE_AUTH_PASSWORD:?APPRISE_AUTH_PASSWORD is required}"
mkdir -p /data/config /data/attach /data/plugin
rm -rf /config /attach /plugin
ln -s /data/config /config
ln -s /data/attach /attach
ln -s /data/plugin /plugin
chown -R "${PUID:-1000}:${PGID:-1000}" /data
hash=$(openssl passwd -apr1 "$APPRISE_AUTH_PASSWORD")
printf '%s:%s\n' "$APPRISE_AUTH_USER" "$hash" > /etc/nginx/.htpasswd
cat > /etc/nginx/location-override.conf <<'EOF'
auth_basic "Apprise API";
auth_basic_user_file /etc/nginx/.htpasswd;
EOF
cat > /etc/nginx/server-override.conf <<'EOF'
location = /status {
    proxy_pass http://apprise_upstream/status/;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_set_header Host $http_host;
    access_log off;
}
EOF
unset APPRISE_AUTH_PASSWORD
exec /opt/apprise/webapp/supervisord-startup
