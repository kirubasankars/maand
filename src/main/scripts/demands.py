import json
import os

def get():
    job = os.environ.get("JOB")
    with open(f"/modules/{job}/_modules/demands.json") as f:
        return json.load(f)