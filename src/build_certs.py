import base64
import os

import cert_provider
import command_helper
import const
import utils
import context_manager
import kv_manager
import maand


def get_cert_if_available(cursor, file_path, namespace, key):
    content = kv_manager.get(cursor, namespace, key)
    if content:
        content = base64.b64decode(content)
        with open(file_path, "wb") as f:
             f.write(content)


def put_cert(cursor, file_path, namespace, key):
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode('utf-8')
        kv_manager.put(cursor, namespace, key, content)


def build_agent_certs(cursor):
    bucket_id = maand.get_bucket_id(cursor)
    agents = maand.get_agents(cursor, labels_filter=None)

    for agent_ip in agents:

        agent_dir = context_manager.get_agent_dir(agent_ip)
        agent_cert_location = f"{agent_dir}/certs"
        command_helper.command_local(f"mkdir -p {agent_cert_location}")

        namespace = f"certs/{agent_ip}"
        agent_cert_path = f"{agent_cert_location}/agent"

        get_cert_if_available(cursor, f"{agent_cert_path}.key", namespace, "certs/agent.key")
        get_cert_if_available(cursor, f"{agent_cert_path}.crt", namespace, "certs/agent.crt")
        get_cert_if_available(cursor, f"{agent_cert_path}.pem", namespace, "certs/agent.pem")

        found = (os.path.isfile(f"{agent_cert_path}.key") and os.path.isfile(f"{agent_cert_path}.crt")
                 and os.path.isfile(f"{agent_cert_path}.pem"))

        if not found or cert_provider.is_certificate_expiring_soon(f"{agent_cert_path}.crt"):
            cert_provider.generate_site_private("agent", agent_cert_location)
            cert_provider.generate_private_pem_pkcs_8("agent", agent_cert_location)
            cert_provider.generate_site_csr("agent", f"/CN={bucket_id}", agent_cert_location)
            subject_alt_name = f"DNS.1:localhost,IP.1:127.0.0.1,IP.2:{agent_ip}"
            cert_provider.generate_site_public("agent", subject_alt_name, 60, agent_cert_location)

            put_cert(cursor, f"{agent_cert_path}.key", namespace, "certs/agent.key")
            put_cert(cursor, f"{agent_cert_path}.crt", namespace, "certs/agent.crt")
            put_cert(cursor, f"{agent_cert_path}.pem", namespace, "certs/agent.pem")


def build_job_certs(cursor):
    bucket_id = maand.get_bucket_id(cursor)
    agents = maand.get_agents(cursor, labels_filter=None)
    jobs = maand.get_jobs(cursor)
    config_parser = utils.get_maand_conf()

    for agent_ip in agents:
        for job in jobs:
            agent_dir = context_manager.get_agent_dir(agent_ip)
            job_cert_location = f"{agent_dir}/jobs/{job}/certs"
            job_cert_kv_location = f"{job}/certs"
            namespace = f"certs/job/{agent_ip}"

            job_certs = maand.get_job_certs_config(cursor, job)

            update_certs = False
            if job_certs:
                current_hash = kv_manager.get(cursor, namespace, f"{job_cert_kv_location}/md5.hash")
                new_hash = maand.get_job_md5_hash(cursor, job)
                if current_hash != new_hash:
                    kv_manager.put(cursor, namespace, f"{job_cert_kv_location}/md5.hash", new_hash)
                    update_certs = True

            for cert in job_certs:
                command_helper.command_local(f"mkdir -p {job_cert_location}")
                name = cert.get("name")
                job_cert_path = f"{job_cert_location}/{name}"

                get_cert_if_available(cursor, f"{job_cert_path}.key", namespace, f"{job_cert_kv_location}/{name}.key")
                get_cert_if_available(cursor, f"{job_cert_path}.crt", namespace, f"{job_cert_kv_location}/{name}.crt")
                get_cert_if_available(cursor, f"{job_cert_path}.pem", namespace, f"{job_cert_kv_location}/{name}.pem")

                found = (os.path.isfile(f"{job_cert_path}.key") and os.path.isfile(f"{job_cert_path}.crt"))
                if cert.get("pkcs8", False):
                    found = found and os.path.isfile(f"{job_cert_path}.pem")

                if update_certs or not found or cert_provider.is_certificate_expiring_soon(f"{job_cert_path}.crt"):
                    ttl = config_parser.get("default", "certs_ttl") or 60
                    cert_provider.generate_site_private(name, job_cert_location)
                    if cert.get("pkcs8", 0) == 1:
                        cert_provider.generate_private_pem_pkcs_8(name, job_cert_location)

                    subj = cert.get("subject", f"/CN={bucket_id}")
                    cert_provider.generate_site_csr(name, subj, job_cert_location)
                    subject_alt_name = cert.get("subject_alt_name", f"DNS.1:localhost,IP.1:127.0.0.1,IP.2:{agent_ip}")
                    cert_provider.generate_site_public(name, subject_alt_name, ttl, job_cert_location)
                    command_helper.command_local(f"rm -f {job_cert_path}.csr")

                    put_cert(cursor, f"{job_cert_path}.key", namespace, f"{job_cert_kv_location}/{name}.key")
                    put_cert(cursor, f"{job_cert_path}.crt", namespace, f"{job_cert_kv_location}/{name}.crt")

                    if cert.get("pkcs8", False):
                        put_cert(cursor, f"{job_cert_path}.pem", namespace, f"{job_cert_kv_location}/{name}.pem")


def build(cursor):
    build_agent_certs(cursor)
    build_job_certs(cursor)
    command_helper.command_local(f"rm -f {const.SECRETS_PATH}/ca.srl")