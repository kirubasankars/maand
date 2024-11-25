import copy
import os.path
import uuid

import kv_manager
from dotenv import dotenv_values

import maand
import const


def build_env(path):
    namespace = os.path.basename(path)
    key_values = dotenv_values(path)

    for key, value in key_values.items():
        kv_manager.put_key_value(namespace, key, value)

    all_keys = kv_manager.get_keys(namespace)
    missing_keys = list(set(all_keys) ^ set(key_values.keys()))
    for key in missing_keys:
        kv_manager.delete_key(namespace, key)


def build_variables(cursor):
    agents = maand.get_agents(cursor, roles_filter=None)

    for agent_ip in agents:
        roles = maand.get_agent_roles(cursor, agent_ip=None)
        agent_roles = maand.get_agent_roles(cursor, agent_ip=agent_ip)

        values = {}
        for role in roles:
            key_nodes = f"{role}_NODES".upper()

            agents = maand.get_agents(cursor, [role])
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
            values[key] = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(role)))

        values["ROLES"] = ",".join(sorted(agent_roles))

        for key, value in values.items():
            kv_manager.put_key_value(f"vars/{agent_ip}", key, value)


def build():
    build_env(f"{const.WORKSPACE_PATH}/secrets.env")
    build_env(f"{const.WORKSPACE_PATH}/variables.env")
    build_env(f"{const.WORKSPACE_PATH}/ports.env")

    with maand.get_db() as db:
        cursor = db.cursor()
        build_variables(cursor)

        cursor.execute("SELECT agent_ip FROM agent_db.agent WHERE detained = 1")
        rows = cursor.fetchall()
        agents_ip = {row[0] for row in rows}

        for agent_ip in agents_ip:
            namespace = f"certs/{agent_ip}"
            keys = kv_manager.get_keys(namespace)
            for key in keys:
                kv_manager.delete_key(namespace, key)

            namespace = f"vars/{agent_ip}"
            keys = kv_manager.get_keys(namespace)
            for key in keys:
                kv_manager.delete_key(namespace, key)


if __name__ == "__main__":
    build()
