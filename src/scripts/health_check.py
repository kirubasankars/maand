import sys

import utils

import job_health_check
import maand


if __name__ == '__main__':
    args = utils.get_args_healthcheck()

    with maand.get_db() as db:
        cursor = db.cursor()
        no_wait = args.no_wait
        maand.export_env_bucket_update_seq(cursor)
        failed = job_health_check.health_check(cursor, args.jobs, no_wait)
        if failed:
            sys.exit(1)
