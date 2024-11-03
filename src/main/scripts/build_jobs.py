import hashlib
import os
import uuid
import json
import glob

import maand_job
import workspace
import const
import command_helper

def build_jobs(cursor):
    jobs = workspace.get_jobs()

    for job in jobs:
        manifest = workspace.get_job_manifest(job)

        roles = manifest.get("roles")
        certs = manifest.get("certs")
        commands = manifest.get("commands")

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
    with maand_job.get_db() as db:
        cursor = db.cursor()
        maand_job.setup(cursor)
        build_jobs(cursor)
        db.commit()
    db.execute("vacuum")


if __name__ == '__main__':
    found_manifest = glob.glob(f"{const.WORKSPACE_PATH}/jobs/*/manifest.json")
    if found_manifest:
        command_helper.command_local(f"rm -rf {const.JOBS_DB_PATH}")
        build()