import os

import maand_agent
import maand_job
import command_helper
import context_manager
import system_manager
import utils


def run_command(agent_ip):
    cmd = os.getenv("CMD")
    namespace = os.getenv("NAMESPACE")
    args = utils.get_args_agents_jobs_concurrency()

    with maand_agent.get_db() as db:
        maand_job.attach_job_db(db)

        cursor = db.cursor()
        agent_jobs = maand_agent.get_agent_jobs(cursor, agent_ip)

        missing_jobs = set(args.jobs) - set(agent_jobs.keys())
        if missing_jobs:
            raise Exception(f"No jobs found: {missing_jobs}")

        jobs = args.jobs or agent_jobs.keys()
        filtered_jobs = ",".join(jobs)
        agent_env = context_manager.get_agent_minimal_env(agent_ip)
        command_helper.command_remote(f"python3 /opt/agent/{namespace}/bin/runner.py {namespace} {cmd} --jobs {filtered_jobs}", env=agent_env)


def run():
    args = utils.get_args_agents_jobs_concurrency()

    with maand_agent.get_db() as db:

        cursor = db.cursor()
        namespace = maand_agent.get_namespace_id(cursor)
        os.environ.setdefault("NAMESPACE", namespace)
        update_seq = maand_agent.get_update_seq(cursor)
        os.environ.setdefault("UPDATE_SEQ", str(update_seq))

        system_manager.run(cursor, context_manager.validate_cluster_update_seq)
        system_manager.run(cursor, run_command, concurrency=args.concurrency, agents_filter=args.agents)


if __name__ == "__main__":
    run()