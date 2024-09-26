import os

import command_helper
import context_manager
import utils


def run_job_command(agent_ip, command):
    values = context_manager.get_values(agent_ip)
    values = context_manager.load_secrets(values)
    values["COMMAND"] = command
    agent_cmd_dir = f"/opt/commands/{agent_ip}"

    assigned_jobs = utils.get_assigned_jobs(agent_ip)
    for job in assigned_jobs:
        if (not os.path.exists(f"{agent_cmd_dir}/{job}/executed_setup.txt")
                and os.path.exists(f"/workspace/jobs/{job}/_commands/setup.sh")):
            os.makedirs(f"{agent_cmd_dir}/{job}", exist_ok=True)
            command_helper.command_local(f"""
                rsync -r /workspace/jobs/{job}/_commands/ {agent_cmd_dir}/{job}/; 
                cd {agent_cmd_dir}/{job} && bash {agent_cmd_dir}/{job}/setup.sh
            """)
            with open(f"{agent_cmd_dir}/{job}/executed_setup.txt", "w") as setup:
                setup.write(f"")
                setup.close()

        if os.path.exists(f"{agent_cmd_dir}/{job}/run.sh"):
            r = command_helper.command_local(f"cd {agent_cmd_dir}/{job} && bash {agent_cmd_dir}/{job}/run.sh",
                                             env=values)
            if r.returncode != 0:
                raise RuntimeError("Runtime Error")
