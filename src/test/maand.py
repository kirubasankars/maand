import json
import os
import shutil
import subprocess


def initialize():
    try:
        subprocess.run(["bash", "/scripts/start.sh", "initialize"])
        fix_maand_config()
    except subprocess.CalledProcessError as e:
        print(e)


def build():
    try:
        subprocess.run(["bash", "/scripts/start.sh", "build_jobs"])
        subprocess.run(["bash", "/scripts/start.sh", "plan"])
    except subprocess.CalledProcessError as e:
        print(e)


def deploy(jobs=None):
    try:
        shutil.rmtree("/opt/agents")
        l = ["bash", "/scripts/start.sh", "deploy"]
        if jobs:
            l.append(f"--jobs={jobs}")
        subprocess.run(l)
    except subprocess.CalledProcessError as e:
        print(e)


def start_jobs(jobs=None):
    try:
        shutil.rmtree("/opt/agents")
        l = ["bash", "/scripts/start.sh", "start_jobs"]
        if jobs:
            l.append(f"--jobs={jobs}")
        subprocess.run(l)
    except subprocess.CalledProcessError as e:
        print(e)


def stop_jobs(jobs=None):
    try:
        shutil.rmtree("/opt/agents")
        l = ["bash", "/scripts/start.sh", "stop_jobs"]
        if jobs:
            l.append(f"--jobs={jobs}")
        subprocess.run(l)
    except subprocess.CalledProcessError as e:
        print(e)


def restart_jobs(jobs=None):
    try:
        shutil.rmtree("/opt/agents")
        l = ["bash", "/scripts/start.sh", "restart_jobs"]
        if jobs:
            l.append(f"--jobs={jobs}")
        subprocess.run(l)
    except subprocess.CalledProcessError as e:
        print(e)


def run_command_no_check(command):
    # Write to command.sh and execute the script
    with open("/workspace/command.sh", "w") as f:
        f.write(command)

    # Run the bash script
    subprocess.run(["bash", "/scripts/start.sh", "run_command_no_check"])


def run_command(command):
    # Write to command.sh and execute the script
    with open("/workspace/command.sh", "w") as f:
        f.write(command)

    # Run the bash script
    subprocess.run(["bash", "/scripts/start.sh", "run_command"])


def clean():
    # List of files to delete
    files_to_delete = [
        "/workspace/variables.env",
        "/workspace/secrets.env",
        "/workspace/maand.job.db",
        "/workspace/maand.agent.db",
        "/workspace/kv.db",
        "/workspace/ca.crt",
        "/workspace/ca.key"
    ]

    # Loop over and try to delete each file
    for file_path in files_to_delete:
        try:
            os.unlink(file_path)
        except Exception as e:
            pass

    try:
        fix_maand_config()
        # Write to command.sh and execute the script
        with open("/workspace/command.sh", "w") as f:
            f.write("rm -rf /opt/agent")

        # Run the bash script
        subprocess.run(["bash", "/scripts/start.sh", "run_command_no_check"])
    except Exception as e:
        print(e)
        pass


def fix_maand_config():
    with open("/workspace/maand.config.env", "w") as f:
        f.write("CA_TTL=3650\n")
        f.write("USE_SUDO=1\n")
        f.write("SSH_USER=agent\n")
        f.write("SSH_KEY=homelab.key\n")


def make_job(name, roles):
    os.makedirs(f"/workspace/jobs/{name}", exist_ok=True)
    with open(f"/workspace/jobs/{name}/manifest.json", "w") as f:
        f.write(json.dumps({"roles": roles}))

    with open("/tests/Makefile.sample", "rb") as rf:
        with open(f"/workspace/jobs/{name}/Makefile", "wb") as wf:
            wf.write(rf.read())


def agents_ip(role):
    with open("/workspace/agents.json") as f:
        data = json.load(f)
    if role:
        return [item for item in data if role in item.get("roles")]
    return data


def sync_files(agents):
    for agent in agents:
        with open("/workspace/command.sh", "w") as f:
            f.write(f'rsync -vr --delete --rsync-path="sudo rsync" --rsh="ssh -i /workspace/homelab.key" agent@{agent}:/opt/agent/ /{agent} > /dev/null; sync')
        subprocess.run(["bash", "/workspace/command.sh"])


def tree(path):
    subprocess.run(["tree", path])