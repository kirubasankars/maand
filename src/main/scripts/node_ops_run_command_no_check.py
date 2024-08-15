import utils
import command_helper

command_helper.command2_remote("/workspace/command.sh", sudo=utils.is_sudo_enabled())
