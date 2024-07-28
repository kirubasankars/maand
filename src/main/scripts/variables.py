import os
import sys

from dotenv import dotenv_values

import utils

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


def get_variables():
    values, agent_ip = load_values()
    values = add_roles_to_values(values)
    values = add_tags_to_values(values, agent_ip)
    return values
