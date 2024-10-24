import uuid
import sqlite3

def __get_connection():
    return sqlite3.connect('/workspace/maand.agent.db')


def setup():
    with __get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS cluster (cluster_id TEXT, update_seq INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS agent (agent_id TEXT, agent_ip TEXT, detained INT, position INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS agent_roles (agent_id TEXT, role TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS agent_tags (agent_id TEXT, key TEXT, value INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS agent_jobs (agent_id TEXT, job TEXT, disabled INT)")

        cursor.execute("SELECT cluster_id FROM cluster")
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO cluster (cluster_id, update_seq) VALUES (?, ?)", (str(uuid.uuid4().hex), 0))
        else:
            raise Exception("cluster is already initialized")

        connection.commit()


def get_agent_jobs(agent_ip):
    with __get_connection() as db:
        db.execute("ATTACH DATABASE '/workspace/maand.job.db' AS job_db;")
        cursor = db.cursor()
        cursor.execute("SELECT j.name, aj.disabled, j.position FROM agent a JOIN agent_jobs aj ON a.agent_id = aj.agent_id JOIN job_db.job j ON j.name = aj.job AND a.agent_ip = ? ORDER BY j.position", (agent_ip,))
        rows = cursor.fetchall()
        return {row[0]: {"disabled": row[1], "order": row[2] } for row in rows}


def get_agent_jobs_by_order(agent_ip):
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT j.name, j.position FROM agent a JOIN agent_jobs aj ON a.agent_id = aj.agent_id JOIN job j ON j.job_id = aj.job_id AND a.agent_ip = ? ORDER BY position", (agent_ip,))
        rows = cursor.fetchall()
        jobs = {}
        for row in rows:
            position = row[1]
            name = row[0]
            if position not in jobs:
                jobs[position] = []
            jobs[position].append(name)
        return jobs


def get_agents(roles_filter=None):
    if not roles_filter:
        roles_filter = ["agent"]
    roles_filter = [f"'{role}'" for role in roles_filter]
    roles_filter = ",".join(roles_filter)
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT DISTINCT agent_ip FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id WHERE ar.role IN ({roles_filter}) ORDER BY position;")
        rows = cursor.fetchall()
        return [row[0] for row in rows]


def get_agent_roles(agent_ip=None):
    with __get_connection() as db:
        cursor = db.cursor()
        if agent_ip:
            cursor.execute(
                f"SELECT DISTINCT role FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id AND agent_ip = ?;", (agent_ip,))
        else:
            cursor.execute(
                f"SELECT DISTINCT role FROM agent a JOIN agent_roles ar ON a.agent_id = ar.agent_id;",)
        rows = cursor.fetchall()
        return [row[0] for row in rows]


def get_agent_tags(agent_ip):
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT key, value FROM agent a JOIN agent_tags at ON a.agent_id = at.agent_id WHERE a.agent_ip = ?", (agent_ip,))
        rows = cursor.fetchall()
        return {row[0]:row[1] for row in rows}


def get_agent_id(agent_ip):
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute(f"SELECT agent_id FROM agent WHERE agent_ip = ?", (agent_ip,))
        row = cursor.fetchone()
        return row[0]


def get_filtered_agent_jobs(jobs, jobs_filter=None, min_order=0, max_order=100):
    filtered_jobs = {}
    if jobs_filter:
        for job_filter in jobs_filter:
            if job_filter in jobs:
                filtered_jobs[job_filter] = jobs[job_filter]
    else:
        jobs_filter = []
        filtered_jobs = jobs

    filtered_jobs2 = {}
    for name, job in filtered_jobs.items():
        if min_order <= job["order"] < max_order:
            filtered_jobs2[name] = job

    if min_order == 0 and max_order == 100:
        filtered_jobs2 = filtered_jobs

    return filtered_jobs2, len(jobs_filter) > 0 or min_order != 0 or max_order != 100


def get_cluster_id():
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT cluster_id FROM cluster")
        row = cursor.fetchone()
        return row[0]


def get_update_seq():
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT update_seq FROM cluster")
        row = cursor.fetchone()
        return row[0]


def update_seq(seq):
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("UPDATE cluster SET update_seq = ?", (seq,))
        db.commit()