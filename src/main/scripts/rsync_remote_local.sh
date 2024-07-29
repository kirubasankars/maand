#!/bin/bash
set -e

# Create the directory if it doesn't exist
mkdir -p /opt/agent

# Check if the /opt/agent directory exists on the remote server
if ssh -o StrictHostKeyChecking=no -o LogLevel=error -l "$SSH_USER" "$AGENT_IP" "test -d /opt/agent"; then
  INCLUDE_PATTERNS="--include='*.txt' --include='*.crt' --include='*.key' --include='*.pem' --exclude='*'"
  rsync -rahzv --rsh="ssh -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" $INCLUDE_PATTERNS "$AGENT_IP":/opt/agent/ /opt/agent/
fi
