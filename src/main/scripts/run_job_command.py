import os
import time

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
        if os.path.exists(f"{agent_cmd_dir}/{job}/run.sh"):
            r = command_helper.command_local(f"cd {agent_cmd_dir}/{job} && bash {agent_cmd_dir}/{job}/run.sh",
                                             env=values)
            if r.returncode != 0:
                raise RuntimeError("Runtime Error")


def health_check(agent_ip):
    time.sleep(10)
    retry = 0
    while True:
        try:
            run_job_command(agent_ip, "health_check")
            break
        except Exception as e:
            if retry >= 100:
                raise TimeoutError("Timed out waiting for agent to become healthy")
            retry = retry + 1
            time.sleep(5)
