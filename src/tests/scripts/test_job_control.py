import os.path

from utils import *

import workspace


def test_start_jobs():
    clean()
    command(get_maand_command("init"))

    make_job("a", labels=["group1"])
    make_job("b", labels=["group2"])
    make_job("c", labels=["group3"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    command(get_maand_command("job --target start"))
    sync()

    command(get_maand_command("job --target start"))
    sync()

    bucket_id = workspace.get_bucket_id()

    agents = workspace.get_agent_ip_by_label("group3")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/start")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/start") == "2"

    agents = workspace.get_agent_ip_by_label("group2")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/start")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/start") == "2"

    agents = workspace.get_agent_ip_by_label("group1")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/start")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/start") == "2"


def test_start_jobs_with_filter():
    clean()
    command(get_maand_command("init"))

    make_job("a", labels=["group1"])
    make_job("b", labels=["group2"])
    make_job("c", labels=["group3"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    command(get_maand_command("job --target start"))
    sync()

    command(get_maand_command("job --target start --jobs=a,b"))
    sync()

    bucket_id = workspace.get_bucket_id()

    agents = workspace.get_agent_ip_by_label("group3")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/start")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/start") == "1"

    agents = workspace.get_agent_ip_by_label("group2")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/start")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/start") == "2"

    agents = workspace.get_agent_ip_by_label("group1")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/start")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/start") == "2"


def test_stop_jobs():
    clean()
    command(get_maand_command("init"))

    make_job("a", labels=["group1"])
    make_job("b", labels=["group2"])
    make_job("c", labels=["group3"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    command(get_maand_command("job --target stop"))
    sync()

    command(get_maand_command("job --target stop"))
    sync()

    bucket_id = workspace.get_bucket_id()

    agents = workspace.get_agent_ip_by_label("group3")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/stop")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/stop") == "2"

    agents = workspace.get_agent_ip_by_label("group2")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/stop")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/stop") == "2"

    agents = workspace.get_agent_ip_by_label("group1")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/stop")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/stop") == "2"


def test_stop_jobs_with_filter():
    clean()
    command(get_maand_command("init"))

    make_job("a", labels=["group1"])
    make_job("b", labels=["group2"])
    make_job("c", labels=["group3"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    command(get_maand_command("job --target stop"))
    sync()

    command(get_maand_command("job --target stop --jobs=a,b"))
    sync()

    bucket_id = workspace.get_bucket_id()

    agents = workspace.get_agent_ip_by_label("group3")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/stop")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/stop") == "1"

    agents = workspace.get_agent_ip_by_label("group2")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/stop")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/stop") == "2"

    agents = workspace.get_agent_ip_by_label("group1")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/stop")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/stop") == "2"


def test_restart_jobs():
    clean()
    command(get_maand_command("init"))

    make_job("a", labels=["group1"])
    make_job("b", labels=["group2"])
    make_job("c", labels=["group3"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    command(get_maand_command("job --target restart"))
    sync()

    command(get_maand_command("job --target restart"))
    sync()

    bucket_id = workspace.get_bucket_id()

    agents = workspace.get_agent_ip_by_label("group3")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/restart")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/restart") == "2"

    agents = workspace.get_agent_ip_by_label("group2")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/restart")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/restart") == "2"

    agents = workspace.get_agent_ip_by_label("group1")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/restart")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/restart") == "2"


def test_restart_jobs_with_filter():
    clean()
    command(get_maand_command("init"))

    make_job("a", labels=["group1"])
    make_job("b", labels=["group2"])
    make_job("c", labels=["group3"])

    command(get_maand_command("build"))
    command(get_maand_command("update"))
    sync()

    command(get_maand_command("job --target restart"))
    sync()

    command(get_maand_command("job --target restart --jobs=a,b"))
    sync()

    bucket_id = workspace.get_bucket_id()

    agents = workspace.get_agent_ip_by_label("group3")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/restart")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/c/restart") == "1"

    agents = workspace.get_agent_ip_by_label("group2")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/restart")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/b/restart") == "2"

    agents = workspace.get_agent_ip_by_label("group1")
    for agent_ip in agents:
        assert os.path.exists(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/restart")
        assert read_file_content(f"/bucket/tmp/{agent_ip}/{bucket_id}/jobs/a/restart") == "2"
