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
    return subprocess.run(["sh", file_path], env=env)


def command_remote(cmd, env=None):
    sudo = utils.is_sudo_enabled()
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    sh = "sh" if sudo else "sudo sh"
    return command_local(
        f"ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error $SSH_USER@$AGENT_IP '{sh}' < {file_path}",
        env=env)
    # TODO: command timeout


def command2_remote(file_path, env=None):
    sudo = utils.is_sudo_enabled()
    sh = "sh" if sudo else "sudo sh"
    return command_local(
        f"ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error $SSH_USER@$AGENT_IP '{sh}' < {file_path}",
        env=env)
