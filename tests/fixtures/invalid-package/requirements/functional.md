---
id: DOC-FUNCTIONAL
status: Approved
version: 1.0.0
updated: 2026-06-17
---

# Functional requirements

DEFECT (G-REQ-SRC): FR-002 below has an empty Source cell.
DEFECT (G-IDS): the prose mentions DEC-099, which is never defined anywhere.
DEFECT (G-IDS): FR-7 (in the prose) is a malformed identifier (needs 3 digits).

FR-001 derives from `DEC-099`. See also the malformed `FR-7` token.

| ID | Requirement | Scope | Source |
|---|---|---|---|
| FR-001 | Create a short link from a submitted long URL. | MVP | Intake brief, line 3 |
| FR-002 | Redirect a short link to its target URL. | MVP | - |
| FR-003 | Count and display click totals per link. | MVP | OQ-001 (resolved) |
