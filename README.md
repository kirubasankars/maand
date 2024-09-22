
**Maand** is a static job orchestration framework that efficiently manages and executes tasks across multiple agents. It coordinates job execution on virtual machines (VMs) within a cluster to streamline task management.

**Inspiration**: The name "Maand" is inspired by the Indian classical music raaga "Maand," symbolizing the framework’s role in harmonizing job execution across a cluster.

### Key Concepts

- **Agent**: A Linux machine identified by its IP address and roles listed in the `agents.json` file.
- **Job**: A directory containing a `manifest.json` file and a `Makefile` with defined targets.
- **Role**: A string that links jobs to agents. Jobs are assigned to agents based on matching roles in `manifest.json` and `agents.json`, allowing for static service discovery.
- **Cluster**: A group of agents working together.

**Maand** supports various tasks by associating jobs with `make` targets, enabling the execution of binaries, Docker commands, Docker Compose tasks, and systemd jobs.

### Example `agents.json` File

```json
[
  {
    "host": "192.168.1.110",
    "roles": ["ROLE1", "ROLE2"]
  },
  {
    "host": "192.168.1.119",
    "roles": ["ROLE1"]
  },
  {
    "host": "192.168.1.134",
    "roles": ["ROLE1"]
  }
]
```

### Prerequisites

Ensure that each agent has `make` and `rsync` installed. **Maand** also requires SSH keys for secure communication between the controller and agents.

1. **Create a Workspace Folder**: Place `agents.json` inside:

```shell
$ tree ./workspace
workspace
└── agents.json
```

2. **Add SSH Key and Secrets**: Include your SSH key and create a `secrets.env` file with the following content:

**Example `secrets.env` File**

```text
SSH_USER=root
SSH_KEY=agent-key.pem
```

**Workspace Structure**

```shell
$ tree ./workspace
workspace
└── agents.json
└── agent-key.pem
└── secrets.env
└── command.sh
```

You may also include:

- `variables.env` for generic key-value pairs
- `ports.env` for port-related configurations

### Running Commands on Agents

Create a `command.sh` file in your workspace to execute Linux commands on agents. For example, to run `uptime`:

```shell
make run_command_no_cluster_check
```

### Cluster Initialization

Initialize the cluster with:

```shell
make initialize
```

This generates:

1. **ca.key** – Certificate authority private key.
2. **ca.crt** – Certificate authority public certificate.
3. **cluster_id.txt** – Unique GUID for the cluster.
4. **update_seq.txt** – Counter that increments with each `make update` command.

**Maand** will manage and generate certificates as needed. The `cluster_id.txt` groups agents into a cluster, while `update_seq.txt` tracks updates.

### Setting Up a Job

Create a `jobs` folder in the `workspace`. Within `jobs`, add a subfolder for each job (e.g., `sample_job`) containing a `manifest.json` and `Makefile`.

**Example Job Structure**

```shell
$ tree ./workspace
workspace
└── agents.json
└── agent-key.pem
└── secrets.env
└── command.sh
└── jobs
    └── sample_job
        └── manifest.json
        └── Makefile
```

**Example `manifest.json`**

```json
{
  "roles": ["ROLE1"]
}
```

**Example `Makefile`**

```text
start:
    echo "starting job"
stop:
    echo "stopping job"
restart:
    echo "restarting job"
```

### Understanding `manifest.json`

The `manifest.json` file specifies which agents should receive a job. Jobs are assigned based on role matches in `manifest.json` and `agents.json`, ensuring proper job distribution.

### Running Updates

To copy or update job files in the agents’ `/opt/agent/` directory:

```shell
make update
```

This command deploys changes to all agents.

### Agent Directory Structure

On each agent, the `/opt/agent` directory will include:

```shell
$ tree /opt/agent
/opt/agent
├── cluster_id.txt
├── agent_id.txt
├── update_seq.txt
├── context.env
├── roles.txt
├── bin
│   ├── start_jobs.sh
│   ├── stop_jobs.sh
│   └── restart_jobs.sh
├── certs
│   ├── agent.key
│   └── agent.crt
└── jobs
    └── sample_job
        ├── manifest.json
        └── Makefile
```

- **`cluster_id.txt`**: Unique identifier for the cluster.
- **`agent_id.txt`**: Unique identifier for the agent.
- **`update_seq.txt`**: Tracks the update count and increments with each update command.
- **`roles.txt`**: Lists roles assigned to the agent.
- **`certs`**: Contains the agent’s private and public certificates (`agent.key` and `agent.crt`).
- **`jobs`**: Directory for job files, with each job having its own folder containing `manifest.json` and `Makefile`.
- **`context.env`**: Environment variables set by **Maand**.

