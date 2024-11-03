import utils

import context_manager
import run_job_command_health_check
import system_manager


def validate(agent_ip):
    context_manager.validate_cluster_update_seq(agent_ip)


if __name__ == '__main__':
    args = utils.get_args_jobs_concurrency()

    system_manager.run(validate)
    system_manager.run(run_job_command_health_check.health_check, concurrency=args.concurrency)
