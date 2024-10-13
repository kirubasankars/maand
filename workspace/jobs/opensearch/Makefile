build:
	docker build -t opensearch ./src

setup:
	sysctl -w vm.max_map_count=262144;
	mkdir -p ./{data,logs} && chown -R 1050 ./{data,logs}

start: build setup
	docker-compose up -d --remove-orphans

stop: build
	docker-compose down

restart: build
	docker-compose restart