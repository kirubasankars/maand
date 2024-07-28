import os
import uuid
from pathlib import Path
from string import Template

import certs
import command_helper
import context_manager
import utils

logger = utils.get_logger()


def process_templates(values):
    for ext in ["*.json", "*.service", "*.conf", "*.yml", "*.env", "*.token"]:
        for f in Path('/opt/agent/').rglob(ext):
            try:
                with open(f, 'r') as file:
                    data = file.read()
                template = Template(data)
                content = template.substitute(values)
                if content != data:
                    with open(f, 'w') as file:
                        file.write(content)
            except Exception as e:
                logger.error(f"Error processing file {f}: {e}")
                raise e


def transpile():
    values = context_manager.get_values()
    process_templates(values)


def sync():
    context_manager.validate_cluster_id()

    cluster_id = os.getenv("CLUSTER_ID")
    agent_ip = os.getenv("AGENT_IP")

    command_helper.command_remote("mkdir -p /opt/agent")
    command_helper.command_local("bash /scripts/rsync_remote_local.sh")

    if not os.path.isfile("/opt/agent/cluster_id.txt"):
        with open("/opt/agent/cluster_id.txt", "w") as f:
            f.write(cluster_id)

    if not os.path.isfile("/opt/agent/agent_id.txt"):
        with open("/opt/agent/agent_id.txt", "w") as f:
            f.write(uuid.uuid4().__str__())

    if not os.path.isfile("/workspace/ca.key"):
        certs.generate_ca_private()
        certs.generate_ca_public(cluster_id, 365)

    command_helper.command_local("""
        mkdir -p /opt/agent/certs
        rsync /workspace/ca.crt /opt/agent/certs/
    """)

    agents = utils.get_agent_roles()
    roles = agents.get(agent_ip, [])
    with open("/opt/agent/roles.txt", "w") as f:
        f.writelines("\n".join(roles))

    assigned_jobs = []
    jobs = utils.get_jobs()
    for job in jobs:
        metadata = utils.get_job_metadata(job)
        job_roles = metadata.get("roles", [])
        if set(roles) & set(job_roles):
            assigned_jobs.append(job)

    command_helper.command_local("""
        rsync -r /agent/bin /opt/agent/
        mkdir -p /opt/agent/jobs/
    """)

    if assigned_jobs:
        assigned_jobs_str = ",".join(assigned_jobs)
        command_helper.command_local(f"rsync -r /workspace/jobs/{assigned_jobs_str} /opt/agent/jobs/")

    transpile()

    values = context_manager.get_values()
    with open("/opt/agent/values.env", "w") as f:
        for key, value in values.items():
            f.write("export {}={}\n".format(key, value))

    update_certificates(jobs, cluster_id)

    command_helper.command_local("rm -f /workspace/ca.srl")
    command_helper.command_local("bash /scripts/rsync_local_remote.sh")


def update_certificates(jobs, cluster_id):
    node_ip = os.getenv("AGENT_IP")
    for job in jobs:
        metadata = utils.get_job_metadata(job, base_path="/opt/agent/jobs")
        if os.getenv("UPDATE_CERTS", "0") == "1":
            certificates = metadata.get("certificates", [])
            for cert in certificates:
                for name, cert_config in cert.items():
                    if not os.path.isfile(f"/opt/agent/certs/{name}.key"):
                        ttl = cert_config.get("ttl", 60)
                        certs.generate_site_private(name)
                        certs.generate_private_pem_pkcs_8(name)

                        common = cert_config.get("subject", cluster_id)
                        certs.generate_site_csr(name, common)

                        subject_alt_name = cert_config.get("subject_alt_name",
                                                           f"DNS.1:localhost,IP.1:127.0.0.1,IP.2:{node_ip}")
                        certs.generate_site_public(name, subject_alt_name, ttl)

                        command_helper.command_local(f"rm /opt/agent/certs/{name}.csr")


if __name__ == "__main__":
    sync()
