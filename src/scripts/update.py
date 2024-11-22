import base64
import json
import os

from copy import deepcopy
from pathlib import Path
from string import Template

import maand
import command_helper
import context_manager
import system_manager
import utils
import const
import kv_manager


logger = utils.get_logger()


def write_cert(location, namespace, kv_path):
    content = kv_manager.get_value(namespace, kv_path)
    content = base64.b64decode(content)
    with open(location, "wb") as f:
        f.write(content)


def update_certificates(cursor, jobs, agent_ip):
    agent_dir = context_manager.get_agent_dir(agent_ip)

    name = "agent"
    agent_cert_location = f"{agent_dir}/certs"
    agent_cert_path = f"{agent_cert_location}/{name}"
    agent_cert_kv_path = f"certs/{name}"

    write_cert(
        f"{agent_cert_path}.key", f"certs/{agent_ip}", f"{agent_cert_kv_path}.key"
    )
    write_cert(
        f"{agent_cert_path}.crt", f"certs/{agent_ip}", f"{agent_cert_kv_path}.crt"
    )
    write_cert(
        f"{agent_cert_path}.pem", f"certs/{agent_ip}", f"{agent_cert_kv_path}.pem"
    )

    for job in jobs:
        job_cert_location = f"{agent_dir}/jobs/{job}/certs"
        job_cert_kv_location = f"{job}/certs"
        namespace = f"certs/job/{agent_ip}"

        job_certs = maand.get_job_certs_config(cursor, job)

        if job_certs:
            command_helper.command_local(f"mkdir -p {job_cert_location}")
            command_helper.command_local(
                f"cp -f {const.SECRETS_PATH}/ca.crt {job_cert_location}/"
            )

        for cert in job_certs:
            name = cert.get("name")
            job_cert_path = f"{job_cert_location}/{name}"
            job_cert_kv_path = f"{job_cert_kv_location}/{name}"

            write_cert(f"{job_cert_path}.key", namespace, f"{job_cert_kv_path}.key")
            write_cert(f"{job_cert_path}.crt", namespace, f"{job_cert_kv_path}.crt")
            if cert.get("pkcs8", False):
                write_cert(f"{job_cert_path}.pem", namespace, f"{job_cert_kv_path}.pem")


def process_templates(values):
    values = deepcopy(values)
    for k, v in values.items():
        values[k] = v.replace("$$", "$")
    agent_ip = values["AGENT_IP"]
    agent_dir = context_manager.get_agent_dir(agent_ip)
    logger.debug("Processing templates...")
    for ext in ["*.json", "*.service", "*.conf", "*.yml", "*.env", "*.token", "*.txt"]:
        for f in Path(f"{agent_dir}/").rglob(ext):
            try:
                with open(f, "r") as file:
                    data = file.read()
                template = Template(data)
                content = template.substitute(values)
                if content != data:
                    with open(f, "w") as file:
                        file.write(content)
                logger.debug(f"Processed template: {f}")
            except Exception as e:
                logger.error(f"Error processing file {f}: {e}")
                raise e


def transpile(agent_ip):
    logger.debug("Transpiling templates...")
    values = context_manager.get_agent_env(agent_ip)
    process_templates(values)


def sync(agent_ip):
    with maand.get_db() as db:
        cursor = db.cursor()

        args = utils.get_args_jobs_concurrency()

        logger.debug("Starting sync process...")
        agent_dir = context_manager.get_agent_dir(agent_ip)

        command_helper.command_local(
            f"""
            mkdir -p {agent_dir}/certs
            rsync {const.SECRETS_PATH}/ca.crt {agent_dir}/certs/
        """
        )

        agent_id = maand.get_agent_id(cursor, agent_ip)
        with open(f"{agent_dir}/agent.txt", "w") as f:
            f.write(agent_id)

        update_seq = maand.get_update_seq(cursor)
        with open(f"{agent_dir}/update_seq.txt", "w") as f:
            f.write(str(update_seq))

        agent_roles = maand.get_agent_roles(cursor, agent_ip)
        with open(f"{agent_dir}/roles.txt", "w") as f:
            f.writelines("\n".join(agent_roles))

        values = {}
        maand_vars = kv_manager.get_keys(f"vars/{agent_ip}")
        for key in maand_vars:
            values[key] = kv_manager.get_value(f"vars/{agent_ip}", key)
        values["AGENT_IP"] = agent_ip
        with open(f"{agent_dir}/context.env", "w") as f:
            keys = sorted(values.keys())
            for key in keys:
                value = values.get(key)
                f.write("{}={}\n".format(key, value))

        command_helper.command_local(
            f"""
            rsync -r /agent/bin {agent_dir}/    
        """
        )

        agent_jobs = maand.get_agent_jobs(cursor, agent_ip)
        with open(f"{agent_dir}/jobs.json", "w") as f:
            f.writelines(json.dumps(agent_jobs))

        if len(agent_jobs) > 0:
            command_helper.command_local(f"mkdir -p {agent_dir}/jobs/")

            for job in agent_jobs:
                maand.copy_job(cursor, job, agent_dir)

        transpile(agent_ip)
        update_certificates(cursor, agent_jobs, agent_ip)

        command_helper.command_local(f"chown -R 1061:1062 {agent_dir}")

        jobs = list(agent_jobs.keys())
        if args.jobs:
            jobs = list(set(agent_jobs.keys()) & set(args.jobs))

        context_manager.rsync_upload_agent_files(agent_ip, jobs)

        logger.debug("Sync process completed.")


def validate_agent_namespace(agent_ip):
    context_manager.validate_agent_namespace(agent_ip, fail_if_no_bucket_id=False)


def update():

    args = utils.get_args_jobs_concurrency()

    with maand.get_db() as db:
        cursor = db.cursor()

        maand.export_env_bucket_update_seq(cursor)

        system_manager.run(cursor, command_helper.scan_agent)
        system_manager.run(cursor, validate_agent_namespace)

        update_seq = maand.get_update_seq(cursor)
        next_update_seq = int(update_seq) + 1
        maand.update_seq(cursor, next_update_seq)

        db.commit()

        system_manager.run(cursor, sync, concurrency=args.concurrency)

    kv_manager.gc()


if __name__ == "__main__":
    update()
