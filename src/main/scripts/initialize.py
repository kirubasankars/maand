import command_helper
import cert_provider
import os

generated_cluster_id = False
cluster_id = os.getenv("CLUSTER_ID")

if not cluster_id:
    result = command_helper.command_local("openssl rand -hex 16")
    cluster_id = result.stdout.strip().decode("utf-8")
    generated_cluster_id = True

files = ['/workspace/secrets.env',
         '/workspace/ca.key',
         '/workspace/ca.crt',
         '/workspace/agents.json']

command_helper.command_local(f"""
    touch /workspace/variables.env    
    touch /workspace/secrets.env
    touch /workspace/agents.json
    mkdir -p /workspace/jobs
""")

if not os.path.isfile('/workspace/ca.key'):
    cert_provider.generate_ca_private()
    cert_provider.generate_ca_public(cluster_id, int(os.getenv("CA_TTL", "3650")))

if generated_cluster_id:
    with open('/workspace/variables.env', 'r') as f:
        variables = f.read()
    with open('/workspace/variables.env', 'w') as f:
        f.write(f"CLUSTER_ID={cluster_id}\n")
        f.write(variables)
