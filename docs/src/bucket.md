---
title: Bucket
---

# Bucket

Logical group of related jobs for better organization and control.

---

## Generated Folder Structure

Initialization creates the following structure:

```plaintext
$ tree
.
|-- data
|   |-- agents.db
|   |-- jobs.db
|   |-- kv.db
|   `-- maand.db
|-- logs
|-- maand.conf
|-- secrets
|   |-- ca.crt
|   `-- ca.key
`-- workspace
    |-- agents.json
    |-- command.sh
    |-- secrets.env
    `-- variables.env

5 directories, 11 files
```

---

#### **Generated Files and Directories**

- **`secrets/ca.key`** & **`ca.crt`**: CA private key and public certificate for issue certs for agents and jobs.
- **`logs/*.log`**: Logs for operations.
- **`data/*.db`**: SQLite databases stores metadata.
  - `kv.db`: Configuration key-value pairs.
- **`workspace/`**:
  - `variables.env`: Environment variables for agents and jobs.
  - `secrets.env`: Sensitive data like passwords and API keys.
  - `agents.json`: Agent and role configurations.
  - `command.sh`: Placeholder for scripts.

---