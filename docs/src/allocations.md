---
title: Job Allocations
---

## Job Allocations

In Maand, when a job is assigned to an agent, it is referred to as an **allocation**. Allocations are determined based on the matching roles between jobs and agents.

---

## Viewing Job Allocations

To see the current job allocations, use the command:

```bash
$ maand cat allocations
```

This displays which jobs are assigned to which agents, along with their statuses.

---

### Example Output

```plaintext
agent_ip       job            disabled  removed
-------------  -------------  --------  -------
10.27.221.181  cassandra      0         0      
10.27.221.144  cassandra      0         0      
10.27.221.170  cassandra      0         0      
10.27.221.181  node_exporter  0         0      
10.27.221.144  node_exporter  0         0      
10.27.221.170  node_exporter  0         0      
10.27.221.181  opensearch     0         0      
10.27.221.144  opensearch     0         0      
10.27.221.170  opensearch     0         0      
10.27.221.181  prometheus     0         0  
```

---

### **Explanation of Columns**

- **`agent_ip`**: The IP address of the agent to which the job is allocated.  
- **`job`**: The name of the allocated job.  
- **`disabled`**: A value of `0` indicates that the job is enabled.  
- **`removed`**: A value of `0` indicates that the job was allocated to that agent and later removed.  

---

### **How Allocations Work**

1. **Build Configuration**:
   - Allocations are prepared during the `maand build` process.

2. **Update Agents**:
   - Allocations are applied to agents during the `maand update` process.

By inspecting the allocations table, you can confirm which jobs are running/ will be on which agents.