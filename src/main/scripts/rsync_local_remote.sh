#!/bin/bash
SSH_OPTIONS="ssh -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER"
rsync -rahzv --rsh=$SSH_OPTIONS /opt/agent/ "$AGENT_IP":/opt/agent/
rsync -rahzv --rsh=$SSH_OPTIONS --delete --exclude 'bin' --exclude 'data' --exclude 'logs' /opt/agent/ "$AGENT_IP":/opt/agent/