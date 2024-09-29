import os

import command_helper
import context_manager
import system_manager
import utils

if not os.path.exists("/workspace/command.sh"):
    raise Exception("No command file found")


def run_command(agent_ip):
    values = context_manager.get_values(agent_ip)
    values = context_manager.load_secrets(values)
    command_helper.command_local("sh /workspace/command.sh", env=values)


if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()
    system_manager.run(context_manager.validate_cluster_update_seq)
    system_manager.run(run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
