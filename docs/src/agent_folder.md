---
title: Agent Folder
---

# Agent Folder


#### Example Output:

```plaintext
/opt/agent
└── db3c0da7-6709-4d8c-94a0-5f66b0e32249
    ├── agent.txt
    ├── bin
    │   └── runner.py
    ├── certs
    │   ├── agent.crt
    │   ├── agent.key
    │   ├── agent.pem
    │   └── ca.crt
    ├── context.env
    ├── jobs.json
    ├── roles.txt
    └── update_seq.txt

6 directories, 10 files
```

---

### Key Files and Directories

- **agent.txt**: Contains metadata about the agent.
- **bin/runner.py**: The runner script that executes jobs.
- **certs/**: Certificates for secure communication.
  - `agent.crt`: Agent certificate.
  - `agent.key`: Agent private key.
  - `ca.crt`: Certificate authority file.
- **context.env**: Environment variables for the agent.
- **jobs.json**: Job definitions synchronized from the workspace.
- **roles.txt**: Lists the roles assigned to the agent.
- **update_seq.txt**: Tracks the last update sequence applied to the agent.