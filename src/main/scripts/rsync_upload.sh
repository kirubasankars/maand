#!/bin/bash

RSYNC_PATH="rsync"
if [[ "$USE_SUDO" -eq 0 ]]; then
  RSYNC_PATH="sudo rsync"
fi

rsync -ravc --stats --human-readable --rsync-path="$RSYNC_PATH" --rsh="ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" --delete --filter='merge /tmp/rsync_rules.txt' $AGENT_DIR/ "$AGENT_IP":/opt/agent/ > /dev/null