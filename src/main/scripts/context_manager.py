import subprocess
import sys
import uuid

import kv_manager

from dotenv import dotenv_values

import command_helper
import utils

logger = utils.get_logger()


def get_agent_id(agent_ip):
    return kv_manager.get_value("maand", agent_ip)


def get_cluster_id():
    return kv_manager.get_value("maand", "cluster_id")


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


def get_values(agent_ip):
    values = dotenv_values("/workspace/variables.env")

    values["CLUSTER_ID"] = get_cluster_id()
    values["AGENT_ID"] = get_agent_id(agent_ip)
    values["AGENT_IP"] = agent_ip

    values = _add_roles_to_values(values, agent_ip)
    values = _add_tags_to_values(values, agent_ip)

    return values


def get_agent_dir(agent_ip):
    return f"/opt/agents/{agent_ip}"


def get_agent_env(agent_ip):
    agent_dir = get_agent_dir(agent_ip)
    values = get_values(agent_ip)
    load_secrets(values)
    values["AGENT_DIR"] = agent_dir
    return values


def get_agent_minimal_env(agent_ip):
    secrets = dotenv_values("/workspace/secrets.env")
    return {
        "AGENT_IP": agent_ip,
        "AGENT_DIR": get_agent_dir(agent_ip),
        "SSH_USER": secrets.get("SSH_USER"),
        "SSH_KEY": secrets.get("SSH_KEY"),
        "USE_SUDO": secrets.get("USE_SUDO")
    }


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


def validate_cluster_id(agent_ip, fail_if_no_cluster_id=True):
    try:
        cluster_id = kv_manager.get_value("maand", "cluster_id")
        agent_env = get_agent_minimal_env(agent_ip)

        if not cluster_id:
            logger.error("Required environment variable: CLUSTER_ID is not set.")
            sys.exit(1)

        res = command_helper.command_remote("cat /opt/agent/cluster_id.txt", agent_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if fail_if_no_cluster_id and res.returncode == 1:
            raise Exception(f"{agent_ip} : {res.stderr}")
        agent_cluster_id = res.stdout.decode("utf-8")
        if res.returncode == 0 and agent_cluster_id != cluster_id:
            raise Exception(f"Failed on cluster id validation: mismatch, agent {agent_ip}.")
    except Exception as e:
        logger.error(e)
        stop_the_world()


def validate_update_seq(agent_ip):
    try:
        update_seq = kv_manager.get_value("maand", "update_seq")
        agent_env = get_agent_minimal_env(agent_ip)

        res = command_helper.command_remote("cat /opt/agent/update_seq.txt", agent_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 1:
            raise Exception(f"{agent_ip} : {res.stderr}")
        agent_update_seq = res.stdout.decode("utf-8")
        if res.returncode == 0 and agent_update_seq != update_seq:
            raise AssertionError(f"Failed on update_seq validation: mismatch, agent {agent_ip}.")
    except Exception as e:
        logger.error(e)
        stop_the_world()


def validate_cluster_update_seq(agent_ip):
    command_helper.scan_agent(agent_ip)
    validate_cluster_id(agent_ip)
    validate_update_seq(agent_ip)


def stop_the_world():
    command_helper.command_local("kill -TERM 1")