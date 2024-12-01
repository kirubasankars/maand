import time
import job_command_executor

import job_data
import utils

logger = utils.get_logger()

def health_check(cursor, jobs_filter, no_wait, interval=5, times=10):
    event = 'health_check'

    jobs = job_data.get_jobs(cursor)
    if jobs_filter:
        jobs = set(jobs_filter) & set(jobs)

    failed = False
    if not no_wait:
        for job in jobs:
            retry = 0
            while True:
                try:
                    job_commands = job_data.get_job_commands(cursor, job, event)
                    for command in job_commands:
                        if not job_command_executor.execute_job_event_command(cursor, job, command, event):
                            raise Exception(f'health check failed : {job}')
                        logger.info(f'health check succeeded : {job}')
                        break
                except Exception as e:
                    if retry >= times:
                        failed = True
                        logger.info(f'health check failed : {job}')
                        break
                    retry = retry + 1
                    logger.info(f'health check failed {job}. retrying...')
                    time.sleep(interval)

    if no_wait:
        for job in jobs:
            try:
                job_commands = job_data.get_job_commands(cursor, job, event)
                for command in job_commands:
                    if not job_command_executor.execute_job_event_command(cursor, job, command, event):
                        logger.info(f'health check failed : {job}')
                        failed = True
                    else:
                        logger.info(f'health check succeeded : {job}')
            except Exception as e:
                pass

    return failed