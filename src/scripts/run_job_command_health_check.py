import time
import utils
import job_command_executor
import maand_job


def health_check():
    event = 'health_check'

    selected_jobs = []
    with maand_job.get_db() as db:
        cursor = db.cursor()
        jobs = maand_job.get_jobs(cursor)
        for job in jobs:
            if maand_job.check_job_command_event(cursor, job, event, event):
                selected_jobs.append(job)

    args = utils.get_args_jobs_concurrency()
    jobs_filter = args.jobs

    if jobs_filter:
        selected_jobs = set(jobs_filter) & set(selected_jobs)

    retry = 0
    while True:
        try:
            for job in selected_jobs:
                if maand_job.check_job_command_event(cursor, job, event, event):
                    job_command_executor.execute_command(job, event, event)
            break
        except Exception as e:
            if retry >= 100:
                raise TimeoutError("Timed out waiting for agent to become healthy")
            retry = retry + 1
            print(f"{e} retrying...", flush=True)
            time.sleep(10)
