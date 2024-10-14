
build:
	docker build -t maand_test .

run:
	docker run --rm -v ./tests:/tests -v $(PWD)/../workspace:/workspace -v /var/run/docker.sock:/var/run/docker.sock -e WORKSPACE=/Users/skiruba/maand/workspace -it maand_test

