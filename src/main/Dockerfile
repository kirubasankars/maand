FROM fedora:42

RUN yum update -y
RUN yum install -y python3 python3-pip jq wget rsync tree openssl openssh-clients tini docker unzip sqlite3

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY scripts /scripts
RUN chmod +x /scripts/*.sh
ENV PYTHONPATH=/scripts

ENTRYPOINT ["tini", "-g", "-p", "SIGTERM", "--", "bash", "/scripts/start.sh"]
