import os
import subprocess
import uuid

import utils
import const

logger = utils.get_logger()


def capture_command_local(cmd, env, log_file, prefix):
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"

    dir_name = os.path.dirname(log_file)
    os.makedirs(dir_name, exist_ok=True)

    with open(log_file, 'w') as file:
        process = subprocess.Popen(
            ["sh", file_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        prefix = f"[{prefix}]"
        for line in process.stdout:
            print(f"{prefix[:30]:<15} {line}", end='')
            file.write(line)

        for line in process.stderr:
            print(f"{prefix[:30]:<15} {line}", end='')
            file.write(line)

        process.wait()


def command_local(cmd, env=None, stdout=None, stderr=None):
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    return subprocess.run(["sh", file_path], env=env, stdout=stdout, stderr=stderr)


def capture_command_remote(cmd, env, log_file, prefix):
    use_sudo = utils.is_sudo_enabled(env)
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    sh = "sh" if not use_sudo else "sudo sh"
    return capture_command_local(
        f"ssh -i {const.BUCKET_PATH}/$SSH_KEY $SSH_USER@$AGENT_IP 'timeout 300 {sh}' < {file_path}",
        env=env, log_file=log_file, prefix=prefix,)


def command_remote(cmd, env=None, stdout=None, stderr=None):
    use_sudo = utils.is_sudo_enabled(env)
    file_id = uuid.uuid4()
    with open(f"/tmp/{file_id}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(cmd)
    file_path = f"/tmp/{file_id}"
    sh = "sh" if not use_sudo else "sudo sh"
    return command_local(
        f"ssh -i {const.BUCKET_PATH}/$SSH_KEY $SSH_USER@$AGENT_IP 'timeout 300 {sh}' < {file_path}",
        env=env, stdout=stdout, stderr=stderr)


def command_file_remote(file_path, env=None, stdout=None, stderr=None):
    use_sudo = utils.is_sudo_enabled(env)
    sh = "sh" if not use_sudo else "sudo sh"
    return command_local(
        f"ssh -i {const.BUCKET_PATH}/$SSH_KEY $SSH_USER@$AGENT_IP 'timeout 300 {sh}' < {file_path}",
        env=env, stdout=stdout, stderr=stderr)


def capture_command_file_remote(file_path, env, log_file, prefix):
    use_sudo = utils.is_sudo_enabled(env)
    sh = "sh" if not use_sudo else "sudo sh"
    return capture_command_local(
        f"ssh -i {const.BUCKET_PATH}/$SSH_KEY $SSH_USER@$AGENT_IP 'timeout 300 {sh}' < {file_path}",
        env, log_file, prefix)


def scan_agent(agent_ip):
    agent_file = agent_ip.replace(".", "_")
    command_local(f"ssh-keyscan -H {agent_ip} > /tmp/{agent_file}.agent; cat /tmp/*.agent > ~/.ssh/known_hosts", stderr=subprocess.DEVNULL)