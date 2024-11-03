import os
import sys

import configparser

import cert_provider
import command_helper
import kv_manager
import maand_agent
import utils

import const

config_parser = configparser.ConfigParser()
logger = utils.get_logger()

db = maand_agent.get_db()
cursor = db.cursor()

try:
    command_helper.command_local("mkdir -p /namespace/{workspace,secrets}")
    maand_agent.setup(cursor)
    kv_manager.setup()
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    sys.exit(1)

command_helper.command_local(f"touch {const.WORKSPACE_PATH}/{{variables.env,secrets.env,command.sh,agents.json}}")

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

if not os.path.isfile('/namespace/secrets/ca.key'):
    ca_ttl = config_parser.get("default", "ca_ttl")
    namespace_id = maand_agent.get_namespace_id(cursor)
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(namespace_id, ca_ttl)

db.commit()