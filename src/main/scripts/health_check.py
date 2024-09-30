import context_manager
import run_job_command
import system_manager


def validate(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_id(agent_ip)
    context_manager.validate_cluster_update_seq(agent_ip)


if __name__ == '__main__':
    # TODO: jobs filter
    system_manager.run(validate)
    system_manager.run(run_job_command.health_check)
