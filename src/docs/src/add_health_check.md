---
title: Health Check
---
# Health check

Maand allow jobs to define specialized command using Python scripts stored in the `_modules` folder. 

---

## Setup

This example demonstrates how to implement a **health check** for the `node_exporter` job, ensuring the service runs correctly across all agents.

---

### **Create the `_modules` Folder**

1. Navigate to the `node_exporter` job directory:
   ```bash
   $ cd workspace/jobs/node_exporter
   ```

2. Create the `_modules` folder:
   ```bash
   $ mkdir _modules
   ```

---

### **Define the Health Check Command**

1. Create the `command_health_check.py` file:
   ```bash
   $ cat > _modules/command_health_check.py
   ```

2. Add the following Python code:
   ```python
   import requests
   import os

   def execute():
       nodes = os.getenv("AGENT_NODES")
       nodes = nodes.split(",")
       for node in nodes:
           r = requests.get(f"http://{node}:9100/metrics")
           r.raise_for_status()
   ```

   **What It Does**:
   - Retrieves the list of agent IPs from the `AGENT_NODES` environment variable.
   - Sends HTTP requests to each agent on port 9100 to verify node_exporter is running. 
   - Raises an exception if a node's health check fails.

## Run

```bash
$ maand health_check
```

Example output

```plaintext
health check successed : node_exporter
```