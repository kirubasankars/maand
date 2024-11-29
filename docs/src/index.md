# Maand

Maand is a lightweight, **agentless orchestration framework** for managing tasks across Linux machines. It uses **SSH** for communication, requiring no additional software on agents, ensuring simple and efficient task execution.

---

### **Inspiration**  
Named after the Indian classical *raaga Maand*, it embodies structured flow and harmony, facilitating seamless orchestration across systems.

---

### **Key Concepts**

- **Agent**: A Linux machine identified by its **IP address** and **roles**, defined in `agents.json`. Maand communicates via SSH.  
- **Job**: A directory with a `manifest.json` (configuration) and `Makefile` (actions like `start`, `stop`). Supports binaries, Docker, and systemd tasks.  
- **Role**: Labels linking jobs and agents, enabling dynamic task assignment and static service discovery.  
- **Bucket**: Logical grouping of related jobs for better organization.

---

### **Highlights**  
- **Agentless**: No installations on target machines; uses SSH.  
- **Versatile**: Handles binaries, Docker, and systemd services.  
- **Static Service Discovery**: Maps roles to IPs for dynamic yet consistent configurations.  
- **Simple Setup**: Lightweight, easy to configure, and highly flexible.  