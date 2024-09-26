import os.path

import command_helper
import context_manager
import system_manager
import utils

if not os.path.exists("/workspace/command.sh"):
    raise Exception("No command file found")


def validate_cluster_id(agent_ip):
    context_manager.rsync_download_agent_files(agent_ip)
    context_manager.validate_cluster_id(agent_ip)


def run_command(agent_ip):
    jobs = ""
    if jobs_filter:
        jobs = ",".join(jobs_filter)
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.command_remote(f"python /opt/agent/bin/runner.py stop {jobs}", env=agent_env)


roles, agents, jobs_filter = utils.args_roles_agents_jobs()
system_manager.run(validate_cluster_id)
system_manager.run(run_command)
