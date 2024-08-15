import context_manager
import command_helper

context_manager.validate_cluster_id()

values = context_manager.get_values()
with open("/opt/agent/context.env", "w") as f:
    keys = sorted(values.keys())
    for key in keys:
        value = values.get(key)
        f.write("{}={}\n".format(key, value))

command_helper.command_local("sh /workspace/command.sh")
