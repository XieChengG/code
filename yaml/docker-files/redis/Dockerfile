FROM alpine

ARG REDIS_HOME=/usr/local/redis
ARG REDIS_VERSION=7.2.5

WORKDIR /usr/local/src

COPY redis-${REDIS_VERSION}.tar.gz redis.tar.gz

RUN set -eux; \
    \
    apk add gcc g++ make cmake; \
    \
    if test ! -d "$REDIS_HOME"; then \
        mkdir -p "$REDIS_HOME"; \
    fi; \
    tar -xvf redis.tar.gz -C "$REDIS_HOME" --strip-components=1; \
    chown -R root.root "$REDIS_HOME"; \
    mkdir -p /redis-data; \
    rm *.tar.gz

WORKDIR "$REDIS_HOME"

RUN make && make install

COPY redis.conf /etc/redis/redis.conf

VOLUME /redis-data

EXPOSE 6379

CMD ["redis-server", "/etc/redis/redis.conf"]