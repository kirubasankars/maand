import os
import sys

from dotenv import dotenv_values

import context_manager
import cert_provider
import command_helper
import kv_manager
import maand_agent
import maand_job
import utils

logger = utils.get_logger()

try:
    maand_agent.setup()
    maand_job.setup()
    kv_manager.setup()
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    sys.exit(1)

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
    cluster_id = maand_agent.get_cluster_id()
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(cluster_id, int(os.getenv("CA_TTL", str(365 * 10))))