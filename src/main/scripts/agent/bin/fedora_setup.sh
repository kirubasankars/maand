#!/bin/bash
set -ueo pipefail

sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
dnf remove firewalld

yum update -y
yum install -y rsync make python docker docker-compose dstat

username=agent
if ! id "$username" &>/dev/null; then
   groupadd --gid 1061 $username || true
   useradd --shell /bin/bash -g $username -u 1062 $username || true
fi
usermod -aG docker agent || true

/usr/bin/systemctl daemon-reload
/usr/bin/systemctl enable --now docker