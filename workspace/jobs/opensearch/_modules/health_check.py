import requests

import os

OPENSEARCH_HOST = os.getenv("OPENSEARCH_0")
OPENSEARCH_NODES_COUNT = int(os.getenv("OPENSEARCH_LENGTH"))

try:

    r = requests.get(f"http://{OPENSEARCH_HOST}:9200/_cluster/health")
    r.raise_for_status()
    if r.json()["number_of_nodes"] == OPENSEARCH_NODES_COUNT:
        exit(0)
    raise Exception("OpenSearch is not healthy yet")

except Exception as e:
    print("Unable to connect to Open Search server", flush=True)
    exit(1)