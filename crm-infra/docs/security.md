# Security Considerations

While this prototype is intended for experimentation, there are several security aspects that should be addressed before running it in production.

## Secrets management

- **Environment variables** – Do not commit real credentials into version control. Use `.env` to store secrets and ensure appropriate file permissions.
- **Database credentials** – Generate strong passwords for PostgreSQL users. Consider using a dedicated secrets management service when possible.
- **GigaChat tokens** – Store API tokens securely (e.g. HashiCorp Vault) and rotate them regularly.

## Network

- **Firewall** – Restrict inbound traffic to ports 80/443 only. Expose SSH only to trusted IPs or via a bastion host.
- **Database exposure** – The PostgreSQL container should not bind to a public interface. In this stack it is only accessible from other containers.
- **HTTPS** – Set `DOMAIN` in `.env` so that Caddy obtains valid TLS certificates. Without a domain the application will be served over HTTP only.

## Authentication & authorisation

The prototype does not implement user authentication. In a production environment you should:

- Add user accounts with hashed passwords and roles (admin, manager, partner, viewer).
- Implement OAuth2/OpenID Connect or integrate with existing identity providers.
- Protect API endpoints with appropriate scopes and verify permissions.

## Data privacy

- **Personal data** – When enriching data about people, respect privacy laws (e.g. GDPR). Implement the *No‑Store* mode to avoid persisting personal data when required.
- **Provenance** – For each piece of enriched data store the source URL, retrieval date and verification status. This allows auditors to verify accuracy.

## Dependencies

Keep Docker images and Python dependencies up to date. Regularly run `docker image ls` and `docker-compose pull` to fetch security updates.
