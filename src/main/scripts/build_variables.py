import copy
import os.path
import uuid

import kv_manager
from dotenv import dotenv_values

import maand_agent
import const


def manage_kv(path):
    namespace = os.path.basename(path)
    key_values = dotenv_values(path)

    for key, value in key_values.items():
        kv_manager.put_key_value(namespace, key, value)

    all_keys = kv_manager.get_keys(namespace)
    missing_keys = list(set(all_keys) ^ set(key_values.keys()))
    for key in missing_keys:
        kv_manager.delete_key(namespace, key)


def build_variables():
    agents = maand_agent.get_agents()

    for agent_ip in agents:
        roles = maand_agent.get_agent_roles(agent_ip=None)
        agent_roles = maand_agent.get_agent_roles(agent_ip=agent_ip)

        values = {}
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
            values[key] = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(role)))

        values["ROLES"] = ",".join(sorted(agent_roles))

        for key, value in values.items():
            kv_manager.put_key_value(f"vars/{agent_ip}", key, value)


if __name__ == "__main__":
    manage_kv(f"{const.WORKSPACE_PATH}/secrets.env")
    manage_kv(f"{const.WORKSPACE_PATH}/variables.env")
    manage_kv(f"{const.WORKSPACE_PATH}/ports.env")
    build_variables()
