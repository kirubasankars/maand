import os
import time

import utils
import command_helper
import context_manager
import node_ops_run_job_command
import node_ops_update

wait_secs = 10


def health_check():
    for i in range(10):
        try:
            node_ops_run_job_command.run_command("health_check")
            break
        except:
            if i >= 9:
                raise Exception("Health check failed")
            time.sleep(wait_secs)


health_check()
context_manager.validate_cluster_id()
node_ops_update.sync()
command_helper.command_remote("sh /opt/agent/bin/force_deploy_jobs.sh", sudo=utils.is_sudo_enabled())
time.sleep(wait_secs)
health_check()
