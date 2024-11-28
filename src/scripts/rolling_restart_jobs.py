import os

import maand
import command_helper
import context_manager
import system_manager
import utils
import const

import job_health_check

def run_command(agent_ip):
    cmd = "restart"
    bucket = os.getenv("BUCKET")
    args = utils.get_args_agents_jobs_concurrency()

    with maand.get_db() as db:
        cursor = db.cursor()

        agent_jobs = maand.get_agent_jobs(cursor, agent_ip)
        agent_jobs = {key: value for key, value in agent_jobs.items() if value.get("disabled") == 0}

        jobs = list(agent_jobs.keys())
        if args.jobs:
            jobs = list(set(jobs) & set(args.jobs))

        if jobs:
            filtered_jobs = ",".join(jobs)
            agent_env = context_manager.get_agent_minimal_env(agent_ip)

            job_health_check.health_check(cursor, jobs, True)
            command_helper.capture_command_remote(f"python3 /opt/agent/{bucket}/bin/runner.py {bucket} {cmd} --jobs {filtered_jobs}",
                                                  env=agent_env,
                                                  log_file=f'{const.LOGS_FOLDER}/{agent_ip}.log',
                                                  prefix=agent_ip)
            job_health_check.health_check(cursor, jobs, False, 2, 50)


def run():
    args = utils.get_args_agents_jobs_concurrency()

    with maand.get_db() as db:
        cursor = db.cursor()

        maand.export_env_bucket_update_seq(cursor)
        system_manager.run(cursor, context_manager.validate_cluster_update_seq)
        system_manager.run(cursor, run_command, concurrency=args.concurrency, agents_filter=args.agents)


if __name__ == "__main__":
    run()