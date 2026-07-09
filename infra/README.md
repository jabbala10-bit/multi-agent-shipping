# Infrastructure

This directory is reserved for deployment and operations assets as the project moves beyond the demo phase.

Current local infrastructure lives at the repository root:

- `docker-compose.local.yml`: local MySQL service seeded from `docs/*.sql`.
- `docs/tools.yaml`: Toolbox tool definitions for order, cart, inventory, and search operations.

Recommended future additions:

- `infra/docker/` for service Dockerfiles and compose overlays.
- `infra/k8s/` for Kubernetes manifests or Helm charts.
- `infra/terraform/` for cloud resources.
- `infra/observability/` for dashboards, alerts, and collectors.
