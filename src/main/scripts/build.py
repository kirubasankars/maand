import uuid
import sqlite3
import workspace

def __get_connection():
    return sqlite3.connect('/workspace/maand.db')


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


def __build_allocated_certs(db):
    pass


def build():
    with __get_connection() as db:
        __build_agents(db)
        __build_jobs(db)
        __build_allocated_jobs(db)
        __build_allocated_certs(db)
        db.commit()


if __name__ == "__main__":
    build()