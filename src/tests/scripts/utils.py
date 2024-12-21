import json
import os
import shutil
import subprocess
import uuid

import workspace

def get_maand_command(args):
    return f"docker run --rm -v $BUCKET_PATH:/bucket:z maand {args}"


def command(cmd, env=None, stdout=None, stderr=None):
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    return subprocess.run(["sh", file_path], env=env, stdout=stdout, stderr=stderr)


def clean():
    clean_bucket()
    shutil.copy("/tests/fixtures/agents.json", "/bucket/workspace/agents.json")
    shutil.copy("/tests/fixtures/homelab.key", "/bucket/secrets/homelab.key")
    shutil.copy("/tests/fixtures/maand.conf", "/bucket/maand.conf")

    scan_agent()

    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        command("mkdir -p /bucket/tmp")
        command(f"ssh -i /bucket/secrets/homelab.key agent@{agent} 'sudo rm -rf /opt/agent'")
        command(f"ssh -i /bucket/secrets/homelab.key agent@{agent} 'sudo mkdir -p /opt/agent'")


def clean_bucket():
    command("rm -rf /bucket/*")
    command("mkdir -p /bucket/{secrets,data,workspace}")


def sync():
    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        command("mkdir -p /bucket/tmp")
        command(f'rsync -vr --delete --rsync-path="sudo rsync" --rsh="ssh -i /bucket/secrets/homelab.key" agent@{agent}:/opt/agent/ /bucket/tmp/{agent};')


def read_file_content(file_path):
    with open(file_path, "r") as f:
        return f.read().strip()


def make_job(name, labels=[], order=0):
    os.makedirs(f"/bucket/workspace/jobs/{name}", exist_ok=True)
    with open(f"/bucket/workspace/jobs/{name}/manifest.json", "w") as f:
        f.write(json.dumps({"labels": labels}))

    with open("/tests/fixtures/Makefile.sample", "rb") as rf:
        with open(f"/bucket/workspace/jobs/{name}/Makefile", "wb") as wf:
            wf.write(rf.read())

def scan_agent():
    agents_ip = workspace.get_agents_ip()
    for agent_ip in agents_ip:
        agent_file = agent_ip.replace(".", "_")
        command(f"ssh-keyscan -H {agent_ip} > /tmp/{agent_file}.agent ; cat /tmp/*.agent > ~/.ssh/known_hosts", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
