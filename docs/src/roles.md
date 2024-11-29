---
title: Roles
---

# Roles and Variables

Maand smartly generates environment variables for each agent based on roles and attributes. 

---

These variables generated to simplify service discovery, role-based configuration, and agent-specific customizations.

Example agents.json file

```json
[
 {
   "host": "10.27.221.181",
   "roles": ["prometheus"]
 },
 {
   "host": "10.27.221.144"
 },
 {
   "host": "10.27.221.170"
 }
]
```

based on example agents.json file, following variables are generated

## Variables
- **`AGENT_0`, `AGENT_1`, `AGENT_2`**: IP addresses of all agents in the agent role.
- **`AGENT_ALLOCATION_INDEX`**: The index of the current agent in the `agent` role.
- **`AGENT_IP`**: The IP address of the current agent.
- **`AGENT_LENGTH`**: Total number of agents in the `agent` role.
- **`AGENT_NODES`**: Comma-separated list of all agent IPs in the `agent` role.
- **`AGENT_PEERS`**: Comma-separated list of all other `agent` IPs (excluding the current agent) in the `agent` role.
- **`AGENT_ROLE_ID`**: Unique identifier for the `agent` role.
- **`ROLES`**: Comma-separated list of roles assigned to the agent.
- **`PROMETHEUS_0`**: IP address of the first agent with the `prometheus` role.
- **`PROMETHEUS_ALLOCATION_INDEX`**: The index of the current agent in the `prometheus` role.
- **`PROMETHEUS_LENGTH`**: Total number of agents with the `prometheus` role.
- **`PROMETHEUS_NODES`**: Comma-separated list of all agent IPs in the `prometheus` role.
- **`PROMETHEUS_ROLE_ID`**: Unique identifier for the `prometheus` role.

---

### **Examples**

#### Agent `10.27.221.181`:
This agent has the roles `agent` and `prometheus`:
```plaintext
AGENT_0=10.27.221.181
AGENT_ALLOCATION_INDEX=0
AGENT_IP=10.27.221.181
AGENT_NODES=10.27.221.181,10.27.221.144,10.27.221.170
PROMETHEUS_0=10.27.221.181
PROMETHEUS_ALLOCATION_INDEX=0
PROMETHEUS_NODES=10.27.221.181
ROLES=agent,prometheus
```

#### Agent `10.27.221.144`:
This agent has only the `agent` role:
```plaintext
AGENT_1=10.27.221.144
AGENT_ALLOCATION_INDEX=1
AGENT_IP=10.27.221.144
AGENT_NODES=10.27.221.181,10.27.221.144,10.27.221.170
PROMETHEUS_NODES=10.27.221.181
ROLES=agent
```

#### Agent `10.27.221.170`:
This agent has only the `agent` role:
```plaintext
AGENT_2=10.27.221.170
AGENT_ALLOCATION_INDEX=2
AGENT_IP=10.27.221.170
AGENT_NODES=10.27.221.181,10.27.221.144,10.27.221.170
PROMETHEUS_NODES=10.27.221.181
ROLES=agent
```

---

### **Usage in Jobs**

These variables allow dynamic behavior in jobs:
- **Static Discovery**: Use `AGENT_NODES` or `AGENT_PEERS` for distributed applications.
- **Role-Specific Logic**: Use `PROMETHEUS_NODES` for tasks targeting `prometheus` agents.
- **Agent Customization**: Tailor configurations based on `AGENT_ALLOCATION_INDEX` or `AGENT_IP`.

This approach ensures scalability and simplifies multi-agent orchestration!