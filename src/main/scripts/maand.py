import sqlite3
import uuid

import const
from job_data import *


def get_db():
    db = sqlite3.connect(const.MAAND_DB_PATH)
    db.execute(f"ATTACH DATABASE '{const.JOBS_DB_PATH}' AS job_db;")
    return db


def setup_maand_database(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS bucket (bucket_id TEXT, update_seq INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agent (agent_id TEXT, agent_ip TEXT, detained INT, position INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agent_roles (agent_id TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agent_tags (agent_id TEXT, key TEXT, value INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agent_jobs (agent_id TEXT, job TEXT, disabled INT, removed INT)")
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


def update_update_seq(cursor, seq):
    cursor.execute("UPDATE bucket SET update_seq = ?", (seq,))


def get_agent_jobs(cursor, agent_ip):
    cursor.execute("SELECT aj.job, aj.disabled FROM agent a JOIN agent_jobs aj ON a.agent_id = aj.agent_id JOIN job_db.job j ON j.name = aj.job AND aj.removed = 0 AND a.agent_ip = ?", (agent_ip,))
    rows = cursor.fetchall()
    return {row[0]: {"disabled": row[1]} for row in rows}


def get_agent_removed_jobs(cursor, agent_ip):
    cursor.execute("select aj.job FROM agent_jobs aj JOIN agent a ON a.agent_id = aj.agent_id WHERE aj.removed = 1 AND agent_ip = ?", (agent_ip,))
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_agent_disabled_jobs(cursor, agent_ip):
    cursor.execute("select aj.job FROM agent_jobs aj JOIN agent a ON a.agent_id = aj.agent_id WHERE aj.disabled = 1 AND agent_ip = ?", (agent_ip,))
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_agents(cursor, roles_filter):
    if not roles_filter:
        roles_filter = ["agent"]
    roles_filter = [f"'{role}'" for role in roles_filter]
    roles_filter = ",".join(roles_filter)

    cursor.execute(f"SELECT DISTINCT agent_ip FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id WHERE a.detained = 0 AND ar.role IN ({roles_filter}) ORDER BY position;")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_allocations(cursor, job):
    cursor.execute("SELECT a.agent_ip FROM agent a JOIN agent_jobs aj ON a.agent_id = aj.agent_id INNER JOIN job_db.job j ON j.name = aj.job WHERE aj.job = ? ORDER BY a.agent_ip", (job, ))
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_agent_roles(cursor, agent_ip):
    if agent_ip:
        cursor.execute("SELECT DISTINCT role FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id AND agent_ip = ?;", (agent_ip,))
    else:
        cursor.execute("SELECT DISTINCT role FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id;",)
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_agent_tags(cursor, agent_ip):
    cursor.execute("SELECT key, value FROM agent a JOIN agent_tags at ON a.agent_id = at.agent_id WHERE a.agent_ip = ?", (agent_ip,))
    rows = cursor.fetchall()
    return {row[0]:row[1] for row in rows}


def get_agent_id(cursor, agent_ip):
    cursor.execute("SELECT agent_id FROM agent WHERE agent_ip = ?", (agent_ip,))
    row = cursor.fetchone()
    return row[0]