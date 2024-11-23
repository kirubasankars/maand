import configparser
import os
import sys

import cert_provider
import command_helper
import const
import kv_manager
import maand
import utils

config_parser = configparser.ConfigParser()
logger = utils.get_logger()

try:
    command_helper.command_local(f"mkdir -p {const.BUCKET_PATH}/{{workspace,secrets,logs,data}}")

    db = maand.get_db()
    cursor = db.cursor()
    maand.setup_maand_database(cursor)
    maand.setup_agent_database(cursor)
    maand.setup_job_database(cursor)

    kv_manager.setup()

except Exception as e:
    print(f"ERROR: {e}", flush=True)
    sys.exit(1)

command_helper.command_local(f"touch {const.WORKSPACE_PATH}/{{variables.env,secrets.env,command.sh,agents.json}}")

with open(f"{const.WORKSPACE_PATH}/agents.json", "r") as f:
    data = f.read().strip()
    if len(data) == 0:
        command_helper.command_local(f"echo '[]' > {const.WORKSPACE_PATH}/agents.json")

config = {
    "ca_ttl": str(365 * 10),
    "use_sudo": "1",
    "ssh_user": "agent",
    "ssh_key": "agent.key"
}

config_parser.add_section("default")
for key, value in config.items():
    config_parser.set('default', key, value)

if not os.path.isfile(const.CONF_PATH):
    with open(const.CONF_PATH, 'w') as f:
        config_parser.write(f)

config_parser = utils.get_maand_conf()

if not os.path.isfile(f'{const.BUCKET_PATH}/secrets/ca.key'):
    ca_ttl = config_parser.get("default", "ca_ttl")
    bucket_id = maand.get_bucket_id(cursor)
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(bucket_id, ca_ttl)

db.commit()
