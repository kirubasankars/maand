import sys

import command_helper

def statement(sql):
    with open("/tmp/sql.txt", "w") as f:
        f.write("ATTACH DATABASE '/workspace/maand.job.db' AS job_db;\n")
        f.write(".header on\n")
        f.write(".mode column\n")
        f.write(f"{sql}\n")

    command_helper.command_local("""
        sqlite3 /workspace/data/maand.agent.db < /tmp/sql.txt
    """)


if __name__ == "__main__":

    name = "namespace"
    if len(sys.argv) > 1:
        name = sys.argv[1]

    if name == "agents":
        statement("SELECT agent_id, agent_ip, detained, (SELECT GROUP_CONCAT(role) FROM agent_roles ar WHERE ar.agent_id = a.agent_id ORDER BY role) as roles FROM agent a")

    if name == "jobs":
        statement("SELECT job_id, name, (SELECT GROUP_CONCAT(role) FROM job_db.job_roles jr WHERE jr.job_id = j.job_id) as roles FROM job_db.job j")

    if name == "allocations":
        statement("SELECT a.agent_id, a.agent_ip, j.job_id, aj.job, aj.disabled FROM agent a JOIN agent_jobs aj ON a.agent_id = aj.agent_id JOIN job_db.job j ON j.name = aj.job")
