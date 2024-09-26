import glob
import json
import os.path
import subprocess
import sys


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
    jobs = []
    for job in glob.glob("/opt/agent/jobs/*/manifest.json"):
        job = os.path.basename(os.path.dirname(job))
        jobs.append(job)
    return jobs


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
    return jobs


def main():
    jobs = get_available_jobs()
    cmd = sys.argv[1]
    if len(sys.argv) > 2:
        jobs_filter = sys.argv[2]
        jobs_filter = jobs_filter.split(",")
        jobs = set(jobs) & set(jobs_filter)
    else:
        disabled_jobs = get_disabled_jobs()
        jobs = list(set(jobs) - set(disabled_jobs))
        print(jobs)
    run_jobs(cmd, jobs)


if __name__ == "__main__":
    main()
