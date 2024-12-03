---
title: Initialize Bucket
---

# Setup a bucket

1. Create and navigate to your directory:
   ```bash
   $ mkdir platform-services
   $ cd platform-services
   ```

2. Initialize the bucket:
   ```bash
   $ maand init
   ```

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

##  View Bucket Info

Retrieve bucket details:
```bash
$ maand info
```

Example Output:
```plaintext
bucket                                update_seq
------------------------------------  ----------
db3c0da7-6709-4d8c-94a0-5f66b0e32249  0
```
