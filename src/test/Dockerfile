FROM maand

COPY requirements.txt /requirements.txt
RUN yum install -y sqlite3
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"
ENV PYTHONPATH=.

COPY . /tests
WORKDIR /tests
RUN chmod +x /tests/*.sh

RUN mkdir /workspace
COPY agents.json /workspace/
COPY homelab.key /workspace/

ENTRYPOINT [ "tini", "-g", "--", "bash", "/tests/start.sh" ]
