import utils
from maand import *

def test_update():
    utils.initialize_cluster()
    run(run_command_no_check())
    run(update())

def test_update_jobs():
    run(update(jobs=["opensearch"]))