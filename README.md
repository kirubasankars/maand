### Maand

**Inspiration:** Named after an Indian classical music raaga, "Maand" symbolizes the framework's role in orchestrating and harmonizing job management across a cluster of agents.

**Objective:** Maand is a static job orchestration framework designed to efficiently manage and execute tasks across various agents listed in the `agents.json` file. It coordinates job execution on virtual machines (VMs) within a cluster, ensuring seamless and effective job management.

**Key Components:**

1. **Agent Configuration (`agents.json`):**
   - The `agents.json` file, located in the workspace folder, lists agents with their IP addresses and roles.
   - Example structure:
     ```json
     [
       {
         "host": "192.168.1.110",
         "roles": ["opensearch"]
       },
       {
         "host": "192.168.1.119",
         "roles": ["opensearch"]
       },
       {
         "host": "192.168.1.134",
         "roles": ["opensearch"]
       }
     ]
     ```
   - Each entry represents an agent that Maand will manage for job orchestration. 

2. **SSH Configuration:**
   - The SSH key required for accessing agents is stored in the workspace folder.
   - `secrets.env` file contains:
     - `SSH_USER`: Username for accessing the Linux machines.
     - `SSH_KEY`: Name of the SSH key file.

3. **Cluster Initialization:**
   - Running `make initialize` sets up the cluster by generating:
     - `ca.key`: The cluster's private key.
     - `ca.crt`: The cluster's public certificate.
     - `cluster_id.txt`: Used to verify that all agents are part of the same cluster.

4. **Agent Configuration:**
   - Running `make update` configures each agent by:
     - Creating a directory at `/opt/agent/`.
     - Setting up:
       - `cluster_id.txt`: Confirms cluster membership.
       - `agent_id.txt`: Contains a unique ID for each agent.
       - `certs` folder: Stores `agent.key` (private key) and `agent.crt` (certificate) for secure communication.
       - `bin` folder: Manages and executes jobs on the agent.
       - `context.env`: environment variables combines (agent context, variable.env, secrets.env)
       - `roles.txt`: all roles assigned to that agent.
     - Every agent has default roles called `agent`.
       
5. **Job Management (`jobs` folder):**
   - The `jobs` folder in the workspace contains subfolders for each job.
   - Each job folder must include:
     - `manifest.json`: Defines the `roles` attribute (an array of strings) indicating which roles the job targets.
     - `Makefile`: Contains instructions for job execution, including targets like `build`, `deploy_job`, `restart_job`, and `stop_job`.
   - Maand matches the roles in `manifest.json` with those of agents in `agents.json`, using `rsync` to sync job files to the appropriate agents. It also leverages variables from `agents.json`, `variables.env`, and `secrets.env` during transfers. Additionally, `manifest.json` can specify certification needs, with Maand handling certificate provisioning and renewal.

6. **Rolling Upgrades:**
   - Maand supports rolling upgrades. Each job can include a `commands` folder with a `run.sh` file. Maand executes this script before and after applying changes to an agent to ensure a smooth upgrade process. Maand waits utils successful error before moving on to next agent.

7. **Executing Adhoc Commands (`command.sh`):**
   - A `command.sh` script in the workspace contains shell commands or scripts for adhoc execution.
   - Running `make run_command` executes `command.sh` on each agent after verifying that all agents belong to the same cluster.
   - Running `make run_command_no_check` executes `command.sh` on each agent without cluster validation.
   - Running `make run_command_local` executes `command.sh` locally on each agent after performing cluster validation.
   - Maand executes run_commands under agent context. 

8. **File Integrity and Certificates:**
   - Maand uses `rsync` to ensure file integrity and manage files on agents. It also renews certificates if they are set to expire within 15 days.

**Summary:**

Maand is a versatile job orchestration framework that efficiently manages job execution across a cluster of agents. It ensures that agents are correctly configured and validated within the cluster, while facilitating secure and flexible job management. With support for various job types, rolling upgrades, and adhoc command execution, Maand optimizes job orchestration and enhances overall system efficiency and security.
