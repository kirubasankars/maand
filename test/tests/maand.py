import os
import subprocess


def run(command):
    workspace = os.environ.get('WORKSPACE')
    r = subprocess.run(f"docker run --rm -v {workspace}:/workspace -it maand {command}", stdout=subprocess.PIPE, shell=True)
    if r.returncode != 0:
        raise Exception(r.stdout.decode('utf-8').strip())


def __prepare_args_agents_roles_concurrency(cmd, roles=None, agents=None, concurrency=4):
    c = [cmd]
    if roles:
        c.append("--roles={}".format(",".join(roles)))
    if agents:
        c.append("--agents={}".format(",".join(agents)))
    if concurrency:
        c.append("--concurrency={}".format(concurrency))
    return " ".join(c)


def __prepare_args_agents_jobs_concurrency(cmd, agents=None, jobs=None, min_order=None, max_order=None, include_disabled=False, concurrency=4):
    c = [cmd]
    if agents:
        c.append("--agents={}".format(",".join(agents)))
    if jobs:
        c.append("--jobs={}".format(",".join(jobs)))
    if min_order:
        c.append("--min-order={}".format(min_order))
    if max_order:
        c.append("--max-order={}".format(max_order))
    if include_disabled:
        c.append("--include-disabled")
    if concurrency:
        c.append("--concurrency={}".format(concurrency))
    return " ".join(c)


def __prepare_args_jobs_concurrency(cmd, jobs=None, min_order=None, max_order=None, include_disabled=False, concurrency=4):
    c = [cmd]
    if jobs:
        c.append("--jobs={}".format(",".join(jobs)))
    if min_order:
        c.append("--min-order={}".format(min_order))
    if max_order:
        c.append("--max-order={}".format(max_order))
    if include_disabled:
        c.append("--include-disabled")
    if concurrency:
        c.append("--concurrency={}".format(concurrency))
    return " ".join(c)


def update(jobs=None, min_order=None, max_order=None, include_disabled=False, concurrency=4):
    return __prepare_args_jobs_concurrency("update", jobs=jobs, min_order=min_order, max_order=max_order, include_disabled=include_disabled, concurrency=concurrency)


def run_command_no_check(roles=None, agents=None, concurrency=4):
    return __prepare_args_agents_roles_concurrency("run_command_no_check", roles=roles, agents=agents, concurrency=concurrency)


def run_command(roles=None, agents=None, concurrency=4):
    return __prepare_args_agents_roles_concurrency("run_command", roles=roles, agents=agents, concurrency=concurrency)


def run_command_with_health_check(roles=None, agents=None, concurrency=1):
    return __prepare_args_agents_roles_concurrency("run_command", roles=roles, agents=agents, concurrency=concurrency)


def start_jobs(agents=None, jobs=None, min_order=None, max_order=None, include_disabled=False, concurrency=4):
    return __prepare_args_agents_jobs_concurrency("start_jobs", agents=agents, jobs=jobs, min_order=min_order,
                                                  max_order=max_order, include_disabled=include_disabled,
                                                  concurrency=concurrency)


def stop_jobs(agents=None, jobs=None, min_order=None, max_order=None, include_disabled=False, concurrency=4):
    return __prepare_args_agents_jobs_concurrency("stop_jobs", agents=agents, jobs=jobs, min_order=min_order,
                                                  max_order=max_order, include_disabled=include_disabled,
                                                  concurrency=concurrency)


def restart_jobs(agents=None, jobs=None, min_order=None, max_order=None, include_disabled=False, concurrency=4):
    return __prepare_args_agents_jobs_concurrency("restart_jobs", agents=agents, jobs=jobs, min_order=min_order,
                                                  max_order=max_order, include_disabled=include_disabled,
                                                  concurrency=concurrency)


def rolling_restart_jobs(agents=None, jobs=None, min_order=None, max_order=None, include_disabled=False, concurrency=4):
    return __prepare_args_agents_jobs_concurrency("rolling_restart_jobs", agents=agents, jobs=jobs, min_order=min_order,
                                                  max_order=max_order, include_disabled=include_disabled,
                                                  concurrency=concurrency)


def health_check(agents=None, jobs=None, min_order=None, max_order=None, include_disabled=False, concurrency=4):
    return __prepare_args_agents_jobs_concurrency("health_check", agents=agents, jobs=jobs, min_order=min_order,
                                                  max_order=max_order, include_disabled=include_disabled,
                                                  concurrency=concurrency)


def initialize():
    return "initialize"