#!/bin/bash
set -e

mkdir -p $AGENT_DIR/

RSYNC_PATH="rsync"
if [[ "$USE_SUDO" -eq 0 ]]; then
  RSYNC_PATH="sudo rsync"
fi

if ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l "$SSH_USER" "$AGENT_IP" "test -d /opt/agent"; then
  rsync -ravc --rsync-path="$RSYNC_PATH" --rsh="ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" --include='*/' --include='cluster_id.txt' --include='agent_id.txt' --include='update_seq.txt' --include='*/certs/*.crt' --include='*/certs/*.key' --include='*/certs/*.pem' --include='*/jobs/*/certs/*.crt' --include='*/jobs/*/certs/*.key' --include='*/jobs/*/certs/*.pem' --include='*/jobs/*/certs/*.hash' --exclude='jobs/*/bin' --exclude='jobs/*/logs' --exclude='jobs/*/data' --exclude='*' "$AGENT_IP":/opt/agent/ $AGENT_DIR/ > /dev/null
  find $AGENT_DIR/jobs -path "*" -type d -empty -delete
fi
