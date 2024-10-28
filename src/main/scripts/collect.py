import argparse
import json

import maand_agent
import command_helper
import context_manager
import system_manager
import utils

alias = ""
command = ""

def run_command(agent_ip):
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.command_local(f"mkdir -p /workspace/reports/{alias}")
    filename = agent_ip.replace(".", "_")
    with open(f"/workspace/reports/{alias}/{filename}.out", "a") as f:
        roles = json.dumps(maand_agent.get_agent_roles(agent_ip))
        f.write(f"Agent IP: {agent_ip}\n")
        f.flush()
        command_helper.command_remote("echo \"Host Name: $(hostname)\"\n", env=agent_env, stdout=f, stderr=f)
        f.write(f"Roles: {roles}\n")
        f.write(f"\n")
        f.flush()
        command_helper.command_remote(command, env=agent_env, stdout=f, stderr=f)


if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()

    parser = argparse.ArgumentParser()
    parser.add_argument('--commands', default="")
    command_args, _  = parser.parse_known_args()

    commands_to_collect = []
    if command_args.commands:
        commands_to_collect = command_args.commands.split(",")

    system_manager.run(command_helper.scan_agent, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)

    commands_map = {
        "ss": "ss -tuln",
        "df": "df -h",
        "dstat": "dstat 1 5 -am --nocolor",
        "services": "systemctl list-units --type=service --all",
        "docker": "docker ps",
        "lscpu": "lscpu",
        "free": "free -h",
        "ps": "ps -aux",
        "uptime": "uptime"
    }

    commands_to_execute = []

    if len(commands_to_collect) == 0:
        commands_to_execute = commands_map.keys()
    else:
        for cmd in commands_to_collect:
            if cmd in commands_map:
                commands_to_execute.append(cmd)
            else:
                raise Exception(f"{cmd} is not a valid command")

    command_helper.command_local(f"rm -rf /workspace/reports")

    for cmd in commands_to_execute:
        alias = cmd
        command = commands_map[cmd]
        print(f"collecting {alias}")
        system_manager.run(run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
