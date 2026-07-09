# Monorepo Structure

PolicyMesh keeps runnable agent packages at the repository root because Google ADK discovers packages such as `shopping`, `shipping`, and `storefront` directly. Shared code and automation live in the `policymesh` package.

## Boundaries

- `policymesh/`: shared support code only. No domain business logic should live here unless it is genuinely cross-cutting.
- `shopping/`: shopping-domain agents, prompts, catalog search, inventory, cart workflow, and product Q&A.
- `shipping/`: shipping-domain agents, prompts, tax/shipping calculation, order summary, and approval workflow.
- `storefront/`: front-door orchestration and remote A2A delegation.
- `tests/`: fast unit and smoke tests that must run without external services.
- `docs/`: roadmap, SQL, Toolbox configuration, and engineering notes.
- `infra/`: local/deployment infrastructure notes and future IaC modules.

## Dependency Policy

Use `pyproject.toml` as the root source of truth. Package-local `requirements.txt` files are retained for ADK/demo compatibility, but new dependencies should be added at the root first.

## Configuration Policy

New code should read configuration through `policymesh.config` or explicit environment variables documented in `.env.example`. Avoid adding hard-coded model names, ports, URLs, or tool names inside agent modules.

## Test Policy

Every structural change should keep these commands green:

```powershell
uv run --extra dev ruff check .
$env:POLICYMESH_OFFLINE_TOOLS="1"; uv run --extra dev pytest
```

Tests should prefer deterministic local behavior. Integration tests that require Toolbox, MySQL, ADK, or Google Cloud should be clearly separated later, for example under `tests/integration/`.

## Future Services

The roadmap anticipates services such as `api-gateway`, `order-service`, `catalog-service`, `policy-service`, `audit-service`, `privacy-service`, and `eval-service`. Add those as top-level packages or service directories only when implementation starts, with their own clear contracts and tests.
