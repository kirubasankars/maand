import functools
import glob
import json
import logging
import os


def custom_sort_order(element):
    custom_order_list = []
    if element in custom_order_list:
        return custom_order_list.index(element)
    else:
        return 99


def flatten(nested_list):
    flat_list = []
    stack = [nested_list]

    while stack:
        current_element = stack.pop()

        if isinstance(current_element, list):
            stack.extend(reversed(current_element))
        else:
            flat_list.append(current_element)

    return list(reversed(flat_list))


def get_agents(role_filter=None):
    with open("/workspace/agents.txt", "r") as f:
        filedata = f.read()

    lines = [x.strip() for x in filedata.split("\n") if x.strip()]

    agents = {}
    for line in lines:
        s = line.split(" ")
        if len(s) == 2:
            agents[s[0]] = s[1].split(",")
        if len(s) == 1:
            agents[s[0]] = []

    agents_ip = agents.keys()
    for agent_ip in agents_ip:
        roles = agents.get(agent_ip)
        roles = list(set(roles))
        agents[agent_ip] = sorted(roles, key=custom_sort_order)

    if role_filter:
        agents = {agent_ip: roles for agent_ip, roles in agents.items() if set(role_filter) & set(roles)}

    return agents


def get_agent_tag_value(agent, tag_key):
    agents = get_agents()
    for agent, roles in agents.items():
        agents[agent] = {r.split(":")[0].strip(): r.split(":")[1].strip() for r in roles if ":" in r}
    return agents.get(agent).get(tag_key)


def get_agent_roles(role_filter=None):
    nodes = get_agents(role_filter)
    for host, roles in nodes.items():
        nodes[host] = [r for r in roles if ":" not in r]
    return nodes


def get_agent_tags(role_filter=None):
    nodes = get_agents(role_filter)
    for host, roles in nodes.items():
        nodes[host] = {r.split(":")[0]: r.split(":")[1] for r in roles if ":" in r}
    return nodes


def get_agent_one(role):
    hosts = get_agent_roles()
    filtered_hosts = [ip for ip, roles in hosts.items() if role in roles]
    if len(filtered_hosts) > 0:
        return filtered_hosts[0]


def get_agents_by_role(role):
    hosts = get_agent_roles()
    role_hosts = set(ip for ip, roles in hosts.items() if role in roles)
    return sorted(role_hosts)


def get_job_metadata(name, base_path="/workspace/jobs/"):
    for job in glob.glob(f"{base_path}/*"):
        metadata_path = os.path.join(job, "metadata.json")
        if os.path.isdir(job) and os.path.isfile(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                if name == metadata.get("name", ""):
                    return metadata
    return {}


@functools.cache
def get_jobs():
    jobs = []
    for job in glob.glob("/workspace/jobs/*"):
        metadata_path = os.path.join(job, "metadata.json")
        if os.path.isdir(job) and os.path.isfile(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                jobs.append(metadata.get("name", ""))
    return jobs


@functools.cache
def get_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)
