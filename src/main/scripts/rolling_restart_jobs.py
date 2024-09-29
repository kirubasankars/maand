import command_helper
import context_manager
import health_check_utils
import system_manager
import utils


def run_command(agent_ip):
    filtered_jobs = utils.get_filtered_jobs(agent_ip, jobs_filter=args.jobs, min_order=args.min_order, max_order=args.max_order)
    disabled_jobs = utils.get_disabled_jobs(agent_ip)
    filtered_jobs = list(set(filtered_jobs) - set(disabled_jobs))

    filtered_jobs = ",".join(filtered_jobs)
    agent_env = context_manager.get_agent_minimal_env(agent_ip)

    health_check_utils.health_check(agent_ip)
    if filtered_jobs:
        command_helper.command_remote(f"python /opt/agent/bin/runner.py restart --jobs {filtered_jobs}", env=agent_env)
    else:
        command_helper.command_remote(f"python /opt/agent/bin/runner.py restart", env=agent_env)
    health_check_utils.health_check(agent_ip)


if __name__ == "__main__":
    args = utils.get_args_agents_jobs_concurrency()
    system_manager.run(context_manager.validate_cluster_update_seq)
    system_manager.run(run_command, concurrency=args.concurrency, agents_filter=args.agents_filter)
