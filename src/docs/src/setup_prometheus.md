---
title: Setup Prometheus
---

# Prometheus

This guide demonstrates creating and deploying a job to manage **prometheus** to a agent and connect **node_exporter**.

## **Create a Job**

1. Create the `jobs` folder in `workspace` and the `prometheus` folder for the job:
   ```bash
   $ mkdir -p workspace/jobs/prometheus
   ```

2. Verify the folder structure:
   ```plaintext
   .
   └── workspace
       ├── agents.json
       ├── jobs
       │   └── node_exporter
       │   │   ├── docker-compose.yaml
       │   │   ├── manifest.json
       │   │   └── Makefile
       │   └── prometheus
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
       "prometheus"
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
    prometheus:
        image: prom/prometheus
        container_name: prometheus
        user: root
        command:
        - '--config.file=/etc/prometheus/prometheus.yml'
        - '--web.config.file=/etc/prometheus/web.config.yml'
        - '--web.listen-address=0.0.0.0:8080'
        network_mode: host
        restart: unless-stopped
        volumes:
        - ./prometheus.yml:/etc/prometheus/prometheus.yml
        - ./web.config.yml:/etc/prometheus/web.config.yml
        - /opt/agent/${BUCKET}/certs:/etc/prometheus/certs
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
   a255d9cb-7286-59f1-8775-8a0544503891  prometheus     0         0               prometheus
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
   10.27.221.181  prometheus     0         0      
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
       │   │   ├── docker-compose.yml
       │   │   ├── Makefile
       │   │   └── manifest.json
       │   └── prometheus
       │       ├── docker-compose.yml
       │       ├── Makefile
       │       └── manifest.json       
   ```
