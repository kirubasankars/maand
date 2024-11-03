import maand_agent
import multiprocessing
import sys


def split_list(input_list, chunk_size=3):
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def run(agent_cursor, func, agents=None, concurrency=None, roles_filter=None, agents_filter=None):
    agents = agents or maand_agent.get_agents(agent_cursor, roles_filter)

    if agents_filter:
        agents = list(set(agents_filter) & set(agents))

    if len(agents) == 0:
        sys.exit(0)

    work_items = split_list(agents, chunk_size=concurrency or len(agents))
    for work_item in work_items:
        with multiprocessing.Pool(processes=len(work_item)) as pool:
            pool.map(func, work_item)