import shutil

import utils
from maand import *

def test_update_no_jobs():
    shutil.rmtree("/workspace/jobs", ignore_errors=True)

    utils.initialize_cluster()

    run(plan())
    run(apply())

    utils.sync()
    run(run_command_local())

    agents = utils.get_agents()

    for agent in agents:
        ip = agent["host"]
        assert os.path.isdir(f"/workspace/tmp/{ip}")
        assert os.path.isdir(f"/workspace/tmp/{ip}/bin")
        assert os.path.isfile(f"/workspace/tmp/{ip}/bin/runner.py")

        assert os.path.isdir(f"/workspace/tmp/{ip}/certs")
        assert os.path.isfile(f"/workspace/tmp/{ip}/certs/agent.crt")
        assert os.path.isfile(f"/workspace/tmp/{ip}/certs/agent.key")
        assert os.path.isfile(f"/workspace/tmp/{ip}/certs/ca.crt")

        assert os.path.isfile(f"/workspace/tmp/{ip}/agent_id.txt")
        assert os.path.isfile(f"/workspace/tmp/{ip}/cluster_id.txt")
        assert os.path.isfile(f"/workspace/tmp/{ip}/context.env")
        assert os.path.isfile(f"/workspace/tmp/{ip}/jobs.json")
        assert os.path.isfile(f"/workspace/tmp/{ip}/roles.txt")
        assert os.path.isfile(f"/workspace/tmp/{ip}/update_seq.txt")


def test_update_with_node_exporter():
    os.makedirs("/workspace/jobs", exist_ok=True)
    shutil.copytree("/jobs/prometheus", "/workspace/jobs/prometheus")

    run(plan())
    run(apply())

