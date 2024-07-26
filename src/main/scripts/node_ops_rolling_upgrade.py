import os
import requests
import command_helper
import node_ops_update

node_ops_update.sync()
command_helper.command_remote("sh /opt/agent/bin/force_deploy_jobs.sh")

while True:
    try:
        r = requests.get(f"http://{os.getenv("HOST")}:9200/_cluster/health")
        r.raise_for_status()
        print(r.json(), flush=True)
        if r.json()["number_of_nodes"] == 3:
            break
    except Exception as e:
        continue

    break

