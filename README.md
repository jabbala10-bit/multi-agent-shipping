# Multi-Agent Shipping Roadmap

This roadmap turns the current ADK demo into a production-oriented full-stack AI ecommerce system with secure agent orchestration, deterministic business controls, privacy governance, compliance evidence, and LLM cost management.

The guiding principle is simple: use LLM agents for conversation, routing, retrieval, and assisted decisions; use deterministic backend services for authorization, payment, inventory, pricing, order state transitions, audit logging, and compliance controls.

## Target System

The complete system should include:

- Customer storefront web app for product search, cart, checkout, shipping, order tracking, and privacy controls.
- API gateway that authenticates users, rate-limits requests, validates inputs, and mediates all agent/tool access.
- Shopping agent for product discovery, product Q&A, inventory explanation, and cart assistance.
- Shipping agent for address collection, shipping options, tax/shipping explanation, order summary, and fulfillment handoff.
- Storefront orchestrator that routes user intent to specialized agents and keeps conversational context compact.
- Deterministic order service for cart creation, cart mutation, inventory reservation, checkout, approval, payment status, and fulfillment state.
- Product and inventory service backed by a single source of truth.
- Retrieval layer for product manuals and policies, with cited answers and no free-form product invention.
- Policy engine for constraint-aware and context-aware action gating.
- Audit, observability, evaluation, and compliance evidence pipelines.
- Privacy controls for data minimization, consent, export, deletion, retention, and PII redaction.

## Compliance Anchors

This project should track:

- EU AI Act: risk classification, transparency, logging, human oversight, robustness, cybersecurity, accuracy, documentation, post-market monitoring, and incident reporting. Current European Commission guidance says transparency rules come into effect in August 2026, GPAI obligations became effective in August 2025, high-risk rules for certain standalone systems apply from 2 December 2027, and high-risk product-integrated systems apply from 2 August 2028.
- NIST AI RMF: Govern, Map, Measure, and Manage as the operating model for AI risk management.
- GDPR: lawfulness, fairness, transparency, purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality, and accountability.
- OWASP LLM Top 10: prompt injection, sensitive information disclosure, insecure plugin/tool design, excessive agency, model denial of service, supply-chain risk, and overreliance.

Primary references:

- EU AI Act overview: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- GDPR Article 5 principles: https://gdpr-info.eu/art-5-gdpr/
- OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/

## Phase 0: Stabilize The Existing Demo

Goal: make the current repo runnable, testable, and internally consistent.

Work items:

- Fix `shopping/agents/search.py` so the loaded Toolbox search tool is actually used.
- Add or implement separate exact and broad search tools if both behaviors are required.
- Wire `product_qa_agent` into the shopping orchestrator or remove it from the prompt until it is ready.
- Move model names, Toolbox URLs, and remote A2A URLs into environment variables.
- Add `.gitignore` entries for `__pycache__/`, `.venv/`, `.env`, and local database files.
- Add a top-level setup guide for running shopping, shipping, storefront, Toolbox, and MySQL together.
- Add smoke tests that import all agents and verify the expected tools/agents are present.

Acceptance criteria:

- `shopping`, `shipping`, and `storefront` import without `NameError`.
- Local ADK web run starts successfully.
- A product can be searched, added to cart, shipped, summarized, and approved in a happy-path demo.
- Basic tests run in CI.

## Phase 1: Define The Production Architecture

Goal: replace demo wiring with a coherent full-stack system design.

Recommended services:

- `web-app`: customer UI.
- `api-gateway`: authentication, authorization context, rate limits, request validation.
- `agent-orchestrator`: ADK/A2A routing, model selection, prompt assembly, agent tracing.
- `shopping-agent`: product search, product Q&A, cart assistance.
- `shipping-agent`: shipping workflow, address collection, shipping/tax explanation.
- `order-service`: deterministic cart/order state machine.
- `catalog-service`: product, price, inventory, and manual metadata.
- `policy-service`: constraints, authorization, compliance gates, tool allow/deny decisions.
- `audit-service`: immutable action logs and compliance evidence.
- `privacy-service`: data subject requests, retention, redaction, consent records.
- `eval-service`: offline and online AI quality/safety/cost evaluation.

