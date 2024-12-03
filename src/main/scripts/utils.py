import argparse
import configparser
import subprocess
from functools import cache

import const

from log_manager import LoggerManager

log_manager = LoggerManager()

def get_logger(ns="maand"):
    return log_manager.get_logger(ns)


def is_sudo_enabled(env):
    return env.get("USE_SUDO", "0") == "1"


def get_args_agents_jobs_concurrency():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--jobs', default="")
    parser.add_argument('--concurrency', default="4", type=int)
    args = parser.parse_args()

    if args.agents:
        args.agents = args.agents.split(',')
    else:
        args.agents = []
    if args.jobs:
        args.jobs = args.jobs.split(',')
    else:
        args.jobs = []

    return args


def get_args_agents_jobs_health_check():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--jobs', default="")
    parser.add_argument('--target', default="", required=True)
    parser.add_argument('--health_check', action='store_true')
    parser.set_defaults(health_check=False)

    args = parser.parse_args()

    if args.agents:
        args.agents = args.agents.split(',')
    else:
        args.agents = []
    if args.jobs:
        args.jobs = args.jobs.split(',')
    else:
        args.jobs = []

    return args


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


def get_args_jobs_concurrency():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', default="", required=False)
    parser.add_argument('--concurrency', default="1", type=int)
    args = parser.parse_args()

    if args.jobs:
        args.jobs = args.jobs.split(',')

    return args


def get_args_healthcheck():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', default="", required=False)
    parser.add_argument('--no-wait', action='store_true')
    parser.set_defaults(no_wait=False)
    args = parser.parse_args()

    if args.jobs:
        args.jobs = args.jobs.split(',')

    return args


@cache
def get_maand_conf():
    config_parser = configparser.ConfigParser()
    config_parser.read(const.CONF_PATH)
    return config_parser


def stop_the_world():
    subprocess.run(["kill", "-TERM", "1"])