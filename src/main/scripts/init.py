import argparse
import os
import sys

import configparser

import cert_provider
import command_helper
import kv_manager
import maand_agent
import utils

parser = argparse.ArgumentParser()
parser.add_argument("--name", help="name of the namespace", default="default")
args = parser.parse_args()

config_parser = configparser.ConfigParser()
logger = utils.get_logger()

try:
    command_helper.command_local("mkdir -p /workspace/{data,secrets}")
    maand_agent.setup(args.name)
    kv_manager.setup()
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    sys.exit(1)

command_helper.command_local("touch /workspace/{variables.env,secrets/secrets.env,command.sh,agents.json}")

config = {
    "ca_ttl": str(365 * 10),
    "use_sudo": "1",
    "ssh_user": "agent",
    "ssh_key": "agent.key"
}

config_parser.add_section("default")
for key, value in config.items():
    config_parser.set('default', key, value)

if not os.path.isfile("/workspace/maand.conf"):
    with open('/workspace/maand.conf', 'w') as f:
        config_parser.write(f)

config_parser = utils.get_maand_conf()

if not os.path.isfile('/workspace/secrets/ca.key'):
    ca_ttl = config_parser.get("default", "ca_ttl")
    namespace_id = maand_agent.get_namespace_id()
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(namespace_id, ca_ttl)

command_helper.command_local("chmod 777 /workspace/{*.env,secrets/secrets.env,*.conf,command.sh,agents.json}")