Core data stores:

- Relational database for users, orders, inventory, payments, audit events, consent, and policies.
- Object storage for manuals, invoices, exports, and evidence artifacts.
- Vector or search index for product manuals and policy retrieval.
- Cache for repeated product Q&A, search results, model responses, and session summaries.

Acceptance criteria:

- Architecture diagram and service contracts exist.
- Every agent action maps to a backend API or policy-gated tool.
- There is one source of truth for products, prices, inventory, and orders.

## Phase 2: Build The Backend Foundation

Goal: make business operations deterministic and secure.

Work items:

- Create an order state machine: `draft`, `priced`, `awaiting_approval`, `approved`, `paid`, `placed`, `packaged`, `shipped`, `delivered`, `cancelled`, `refunded`.
- Require legal state transitions instead of arbitrary status updates.
- Add `user_id` or `tenant_id` ownership checks to every order read/update.
- Replace `UPDATE orders WHERE order_id = ?` with guarded operations such as `WHERE order_id = ? AND user_id = ? AND order_status = ?`.
- Add inventory reservation and release, with idempotency keys.
- Add price snapshots so checkout totals do not change silently.
- Add structured address validation and country/state-specific tax/shipping rules.
- Add API schemas with Pydantic or equivalent validation.
- Add error contracts for authorization failure, invalid state, unavailable inventory, stale price, and policy denial.

Acceptance criteria:

- A user cannot read or mutate another user's order.
- A finalized order cannot be modified by prompt injection or direct tool calls.
- Inventory cannot be oversold in concurrent checkout tests.
- Every state transition is logged with actor, reason, input, result, and correlation ID.

## Phase 3: Build The Full-Stack Storefront

Goal: give users a complete ecommerce experience.

Screens:

- Product search and browsing.
- Product detail with manual-backed Q&A.
- Cart.
- Checkout address.
- Shipping options.
- Order review and explicit approval.
- Order tracking.
- Privacy center for export/delete requests and consent preferences.
- Admin view for catalog, inventory, order status, evals, and audit events.

Frontend requirements:

- Show clearly when the user is interacting with AI.
- Require explicit user confirmation for checkout, order placement, cancellation, refund, or address changes.
- Display citations for product-manual answers.
- Show pricing breakdowns and data-use notices.
- Provide accessible, responsive UI.

Acceptance criteria:

- A non-technical user can complete the full order flow from product discovery to order tracking.
- High-impact actions require explicit UI confirmation, not only conversational approval.
- Product Q&A answers include cited retrieved context.

## Phase 4: Make Agents Constraint-Aware

Goal: prevent agents from bypassing business, safety, and privacy rules.

Policy gates:

- User owns the target resource.
- Session is authenticated.
- Action is allowed for the current role.
- Order state allows the requested transition.
- Inventory is available or reserved.
- Price snapshot is current.
- Address data is necessary for the requested task.
- Tool output does not include unnecessary PII.
- LLM response does not expose secrets, internal policies, or other users' data.
- Human approval is present for high-impact actions.

Implementation pattern:

1. Agent proposes a structured action.
2. Policy service evaluates context, constraints, and risk.
3. Backend executes the action only if allowed.
4. Audit service records the proposal, policy decision, execution result, and model/tool metadata.
5. Agent explains the result to the user.

Acceptance criteria:

- No tool is callable directly by the LLM without policy mediation.
- Policy denial returns a safe user-facing explanation.
- Red-team prompts cannot force checkout, cross-user lookup, or hidden data disclosure.

## Phase 5: Make Agents Context-Aware

Goal: improve quality while reducing prompt size and privacy exposure.

Context design:

- Store structured session state: active cart, order ID, confirmed shipping address, selected shipping option, approval status.
- Keep short conversation summaries rather than full chat history.
- Retrieve only the product/manual/order data needed for the current task.
- Redact or tokenize PII before sending it to the model where possible.
- Separate public catalog context from personal order context.
- Add freshness markers for inventory, price, and shipping estimates.

Acceptance criteria:

- Agents can resume a shopping session without loading the full transcript.
- PII sent to LLMs is minimized and logged.
- Answers distinguish confirmed facts, estimates, and unavailable information.

