# Development Guide

## Prerequisites

- Python 3.11 or newer
- `uv`
- Docker Desktop or Docker Engine, if you want local MySQL
- Google ADK credentials for live agent runs
- Toolbox service for database-backed tools

## Setup

```powershell
uv sync --extra dev
Copy-Item .env.example .env
```

Set `GOOGLE_API_KEY` or the Google authentication method expected by your ADK setup before live agent runs.

## Test And Lint

```powershell
$env:POLICYMESH_OFFLINE_TOOLS="1"; uv run --extra dev pytest
uv run --extra dev ruff check .
```

The tests are intentionally fast and import-oriented. They validate the monorepo foundation without requiring cloud credentials, MySQL, or Toolbox.

## Launch Agents

```powershell
uv run --extra dev policymesh adk shopping
uv run --extra dev policymesh adk shipping
uv run --extra dev policymesh adk storefront
```

The helper currently launches one ADK app at a time. For end-to-end local work, run the required services in separate terminals.

## Environment

Important variables:

- `POLICYMESH_MODEL`: model used by all local agents.
- `POLICYMESH_OFFLINE_TOOLS`: set to `1` for tests or docs builds without Toolbox.
- `SHOPPING_TOOLBOX_URL`: Toolbox endpoint for shopping/catalog tools.
- `SHIPPING_TOOLBOX_URL`: Toolbox endpoint for order/shipping tools.
- `POLICYMESH_SHOPPING_A2A_URL`: storefront remote shopping agent URL.
- `POLICYMESH_SHIPPING_A2A_URL`: storefront remote shipping agent URL.

See [.env.example](../.env.example) for all currently supported values.

## Local Database

```powershell
docker compose -f docker-compose.local.yml up -d
```

This starts MySQL and loads the SQL files under `databases/sql/`. The Toolbox config in `databases/tools.yaml` expects a `storefront` database.

## CI

GitHub Actions runs:

```bash
python -m pip install -r requirements.txt
python -m ruff check .
python -m pytest
```

CI uses `POLICYMESH_OFFLINE_TOOLS=1`, so failures should generally indicate Python import, wiring, config, lint, or deterministic tool behavior problems rather than missing external services.
