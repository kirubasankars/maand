---
title: Agent Setup
---

# Agent

An **Agent** is a Linux machine identified by its **IP address** and **role**, defined in `agents.json`.

---

Maand uses SSH for communication, requiring user permissions and specific configurations.

## **Prerequisites**

1. **User Permissions**  
   The SSH user (e.g., `agent`) must have:
   - Non-interactive command execution privileges.
   - Sudo/root access for administrative tasks.

2. **Key File**  
   Place the private SSH key (`agent.key`) in the `secrets` folder.

---

## **Configuration Steps**

1. **Place Key File**  
   Move the `agent.key` file to the `secrets` directory:
   ```plaintext
   platform-services/secrets/agent.key
   ```

2. **Update `maand.conf`**  
   Configure SSH details in `maand.conf`:
   ```ini
   [default]
   ca_ttl = 3650          # Certificate Authority validity
   use_sudo = 1           # Enable sudo for privileged tasks
   ssh_user = agent       # SSH user
   ssh_key = secrets/agent.key  # Path to private SSH key
   ```

3. **Install Tools on Agents**  
   Ensure each agent has the following installed:
   - `rsync`, `make`, `docker`, `docker-compose`, `python3`.

---

### **Defining Agents**

1. Create the `agents.json` file in `workspace/`:
   ```json
   [
     { "host": "10.27.221.181" },
     { "host": "10.27.221.144" },
     { "host": "10.27.221.170" }
   ]
   ```

---

## **Verify Setup**

1. **Build Workspace**  
   Compile the changes:
   ```bash
   $ maand build
   ```

2. **Verify Connectivity**  
   Test communication with agents:
   ```bash
   $ maand uptime
   [10.27.221.181] 14:39:54 up 1:06, load average: 0.11, 0.07, 0.01
   [10.27.221.170] 14:39:54 up 1:06, load average: 0.03, 0.08, 0.08
   [10.27.221.144] 14:39:54 up 1:06, load average: 0.12, 0.05, 0.01
   ```

---

Your setup is complete, and Maand is ready to orchestrate jobs across your agents.