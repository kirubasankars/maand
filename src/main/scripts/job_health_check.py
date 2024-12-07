import time
import job_command_executor

import job_data
import utils

def health_check(cursor, jobs_filter, no_wait, interval=5, times=10):
    logger = utils.get_logger()
    event = 'health_check'

    # Get filtered jobs
    jobs = job_data.get_jobs(cursor)
    if jobs_filter:
        jobs = set(jobs_filter) & set(jobs)

    failed = False

    def execute_health_check(job):
        """Executes health check commands for a single job."""
        nonlocal failed
        try:
            job_commands = job_data.get_job_commands(cursor, job, event)
            for command in job_commands:
                if not job_command_executor.execute_job_event_command(cursor, job, command, event):
                    failed = True
                    return False
            logger.info(f'Health check succeeded: {job}')
            return True
        except Exception as e:
            logger.error(f'Exception during health check for {job}: {str(e)}')
            failed = True
            return False

    if not no_wait:
        # Perform health checks with retries
        for job in jobs:
            for attempt in range(times):
                if execute_health_check(job):
                    break
                logger.info(f'Health check failed for {job}. Retrying... ({attempt + 1}/{times})')
                time.sleep(interval)
            else:
                logger.info(f'Health check permanently failed for {job} after {times} retries.')

    else:
        # Perform health checks without retries
        for job in jobs:
            execute_health_check(job)

    return failed
