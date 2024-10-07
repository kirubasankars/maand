import os
import sys
import uuid

from dotenv import dotenv_values

import command_helper
import utils

logger = utils.get_logger()


def get_agent_id(agent_ip):
    agent_dir = get_agent_dir(agent_ip)
    try:
        with open(f"{agent_dir}/agent_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error("agent_id.txt not found.")
        sys.exit(1)


def get_agent_cluster_id(agent_id):
    agent_dir = get_agent_dir(agent_id)
    with open(f"{agent_dir}/cluster_id.txt", "r") as f:
        return f.read().strip()


def load_secrets(values):
    secrets = dotenv_values("/workspace/secrets.env")
    for key, value in secrets.items():
        values[key] = value
    return values


def _add_roles_to_values(values, agent_ip):
    available_roles = set()
    agent_roles = utils.get_agent_and_roles()

    for ip, roles in agent_roles.items():
        available_roles.update(roles)

    available_roles = set(available_roles)

    for role in available_roles:
        key_nodes = f"{role}_NODES".upper()
        agent_roles = utils.get_agents([role])
        hosts_ip = list(agent_roles.keys())
        values[key_nodes] = ",".join(hosts_ip)

        other_agents = list(agent_roles.keys())
        if agent_ip in other_agents:
            other_agents.remove(agent_ip)
        key_others = f"{role}_OTHERS".upper()
        if other_agents:
            values[key_others] = ",".join(other_agents)

        for idx, host in enumerate(list(agent_roles.keys())):
            key = f"{role}_{idx}".upper()
            values[key] = host

            if host == agent_ip:
                key = f"{role}_ALLOCATION_INDEX".upper()
                values[key] = str(idx)

        key = f"{role}_LENGTH".upper()
        values[key] = str(len(agent_roles.keys()))

        key = f"{role}_ID".upper()
        values[key] = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(role)))

    agent_roles = utils.get_agent_and_roles()
    values["ROLES"] = ",".join(sorted(agent_roles.get(agent_ip)))

    return values


def _add_tags_to_values(values, agent_ip):
    agents = utils.get_agent_and_tags()
    tags = agents.get(agent_ip, {})
    for k, v in tags.items():
        key = f"{k}".upper()
        values[key] = v
    return values


def get_agent_dir(agent_ip):
    return f"/opt/agents/{agent_ip}"


def get_values(agent_ip):
    values = dotenv_values("/workspace/variables.env")

    values["CLUSTER_ID"] = get_agent_cluster_id(agent_ip)
    values["AGENT_ID"] = get_agent_id(agent_ip)
    values["AGENT_IP"] = agent_ip

    values = _add_roles_to_values(values, agent_ip)
    values = _add_tags_to_values(values, agent_ip)

    return values


def get_agent_env(agent_ip):
    agent_dir = get_agent_dir(agent_ip)
    values = get_values(agent_ip)
    load_secrets(values)
    values["AGENT_DIR"] = agent_dir
    return values


def get_agent_minimal_env(agent_ip):
    secrets = dotenv_values("/workspace/secrets.env")
    return {"AGENT_IP": agent_ip, "AGENT_DIR": get_agent_dir(agent_ip), "SSH_USER": secrets.get("SSH_USER"),
            "SSH_KEY": secrets.get("SSH_KEY")}


def rsync_download_agent_files(agent_ip):
    command_helper.command_local(f"mkdir -p {get_agent_dir(agent_ip)}")
    command_helper.command_local("bash /scripts/rsync_download.sh", env=get_agent_minimal_env(agent_ip))


def rsync_upload_agent_files(agent_ip, jobs):
    agent_env = get_agent_minimal_env(agent_ip)
    lines = []
    if jobs:
        for job in jobs:
            lines.append(f"+ jobs/{job}\n")
        lines.append("- jobs/*\n")
    with open("/tmp/rsync_rules.txt", "w") as f:
        f.writelines(lines)
    command_helper.command_remote("mkdir -p /opt/agent", env=agent_env)
    command_helper.command_local("bash /scripts/rsync_upload.sh", env=agent_env)


def validate_cluster_id(agent_ip, failed_if_cluster_id_not_found=False):
    cluster_id = os.getenv("CLUSTER_ID")
    agent_dir = get_agent_dir(agent_ip)

    if not cluster_id:
        logger.error("Required environment variable: CLUSTER_ID is not set.")
        sys.exit(1)

    if os.path.exists(f"{agent_dir}/cluster_id.txt"):
        with open(f"{agent_dir}/cluster_id.txt", "r", encoding='utf-8') as f:
            data = f.read().strip().casefold()
            if data != cluster_id.strip():
                raise Exception(f"Failed on cluster id validation: mismatch, agent {agent_ip}.")
    else:
        if failed_if_cluster_id_not_found:
            raise Exception(f"Failed on cluster id validation: cluster_id.txt not found, agent {agent_ip}.")


def validate_update_seq(agent_ip):
    agent_dir = get_agent_dir(agent_ip)

    update_seq = 0
    with open(f"/workspace/update_seq.txt", "r", encoding='utf-8') as f:
        update_seq = f.read().strip().casefold()

    if os.path.isfile(f"{agent_dir}/update_seq.txt"):
        with open(f"{agent_dir}/update_seq.txt", "r", encoding='utf-8') as f:
            data = f.read().strip().casefold()
            if update_seq != data:
                raise Exception(f"Failed on update_seq validation: mismatch, agent {agent_ip}.")
    else:
        raise Exception(f"Failed on update_seq validation: update_seq.txt not found, agent {agent_ip}.")


def validate_cluster_update_seq(agent_ip):
    rsync_download_agent_files(agent_ip)
    validate_cluster_id(agent_ip)
    validate_update_seq(agent_ip)
