import copy
import importlib
import multiprocessing
import os

import job_command_executor

import utils
import maand
import target_executor


def run_target(job, allocations):
    work_items = []
    for agent_ip in allocations:
        work_items.append((job, agent_ip,))
    with multiprocessing.Pool(processes=len(work_items)) as pool:
        pool.map(target_executor.execute, work_items)


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

            os.environ.setdefault("TARGET", args.target)

            for job, allocations in job_allocations.items():
                event = "job_control"
                job_commands = maand.get_job_commands(cursor, job, event)
                if job_commands:
                    for command in job_commands:
                        job_command_executor.execute_job_event_command(cursor, job, command, event)
                else:
                    run_target(job, allocations)


if __name__ == "__main__":
    main()
