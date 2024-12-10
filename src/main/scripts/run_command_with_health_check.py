import os

import command_helper
import const
import context_manager
import job_health_check
import maand
import system_manager
import utils

if not os.path.exists(f"{const.WORKSPACE_PATH}/command.sh"):
    raise Exception("No command file found")


def run_command(agent_ip):
    env = context_manager.get_agent_env(agent_ip)
    with maand.get_db() as db:
        cursor = db.cursor()

        jobs = maand.get_agent_jobs(cursor, agent_ip)
        job_health_check.health_check(cursor, jobs, True)
        command_helper.capture_command_file_remote(f"{const.WORKSPACE_PATH}/command.sh", env, prefix=agent_ip)
        job_health_check.health_check(cursor, jobs, False)


if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()

    with maand.get_db() as db:
        cursor = db.cursor()
        maand.export_env_bucket_update_seq(cursor)
        system_manager.run(cursor, context_manager.validate_cluster_update_seq)
        system_manager.run(cursor, run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
