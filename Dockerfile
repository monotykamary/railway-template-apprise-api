FROM docker.io/caronc/apprise:2.0.1@sha256:0b2913b15c8eb47c25345722985ffbfae701326edde21909c205d296d62dd52c
COPY entrypoint.sh /usr/local/bin/apprise-railway-entrypoint
RUN chmod +x /usr/local/bin/apprise-railway-entrypoint
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/apprise-railway-entrypoint"]
