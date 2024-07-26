from command_helper import *


def generate_ca_private():
    command_local("openssl genrsa -out /workspace/ca.key 4096")


def generate_ca_public(common_name, ttl):
    command_local(f"openssl req -new -x509 -sha256 -days {ttl} -subj /CN={common_name} -key "
                  "/workspace/ca.key -out /workspace/ca.crt")


def generate_site_private(name):
    command_local(f"openssl genrsa -out /opt/agent/certs/{name}.key 4096")


def generate_site_csr(name, common_name):
    command_local(f"openssl req -new -sha256 -subj /CN={common_name} -key /opt/agent/certs/{name}.key "
                  f"-out /opt/agent/certs/{name}.csr")


def generate_private_pem_pkcs_8(name):
    command_local(f"openssl pkcs8 -inform PEM -outform PEM -in /opt/agent/certs/{name}.key -topk8 -nocrypt "
                  f"-v1 PBE-SHA1-3DES -out /opt/agent/certs/{name}.pem")


def generate_site_public(name, san, ttl):
    with open("/tmp/extfile.conf", "w") as f:
        f.writelines(f"subjectAltName={san}")
    command_local(f"openssl x509 -req -sha256 -days {ttl} -in /opt/agent/certs/{name}.csr "
                  f"-CA /workspace/ca.crt -CAkey /workspace/ca.key "
                  f"-out /opt/agent/certs/{name}.crt -extfile /tmp/extfile.conf -CAcreateserial 2> /dev/null")


def trust_ca_public():
    command_local("""
        update-ca-trust force-enable
        cp /opt/agent/certs/ca.crt /etc/pki/ca-trust/source/anchors/
        update-ca-trust extract
    """)


def generate_encryption_key():
    result = command_local("openssl rand -base64 32")
    return result.stdout.decode('utf-8').strip()
