import glob
import json
import os
import sqlite3


def get_agents():
    with open("/bucket/workspace/agents.json", "r") as f:
        return json.loads(f.read())


def get_agents_ip():
    agents_config = get_agents()
    return [agent.get("host") for agent in agents_config]


def get_agent_ip_by_label(label):
    agents_config = get_agents()
    agents_ip = []
    for agent in agents_config:
        if label in agent.get("labels", []):
            agents_ip.append(agent["host"])
    return agents_ip


def get_jobs():
    jobs = []
    for manifest_path in glob.glob("/bucket/workspace/jobs/*/manifest.json"):
        job_name = os.path.basename(os.path.dirname(manifest_path))
        jobs.append(job_name)
    return jobs


def get_job_manifest(job_name):
    manifest_path = os.path.join("/bucket/workspace/jobs", job_name, "manifest.json")
    with open(manifest_path, "r") as f:
        metadata = json.loads(f.read())
        if "order" not in metadata:
            metadata["order"] = 99
        if "labels" not in metadata:
            metadata["labels"] = []
        if "certs" not in metadata:
            metadata["certs"] = []
        if "commands" not in metadata:
            metadata["commands"] = {}
        if "plugins" not in metadata:
            metadata["plugins"] = []
        return metadata


def get_job_files(job_name):
    return glob.glob("{}/**".format(job_name), recursive=True, root_dir="/bucket/workspace/jobs")


def get_disabled_jobs():
    if not os.path.exists(f"/bucket/workspace/disabled.json"):
        return {"jobs":{}, "agents":[]}

    with open("/bucket/workspace/disabled.json", "r") as f:
        return json.load(f)


def get_bucket_id():
    db = sqlite3.connect("/bucket/data/maand.db")
    cursor = db.cursor()
    cursor.execute("SELECT bucket_id from bucket")
    return cursor.fetchone()[0]
