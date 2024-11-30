import copy
import multiprocessing
import os

import maand
import command_helper
import context_manager
import utils

import job_health_check

def execute(p):
    job, agent_ip = p
    args = utils.get_args_agents_jobs_health_check()
    bucket = os.getenv("BUCKET")

    with maand.get_db() as db:
        cursor = db.cursor()

        agent_env = context_manager.get_agent_minimal_env(agent_ip)
        allocations = maand.get_allocations(cursor, job)
        agent_0_ip = allocations[0]
        if agent_ip == agent_0_ip and args.health_check:
            job_health_check.health_check(cursor, [job], True)

        command_helper.capture_command_remote(f"python3 /opt/agent/{bucket}/bin/runner.py {bucket} {args.target} --jobs {job}", env=agent_env,log_file=f'/bucket/logs/{agent_ip}.log', prefix=agent_ip)

        if agent_ip == agent_0_ip and args.health_check:
            job_health_check.health_check(cursor, [job], False)

def run_target(job, allocations):
    work_items = []
    for agent_ip in allocations:
        work_items.append((job, agent_ip,))

    with multiprocessing.Pool(processes=len(work_items)) as pool:
        pool.map(execute, work_items)


def main():
    args = utils.get_args_agents_jobs_health_check()

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
                run_target(job, allocations)


if __name__ == "__main__":
    main()
