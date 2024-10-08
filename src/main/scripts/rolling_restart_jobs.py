import run_job_command_health_check

import command_helper
import context_manager
import system_manager
import utils


def run_command(agent_ip):
    filtered_jobs, filter_applied = utils.get_filtered_jobs(agent_ip, jobs_filter=args.jobs, min_order=args.min_order, max_order=args.max_order)
    if not args.include_disabled:
        disabled_jobs = utils.get_disabled_jobs(agent_ip)
        filtered_jobs = list(set(filtered_jobs) - set(disabled_jobs))

    filtered_jobs = ",".join(filtered_jobs)
    agent_env = context_manager.get_agent_minimal_env(agent_ip)

    run_job_command_health_check.health_check(agent_ip)
    if filter_applied:
        if filtered_jobs:
            command_helper.command_remote(f"python /opt/agent/bin/runner.py restart --jobs {filtered_jobs}", env=agent_env)
    else:
        command_helper.command_remote(f"python /opt/agent/bin/runner.py restart", env=agent_env)
    run_job_command_health_check.health_check(agent_ip)


if __name__ == "__main__":
    args = utils.get_args_agents_jobs_concurrency()
    system_manager.run(context_manager.validate_cluster_update_seq)
    system_manager.run(run_command, concurrency=args.concurrency, agents_filter=args.agents_filter)
