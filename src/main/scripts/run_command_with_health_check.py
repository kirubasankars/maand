import os

import command_helper
import context_manager
import health_check_utils
import system_manager

if not os.path.exists("/workspace/command.sh"):
    raise Exception("No command file found")


def validate_cluster_id(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_id(agent_ip)


def run_command(agent_ip):
    values = context_manager.get_values(agent_ip)
    values = context_manager.load_secrets(values)

    health_check_utils.health_check(agent_ip)
    command_helper.command2_remote("/workspace/command.sh", env=values)
    health_check_utils.health_check(agent_ip)


system_manager.run(validate_cluster_id)
system_manager.run(run_command, concurrency=1)
