import os
import sqlite3

import const


def get_db():
    return sqlite3.connect(const.JOBS_DB_PATH)

def attach_job_db(target):
    target.execute(f"ATTACH DATABASE '{const.JOBS_DB_PATH}' AS job_db;\n")

def setup(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS job (job_id TEXT PRIMARY KEY, name TEXT, certs_md5_hash TEXT, deployment_seq INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS job_roles (job_id TEXT, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS job_certs (job_id TEXT, name TEXT, pkcs8 INT, subject TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS job_files (job_id TEXT, path TEXT, content BLOB, isdir BOOL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS job_commands (job_id TEXT, job_name TEXT, name TEXT, executed_on TEXT, depend_on_job TEXT, depend_on_command TEXT, depend_on_config TEXT)")


def get_jobs(cursor):
    cursor.execute("SELECT name FROM job")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_job_certs_config(cursor, job):
    cursor.execute("SELECT jc.name, jc.pkcs8, jc.subject FROM job_certs jc JOIN job j ON j.job_id = jc.job_id WHERE j.name = ?", (job,))
    rows = cursor.fetchall()
    return [{"name": row[0], "pkcs8": row[1], "subject": row[2]}  for row in rows]


def get_job_md5_hash(cursor, job):
    cursor.execute("SELECT certs_md5_hash FROM job WHERE name = ?", (job,))
    row = cursor.fetchone()
    return row[0]


def check_job_command_event(cursor, job, command, event):
    cursor.execute("SELECT 1 FROM job_commands WHERE job_name = ? AND name = ? AND executed_on = ?", (job, command, event))
    row = cursor.fetchone()
    if not row:
        return False
    return True


def copy_job(cursor, name, agent_dir):
    cursor.execute("SELECT path, content, isdir FROM job_files WHERE job_id = (SELECT job_id FROM job WHERE name = ?) AND path NOT LIKE ? ORDER BY isdir DESC", (name, f"{name}/_modules%"))
    rows = cursor.fetchall()

    for path, content, isdir in rows:
        if isdir:
            os.makedirs(f"{agent_dir}/jobs/{path}", exist_ok=True)
            continue
        with open(f"{agent_dir}/jobs/{path}", "wb") as f:
            f.write(content)