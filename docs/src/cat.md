---
title: Maand Build
---

# cat

cat command helps to view information

## View Bucket

To check the details of your current bucket:

```bash
$ maand cat info
```

#### Example Output:

```plaintext
bucket                                update_seq
------------------------------------  ----------
db3c0da7-6709-4d8c-94a0-5f66b0e32249  0
```

- **bucket**: Unique GUID assigned to the bucket.
- **update_seq**: Tracks the number of updates made to the bucket. It increments with each successful build.


## List Agents

To view all agents, their roles, and statuses, use:

```shell
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

- **agent_id**: Unique identifier for each agent.
- **agent_ip**: IP address of the agent.
- **detained**: Indicates whether the agent status (0 for active, 1 for detained).
- **roles**: Roles assigned to the agent.