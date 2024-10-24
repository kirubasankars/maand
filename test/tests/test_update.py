import os
import shutil

import maand

agents = maand.agents_ip(None)
agents_ip = [item.get("host") for item in agents]

def test_update():
    maand.clean()
    maand.initialize()
    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        files = [
            f"/{agent}/certs/agent.crt",
            f"/{agent}/certs/agent.key",
            f"/{agent}/certs/ca.crt",
            f"/{agent}/jobs.json",
            f"/{agent}/bin/runner.py",
            f"/{agent}/roles.txt",
            f"/{agent}/update_seq.txt",
            f"/{agent}/agent_id.txt",
        ]
        for f in files:
            assert os.path.exists(f)


def test_add_job_a():
    maand.make_job("a", ["agent"])

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        assert os.path.exists(f"/{agent}/jobs/a/manifest.json")


def test_add_job_b():
    maand.make_job("b", ["agent"])

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        assert os.path.exists(f"/{agent}/jobs/b/manifest.json")


def test_update_jobs():
    with open("/workspace/jobs/a/new_file.txt", "w") as f:
        f.write("test_file")
    with open("/workspace/jobs/b/new_file.txt", "w") as f:
        f.write("test_file")

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        assert os.path.exists(f"/{agent}/jobs/a/new_file.txt")
        assert os.path.exists(f"/{agent}/jobs/b/new_file.txt")

        with open("/workspace/jobs/a/new_file.txt", "r") as f:
            assert "test_file" == f.read().strip()
        with open("/workspace/jobs/b/new_file.txt", "r") as f:
            assert "test_file" == f.read().strip()

    with open("/workspace/jobs/a/new_file.txt", "w") as f:
        f.write("test_file_v2")
    with open("/workspace/jobs/b/new_file.txt", "w") as f:
        f.write("test_file_v2")

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        assert os.path.exists(f"/{agent}/jobs/a/new_file.txt")
        with open("/workspace/jobs/a/new_file.txt", "r") as f:
            assert "test_file_v2" == f.read().strip()
        with open("/workspace/jobs/b/new_file.txt", "r") as f:
            assert "test_file_v2" == f.read().strip()


def test_update_jobs_delete_file():
    os.remove("/workspace/jobs/a/new_file.txt")

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        assert not os.path.exists(f"/{agent}/jobs/a/new_file.txt")


def test_add_job_c():
    maand.make_job("c", ["agent"])

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        assert os.path.exists(f"/{agent}/jobs/c/manifest.json")


def test_remove_job_c():
    shutil.rmtree("/workspace/jobs/c")
    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        assert not os.path.exists(f"/{agent}/jobs/c")