import glob
import hashlib
import json
import os
import shutil
import uuid
from pathlib import Path
from string import Template

import cert_provider
import command_helper
import context_manager
import system_manager
import utils

logger = utils.get_logger()


def update_certificates(jobs, agent_ip):
    cluster_id = os.getenv("CLUSTER_ID")
    agent_dir = context_manager.get_agent_dir(agent_ip)

    if (not os.path.isfile(f"{agent_dir}/certs/agent.key") or
            (os.path.isfile(f"{agent_dir}/certs/agent.crt") and cert_provider.is_certificate_expiring_soon(
                f"{agent_dir}/certs/agent.crt"))):
        logger.debug(f"Updating certificates agent.key and agent.crt")
        name = "agent"
        cert_provider.generate_site_private(name, f"{agent_dir}/certs")
        cert_provider.generate_private_pem_pkcs_8(name, f"{agent_dir}/certs")
        cert_provider.generate_site_csr(name, f"/CN={cluster_id}", f"{agent_dir}/certs")
        subject_alt_name = f"DNS.1:localhost,IP.1:127.0.0.1,IP.2:{agent_ip}"
        cert_provider.generate_site_public(name, subject_alt_name, 60, f"{agent_dir}/certs")
        command_helper.command_local(f"rm -f {agent_dir}/certs/{name}.csr")

        with open(f"{agent_dir}/certs/reload.txt", "w") as f:
            f.write("")

    for job in jobs:
        metadata = utils.get_job_metadata(job, base_path=f"{agent_dir}/jobs")
        certificates = metadata.get("certs", [])

        if not certificates:
            continue

        path = f"{agent_dir}/jobs/{job}/certs"
        command_helper.command_local(f"mkdir -p {path}")
        command_helper.command_local(f"cp -f /workspace/ca.crt {agent_dir}/jobs/{job}/certs/")

        update_certs = False
        hash_file = f"{agent_dir}/jobs/{job}/certs/md5.hash"

        certs_str = json.dumps(certificates)
        new_hash = hashlib.md5(certs_str.encode()).hexdigest()

        if os.path.exists(hash_file):
            with open(hash_file, "r") as f:
                current_hash = f.read()

            if new_hash != current_hash:
                update_certs = True
        else:
            update_certs = True

        with open(hash_file, "w") as f:
            f.write(new_hash)

        for cert in certificates:
            for name, cert_config in cert.items():
                if update_certs or (not os.path.isfile(f"{path}/{name}.key") or
                                    (os.path.isfile(
                                        f"{path}/{name}.key") and cert_provider.is_certificate_expiring_soon(
                                        f"{path}/{name}.crt"))):
                    logger.debug(f"Updating certificates {name}.key and {name}.crt")
                    ttl = cert_config.get("ttl", 60)
                    cert_provider.generate_site_private(name, path)

                    if cert_config.get("pkcs8", False):
                        cert_provider.generate_private_pem_pkcs_8(name, path)

                    subj = cert_config.get("subject", f"/CN={cluster_id}")
                    cert_provider.generate_site_csr(name, subj, path)

                    subject_alt_name = cert_config.get("subject_alt_name",
                                                       f"DNS.1:localhost,IP.1:127.0.0.1,IP.2:{agent_ip}")
                    cert_provider.generate_site_public(name, subject_alt_name, ttl, path)
                    command_helper.command_local(f"rm -f {path}/{name}.csr")

                    with open(f"{path}/reload.txt", "w") as f:
                        f.write("")


def process_templates(values):
    agent_ip = values["AGENT_IP"]
    agent_dir = context_manager.get_agent_dir(agent_ip)
    logger.debug("Processing templates...")
    for ext in ["*.json", "*.service", "*.conf", "*.yml", "*.env", "*.token"]:
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


def validate_cluster_id(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_id(agent_ip)


def sync(agent_ip):
    args = utils.get_args_jobs()

    cluster_id = os.getenv("CLUSTER_ID")
    agent_dir = context_manager.get_agent_dir(agent_ip)

    logger.debug("Starting sync process...")
    context_manager.rsync_download_agent_files(agent_ip)

    if not os.path.isfile(f"{agent_dir}/cluster_id.txt"):
        with open(f"{agent_dir}/cluster_id.txt", "w") as f:
            f.write(cluster_id)

    if not os.path.isfile(f"{agent_dir}/agent_id.txt"):
        with open(f"{agent_dir}/agent_id.txt", "w") as f:
            f.write(uuid.uuid4().__str__())

    command_helper.command_local(f"""
        mkdir -p {agent_dir}/certs
        rsync /workspace/ca.crt {agent_dir}/certs/
    """)

    assigned_jobs = utils.get_assigned_jobs(agent_ip)
    assigned_roles = utils.get_assigned_roles(agent_ip)
    disabled_jobs = utils.get_disabled_jobs(agent_ip)

    with open(f"{agent_dir}/roles.txt", "w") as f:
        f.writelines("\n".join(assigned_roles))

    with open(f"{agent_dir}/jobs.txt", "w") as f:
        f.writelines("\n".join(assigned_jobs))

    with open(f"{agent_dir}/disabled_jobs.txt", "w") as f:
        f.writelines("\n".join(disabled_jobs))

    command_helper.command_local(f"""
        rsync -r /agent/bin {agent_dir}/
        mkdir -p {agent_dir}/jobs/
    """)

    exists_jobs = []
    for x in glob.glob(f"{agent_dir}/jobs/*"):
        exists_jobs.append(os.path.basename(x))

    removables = set(exists_jobs) ^ set(assigned_jobs)
    for job in removables:
        shutil.rmtree(f"{agent_dir}/jobs/" + job, ignore_errors=True)

    # TODO: replicas and placement
    for job in assigned_jobs:
        command_helper.command_local(f"rsync -r --exclude '_commands' /workspace/jobs/{job} {agent_dir}/jobs/")

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

    filtered_jobs = utils.get_filtered_jobs(agent_ip, jobs_filter=args.jobs, min_order=args.min_order, max_order=args.max_order)
    context_manager.rsync_upload_agent_files(agent_ip, filtered_jobs)
    command_helper.command_local(f"cp /workspace/update_seq.txt {agent_dir}/update_seq.txt")
    context_manager.rsync_upload_agent_files(agent_ip, filtered_jobs)

    logger.debug("Sync process completed.")

    # TODO: update crontab if start on restart enabled


def update():
    if os.path.isfile(f"/workspace/update_seq.txt"):
        with open(f"/workspace/update_seq.txt", "r+") as f:
            seq = int(f.read()) + 1
            f.seek(0)
            f.write(str(seq))

    system_manager.run(validate_cluster_id)
    system_manager.run(sync)


if __name__ == "__main__":
    update()
