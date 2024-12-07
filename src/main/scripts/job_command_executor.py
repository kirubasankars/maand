import argparse
import importlib
import json
import os
import io
from multiprocessing import Process

import context_manager
import contextlib
import sys
import maand
import utils

logger = utils.get_logger()

def executor(job_command, demands, env):
    with open(f"{os.path.curdir}/demands.json", "w") as f:
        f.write(json.dumps(demands))
    for k, v in env.items():
        os.environ.setdefault(k, v)
    try:
        result = job_command.execute()
        if result is None:
            return True
        else:
            return result
    except Exception as e:
        logger.error(e)
        return False


def execute_job_event_command(cursor, job, command, event):
    maand.export_env_bucket_update_seq(cursor)
    os.environ.setdefault("JOB", job)

    cursor.execute("SELECT depend_on_job, depend_on_command, depend_on_config FROM job_db.job_commands WHERE job_name = ? AND name = ? AND executed_on = ?", (job, command, event,))
    rows = cursor.fetchall()

    demands = []
    for depend_on_job, depend_on_command, depend_on_config in rows:
        demands.append({"job": depend_on_job, "command": depend_on_command, "config": json.loads(depend_on_config) })

    maand.copy_job_modules(cursor, job)
    spec = importlib.util.spec_from_file_location(job, f"/modules/{job}/_modules/command_{command}.py")
    job_command = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(job_command)

    allocations = maand.get_allocations(cursor, job)
    agent_context = allocations

    if "on_context" in dir(job_command):
        selector = job_command.on_context()
        env = context_manager.get_agent_env(allocations[0])
        selector_agents_ip = env.get(selector, "")
        agent_context = selector_agents_ip.split(",")

    result = True
    for agent_ip in agent_context:
        env = context_manager.get_agent_env(agent_ip)
        env["JOB"] = job
        #with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            p = Process(target=executor, args=(job_command, demands, env,))
            p.start()
            p.join()
            if p.exitcode != 0:
                logger.info(f"Health check failed for {job} and allocation {agent_ip}.")
                result = False
        except:
            logger.info(f"Health check failed for {job} and allocation {agent_ip}.")
            result = False
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', default="", required=True)
    parser.add_argument('--command', default="", required=True)
    args = parser.parse_args()

    event = os.environ.get("EVENT", "direct")

    with maand.get_db() as db:
        cursor = db.cursor()

        commands = maand.get_job_commands(cursor, args.job, event)
        if args.command not in commands:
            raise Exception(f"job: {args.job}, command: {args.command}, event {event} not found")

        result = execute_job_event_command(cursor, args.job, args.command, event)
        if not result:
            sys.exit(1)


if __name__ == '__main__':
    main()
