#!/bin/bash

# Requires yq: https://github.com/mikefarah/yq
CONFIG_FILE="accounts.yaml"

if ! command -v yq &> /dev/null; then
    echo "yq is required. Install with: sudo apt install yq"
    exit 1
fi

count=$(yq '.accounts | length' "$CONFIG_FILE")
for i in $(seq 0 $((count - 1))); do
    username=$(yq ".accounts[$i].username" "$CONFIG_FILE")
    password=$(yq ".accounts[$i].password" "$CONFIG_FILE")
    echo "Creating account: $username with password: $password"
done