# Sales Intelligence Hub – Infrastructure

This repository contains a full-stack prototype of a **CRM/B2B sales intelligence hub**. It packages a static frontend, a FastAPI backend, background workers and schedulers, a PostgreSQL database and Redis queue into a single `docker‑compose` deployment. The goal is to provide an opinionated, batteries‑included starting point that can be deployed on a single VM and later scaled out.

## Project layout

```
crm-infra/
├── api/                 # FastAPI application (backend)
├── worker/              # Background worker and scheduler using RQ
├── ui/                  # Static frontend (HTML/CSS/JS)
├── nginx/               # Nginx config for serving UI and proxying API
├── caddy/               # Caddyfile for automatic HTTPS
├── scripts/             # Helper scripts for setup and maintenance
├── docs/                # Architecture, security and scaling notes
├── backups/             # Location where database backups will be stored
├── docker-compose.yml   # Compose file to bring everything up
└── .env.example         # Template for runtime configuration
```

## Quick start

1. **Clone this repository** to your server or development machine.

2. **Create a `.env` file** from the provided template:

   ```sh
   cp .env.example .env
   # edit .env and provide strong secrets and a DOMAIN if you have one
   ```

3. **Build and run the stack** (requires Docker and docker‑compose):

   ```sh
   docker compose up -d --build
   ```

4. **Access the application**:

   - The UI is served via Caddy at `https://<DOMAIN>` (or `http://<IP>` if no domain is set).
   - The API is reachable at `/api`. Basic health check endpoint: `/api/health`.

## Components

- **UI** – The UI lives under `ui/` and consists of a single `index.html`. It is static and uses vanilla HTML/CSS/JS. As your backend evolves you can hook up the API via `fetch()` calls or migrate to a framework of your choice.

- **API** – Implemented with FastAPI. It exposes endpoints to manage companies, clients, deals and timeline events. See [`api/main.py`](api/main.py) for details. The database layer uses SQLAlchemy and PostgreSQL.

- **Worker** – Long‑running tasks (parsers, synchronisation, AI integration) are handled by background workers using RQ and Redis. A scheduler process periodically enqueues tasks. See [`worker/tasks.py`](worker/tasks.py) and [`worker/scheduler.py`](worker/scheduler.py).

- **Database** – A PostgreSQL 16 container stores all application data. Backups are created daily via `pgbackups` and stored in the `backups/` volume. Adjust retention in `.env`.

- **Nginx & Caddy** – Nginx serves the static UI and proxies API requests. Caddy handles TLS termination and automatic certificate management. If you set `DOMAIN` in your `.env` Caddy will request and renew certificates for you.

## Development

You can run the backend and worker locally without Docker if you have Python 3.12 and PostgreSQL installed. Install dependencies:

```sh
cd api && pip install -r requirements.txt
```

Then start the API:

```sh
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The worker can be started similarly:

```sh
cd worker && pip install -r requirements.txt
rq worker --with-scheduler -u redis://localhost:6379/0
```

## Deployment

See [`docs/deploy-1-hour.md`](docs/deploy-1-hour.md) for a step‑by‑step guide on preparing your VM and running this project in under an hour. It includes firewall guidelines, environment variable setup and verification steps.

## Contributing

This project is a prototype intended for extension and experimentation. Feel free to fork, add new models or endpoints, plug in real parsers and integrate your own AI services.
