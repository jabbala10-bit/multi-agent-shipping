# PolicyMesh

PolicyMesh is a monorepo starter for a policy-gated, multi-agent ecommerce system. The current codebase contains three Google ADK agent packages:

- `shopping`: product search, inventory checks, product Q&A, and cart assistance.
- `shipping`: address collection, tax/shipping calculation, order summary, and approval.
- `storefront`: customer-facing orchestrator that delegates to shopping and shipping over A2A.

The roadmap in [docs/ROADMAP.md](docs/ROADMAP.md) describes the target production system. This repo now starts from a clean Phase 0 foundation: shared configuration, test automation, CI, local launch commands, and import-safe agent smoke tests.

## Repository Layout

```text
policymesh/
|-- policymesh/              # Shared config, Toolbox loading, and dev CLI
|-- shopping/                # Shopping ADK agent package
|-- shipping/                # Shipping ADK agent package
|-- storefront/              # Storefront ADK/A2A orchestrator package
|-- tests/                   # Fast smoke/config/tool tests
|-- scripts/                 # Thin shell wrappers for local commands
|-- data/                    # Product manuals and other sample data
|-- databases/               # SQL seeds and Toolbox database config
|-- docs/                    # Roadmap and engineering notes
|-- infra/                   # Infrastructure notes and future IaC home
|-- docker-compose.local.yml # Local MySQL bootstrap
|-- pyproject.toml           # Python project, dependency, lint, test config
`-- .github/workflows/ci.yml # CI lint and test automation
```

## Quick Start

Install dependencies:

```powershell
uv sync --extra dev
```

Copy local environment defaults:

```powershell
Copy-Item .env.example .env
```

Run checks:

```powershell
uv run --extra dev ruff check .
$env:POLICYMESH_OFFLINE_TOOLS="1"; uv run --extra dev pytest
```

Run an agent in ADK web mode:

```powershell
uv run --extra dev policymesh adk shopping
uv run --extra dev policymesh adk shipping
uv run --extra dev policymesh adk storefront
```

Offline tests set `POLICYMESH_OFFLINE_TOOLS=1` so agent imports do not require live Toolbox or database services.

## Local Services

Start the local database:

```powershell
docker compose -f docker-compose.local.yml up -d
```

The Toolbox config lives at [databases/tools.yaml](databases/tools.yaml). Run your Toolbox service against that file and set the URLs in `.env`:

```text
SHOPPING_TOOLBOX_URL=http://127.0.0.1:5001
SHIPPING_TOOLBOX_URL=http://127.0.0.1:5000
```

## Development Commands

Use the shared CLI directly:

```powershell
uv run --extra dev policymesh test
uv run --extra dev policymesh lint
uv run --extra dev policymesh smoke
uv run --extra dev policymesh doctor
```

Or use the thin PowerShell wrapper:

```powershell
.\scripts\dev.ps1 test
.\scripts\dev.ps1 adk shopping
```

## Current Phase 0 Guarantees

- Agent model names and remote A2A URLs are environment-driven.
- Toolbox loading is centralized and supports deterministic offline placeholders for tests.
- Shopping search uses the Toolbox tool it loads.
- Product Q&A is wired into the shopping orchestrator.
- CI runs Ruff and pytest on Python 3.11 and 3.12.

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) and [docs/MONOREPO.md](docs/MONOREPO.md) for the working conventions.
