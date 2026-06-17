# Context diagram — support-triage-agent

The agent and the external actors/systems it touches. All external systems are reached behind
vendor-neutral ports (`ASM-004`, `CON-003`).

```
        ┌─────────────┐         emails           ┌───────────────────────────┐
        │  Customers  │ ───────────────────────▶ │  Email system / mailbox    │  DEP-002
        └─────────────┘                          └─────────────┬─────────────┘
                                                               │ inbound
                                                               ▼
   DEP-003 ┌────────────────┐  grounding    ┌─────────────────────────────────┐  drafts/escalations
           │ Knowledge base │ ◀───────────▶ │     support-triage-agent         │ ─────────────▶ ┌──────────────────┐
           └────────────────┘               │  (bounded loop, INV-005)         │                │ Human-review     │ DEP-004
   DEP-001 ┌────────────────┐  classify/draft│  audit log INV-004 · PII INV-003 │ ◀── approval ──│ queue / agents   │
           │ Model provider │ ◀───────────▶ └─────────────────────────────────┘                └──────────────────┘
           └────────────────┘                          │ send (only after approval, INV-001)
                                                        ▼
                                                  Customer reply
```

- Support Ops (`STK-004`) owns the taxonomy + auto-send whitelist; Security (`STK-002`) owns the PII
  boundary; agents (`STK-005`) approve/edit drafts.
