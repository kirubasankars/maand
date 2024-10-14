from maand import *


def initialize_cluster():
    if os.path.exists("/workspace/ca.key"):
        os.remove("/workspace/ca.key")
    if os.path.exists("/workspace/ca.crt"):
        os.remove("/workspace/ca.crt")
    if os.path.exists("/workspace/maand.db"):
        os.remove("/workspace/maand.db")

    write_command(["rm -rf /opt/agent"])

    run(run_command_no_check())
    run(initialize())


def write_command(lines):
    lines = [f"{l}\n" for l in lines]
    with open("/workspace/command.sh", "w") as f:
        f.writelines(lines)