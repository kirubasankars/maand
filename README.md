# Maand - Job Orchestrator Framework

Maand is a job orchestrator framework designed to manage and distribute jobs across multiple agents. The framework is configured to ensure seamless job assignment and execution based on predefined roles.

## Key Components

### Agent Configuration

- **Agents are defined in an `agents.json` file located in the workspace directory.**
  - Each agent entry includes a host and a list of roles.

- **Example `agents.json` configuration:**

  ```json
  [
    {
      "host": "192.168.1.110", "roles": ["opensearch"]
    },
    {
      "host": "192.168.1.119", "roles": ["opensearch"]
    },
    {
      "host": "192.168.1.134", "roles": ["opensearch"]
    }
  ]
  ```

### Job Matching

- **Jobs are stored in the `jobs` folder within the workspace.**
  - Each job has a manifest file specifying the roles required for execution.
  - Maand matches jobs to agents based on the roles specified in the manifest and the roles assigned to each agent. If an agent's roles match the required roles, the job is assigned to that agent.
  - Maand is a generic framework that supports various types of jobs, including (shell script, binary, docker or docker-compose)

### Job Distribution

- **The matched jobs are copied to the agents.**
  - Files are synchronized to the `/opt/agent` directory on each agent's VM.

### TLS Certificates Management
   Maand handles TLS certificates management for agents and jobs. The framework checks if certificates are close to expiration, missing, or if configurations have changed, and updates them accordingly.

### Health Checks and Rolling Upgrades
   - Maand provides support for health checks and rolling upgrades.
   - Health checks are performed on agents to ensure that jobs are running smoothly.
   - Rolling upgrades allow for updating jobs on agents without disrupting the overall system.

### Command Execution Targets
- **Maand includes several command execution targets:**
  - run_command: Runs any script defined in the command.sh file located in the workspace folder on the agent.
  - run_command_local: Executes the script locally with the agent context (variables).
  - run_command_no_check: Performs the same operation as run_command but without checking the cluster_id.