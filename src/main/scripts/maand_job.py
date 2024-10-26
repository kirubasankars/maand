import importlib
import json
import os.path
import sqlite3
import sys
import uuid

import workspace

def __get_connection():
    return sqlite3.connect('workspace/maand.job.db')


def setup():
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS job (job_id TEXT, name TEXT, position INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_roles (job_id TEXT, role TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_certs (job_id TEXT, name TEXT, pkcs8 INT, subject TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_files (job_id TEXT, path TEXT, content BLOB, isdir BOOL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_commands (job_id TEXT, name TEXT, executed_on TEXT, availability TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_plugins (job_id TEXT, source_job TEXT, command TEXT, config TEXT)")


def __build_jobs(db):
    jobs = workspace.get_jobs()

    db.execute("DELETE FROM job_roles")
    db.execute("DELETE FROM job_certs")
    db.execute("DELETE FROM job_files")
    db.execute("DELETE FROM job_commands")
    db.execute("DELETE FROM job_plugins")
    db.execute("DELETE FROM job")

    for job in jobs:
        manifest = workspace.get_job_manifest(job)

        roles = manifest.get("roles")
        position = manifest.get("order")
        certs = manifest.get("certs")
        commands = manifest.get("commands")
        plugins = manifest.get("plugins")

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
                cursor.execute("INSERT INTO job_certs (job_id, name, pkcs8, subject) VALUES (?, ?, ?, ?)",
                               (job_id, name, pkcs8, subject,))

        for command, command_obj in commands.items():
            executed_on = command_obj.get("executed_on", [])
            availability = command_obj.get("availability", "self")
            for on in executed_on:
                cursor.execute("INSERT INTO job_commands (job_id, name, executed_on, availability) VALUES (?, ?, ?, ?)",
                               (job_id, command, on, availability,))

        for plugin in plugins:
            source_job = plugin.get("job")
            command = plugin.get("command")
            config = plugin.get("config")
            cursor.execute("INSERT INTO job_plugins (job_id, source_job, command, config) VALUES (?, ?, ?, ?)",
                           (job_id, source_job, command, json.dumps(config)))

        files = workspace.get_job_files(job)
        for file in files:
            isdir = os.path.isdir(f"/workspace/jobs/{file}")
            content = ""
            if not isdir:
                with open(f"/workspace/jobs/{file}", 'rb') as f:
                    content = f.read()
            cursor.execute("INSERT INTO job_files (job_id, path, content, isdir) VALUES (?, ?, ?, ?)",
                           (job_id, file, content, isdir))


def build():
    setup()
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
    build()