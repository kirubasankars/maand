import command_helper
import context_manager
import system_manager
import maand
import utils

def run_command(agent_ip):
    agent_env = context_manager.get_agent_minimal_env(agent_ip)
    command_helper.capture_command_remote(f"uptime", env=agent_env, log_file=f"/tmp/{agent_ip}.log", prefix=agent_ip)

if __name__ == "__main__":
    args = utils.get_args_agents_roles_concurrency()

    with maand.get_db() as db:
        cursor = db.cursor()

        maand.export_env_bucket_update_seq(cursor)
        system_manager.run(cursor, command_helper.scan_agent, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
        system_manager.run(cursor, run_command, concurrency=args.concurrency, roles_filter=args.roles, agents_filter=args.agents)
