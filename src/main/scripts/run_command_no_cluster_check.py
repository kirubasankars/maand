import os

import command_helper
import context_manager
import system_manager
import utils

if not os.path.exists("/workspace/command.sh"):
    raise Exception("No command file found")


def run_command(agent_ip):
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.command2_remote("/workspace/command.sh", env=agent_env)


roles_filter, _, agents_filter = utils.args_filters(roles_filter=True, agents_filter=True, jobs_filter=False)
system_manager.run(run_command, roles_filter=roles_filter, agents_filter=agents_filter)
