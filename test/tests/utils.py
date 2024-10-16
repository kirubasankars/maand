import json

from maand import *


def initialize_cluster():
    if os.path.exists("/workspace/ca.key"):
        os.remove("/workspace/ca.key")
    if os.path.exists("/workspace/ca.crt"):
        os.remove("/workspace/ca.crt")
    if os.path.exists("/workspace/maand.db"):
        os.remove("/workspace/maand.db")
    if os.path.exists("/workspace/kv.db"):
        os.remove("/workspace/kv.db")

    write_command(["rm -rf /opt/agent"])
    run(initialize())
    run(plan())
    run(run_command_no_check())



def write_command(lines):
    lines = [f"{l}\n" for l in lines]
    with open("/workspace/command.sh", "w") as f:
        f.writelines(lines)


def sync():
    write_command(["mkdir -p /workspace/tmp/ && rsync --delete --rsync-path=\"sudo rsync\" -vrc --rsh=\"ssh -i /workspace/$SSH_KEY\" $SSH_USER@$AGENT_IP:/opt/agent/ /workspace/tmp/$AGENT_IP"])


def get_agents():
    with open("/workspace/agents.json", "r") as f:
        return json.load(f)