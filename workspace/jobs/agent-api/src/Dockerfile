FROM fedora

RUN mkdir -p /python-docker
RUN yum install -y gcc python3-devel python3-pip

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=80"]