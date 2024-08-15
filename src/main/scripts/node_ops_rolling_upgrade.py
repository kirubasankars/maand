import time

import utils
import command_helper
import context_manager
import node_ops_run_job_command
import node_ops_update

context_manager.validate_cluster_id()

node_ops_run_job_command.run_command("health_check")
node_ops_update.sync()
command_helper.command_remote("sh /opt/agent/bin/force_deploy_jobs.sh", sudo=utils.is_sudo_enabled())

time.sleep(10)
for i in range(10):
    try:
        node_ops_run_job_command.run_command("health_check")
        break
    except:
        time.sleep(10)

