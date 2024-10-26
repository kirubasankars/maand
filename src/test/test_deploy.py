from utils import *
import workspace



def test_update_seq():

    clean()
    scan_agent()

    command(get_maand_command("initialize"))
    command(get_maand_command("build"))
    command(get_maand_command("deploy"))

    sync()
    agents_ip = workspace.get_agents_ip()

    for agent in agents_ip:
        files = [
            f"/workspace/data/{agent}/certs/agent.crt",
            f"/workspace/data/{agent}/certs/agent.key",
            f"/workspace/data/{agent}/certs/ca.crt",
            f"/workspace/data/{agent}/jobs.json",
            f"/workspace/data/{agent}/bin/runner.py",
            f"/workspace/data/{agent}/roles.txt",
            f"/workspace/data/{agent}/update_seq.txt",
            f"/workspace/data/{agent}/agent_id.txt",
        ]
        for f in files:
            assert os.path.exists(f)

    for agent in agents_ip:
        assert read_file_content(f"/workspace/data/{agent}/update_seq.txt") == "1"

    command(get_maand_command("deploy"))
    sync()

    for agent in agents_ip:
        assert read_file_content(f"/workspace/data/{agent}/update_seq.txt") == "2"


def test_add_jobs_incrementally():
    clean()
    scan_agent()

    command(get_maand_command("initialize"))
    make_job("a", ["agent"])

    command(get_maand_command("build"))
    command(get_maand_command("deploy"))
    sync()

    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/a/manifest.json")

    make_job("b", ["agent"])

    command(get_maand_command("build"))
    command(get_maand_command("deploy"))
    sync()

    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/a/manifest.json")
        assert os.path.exists(f"/workspace/data/{agent}/jobs/b/manifest.json")


def test_update_a_job():
    clean()
    command(get_maand_command("initialize"))

    make_job("a", ["agent"])
    make_job("b", ["agent"])

    command(get_maand_command("build"))
    command(get_maand_command("deploy"))
    sync()

    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/a/manifest.json")
        assert os.path.exists(f"/workspace/data/{agent}/jobs/b/manifest.json")

    make_job("c", ["agent"])
    command("touch /workspace/jobs/a/test_file")
    command("touch /workspace/jobs/b/test_file")
    command("touch /workspace/jobs/c/test_file")
    command(get_maand_command("build"))

    command(get_maand_command("deploy --jobs=a"))
    sync()

    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/a/test_file")
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/b/test_file")
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/c/test_file")

    command("rm /workspace/jobs/a/test_file")
    command("touch /workspace/jobs/b/test_file")
    command(get_maand_command("build"))

    command(get_maand_command("deploy --jobs=b"))
    sync()

    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/a/test_file")
        assert os.path.exists(f"/workspace/data/{agent}/jobs/b/test_file")
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/c/test_file")

    command(get_maand_command("deploy --jobs=a,b"))
    sync()

    for agent in agents_ip:
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/a/test_file")
        assert os.path.exists(f"/workspace/data/{agent}/jobs/b/test_file")
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/c/test_file")

    for agent in agents_ip:
        assert read_file_content(f"/workspace/data/{agent}/update_seq.txt") == "4"


def test_update_a_job_with_agent_role():
    clean()
    command(get_maand_command("initialize"))

    make_job("a", ["group1"])
    make_job("b", ["group2"])

    command(get_maand_command("build"))
    command(get_maand_command("deploy"))
    sync()

    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/a/manifest.json")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/b/manifest.json")

    make_job("c", ["group3"])
    command("touch /workspace/jobs/a/test_file")
    command("touch /workspace/jobs/b/test_file")
    command("touch /workspace/jobs/c/test_file")
    command(get_maand_command("build"))

    command(get_maand_command("deploy --jobs=a"))
    sync()

    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/a/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/b/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group3")
    for agent in agents_ip:
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/c/test_file")

    command("rm /workspace/jobs/a/test_file")
    command(get_maand_command("build"))
    command(get_maand_command("deploy --jobs=b"))
    sync()

    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/a/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/b/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group3")
    for agent in agents_ip:
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/c/test_file")

    command(get_maand_command("deploy --jobs=a,b"))
    sync()

    agents_ip = workspace.get_agent_ip_by_role("group1")
    for agent in agents_ip:
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/a/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group2")
    for agent in agents_ip:
        assert os.path.exists(f"/workspace/data/{agent}/jobs/b/test_file")

    agents_ip = workspace.get_agent_ip_by_role("group3")
    for agent in agents_ip:
        assert not os.path.exists(f"/workspace/data/{agent}/jobs/c/test_file")

    agents_ip = workspace.get_agents_ip()
    for agent in agents_ip:
        assert read_file_content(f"/workspace/data/{agent}/update_seq.txt") == "4"