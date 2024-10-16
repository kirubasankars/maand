FROM maand

COPY requirements.txt /requirements.txt
COPY jobs /jobs

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"
ENV PYTHONPATH=.

WORKDIR /tests

ENTRYPOINT [ "pytest", "-s" ]