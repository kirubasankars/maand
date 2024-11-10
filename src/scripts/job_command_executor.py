import argparse
import importlib
import json
import os

import kv_manager
import sys
import maand
import utils

logger = utils.get_logger()


def run_job_command(job, job_command, demands, env):
    with open(f"{os.path.curdir}/demands.json", "w") as f:
        f.write(json.dumps(demands))

    for k, v in env.items():
        os.environ.setdefault(k, v)
    os.environ.setdefault("JOB", job)
    try:
        job_command.execute()
        return True
    except Exception as e:
        logger.error(e)
        return False


def execute_command(cursor, job, command, event):
    if "/commands" not in sys.path:
        sys.path.append("/commands")

    os.makedirs("/commands", exist_ok=True)
    if not maand.check_job_command_event(cursor, job, command, event):
        return False

    agent_0_ip = maand.get_first_agent_for_job(cursor, job)

    for namespace in ["variables.env", "secrets.env", "ports.env", f"vars/{agent_0_ip}"]:
        keys = kv_manager.get_keys(namespace)
        env = {}
        for key in keys:
            env[key] = kv_manager.get_value(namespace, key)

    cursor.execute("SELECT path, content, isdir FROM job_db.job_files WHERE job_id = (SELECT job_id FROM job_db.job WHERE name = ?) AND path like ? ORDER BY isdir DESC", (job, f"{job}/_modules%"))
    rows = cursor.fetchall()

    for path, content, isdir in rows:
        if isdir:
            os.makedirs(f"/commands/{path}", exist_ok=True)
            continue
        with open(f"/commands/{path}", "wb") as f:
            f.write(content)

    cursor.execute("SELECT job_name, name as command_name, depend_on_config as config FROM job_db.job_commands WHERE depend_on_job = ? AND depend_on_command = ?", (job, command, ))
    rows = cursor.fetchall()

    demands = []
    for job_name, command_name, config in rows:
        demands.append({"job": job_name, "command": command_name, "config": json.loads(config) })
    try:
        job_command = importlib.import_module(f'{job}._modules.command_{command}')
        if "execute" in dir(job_command):
            return run_job_command(job, job_command, demands, env)
        else:
            logger.error(f"execute method not found: command_{command}")
    except ModuleNotFoundError:
        logger.error(f"command not found: job = {job}, command = command_{command}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('job', default="")
    parser.add_argument('command', default="")
    args, _ = parser.parse_known_args()

    with maand.get_db() as db:
        cursor = db.cursor()
        execute_command(cursor, args.job, args.command, os.environ.get("EVENT", "direct"))