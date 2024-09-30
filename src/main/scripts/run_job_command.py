import os

import command_helper
import context_manager
import utils


def run_job_command(agent_ip, command, jobs_filter=None):
    values = context_manager.get_values(agent_ip)
    values = context_manager.load_secrets(values)
    values["COMMAND"] = command
    agent_cmd_dir = f"/opt/commands/{agent_ip}"

    jobs = jobs_filter
    if not jobs:
        jobs = utils.get_assigned_jobs(agent_ip)

    for job in jobs:
        if os.path.exists(f"{agent_cmd_dir}/{job}/run.sh"):
            r = command_helper.command_local(f"cd {agent_cmd_dir}/{job} && bash {agent_cmd_dir}/{job}/run.sh",
                                             env=values)
            if r.returncode != 0:
                raise RuntimeError("Runtime Error")