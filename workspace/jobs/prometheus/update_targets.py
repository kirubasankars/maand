def update_targets(file, port, variable):
    with open(file, "r") as f:
        line = f.readline()
        targets = ",".join([f'"{t.strip()}:{port}"' for t in line.split(",") if len(t.strip()) > 0])

    file_path = "./prometheus.yml"

    with open(file_path, 'r') as file:
        content = file.read()

    new_content = content.replace(variable, targets)

    with open(file_path, 'w') as file:
        file.write(new_content)

update_targets("./node_exporter_targets.txt", "9100", "$NODE_EXPORTER_TARGETS")
update_targets("./node_exporter_targets.txt", "9101", "$CADVISOR_EXPORTER_TARGETS")
update_targets("./opensearch_exporter_targets.txt", "9114", "$OPENSEARCH_EXPORTER_TARGETS")
update_targets("./opensearch_exporter_targets.txt", "5100", "$AGENT_API_EXPORTER_TARGETS")