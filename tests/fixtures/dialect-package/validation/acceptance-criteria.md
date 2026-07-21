---
id: DOC-ACCEPTANCE
status: Approved
version: 1.0.0
updated: 2026-06-17
---

# Acceptance criteria

Testable, user-visible criteria for the MVP requirements. Statements exceed 120
characters on purpose — the length that was silently truncated before plan 017
(field-evidence C12).

| ID | Given / When / Then | Verifies |
|---|---|---|
| AC-001 | Given a long URL submitted through the public form or the API endpoint, when the shortener processes the submission and persists the record, then a unique short code is returned to the caller and stored exactly once. | FR-001 |
| AC-002 | Given a previously issued short code requested over HTTP by any client, when the redirect handler resolves the code against the single-table store, then the client is redirected to the original target URL with a 301 response. | FR-002 |
| AC-003 | Given a link that has accumulated prior visits from distinct clients, when its statistics page is viewed by the owner, then the displayed click total matches the number of recorded visits including the batched increments. | FR-003 |
