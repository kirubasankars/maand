import json

import maand
import kv_manager
from utils import *

import workspace


def get_agents():
    with maand.get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT agent_id, agent_ip, agent_memory_mb, agent_cpu, detained, position FROM agent WHERE detained = 0 ORDER BY position")
        return cursor.fetchall()


def test_build_agent_position():
    clean_bucket()
    command(get_maand_command("init"))

    agents = [{"host":"192.0.0.1", "position": 0}, {"host":"192.0.0.2", "position": 1}, {"host":"192.0.0.3", "position": 2}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    rows = get_agents()
    assert len(rows) == 3

    output_agent = []
    for (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position,) in rows:
        output_agent.append({"host": agent_ip, "position": position})

    assert output_agent == agents

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_ALLOCATION_INDEX") == "0"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_PEERS") == "192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LABEL_ID") is not None

        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_ALLOCATION_INDEX") == "1"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_PEERS") == "192.0.0.1,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_LABEL_ID") is not None

        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_ALLOCATION_INDEX") == "2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_PEERS") == "192.0.0.1,192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_LABEL_ID") is not None


def test_build_agent_position_swap():
    clean_bucket()

    agents = [{"host":"192.0.0.1", "position": 0}, {"host":"192.0.0.2", "position": 1}, {"host":"192.0.0.3", "position": 2}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("init"))

    agents = [{"host":"192.0.0.1", "position": 0}, {"host":"192.0.0.3", "position": 1}, {"host":"192.0.0.2", "position": 2}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    rows = get_agents()
    output_agent = []
    for (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position,) in rows:
        output_agent.append({"host": agent_ip, "position": position})

    assert output_agent == agents

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_1") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_2") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_NODES") == "192.0.0.1,192.0.0.3,192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_ALLOCATION_INDEX") == "0"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_PEERS") == "192.0.0.3,192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LABEL_ID") is not None

        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_1") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_2") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_NODES") == "192.0.0.1,192.0.0.3,192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_ALLOCATION_INDEX") == "2"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_PEERS") == "192.0.0.1,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_LABEL_ID") is not None

        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_1") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_2") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_NODES") == "192.0.0.1,192.0.0.3,192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_ALLOCATION_INDEX") == "1"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_PEERS") == "192.0.0.1,192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_LABEL_ID") is not None


def test_build_agent_update_labels():
    clean_bucket()

    agents = [{"host":"192.0.0.1", "position": 0}, {"host":"192.0.0.2", "position": 1}, {"host":"192.0.0.3", "position": 2}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("init"))

    with maand.get_db() as db:
        cursor = db.cursor()
        agent_label_id = kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LABEL_ID")

    agents = [{"host":"192.0.0.1"}, {"host":"192.0.0.2", "labels": ["test"]}, {"host":"192.0.0.3", "labels": ["test"]}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_ALLOCATION_INDEX") == "0"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_PEERS") == "192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LABEL_ID") == agent_label_id

        assert kv_manager.get(cursor, "vars/192.0.0.1", "TEST_0") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "TEST_1") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "TEST_NODES") == "192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "TEST_PEERS") is None
        assert kv_manager.get(cursor, "vars/192.0.0.1", "TEST_ALLOCATION_INDEX") is None
        assert kv_manager.get(cursor, "vars/192.0.0.1", "TEST_LENGTH") == "2"

        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_ALLOCATION_INDEX") == "1"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_PEERS") == "192.0.0.1,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "LABELS") == "agent,test"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_LABEL_ID") == agent_label_id

        assert kv_manager.get(cursor, "vars/192.0.0.2", "TEST_0") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "TEST_1") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "TEST_NODES") == "192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "TEST_PEERS") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "TEST_ALLOCATION_INDEX") == "0"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "TEST_LENGTH") == "2"

        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_ALLOCATION_INDEX") == "2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_PEERS") == "192.0.0.1,192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "LABELS") == "agent,test"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_LABEL_ID") == agent_label_id

        assert kv_manager.get(cursor, "vars/192.0.0.3", "TEST_0") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "TEST_1") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "TEST_NODES") == "192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "TEST_PEERS") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "TEST_ALLOCATION_INDEX") == "1"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "TEST_LENGTH") == "2"


