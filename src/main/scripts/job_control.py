import os
import sys

import maand_agent
import command_helper
import context_manager
import system_manager
import utils


def run_command(agent_ip):
    jobs = maand_agent.get_agent_jobs(agent_ip)
    filtered_jobs, filter_applied = maand_agent.get_filtered_agent_jobs(jobs, jobs_filter=args.jobs, min_order=args.min_order, max_order=args.max_order)

    if not args.include_disabled:
        disabled_jobs = [name for name, job in jobs.items() if job.get("disabled", 0) == 1]
        filtered_jobs = list(set(filtered_jobs.keys()) - set(disabled_jobs))

    filtered_jobs = ",".join(filtered_jobs)
    agent_env = context_manager.get_agent_minimal_env(agent_ip)

    if filter_applied:
        if filtered_jobs:
            command_helper.command_remote(f"python3 /opt/agent/bin/runner.py {cmd} --jobs {filtered_jobs}", env=agent_env)
    else:
        command_helper.command_remote(f"python3 /opt/agent/bin/runner.py {cmd}", env=agent_env)


if __name__ == "__main__":
    cmd = os.getenv("CMD")
    args = utils.get_args_agents_jobs_concurrency()
    system_manager.run(context_manager.validate_cluster_update_seq)
    system_manager.run(run_command, concurrency=args.concurrency, agents_filter=args.agents)
