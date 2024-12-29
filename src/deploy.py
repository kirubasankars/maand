import argparse
import os
import json
import const
import system_manager
import update_job
import alloc_command_executor
import command_helper
import context_manager
import job_health_check
import maand_data
from itertools import chain


def get_args():
    parser = argparse.ArgumentParser(description="Deploy and manage jobs.")
    parser.add_argument('--jobs', default="", help="Comma-separated list of jobs to process.")
    args = parser.parse_args()
    args.jobs = args.jobs.split(',') if args.jobs else []
    return args


def run_target(target, job, allocations, alloc_health_check_flag=False, job_health_check_flag=False):
    with maand_data.get_db() as db:
        cursor = db.cursor()

        # Run pre-target commands
        pre_commands = maand_data.get_job_commands(cursor, job, "pre_deploy")
        execute_commands(cursor, pre_commands, job, allocations, target)

        # Run main job control or default action
        job_control_commands = maand_data.get_job_commands(cursor, job, "job_control")
        if job_control_commands:
            execute_commands(cursor, job_control_commands, job, allocations, target, alloc_health_check_flag)
        else:
            execute_default_action(job, allocations, target, alloc_health_check_flag)

        # Perform job-level health checks if needed
        if job_health_check_flag:
            job_health_check.health_check(cursor, [job], wait=True)

        # Run post-target commands
        post_commands = maand_data.get_job_commands(cursor, job, "post_deploy")
        execute_commands(cursor, post_commands, job, allocations, target)


def execute_commands(cursor, commands, job, allocations, target, alloc_health_check=False):
    for command in commands:
        alloc_command_executor.prepare_command(cursor, job, command)
        for agent_ip in allocations:
            alloc_command_executor.execute_alloc_command(cursor, job, command, agent_ip, {"TARGET": target})
            if alloc_health_check:
                job_health_check.health_check(cursor, [job], wait=True)


def execute_default_action(job, allocations, target, alloc_health_check):
    bucket = os.getenv("BUCKET")
    for agent_ip in allocations:
        agent_env = context_manager.get_agent_minimal_env(agent_ip)
        command_helper.capture_command_remote(
            f"python3 /opt/agent/{bucket}/bin/runner.py {bucket} {target} --jobs {job}",
            env=agent_env, prefix=agent_ip
        )
        if alloc_health_check:
            with maand_data.get_db() as db:
                cursor = db.cursor()
                job_health_check.health_check(cursor, [job], wait=True)


def deploy_job(job):
    with maand_data.get_db() as db:
        cursor = db.cursor()
        allocations = maand_data.get_allocations(cursor, job)
        counts = maand_data.get_allocation_counts(cursor, job)
        new_allocations = maand_data.get_new_allocations(cursor, job)
        changed_allocations = maand_data.get_changed_allocations(cursor, job)
        removed_allocations = maand_data.get_removed_allocations(cursor, job)
        db.commit()

    if counts['unchanged'] == counts['total']:
        job_health_check.health_check(cursor, [job], wait=True)
    elif counts['removed'] == counts['total']: # job removed
        print("# job removed")
        run_target("stop", job, removed_allocations, alloc_health_check_flag=False, job_health_check_flag=False)
    elif counts['removed'] == 0 and counts['new'] == counts['total']: # job added
        print("# job added")
        run_target("start", job, allocations, alloc_health_check_flag=False, job_health_check_flag=True)
    elif counts['removed'] == 0 and counts['unchanged'] == 0 and counts['changed'] == counts['total']: # job modified
        print("# job modified")
        run_target("restart", job, allocations, alloc_health_check_flag=True, job_health_check_flag=False)
    elif counts['removed'] == 0 and counts['unchanged'] == 0 and counts['new'] > 0: # new alloctions added
        print("# new alloctions added")
        run_target("start", job, new_allocations, alloc_health_check_flag=False, job_health_check_flag=True)
    elif counts['changed'] > 0: # few alloctions modified
        print("# few alloctions modified")
        run_target("restart", job, changed_allocations, alloc_health_check_flag=True, job_health_check_flag=False)
    elif counts['removed'] > 0: # few alloctions removed
        print("# few alloctions removed")
        run_target("stop", job, removed_allocations, alloc_health_check_flag=True, job_health_check_flag=False)

