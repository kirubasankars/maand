import command_helper
import context_manager
import system_manager
import utils

def run_command(agent_ip):
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.command_remote(f"echo {agent_ip} $(uptime)", env=agent_env)

if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()
    system_manager.run(command_helper.scan_agent, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
    system_manager.run(run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
