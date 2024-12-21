import kv_manager
import maand


def clean_agents(cursor):
    cursor.execute("DELETE FROM agent_roles WHERE agent_id IN (SELECT agent_id FROM agent WHERE detained = 1)")
    cursor.execute("DELETE FROM agent_tags WHERE agent_id IN (SELECT agent_id FROM agent WHERE detained = 1)")
    cursor.execute("DELETE FROM agent WHERE detained = 1")
    cursor.execute("DELETE FROM agent_jobs WHERE removed = 1")
    cursor.execute("DELETE FROM kv_db.key_value WHERE deleted = 1")


def clean():
    with maand.get_db() as db:
        cursor = db.cursor()
        clean_agents(cursor)
        kv_manager.gc(cursor)
        db.commit()



if __name__ == '__main__':
    clean()
