import argparse
import json
import subprocess


def get_context_env():
    agent_env = {}
    with open("/opt/agent/context.env") as f:
        for line in f.readlines():
            if line.index("=") > 0:
                key = (line.split("=")[0]).strip()
                value = (line.split("=")[1]).strip()
                agent_env[key] = value
    return agent_env


def get_available_jobs():
    with open("/opt/agent/jobs.txt", "r") as f:
        return [l.strip() for l in f.readlines()]


def run_jobs(cmd, jobs):
    for job in jobs:
        subprocess.run(["make", "-C", f"/opt/agent/jobs/{job}", "build", cmd])


def get_disabled_jobs():
    context_env = get_context_env()
    agent_ip = context_env["AGENT_IP"]

    jobs = []
    with open("/opt/agent/disabled.json", "r") as f:
        data = json.load(f)
        for job, value in data.get("jobs", {}).items():
            if "agents" in value:
                if agent_ip in value["agents"]:
                    jobs.append(job)
            else:
                jobs.append(job)

        agents = data.get("agents", [])
        if agent_ip in agents:
            jobs = get_available_jobs()

    return jobs


def main(args):
    available_jobs = get_available_jobs()
    if args.cmd in ["start", "restart"] and not args.jobs:
        disabled_jobs = get_disabled_jobs()
        jobs_to_run = list(set(available_jobs) - set(disabled_jobs))
    else:
        if args.jobs:
            jobs_to_run = set(available_jobs) & set(args.jobs)
        else:
            jobs_to_run = available_jobs

    run_jobs(args.cmd, jobs_to_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', default="")
    parser.add_argument('--jobs', default=None, required=False)
    args = parser.parse_args()
    if args.jobs:
        args.jobs = args.jobs.split(",")
    print(args)
    main(args)
