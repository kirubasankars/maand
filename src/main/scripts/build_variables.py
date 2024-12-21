import copy
import os.path
import uuid

from dotenv import dotenv_values

import const
import kv_manager
import maand


def build_env(cursor, path):
    namespace = os.path.basename(path)
    key_values = dotenv_values(path)

    for key, value in key_values.items():
        key = key.upper()
        kv_manager.put(cursor, namespace, key, value)

    all_keys = kv_manager.get_keys(cursor, namespace)
    missing_keys = list(set(all_keys) ^ set(key_values.keys()))
    for key in missing_keys:
        kv_manager.delete(cursor, namespace, key)


def build_agent_variables(cursor):
    agents = maand.get_agents(cursor, roles_filter=None)

    for agent_ip in agents:
        roles = maand.get_agent_roles(cursor, agent_ip=None)
        agent_roles = maand.get_agent_roles(cursor, agent_ip=agent_ip)

        values = {}
        for role in roles:
            key_nodes = f"{role}_nodes".upper()

            agents = maand.get_agents(cursor, [role])
            values[key_nodes] = ",".join(agents)

            key = f"{role}_length".upper()
            values[key] = str(len(agents))

            for idx, host in enumerate(agents):
                key = f"{role}_{idx}".upper()
                values[key] = host

            if role not in agent_roles:
                continue

            other_agents = copy.deepcopy(agents)
            if agent_ip in other_agents:
                other_agents.remove(agent_ip)

            key_peers = f"{role}_peers".upper()
            if other_agents:
                values[key_peers] = ",".join(other_agents)

            for idx, host in enumerate(agents):
                if host == agent_ip:
                    key = f"{role}_allocation_index".upper()
                    values[key] = str(idx)

            key = f"{role}_role_id".upper()
            values[key] = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(role)))

        values["ROLES"] = ",".join(sorted(agent_roles))

        agent_tags = maand.get_agent_tags(cursor, agent_ip)
        for key, value in agent_tags.items():
            values[key] = value

        available_memory, available_cpu = maand.get_agent_available_resources(cursor, agent_ip)
        if available_memory != "0.0":
            values["AGENT_MEMORY"] = available_memory
        if available_cpu != "0.0":
            values["AGENT_CPU"] = available_cpu

        namespace = f"vars/{agent_ip}"
        for key, value in values.items():
            kv_manager.put(cursor, namespace, key, value)

        all_keys = kv_manager.get_keys(cursor, namespace)
        missing_keys = list(set(all_keys) ^ set(values.keys()))
        for key in missing_keys:
            kv_manager.delete(cursor, namespace, key)


def build(cursor):
    build_env(cursor, f"{const.WORKSPACE_PATH}/variables.env")
    build_agent_variables(cursor)
