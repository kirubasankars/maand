build:
	docker build -t agent_api ./src

start: build
	docker-compose up -d --remove-orphans

stop: build
	docker-compose down

restart: build
	docker-compose restart