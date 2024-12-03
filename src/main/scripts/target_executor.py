import os

import maand
import command_helper
import context_manager
import utils

import job_health_check

def execute(p):
    job, agent_ip = p
    args = utils.get_args_agents_jobs_health_check()
    bucket = os.getenv("BUCKET")
    with maand.get_db() as db:
        cursor = db.cursor()

        agent_env = context_manager.get_agent_minimal_env(agent_ip)
        allocations = maand.get_allocations(cursor, job)

        agent_0_ip = allocations[0]
        command_helper.capture_command_remote(f"python3 /opt/agent/{bucket}/bin/runner.py {bucket} {args.target} --jobs {job}", env=agent_env, prefix=agent_ip)

        if agent_ip == agent_0_ip and args.health_check:
            job_health_check.health_check(cursor, [job], False)