def test_build_agent_detailed():
    clean_bucket()
    command(get_maand_command("init"))

    agents = [{"host":"192.0.0.1", "position": 0}, {"host":"192.0.0.2", "position": 1}, {"host":"192.0.0.3", "position": 2}, {"host":"192.0.0.4", "position": 3}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    rows = get_agents()
    assert len(rows) == 4

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LENGTH") == "4"

    output_agent = []
    for (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position,) in rows:
        output_agent.append({"host": agent_ip, "position": position})

    assert output_agent == agents

    agents.pop()
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    rows = get_agents()
    assert len(rows) == 3

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_ALLOCATION_INDEX") == "0"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_PEERS") == "192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_LABEL_ID") is not None

        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_ALLOCATION_INDEX") == "1"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_PEERS") == "192.0.0.1,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.2", "AGENT_LABEL_ID") is not None

        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_0") == "192.0.0.1"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_1") == "192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_2") == "192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_NODES") == "192.0.0.1,192.0.0.2,192.0.0.3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_ALLOCATION_INDEX") == "2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_PEERS") == "192.0.0.1,192.0.0.2"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_LENGTH") == "3"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "LABELS") == "agent"
        assert kv_manager.get(cursor, "vars/192.0.0.3", "AGENT_LABEL_ID") is not None


def test_build_remove_update_agent_id_remain_same():
    clean_bucket()

    agents = [{"host":"192.0.0.1", "position": 0}, {"host":"192.0.0.2", "position": 1}, {"host":"192.0.0.3", "position": 2}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("init"))

    rows = get_agents()
    output_agent = []
    for (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position,) in rows:
        output_agent.append(agent_id)

    agents = [{"host":"192.0.0.1", "position": 0}, {"host":"192.0.0.3", "position": 1}, {"host":"192.0.0.2", "position": 2}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    rows = get_agents()
    for (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position,) in rows:
        output_agent.append(agent_id)

    output_agent = set(output_agent)
    assert len(output_agent) == 3


def test_build_remove_gc_agent_agent_id_diff():
    clean_bucket()

    agents = [{"host":"192.0.0.1"}, {"host":"192.0.0.2"}, {"host":"192.0.0.3"}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))
    command(get_maand_command("init"))

    rows = get_agents()
    output_agent = []
    for (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position,) in rows:
        output_agent.append(agent_id)

    agents = [{"host":"192.0.0.1"}, {"host":"192.0.0.2"}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))
    command(get_maand_command("build"))
    command(get_maand_command("gc"))

    agents = [{"host":"192.0.0.1"}, {"host":"192.0.0.3"}, {"host":"192.0.0.2"}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))
    command(get_maand_command("build"))

    rows = get_agents()
    for (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position,) in rows:
        output_agent.append(agent_id)

    output_agent = set(output_agent)
    assert len(output_agent) == 4


def test_build_update_resources():
    clean_bucket()

    agents = [{"host":"192.0.0.1", "memory": "1024"}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))
    command(get_maand_command("init"))

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_MEMORY") == "1024.0"

    agents = [{"host":"192.0.0.1", "cpu": "100", "memory": "1024"}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))
    command(get_maand_command("build"))

    rows = get_agents()
    for (agent_id, agent_ip, agent_memory_mb, agent_cpu, detained, position,) in rows:
        assert agent_memory_mb == "1024.0"
        assert agent_cpu == "100.0"

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_MEMORY") == "1024.0"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_CPU") == "100.0"

    agents = [{"host":"192.0.0.1", "cpu": "200", "memory": "2024"}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))
    command(get_maand_command("build"))

    rows = get_agents()
    for (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position,) in rows:
        assert available_memory_mb == "2024.0"
        assert available_cpu == "200.0"

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_MEMORY") == "2024.0"
        assert kv_manager.get(cursor, "vars/192.0.0.1", "AGENT_CPU") == "200.0"


def test_build_label_id_same():
    clean_bucket()

    agents = [{"host":"192.0.0.1", "labels": ["a"]}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("init"))

    a_label_id1 = None
    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "a,agent"
        a_label_id1 = kv_manager.get(cursor, "vars/192.0.0.1", "A_LABEL_ID")

    command(get_maand_command("build"))

    agents = [{"host":"192.0.0.1", "labels": []}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))
    command(get_maand_command("gc"))

    agents = [{"host":"192.0.0.1", "labels": ["a"]}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    a_label_id2 = None
    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "a,agent"
        a_label_id2 = kv_manager.get(cursor, "vars/192.0.0.1", "A_LABEL_ID")

    assert a_label_id1 == a_label_id2


def test_build_role_removed():
    clean_bucket()

    agents = [{"host":"192.0.0.1", "labels": ["a", "b"]}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("init"))

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "a,agent,b"

    agents = [{"host":"192.0.0.1", "labels": ["a"]}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "a,agent"

    agents = [{"host":"192.0.0.1", "labels": []}]
    with open("/bucket/workspace/agents.json", "w") as f:
        f.write(json.dumps(agents))

    command(get_maand_command("build"))

    with maand.get_db() as db:
        cursor = db.cursor()
        assert kv_manager.get(cursor, "vars/192.0.0.1", "LABELS") == "agent"
