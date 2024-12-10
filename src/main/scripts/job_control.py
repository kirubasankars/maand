import argparse
import copy
import os

import command_helper
import context_manager
import alloc_command_executor
import job_health_check
import maand
import utils


def get_args_agents_jobs_health_check():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--jobs', default="")
    parser.add_argument('--target', default="", required=True)
    parser.add_argument('--job_health_check', action='store_true')
    parser.add_argument('--alloc_health_check', action='store_true')
    parser.set_defaults(job_health_check=False)
    parser.set_defaults(alloc_health_check=False)

    args = parser.parse_args()

    if args.agents:
        args.agents = args.agents.split(',')
    else:
        args.agents = []
    if args.jobs:
        args.jobs = args.jobs.split(',')
    else:
        args.jobs = []

    return args


def run_target(target, job, allocations):
    args = get_args_agents_jobs_health_check()
    alloc_work_items = utils.split_list(allocations, 1)
    with maand.get_db() as db:
        cursor = db.cursor()
        job_commands = maand.get_job_commands(cursor, job, "job_control")
        if len(job_commands) == 0:
            for work_item in alloc_work_items:
                for agent_ip in work_item:
                    bucket = os.getenv("BUCKET")
                    agent_env = context_manager.get_agent_minimal_env(agent_ip)
                    command_helper.capture_command_remote(f"python3 /opt/agent/{bucket}/bin/runner.py {bucket} {target} --jobs {job}", env=agent_env, prefix=agent_ip)
                    if args.alloc_health_check:
                        job_health_check.health_check(cursor, [job], wait=True)
            if args.job_health_check:
                job_health_check.health_check(cursor, [job], wait=True)
        else:
            alloc_command_executor.prepare_command(cursor, job, "job_control")
            for command in job_commands:
                for work_item in alloc_work_items:
                    for agent_ip in work_item:
                        alloc_command_executor.execute_alloc_command(job, command, agent_ip, {"TARGET": args.target})
                        if args.alloc_health_check:
                            job_health_check.health_check(cursor, [job], wait=True)
                if args.job_health_check:
                    job_health_check.health_check(cursor, [job], wait=True)


def main():
    args = get_args_agents_jobs_health_check()

    with maand.get_db() as db:
        cursor = db.cursor()

        maand.export_env_bucket_update_seq(cursor)
        max_deployment_seq = maand.get_max_deployment_seq(cursor)

        for seq in range(0, max_deployment_seq + 1):

            jobs = maand.get_jobs(cursor, deployment_seq=seq)
            if args.jobs:
                jobs = list(set(jobs) & set(args.jobs))

            job_allocations = {}
            for job in jobs:
                allocations = maand.get_allocations(cursor, job)
                if args.agents:
                    allocations = list(set(allocations) & set(args.agents))

                if args.target != "stop":
                    allocations_clone = copy.deepcopy(allocations)
                    allocations = []
                    for agent_ip in allocations_clone:
                        agent_jobs = maand.get_agent_jobs(cursor, agent_ip)
                        agent_jobs = {key: value for key, value in agent_jobs.items() if value.get("disabled") == 0}
                        if job in agent_jobs:
                            allocations.append(agent_ip)

                if allocations:
                    job_allocations[job] = allocations

            for job, allocations in job_allocations.items():
                run_target(args.target, job, allocations)


if __name__ == "__main__":
    main()
