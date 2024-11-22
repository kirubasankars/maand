docker:
	docker build -t maand ./src

alias:
	alias maand="docker run --rm -v $(PWD)/bucket:/bucket:z maand "

exec:
	docker run --rm --user=root --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace:z -it maand

clean:
	rm -rf $(PWD)/bucket/*
