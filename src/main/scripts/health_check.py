import context_manager
import run_job_command_health_check
import system_manager


def validate(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_update_seq(agent_ip)


if __name__ == '__main__':
    system_manager.run(validate)
    system_manager.run(run_job_command_health_check.health_check)
