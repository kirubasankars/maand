import re
import argparse
import configparser
import subprocess
from functools import cache

import const
from log_manager import LoggerManager

log_manager = LoggerManager()

def get_logger(ns="maand"):
    return log_manager.get_logger(ns)

def get_args_agents_roles_concurrency(allow_no_check=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--roles', default="")
    parser.add_argument('--concurrency', default="4", type=int)

    if allow_no_check:
        parser.add_argument('--no-check', action='store_true')
        parser.set_defaults(no_check=False)

    args = parser.parse_args()

    if args.agents:
        args.agents = args.agents.split(',')
    if args.roles:
        args.roles = args.roles.split(',')

    return args


@cache
def get_maand_conf():
    config_parser = configparser.ConfigParser()
    config_parser.read(const.CONF_PATH)
    return config_parser


def split_list(input_list, chunk_size=3):
    return [
        input_list[i : i + chunk_size] for i in range(0, len(input_list), chunk_size)
    ]


def extract_size_in_mb(size_string):
    # If input is an integer, directly return it as MB
    if isinstance(size_string, int):
        return float(size_string)
    unit_to_mb = {
        "MB": 1,
        "GB": 1024,
        "TB": 1024 ** 2,
    }
    match = re.match(r"([\d.]+)\s*([a-zA-Z]+)", size_string)
    if not match:
        raise ValueError(f"Invalid size string: {size_string}")
    size = float(match.group(1))
    unit = match.group(2).upper()
    if unit not in unit_to_mb:
        raise ValueError(f"Unit smaller than MB or invalid: {unit}")
    size_in_mb = size * unit_to_mb[unit]
    return size_in_mb


def stop_the_world():
    subprocess.run(["kill", "-TERM", "1"])
