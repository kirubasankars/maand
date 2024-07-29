import requests

import os

OPENSEARCH_HOST = os.getenv("OPENSEARCH_0")

while True:
    try:
        r = requests.get(f"http://{OPENSEARCH_HOST}:9200/_cluster/health")
        r.raise_for_status()
        if r.json()["number_of_nodes"] == 3:
            break
    except Exception as e:
        print(e, flush=True)

