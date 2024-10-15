#rm -rf /opt/agent
mkdir -p /workspace/tmp
rsync --rsync-path="sudo rsync" -rvc --rsh="ssh -i /workspace/$SSH_KEY" $SSH_USER@$AGENT_IP:/opt/agent/ /workspace/tmp/$AGENT_IP/
