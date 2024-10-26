import os

import maand

agents = maand.agents_ip(None)
agents_ip = [item.get("host") for item in agents]


def test_start_jobs():
    maand.clean()
    maand.initialize()

    maand.make_job("a", ["agent"])

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        with open(f"/{agent}/update_seq.txt", "r") as f:
            assert f.read().strip() == "1"

    maand.start_jobs()
    maand.sync_files()

    for agent in agents_ip:
        with open(f"/{agent}/jobs/a/start", "r") as f:
            assert f.read().strip() == "1"

    maand.start_jobs()
    maand.sync_files()

    for agent in agents_ip:
        with open(f"/{agent}/jobs/a/start", "r") as f:
            assert f.read().strip() == "2"


def test_start_a_job_b():
    maand.clean()
    maand.initialize()

    maand.make_job("a", ["agent"])
    maand.make_job("b", ["agent"])

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        with open(f"/{agent}/update_seq.txt", "r") as f:
            assert f.read().strip() == "1"

    maand.start_jobs(jobs="a")
    maand.sync_files()

    for agent in agents_ip:
        assert not os.path.exists(f"/{agent}/jobs/b/start")
        with open(f"/{agent}/jobs/a/start", "r") as f:
            assert f.read().strip() == "1"


def test_stop_jobs():
    maand.clean()
    maand.initialize()

    maand.make_job("a", ["agent"])


    maand.build()
    maand.deploy()
    maand.stop_jobs()
    maand.sync_files()

    for agent in agents_ip:
        maand.tree(f"/{agent}/jobs")
        with open(f"/{agent}/jobs/a/stop", "r") as f:
            assert f.read().strip() == "1"

    maand.stop_jobs()
    maand.sync_files()

    for agent in agents_ip:
        with open(f"/{agent}/jobs/a/stop", "r") as f:
            assert f.read().strip() == "2"


def test_restart_jobs():
    maand.clean()
    maand.initialize()

    maand.make_job("a", ["agent"])

    maand.build()
    maand.deploy()
    maand.sync_files()

    for agent in agents_ip:
        with open(f"/{agent}/update_seq.txt", "r") as f:
            assert f.read().strip() == "1"

    maand.restart_jobs()
    maand.sync_files()

    for agent in agents_ip:
        with open(f"/{agent}/jobs/a/restart", "r") as f:
            assert f.read().strip() == "1"

    maand.restart_jobs()
    maand.sync_files()

    for agent in agents_ip:
        with open(f"/{agent}/jobs/a/restart", "r") as f:
            assert f.read().strip() == "2"

