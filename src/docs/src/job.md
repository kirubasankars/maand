---
title: Job
---

# Job

A **Job** in Maand is a deployable folder containing configuration and execution logic. Jobs are dynamically assigned to agents based on matching roles.

---

## **Job Structure**

A job folder must include:
1. **`manifest.json`**  
   - Defines the roles the job applies to.
2. **`Makefile`**  
   - Includes targets (`start`, `stop`, `restart`) that define the job's lifecycle operations.

---

## **Job Role Matching**

- **Role Assignment**: When the roles in `manifest.json` match the roles assigned to an agent, Maand allocates the job folder to that agent.  
- **Dynamic Variable Replacement**: Variables assigned to agents (based on roles) are stored in a key-value (KV) database when `maand build` is called. These variables are replaced with actual values during `maand update`.

---

## **Makefile Targets**

Maand expects the following targets in the job's `Makefile`:
1. **`start`**  
   Defines the logic to initialize or run the job.
2. **`stop`**  
   Handles stopping or cleaning up the job.
3. **`restart`**  
   Combines the `stop` and `start` targets for job restarts.

#### **Important Note**:
- These targets **must not** be long-running tasks. They should execute quickly and complete within a reasonable timeframe.

---

## **Workflow**

1. **Build Configuration**:
   ```bash
   $ maand build
   ```
   - Generates variables for agents based on roles and updates the KV database.

2. **Deploy Job**:
   ```bash
   $ maand update
   ```
   - Allocates the job folder to matching agents and replaces variables in the configuration with actual values.

