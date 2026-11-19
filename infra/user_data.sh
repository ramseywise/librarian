#!/bin/bash
# First-boot setup for a librarian host: Docker Engine, Compose v2, /srv/librarian.
# It does not clone the repository, pull an image, or start anything, and it holds no secret.
# Releases are made with ./librarian as docs/ops/deploy.md describes. Log: /var/log/cloud-init-output.log
set -euxo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends ca-certificates curl git rsync

# Docker's own apt repository: Ubuntu's docker.io package has no Compose v2 plugin.
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker

# Where deploy.md clones the repository. Owned by the login user that Ubuntu images create.
mkdir -p /srv/librarian
chown ubuntu:ubuntu /srv/librarian

# Fail the boot log loudly if the tools are missing.
docker --version
docker compose version
