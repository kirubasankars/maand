#!/bin/bash
set -e

# Create the directory if it doesn't exist
mkdir -p $AGENT_DIR/

# Check if the /opt/agent directory exists on the remote server
if ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l "$SSH_USER" "$AGENT_IP" "test -d /opt/agent"; then
  rsync -ravc --rsh="ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" --include='*/' --include='*.txt' --include='*.crt' --include='*.key' --include='*.pem' --include='*.hash' --exclude='jobs/**/bin' --exclude='jobs/**/logs' --exclude='jobs/**/data' --exclude='*' "$AGENT_IP":/opt/agent/ $AGENT_DIR/ > /dev/null
fi
