import subprocess
import uuid

import utils

logger = utils.get_logger()


def command_local(cmd, env=None, stdout=None, stderr=None):
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    return subprocess.run(["sh", file_path], env=env, stdout=stdout, stderr=stderr)


def command_remote(cmd, env=None, stdout=None, stderr=None):
    use_sudo = utils.is_sudo_enabled(env)
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    sh = "sh" if not use_sudo else "sudo sh"
    return command_local(
        f"ssh -i /workspace/$SSH_KEY $SSH_USER@$AGENT_IP 'timeout 300 {sh}' < {file_path}",
        env=env, stdout=stdout, stderr=stderr)


def command2_remote(file_path, env=None, stdout=None, stderr=None):
    use_sudo = utils.is_sudo_enabled(env)
    sh = "sh" if not use_sudo else "sudo sh"
    return command_local(
        f"ssh -i /workspace/$SSH_KEY $SSH_USER@$AGENT_IP 'timeout 300 {sh}' < {file_path}",
        env=env, stdout=stdout, stderr=stderr)


def scan_agent(agent_ip):
    agent_file = agent_ip.replace(".", "_")
    command_local(f"ssh-keyscan -H {agent_ip} > /tmp/{agent_file}.agent; cat /tmp/*.agent > ~/.ssh/known_hosts", stderr=subprocess.DEVNULL)