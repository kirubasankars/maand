import argparse
import os

import command_helper
import const
import context_manager
import job_health_check
import maand
import system_manager

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--roles', default="")
    parser.add_argument('--concurrency', default="4", type=int)
    parser.set_defaults(no_check=False)
    args = parser.parse_args()

    if args.agents:
        args.agents = args.agents.split(',')
    if args.roles:
        args.roles = args.roles.split(',')

    return args

def run_command(agent_ip):
    env = context_manager.get_agent_env(agent_ip)
    with maand.get_db() as db:
        cursor = db.cursor()

        jobs = maand.get_agent_jobs(cursor, agent_ip)
        job_health_check.health_check(cursor, jobs, True)
        command_helper.capture_command_file_remote(f"{const.WORKSPACE_PATH}/command.sh", env, prefix=agent_ip)
        job_health_check.health_check(cursor, jobs, False)

if __name__ == "__main__":
    if not os.path.exists(f"{const.WORKSPACE_PATH}/command.sh"):
        raise Exception("No command file found")

    args = get_args()

    with maand.get_db() as db:
        cursor = db.cursor()
        maand.export_env_bucket_update_seq(cursor)
        system_manager.run(cursor, context_manager.validate_cluster_update_seq)
        system_manager.run(cursor, run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
