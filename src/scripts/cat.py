import sys
import maand
import const
import command_helper

def statement(sql, no_rows_found_msg):
    with open("/tmp/sql.txt", "w") as f:
        f.write(f"ATTACH DATABASE '{const.JOBS_DB_PATH}' AS job_db;\n")
        f.write(f"ATTACH DATABASE '{const.AGENTS_DB_PATH}' AS agent_db;\n")
        f.write(f"ATTACH DATABASE '{const.KV_DB_PATH}' AS kv_db;\n")
        f.write(".header on\n")
        f.write(".mode column\n")
        f.write(f"{sql}\n")

    with maand.get_db() as db:
        db.execute(f"ATTACH DATABASE '{const.KV_DB_PATH}' AS kv_db;")
        cursor = db.cursor()
        cursor.execute(sql)
        if len(cursor.fetchall()) == 0:
            print(no_rows_found_msg)
        else:
            command_helper.command_local(f"""
                sqlite3 {const.MAAND_DB_PATH} < /tmp/sql.txt
            """)


if __name__ == "__main__":

    name = "namespace"
    if len(sys.argv) > 1:
        name = sys.argv[1]

    if name == "agents":
        statement("SELECT agent_id, agent_ip, detained, (SELECT GROUP_CONCAT(role) FROM agent_db.agent_roles ar WHERE ar.agent_id = a.agent_id ORDER BY role) as roles FROM agent_db.agent a", "no agents found")

    if name == "jobs":
        statement("SELECT DISTINCT job_id, name, (CASE WHEN (SELECT COUNT(1) FROM agent_db.agent_jobs aj WHERE j.name = aj.job AND aj.disabled = 0) > 0 THEN 0 ELSE 1 END) AS disabled, deployment_seq, (SELECT GROUP_CONCAT(role) FROM job_db.job_roles jr WHERE jr.job_id = j.job_id) as roles FROM job_db.job j ORDER BY deployment_seq, name", "no jobs found")

    if name == "allocations":
        statement("SELECT a.agent_ip, aj.job, aj.disabled, aj.removed FROM agent_db.agent a JOIN agent_db.agent_jobs aj ON a.agent_id = aj.agent_id LEFT JOIN job_db.job j ON j.name = aj.job ORDER BY aj.job", "no allocations found")

    if name == "job_commands":
        statement("SELECT job_name, name as command_name, executed_on, depend_on_job, depend_on_command, depend_on_config  FROM job_commands ORDER BY job_name, name", "no commands found")

    if name == "kv":
        statement("SELECT * FROM (SELECT key, namespace, max(version) as version, ttl, created_date, rotatable, deleted FROM kv_db.key_value GROUP BY key, namespace) t ORDER BY namespace, key, version", "no key values found")