import maand
import kv_manager
import utils
import workspace

logger = utils.get_logger()


def build_allocated_jobs(cursor):
    disabled = workspace.get_disabled_jobs()
    disabled_jobs = disabled.get("jobs", {})
    disabled_agents = disabled.get("agents", [])
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
                cursor.execute("UPDATE agent_jobs SET disabled = ?, removed = 0 WHERE job = ? AND agent_id = ?", (disabled, job, agent_id,))
            else:
                cursor.execute("INSERT INTO agent_jobs (job, agent_id, disabled, removed) VALUES (?, ?, ?, 0)", (job, agent_id, disabled))

        cursor.execute("SELECT job FROM agent_jobs WHERE agent_id = ?", (agent_id,))
        all_assigned_jobs = [row[0] for row in cursor.fetchall()]
        removed_jobs = list(set(all_assigned_jobs) ^ set(assigned_jobs))
        for job in removed_jobs:
            cursor.execute(f"UPDATE agent_jobs SET removed = 1 WHERE job = ? AND agent_id = ?", (job, agent_id,))

        cursor.execute("UPDATE agent_jobs SET disabled = 1 WHERE agent_id IN (SELECT agent_id FROM agent WHERE agent_ip = ? AND detained = 1)",(agent_ip,))


def validate_resource_limit(cursor):
    cursor.execute("SELECT agent_ip, CAST(available_memory_mb AS FLOAT) AS available_memory_mb, CAST(available_cpu AS FLOAT) AS available_cpu FROM agent")
    agents = cursor.fetchall()

    for agent_ip, available_memory_mb, available_cpu  in agents:
        jobs = maand.get_agent_jobs(cursor, agent_ip).keys()

        total_allocated_memory = 0
        total_allocated_cpu = 0
        for job in jobs:
            min_memory_mb, max_memory_mb, min_cpu, max_cpu, ports = maand.get_job_resource_limits(cursor, job)

            namespace = f"vars/job/{job}"
            job_cpu = float(kv_manager.get(namespace, "CPU") or "0") or max_cpu
            job_memory = float(kv_manager.get(namespace, "MEMORY") or "0") or max_memory_mb

            if min_memory_mb > 0 and job_memory <= min_memory_mb:
                raise Exception(
                    f"Memory allocation for job {job} is invalid. "
                    f"Minimum allowed: {min_memory_mb} MB, Allocated: {job_memory} MB."
                )

            if max_memory_mb > 0 and job_memory > max_memory_mb:
                raise Exception(
                    f"Memory allocation for job {job} is invalid. "
                    f"Maximum allowed: {max_memory_mb} MB, Allocated: {job_memory} MB."
                )

            if min_cpu > 0 and job_cpu <= min_cpu:
                raise Exception(
                    f"CPU allocation for job {job} is invalid. "
                    f"Minimum allowed: {min_cpu} MHZ, Allocated: {job_cpu} MHZ."
                )

            if max_cpu > 0 and job_cpu > max_cpu:
                raise Exception(
                    f"CPU allocation for job {job} is invalid. "
                    f"Maximum allowed: {max_cpu} MHZ, Allocated: {job_cpu} MHZ."
                )

            total_allocated_memory += job_memory
            total_allocated_cpu += job_cpu

            if total_allocated_memory > available_memory_mb:
                raise Exception(
                    f"Agent {agent_ip} has insufficient memory. "
                    f"Available: {available_memory_mb} MB, Required: {total_allocated_memory} MB."
                )
            if total_allocated_cpu > available_cpu:
                raise Exception(
                    f"Agent {agent_ip} has insufficient CPU. "
                    f"Available: {available_cpu} MHZ, Required: {total_allocated_cpu} MHZ."
                )


def build():
    with maand.get_db() as db:
        try:
            cursor = db.cursor()
            build_allocated_jobs(cursor)
            validate_resource_limit(cursor)
            db.commit()
        except Exception as e:
            logger.fatal(e)
            db.rollback()


if __name__ == "__main__":
    build()
