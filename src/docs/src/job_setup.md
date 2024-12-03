---
title: Job Setup
---

# Job

A **Job** is a deployable task that includes configuration and execution logic.

---

This guide demonstrates creating and deploying a job to manage **node_exporter** across multiple agents.

## **Create a Job**

1. Create the `jobs` folder in `workspace` and the `node_exporter` folder for the job:
   ```bash
   $ mkdir -p workspace/jobs/node_exporter
   ```

2. Verify the folder structure:
   ```plaintext
   .
   └── workspace
       ├── agents.json
       ├── jobs
       │   └── node_exporter
       │       ├── docker-compose.yaml
       │       ├── manifest.json
       │       └── Makefile
   ```

---

## **Add Job Files**

1. **`manifest.json`**  
   Define the roles the job applies to:
   ```json
   {
     "roles": [
       "agent"
     ]
   }
   ```

2. **`Makefile`**  
   Define job commands to manage the task:
   ```Makefile
   start:
   	docker-compose up -d --remove-orphans
   	
   stop:
   	docker-compose down
   	
   restart: stop start
   ```

3. **`docker-compose.yaml`**  
   Configuration for running `node_exporter`:
   ```yaml
   services:
     node_exporter:
       image: quay.io/prometheus/node-exporter:latest
       container_name: node_exporter
       command:
         - '--path.rootfs=/host'
       network_mode: host
       pid: host
       restart: unless-stopped
       volumes:
         - '/:/host:ro,rslave'
   ```

---

## **Build**

Compile changes

```bash
$ maand build
```

---

## **View Jobs**

1. List all jobs:
   ```bash
   $ maand cat jobs
   ```
   
   Example output:
   ```plaintext
   job_id                                name           disabled  deployment_seq  roles
   ------------------------------------  -------------  --------  --------------  -----
   a255d9cb-7286-59f1-8775-8a0544503891  node_exporter  0         0               agent
   ```

2. Check job's allocations:
   ```bash
   $ maand cat allocations
   ```
   
   Example output:
   ```plaintext
   agent_ip       job            disabled  removed
   -------------  -------------  --------  -------
   10.27.221.181  node_exporter  0         0      
   10.27.221.144  node_exporter  0         0      
   10.27.221.170  node_exporter  0         0    
   ```

---

## **Deploy**

Deploy the job to the agents:
```bash
$ maand update
```

---

## **Verify**

1. SSH into an agent and confirm the job files are deployed:
   ```bash
   $ ssh -i secrets/agent.key agent@10.27.221.181 'tree /opt/agent'
   ```

2. Example output:
   ```plaintext
   /opt/agent
   └── db3c0da7-6709-4d8c-94a0-5f66b0e32249
       ├── jobs
       │   └── node_exporter
       │       ├── docker-compose.yml
       │       ├── Makefile
       │       └── manifest.json
   ```

---

### **Key Notes**

- **Roles**: Ensure the job's `manifest.json` roles match the agents' roles in `agents.json`.  
- **Update After Changes**: Always run `maand build` and `maand update` after modifying job files or configurations.  
- **File Locations**: Deployed jobs reside under `/opt/agent` on each agent.