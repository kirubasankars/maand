import argparse
import json
import subprocess


def get_jobs(namespace):
    with open(f"/opt/agent/{namespace}/jobs.json", "r") as f:
        return json.loads(f.read())


def run_jobs(namespace, cmd, jobs):
    for job in jobs:
        subprocess.run(["make", "-C", f"/opt/agent/{namespace}/jobs/{job}", cmd])


def main(args):
    jobs = get_jobs(args.namespace)
    if args.cmd in ["start", "restart"] and not args.jobs:
        jobs_to_run = [job for job, obj in jobs.items() if obj.get("disabled", 0) == 0]
    else:
        available_jobs = [job for job, obj in jobs.items()]
        if args.jobs:
            jobs_to_run = set(available_jobs) & set(args.jobs)
        else:
            jobs_to_run = available_jobs

    run_jobs(args.namespace, args.cmd, jobs_to_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('namespace', default="")
    parser.add_argument('cmd', default="")
    parser.add_argument('--jobs', default=None, required=False)
    args = parser.parse_args()
    if args.jobs:
        args.jobs = args.jobs.split(",")
    main(args)
