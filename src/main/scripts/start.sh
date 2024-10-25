#!/bin/bash
set -ueo pipefail
echo "StrictHostKeyChecking accept-new" >> /etc/ssh/ssh_config

mkdir -p /opt/agents
test -f /workspace/maand.config.env && source /workspace/maand.config.env

export OPERATION=$1
shift

export UPDATE_CERTS=${UPDATE_CERTS:-0}
export SSH_USER=${SSH_USER:-""}
export SSH_KEY=${SSH_KEY:-""}
export AGENT_API=${AGENT_API:-"true"}
export USE_SUDO=${USE_SUDO:-"0"}

if [ "$OPERATION" == "initialize" ]; then
  python3 /scripts/initialize.py
elif [ "$OPERATION" == "uptime" ]; then
  python3 /scripts/uptime.py $@
elif [ "$OPERATION" == "collect" ]; then
  python3 /scripts/collect.py $@
elif [ "$OPERATION" == "build_jobs" ]; then
  python3 /scripts/maand_job.py $@
elif [ "$OPERATION" == "plan" ]; then
  python3 /scripts/plan.py $@
elif [ "$OPERATION" == "deploy" ]; then
  python3 /scripts/deploy.py $@
elif [ "$OPERATION" == "run_command" ]; then
  python3 /scripts/run_command.py $@
elif [ "$OPERATION" == "run_command_local" ]; then
  python3 /scripts/run_command_local.py $@
elif [ "$OPERATION" == "run_command_with_health_check" ]; then
  python3 /scripts/run_command_with_health_check.py $@
elif [ "$OPERATION" == "start_jobs" ]; then
  CMD="start" python3 /scripts/job_control.py $@
elif [ "$OPERATION" == "stop_jobs" ]; then
  CMD="stop" python3 /scripts/job_control.py $@
elif [ "$OPERATION" == "restart_jobs" ]; then
  CMD="restart" python3 /scripts/job_control.py $@
elif [ "$OPERATION" == "rolling_restart_jobs" ]; then
  python3 /scripts/rolling_restart_jobs.py $@
elif [ "$OPERATION" == "health_check" ]; then
  python3 /scripts/health_check.py $@
elif [ "$OPERATION" == "run_command_no_check" ]; then
  python3 /scripts/run_command_no_check.py $@
fi