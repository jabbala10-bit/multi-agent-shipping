# Databases

This directory holds database-facing assets for local development and future service work.

- `sql/`: SQL seed files and schema snippets loaded by local Compose.
- `tools.yaml`: Toolbox tool definitions that expose database operations to agents.

The local Compose file expects these paths:

```text
databases/sql/inventory.sql
databases/sql/shipping.sql
databases/tools.yaml
```
