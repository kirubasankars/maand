FROM fedora:latest

RUN dnf update -y && dnf install -y openssh-server rsync make tree docker python3

RUN mkdir -p /var/run/sshd /root/.ssh
COPY my_key.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

RUN sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN ssh-keygen -A

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
