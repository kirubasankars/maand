with open("./node_exporter_targets.txt", "r") as f:
    line = f.readline()
    targets = ",".join([f'"{t.strip()}:9100"' for t in line.split(",") if len(t.strip()) > 0])

file_path = "./prometheus.yml"

with open(file_path, 'r') as file:
    content = file.read()

new_content = content.replace('$TELEGRAF_TARGETS', targets)

with open(file_path, 'w') as file:
    file.write(new_content)