IMAGE="maand"

docker:
	docker build -t $(IMAGE) ./src/main

alias:
	alias maand="docker run --rm -v $(PWD)/namespace:/namespace:z maand "

test:
	docker build -t maand_test ./src/test
	docker run --rm --privileged -e WORKSPACE_PATH=$(PWD)/workspace -v $(PWD)/workspace:/workspace:z -v /var/run/docker.sock:/var/run/docker.sock -it maand_test

exec:
	docker run --rm --user=root --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace:z -it $(IMAGE)

clean:
	sudo rm -rf $(PWD)/namespace/*