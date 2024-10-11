rm -rf /opt/agent
mkdir -p /opt/agent
chown -R photonconfig /opt/agent

#iptables -A INPUT -p tcp --dport 5100 -j ACCEPT
#iptables -A INPUT -p tcp --dport 9300 -j ACCEPT
#iptables -A INPUT -p tcp --dport 9200 -j ACCEPT

#cd /opt/agent/jobs/telegraf && docker-compose stats

#rm -rf /opt/agent/jobs/opensearch