## Phase 6: Security Hardening

Goal: defend the system as an internet-facing AI application.

Controls:

- OIDC/OAuth2 authentication.
- Role-based and attribute-based access control.
- Service-to-service authentication with mTLS or signed tokens.
- TLS everywhere.
- Secrets manager for API keys and database credentials.
- Prompt-injection resistant tool design.
- Strict JSON schemas for tool inputs and outputs.
- Output validation before rendering or executing downstream actions.
- Rate limits and budget limits by user, tenant, IP, model, and action.
- Dependency scanning, SBOM, SAST, DAST, and container scanning.
- Database least privilege: separate read-only and write roles per service.
- Centralized security logging and alerting.

Acceptance criteria:

- Security tests cover OWASP LLM risks relevant to the system.
- Compromised or manipulated retrieved documents cannot trigger tool calls.
- Secrets do not appear in prompts, traces, logs, or frontend output.

## Phase 7: Privacy And GDPR Readiness

Goal: make privacy controls operational, not just policy text.

Work items:

- Create a data inventory: users, orders, addresses, chat logs, traces, model prompts, tool outputs, analytics, support tickets.
- Define legal basis and purpose for each data category.
- Minimize prompts and logs to the data required for each task.
- Add consent records where consent is the legal basis.
- Add privacy notice and AI interaction notice.
- Add data export endpoint.
- Add deletion/anonymization endpoint.
- Add retention schedules for chat logs, traces, carts, abandoned orders, and audit logs.
- Encrypt PII at rest and in transit.
- Redact PII in observability tooling.
- Add DPIA template and records of processing activities.
- Define processor/subprocessor records for model providers, hosting, analytics, and search services.

Acceptance criteria:

- A data subject request can be fulfilled through tested workflows.
- Retention jobs delete or anonymize expired data.
- Audit logs prove what personal data was used, why, and by which service.

## Phase 8: AI Governance, EU AI Act, And NIST AI RMF

Goal: maintain an evidence base for responsible AI operation.

Govern:

- AI system inventory.
- Ownership and RACI.
- AI acceptable-use policy.
- Human oversight process.
- Incident response plan.
- Vendor/model governance.
- Change approval process for prompts, tools, models, policies, and retrieval indexes.

Map:

- Intended use and reasonably foreseeable misuse.
- Users and affected persons.
- Data flows.
- Tool/action inventory.
- Risk classification under EU AI Act.
- Fundamental-rights, safety, privacy, and security impact analysis.

Measure:

- Task success rate.
- Hallucination and unsupported-answer rate.
- Retrieval citation quality.
- Prompt-injection resistance.
- Unauthorized action prevention.
- PII leakage rate.
- Latency and uptime.
- Cost per session/order.
- Human escalation rate.

Manage:

- Risk treatment plan.
- Production monitoring.
- Incident and serious-incident reporting workflow.
- Post-market monitoring.
- Periodic model and prompt reviews.
- Rollback plan.

Acceptance criteria:

- Each release has a model/prompt/tool change log and eval report.
- AI risks have owners, controls, test evidence, and review dates.
- The system can produce compliance evidence on demand.

## Phase 9: LLM Cost Reduction Strategy

Goal: reduce cost without degrading user trust or safety.

Strategies:

- Route simple tasks to smaller models.
- Keep deterministic work out of the LLM: tax, shipping, price, inventory, order status, policy checks.
- Cache stable product Q&A and search results.
- Use retrieval snippets instead of whole manuals.
- Summarize sessions into compact structured state.
- Limit max tokens per agent and per workflow.
- Avoid unnecessary multi-agent fan-out.
- Use embeddings/search for product matching before invoking a chat model.
- Batch offline evals and manual indexing.
- Track cost per user, session, order, agent, tool, and model.
- Add budget kill switches and graceful degradation.

Acceptance criteria:

- Cost per completed order is measured and visible.
- Repeated product/manual questions hit cache.
- Model routing is configurable by task risk and complexity.

## Phase 10: Observability And Evaluation

Goal: know what the system is doing and whether it is safe.

Telemetry:

