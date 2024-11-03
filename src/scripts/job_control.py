import os

import maand_agent
import command_helper
import context_manager
import system_manager
import utils


def run_command(agent_ip):
    agent_jobs = maand_agent.get_agent_jobs(agent_ip)

    missing_jobs = set(args.jobs) - set(agent_jobs.keys())
    if missing_jobs:
        raise Exception(f"No jobs found: {missing_jobs}")

    jobs = args.jobs or agent_jobs.keys()
    filtered_jobs = ",".join(jobs)
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.command_remote(f"python3 /opt/agent/bin/runner.py {cmd} --jobs {filtered_jobs}", env=agent_env)


if __name__ == "__main__":
    cmd = os.getenv("CMD")
    args = utils.get_args_agents_jobs_concurrency()
    system_manager.run(context_manager.validate_cluster_update_seq)
    system_manager.run(run_command, concurrency=args.concurrency, agents_filter=args.agents)
