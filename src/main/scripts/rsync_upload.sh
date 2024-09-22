#!/bin/bash
rsync -rahz --quiet --rsh="ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" $AGENT_DIR/ "$AGENT_IP":/opt/agent/ > /dev/null
rsync -rahz --quiet --rsh="ssh -i /workspace/$SSH_KEY -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" --delete --exclude 'bin' --exclude 'data' --exclude 'logs' $AGENT_DIR/ "$AGENT_IP":/opt/agent/ > /dev/null