import configparser
import hashlib
import json
import os
import uuid

import command_helper
import const
import job_data
import kv_manager
import maand
import utils
import workspace

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
            executed_on = command_obj.get("executed_on")
            depend_on = command_obj.get("depend_on", {})
            if executed_on and executed_on in ["direct", "job_control", "health_check"]:
                depend_on_job = depend_on.get("job")
                if depend_on_job and depend_on_job not in jobs:
                    logger.error(f"{depend_on_job} job not found: command: {command}, depend on job: {depend_on_job}")
                depend_on_command = depend_on.get("command")
                depend_on_config = json.dumps(depend_on.get("config", {}))
                cursor.execute("INSERT INTO job_db.job_commands (job_id, job_name, name, executed_on, depend_on_job, depend_on_command, depend_on_config) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (job_id, job, command, executed_on, depend_on_job, depend_on_command, depend_on_config))
            else:
                logger.error("The commands must include an 'executed_on'. The 'value' must be one of the following: 'direct', 'health_check', or 'job_control'.")
                logger.error(f"job: {job}, command: {command}")

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


def build_maand_jobs_conf(cursor, path):
    # TODO: reversed key check
    if os.path.exists(path):
        config_parser = configparser.ConfigParser()
        config_parser.read(path)

        jobs = maand.get_jobs(cursor)
        for job in jobs:
            namespace = f"vars/job/{job}"
            name = f"{job}.variables"
            keys = []
            if config_parser.has_section(name):
                keys = config_parser.options(name)
                for key in keys:
                    key = key.upper()
                    value =  config_parser.get(name, key)
                    kv_manager.put_key_value(namespace, key, value)

            keys = [key.upper() for key in keys]
            all_keys = kv_manager.get_keys(namespace)
            missing_keys = list(set(all_keys) ^ set(keys))
            for key in missing_keys:
                kv_manager.delete_key(namespace, key)

        agents = maand.get_agents(cursor, roles_filter=None)
        for agent_ip in agents:
            agent_removed_jobs = maand.get_agent_removed_jobs(cursor, agent_ip)
            for job in agent_removed_jobs:
                for namespace in [f"job/{job}", f"vars/job/{job}"]:
                    deleted_keys = kv_manager.get_keys(namespace)
                    for key in deleted_keys:
                        kv_manager.delete_key(namespace, key)


def build():
    jobs = workspace.get_jobs()
    if jobs:
        command_helper.command_local(f"rm -rf {const.JOBS_DB_PATH}")

    with maand.get_db() as db:
        cursor = db.cursor()
        job_data.setup_job_database(cursor)
        build_jobs(cursor)
        db.commit()
    db.execute("vacuum")


if __name__ == '__main__':
    build()
