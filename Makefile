build:
	docker build -t maand ./src/main

test: build
	docker build -t maand_test ./src/tests
	docker run --user=root --rm --privileged -e BUCKET_PATH=$(PWD)/bucket -v $(PWD)/bucket:/bucket:z -v /var/run/docker.sock:/var/run/docker.sock -it maand_test

exec:
	docker run --rm --user=root --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace:z -it maand

alias:
	alias maand="docker run --rm -v $(PWD)/bucket:/bucket:z maand "