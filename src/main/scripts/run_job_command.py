import os
import shutil

import maand
import command_helper
import context_manager
import utils


def run_job_command(agent_ip, command):
    mutex = utils.FileMutex("/tmp/lock")

    args = utils.get_args_jobs_concurrency()
    filtered_jobs, filtered = utils.get_filtered_jobs(agent_ip, jobs_filter=args.jobs, min_order=args.min_order, max_order=args.max_order)
    if not args.include_disabled:
        disabled_jobs = [name for name, job in maand.get_agent_jobs(agent_ip).items() if job["disabled"]]
        filtered_jobs = list(set(filtered_jobs) - set(disabled_jobs))

    if filtered and not filtered_jobs:
        raise Exception("No jobs found")

    values = context_manager.get_values(agent_ip)
    values = context_manager.load_secrets(values)
    values["COMMAND"] = command
    modules_dir = f"/opt/modules"

    for job in filtered_jobs:

        mutex.acquire()
        if not os.path.exists(f"{modules_dir}/{job}/run.sh"):
            if os.path.exists(f"/workspace/jobs/{job}/_modules"):
                shutil.copytree(f"/workspace/jobs/{job}/_modules", f"{modules_dir}/{job}/")
        mutex.release()

        if os.path.exists(f"{modules_dir}/{job}/run.sh"):
           r = command_helper.command_local(f"cd {modules_dir}/{job} && bash {modules_dir}/{job}/run.sh", env=values)
           if r.returncode != 0:
               raise RuntimeError("Runtime Error")