#!/bin/bash
set -ueo pipefail

WORKSPACE=${WORKSPACE:-""}
function maand() {
  echo "maand $@"
  docker run --rm -v $WORKSPACE:/workspace maand $@
}

rm -rf /workspace/{ca.crt,ca.key,kv.db,maand.db,secrets.env,variables.env,command.sh}
echo "rm -rf /opt/agent" > /workspace/command.sh
maand run_command_no_check

maand initialize
pytest /tests/test_initialize.py

echo 'OPENSEARCH_ADMIN_PASSWORD_HASH="$$2y$$10$$FNNuaKNKyBQTI3TvzpSl4ummss1zTt2i3mfGUS423lmpN7xlb2woC"' >> /workspace/secrets.env
echo 'PROMETHEUS_ADMIN_PASSWORD_HASH="$$2y$$10$$FNNuaKNKyBQTI3TvzpSl4ummss1zTt2i3mfGUS423lmpN7xlb2woC"' >> /workspace/secrets.env

maand build
maand deploy

maand start_jobs --jobs="prometheus"
python3 /tests/prometheus_targets.py prometheus up 1
python3 /tests/prometheus_targets.py node_exporter down 4
python3 /tests/prometheus_targets.py cadvisor_exporter down 4
python3 /tests/prometheus_targets.py opensearch_exporter down 3

maand start_jobs --jobs="node_exporter"
python3 /tests/prometheus_targets.py prometheus up 1
python3 /tests/prometheus_targets.py node_exporter up 4
python3 /tests/prometheus_targets.py cadvisor_exporter down 4
python3 /tests/prometheus_targets.py opensearch_exporter down 3

maand start_jobs --jobs="cadvisor_exporter"
python3 /tests/prometheus_targets.py prometheus up 1
python3 /tests/prometheus_targets.py node_exporter up 4
python3 /tests/prometheus_targets.py cadvisor_exporter up 4
python3 /tests/prometheus_targets.py opensearch_exporter down 3

maand start_jobs --jobs="opensearch"
python3 /tests/prometheus_targets.py prometheus up 1
python3 /tests/prometheus_targets.py node_exporter up 4
python3 /tests/prometheus_targets.py cadvisor_exporter up 4
python3 /tests/prometheus_targets.py opensearch_exporter up 3

maand stop_jobs --jobs="opensearch,node_exporter,cadvisor_exporter"
python3 /tests/prometheus_targets.py opensearch_exporter down 3
python3 /tests/prometheus_targets.py node_exporter down 4
python3 /tests/prometheus_targets.py cadvisor_exporter down 4

maand start_jobs --min-order=8 --max-order=12
python3 /tests/prometheus_targets.py prometheus up 1
python3 /tests/prometheus_targets.py node_exporter down 4
python3 /tests/prometheus_targets.py cadvisor_exporter up 4
python3 /tests/prometheus_targets.py opensearch_exporter down 3

maand start_jobs --max-order=1
python3 /tests/prometheus_targets.py prometheus up 1
python3 /tests/prometheus_targets.py node_exporter up 4
python3 /tests/prometheus_targets.py cadvisor_exporter up 4
python3 /tests/prometheus_targets.py opensearch_exporter down 3

maand start_jobs --min-order=55
python3 /tests/prometheus_targets.py prometheus up 1
python3 /tests/prometheus_targets.py node_exporter up 4
python3 /tests/prometheus_targets.py cadvisor_exporter up 4
python3 /tests/prometheus_targets.py opensearch_exporter up 3

