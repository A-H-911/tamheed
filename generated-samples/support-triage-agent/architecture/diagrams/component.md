# Component diagram — support-triage-agent

Internal components and the controls that wrap them. The orchestration pattern *inside* the bounded loop
is deferred (`DEC-005`, `POC-001`); the components and their contracts are fixed.

```
┌──────────────────────────── bounded loop runtime (ADR-0003, INV-005) ────────────────────────────┐
│  allow-list + per-run cost/iteration cap; fail closed                                             │
│                                                                                                   │
│   Ingestor ─▶ Classifier ─▶ Retriever ─▶ Drafter ─▶ Router ─▶ Approval gate ─▶ (send)             │
│   FR-001       FR-002        FR-003       FR-004      FR-005     FR-006/INV-001                    │
│      │           │             │            │ {reply,cites} | {defer}                              │
│      │           │             │            └── ADR-0002 / INV-002                                 │
│      ▼           ▼             ▼            ▼          ▼          ▼                                 │
│  ┌──────────────────── audit log (append-only, FR-007 / INV-004) ────────────────────┐            │
│  └──────────────────── PII boundary (INV-003) across every port call ─────────────────┘            │
│                                                                                                   │
│   model/tool ports (vendor-neutral) ── DEP-001 (model) · DEP-003 (KB) · DEP-004 (queue)            │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```
