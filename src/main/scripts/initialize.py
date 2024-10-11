import os
import uuid

import cert_provider
import command_helper
import kv_manager
import utils

logger = utils.get_logger()
kv_manager.setup()

cluster_id = kv_manager.get_value("maand", "cluster_id")
if cluster_id:
    logger.error("found /workspace/cluster_id.txt, cluster is already initialized")
    exit(1)

kv_manager.put_key_value("maand", "cluster_id", str(uuid.uuid4()))
kv_manager.put_key_value("maand", "update_seq", str(1))

command_helper.command_local("""
    touch /workspace/{variables.env,secrets.env,agents.json}
""")

if not os.path.isfile('/workspace/ca.key'):
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(cluster_id, int(os.getenv("CA_TTL", "3650")))