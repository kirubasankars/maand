import os

import context_manager
import cert_provider
import command_helper
import kv_manager
import maand
import utils

logger = utils.get_logger()

try:
    maand.setup()
    kv_manager.setup()
except Exception as e:
    logger.error(f"ERROR: {e}")
    context_manager.stop_the_world()

command_helper.command_local("""
    touch /workspace/{variables.env,secrets.env,command.sh,agents.json}
""")

if not os.path.isfile('/workspace/ca.key'):
    cluster_id = maand.get_cluster_id()
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(cluster_id, int(os.getenv("CA_TTL", "3650")))
