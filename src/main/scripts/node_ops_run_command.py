import os
import subprocess
import sys
import uuid

import utils
import command_helper
import node_ops_update

logger = utils.get_logger()

cluster_id = os.getenv("CLUSTER_ID")

if not cluster_id:
    logger.error("Required environment variable: CLUSTER_ID is not set.")
    sys.exit(1)

command_helper.command_local("""
    bash /scripts/rsync_remote_local.sh
""")

values, agent_ip = node_ops_update.load_values()
values = node_ops_update.add_roles_to_values(values)
values = node_ops_update.add_tags_to_values(values, agent_ip)

with open("/tmp/values.env", "w") as f:
    for key, value in values.items():
        f.write("export {}={}\n".format(key, value))

file_id = uuid.uuid4()
with open(f"/tmp/{file_id}", "w") as f:
    f.write("#!/bin/bash\n")
    f.write("set -ueo pipefail\n")
    f.write("scp /tmp/values.env $SSH_USER@$AGENT_IP:/tmp/values.env\n")
    f.write(f"ssh -o StrictHostKeyChecking=no -o LogLevel=error $SSH_USER@$AGENT_IP 'source /tmp/values.env && bash -xs' < /workspace/command.sh")
file_path = f"/tmp/{file_id}"
r = subprocess.run(["sh", file_path], env=os.environ.copy())

if r.returncode != 0:
    sys.exit(r.returncode)
