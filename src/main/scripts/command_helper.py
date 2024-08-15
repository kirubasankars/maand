import os
import subprocess
import uuid
import utils

logger = utils.get_logger()


def command_local(cmd, env=None):
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    env = env or os.environ.copy()
    return subprocess.run(["sh", file_path], env=env)


def command_remote(cmd, agent_ip=None, sudo=False):
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    env = os.environ.copy()
    env.setdefault("AGENT_IP", agent_ip)
    sh = "sh" if sudo else "sudo sh"
    return command_local(
        f"ssh -o StrictHostKeyChecking=no -o LogLevel=error $SSH_USER@$AGENT_IP '{sh}' < {file_path}", env=env)


def command2_remote(file_path, agent_ip=None, sudo=False):
    env = os.environ.copy()
    env.setdefault("AGENT_IP", agent_ip)
    sh = "sh" if sudo else "sudo sh"
    return command_local(
        f"ssh -o StrictHostKeyChecking=no -o LogLevel=error $SSH_USER@$AGENT_IP '{sh}' < {file_path}", env=env)