The update command also renews agent and job certificates if they expire within 15 days or if configurations change.

### Variable Substitution

**Maand** supports dynamic variable substitution in job files. For example, with the following `agents.json`:

```json
[
  {
    "host": "192.168.1.110",
    "roles": ["OPENSEARCH", "LEADER"]
  },
  {
    "host": "192.168.1.119",
    "roles": ["OPENSEARCH"]
  },
  {
    "host": "192.168.1.134",
    "roles": ["OPENSEARCH"]
  }
]
```

**Maand** generates variables based on roles and attributes, which are used in job files with extensions such as `*.json`, `*.service`, `*.conf`, `*.yml`, `*.env`, and `*.token`.

**Example Variable Usage**

**`config.env`**

```shell
LEADER=$LEADER_0
LEADER_COUNT=$LEADER_LENGTH
OPENSEARCH1=$OPENSEARCH_1
```

**On the Agent**

```shell
$ cat /opt/agent/jobs/sample_job/config.env
LEADER=0
LEADER_COUNT=1
OPENSEARCH1=192.168.1.119
```

```text
CLUSTER_ID=xxxxx-xxx-xxx-xxxx  # GUID
AGENT_ID=xxxxx-xxx-xxx-xxxx    # GUID
AGENT_IP=192.168.1.110
OPENSEARCH_ALLOCATION_INDEX=0
OPENSEARCH_1=192.168.1.110
OPENSEARCH_2=192.168.1.119
OPENSEARCH_3=192.168.1.134
OPENSEARCH_OTHERS=192.168.1.119,192.168.1.134
OPENSEARCH_NODES=192.168.1.110,192.168.1.119,192.168.1.134
OPENSEARCH_LENGTH=3
LEADER_ALLOCATION_INDEX=0
LEADER_1=192.168.1.110
LEADER_LENGTH=1
ROLES=opensearch,leader
## values from variables.env, secrets.env, and ports.env
```

**For `192.168.1.119`**

```text
CLUSTER_ID=xxxxx-xxx-xxx-xxxx  # GUID
AGENT_ID=xxxxx-xxx-xxx-xxxx    # GUID
AGENT_IP=192.168.1.119
OPENSEARCH_ALLOCATION_INDEX=1
OPENSEARCH_1=192.168.1.110
OPENSEARCH_2=192.168.1.119
OPENSEARCH_3=192.168.1.134
OPENSEARCH_OTHERS=192.168.1.110,192.168.1.134
OPENSEARCH_NODES=192.168.1.110,192.168.1.119,192.168.1.134
OPENSEARCH_LENGTH=3
LEADER_1=192.168.1.110
LEADER_LENGTH=1
ROLES=opensearch
## values from variables.env, secrets.env, and ports.env
```

**Note**: Variables are also available in `/opt/agent/context.env`, but `secrets.env` is not included.

These dynamically generated variables enable **Maand** to handle complex orchestration scenarios effectively, using roles and attributes defined in `agents.json`.

### Executing Commands

The `command.sh` script in the workspace can be used for ad-hoc command execution. 

- Running `make run_command` executes `command.sh` on each agent after verifying cluster membership using `cluster_id.txt` between the agent and workspace.
- Running `make run_command_no_cluster_check` executes `command.sh` on each agent without cluster validation.
- Running `make run_command_local` executes `command.sh` locally on

 the **Maand** controller while validating cluster membership under agent context.
- Running `make run_command_health_check` executes `command.sh` on each agent, performing health checks before execution.

### Job Control

- Running `make start_jobs` executes `/opt/agent/bin/start_jobs.sh`, which runs the `start` target from the `Makefile` of each job on the agent.
- Running `make stop_jobs` executes `/opt/agent/bin/stop_jobs.sh`, which runs the `stop` target from the `Makefile` of each job on the agent.
- Running `make restart_jobs` executes `/opt/agent/bin/restart_jobs.sh`, which runs the `restart` target from the `Makefile` of each job on the agent.
- Running `make rolling_restart_jobs` executes `/opt/agent/bin/restart_jobs.sh`, which runs the `restart` target from the `Makefile` of each job on the agent and runs health checks before and after per each agent.

### Health Check

Each job folder can include a `modules` directory and a `run.sh` file. The `run.sh` file is executed with the agent context on the Maand controller node and should include health checks for the job. These health checks are also used for safe rolling restarts.

To perform a health check, use the following command:

```shell
make health_check
```


