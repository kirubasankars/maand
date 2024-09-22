IMAGE="maand"

build:
	docker build -t $(IMAGE) ./src/main

exec:
	docker run --rm --entrypoint=/bin/bash -v $(PWD)/workspace:/workspace -it $(IMAGE)

initialize:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) initialize

update:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) update

run_command:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) run_command

run_command_with_health_check:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) run_command_with_health_check

run_command_local:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) run_command_local

start_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) start_jobs

stop_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) stop_jobs

restart_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) restart_jobs

rolling_restart_jobs:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) rolling_restart_jobs

health_check:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) health_check

run_command_no_cluster_check:
	docker run --rm -v $(PWD)/workspace:/workspace $(IMAGE) run_command_no_cluster_check