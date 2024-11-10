import os
import command_helper
import context_manager
import system_manager
import maand
import utils

def run_command(agent_ip):
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.command_remote(f"echo {agent_ip} $(uptime)", env=agent_env)

if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()
    with maand.get_db() as db:
        cursor = db.cursor()

        namespace = maand.get_namespace_id(cursor)
        os.environ.setdefault("NAMESPACE", namespace)
        update_seq = maand.get_update_seq(cursor)
        os.environ.setdefault("UPDATE_SEQ", str(update_seq))

        system_manager.run(cursor, command_helper.scan_agent, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
        system_manager.run(cursor, run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
