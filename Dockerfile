FROM docker.io/caronc/apprise:v1.5.4@sha256:c5ea17408c10fd84c8fdb05a421114a1a677b16343c274bf9b1a55701b530829
COPY entrypoint.sh /usr/local/bin/apprise-railway-entrypoint
RUN chmod +x /usr/local/bin/apprise-railway-entrypoint
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/apprise-railway-entrypoint"]
