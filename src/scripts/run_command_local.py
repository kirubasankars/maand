import argparse
import os

import command_helper
import context_manager
import system_manager
import utils
import maand_agent
import const

if not os.path.exists(f"{const.WORKSPACE_PATH}/command.sh"):
    raise Exception("No command file found")


def run_command(agent_ip):
    values = context_manager.get_values(agent_ip)
    values = context_manager.load_secrets(values)
    print(values)
    command_helper.command_local(f"sh {const.WORKSPACE_PATH}/command.sh", env=values)


if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()

    parser = argparse.ArgumentParser()
    parser.add_argument('--no-check', action='store_true')
    parser.set_defaults(no_check=False)
    local_args, _ = parser.parse_known_args()

    with maand_agent.get_db() as db:
        cursor = db.cursor()
        system_manager.run(cursor, command_helper.scan_agent)
        namespace = maand_agent.get_namespace_id(cursor)
        os.environ.setdefault("NAMESPACE", namespace)
        update_seq = maand_agent.get_update_seq(cursor)
        os.environ.setdefault("UPDATE_SEQ", str(update_seq))
        if not local_args.no_check:
            system_manager.run(cursor, context_manager.validate_cluster_update_seq)

        system_manager.run(cursor, run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
