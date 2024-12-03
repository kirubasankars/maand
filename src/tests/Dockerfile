FROM maand

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"
ENV PYTHONPATH=.

COPY /scripts /tests
WORKDIR /tests
RUN chmod +x /tests/*.sh

RUN mkdir /bucket
ENTRYPOINT [ "tini", "-g", "--", "bash", "/tests/start.sh" ]
