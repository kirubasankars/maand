import os

from dotenv import dotenv_values

import context_manager
import cert_provider
import command_helper
import kv_manager
import maand
import job
import utils

logger = utils.get_logger()

try:
    maand.setup()
    job.setup()
    kv_manager.setup()
except Exception as e:
    logger.error(f"ERROR: {e}")
    context_manager.stop_the_world()

command_helper.command_local("""
    touch /workspace/{variables.env,secrets.env,command.sh,agents.json}
""")

config = {
    "CA_TTL": str(365 * 10),
    "USE_SUDO": 1,
    "SSH_USER": "root",
    "SSH_KEY": "agent.key"
}

if not os.path.isfile("/workspace/maand.config.env"):
    with open('/workspace/maand.config.env', 'w') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")

config = dotenv_values("/workspace/maand.config.env")
if not os.path.isfile('/workspace/ca.key'):
    cluster_id = maand.get_cluster_id()
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(cluster_id, int(os.getenv("CA_TTL", str(365 * 10))))