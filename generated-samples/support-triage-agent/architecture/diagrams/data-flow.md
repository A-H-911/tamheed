# Data-flow diagram — support-triage-agent

What data moves where, with the PII boundary (`INV-003`) marked. Personal data is redacted/tokenized
before it crosses any port to the model or logs.

```
 email (may contain PII) ──▶ Ingestor ──▶ [PII boundary: redact/tokenize before egress]
                                              │
            ┌─────────────────────────────────┼─────────────────────────────────┐
            ▼                                  ▼                                  ▼
   classify features ──▶ Model port      retrieval query ──▶ KB port      audit record ──▶ audit store
   (no raw PII)          (DEP-001)        (no raw PII)        (DEP-003)    (PII-safe fields)  (INV-004)
            │                                                                  
            ▼                                                                  
   {category, urgency, confidence} ──▶ Drafter ──▶ {reply + citations} | {defer}
                                                         │
                                                         ▼
                                          Router/Approval ──▶ human queue (DEP-004)
                                                         │ approved
                                                         ▼
                                              send to customer (INV-001)
```

- Confidence feeds routing (`FR-005`) and, in PH-2 only, the gated auto-send decision (`ADR-0004`).
