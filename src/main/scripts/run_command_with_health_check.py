import os

import command_helper
import context_manager
import health_check_utils
import system_manager
import utils

if not os.path.exists("/workspace/command.sh"):
    raise Exception("No command file found")


def run_command(agent_ip):
    values = context_manager.get_values(agent_ip)
    values = context_manager.load_secrets(values)

    health_check_utils.health_check(agent_ip)
    command_helper.command2_remote("/workspace/command.sh", env=values)
    health_check_utils.health_check(agent_ip)


if __name__ == "__main__":
    agents_filter, roles_filter, concurrency = utils.get_args_agents_roles_concurrency()
    system_manager.run(context_manager.validate_cluster_update_seq)
    system_manager.run(run_command, concurrency=concurrency, roles_filter=roles_filter, agents_filter=agents_filter)
