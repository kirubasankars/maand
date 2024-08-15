import utils
import context_manager
import command_helper

context_manager.validate_cluster_id()
command_helper.command2_remote("sh /workspace/command.sh", sudo=utils.is_sudo_enabled())
