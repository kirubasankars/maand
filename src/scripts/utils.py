import argparse
import configparser
import functools
import logging
import os
import fcntl
from functools import cache
from logging import getLogger

import const


@functools.cache
def get_logger(ns=None):
    root_logger = getLogger(ns)
    console_handler = logging.StreamHandler()
    root_logger.addHandler(console_handler)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger.setLevel(log_level)
    return root_logger


def is_sudo_enabled(env):
    return env.get("USE_SUDO", "0") == "1"


def get_args_agents_jobs_concurrency():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--jobs', default="")
    parser.add_argument('--include-disabled', default=False, required=False, action='store_true')
    parser.add_argument('--concurrency', default="4", type=int)
    args, _ = parser.parse_known_args()

    if args.agents:
        args.agents = args.agents.split(',')
    else:
        args.agents = []
    if args.jobs:
        args.jobs = args.jobs.split(',')
    else:
        args.jobs = []

    return args


def get_args_agents_roles_concurrency():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', default="")
    parser.add_argument('--roles', default="")
    parser.add_argument('--concurrency', default="4", type=int)
    args, _ = parser.parse_known_args()

    if args.agents:
        args.agents = args.agents.split(',')
    if args.roles:
        args.roles = args.roles.split(',')

    return args

def get_args_jobs_concurrency():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', default="", required=False)
    parser.add_argument('--concurrency', default="4", type=int)
    args, _ = parser.parse_known_args()

    if args.jobs:
        args.jobs = args.jobs.split(',')

    return args

@cache
def get_maand_conf():
    config_parser = configparser.ConfigParser()
    config_parser.read(const.CONF_PATH)
    return config_parser

class FileMutex:
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    def acquire(self):
        self.file = open(self.filename, 'w')

        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)

    def release(self):
        """Release the mutex by unlocking the file."""
        if self.file:
            # Release the lock on the file
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)
            self.file.close()