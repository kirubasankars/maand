import os

import command_helper
import context_manager
import utils


def run_command(command=None):
    context_manager.validate_cluster_id()

    agent_ip = os.getenv("AGENT_IP")
    assigned_jobs = utils.get_assigned_jobs(agent_ip)

    values = context_manager.get_values()
    if command is None:
        command = os.getenv("COMMAND")
    values["COMMAND"] = command

    with open("/opt/agent/context.env", "w") as f:
        for key, value in values.items():
            f.write("{}={}\n".format(key, value))

    for job in assigned_jobs:
        if os.path.exists(f"/workspace/jobs/{job}/command/run.sh"):
            command_helper.command_local(f"""
                mkdir -p /commands/{job};
                rsync -r /workspace/jobs/{job}/command/ /commands/{job}/;
                cd /commands/{job} && bash /commands/{job}/run.sh
            """)


if __name__ == "__main__":
    run_command()
