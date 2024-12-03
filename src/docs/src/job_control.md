---
title: Job Control (Start, Stop, and Restart)
---

# Job Control

Maand simplifies the lifecycle management of jobs across all agents using predefined `Makefile` targets (`start`, `stop`, `restart`).

---

## **Start All Jobs**

```bash
$ maand job start
```

- Runs the `start` target in the `Makefile` of each deployed job.  
- Example (`node_exporter`): Executes:
  ```bash
  docker-compose up -d --remove-orphans
  ```
  Starts the `node_exporter` service.

---

## **Stop All Jobs**
```bash
$ maand job stop
```
- Runs the `stop` target in the `Makefile` of each deployed job.  
- Example (`node_exporter`): Executes:
  ```bash
  docker-compose down
  ```
  Stops and removes the `node_exporter` container.

---

## **Restart All Jobs**
```bash
$ maand job restart
```
- Runs the `stop` target followed by the `start` target in the `Makefile` of each job.  
- Example (`node_exporter`): Executes:
  ```bash
  docker-compose down
  docker-compose up -d --remove-orphans
  ```

---

### **Key Advantages**

- **Centralized Control**: Manage all jobs from one command, without logging into individual agents.  
- **Standardized Execution**: Ensures consistent operations across jobs and agents.  
- **Scalable**: Easily handles multiple jobs and agents simultaneously.

---

By using these simple commands, you can efficiently manage job operations at scale.