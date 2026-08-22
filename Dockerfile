FROM docker.io/caronc/apprise:v1.5.2@sha256:feb3ad42d280bca0c58fdff6f77f46e2586a65bbc6d2bff614d31245ff8a399c
COPY entrypoint.sh /usr/local/bin/apprise-railway-entrypoint
RUN chmod +x /usr/local/bin/apprise-railway-entrypoint
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/apprise-railway-entrypoint"]
