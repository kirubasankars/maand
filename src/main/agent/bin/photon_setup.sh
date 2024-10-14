#!/bin/bash
set -ueo pipefail

yum update -y
yum install -y rsync make python corntab docker docker-compose git

username=agent
if ! id "$username" &>/dev/null; then
   groupadd --gid 1061 $username || true
   useradd --shell /bin/bash -g $username -u 1062 $username || true
fi
usermod -aG docker agent || true

/usr/bin/systemctl daemon-reload
/usr/bin/systemctl enable --now docker

iptables -A INPUT -p tcp --dport 9090 -j ACCEPT
iptables -A INPUT -p tcp --dport 5100 -j ACCEPT
iptables -A INPUT -p tcp --dport 9100 -j ACCEPT
iptables -A INPUT -p tcp --dport 9144 -j ACCEPT
iptables -A INPUT -p tcp --dport 9200 -j ACCEPT
iptables -A INPUT -p tcp --dport 9300 -j ACCEPT