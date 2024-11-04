import argparse
import importlib
import json
import os

import maand_job
import sys

import utils

logger = utils.get_logger()

def execute_command(job, command):
    if "/commands" not in sys.path:
        sys.path.append("/commands")
    os.makedirs("/commands", exist_ok=True)

    with maand_job.get_db() as db:
        cursor = db.cursor()

        cursor.execute("SELECT path, content, isdir FROM job_files WHERE job_id = (SELECT job_id FROM job WHERE name = ?) AND path like ? ORDER BY isdir DESC", (job, f"{job}/_modules%"))
        rows = cursor.fetchall()

        for path, content, isdir in rows:
            if isdir:
                os.makedirs(f"/commands/{path}", exist_ok=True)
                continue
            with open(f"/commands/{path}", "wb") as f:
                f.write(content)

        cursor.execute("SELECT job_name, name as command_name, depend_on_config as config FROM job_commands WHERE depend_on_job = ? AND depend_on_command = ?", (job, command, ))
        rows = cursor.fetchall()

        context = []
        for job_name, command_name, config in rows:
            context.append({"job": job_name, "command": command_name, "config": json.loads(config) })

        with open(f"/commands/{job}/_modules/context.json", "w") as f:
            f.write(json.dumps(context))
    try:
        job_command = importlib.import_module(f'{job}._modules.command_{command}')
        if "execute" in dir(job_command):
            os.chdir(f"/commands/{job}/_modules")
            job_command.execute()
            os.chdir(f"/")
        else:
            logger.error(f"execute method not found: command_{command}")
    except ModuleNotFoundError:
        logger.error(f"command not found: job = {job}, command = command_{command}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('job', default="")
    parser.add_argument('command', default="")
    args, _ = parser.parse_known_args()
    execute_command(args.job, args.command)