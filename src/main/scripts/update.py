import base64
import glob
import hashlib
import json
import os
import shutil
import uuid
from copy import deepcopy
from pathlib import Path
from string import Template

import cert_provider
import command_helper
import context_manager
import system_manager
import utils
import kv_manager

logger = utils.get_logger()

namespace = "maand"

def get_cert_if_available(location, kv_path):
    content = kv_manager.get_value(namespace, kv_path)
    if content:
        content = base64.b64decode(content)
        with open(location, "wb") as f:
             f.write(content)


def put_cert(location, kv_path):
    with open(location, "rb") as f:
        content = base64.b64encode(f.read()).decode('utf-8')
        kv_manager.put_key_value(namespace, kv_path, content)


def update_certificates(jobs, agent_ip):
    cluster_id = os.getenv("CLUSTER_ID")
    agent_dir = context_manager.get_agent_dir(agent_ip)

    name = "agent"
    agent_cert_location = f"{agent_dir}/certs"
    agent_cert_path = f"{agent_cert_location}/agent"
    agent_cert_kv_path = f"certs/{agent_ip}/agent"

    get_cert_if_available(f"{agent_cert_path}.key", f"{agent_cert_kv_path}.key")
    get_cert_if_available(f"{agent_cert_path}.crt", f"{agent_cert_kv_path}.crt")
    get_cert_if_available(f"{agent_cert_path}.pem", f"{agent_cert_kv_path}.pem")

    if (not os.path.isfile(f"{agent_cert_path}.key") or (os.path.isfile(f"{agent_cert_path}.crt") and cert_provider.is_certificate_expiring_soon(f"{agent_cert_path}.crt"))):
        logger.debug(f"Updating certificates {name}.key and {name}.crt")

        cert_provider.generate_site_private(name, agent_cert_location)
        cert_provider.generate_private_pem_pkcs_8(name, agent_cert_location)
        cert_provider.generate_site_csr(name, f"/CN={cluster_id}", agent_cert_location)
        subject_alt_name = f"DNS.1:localhost,IP.1:127.0.0.1,IP.2:{agent_ip}"
        cert_provider.generate_site_public(name, subject_alt_name, 60, agent_cert_location)
        command_helper.command_local(f"rm -f {agent_cert_path}.csr")

        put_cert(f"{agent_cert_path}.key", f"{agent_cert_kv_path}.key")
        put_cert(f"{agent_cert_path}.crt", f"{agent_cert_kv_path}.crt")
        put_cert(f"{agent_cert_path}.pem", f"{agent_cert_kv_path}.pem")

        with open(f"{agent_cert_location}/reload.txt", "w") as f:
            f.write("")

    for job in jobs:
        metadata = utils.get_job_metadata(job, base_path=f"{agent_dir}/jobs")
        certificates = metadata.get("certs", [])

        if not certificates:
            continue

        job_cert_location = f"{agent_dir}/jobs/{job}/certs"
        job_cert_kv_location = f"certs/{agent_ip}/{job}"
        command_helper.command_local(f"mkdir -p {job_cert_location}")
        command_helper.command_local(f"cp -f /workspace/ca.crt {job_cert_location}/")

        update_certs = False

        current_hash = kv_manager.get_value(namespace, f"{job_cert_kv_location}/md5.hash")
        new_hash = hashlib.md5(json.dumps(certificates).encode()).hexdigest()
        if current_hash != new_hash:
            kv_manager.put_key_value(namespace, f"{job_cert_kv_location}/md5.hash", new_hash)
            update_certs = True

        for cert in certificates:
            for name, cert_config in cert.items():
                job_cert_path = f"{job_cert_location}/{name}"
                job_cert_kv_path = f"{job_cert_kv_location}/{name}"

                get_cert_if_available(f"{job_cert_path}.key", f"{job_cert_kv_path}.key")
                get_cert_if_available(f"{job_cert_path}.crt", f"{job_cert_kv_path}.crt")
                get_cert_if_available(f"{job_cert_path}.pem", f"{job_cert_kv_path}.pem")

                if update_certs or (not os.path.isfile(f"{job_cert_path}.key") or (os.path.isfile(f"{job_cert_path}.key") and cert_provider.is_certificate_expiring_soon(f"{job_cert_path}.crt"))):

                    logger.debug(f"Updating certificates {name}.key and {name}.crt")
                    ttl = cert_config.get("ttl", 60)
                    cert_provider.generate_site_private(name, job_cert_location)
                    if cert_config.get("pkcs8", False):
                        cert_provider.generate_private_pem_pkcs_8(name, job_cert_location)

                    subj = cert_config.get("subject", f"/CN={cluster_id}")
                    cert_provider.generate_site_csr(name, subj, job_cert_location)
                    subject_alt_name = cert_config.get("subject_alt_name", f"DNS.1:localhost,IP.1:127.0.0.1,IP.2:{agent_ip}")
                    cert_provider.generate_site_public(name, subject_alt_name, ttl, job_cert_location)
                    command_helper.command_local(f"rm -f {job_cert_path}.csr")

                    put_cert(f"{job_cert_path}.key", f"{job_cert_kv_path}.key")
                    put_cert(f"{job_cert_path}.crt", f"{job_cert_kv_path}.crt")
                    if cert_config.get("pkcs8", False):
                        put_cert(f"{job_cert_path}.pem", f"{job_cert_kv_path}.pem")

                    with open(f"{job_cert_location}/reload.txt", "w") as f:
                        f.write("")


