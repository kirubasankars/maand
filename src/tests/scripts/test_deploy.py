from utils import *

import workspace


def test_update_seq():
    clean()
    scan_agent()
    command(get_maand_command("init"))
    command(get_maand_command("update"))

    sync()
    agents_ip = workspace.get_agents_ip()
    bucket_id = workspace.get_bucket_id()

    for agent in agents_ip:
        files = [
            f"/bucket/tmp/{agent}/{bucket_id}/certs/agent.crt",
            f"/bucket/tmp/{agent}/{bucket_id}/certs/agent.key",
            f"/bucket/tmp/{agent}/{bucket_id}/certs/ca.crt",
            f"/bucket/tmp/{agent}/{bucket_id}/jobs.json",
            f"/bucket/tmp/{agent}/{bucket_id}/bin/runner.py",
            f"/bucket/tmp/{agent}/{bucket_id}/roles.txt",
            f"/bucket/tmp/{agent}/{bucket_id}/update_seq.txt",
            f"/bucket/tmp/{agent}/{bucket_id}/agent.txt",
        ]
        for f in files:
            assert os.path.exists(f)

    for agent in agents_ip:
        assert read_file_content(f"/bucket/tmp/{agent}/{bucket_id}/update_seq.txt") == "1"

    command(get_maand_command("update"))
    sync()

    for agent in agents_ip:
        assert read_file_content(f"/bucket/tmp/{agent}/{bucket_id}/update_seq.txt") == "2"


def test_update_add_jobs_incrementally():
    clean()
    scan_agent()

    command(get_maand_command("init"))

    bucket_id = workspace.get_bucket_id()
    make_job("a", ["agent"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/manifest.json")

    make_job("b", ["agent"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/manifest.json")
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/manifest.json")


def test_update_a_job():
    clean()
    command(get_maand_command("init"))

    bucket_id = workspace.get_bucket_id()
    make_job("a", ["agent"])
    make_job("b", ["agent"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/manifest.json")
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/manifest.json")

    make_job("c", ["agent"])
    command("touch /bucket/workspace/jobs/a/test_file")
    command("touch /bucket/workspace/jobs/b/test_file")
    command("touch /bucket/workspace/jobs/c/test_file")
    command(get_maand_command("build"))

    command(get_maand_command("update --jobs=a"))
    sync()

    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/test_file")
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/test_file")
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/c/test_file")

    command("rm /bucket/workspace/jobs/a/test_file")
    command("touch /bucket/workspace/jobs/b/test_file")
    command(get_maand_command("build"))

    command(get_maand_command("update --jobs=b"))
    sync()

    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/test_file")
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/test_file")
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/c/test_file")

    command(get_maand_command("update --jobs=a,b"))
    sync()

    for agent in agents_ip:
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/test_file")
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/test_file")
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/c/test_file")

    for agent in agents_ip:
        assert read_file_content(f"/bucket/tmp/{agent}/{bucket_id}/update_seq.txt") == "4"


def test_update_add_a_job_with_agent_role():
    clean()

    command(get_maand_command("init"))
    bucket_id = workspace.get_bucket_id()

    make_job("a", ["group1"])
    make_job("b", ["group2"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/manifest.json")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/manifest.json")

    make_job("c", ["group3"])
    command("touch /bucket/workspace/jobs/a/test_file")
    command("touch /bucket/workspace/jobs/b/test_file")
    command("touch /bucket/workspace/jobs/c/test_file")
    command(get_maand_command("build"))

    command(get_maand_command("update --jobs=a"))
    sync()

    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group3")
    for agent in agents_ip:
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/c/test_file")

    command("rm /bucket/workspace/jobs/a/test_file")
    command(get_maand_command("build"))
    command(get_maand_command("update --jobs=b"))
    sync()

    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group3")
    for agent in agents_ip:
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/c/test_file")

    command(get_maand_command("update --jobs=a,b"))
    sync()

    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group3")
    for agent in agents_ip:
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/c/test_file")

    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        assert read_file_content(f"/bucket/tmp/{agent}/{bucket_id}/update_seq.txt") == "4"


def test_update_remove_job():
    clean()
    command(get_maand_command("init"))

    make_job("a", roles=["group1"])
    make_job("b", roles=["group2"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))

    sync()

    shutil.rmtree("/bucket/workspace/jobs/b")
    command(get_maand_command("build"))
    command(get_maand_command("update"))

    sync()

    bucket_id = workspace.get_bucket_id()
    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/a/Makefile")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert not os.path.exists(f"/bucket/tmp/{agent}/{bucket_id}/jobs/b/Makefile")
