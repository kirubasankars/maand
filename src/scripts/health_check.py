import os
import utils

import context_manager
import run_job_command_health_check
import system_manager
import maand_agent


def validate(agent_ip):
    #context_manager.validate_cluster_update_seq(agent_ip)
    pass


if __name__ == '__main__':
    args = utils.get_args_jobs_concurrency()
    with maand_agent.get_db() as db:
        cursor = db.cursor()

        namespace = maand_agent.get_namespace_id(cursor)
        os.environ.setdefault("NAMESPACE", namespace)
        update_seq = maand_agent.get_update_seq(cursor)
        os.environ.setdefault("UPDATE_SEQ", str(update_seq))

        system_manager.run(cursor, validate)
        run_job_command_health_check.health_check()
