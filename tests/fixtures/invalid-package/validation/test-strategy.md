---
id: DOC-TEST-STRATEGY
status: Approved
version: 1.0.0
updated: 2026-06-17
---

# Test strategy

Note: FR-003 deliberately has no test here, to seed the G-TRACE gap.

| ID | Test | Verifies |
|---|---|---|
| TEST-001 | Unit + API test for short-code creation. | FR-001, AC-001 |
| TEST-002 | Integration test for redirect behaviour. | FR-002, AC-002 |
| TEST-004 | Latency benchmark asserting median < 50 ms. | NFR-001 |
