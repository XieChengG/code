FROM centos

ENV JAVA_HOME=/usr/local/java
ENV PATH=${JAVA_HOME}/bin:$PATH
ENV JENKINS_VERSION=2.452.3

WORKDIR /usr/local/src

COPY jdk-21_linux-x64_bin.tar.gz jdk.tar.gz

RUN set -eux; \
    \
    sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*; \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*; \
    \
    yum install -y wget openssl; \
    \
    wget https://mirrors.tuna.tsinghua.edu.cn/jenkins/redhat-stable/jenkins-${JENKINS_VERSION}-1.1.noarch.rpm; \
    \
    if test ! -d "$JAVA_HOME"; then \
        mkdir -p "$JAVA_HOME"; \
    fi; \
    tar -xvf jdk.tar.gz -C "$JAVA_HOME" --strip-components=1; \
    chown -R root.root "$JAVA_HOME"; \
    java -version; \
    \
    rm *.tar.gz; \
    \
    yum install -y jenkins-${JENKINS_VERSION}-1.1.noarch.rpm; \
    yum clean all; \
    rm *.rpm

VOLUME /var/log/jenkins /var/lib/jenkins

EXPOSE 8080
CMD ["jenkins"]