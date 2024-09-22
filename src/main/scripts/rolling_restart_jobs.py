import command_helper
import context_manager
import health_check_utils
import system_manager


def validate_cluster_id(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_id(agent_ip)


def run_command(agent_ip):
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    health_check_utils.health_check(agent_ip)
    command_helper.command_remote("sh /opt/agent/bin/restart_jobs.sh", env=agent_env)
    health_check_utils.health_check(agent_ip)


system_manager.run(validate_cluster_id)
system_manager.run(run_command, concurrency=1)
