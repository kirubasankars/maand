docker:
	docker build -t maand ./src

alias:
	alias maand="docker run --rm -v $(PWD)/namespace:/namespace:z maand "

test:
	docker build -t maand_test ./src/test
	docker run --rm --privileged -e NAMESPACE_PATH=$(PWD)/namespace -v $(PWD)/namespace:/namespace:z -v /var/run/docker.sock:/var/run/docker.sock -it maand_test

exec:
	docker run --rm --user=root --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace:z -it $(IMAGE)

clean:
	sudo rm -rf $(PWD)/namespace/*