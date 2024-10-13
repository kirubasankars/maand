start:
	python3 update_targets.py
	docker-compose up -d --remove-orphans

stop:
	docker-compose down

restart:
	python3 parse_node_exporter_targets.py
	docker-compose restart