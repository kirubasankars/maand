import configparser
import hashlib
import json
import os
import uuid

import const
import job_data
import kv_manager
import maand
import utils
import workspace
import jsonschema
from jsonschema import Draft202012Validator

logger = utils.get_logger()


def delete_job(cursor, job):
    cursor.execute("DELETE FROM job_db.job_ports WHERE job_id = (SELECT job_id FROM job_db.job WHERE name = ?)", (job,))
    cursor.execute("DELETE FROM job_db.job_labels WHERE job_id = (SELECT job_id FROM job_db.job WHERE name = ?)", (job,))
    cursor.execute("DELETE FROM job_db.job_certs WHERE job_id = (SELECT job_id FROM job_db.job WHERE name = ?)", (job,))
    cursor.execute("DELETE FROM job_db.job_commands WHERE job_id = (SELECT job_id FROM job_db.job WHERE name = ?)", (job,))
    cursor.execute("DELETE FROM job_db.job_files WHERE job_id = (SELECT job_id FROM job_db.job WHERE name = ?)", (job,))
    cursor.execute("DELETE FROM job_db.job WHERE name = ?", (job,))


def build_jobs(cursor):
    jobs = workspace.get_jobs()

    for job in jobs:
        delete_job(cursor, job)

        schema = {
            "type": "object",
            "properties": {
                "version": {"type": "string"},
                "labels": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "resources": {
                    "type": "object",
                    "properties": {
                        "memory": {
                            "type": "object",
                            "properties": {
                                "min": {"type": "string"},
                                "max": {"type": "string"}
                            },
                            "additionalProperties": False
                        },
                        "cpu": {
                            "type": "object",
                            "properties": {
                                "min": {"type": "string"},
                                "max": {"type": "string"}
                            },
                            "additionalProperties": False
                        },
                        "ports": {
                            "type": "object",
                            "patternProperties": {
                                "^port_": {"type": ["string", "object"]}
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
                },
                "certs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "patternProperties": {
                            ".*": {"type": ["string", "object"]}
                        },
                        "additionalProperties": False
                    }
                },
                "commands": {
                    "type": "object",
                    "patternProperties": {
                        "^command_": {
                            "type": "object",
                            "properties": {
                                "config": {"type": "object"},
                                "executed_on": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "allOf": [
                                            {"pattern": "^(direct|job_control|pre_build|post_build|pre_[a-zA-Z0-9_]+|post_[a-zA-Z0-9_]+)$"}
                                        ]
                                    }
                                },
                                "depend_on": {
                                    "type": "object",
                                    "properties": {
                                        "job": {"type": "string"},
                                        "command": {"type": "string"}
                                    },
                                    "additionalProperties": False
                                }
                            },
                            "additionalProperties": False
                        }
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        }

        manifest = workspace.get_job_manifest(job)
        jsonschema.validate(instance=manifest, schema=schema, format_checker=Draft202012Validator.FORMAT_CHECKER,)

        files = workspace.get_job_files(job)

        labels = manifest.get("labels")
        certs = manifest.get("certs")
        version = manifest.get("version", "unknown")
        commands = manifest.get("commands")

        job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(job)))
        min_memory_limit = float(utils.extract_size_in_mb(manifest.get("resources", {}).get("memory", {}).get("min", "0 MB")))
        max_memory_limit = float(utils.extract_size_in_mb(manifest.get("resources", {}).get("memory", {}).get("max", "0 MB")))
        min_cpu_limit = float(utils.extract_cpu_frequency_in_mhz(manifest.get("resources", {}).get("cpu", {}).get("min", "0 MHZ")))
        max_cpu_limit = float(utils.extract_cpu_frequency_in_mhz(manifest.get("resources", {}).get("cpu", {}).get("max", "0 MHZ")))
        ports = manifest.get("resources", {}).get("ports", {})
        certs_hash = hashlib.md5(json.dumps(certs).encode()).hexdigest()

        cursor.execute("INSERT INTO job_db.job (job_id, name, version, min_memory_mb, max_memory_mb, min_cpu, max_cpu, certs_md5_hash, deployment_seq) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)",
                        (job_id, job, version, min_memory_limit, max_memory_limit, min_cpu_limit, max_cpu_limit, certs_hash))

        for label in labels:
            cursor.execute("INSERT INTO job_db.job_labels (job_id, label) VALUES (?, ?)", (job_id, label,))

        for cert in certs:
            for name, config in cert.items():
                pkcs8 = config.get("pkcs8", 0)
                subject = config.get("subject", "")
                cursor.execute("INSERT INTO job_db.job_certs (job_id, name, pkcs8, subject) VALUES (?, ?, ?, ?)",
                               (job_id, name, pkcs8, subject,))

        for command, command_obj in commands.items():
            executed_on = command_obj.get("executed_on", ["direct"])
            depend_on = command_obj.get("depend_on", {})
            if executed_on:
                depend_on_job = depend_on.get("job")
                if depend_on_job and depend_on_job not in jobs:
                    logger.error(f"{depend_on_job} job not found: command: {command}, depend on job: {depend_on_job}")
                depend_on_command = depend_on.get("command")
                depend_on_config = json.dumps(depend_on.get("config", {}))
                for on in executed_on:
                    cursor.execute("INSERT INTO job_db.job_commands (job_id, job_name, name, executed_on, depend_on_job, depend_on_command, depend_on_config) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (job_id, job, command, on, depend_on_job, depend_on_command, depend_on_config))
            else:
                logger.error(f"The commands must include an 'executed_on'. job: {job}, command: {command}")

        for file in files:
            isdir = os.path.isdir(f"{const.WORKSPACE_PATH}/jobs/{file}")
            content = ""
            if not isdir:
                with open(f"{const.WORKSPACE_PATH}/jobs/{file}", 'rb') as f:
                    content = f.read()
            cursor.execute("INSERT INTO job_db.job_files (job_id, path, content, isdir) VALUES (?, ?, ?, ?)",
                           (job_id, file, content, isdir))

        for name, port in ports.items():
            name = name.upper()
            cursor.execute("INSERT INTO job_db.job_ports (job_id, name, port) VALUES (?, ?, ?)", (job_id, name, port,))

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

    cursor.execute(sql)

    cursor.execute("SELECT name FROM job_db.job")
    all_jobs = [row[0] for row in cursor.fetchall()]
    missing_jobs = list(set(jobs) ^ set(all_jobs))
    for job in missing_jobs:
        delete_job(cursor, job)


def get_job_variables(job):
    path = "/bucket/workspace/maand.jobs.conf"
    if not os.path.exists(path):
        return {}

    config_parser = configparser.ConfigParser()
    config_parser.read(path)

    name = f"{job}.variables"
    job_kv = {}
    if config_parser.has_section(name):
        keys = config_parser.options(name)
        for key in keys:
            key = key.upper()
            value =  config_parser.get(name, key)
            job_kv[key] = value

    job_kv["MEMORY"] = float(utils.extract_size_in_mb(job_kv.get("MEMORY", "0 MB")))
    job_kv["CPU"] = float(utils.extract_cpu_frequency_in_mhz(job_kv.get("CPU", "0 MHZ")))

    return job_kv


def build_maand_jobs_conf(cursor):
    # TODO: reversed key check
    path = "/bucket/workspace/maand.jobs.conf"
    if not os.path.exists(path):
        return

    config_parser = configparser.ConfigParser()
    config_parser.read(path)

    jobs = maand.get_jobs(cursor)
    for job in jobs:
        kv_namespace = f"vars/job/{job}"

        job_kv = get_job_variables(job)
        for key, value in job_kv.items():
            kv_manager.put(cursor, kv_namespace, key, str(value))

        keys = job_kv.keys()
        keys = [key.upper() for key in keys]
        all_keys = kv_manager.get_keys(cursor, kv_namespace)
        missing_keys = list(set(all_keys) ^ set(keys))
        for key in missing_keys:
            kv_manager.delete(cursor, kv_namespace, key)

    agents = maand.get_agents(cursor, labels_filter=None)
    for agent_ip in agents:
        agent_removed_jobs = maand.get_agent_removed_jobs(cursor, agent_ip)
        for job in agent_removed_jobs:
            for namespace in [f"job/{job}", f"vars/job/{job}"]:
                deleted_keys = kv_manager.get_keys(cursor, namespace)
                for key in deleted_keys:
                    kv_manager.delete(cursor, namespace, key)


def build_ports(cursor):
    cursor.execute("SELECT (SELECT name FROM job_db.job WHERE job_id = jp.job_id) AS job, name, port FROM job_db.job_ports jp")
    rows = cursor.fetchall()
    for job, name, port in rows:
        kv_namespace = f"vars/job/{job}"
        kv_manager.put(cursor, kv_namespace, f"{name}", str(port))


def build(cursor):
    job_data.setup_job_database(cursor)
    build_jobs(cursor)
    build_maand_jobs_conf(cursor)
    build_ports(cursor)
