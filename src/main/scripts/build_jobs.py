import hashlib
import os
import uuid
import json

import maand
import job_data
import workspace
import const
import command_helper

import utils

logger = utils.get_logger()


def build_jobs(cursor):
    jobs = workspace.get_jobs()

    for job in jobs:
        manifest = workspace.get_job_manifest(job)
        files = workspace.get_job_files(job)

        roles = manifest.get("roles")
        certs = manifest.get("certs")
        commands = manifest.get("commands")

        job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(job)))
        certs_hash = hashlib.md5(json.dumps(certs).encode()).hexdigest()

        cursor.execute("INSERT INTO job_db.job (job_id, name, certs_md5_hash, deployment_seq) VALUES (?, ?, ?, 0)",
                       (job_id, job, certs_hash))

        for role in roles:
            cursor.execute("INSERT INTO job_db.job_roles (job_id, role) VALUES (?, ?)", (job_id, role,))

        for cert in certs:
            for name, config in cert.items():
                pkcs8 = config.get("pkcs8", 0)
                subject = config.get("subject", "")
                cursor.execute("INSERT INTO job_db.job_certs (job_id, name, pkcs8, subject) VALUES (?, ?, ?, ?)",
                               (job_id, name, pkcs8, subject,))

        for command, command_obj in commands.items():
            executed_ons = command_obj.get("executed_on", [])
            depend_on = command_obj.get("depend_on", {})
            for executed_on in executed_ons:
                depend_on_job = depend_on.get("job")
                if depend_on_job and depend_on_job not in jobs:
                    logger.error(f"{depend_on_job} job not found: command: {command}, depend on job: {depend_on_job}")
                depend_on_command = depend_on.get("command")
                depend_on_config = json.dumps(depend_on.get("config", {}))
                cursor.execute("INSERT INTO job_db.job_commands (job_id, job_name, name, executed_on, depend_on_job, depend_on_command, depend_on_config) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (job_id, job, command, executed_on, depend_on_job, depend_on_command, depend_on_config))

        for file in files:
            isdir = os.path.isdir(f"{const.WORKSPACE_PATH}/jobs/{file}")
            content = ""
            if not isdir:
                with open(f"{const.WORKSPACE_PATH}/jobs/{file}", 'rb') as f:
                    content = f.read()
            cursor.execute("INSERT INTO job_db.job_files (job_id, path, content, isdir) VALUES (?, ?, ?, ?)",
                           (job_id, file, content, isdir))

    sql = '''
WITH RECURSIVE job_command_seq AS (
    SELECT jc.job_name, 0 AS level FROM job_db.job_commands jc WHERE jc.depend_on_job IS NULL

    UNION ALL

    SELECT jc.job_name, jcs.level + 1 AS level
    FROM
        job_db.job_commands jc INNER JOIN job_command_seq jcs ON jc.depend_on_job = jcs.job_name
)
UPDATE job_db.job SET deployment_seq = t.deployment_seq FROM (
SELECT 
    DISTINCT job_name, deployment_seq
FROM 
    (SELECT job_name, (SELECT MAX(level) FROM job_command_seq jcs WHERE jcs.job_name = t.job_name) as deployment_seq FROM job_command_seq t) t1
ORDER BY deployment_seq) t WHERE job.name = t.job_name;
        '''

    cursor.executescript(sql)


def build():
    with maand.get_db() as db:
        cursor = db.cursor()
        job_data.setup_job_database(cursor)
        build_jobs(cursor)
        db.commit()
    db.execute("vacuum")


if __name__ == '__main__':
    command_helper.command_local(f"rm -rf {const.JOBS_DB_PATH}")
    build()