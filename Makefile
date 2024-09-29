IMAGE="maand"

build:
	docker build -t $(IMAGE) ./src/main

exec:
	docker run --rm --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace -it $(IMAGE)

initialize:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) initialize

update:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) update $(ARGS)

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