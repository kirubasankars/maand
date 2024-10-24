IMAGE="maand"

docker:
	docker build -t $(IMAGE) ./src/main

exec:
	docker run --rm --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace -it $(IMAGE)

clean:
	rm -rf $(PWD)/workspace/*.db $(PWD)/workspace/{*.crt,*.key,command.sh}

initialize:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) initialize

build_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) build_jobs

plan:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) plan

build:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) build_jobs
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) plan

deploy:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) deploy $(ARGS)

run_command:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) run_command $(ARGS)

run_command_with_health_check:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) run_command_with_health_check $(ARGS)

run_command_local:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) run_command_local $(ARGS)

start_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) start_jobs $(ARGS)

stop_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) stop_jobs $(ARGS)

restart_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) restart_jobs $(ARGS)

rolling_restart_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) rolling_restart_jobs $(ARGS)

health_check:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) health_check $(ARGS)

run_command_no_check:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) run_command_no_check $(ARGS)

test: docker
	make -C ./src/test build run