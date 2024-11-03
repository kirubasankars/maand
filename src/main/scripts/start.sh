#!/bin/bash
set -ueo pipefail
echo "StrictHostKeyChecking accept-new" >> /etc/ssh/ssh_config

export UPDATE_CERTS=${UPDATE_CERTS:-0}
export OPERATION=$1
shift

mkdir -p /opt/agents
python3 /scripts/kv_manager.py

if [ "$OPERATION" == "init" ]; then
  python3 /scripts/init.py $@
elif [ "$OPERATION" == "build" ]; then
  python3 /scripts/build_jobs.py
  python3 /scripts/plan_agents.py
  python3 /scripts/build_certs.py
  python3 /scripts/build_variables.py
elif [ "$OPERATION" == "update" ]; then
  python3 /scripts/update.py $@
elif [ "$OPERATION" == "deploy" ]; then
  python3 /scripts/update.py $@
elif [ "$OPERATION" == "uptime" ]; then
  python3 /scripts/uptime.py $@
elif [ "$OPERATION" == "run_command" ]; then
  python3 /scripts/run_command.py $@
elif [ "$OPERATION" == "run_command_local" ]; then
  python3 /scripts/run_command_local.py $@
elif [ "$OPERATION" == "start_jobs" ]; then
  CMD="start" python3 /scripts/job_control.py $@
elif [ "$OPERATION" == "stop_jobs" ]; then
  CMD="stop" python3 /scripts/job_control.py $@
elif [ "$OPERATION" == "restart_jobs" ]; then
  CMD="restart" python3 /scripts/job_control.py $@
elif [ "$OPERATION" == "cat" ]; then
  python3 /scripts/cat.py $@
elif [ "$OPERATION" == "run_command_with_health_check" ]; then
  python3 /scripts/run_command_with_health_check.py $@
elif [ "$OPERATION" == "rolling_restart_jobs" ]; then
  python3 /scripts/rolling_restart_jobs.py $@
elif [ "$OPERATION" == "collect" ]; then
  python3 /scripts/collect.py $@
elif [ "$OPERATION" == "health_check" ]; then
  python3 /scripts/health_check.py $@
fi