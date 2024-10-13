iptables -A INPUT -p tcp --dport 9090 -j ACCEPT
iptables -A INPUT -p tcp --dport 5100 -j ACCEPT
iptables -A INPUT -p tcp --dport 9100 -j ACCEPT
iptables -A INPUT -p tcp --dport 9144 -j ACCEPT
iptables -A INPUT -p tcp --dport 9200 -j ACCEPT
iptables -A INPUT -p tcp --dport 9300 -j ACCEPT

#rm -rf /opt/agent
#mkdir -p /opt/agent
#chown -R photonconfig /opt/agent
