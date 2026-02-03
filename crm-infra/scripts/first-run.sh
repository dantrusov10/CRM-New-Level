#!/bin/bash
# First run script to prepare a Ubuntu/Debian server for the Sales Intelligence Hub.
#
# This script installs Docker and docker‑compose if they are not present,
# clones the CRM repository and brings up the stack. It assumes you are
# running as a user with sudo privileges.

set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Installing Docker..."
  sudo apt update
  sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update
  sudo apt install -y docker-ce docker-ce-cli containerd.io
  sudo usermod -aG docker "$USER"
fi

if ! command -v docker compose >/dev/null 2>&1; then
  echo "Installing docker-compose plugin..."
  sudo apt install -y docker-compose-plugin
fi

# Clone repository if not already present
REPO_DIR=${REPO_DIR:-~/crm-infra}
if [ ! -d "$REPO_DIR" ]; then
  echo "Cloning repository into $REPO_DIR..."
  git clone https://example.com/your-crm-repo.git "$REPO_DIR"
fi

cd "$REPO_DIR"

# Copy .env.example to .env if not present
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Please edit .env and set strong passwords and your domain before running docker compose"
fi

echo "Bringing up containers..."
docker compose up -d --build

echo "Done. Visit the UI at http://<server-ip>/"
