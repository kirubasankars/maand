copy-config:
	find /opt/agent/jobs/ -path "*/telegraf.d/input.*.conf" -exec cp {} /opt/agent/jobs/telegraf/telegraf.d/ \;

start: copy-config
	docker-compose up -d --remove-orphans

stop:
	docker-compose down

restart:
	docker-compose restart