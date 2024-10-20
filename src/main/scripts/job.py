import os.path
import sqlite3
import uuid

import workspace

def __get_connection():
    return sqlite3.connect('/workspace/maand.jobs.db')


def setup():
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS job (job_id TEXT, name TEXT, position INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_roles (job_id TEXT, role TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_certs (job_id TEXT, name TEXT, pkcs8 INT, subject TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS job_files (job_id TEXT, path TEXT, content BLOB, isdir BOOL)")


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
                cursor.execute("INSERT INTO job_certs (job_id, name, pkcs8, subject) VALUES (?, ?, ?, ?)",
                               (job_id, name, pkcs8, subject,))

        files = workspace.get_job_files(job)
        for file in files:
            isdir = os.path.isdir(f"/workspace/jobs/{file}")
            content = ""
            if not isdir:
                with open(f"/workspace/jobs/{file}", 'rb') as f:
                    content = f.read()
            cursor.execute("INSERT INTO job_files (job_id, path, content, isdir) VALUES (?, ?, ?, ?)", (job_id, file, content, isdir))


def build():
    with __get_connection() as db:
        __build_jobs(db)


def get_jobs():
    with __get_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM job")
        rows = cursor.fetchall()
        return [row[0] for row in rows]


if __name__ == '__main__':
    build()