---
title: Maand Update
---

# Update

The `maand update` command apply changes to the remote agents by synchronizing files.

---

## Update Command

To propagate changes to all agents, use:

```shell
$ maand update
```

This command uses `rsync` to copy the necessary files to each agent.

---

## Verify

1. SSH into an agent and confirm the job files are deployed:
   ```bash
   $ ssh -i secrets/agent.key agent@10.27.221.181 'tree /opt/agent'
   ```

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