AGENT_MASK=$(echo $AGENT_IP | sed 's/./_/g')
mkdir -p /workspace/$AGENT_MASK
#rsync -rahzv --rsh="ssh -o StrictHostKeyChecking=no -o LogLevel=error -l $SSH_USER" "$AGENT_IP":/opt/agent/ /opt/agent/