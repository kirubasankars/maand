#!/bin/bash
mkdir -p /opt/agent
ssh -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER "$AGENT_IP" "test -d /opt/agent"
if [ $? -eq 0 ]; then
  rsync -rahzv --rsh="ssh -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" --include='*.txt' --exclude='*' "$AGENT_IP":/opt/agent/ /opt/agent/
fi