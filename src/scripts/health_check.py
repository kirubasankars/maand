import utils

import job_health_check
import maand


if __name__ == '__main__':
    args = utils.get_args_jobs_concurrency()

    with maand.get_db() as db:
        cursor = db.cursor()

        maand.export_env_namespace_update_seq(cursor)
        job_health_check.health_check(cursor)
