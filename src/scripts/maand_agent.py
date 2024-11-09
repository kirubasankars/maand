import uuid
import sqlite3

import const


def get_db():
    return sqlite3.connect(const.MAAND_DB_PATH)


def setup(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS namespace (namespace_id TEXT, update_seq INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agent (agent_id TEXT, agent_ip TEXT, detained INT, position INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agent_roles (agent_id TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agent_tags (agent_id TEXT, key TEXT, value INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS agent_jobs (agent_id TEXT, job TEXT, disabled INT, removed INT)")

    cursor.execute("SELECT namespace_id FROM namespace")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO namespace (namespace_id, update_seq) VALUES (?, ?)", (str(uuid.uuid4()), 0))
    else:
        raise Exception("cluster is already initialized")


def get_agent_jobs(cursor, agent_ip):
    cursor.execute("SELECT aj.job, aj.disabled FROM agent a JOIN agent_jobs aj ON a.agent_id = aj.agent_id JOIN job_db.job j ON j.name = aj.job AND a.agent_ip = ?", (agent_ip,))
    rows = cursor.fetchall()
    return {row[0]: {"disabled": row[1]} for row in rows}


def get_agents(cursor, roles_filter):
    if not roles_filter:
        roles_filter = ["agent"]
    roles_filter = [f"'{role}'" for role in roles_filter]
    roles_filter = ",".join(roles_filter)

    cursor.execute(f"SELECT DISTINCT agent_ip FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id WHERE a.detained = 0 AND ar.role IN ({roles_filter}) ORDER BY position;")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_first_agent_for_job(cursor, job):
    cursor.execute("SELECT a.agent_ip FROM agent a JOIN agent_jobs aj ON a.agent_id = aj.agent_id INNER JOIN job_db.job j ON j.name = aj.job WHERE aj.job = ? ORDER BY a.agent_ip LIMIT 1", (job, ))
    agent_0_ip, = cursor.fetchone()
    return agent_0_ip


def get_agent_roles(cursor, agent_ip):
    if agent_ip:
        cursor.execute(
            f"SELECT DISTINCT role FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id AND agent_ip = ?;", (agent_ip,))
    else:
        cursor.execute(
            f"SELECT DISTINCT role FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id;",)
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_agent_tags(cursor, agent_ip):
    cursor.execute(f"SELECT key, value FROM agent a JOIN agent_tags at ON a.agent_id = at.agent_id WHERE a.agent_ip = ?", (agent_ip,))
    rows = cursor.fetchall()
    return {row[0]:row[1] for row in rows}


def get_agent_id(cursor, agent_ip):
    cursor.execute(f"SELECT agent_id FROM agent WHERE agent_ip = ?", (agent_ip,))
    row = cursor.fetchone()
    return row[0]


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