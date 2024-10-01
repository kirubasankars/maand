#!/bin/bash
set -ueo pipefail
echo "StrictHostKeyChecking accept-new" >> /etc/ssh/ssh_config

mkdir -p /opt/agents
test -f /workspace/variables.env && source /workspace/variables.env
test -f /workspace/ports.env && source /workspace/ports.env
test -f /workspace/secrets.env && source /workspace/secrets.env

export OPERATION=$1
shift

if [ "$OPERATION" == "initialize" ]; then
  python3 /scripts/initialize.py
  exit $?
fi

export CLUSTER_ID=$(cat /workspace/cluster_id.txt)
export UPDATE_CERTS=${UPDATE_CERTS:-0}
export SSH_USER=${SSH_USER:-""}
export SSH_KEY=${SSH_KEY:-""}
export MAX_CONCURRENCY=${MAX_CONCURRENCY:-"4"}
export AGENT_API=${AGENT_API:-"true"}
export USE_SUDO=${USE_SUDO:-"0"}

if [[ -z "$OPERATION" || -z "$SSH_USER" || -z "$SSH_KEY" || -z "$CLUSTER_ID" ]]; then
  echo "missing arguments (OPERATION, SSH_USER, SSH_KEY, CLUSTER_ID)" >&2;
  exit 1
fi

# TODO: validate target

if [ "$OPERATION" == "run_command" ]; then
  python3 /scripts/run_command.py $@
elif [ "$OPERATION" == "run_command_local" ]; then
  python3 /scripts/run_command_local.py $@
elif [ "$OPERATION" == "run_command_with_health_check" ]; then
  python3 /scripts/run_command_with_health_check.py $@
elif [ "$OPERATION" == "update" ]; then
  python3 /scripts/update.py $@
elif [ "$OPERATION" == "start_jobs" ]; then
  python3 /scripts/start_jobs.py $@
elif [ "$OPERATION" == "stop_jobs" ]; then
  python3 /scripts/stop_jobs.py $@
elif [ "$OPERATION" == "restart_jobs" ]; then
  python3 /scripts/restart_jobs.py $@
elif [ "$OPERATION" == "rolling_restart_jobs" ]; then
  python3 /scripts/rolling_restart_jobs.py $@
elif [ "$OPERATION" == "health_check" ]; then
  python3 /scripts/health_check.py $@
elif [ "$OPERATION" == "run_command_no_check" ]; then
  python3 /scripts/run_command_no_check.py $@
fi