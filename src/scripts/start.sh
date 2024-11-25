#!/bin/bash
set -ueo pipefail
echo "StrictHostKeyChecking accept-new" >> /etc/ssh/ssh_config

if [ -z "${1+x}" ]; then
  echo "Usage: maand <operation>"
  echo "Operations:"
  echo "  init                          Initialize the bucket"
  echo "  build                         Build bucket"
  echo "  update                        Update agents"
  echo "  uptime                        Check connectivity or uptime"
  echo "  run_command                   Run a command on the agents"
  echo "  run_command_local             Run a command locally"
  echo "  job                           Run job control operations (start, stop, restart, and rolling_restart)"
  echo "  run_job_command               Run job-related commands"
  echo "  cat                           Cat info from build action (agents, jobs, allocations, kv)"
  echo "  run_command_with_health_check Run command with health check"
  echo "  health_check                  Run health checks"
  echo "  gc                            Garbage collect"
  exit 1
fi

export UPDATE_CERTS=${UPDATE_CERTS:-0}
export OPERATION=$1
shift

rm -rf /bucket/logs/*
mkdir -p /opt/agents
python3 /scripts/kv_manager.py

if [ "$OPERATION" == "init" ]; then
  python3 /scripts/init.py
elif [ "$OPERATION" == "build" ]; then
  python3 /scripts/build_jobs.py
  python3 /scripts/build_agents.py
  python3 /scripts/build_variables.py
  python3 /scripts/build_certs.py
elif [ "$OPERATION" == "update" ]; then
  python3 /scripts/update.py $@
elif [ "$OPERATION" == "uptime" ]; then
  python3 /scripts/uptime.py $@
elif [ "$OPERATION" == "run_command" ]; then
  python3 /scripts/run_command.py $@
elif [ "$OPERATION" == "run_command_local" ]; then
  python3 /scripts/run_command_local.py $@
elif [ "$OPERATION" == "job" ]; then
  export CMD="$1" && shift
  if [ "$CMD" == "rolling_restart" ]; then
    python3 /scripts/rolling_restart_jobs.py $@
  else
    python3 /scripts/job_control.py $@
  fi
elif [ "$OPERATION" == "run_job_command" ]; then
  python3 /scripts/job_command_executor.py $@
elif [ "$OPERATION" == "cat" ]; then
  python3 /scripts/cat.py $@
elif [ "$OPERATION" == "run_command_with_health_check" ]; then
  python3 /scripts/run_command_with_health_check.py $@
elif [ "$OPERATION" == "health_check" ]; then
  python3 /scripts/health_check.py $@
elif [ "$OPERATION" == "gc" ]; then
  python3 /scripts/gc.py
fi