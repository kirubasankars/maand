import os.path
import uuid
import workspace
import maand_job
from maand_agent import __get_connection

import const

def __plan_agents(db):
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
            cursor.execute("UPDATE agent SET position = ?, detained = 0 WHERE agent_id = ?", (position, agent_id,))
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


def __plan_allocated_jobs(db):
    disabled = workspace.get_disabled_jobs()
    disabled_jobs = disabled.get("jobs", {})
    disabled_agents = disabled.get("agents", [])

    cursor = db.cursor()
    cursor.execute("SELECT agent_id, agent_ip FROM agent")
    agents = cursor.fetchall()

    for agent_id, agent_ip in agents:
        cursor.execute("""
                       SELECT j.name FROM job_db.job j JOIN job_db.job_roles jr WHERE jr.job_id = j.job_id AND EXISTS(
                            SELECT 1 FROM agent a JOIN agent_roles ar on a.agent_id = ar.agent_id AND jr.role = ar.role AND a.agent_ip = ?
                       )
                       """, (agent_ip,))

        assigned_jobs = [row[0] for row in cursor.fetchall()]

        for job in assigned_jobs:

            disabled = agent_ip in disabled_agents
            if not disabled:
                job_disabled_agents = disabled_jobs.get(job, {}).get("agents", [])
                disabled = agent_ip in job_disabled_agents
                if len(job_disabled_agents) == 0:
                    disabled = job in disabled_jobs

            cursor.execute("SELECT * FROM agent_jobs WHERE job = ? AND agent_id = ?", (job, agent_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE agent_jobs SET disabled = ? WHERE job = ? AND agent_id = ?", (disabled, job, agent_id,))
            else:
                cursor.execute("INSERT INTO agent_jobs (job, agent_id, disabled, removed) VALUES (?, ?, ?, 0)", (job, agent_id, disabled))

        cursor.execute("SELECT job FROM agent_jobs WHERE agent_id = ?", (agent_id,))
        all_assigned_jobs = [row[0] for row in cursor.fetchall()]
        removed_jobs = list(set(all_assigned_jobs) ^ set(assigned_jobs))
        for job in removed_jobs:
            cursor.execute(f"UPDATE agent_jobs SET removed = 1 WHERE job = ? AND agent_id = ?", (job, agent_id,))

def __interceptor(db, action_type):
    cursor = db.cursor()
    cursor.execute("SELECT ( SELECT name FROM job j WHERE j.job_id = jp.job_id ) as name, source_job, command, config FROM job_db.job_plugins jp, job_db.job_commands jc WHERE jc.executed_on = ?", (action_type,))
    rows = cursor.fetchall()
    for row in rows:
        job, command_job, command, config = row
        maand_job.execute_command(command_job, command, (action_type, job, config))


def plan():
    with __get_connection() as db:
        __plan_agents(db)
        if os.path.exists(const.JOBS_DB_PATH):
            db.execute(f"ATTACH DATABASE '{const.JOBS_DB_PATH}' AS job_db;")
            #__interceptor(db, "pre_plan")
            __plan_allocated_jobs(db)
            #__interceptor(db, "post_plan")
        db.commit()


if __name__ == "__main__":
    plan()