# Scaling Plan

This prototype is optimised for a single VM deployment. As your CRM usage grows you may need to scale out components independently. Below are suggestions for evolving the architecture.

## Database

- Move PostgreSQL to a managed database service (e.g. Yandex Managed DB, AWS RDS) for automated backups, failover and monitoring.
- Increase instance size or switch to a more powerful machine type as data grows. Monitor CPU, memory and disk I/O.
- Use read replicas if read traffic dominates.

## Backend & worker

- Separate the API and worker processes onto different VMs/containers. This prevents CPU‑intensive jobs from affecting API response times.
- Horizontal scaling can be achieved by running multiple API containers behind a load balancer (e.g. Nginx, Caddy or cloud LB).
- Scale worker processes independently based on queue length. RQ allows multiple workers to consume tasks from the same queue.

## Caching & queueing

- Introduce a caching layer (e.g. Redis) for frequently accessed data or results of expensive queries.
- Use dedicated Redis or managed services when throughput exceeds local container capacity.

## Frontend

- Host the static UI on a CDN to reduce latency and offload traffic from your origin server.
- Implement client‑side caching and offline capabilities with Service Workers.

## Observability

- Add logging and monitoring (e.g. Prometheus + Grafana, ELK stack) to track request latency, error rates and resource utilisation.
- Set up alerts on key metrics (CPU, memory, disk, queue length, database connections).

## High availability

- Run services in at least two availability zones.
- Use a load balancer to distribute traffic across multiple instances.
- Implement automated recovery for worker processes.
