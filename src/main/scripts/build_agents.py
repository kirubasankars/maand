import uuid
import utils
import workspace
import kv_manager

logger = utils.get_logger()


def build_agent_tags(cursor, agent_id, agent_ip, agent):
    namespace = f"tags/{agent_ip}"
    cursor.execute("DELETE FROM agent_tags WHERE agent_id = ?", (agent_id,))
    tags = agent.get("tags", {})
    for key, value in tags.items():
        key = key.upper()
        value = str(value)
        cursor.execute("INSERT INTO agent_tags (agent_id, key, value) VALUES (?, ?, ?)", (agent_id, key, value,))
        kv_manager.put(cursor, namespace, key, value)

    available_tags_keys = [x.upper() for x in tags.keys()]
    all_keys = kv_manager.get_keys(cursor, namespace)
    missing_tags = set(available_tags_keys) ^ set(all_keys)
    for key in missing_tags:
        kv_manager.delete(cursor, namespace, key)


def build_agents(cursor):
    agents = workspace.get_agents()
    for index, agent in enumerate(agents):
        agent_ip = agent.get("host")

        available_memory = float(utils.extract_size_in_mb(agent.get("memory", "0 MB")))
        available_cpu = float(utils.extract_cpu_frequency_in_mhz(agent.get("cpu", "0 MHZ")))

        cursor.execute("SELECT agent_id FROM agent WHERE agent_ip = ?", (agent_ip,))
        row = cursor.fetchone()

        if row:
            agent_id = row[0]
        else:
            agent_id = str(uuid.uuid4())

        if row:
            cursor.execute("UPDATE agent SET available_memory_mb = ?, available_cpu = ?, position = ?, detained = 0 WHERE agent_id = ?", (available_memory, available_cpu, index, agent_id, ))
        else:
            cursor.execute("INSERT INTO agent (agent_id, agent_ip, available_memory_mb, available_cpu, detained, position) VALUES (?, ?, ?, ?, 0, ?)", (agent_id, agent_ip, available_memory, available_cpu, index,))

        cursor.execute("DELETE FROM agent_roles WHERE agent_id = ?", (agent_id,))
        roles = agent.get("roles", [])
        roles.append("agent")
        roles = list(set(roles))
        for role in roles:
            cursor.execute("INSERT INTO agent_roles (agent_id, role) VALUES (?, ?)", (agent_id, role,))

        build_agent_tags(cursor, agent_id, agent_ip, agent)

    cursor.execute("SELECT agent_ip FROM agent")
    rows = cursor.fetchall()

    host_ips = [agent["host"] for agent in agents]
    agent_ips = [row[0] for row in rows]
    missing_agents = list(set(agent_ips) - set(host_ips))

    for agent_ip in missing_agents:
        cursor.execute("UPDATE agent SET detained = 1 WHERE agent_ip = ?", (agent_ip,))

    cursor.execute("SELECT agent_ip FROM agent WHERE detained = 1")
    rows = cursor.fetchall()
    agents_ip = {row[0] for row in rows}

    for agent_ip in agents_ip:
        for namespace in [ f"certs/{agent_ip}", f"vars/{agent_ip}", f"tags/{agent_ip}"]:
            keys = kv_manager.get_keys(cursor, namespace)
            for key in keys:
                kv_manager.delete(cursor, namespace, key)


def build(cursor):
    build_agents(cursor)
