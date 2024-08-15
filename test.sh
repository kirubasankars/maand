#!/bin/bash

# Define the network range (replace with your actual network range)
network="192.168.1"

# Loop through all possible IP addresses in the range
for ip in {1..254}
do
  # Ping each IP address once and check if it is alive
  if ping -c 1 -W 1 "$network.$ip" > /dev/null; then
    echo "IP $network.$ip is active"
  fi
done
