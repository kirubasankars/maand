import sqlite3
import uuid

import workspace

def __get_connection():
    return sqlite3.connect('/workspace/maand.db')


def setup():
    with __get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS cluster (cluster_id TEXT, update_seq INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS agent (agent_id TEXT, agent_ip TEXT, detained INT, position INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS agent_roles (agent_id TEXT, role TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS agent_tags (agent_id TEXT, key TEXT, value INT)")

        cursor.execute("CREATE TABLE IF NOT EXISTS job (job_id TEXT, name TEXT, position INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_roles (job_id TEXT, role TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_certs (job_id TEXT, name TEXT, pkcs8 INT, subject TEXT)")

        cursor.execute("CREATE TABLE IF NOT EXISTS agent_jobs (agent_id TEXT, job_id TEXT, disabled INT)")

        cursor.execute("SELECT cluster_id FROM cluster")
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO cluster (cluster_id, update_seq) VALUES (?, ?)", (str(uuid.uuid4().hex), 0))
        else:
            raise Exception("cluster is already initialized")

        connection.commit()


def __build_agents(db):
    agents = workspace.get_agents()
    for index, agent in enumerate(agents):
        agent_ip = agent["host"]
        position = index + 1

        cursor = db.cursor()
        cursor.execute("SELECT * FROM agent WHERE agent_ip = ?", (agent_ip,))
        row = cursor.fetchone()

        if row:
            agent_id = row[0]
        else:
            agent_id = str(uuid.uuid4().hex)

        if row:
            cursor.execute("UPDATE agent SET position = ? WHERE agent_id = ?", (position, agent_id,))
        else:
            cursor.execute("INSERT INTO agent (agent_id, agent_ip, detained, position) VALUES (?, ?, 0, ?)", (agent_id, agent_ip, position,))


        cursor.execute("DELETE FROM agent_roles WHERE agent_id = ?", (agent_id,))
        roles = agent.get("roles", [])
        roles.append("agent")
        roles = list(set(roles))

        for role in roles:
            cursor.execute("INSERT INTO agent_roles (agent_id, role) VALUES (?, ?)", (agent_id, role,))

        cursor.execute("DELETE FROM agent_tags WHERE agent_id = ?", (agent_id,))
        tags = agent.get("tags", {})
        for key, value in tags.items():
            cursor.execute("INSERT INTO agent_tags (agent_id, key, value) VALUES (?, ?, ?)", (agent_id, key, str(value),))

    cursor = db.cursor()
    cursor.execute("SELECT agent_ip FROM agent")
    rows = cursor.fetchall()

    host_ips = [agent["host"] for agent in agents]
    agent_ips = [row[0] for row in rows]
    missing_agents = list(set(agent_ips) - set(host_ips))

    for agent_ip in missing_agents:
        cursor.execute("UPDATE agent SET detained = 1 WHERE agent_ip = ?", (agent_ip,))


def __build_jobs(db):
    jobs = workspace.get_jobs()

    db.execute("DELETE FROM job_roles")
    db.execute("DELETE FROM job_certs")

    for job in jobs:
        manifest = workspace.get_job_manifest(job)

        roles = manifest.get("roles")
        position = manifest.get("order")
        certs = manifest.get("certs")

        cursor = db.cursor()
        cursor.execute("SELECT * FROM job WHERE name = ?", (job,))
        row = cursor.fetchone()
        if row:
            job_id = row[0]
        else:
            job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(job)).hex)

        if row:
            cursor.execute("UPDATE job SET position = ? WHERE job_id = ?", (position, job_id,))
        else:
            cursor.execute("INSERT INTO job (job_id, name, position) VALUES (?, ?, ?)", (job_id, job, position))

        for role in roles:
            cursor.execute("INSERT INTO job_roles (job_id, role) VALUES (?, ?)", (job_id, role,))

        for cert in certs:
            for name, config in cert.items():
                pkcs8 = config.get("pkcs8", 0)
                subject = config.get("subject", "")
                cursor.execute("INSERT INTO job_certs (job_id, name, pkcs8, subject) VALUES (?, ?, ?, ?)", (job_id, name, pkcs8, subject,))


def __build_allocated_jobs(db):
    disabled = workspace.get_disabled_jobs()
    disabled_jobs = disabled.get("jobs", [])
    disabled_agents = disabled.get("agents", [])

    cursor = db.cursor()
    cursor.execute("SELECT agent_id, agent_ip FROM agent")
    agents = cursor.fetchall()

    for agent_id, agent_ip in agents:
        cursor.execute("""
                       SELECT j.job_id, j.name FROM job j JOIN job_roles jr WHERE jr.job_id = j.job_id AND EXISTS(
                            SELECT 1 FROM agent a JOIN agent_roles ar on a.agent_id = ar.agent_id AND jr.role = ar.role AND a.agent_ip = ?
                       )
                       """, (agent_ip,))
        assigned_jobs = cursor.fetchall()

        for job_id, job in assigned_jobs:

            disabled = agent_ip in disabled_agents
            if not disabled:
                job_disabled_agents = disabled_jobs.get(job, {}).get("agents", [])
                disabled = agent_ip in job_disabled_agents
                if len(job_disabled_agents) == 0:
                    disabled = job in disabled_jobs

            cursor.execute("SELECT * FROM agent_jobs WHERE job_id = ? AND agent_id = ?", (job_id, agent_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE agent_jobs SET disabled = ? WHERE job_id = ? AND agent_id = ?", (disabled, job_id, agent_id,))
            else:
                cursor.execute("INSERT INTO agent_jobs (job_id, agent_id, disabled) VALUES (?, ?, ?)", (job_id, agent_id, disabled))


def build():
    with __get_connection() as db:
        __build_agents(db)
        __build_jobs(db)
        __build_allocated_jobs(db)
        db.commit()


def get_agent_jobs(agent_ip):
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT j.name, aj.disabled, j.position FROM agent a JOIN agent_jobs aj ON a.agent_id = aj.agent_id JOIN job j ON j.job_id = aj.job_id AND a.agent_ip = ? ORDER BY j.position", (agent_ip,))
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

    return filtered_jobs2, len(jobs_filter) > 0 or min_order != 0 or max_order != 99


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


if __name__ == '__main__':
    build()