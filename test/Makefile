
build:
	docker build -t maand_test .

run:
	docker run --entrypoint=/bin/bash -v ./maand.py:/maand.py -v /var/run/docker.sock:/var/run/docker.sock -e WORKSPACE=/Users/skiruba/maand/workspace -it maand_test

