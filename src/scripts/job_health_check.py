import time
import job_command_executor

import job_data


def health_check(cursor, jobs_filter, no_wait, interval=1, times=10):
    event = 'health_check'

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

    failed = False
    if not no_wait:
        for job in jobs:
            retry = 0
            while True:
                try:
                    if not job_command_executor.execute_command(cursor, job, event, event):
                        raise Exception(f'health check failed : {job}')
                    print(f'health check succeeded : {job}', flush=True)
                    break
                except Exception as e:
                    if retry >= times:
                        failed = True
                        print(f'health check failed : {job}', flush=True)
                        break
                    retry = retry + 1
                    print(f"health check failed {job}. retrying...", flush=True)
                    time.sleep(interval)

    if no_wait:
        for job in jobs:
            try:
                if not job_command_executor.execute_command(cursor, job, event, event):
                    print(f'health check failed : {job}', flush=True)
                    failed = True
                else:
                    print(f'health check succeeded : {job}', flush=True)
            except Exception as e:
                pass

    return failed