import context_manager
import health_check_utils
import system_manager


def validate_cluster_id(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_id(agent_ip)


system_manager.run(validate_cluster_id)
system_manager.run(health_check_utils.health_check)