def process_templates(values):
    values = deepcopy(values)
    for k, v in values.items():
        values[k] = v.replace("$$", "$")
    agent_ip = values["AGENT_IP"]
    agent_dir = context_manager.get_agent_dir(agent_ip)
    logger.debug("Processing templates...")
    for ext in ["*.json", "*.service", "*.conf", "*.yml", "*.env", "*.token", "*.txt"]:
        for f in Path(f'{agent_dir}/').rglob(ext):
            try:
                with open(f, 'r') as file:
                    data = file.read()
                template = Template(data)
                content = template.substitute(values)
                if content != data:
                    with open(f, 'w') as file:
                        file.write(content)
                logger.debug(f"Processed template: {f}")
            except Exception as e:
                logger.error(f"Error processing file {f}: {e}")
                raise e


def transpile(agent_ip):
    logger.debug("Transpiling templates...")
    values = context_manager.get_values(agent_ip)
    context_manager.load_secrets(values)
    process_templates(values)


def sync(agent_ip):
    args = utils.get_args_jobs_concurrency()

    cluster_id = kv_manager.get_value(namespace, "cluster_id")
    agent_dir = context_manager.get_agent_dir(agent_ip)

    logger.debug("Starting sync process...")

    command_helper.command_local(f"mkdir -p {agent_dir}")
    with open(f"{agent_dir}/cluster_id.txt", "w") as f:
        f.write(cluster_id)

    agent_id = kv_manager.get_value(namespace, agent_ip)
    if not agent_id:
        kv_manager.put_key_value(namespace, agent_ip, uuid.uuid4().__str__())

    agent_id = kv_manager.get_value(namespace, agent_ip)
    with open(f"{agent_dir}/agent_id.txt", "w") as f:
        f.write(agent_id)

    update_seq = kv_manager.get_value(namespace, "update_seq")
    with open(f"{agent_dir}/update_seq.txt", "w") as f:
        f.write(update_seq)

    command_helper.command_local(f"""
        mkdir -p {agent_dir}/certs
        rsync /workspace/ca.crt {agent_dir}/certs/
    """)

    assigned_jobs = utils.get_assigned_jobs(agent_ip)
    assigned_roles = utils.get_assigned_roles(agent_ip)
    disabled_jobs = utils.get_disabled_jobs(agent_ip)

    with open(f"{agent_dir}/roles.txt", "w") as f:
        f.writelines("\n".join(assigned_roles))

    jobs = {}
    for job in assigned_jobs:
        metadata = utils.get_job_metadata(job)
        jobs[job] = {
            "order": metadata.get("order", 99),
        }
        if job in disabled_jobs:
            jobs[job]["disabled"] = True

    with open(f"{agent_dir}/jobs.json", "w") as f:
        f.writelines(json.dumps(jobs))

    command_helper.command_local(f"""
        rsync -r /agent/bin {agent_dir}/
        cp /agent/agent.gitignore {agent_dir}/.gitignore
        mkdir -p {agent_dir}/jobs/
    """)

    exists_jobs = []
    for x in glob.glob(f"{agent_dir}/jobs/*"):
        exists_jobs.append(os.path.basename(x))

    removables = set(exists_jobs) ^ set(assigned_jobs)
    for job in removables:
        shutil.rmtree(f"{agent_dir}/jobs/" + job, ignore_errors=True)

    for job in assigned_jobs:
        command_helper.command_local(f"rsync -r --exclude '_*' /workspace/jobs/{job} {agent_dir}/jobs/")

    transpile(agent_ip)

    values = context_manager.get_values(agent_ip)
    with open(f"{agent_dir}/context.env", "w") as f:
        keys = sorted(values.keys())
        for key in keys:
            value = values.get(key)
            f.write("{}={}\n".format(key, value))

    update_certificates(assigned_jobs, agent_ip)

    command_helper.command_local("rm -f /workspace/ca.srl")
    command_helper.command_local(f"chown -R 1050:1042 {agent_dir}")

    filtered_jobs, filtered = utils.get_filtered_jobs(agent_ip, jobs_filter=args.jobs, min_order=args.min_order,max_order=args.max_order)
    if not filtered:
        filtered_jobs = []

    context_manager.rsync_upload_agent_files(agent_ip, filtered_jobs)

    logger.debug("Sync process completed.")

    # TODO: update crontab if start on restart enabled


def validate_cluster_id(agent_ip):
    context_manager.validate_cluster_id(agent_ip, fail_if_no_cluster_id=False)


def update():
    args = utils.get_args_jobs_concurrency()

    update_seq = kv_manager.get_value(namespace, "update_seq")
    next_update_seq = int(update_seq) + 1
    kv_manager.put_key_value(namespace, "update_seq", str(next_update_seq))

    system_manager.run(command_helper.scan_agent)
    system_manager.run(validate_cluster_id)
    system_manager.run(sync, concurrency=args.concurrency)
    kv_manager.gc()


if __name__ == "__main__":
    update()
