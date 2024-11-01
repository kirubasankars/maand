import json
import os
import shutil
import subprocess
import uuid

import workspace


def get_maand_command(args):
    return f"docker run --rm -v $WORKSPACE_PATH:/workspace:z maand {args}"


def command(cmd, env=None, stdout=None, stderr=None):
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    return subprocess.run(["sh", file_path], env=env, stdout=stdout, stderr=stderr)


def clean():
    command("rm -rf /workspace/*")
    shutil.copy("/tests/fixtures/agents.json", "/workspace/agents.json")
    shutil.copy("/tests/fixtures/homelab.key", "/workspace/homelab.key")
    shutil.copy("/tests/fixtures/maand.conf", "/workspace/maand.conf")

    # scan_agent()
    #
    # agents_ip = workspace.get_agents_ip()
    # for agent in agents_ip:
    #     command("mkdir -p /workspace/tmp")
    #     command(f"ssh -i /workspace/homelab.key agent@{agent} 'sudo rm -rf /opt/agent'")


def sync():
    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        command("mkdir -p /workspace/tmp")
        command(f"ssh -i /workspace/homelab.key agent@{agent} 'sync'")
        command(f'rsync -vr --delete --rsync-path="sudo rsync" --rsh="ssh -i /workspace/homelab.key" agent@{agent}:/opt/agent/ /workspace/tmp/{agent};')


def read_file_content(file_path):
    with open(file_path, "r") as f:
        return f.read()


def make_job(name, roles=[], order=0):
    os.makedirs(f"/workspace/jobs/{name}", exist_ok=True)
    with open(f"/workspace/jobs/{name}/manifest.json", "w") as f:
        f.write(json.dumps({"roles": roles, "order": order}))

    with open("/tests/fixtures/Makefile.sample", "rb") as rf:
        with open(f"/workspace/jobs/{name}/Makefile", "wb") as wf:
            wf.write(rf.read())

def scan_agent():
    agents_ip = workspace.get_agents_ip()
    for agent_ip in agents_ip:
        agent_file = agent_ip.replace(".", "_")
        command(f"ssh-keyscan -H {agent_ip} > /tmp/{agent_file}.agent ; cat /tmp/*.agent > ~/.ssh/known_hosts", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)