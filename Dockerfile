FROM docker.io/caronc/apprise:v2.0.0@sha256:cc5ef662ad2a4a25958f1eddbf87f2e95f9bf637ea481f1adcec18312ad262f5
COPY entrypoint.sh /usr/local/bin/apprise-railway-entrypoint
RUN chmod +x /usr/local/bin/apprise-railway-entrypoint
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/apprise-railway-entrypoint"]
