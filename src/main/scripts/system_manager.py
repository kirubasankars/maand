import multiprocessing
import sys

import utils


def split_list(input_list, chunk_size=3):
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def run(func, concurrency=None):
    agents = utils.get_agent_and_roles()
    agents_ip = list(agents.keys())
    if len(agents_ip) == 0:
        sys.exit(0)

    work_items = split_list(agents_ip, chunk_size=concurrency or len(agents_ip))
    for work_item in work_items:
        with multiprocessing.Pool(processes=len(work_item)) as pool:
            pool.map(func, work_item)
