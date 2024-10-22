import copy
import subprocess
import uuid

import maand_agent

from dotenv import dotenv_values

import command_helper
import utils

logger = utils.get_logger()


def load_secrets(values):
    secrets = dotenv_values("/workspace/secrets.env")
    for key, value in secrets.items():
        values[key] = value
    return values


def _add_roles_to_values(values, agent_ip):
    agent_roles = maand_agent.get_agent_roles(agent_ip=agent_ip)

    roles = maand_agent.get_agent_roles(agent_ip=None)

    for role in roles:
        key_nodes = f"{role}_NODES".upper()

        agents = maand_agent.get_agents([role])
        values[key_nodes] = ",".join(agents)

        other_agents = copy.deepcopy(agents)
        if agent_ip in other_agents:
            other_agents.remove(agent_ip)

        key = f"{role}_LENGTH".upper()
        values[key] = str(len(agents))

        if role not in agent_roles:
            continue

        key_peers = f"{role}_PEERS".upper()
        if other_agents:
            values[key_peers] = ",".join(other_agents)

        for idx, host in enumerate(agents):
            key = f"{role}_{idx}".upper()
            values[key] = host

            if host == agent_ip:
                key = f"{role}_ALLOCATION_INDEX".upper()
                values[key] = str(idx)

        key = f"{role}_ROLE_ID".upper()
        values[key] = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(role)).hex)

    values["ROLES"] = ",".join(sorted(agent_roles))

    return values


def _add_tags_to_values(values, agent_ip):
    tags = maand_agent.get_agent_tags(agent_ip=agent_ip)
    for k, v in tags.items():
        key = f"{k}".upper()
        values[key] = str(v)
    return values


def get_values(agent_ip):
    values = dotenv_values("/workspace/variables.env")

    values["CLUSTER_ID"] = maand_agent.get_cluster_id()
    values["AGENT_ID"] = maand_agent.get_agent_id(agent_ip)
    values["AGENT_IP"] = agent_ip

    values = _add_roles_to_values(values, agent_ip)
    values = _add_tags_to_values(values, agent_ip)

    return values


def get_agent_dir(agent_ip):
    return f"/opt/agents/{agent_ip}"


def get_agent_minimal_env(agent_ip):
    config = dotenv_values("/workspace/maand.config.env")
    return {
        "AGENT_IP": agent_ip,
        "AGENT_DIR": get_agent_dir(agent_ip),
        "SSH_USER": config.get("SSH_USER"),
        "SSH_KEY": config.get("SSH_KEY"),
        "USE_SUDO": config.get("USE_SUDO")
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
        cluster_id = maand_agent.get_cluster_id()
        agent_env = get_agent_minimal_env(agent_ip)
        res = command_helper.command_remote("cat /opt/agent/cluster_id.txt", agent_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if fail_if_no_cluster_id and res.returncode != 0:
            raise Exception(f"{agent_ip} : {res.stderr}")
        agent_cluster_id = res.stdout.decode("utf-8")
        if res.returncode == 0 and agent_cluster_id != cluster_id:
            raise Exception(f"Failed on cluster id validation: mismatch, agent {agent_ip}.")
    except Exception as e:
        logger.error(e)
        stop_the_world()


def validate_update_seq(agent_ip):
    try:
        update_seq = str(maand_agent.get_update_seq())
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