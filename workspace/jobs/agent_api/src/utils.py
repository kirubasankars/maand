import functools
import glob
import json
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
    with open("/opt/agent/jobs.json", "r") as f:
        return json.loads(f.read())


def get_update_seq():
    return int(open("/opt/agent/update_seq.txt", "r").read().strip())
