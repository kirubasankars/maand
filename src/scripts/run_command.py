import argparse
import os.path

import command_helper
import context_manager
import system_manager
import utils

import const
import maand_agent

if not os.path.exists(f"{const.WORKSPACE_PATH}/command.sh"):
    raise Exception("No command file found")


def run_command(agent_ip):
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.command2_remote(f"{const.WORKSPACE_PATH}/command.sh", env=agent_env)


if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()

    parser = argparse.ArgumentParser()
    parser.add_argument('--no-check', action='store_true')
    parser.set_defaults(no_check=False)
    local_args, _ = parser.parse_known_args()

    with maand_agent.get_db() as db:
        cursor = db.cursor()
        namespace = maand_agent.get_namespace_id(cursor)
        os.environ.setdefault("NAMESPACE", namespace)
        system_manager.run(cursor, command_helper.scan_agent)
        if not local_args.no_check:
            system_manager.run(cursor, context_manager.validate_cluster_update_seq)

        system_manager.run(cursor, run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
