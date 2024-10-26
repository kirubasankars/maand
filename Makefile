IMAGE="maand"

docker:
	docker build -t $(IMAGE) ./src/main

test:
	docker build -t maand_test ./src/test
	docker run --rm --privileged -e WORKSPACE_PATH=$(PWD)/workspace -v $(PWD)/workspace:/workspace:z -v /var/run/docker.sock:/var/run/docker.sock -it maand_test

exec:
	docker run --rm --user=root --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace:z -it $(IMAGE)

clean:
	rm -rf $(PWD)/workspace/{ca.crt,ca.key,command.sh,*.db,secrets.env,variables.env,reports,data}

initialize:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) initialize

build_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) build_jobs

plan:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) plan

update:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) update $(ARGS)

build:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) build_jobs
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) plan

deploy:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) update $(ARGS)
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) deploy $(ARGS)

run_command:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) run_command $(ARGS)

run_command_with_health_check:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) run_command_with_health_check $(ARGS)

run_command_local:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) run_command_local $(ARGS)

run_command_no_check:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) run_command_no_check $(ARGS)

uptime:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) uptime $(ARGS)

collect:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) collect $(ARGS)

start_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) start_jobs $(ARGS)

stop_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) stop_jobs $(ARGS)

restart_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) restart_jobs $(ARGS)

rolling_restart_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) rolling_restart_jobs $(ARGS)

health_check:
	docker run --rm -v $(PWD)/workspace:/workspace:z $(IMAGE) health_check $(ARGS)