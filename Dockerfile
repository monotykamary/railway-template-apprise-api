FROM docker.io/caronc/apprise:2.1.0@sha256:bd7dc73b75882326b97d2963b7c3dd2a5e033df27d84c51f0090465d583fb316
COPY entrypoint.sh /usr/local/bin/apprise-railway-entrypoint
RUN chmod +x /usr/local/bin/apprise-railway-entrypoint
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/apprise-railway-entrypoint"]
