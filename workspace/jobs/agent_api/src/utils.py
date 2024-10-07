import functools
import glob
import os


@functools.cache
def get_agent_id():
    return open("/opt/agent/agent_id.txt", "r").read().strip()


@functools.cache
def get_cluster_id():
    return open("/opt/agent/cluster_id.txt", "r").read().strip()


@functools.cache
def get_roles():
    with open("/opt/agent/roles.txt", "r") as f:
        return f.read().strip().split("\n")


@functools.cache
def get_jobs():
    jobs = []
    for metadata_path in glob.glob("/opt/agent/jobs/*/manifest.json"):
        jobs.append(os.path.basename(os.path.dirname(metadata_path)))
    return jobs


def get_update_seq():
    return int(open("/opt/agent/update_seq.txt", "r").read().strip())
