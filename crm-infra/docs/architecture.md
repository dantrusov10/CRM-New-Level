# Architecture Overview

This document describes the high‑level architecture of the Sales Intelligence Hub prototype.

## Components

### UI

The UI is a **static single‑page application** served by Nginx. It consists of an `index.html` file and accompanying CSS and JavaScript. The prototype uses only vanilla HTML/CSS/JS, but can be extended or replaced by any front‑end framework. The UI interacts with the backend via AJAX (`fetch()`) requests to `/api`.

### API

The API is a **FastAPI** application running in a Docker container. It exposes RESTful endpoints for managing core entities:

- **Companies** – organisations being sold to. Each company has a name, tax ID (ИНН) and industry.
- **Clients** – contacts within a company, including their position, department and status.
- **Deals** – sales opportunities tied to companies. Each deal has a stage, owner, probability and potential economy.
- **Events** – timeline entries representing activities such as notes, media mentions, tenders or AI‑generated insights.

The API uses **SQLAlchemy** with a **PostgreSQL** database. Each request obtains a database session from a pool and returns Pydantic models.

### Worker & Scheduler

Long‑running and periodic tasks are executed by the **RQ** worker. Examples include:

- Fetching media mentions (media parser)
- Parsing tender data
- Performing minute‑by‑minute synchronisation with external systems
- AI enrichment via GigaChat

The **scheduler** enqueues these tasks at configurable intervals. Both the worker and scheduler use **Redis** for task storage.

### Database

A **PostgreSQL 16** container persists all application data. A separate container (`pgbackups`) performs daily backups, storing them in the `backups/` volume. Retention policies can be configured via environment variables.

### Proxy & TLS

**Nginx** serves static files and proxies API requests. **Caddy** sits in front of Nginx and handles TLS termination with automatic LetsEncrypt certificates. If no domain is configured, Caddy will still serve the site over HTTP.

## Data flow

1. Users access the UI via their browser. The HTML/CSS/JS are delivered by Nginx (via Caddy if HTTPS).
2. The UI fetches data from the FastAPI backend (`/api`) over HTTP. Responses are JSON.
3. Backend interacts with PostgreSQL to read and write entities.
4. Background tasks run asynchronously via RQ, emitting events back into the API when necessary.
5. Database backups are created daily and stored locally in the backups volume.
