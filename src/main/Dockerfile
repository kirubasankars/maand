FROM fedora

RUN yum update -y
RUN yum install -y python3 python3-pip jq wget rsync tree openssl openssh-clients tini docker unzip which hostname

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY agent /agent
COPY scripts /scripts
RUN chmod +x /scripts/*.sh

ENTRYPOINT ["tini", "-g", "--", "bash", "/scripts/start.sh"]