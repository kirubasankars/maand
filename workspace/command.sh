mkdir -p /workspace/tmp/$AGENT_IP
sudo rsync -r --rsync-path="sudo rsync" --rsh="ssh -i /workspace/$SSH_KEY" $SSH_USER@$AGENT_IP:/opt/agent/ /workspace/tmp/$AGENT_IP/