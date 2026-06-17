# Integration diagram — support-triage-agent

External integration points and their ports. Each dependency is swappable behind its port (`ADR-0003`,
`CON-003`, `ASM-004`); test doubles exist for every one.

| Integration | Dependency | Port / contract | Direction | Test double |
|---|---|---|---|---|
| Inbound + send | `DEP-002` email/mailbox | mailbox port: `fetch()`, `send(approval_token)` | in + out (out gated by `INV-001`) | in-memory mailbox |
| Model | `DEP-001` model provider | model port: `classify()`, `draft()` | out | stub model |
| Knowledge base | `DEP-003` KB/retrieval | retrieval port: `search(query) -> passages[]` | out | test corpus |
| Human review | `DEP-004` queue/ticketing | queue port: `enqueue(draft)`, `awaitApproval()` | out + in | stand-in queue |

```
   support-triage-agent
        │  mailbox port ───────▶ DEP-002 (fetch / gated send)
        │  model port  ───────▶ DEP-001
        │  retrieval port ────▶ DEP-003
        └  queue port  ───────▶ DEP-004 (enqueue / approval)
```

- Send through the mailbox port requires an `approval_token`; in PH-2 that token is auto-issued **only**
  for whitelisted categories (`ADR-0004`, Proposed). All ports are exercised in `POC-001` with stubs.
