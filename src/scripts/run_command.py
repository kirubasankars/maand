
import command_helper
import context_manager
import system_manager
import utils

import const
import maand

import os

if not os.path.exists(f"{const.WORKSPACE_PATH}/command.sh"):
    raise Exception("No command file found")


def run_command(agent_ip):
    env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.capture_command_file_remote(
        f"{const.WORKSPACE_PATH}/command.sh", env,
        f'{const.BUCKET_PATH}/logs/{agent_ip}.log',
        agent_ip
    )


if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency(allow_no_check=True)

    with maand.get_db() as db:
        cursor = db.cursor()

        maand.export_env_bucket_update_seq(cursor)
        system_manager.run(cursor, command_helper.scan_agent)

        if not args.no_check:
            system_manager.run(cursor, context_manager.validate_cluster_update_seq)

        system_manager.run(
            cursor,
            run_command,
            concurrency=args.concurrency,
            roles_filter=args.roles,
            agents_filter=args.agents,
        )