import sqlite3
import uuid

import const

from job_data import *
from agent_data import *

def get_db():
    db = sqlite3.connect(const.MAAND_DB_PATH)
    db.execute(f"ATTACH DATABASE '{const.JOBS_DB_PATH}' AS job_db;")
    db.execute(f"ATTACH DATABASE '{const.AGENTS_DB_PATH}' AS agent_db;")
    return db


def setup_maand_database(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS bucket (bucket_id TEXT, update_seq INT)")
    cursor.execute("SELECT bucket_id FROM bucket")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO bucket (bucket_id, update_seq) VALUES (?, ?)", (str(uuid.uuid4()), 0))
    else:
        raise Exception("cluster is already initialized")


def get_bucket_id(cursor):
    cursor.execute("SELECT bucket_id FROM bucket")
    row = cursor.fetchone()
    return row[0]


def get_update_seq(cursor):
    cursor.execute("SELECT update_seq FROM bucket")
    row = cursor.fetchone()
    return row[0]


def update_seq(cursor, seq):
    cursor.execute("UPDATE bucket SET update_seq = ?", (seq,))


def export_env_bucket_update_seq(cursor):
    bucket = get_bucket_id(cursor)
    os.environ.setdefault("BUCKET", bucket)
    update_seq = get_update_seq(cursor)
    os.environ.setdefault("UPDATE_SEQ", str(update_seq))