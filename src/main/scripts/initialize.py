import os
import sys
import uuid

import context_manager
import cert_provider
import command_helper
import kv_manager
import utils

logger = utils.get_logger()
kv_manager.setup()

cluster_id = kv_manager.get_value("maand", "cluster_id")
if cluster_id:
    logger.error("found cluster_id, cluster is already initialized")
    context_manager.stop_the_world()

kv_manager.put_key_value("maand", "cluster_id", str(uuid.uuid4()))
kv_manager.put_key_value("maand", "update_seq", str(0))

command_helper.command_local("""
    touch /workspace/{variables.env,secrets.env,command.sh,agents.json}
""")

if not os.path.isfile('/workspace/ca.key'):
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(cluster_id, int(os.getenv("CA_TTL", "3650")))