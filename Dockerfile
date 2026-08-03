FROM docker.io/caronc/apprise:v1.5.1@sha256:c06bdf3074331fabc2dc254bd856bf3d337ba13cea61a21ddab68a820d04d52c
COPY entrypoint.sh /usr/local/bin/apprise-railway-entrypoint
RUN chmod +x /usr/local/bin/apprise-railway-entrypoint
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/apprise-railway-entrypoint"]
