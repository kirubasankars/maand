#!/bin/bash
set -e

# Create the directory if it doesn't exist
mkdir -p $AGENT_DIR/

# Check if the /opt/agent directory exists on the remote server
if ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l "$SSH_USER" "$AGENT_IP" "test -d /opt/agent"; then
  rsync -avc --rsh="ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" --include='*/' --include='cluster_id.txt' --include='agent_id.txt' --include='update_seq.txt' --include='*/certs/*.crt' --include='*/certs/*.key' --include='*/certs/*.pem' --include='*/jobs/*/*.crt' --include='*/jobs/*/*.key' --include='*/jobs/*/*.pem' --include='*/jobs/*/*.hash' --exclude='jobs/**/bin' --exclude='jobs/**/logs' --exclude='jobs/**/data' --exclude='*' "$AGENT_IP":/opt/agent/ $AGENT_DIR/ > /dev/null
  find $AGENT_DIR/ -type d -empty -delete
fi
