build:
	docker build -t opensearch ./src

setup:
	sysctl -w vm.max_map_count=262144;
	chown -R 1050 ../../certs
	chown -R 1050 ./config
	rm -rf /opt/maand/opensearch/{data,logs}
	mkdir -p /opt/maand/opensearch/{data,logs} && chown -R 1050 /opt/maand/opensearch/{data,logs}

deploy: setup
	docker-compose up -d --remove-orphans

force-deploy: setup
	docker-compose up -d --remove-orphans --force-recreate

restart:
	docker-compose restart

stop:
	docker-compose stop