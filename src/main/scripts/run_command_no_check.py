import os

import workspace
import command_helper
import context_manager
import system_manager
import utils
from context_manager import stop_the_world

if not os.path.exists("/workspace/command.sh"):
    raise Exception("No command file found")


def run_command(agent_ip):
    try:
        agent_env = context_manager.get_agent_minimal_env(agent_ip)
        r = command_helper.command2_remote("/workspace/command.sh", env=agent_env)
        if r.returncode != 0:
            raise Exception(r)
    except Exception as e:
        stop_the_world()


if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()
    system_manager.run(command_helper.scan_agent)
    system_manager.run(run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
