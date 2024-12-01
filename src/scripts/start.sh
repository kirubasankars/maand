#!/bin/bash
set -ueo pipefail

if [ -z "${1+x}" ]; then
  echo "Usage: maand <operation>"
  echo "Operations:"
  echo "  init                          Initialize the bucket"
  echo "  build                         Build bucket"
  echo "  update                        Update agents"
  echo "  uptime                        Check connectivity or uptime"
  echo "  run_command                   Run a command on the agents"
  echo "  run_command_local             Run a command locally"
  echo "  job                           Run job control operations (start, stop and restart)"
  echo "  run_job_command               Run job-related commands"
  echo "  cat                           Cat info from build action (agents, jobs, allocations, kv)"
  echo "  run_command_with_health_check Run command with health check"
  echo "  health_check                  Run health checks"
  echo "  gc                            Garbage collect"
  exit 1
fi

export OPERATION=$1
shift

echo "StrictHostKeyChecking accept-new" >> /etc/ssh/ssh_config
test -f /bucket/setup.sh && sh /bucket/setup.sh
rm -rf /bucket/logs/*
mkdir -p /opt/agents
python3 /scripts/kv_manager.py

function run_python_script {
    script=$1
    shift
    python3 "/scripts/$script" "$@"
}

case "$OPERATION" in
  "init")
    run_python_script "init.py"
    ;;
  "info")
    run_python_script "cat.py" info
    ;;
  "build")
    run_python_script "build_jobs.py"
    run_python_script "build_agents.py"
    run_python_script "build_variables.py"
    run_python_script "build_certs.py"
    ;;
  "update")
    run_python_script "update.py" "$@"
    ;;
  "job")
    run_python_script "job_control.py" "$@"
    ;;
  "health_check")
    run_python_script "health_check.py" "$@"
    ;;
  "job_command")
    run_python_script "job_command_executor.py" "$@"
    ;;
  "cat")
    run_python_script "cat.py" "$@"
    ;;
  "uptime")
    run_python_script "uptime.py" "$@"
    ;;
  "run_command")
    run_python_script "run_command.py" "$@"
    ;;
  "run_command_local")
    run_python_script "run_command_local.py" "$@"
    ;;
  "run_command_with_health_check")
    run_python_script "run_command_with_health_check.py" "$@"
    ;;
  "gc")
    run_python_script "gc.py"
    ;;
  *)
    echo "Unknown operation: $OPERATION"
    exit 1
    ;;
esac
