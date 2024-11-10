import time
import utils
import job_command_executor

import job_data


def health_check(cursor):
    event = 'health_check'
    args = utils.get_args_jobs_concurrency()
    jobs_filter = args.jobs

    selected_jobs = []
    jobs = job_data.get_jobs(cursor)
    for job in jobs:
        if job_data.check_job_command_event(cursor, job, event, event):
            selected_jobs.append(job)

    if jobs_filter:
        selected_jobs = set(jobs_filter) & set(selected_jobs)

    jobs = []
    for job in selected_jobs:
        if job_data.check_job_command_event(cursor, job, event, event):
            jobs.append(job)

    for job in jobs:
        retry = 0
        while True:
            try:
                if not job_command_executor.execute_command(cursor, job, event, event):
                    raise Exception(f'job: {job} health check failed')
                break
            except Exception as e:
                if retry >= 100:
                    raise TimeoutError("Timed out waiting for agent to become healthy")
                retry = retry + 1
                print(f"{e} retrying...", flush=True)
                time.sleep(10)
