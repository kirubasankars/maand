FROM fedora

RUN yum update -y
RUN yum install -y python3 python3-pip jq wget rsync tree openssl openssh-clients tini docker unzip which hostname
RUN pip install requests pytest python-dotenv pyopenssl retry

COPY agent /agent
COPY scripts /scripts
RUN chmod +x /scripts/*.sh

ENTRYPOINT ["tini", "-g", "--", "/scripts/start.sh"]