def run_deploy(jobs):
    job_allocations = {}

    with maand_data.get_db() as db:
        cursor = db.cursor()
        for job in jobs:
            allocations = maand_data.get_allocations(cursor, job)
            job_allocations[job] = allocations

    jobs_agents = []
    for allocations in job_allocations.values():
        jobs_agents.extend(allocations)
    jobs_agents = list(set(jobs_agents))

    for agent_ip in jobs_agents:
        agent_removed_jobs = maand_data.get_agent_removed_jobs(cursor, agent_ip)
        agent_disabled_jobs = maand_data.get_agent_disabled_jobs(cursor, agent_ip)
        jobs_need_stop = jobs & list(chain(agent_removed_jobs, agent_disabled_jobs))
        for job in jobs_need_stop:
            deploy_job(job)

    with maand_data.get_db() as db:
        cursor = db.cursor()

        update_seq = maand_data.get_update_seq(cursor)
        next_update_seq = int(update_seq) + 1
        maand_data.update_update_seq(cursor, next_update_seq)
        bucket_id = maand_data.get_bucket_id(cursor)

        for job in jobs:
            allocations = job_allocations[job]

            for agent_ip in allocations:
                agent_dir = context_manager.get_agent_dir(agent_ip)
                command_helper.command_local(f"""
                    mkdir -p {agent_dir}/certs
                    rsync {const.SECRETS_PATH}/ca.crt {agent_dir}/certs/
                """)

                agent_id = maand_data.get_agent_id(cursor, agent_ip)
                with open(f"{agent_dir}/agent.txt", "w") as f:
                    f.write(agent_id)

                with open(f"{agent_dir}/bucket.txt", "w") as f:
                    f.write(bucket_id)

                update_seq = maand_data.get_update_seq(cursor)
                with open(f"{agent_dir}/update_seq.txt", "w") as f:
                    f.write(str(update_seq))

                agent_labels = maand_data.get_agent_labels(cursor, agent_ip)
                with open(f"{agent_dir}/labels.txt", "w") as f:
                    f.writelines("\n".join(agent_labels))

                agent_jobs = maand_data.get_agent_jobs(cursor, agent_ip)
                with open(f"{agent_dir}/jobs.json", "w") as f:
                    f.writelines(json.dumps(agent_jobs))

                command_helper.command_local(f"mkdir -p {agent_dir}/bin")
                command_helper.command_local(f"rsync -r /maand/agent/bin/ {agent_dir}/bin/")

    for job, allocations in job_allocations.items():
        for allocation_ip in allocations:
            update_job.update_allocation(job, allocation_ip) # copy files to agent dir

    for agent_ip in jobs_agents:
        agent_jobs = maand_data.get_agent_jobs(cursor, agent_ip)
        agent_removed_jobs = maand_data.get_agent_removed_jobs(cursor, agent_ip)
        context_manager.rsync_upload_agent_files(agent_ip, agent_jobs.keys(), agent_removed_jobs) # update changes

    for job in jobs:
        deploy_job(job)

def main():
    args = get_args()

    with maand_data.get_db() as db:
        cursor = db.cursor()

        # Update agents and system environment
        system_manager.run(cursor, command_helper.scan_agent)
        context_manager.export_env_bucket_update_seq(cursor)

        max_deployment_seq = maand_data.get_max_deployment_seq(cursor)
        for seq in range(max_deployment_seq + 1):
            jobs = maand_data.get_jobs(cursor, deployment_seq=seq)
            if args.jobs:
                jobs = list(set(jobs) & set(args.jobs))

            run_deploy(jobs)


if __name__ == "__main__":
    main()