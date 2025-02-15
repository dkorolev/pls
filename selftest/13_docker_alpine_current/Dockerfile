FROM alpine:latest
RUN apk add bash python3 clang cmake make git

# Collected by `pls_go.sh`, `.gitignore`-d.
COPY ./_pls /_pls
RUN ln -sf /_pls/pls /usr/bin/pls

COPY entrypoint.sh /
COPY example.cc /demo/
ENTRYPOINT ["/entrypoint.sh"]
