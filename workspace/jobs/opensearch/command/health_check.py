import requests

import os

OPENSEARCH_HOST = os.getenv("OPENSEARCH_0")
OPENSEARCH_NODES_COUNT = int(os.getenv("OPENSEARCH_LENGTH"))

while True:
    try:
        r = requests.get(f"http://{OPENSEARCH_HOST}:9200/_cluster/health")
        r.raise_for_status()
        if r.json()["number_of_nodes"] == OPENSEARCH_NODES_COUNT:
            break
    except ConnectionRefusedError as e:
        print("Unable to connect to Open Search server", flush=True)
