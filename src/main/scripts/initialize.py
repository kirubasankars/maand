import os
import uuid
import utils
import cert_provider
import command_helper

logger = utils.get_logger()
cluster_id = None

if os.path.isfile('/workspace/cluster_id.txt'):
    logger.error("found /workspace/cluster_id.txt, cluster is already initialized")
    exit(1)

with open('/workspace/cluster_id.txt', 'w') as f:
    f.write(uuid.uuid4().__str__())

with open('/workspace/update_seq.txt', 'w') as f:
    f.write(str(1))

command_helper.command_local("""
    touch /workspace/{variables.env,secrets.env,agents.json}    
    mkdir -p /workspace/jobs
""")

if not os.path.isfile('/workspace/ca.key'):
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(cluster_id, int(os.getenv("CA_TTL", "3650")))
