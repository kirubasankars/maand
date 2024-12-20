import maand
import utils
import build_agents
import build_jobs
import build_allocations
import build_variables
import build_certs

logger = utils.get_logger()

def build():
    with maand.get_db() as db:
        cursor = db.cursor()
        try:
            build_agents.build(cursor)
            build_jobs.build(cursor)
            build_allocations.build(cursor)
            build_variables.build(cursor)
            build_certs.build(cursor)
        except Exception as e:
            db.rollback()
            raise e


if __name__ == "__main__":
    build()
