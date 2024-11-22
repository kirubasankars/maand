docker:
	docker build -t mad ./src

alias:
	alias mad="docker run --rm -v $(PWD)/bucket:/bucket:z mad "

exec:
	docker run --rm --user=root --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace:z -it mad

clean:
	rm -rf $(PWD)/bucket/*
