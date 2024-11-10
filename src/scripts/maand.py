import sqlite3
import uuid

import const

from job_data import *
from agent_data import *


def get_db():
    db = sqlite3.connect(const.MAAND_DB_PATH)
    db.execute(f"ATTACH DATABASE '{const.JOBS_DB_PATH}' AS job_db;\n")
    db.execute(f"ATTACH DATABASE '{const.AGENTS_DB_PATH}' AS agent_db;\n")
    return db


def setup_maand_database(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS namespace (namespace_id TEXT, update_seq INT)")
    cursor.execute("SELECT namespace_id FROM namespace")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO namespace (namespace_id, update_seq) VALUES (?, ?)", (str(uuid.uuid4()), 0))
    else:
        raise Exception("cluster is already initialized")


def get_namespace_id(cursor):
    cursor.execute("SELECT namespace_id FROM namespace")
    row = cursor.fetchone()
    return row[0]


def get_update_seq(cursor):
    cursor.execute("SELECT update_seq FROM namespace")
    row = cursor.fetchone()
    return row[0]


def update_seq(cursor, seq):
    cursor.execute("UPDATE namespace SET update_seq = ?", (seq,))


def export_env_namespace_update_seq(cursor):
    namespace = get_namespace_id(cursor)
    os.environ.setdefault("NAMESPACE", namespace)
    update_seq = get_update_seq(cursor)
    os.environ.setdefault("UPDATE_SEQ", str(update_seq))