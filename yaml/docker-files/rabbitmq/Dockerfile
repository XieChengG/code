FROM ubuntu

ARG RABBITMQ_VERSION=3.13.6
WORKDIR /usr/local/src
RUN set -eux; \
    \
    mkdir -p "/etc/apt/keyrings/"; \
    apt update && apt install -y curl gpg software-properties-common; \
    curl -s https://binaries2.erlang-solutions.com/GPG-KEY-pmanager.asc | gpg --dearmor | tee /etc/apt/keyrings/erlang-solutions-archive_compat.gpg > /dev/null; \
    mkdir -p "/etc/apt/sources.list.d/"; \
    \
    add-apt-repository ppa:rabbitmq/rabbitmq-erlang; \
    \
    apt install -y erlang logrotate

COPY rabbitmq-server_${RABBITMQ_VERSION}-1_all.deb rabbitmq-server_${RABBITMQ_VERSION}-1_all.deb
RUN set -eux; \
    dpkg -i rabbitmq-server_${RABBITMQ_VERSION}-1_all.deb; \
    rm *.deb; \
    apt-get clean

VOLUME /var/lib/rabbitmq
EXPOSE 5672
EXPOSE 15672
CMD ["rabbitmq-server"]