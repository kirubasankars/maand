import argparse
import functools
import glob
import json
import logging
import os


def get_agents(roles_filter=None):
    with open("/workspace/agents.json", "r") as f:
        data = json.loads(f.read())

    agents = {item.get("host"): item for item in data}

    for agent_ip in agents:
        agent = agents[agent_ip]
        if not agent.get("roles"):
            agent["roles"] = ["agent"]
        else:
            agent["roles"].append("agent")

        if not agent.get("tags"):
            agent["tags"] = {}

    if roles_filter:
        agents = {agent_ip: agent for agent_ip, agent in agents.items() if
                  set(roles_filter or []) & set(agent.get("roles", []))}

    return agents


def get_agent_and_roles(roles_filter=None):
    agents = get_agents(roles_filter)
    for agent_ip, agent in agents.items():
        agents[agent_ip] = agent.get("roles")
    return agents


def get_agent_and_tags(role_filter=None):
    agents = get_agents(role_filter)
    for host, agent in agents.items():
        agents[host] = agent.get("tags")
    return agents


def get_ssh_port(agent_ip):
    return get_agents(None).get(agent_ip).get("ssh_port", 22)


def get_job_metadata(job_folder_name, base_path="/workspace/jobs/"):
    metadata_path = os.path.join(base_path, job_folder_name, "manifest.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
            if "roles" not in metadata:
                metadata["roles"] = []
            return metadata
    return {"roles": []}


def get_role_and_jobs():
    roles = {}
    for metadata_path in glob.glob("/workspace/jobs/*/manifest.json"):

        job_folder_name = os.path.basename(os.path.dirname(metadata_path))
        metadata = get_job_metadata(job_folder_name)

        for role in metadata["roles"]:
            if role not in roles:
                roles[role] = []
            roles[role].append(job_folder_name)

    return roles


def get_assigned_jobs(agent_ip):
    agents = get_agents()
    roles = agents.get(agent_ip).get("roles")
    role_jobs = get_role_and_jobs()
    assigned_jobs = []
    for role in roles:
        assigned_jobs.extend(role_jobs.get(role, []))
    assigned_jobs = list(set(assigned_jobs))

    assigned_jobs_bucket = {}
    for job in assigned_jobs:
        job_metadata = get_job_metadata(job)
        order = int(job_metadata.get("order", 99))
        if order not in assigned_jobs_bucket:
            assigned_jobs_bucket[order] = []
        assigned_jobs_bucket[order].append(job)

    ordered_assigned_jobs = []
    nums = sorted(assigned_jobs_bucket.keys())
    for num in nums:
        ordered_assigned_jobs.extend(assigned_jobs_bucket[num])

    return ordered_assigned_jobs


def get_disabled_jobs(agent_ip):
    if not os.path.exists(f"/workspace/disabled.json"):
        return []

    jobs = []
    with open("/workspace/disabled.json", "r") as f:
        data = json.load(f)
        for job, value in data.get("jobs", {}).items():
            if "agents" in value:
                if agent_ip in value["agents"]:
                    jobs.append(job)
            else:
                jobs.append(job)

        agents = data.get("agents", [])
        if agent_ip in agents:
            jobs = get_assigned_jobs(agent_ip)

    return jobs


def get_filtered_jobs(agent_ip, jobs_filter, min_order, max_order):
    assigned_jobs = get_assigned_jobs(agent_ip)
    filtered_jobs = []
    for job in assigned_jobs:
        job_metadata = get_job_metadata(job)
        order = int(job_metadata.get("order", 99))
        if jobs_filter:
            if job in jobs_filter and min_order <= order < max_order:
                filtered_jobs.append(job)
        else:
            if min_order <= order < max_order:
                filtered_jobs.append(job)

    if (min_order != 0 or max_order != 100) and not filtered_jobs:
        raise Exception("No jobs found.")

    return filtered_jobs


def get_assigned_roles(agent_ip):
    agents = get_agents()
    roles = agents.get(agent_ip).get("roles")
    return list(set(roles))


@functools.cache
def get_logger():
    root_logger = logging.getLogger(os.getenv("AGENT_IP"))
    console_handler = logging.StreamHandler()
    root_logger.addHandler(console_handler)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger.setLevel(log_level)
    return root_logger


def is_sudo_enabled():
    return os.environ.get("USE_SUDO", "0") == "1"


def get_args_agents_jobs_concurrency():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--jobs', default="")
    parser.add_argument('--min-order', default="0", type=int)
    parser.add_argument('--max-order', default="100", type=int)
    parser.add_argument('--include-disabled', default=False, required=False, action='store_true')
    parser.add_argument('--concurrency', default="4", type=int)
    args = parser.parse_args()

    if args.agents:
        args.agents = args.agents.split(',')
    if args.jobs:
        args.jobs = args.jobs.split(',')

    return args


def get_args_agents_roles_concurrency():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--roles', default="")
    parser.add_argument('--concurrency', default="4", type=int)
    args = parser.parse_args()

    if args.agents:
        args.agents = args.agents.split(',')
    if args.roles:
        args.roles = args.roles.split(',')

    return args


def get_args_jobs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', default="", required=False)
    parser.add_argument('--min-order', default="0", required=False, type=int)
    parser.add_argument('--max-order', default="100", required=False, type=int)
    parser.add_argument('--include-disabled', default=False, required=False, action='store_true')
    args = parser.parse_args()

    if args.jobs:
        args.jobs = args.jobs.split(',')

    return args
