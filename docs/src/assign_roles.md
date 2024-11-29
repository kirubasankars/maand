---
title: Agent Roles
---

# Roles

**Roles** works as node selector and static service discovery in maand.

---

Roles are defined in the `agents.json` file and matched to jobs for allocations.

## **Viewing Roles**

List all agents and their roles:
```bash
$ maand cat agents
```

#### Example Output:
```plaintext
agent_id                              agent_ip       detained  roles                                
------------------------------------  -------------  --------  -------------------------------------
1117262b-c412-4c28-8724-e22a3c194947  10.27.221.181  0         agent
25d833a2-a7da-450f-81a6-11ecd1ef4632  10.27.221.144  0         agent           
94dfe46b-2326-46d5-8956-971a774af8d2  10.27.221.170  0         agent   
```

---

### **Default Role**
- All agents are assigned the `agent` role by default.
- Additional roles can be added to customize their responsibilities.

---

## **Assigning Roles**

**Edit `agents.json`**  
Add roles to agents under the `roles` key:
```json
[
 {
   "host": "10.27.221.181",
   "roles": ["prometheus"]
 },
 {
   "host": "10.27.221.144"
 },
 {
   "host": "10.27.221.170"
 }
]
```

**Build Configuration**  
Apply the changes by running:
```bash
$ maand build
```

**Verify Roles**  
Check role assignments:
```bash
$ maand cat agents
```
#### Example Output:
```plaintext
agent_id                              agent_ip       detained  roles                                
------------------------------------  -------------  --------  -------------------------------------
1117262b-c412-4c28-8724-e22a3c194947  10.27.221.181  0         agent,prometheus
25d833a2-a7da-450f-81a6-11ecd1ef4632  10.27.221.144  0         agent           
94dfe46b-2326-46d5-8956-971a774af8d2  10.27.221.170  0         agent   
```