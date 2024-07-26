build:
	docker build -t opensearch ./src

setup:
	mkdir -p /opt/{data,logs}
	sysctl -w vm.max_map_count=262144;
	chown -R 1050 ../../certs
	chown -R 1050 ./config
	chown -R 1050 /opt/{data,logs}

deploy: setup
	docker-compose up -d --remove-orphans

force-deploy: setup
	docker-compose up -d --remove-orphans --force-recreate

restart:
	docker-compose restart

stop:
	docker-compose stop