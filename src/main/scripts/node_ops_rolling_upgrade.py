import time

import command_helper
import context_manager
import node_ops_update
import node_ops_health_check

context_manager.validate_cluster_id()

node_ops_health_check.health_check()
node_ops_update.sync()
command_helper.command_remote("sh /opt/agent/bin/force_deploy_jobs.sh")
time.sleep(10)
node_ops_health_check.health_check()
