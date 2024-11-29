---
title: Execute Command
---

# Running Commands

Maand enables executing Linux commands across all agents seamlessly.

---

## **Commands**

Commands are added to the `command.sh` file in the `workspace` folder.

#### Example Folder Structure
```plaintext
.
....
|-- maand.conf
|-- secrets
|   |-- ca.crt
|   `-- ca.key
`-- workspace
    |-- agents.json
    |-- command.sh   <====
    |-- secrets.env
    `-- variables.env
```

---

### **Define Commands**

1. Open the `workspace/command.sh` file.
2. Add the desired command(s).

#### Example: Disk Usage Check
```bash
$ cat workspace/command.sh
df -h
```

---

### **Execute Commands**

Run the script across all agents:
```bash
$ maand run_command --no-check
```

---

### **Sample Output**

Results are displayed per agent:
```plaintext
[10.27.221.144] Filesystem                      Size  Used Avail Use% Mounted on
[10.27.221.144] /dev/mapper/fedora_agent2-root   15G  9.9G  5.1G  66% /
[10.27.221.170] Filesystem                      Size  Used Avail Use% Mounted on
[10.27.221.170] /dev/mapper/fedora_agent3-root   15G  9.8G  5.2G  66% /
[10.27.221.181] Filesystem                      Size  Used Avail Use% Mounted on
[10.27.221.181] /dev/mapper/fedora_fedora-root   15G   11G  4.5G  71% /
```

---

## **Logs**

Command results are saved in the `logs` directory for each agent.

#### Example:
```plaintext
$ tree logs
logs
├── 10.27.221.144.log
├── 10.27.221.170.log
└── 10.27.221.181.log
```

#### Log Content:
```plaintext
Filesystem                      Size  Used Avail Use% Mounted on
/dev/mapper/fedora_agent2-root   15G  9.9G  5.1G  66% /
devtmpfs                        4.0M     0  4.0M   0% /dev
tmpfs                           7.8G     0  7.8G   0% /dev/shm
```