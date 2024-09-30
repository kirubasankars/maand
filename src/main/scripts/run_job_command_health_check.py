import utils
import time

import run_job_command


def health_check(agent_ip):
    args = utils.get_args_jobs()
    filtered_jobs = utils.get_filtered_jobs(agent_ip, jobs_filter=args.jobs, min_order=args.min_order, max_order=args.max_order)
    if not args.include_disabled:
        disabled_jobs = utils.get_disabled_jobs(agent_ip)
        filtered_jobs = list(set(filtered_jobs) - set(disabled_jobs))

    time.sleep(10)
    retry = 0
    while True:
        try:
            run_job_command.run_job_command(agent_ip, "health_check", jobs_filter=filtered_jobs)
            break
        except Exception as e:
            if retry >= 100:
                raise TimeoutError("Timed out waiting for agent to become healthy")
            retry = retry + 1
            time.sleep(5)
