import os
import sys
import uuid
from pathlib import Path
from string import Template

from dotenv import dotenv_values

import certs
import command_helper
import utils
import variables

logger = utils.get_logger()


def get_agent_id():
    try:
        with open("/opt/agent/agent_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error("agent_id.txt not found.")
        sys.exit(1)


def get_cluster_id():
    try:
        with open("/opt/agent/cluster_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error("agent_id.txt not found.")
        sys.exit(1)


def load_values():
    values = dotenv_values("/workspace/variables.env")

    agent_id = get_agent_id()
    agent_ip = os.getenv("AGENT_IP")

    values["AGENT_ID"] = agent_id
    values["AGENT_IP"] = agent_ip

    return values, agent_ip


def add_roles_to_values(values):
    node_ip = values["AGENT_IP"]
    available_roles = set()
    nodes = utils.get_agent_roles()

    for ip, roles in nodes.items():
        available_roles.update(roles)

    for role in available_roles:
        key_nodes = f"{role}_NODES".upper()
        role_hosts = utils.get_agents_by_role(role)
        values[key_nodes] = ",".join(role_hosts)

        if node_ip in role_hosts:
            role_hosts.remove(node_ip)
        key_others = f"{role}_OTHERS".upper()
        values[key_others] = ",".join(role_hosts)

        for idx, host in enumerate(utils.get_agents_by_role(role)):
            key = f"{role}_{idx}".upper()
            values[key] = host

            if host == node_ip:
                key = f"{role}_ALLOCATION_INDEX".upper()
                values[key] = idx

    host_roles = utils.get_agent_roles()
    values["ROLES"] = ",".join(host_roles.get(node_ip))

    return values


def add_tags_to_values(values, node_ip):
    nodes = utils.get_agent_tags()
    tags = nodes.get(node_ip, {})
    for k, v in tags.items():
        key = f"{k}".upper()
        values[key] = v
    return values


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
    values, agent_ip = load_values()
    values = add_roles_to_values(values)
    values = add_tags_to_values(values, agent_ip)
    process_templates(values)


def sync():
    cluster_id = os.getenv("CLUSTER_ID")
    agent_ip = os.getenv("AGENT_IP")

    if not cluster_id:
        logger.error("Required environment variable: CLUSTER_ID is not set.")
        sys.exit(1)

    if not os.path.isfile("/workspace/ca.key"):
        certs.generate_ca_private()
        certs.generate_ca_public(cluster_id, 365)

    command_helper.command_remote("mkdir -p /opt/agent")

    command_helper.command_local("""
        mkdir -p /opt/agent/certs
        rsync /workspace/ca.crt /opt/agent/certs/
        bash /scripts/rsync_remote_local.sh
    """)

    if not os.path.isfile("/opt/agent/agent_id.txt"):
        with open("/opt/agent/agent_id.txt", "w") as f:
            f.write(uuid.uuid4().__str__())

    if not os.path.isfile("/opt/agent/cluster_id.txt"):
        with open("/opt/agent/cluster_id.txt", "w") as f:
            f.write(cluster_id)

    if get_cluster_id() != cluster_id:
        raise Exception("Failed on cluster id validation: mismatch")

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
