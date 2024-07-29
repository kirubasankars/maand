import os

import utils
import command_helper
import context_manager

context_manager.validate_cluster_id()

agent_ip = os.getenv("AGENT_IP")

agents = utils.get_agent_roles()
roles = agents.get(agent_ip, [])

values = context_manager.get_values()
with open("/opt/agent/values.env", "w") as f:
    for key, value in values.items():
        f.write("export {}={}\n".format(key, value))

for role in roles:
    if os.path.exists(f"/workspace/jobs/{role}/modules/health_check.sh"):
        command_helper.command_local(f"""
            mkdir -p /modules/{role} && rsync -r /workspace/jobs/{role}/modules/ /modules/{role}/
            source /opt/agent/values.env && bash /modules/{role}/health_check.sh
        """)
