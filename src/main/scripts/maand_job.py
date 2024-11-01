import glob
import hashlib
import importlib
import json

import const
import os.path
import sqlite3
import sys
import uuid

import workspace
from command_helper import command_local



def __get_connection():
    return sqlite3.connect(const.JOBS_DB_PATH)


def setup():
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS job (job_id TEXT PRIMARY KEY, name TEXT, certs_md5_hash)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_roles (job_id TEXT, role TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_certs (job_id TEXT, name TEXT, pkcs8 INT, subject TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_files (job_id TEXT, path TEXT, content BLOB, isdir BOOL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_commands (job_id TEXT, name TEXT, executed_on TEXT)")


def __build_jobs(db):
    jobs = workspace.get_jobs()

    for job in jobs:
        manifest = workspace.get_job_manifest(job)

        roles = manifest.get("roles")
        certs = manifest.get("certs")
        commands = manifest.get("commands")

        cursor = db.cursor()
        job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(job)))
        certs_hash = hashlib.md5(json.dumps(certs).encode()).hexdigest()
        cursor.execute("INSERT INTO job (job_id, name, certs_md5_hash) VALUES (?, ?, ?)", (job_id, job, certs_hash))

        for role in roles:
            cursor.execute("INSERT INTO job_roles (job_id, role) VALUES (?, ?)", (job_id, role,))

        for cert in certs:
            for name, config in cert.items():
                pkcs8 = config.get("pkcs8", 0)
                subject = config.get("subject", "")
                cursor.execute("INSERT INTO job_certs (job_id, name, pkcs8, subject) VALUES (?, ?, ?, ?)",
                               (job_id, name, pkcs8, subject,))

        for command, command_obj in commands.items():
            executed_ons = command_obj.get("executed_on", [])
            for executed_on in executed_ons:
                cursor.execute("INSERT INTO job_commands (job_id, name, executed_on) VALUES (?, ?, ?)",
                               (job_id, command, executed_on,))

        files = workspace.get_job_files(job)
        for file in files:
            isdir = os.path.isdir(f"{const.WORKSPACE_PATH}/jobs/{file}")
            content = ""
            if not isdir:
                with open(f"{const.WORKSPACE_PATH}/jobs/{file}", 'rb') as f:
                    content = f.read()
            cursor.execute("INSERT INTO job_files (job_id, path, content, isdir) VALUES (?, ?, ?, ?)",
                           (job_id, file, content, isdir))


def build():
    with __get_connection() as db:
        __build_jobs(db)
        db.commit()
    db.execute("vacuum")


def get_jobs():
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM job")
        rows = cursor.fetchall()
        return [row[0] for row in rows]


def get_job_certs(job):
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT jc.name, jc.pkcs8, jc.subject FROM job_certs jc JOIN job j ON j.job_id = jc.job_id WHERE j.name = ?", (job,))
        rows = cursor.fetchall()
        return [{"name": row[0], "pkcs8": row[1], "subject": row[2]}  for row in rows]


def copy_job(name, agent_dir):
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT path, content, isdir FROM job_files WHERE job_id = (SELECT job_id FROM job WHERE name = ?) AND path NOT LIKE ? ORDER BY isdir DESC", (name, f"{name}/_modules%"))
        rows = cursor.fetchall()

        for path, content, isdir in rows:
            if isdir:
                os.makedirs(f"{agent_dir}/jobs/{path}", exist_ok=True)
                continue
            with open(f"{agent_dir}/jobs/{path}", "wb") as f:
                f.write(content)


def execute_command(job, command, context):

    if "/commands" not in sys.path:
        sys.path.append("/commands")
    os.makedirs("/commands", exist_ok=True)

    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT path, content, isdir FROM job_files WHERE job_id = (SELECT job_id FROM job WHERE name = ?) AND path like ? ORDER BY isdir DESC", (job, f"{job}/_modules%"))
        rows = cursor.fetchall()

        for path, content, isdir in rows:
            if isdir:
                os.makedirs(f"/commands/{path}", exist_ok=True)
                continue
            with open(f"/commands/{path}", "wb") as f:
                f.write(content)

    job_command = importlib.import_module(f'{job}._modules.command_{command}')
    if "execute" in dir(job_command):
        job_command.execute(context)
    else:
        raise Exception("No execute method defined")


if __name__ == '__main__':
    command_local(f"rm -rf {const.JOBS_DB_PATH}")
    jobs = glob.glob(f"{const.WORKSPACE_PATH}/jobs/*/manifest.json")
    if jobs:
        setup()
        build()