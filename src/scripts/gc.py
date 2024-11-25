import kv_manager
import maand


def clean_agents(cursor):
    cursor.execute("DELETE FROM agent_db.agent WHERE detained = 1")
    cursor.execute("DELETE FROM agent_db.agent_jobs WHERE removed = 1")

def clean():
    with maand.get_db() as db:
        cursor = db.cursor()
        clean_agents(cursor)
        db.commit()
    kv_manager.gc()

if __name__ == '__main__':
    clean()