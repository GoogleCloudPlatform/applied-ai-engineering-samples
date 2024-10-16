#!/bin/bash
# Ref: https://developer.hashicorp.com/terraform/install

# Set apt to be non-interactive.
export DEBIAN_FRONTEND=noninteractive

apt-get update && apt-get install -y gnupg software-properties-common redis-tools
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
apt-get update && apt-get install -y terraform
