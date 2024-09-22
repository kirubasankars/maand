import time

import run_job_command


def health_check(agent_ip):
    time.sleep(10)
    retry = 0
    while True:
        try:
            run_job_command.run_job_command(agent_ip, "health_check")
            break
        except Exception as e:
            if retry >= 100:
                raise TimeoutError("Timed out waiting for agent to become healthy")
            retry = retry + 1
            time.sleep(5)
