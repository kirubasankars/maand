import command_helper
import context_manager
import health_check_utils
import system_manager
import utils
from src.main.scripts.run_command import agents


def validate_cluster_id(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_id(agent_ip)


def run_command(agent_ip):
    jobs = ""
    if jobs_filter:
        jobs = ",".join(jobs_filter)
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    health_check_utils.health_check(agent_ip)
    command_helper.command_remote(f"python /opt/agent/bin/runner.py restart {jobs}", env=agent_env)
    health_check_utils.health_check(agent_ip)


_, jobs_filter, _ = utils.args_filters(roles_filter=False, agents_filter=False, jobs_filter=True)
system_manager.run(validate_cluster_id)
system_manager.run(run_command, concurrency=1)
