#!/bin/bash
set -ueo pipefail

sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
dnf remove firewalld

yum update -y
yum install -y rsync make python corntab docker docker-compose

username=agent
if ! id "$username" &>/dev/null; then
   groupadd --gid 1051 $username || true
   useradd --shell /bin/bash -g $username -u 1052 $username || true
fi
usermod -aG docker agent || true

/usr/bin/systemctl daemon-reload
/usr/bin/systemctl enable --now docker