- Request ID, session ID, user ID hash, tenant ID.
- Model name, prompt version, token counts, latency, and cost.
- Tool name, input hash, output hash, policy decision, and execution result.
- Retrieval query, document IDs, chunk IDs, and citation score.
- State transition events.
- PII redaction events.
- User feedback and human escalation events.

Evals:

- Golden-path ecommerce flows.
- Product Q&A groundedness.
- Prompt-injection attempts.
- Cross-user data access attempts.
- Checkout confirmation bypass attempts.
- PII leakage tests.
- Regression tests for prompts and policies.

Acceptance criteria:

- Dashboards show quality, safety, cost, and latency.
- Failed or risky agent behavior can be replayed safely from logs.
- CI blocks prompt/tool changes that fail critical evals.

## Phase 11: Deployment And Operations

Goal: run the system reliably in realistic environments.

Work items:

- Dockerize every service.
- Add local Docker Compose for app, database, Toolbox or tool gateway, search index, and observability.
- Add environment-specific configuration for dev, staging, and production.
- Add migrations.
- Add CI for tests, type checks, linting, security scans, and container builds.
- Add CD with staged rollout and rollback.
- Add backups and disaster recovery.
- Add production runbooks.
- Add SLOs for checkout, search, order placement, and agent response.

Acceptance criteria:

- A new developer can run the whole stack locally.
- Staging mirrors production service boundaries.
- Production deployment is repeatable and rollback-capable.

## Suggested Milestones

### Milestone 1: Runnable Demo Hardening

Duration: 1-2 weeks.

Deliverables:

- Fixed imports and agent wiring.
- Environment-based configuration.
- Smoke tests.
- Local run guide.
- Basic `.gitignore`.

### Milestone 2: Secure Backend Core

Duration: 2-4 weeks.

Deliverables:

- Authenticated API gateway.
- Order service with state machine.
- Guarded SQL/tool operations.
- Inventory reservation.
- Audit events.

### Milestone 3: Full Customer Flow

Duration: 3-5 weeks.

Deliverables:

- Web storefront.
- Product search/detail/cart/checkout/tracking.
- Agent-assisted product Q&A.
- Explicit checkout approval UI.
- Basic admin dashboard.

### Milestone 4: Policy-Gated Agentic System

Duration: 3-4 weeks.

Deliverables:

- Policy service.
- Structured agent actions.
- Tool allow/deny gates.
- PII redaction.
- Prompt-injection and unauthorized-action tests.

### Milestone 5: Compliance And Governance Pack

Duration: 2-4 weeks.

Deliverables:

- AI system card.
- Risk register.
- DPIA template.
- Data inventory.
- AI Act classification memo.
- NIST AI RMF control map.
- Eval reports.
- Incident response runbook.

### Milestone 6: Cost, Observability, And Production Readiness

Duration: 2-4 weeks.

Deliverables:

- Cost dashboards.
- Model routing.
- Caching.
- Full telemetry.
- CI/CD.
- Deployment runbooks.

## Priority Backlog

High priority:

- Fix broken search agent.
- Wire product QA or remove stale prompt references.
- Add user ownership checks to all order tools.
- Replace arbitrary status updates with state-machine transitions.
- Add audit logging around all tool calls.
- Move hard-coded URLs and models into config.
- Add prompt/tool security tests.

Medium priority:

- Create unified product/catalog source of truth.
- Add frontend checkout flow.
- Add retrieval citations for product manuals.
- Add privacy center.
- Add cost tracking and model routing.
- Add Docker Compose and migrations.

Lower priority:

- Multi-tenant admin console.
- Advanced personalization.
- A/B testing framework for search and prompts.
- Human support console.
- Formal certification artifacts if the use case becomes high-risk.

## Definition Of Done

The project should be considered a complete AI system when:

- Users can complete the full ecommerce flow through the UI.
- All agent tool use is policy-gated and audited.
- Business-critical operations are deterministic.
- Authorization is enforced at the backend and database/tool layer.
- Personal data handling is documented, minimized, secured, retained, exported, and deleted according to policy.
- AI risks are mapped, measured, managed, and reviewed.
- Prompt-injection, PII leakage, unauthorized action, and cost-overrun tests exist.
- Cost per session and cost per completed order are measured.
- The system has deployment, rollback, monitoring, and incident runbooks.
