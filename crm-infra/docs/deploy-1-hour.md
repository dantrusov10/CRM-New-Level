# One‑Hour Deployment Guide

This guide describes how to deploy the Sales Intelligence Hub on a fresh Linux VM (Ubuntu/Debian) in less than an hour. It assumes basic familiarity with the command line and sudo privileges.

## 1. Prepare your VM

1. Provision a virtual machine with at least **4 vCPUs**, **8 GB RAM** and **80 GB SSD** storage.
2. Update system packages:

   ```sh
   sudo apt update && sudo apt upgrade -y
   ```

3. Install dependencies (curl, git, etc.):

   ```sh
   sudo apt install -y git curl
   ```

## 2. Install Docker & Compose

Run the `scripts/first-run.sh` provided in this repository or follow these manual steps:

```sh
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install docker compose plugin
sudo apt install -y docker-compose-plugin

# Add your user to the docker group to run without sudo
sudo usermod -aG docker $USER
```

Log out and back in to apply group changes.

## 3. Clone the repository

```sh
git clone https://example.com/your-crm-repo.git
cd your-crm-repo
```

## 4. Configure environment variables

Copy the provided example and edit:

```sh
cp .env.example .env
nano .env
```

Set **strong passwords** for `POSTGRES_PASSWORD` and optionally specify `DOMAIN` if you have a DNS record pointing to your VM. Without a domain the site will be served over HTTP only.

## 5. Start the stack

```sh
docker compose up -d --build
```

Docker will build the API and worker images, pull dependencies and start all services. This may take several minutes.

## 6. Verify the deployment

Visit `http://<your-vm-ip>/` in your browser. You should see the Sales Intelligence Hub UI. Test the API with curl:

```sh
curl http://<your-vm-ip>/api/health
# → {"ok": true}
```

If you set `DOMAIN` in `.env`, Caddy will automatically request and install TLS certificates. Browse to `https://<your-domain>/` after a few minutes.

## 7. Firewall & hardening

- Allow inbound traffic on ports **80** and **443** only. Restrict SSH to trusted IPs.
- Ensure the `.env` file is not world‑readable.
- Regularly update container images: `docker compose pull && docker compose up -d`.

## 8. Next steps

This prototype provides a foundation for your CRM. You can now:

- Extend the backend models and endpoints.
- Implement real parsers and AI integrations in the worker.
- Add authentication and access control.
- Connect the UI to the API by adding JavaScript fetch calls.
