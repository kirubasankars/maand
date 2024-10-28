import base64
import hashlib
import json
import os

from copy import deepcopy
from pathlib import Path
from string import Template

import maand_job
import cert_provider
import command_helper
import context_manager
import system_manager
import utils
import maand_agent
import workspace
import kv_manager

logger = utils.get_logger()

kv_namespace = "maand"

def get_cert_if_available(location, kv_path):
    content = kv_manager.get_value(kv_namespace, kv_path)
    if content:
        content = base64.b64decode(content)
        with open(location, "wb") as f:
             f.write(content)


def put_cert(location, kv_path):
    with open(location, "rb") as f:
        content = base64.b64encode(f.read()).decode('utf-8')
        kv_manager.put_key_value(kv_namespace, kv_path, content)


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

    if (not os.path.isfile(f"{agent_cert_path}.key") or
            (os.path.isfile(f"{agent_cert_path}.crt") and cert_provider.is_certificate_expiring_soon(f"{agent_cert_path}.crt"))):

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

        with open(f"{agent_dir}/jobs/{job}/manifest.json") as f:
            metadata = json.load(f)

        certificates = metadata.get("certs", [])

        if not certificates:
            continue

        job_cert_location = f"{agent_dir}/jobs/{job}/certs"
        job_cert_kv_location = f"certs/{agent_ip}/{job}"
        command_helper.command_local(f"mkdir -p {job_cert_location}")
        command_helper.command_local(f"cp -f /workspace/ca.crt {job_cert_location}/")

        update_certs = False

        current_hash = kv_manager.get_value(kv_namespace, f"{job_cert_kv_location}/md5.hash")
        new_hash = hashlib.md5(json.dumps(certificates).encode()).hexdigest()
        if current_hash != new_hash:
            kv_manager.put_key_value(kv_namespace, f"{job_cert_kv_location}/md5.hash", new_hash)
            update_certs = True

        for cert in certificates:
            for name, cert_config in cert.items():
                job_cert_path = f"{job_cert_location}/{name}"
                job_cert_kv_path = f"{job_cert_kv_location}/{name}"

                get_cert_if_available(f"{job_cert_path}.key", f"{job_cert_kv_path}.key")
                get_cert_if_available(f"{job_cert_path}.crt", f"{job_cert_kv_path}.crt")
                get_cert_if_available(f"{job_cert_path}.pem", f"{job_cert_kv_path}.pem")

                if (update_certs or not os.path.isfile(f"{job_cert_path}.key") or
                            (os.path.isfile(f"{job_cert_path}.key") and cert_provider.is_certificate_expiring_soon(f"{job_cert_path}.crt"))):

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
    cluster_id = maand_agent.get_namespace_id()
    agent_dir = context_manager.get_agent_dir(agent_ip)

    logger.debug("Starting sync process...")

    command_helper.command_local(f"mkdir -p {agent_dir}")
    with open(f"{agent_dir}/namespace.txt", "w") as f:
        f.write(cluster_id)

    agent_id = maand_agent.get_agent_id(agent_ip)
    with open(f"{agent_dir}/agent.txt", "w") as f:
        f.write(agent_id)

    update_seq = maand_agent.get_update_seq()
    with open(f"{agent_dir}/update_seq.txt", "w") as f:
        f.write(str(update_seq))

    command_helper.command_local(f"""
        mkdir -p {agent_dir}/certs
        rsync /workspace/secrets/ca.crt {agent_dir}/certs/
    """)

    agent_jobs = maand_agent.get_agent_jobs(agent_ip)
    with open(f"{agent_dir}/jobs.json", "w") as f:
        f.writelines(json.dumps(agent_jobs))

    agent_roles = maand_agent.get_agent_roles(agent_ip)
    with open(f"{agent_dir}/roles.txt", "w") as f:
        f.writelines("\n".join(agent_roles))

    values = context_manager.get_values(agent_ip)
    with open(f"{agent_dir}/context.env", "w") as f:
        keys = sorted(values.keys())
        for key in keys:
            value = values.get(key)
            f.write("{}={}\n".format(key, value))

    command_helper.command_local(f"""
        rsync -r /agent/bin {agent_dir}/    
    """)

    if len(agent_jobs) > 0:
        command_helper.command_local(f"mkdir -p {agent_dir}/jobs/")

    for job in agent_jobs:
        maand_job.copy_job(job, agent_dir)

    transpile(agent_ip)
    update_certificates(agent_jobs, agent_ip)

    command_helper.command_local("rm -f /workspace/secrets/ca.srl")
    command_helper.command_local(f"chown -R 1061:1062 {agent_dir}")

    jobs = list(agent_jobs.keys())
    if args.jobs:
        jobs = list(set(agent_jobs.keys()) & set(args.jobs))

    context_manager.rsync_upload_agent_files(agent_ip, jobs)
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.command_remote("sync", env=agent_env)
    logger.debug("Sync process completed.")


def validate_cluster_id(agent_ip):
    context_manager.validate_namespace_id(agent_ip, fail_if_no_namespace_id=False)


def apply():
    args = utils.get_args_jobs_concurrency()

    update_seq = maand_agent.get_update_seq()
    next_update_seq = int(update_seq) + 1
    maand_agent.update_seq(next_update_seq)

    system_manager.run(command_helper.scan_agent)
    system_manager.run(validate_cluster_id)
    system_manager.run(sync, concurrency=args.concurrency)
    kv_manager.gc()


if __name__ == "__main__":
    apply()
