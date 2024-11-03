import copy
import os
import subprocess
import uuid

import maand_agent
import kv_manager
import command_helper
import utils

logger = utils.get_logger()


def load_secrets(values):
    keys = kv_manager.get_keys("secrets.env")
    for key in keys:
        values[key] = kv_manager.get_value("secrets.env", key)
    return values


def get_values(agent_ip):
    keys = kv_manager.get_keys("variables.env")
    values = {}
    for key in keys:
        values[key] = kv_manager.get_value("variables.env", key)

    values["NAMESPACE_ID"] = maand_agent.get_namespace_id()
    values["AGENT_ID"] = maand_agent.get_agent_id(agent_ip)
    values["AGENT_IP"] = agent_ip

    values = _add_roles_to_values(values, agent_ip)
    values = _add_tags_to_values(values, agent_ip)

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


def get_agent_dir(agent_ip):
    return f"/opt/agents/{agent_ip}"


def get_agent_minimal_env(agent_ip):
    config = utils.get_maand_conf()
    return {
        "AGENT_IP": agent_ip,
        "AGENT_DIR": get_agent_dir(agent_ip),
        "SSH_USER": config.get("default", "ssh_user"),
        "SSH_KEY": config.get("default", "ssh_key"),
        "USE_SUDO": config.get("default", "use_sudo"),
        "NAMESPACE": os.environ.get("NAMESPACE")
    }


def rsync_upload_agent_files(agent_ip, jobs):
    agent_env = get_agent_minimal_env(agent_ip)
    lines = []

    for job in jobs:
        lines.append(f"+ jobs/{job}\n")

    lines.append("- jobs/*\n")

    with open(f"/tmp/{agent_ip}_rsync_rules.txt", "w") as f:
        f.writelines(lines)

    namespace = agent_env.get("NAMESPACE", "")
    command_helper.command_remote(f"mkdir -p /opt/agent/{namespace}", env=agent_env)
    command_helper.command_local(f"bash /scripts/rsync_upload.sh", env=agent_env)


def validate_agent_namespace(agent_ip, fail_if_no_namespace_id=True):
    try:
        agent_env = get_agent_minimal_env(agent_ip)
        namespace = os.environ.get("NAMESPACE")
        res = command_helper.command_remote(f"ls /opt/agent/{namespace}", agent_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if fail_if_no_namespace_id and res.returncode != 0:
            raise Exception(f"agent {agent_ip} : namespace not found.")
    except Exception as e:
        logger.error(e)
        stop_the_world()


def validate_update_seq(agent_ip):
    try:
        agent_env = get_agent_minimal_env(agent_ip)
        update_seq = os.environ.get("UPDATE_SEQ")
        namespace_id = os.environ.get("NAMESPACE")
        res = command_helper.command_remote(f"cat /opt/agent/{namespace_id}/update_seq.txt", agent_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 1:
            raise Exception(f"{agent_ip} : {res.stderr}")
        agent_update_seq = res.stdout.decode("utf-8")
        if res.returncode == 0 and agent_update_seq != update_seq:
            raise AssertionError(f"Failed on update_seq validation: mismatch, agent {agent_ip}.")
    except Exception as e:
        logger.error(e)
        stop_the_world()


def validate_cluster_update_seq(agent_ip):
    validate_agent_namespace(agent_ip)
    validate_update_seq(agent_ip)


def stop_the_world():
    command_helper.command_local("kill -TERM 1")