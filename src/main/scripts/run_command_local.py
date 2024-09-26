import os

import command_helper
import context_manager
import system_manager
import utils

if not os.path.exists("/workspace/command.sh"):
    raise Exception("No command file found")


def validate_cluster_id(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_id(agent_ip)


def run_command(agent_ip):
    values = context_manager.get_values(agent_ip)
    values = context_manager.load_secrets(values)
    agent_dir = context_manager.get_agent_dir(agent_ip)
    command_helper.command_local("sh /workspace/command.sh", cwd=agent_dir, env=values)


roles, agents = utils.args_roles_agents()
system_manager.run(validate_cluster_id)
system_manager.run(run_command, roles_filter=roles, agents_filter=agents)
