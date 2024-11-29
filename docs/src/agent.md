---
title: Agent
---

# Agent

An **Agent** is a Linux machine identified by its **IP address** and assigned **roles** as specified in the `agents.json` file.

---

## Rules for Agents

1. SSH Accessibility
   - Agents must be accessible over SSH for Maand to function.

2. Required Tools 
   - Each agent must have the following installed:  
     - **`make`**: For running job Makefiles.  
     - **`rsync`**: For file synchronization.

3. Bucket  
   - An agent can belong to multiple buckets.  
   - **Buckets** are logical groupings of jobs, represented by separate directories.
   - `/opt/agent` should have all bucket's folder when a agent belongs to multiple buckets.

4. Linux Compatibility
   - Agents must run a Linux or Linux-like operating system.

5. Non-Interactive Command Execution
   - The agent's user account must support running commands in a non-interactive manner.

6. Single User and Key Access
   - Maand requires a single user and private key for SSH access to all agents.  
   - The same key is used to authenticate across all agents.

---

These rules ensure uniformity and reliability when managing agents and executing jobs in Maand.