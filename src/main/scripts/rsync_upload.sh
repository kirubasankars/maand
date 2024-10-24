#!/bin/bash

RSYNC_PATH="rsync"
if [[ "$USE_SUDO" -eq 1 ]]; then
  RSYNC_PATH="sudo rsync"
fi

RSYNC_OPTIONS=" \
  --ignore-times \
  --verbose \
  --force \
  --delete \
  --compress \
  --checksum \
  --recursive \
  --exclude=\".git\" \
  --exclude=\"certs/reload.txt\" \
  --exclude=\"jobs/*/bin\" \
  --exclude=\"jobs/*/data\" \
  --exclude=\"jobs/*/logs\" \
  --filter='merge /tmp/rsync_rules.txt' \
"

rsync_command="rsync --rsync-path=\"$RSYNC_PATH\" $RSYNC_OPTIONS --rsh=\"ssh -i /workspace/$SSH_KEY\" $AGENT_DIR/ $SSH_USER@$AGENT_IP:/opt/agent/"
bash -c "$rsync_command" > /dev/null
