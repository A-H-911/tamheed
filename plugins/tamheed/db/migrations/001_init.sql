-- Tamheed v2 relational package store — schema (ADR-0001, plan 007/B2).
-- Canonical storage is JSONL per table (see CANONICAL.md); this schema is the SQLite
-- runtime the loader enforces integrity with. `PRAGMA foreign_keys = ON` is set by the
-- single connection factory in store.py — NOT here (pragmas don't persist in DDL).
--
-- Conventions (ADR-0001):
--   * TEXT primary keys use the governed ID scheme (FR-001 style) — v1 identifiers
--     survive migration unchanged.
--   * Three-axis status: lifecycle_status / verdict / disposition are independent.
--     A non-null disposition REQUIRES disposition_reason_ref (the deciding DEC-/ADR-).
--   * Provenance: source_kind + source_span; NOT NULL on requirements (G-REQ-SRC).
--   * `custom_attributes` (JSON TEXT) + `last_referenced` on every entity table.
--   * entity_index is DERIVED (trigger-maintained) — never serialized to JSONL.
--     Cross-type references (trace_edges, disposition_reason_ref, discharged_by)
--     FK into it: G-IDS as schema.
--   * Approval-bearing rows (adrs, approved acceptance_criteria) are immutable:
--     supersede (INSERT successor, set superseded_by), never edit — trigger-enforced.
--   * This file's versioned twin is migrations/001_init.sql (byte-identical).
--     Never edit 001 after it ships; future change = migrations/NNN_*.sql (append-only).
--
-- Required entity_types registry rows (seeded at package init, not here — DDL stays pure):
--   requirement constraint invariant assumption dependency open-question decision adr risk
--   hypothesis experiment poc test kpi stakeholder phase milestone slice wbs-item
--   acceptance-criterion audit-verdict progress-entry defect deferred-work execution-gate
--   execution-plan convention diagram prompt scope-change narrative-document document-section

-- ---------------------------------------------------------------- package & registry

CREATE TABLE packages (
  name              TEXT PRIMARY KEY,
  title             TEXT NOT NULL,
  profile           TEXT NOT NULL CHECK (profile IN ('enterprise','rnd','legacy','ai-agentic','unknown')),
  mode              TEXT NOT NULL,
  iteration         INTEGER NOT NULL DEFAULT 1,          -- D-UPDATE iteration counter
  package_version   TEXT NOT NULL,
  mvp_definition    TEXT,
  entry_point       TEXT,                                -- absorbed handoff-manifest field (R2)
  go_no_go          TEXT,                                -- absorbed handoff-manifest field (R2)
  created_at        TEXT NOT NULL,
  custom_attributes TEXT
);

CREATE TABLE entity_types (                              -- extensibility registry (plan 015)
  type_id           TEXT PRIMARY KEY,
  label             TEXT NOT NULL,
  id_prefix         TEXT UNIQUE,                         -- NULL for un-prefixed families
  generation_class  TEXT NOT NULL CHECK (generation_class IN
                      ('Always','Conditional','Derived','On-request','Continuous')),
  template_ref      TEXT,
  custom_attributes TEXT
);

CREATE TABLE omissions (                                 -- G-SET: recorded-omitted with reason
  entity_type       TEXT PRIMARY KEY REFERENCES entity_types(type_id),
  reason            TEXT NOT NULL CHECK (reason <> '')
);

CREATE TABLE entity_index (                              -- DERIVED: trigger-maintained, not serialized
  id                TEXT PRIMARY KEY,
  entity_type       TEXT NOT NULL REFERENCES entity_types(type_id)
);

-- ---------------------------------------------------------------- requirements family

CREATE TABLE requirements (
  id                TEXT PRIMARY KEY,
  kind              TEXT NOT NULL,
  title             TEXT NOT NULL,
  statement         TEXT,
  priority          TEXT,
  mvp               INTEGER NOT NULL DEFAULT 0 CHECK (mvp IN (0,1)),
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT NOT NULL CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT NOT NULL CHECK (source_span <> ''),
  introduced_in     INTEGER NOT NULL DEFAULT 1,
  retired_in        INTEGER,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK ((kind = 'functional' AND id GLOB 'FR-[0-9]*')
      OR (kind = 'non-functional' AND id GLOB 'NFR-[0-9]*')),
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE constraints (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'CON-[0-9]*'),
  title             TEXT NOT NULL,
  statement         TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE invariants (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'INV-[0-9]*'),
  title             TEXT NOT NULL,
  statement         TEXT,
  enforcement       TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE assumptions (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'ASM-[0-9]*'),
  title             TEXT NOT NULL,
  statement         TEXT,
  risk_if_wrong     TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE dependencies (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'DEP-[0-9]*'),
  title             TEXT NOT NULL,
  statement         TEXT,
  owner             TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

-- ---------------------------------------------------------------- decisions family

CREATE TABLE open_questions (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'OQ-[0-9]*'),
  title             TEXT NOT NULL,
  question          TEXT,
  resolution        TEXT,
  resolved_by       TEXT REFERENCES entity_index(id),
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE decisions (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'DEC-[0-9]*'),
  title             TEXT NOT NULL,
  decision          TEXT,
  rationale         TEXT,
  -- D-U1 / G-DEC-STATUS: decision statuses are EXACTLY these (no Draft).
  lifecycle_status  TEXT NOT NULL CHECK (lifecycle_status IN
    ('Proposed','Approved','Rejected','Superseded','Deferred','Implemented')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  promoted_to       TEXT REFERENCES adrs(id),            -- DEC-007 -> ADR-0003 promotion link
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE adrs (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'ADR-[0-9][0-9][0-9][0-9]'),
  title             TEXT NOT NULL,
  context           TEXT,
  decision          TEXT,
  consequences      TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Proposed' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  superseded_by     TEXT REFERENCES adrs(id),            -- successor must be INSERTed first
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

-- ---------------------------------------------------------------- risk

CREATE TABLE risks (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'RISK-[0-9]*'),
  title             TEXT NOT NULL,
  description       TEXT,
  probability       TEXT,
  impact            TEXT,
  mitigation        TEXT,                                -- mitigation-plan row folded in (R2)
  -- Field-evidence C5: execution lifecycle so risks stop being write-only.
  risk_state        TEXT NOT NULL DEFAULT 'open' CHECK (risk_state IN
    ('open','mitigated','materialized','retired','accepted')),
  discharged_by     TEXT REFERENCES entity_index(id),    -- the AC/test that discharges it
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

-- ---------------------------------------------------------------- research family

CREATE TABLE hypotheses (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'HYP-[0-9]*'),
  title             TEXT NOT NULL,
  statement         TEXT,                                -- falsifiable form
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE experiments (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'EXP-[0-9]*'),
  title             TEXT NOT NULL,
  method            TEXT,
  timebox           TEXT,
  verdict           TEXT NOT NULL DEFAULT 'Pending' CHECK (verdict IN ('PASS','FAIL','Pending')),
  results           TEXT,                                -- append-only by convention
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE pocs (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'POC-[0-9]*'),
  title             TEXT NOT NULL,
  method            TEXT,
  timebox           TEXT,
  verdict           TEXT NOT NULL DEFAULT 'Pending' CHECK (verdict IN ('PASS','FAIL','Pending')),
  results           TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

-- ---------------------------------------------------------------- validation family

CREATE TABLE tests (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'TEST-[0-9]*'),
  title             TEXT NOT NULL,
  kind              TEXT,
  verdict           TEXT NOT NULL DEFAULT 'Pending' CHECK (verdict IN ('Pass','Fail','Pending')),
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE kpis (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'KPI-[0-9]*'),
  title             TEXT NOT NULL,
  measure           TEXT,
  target            TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE stakeholders (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'STK-[0-9]*'),
  name              TEXT NOT NULL,
  role              TEXT,
  interest          TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

-- ---------------------------------------------------------------- planning family

CREATE TABLE phases (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'PH-[0-9]*'),
  title             TEXT NOT NULL,
  objective         TEXT,
  exit_criteria     TEXT,
  sort_order        INTEGER NOT NULL DEFAULT 0,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  introduced_in     INTEGER NOT NULL DEFAULT 1,          -- D-UPDATE: phases appendable via scope change
  retired_in        INTEGER,
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE milestones (                                -- document merged into roadmap; DATA lives (006)
  id                TEXT PRIMARY KEY CHECK (id GLOB 'MS-[0-9]*'),
  title             TEXT NOT NULL,
  phase_id          TEXT NOT NULL REFERENCES phases(id),
  due               TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE slices (                                    -- field-evidence C6: phase -> slice
  id                TEXT PRIMARY KEY CHECK (id GLOB 'SL-[0-9]*'),
  title             TEXT NOT NULL,
  phase_id          TEXT NOT NULL REFERENCES phases(id),
  objective         TEXT,
  sort_order        INTEGER NOT NULL DEFAULT 0,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  introduced_in     INTEGER NOT NULL DEFAULT 1,
  retired_in        INTEGER,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE wbs_items (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'WBS-[0-9]*'),
  title             TEXT NOT NULL,
  parent_id         TEXT REFERENCES wbs_items(id),
  phase_id          TEXT REFERENCES phases(id),
  slice_id          TEXT REFERENCES slices(id),
  effort            TEXT,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

-- ---------------------------------------------------------------- acceptance & audit

CREATE TABLE acceptance_criteria (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'AC-[0-9]*'),
  title             TEXT NOT NULL,
  statement         TEXT,                                -- given/when/then or equivalent
  requirement_id    TEXT REFERENCES requirements(id),
  slice_id          TEXT REFERENCES slices(id),          -- C6: ACs bind to slices
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  superseded_by     TEXT REFERENCES acceptance_criteria(id),
  introduced_in     INTEGER NOT NULL DEFAULT 1,
  retired_in        INTEGER,
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL)
);

CREATE TABLE audit_verdicts (                            -- acceptance audit as data (006: Always in execution)
  id                TEXT PRIMARY KEY CHECK (id GLOB 'AV-[0-9]*'),
  ac_id             TEXT NOT NULL REFERENCES acceptance_criteria(id),
  verdict           TEXT NOT NULL CHECK (verdict IN ('Met','Partial','Not-met','Pending')),
  evidence          TEXT,
  iteration         INTEGER NOT NULL DEFAULT 1,
  recorded_at       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT
);

-- ---------------------------------------------------------------- execution tracking

CREATE TABLE progress_entries (                          -- append-only journal
  id                TEXT PRIMARY KEY CHECK (id GLOB 'PE-[0-9]*'),
  entry             TEXT NOT NULL,
  phase_id          TEXT REFERENCES phases(id),
  slice_id          TEXT REFERENCES slices(id),
  occurred_at       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE defects (                                   -- 006 pre-approved add-new
  id                TEXT PRIMARY KEY CHECK (id GLOB 'DEF-[0-9]*'),
  title             TEXT NOT NULL,
  severity          TEXT NOT NULL CHECK (severity IN ('critical','high','medium','low')),
  status            TEXT NOT NULL DEFAULT 'Open' CHECK (status IN
    ('Open','In-progress','Fixed','Won''t-fix','Duplicate')),
  found_in          TEXT REFERENCES entity_index(id),    -- slice/phase/AC where found
  fixed_by          TEXT REFERENCES entity_index(id),
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE deferred_work (                             -- field-evidence C2: the strongest signal
  id                TEXT PRIMARY KEY CHECK (id GLOB 'DW-[0-9]*'),
  title             TEXT NOT NULL,
  severity          TEXT NOT NULL CHECK (severity IN ('critical','high','medium','low')),
  activation_trigger TEXT,                               -- when this must be picked up
  invariant_at_stake TEXT REFERENCES invariants(id),
  status            TEXT NOT NULL DEFAULT 'Open' CHECK (status IN
    ('Open','Activated','Scheduled','Done','Won''t-do')),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE execution_gates (                           -- 006: DoR/DoD/checkpoints/gate-definitions merged
  id                TEXT PRIMARY KEY CHECK (id GLOB 'GATE-[0-9]*'),
  gate_kind         TEXT NOT NULL CHECK (gate_kind IN ('ready','done','checkpoint','approval')),
  definition        TEXT NOT NULL,
  applies_to        TEXT REFERENCES entity_index(id),    -- NULL = package-wide
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE execution_plans (                           -- field-evidence C8: per-slice, package-resident
  id                TEXT PRIMARY KEY CHECK (id GLOB 'EP-[0-9]*'),
  slice_id          TEXT NOT NULL REFERENCES slices(id),
  plan              TEXT NOT NULL,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE conventions (                               -- field-evidence C8: durable conventions
  id                TEXT PRIMARY KEY CHECK (id GLOB 'CONV-[0-9]*'),
  statement         TEXT NOT NULL,
  rationale         TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE scope_changes (                             -- D-UPDATE: agile scope change record
  id                TEXT PRIMARY KEY CHECK (id GLOB 'SC-[0-9]*'),
  decision_ref      TEXT NOT NULL REFERENCES entity_index(id),  -- the DEC-/ADR- authorizing it
  description       TEXT NOT NULL,
  iteration         INTEGER NOT NULL,
  custom_attributes TEXT,
  last_referenced   TEXT
);

-- ---------------------------------------------------------------- prose & artifacts

CREATE TABLE narrative_documents (                       -- charter-class prose (006 split)
  id                TEXT PRIMARY KEY CHECK (id GLOB 'DOC-[0-9]*'),
  doc_kind          TEXT NOT NULL CHECK (doc_kind IN
    ('charter','executive-summary','architecture','research-plan','technology-comparison',
     'handoff-overview','readme','governance','contributing','naming','agent-control','other')),
  title             TEXT NOT NULL,
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE document_sections (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'SEC-[0-9]*'),
  document_id       TEXT NOT NULL REFERENCES narrative_documents(id),
  heading           TEXT NOT NULL,
  body              TEXT,
  sort_order        INTEGER NOT NULL DEFAULT 0,
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE diagrams (                                  -- 006: five catalog rows collapsed to one family
  id                TEXT PRIMARY KEY CHECK (id GLOB 'DIA-[0-9]*'),
  kind              TEXT NOT NULL CHECK (kind IN
    ('context','component','integration','deployment','data-flow')),  -- new kind = migration (additive)
  title             TEXT NOT NULL,
  body              TEXT,                                -- diagram source (e.g. mermaid)
  generation_class  TEXT NOT NULL CHECK (generation_class IN ('Conditional','On-request')),
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TABLE prompts (                                   -- handoff prompt bodies as data
  id                TEXT PRIMARY KEY CHECK (id GLOB 'PRM-[0-9]*'),
  prompt_kind       TEXT NOT NULL CHECK (prompt_kind IN ('initial','follow-up','review','situational')),
  title             TEXT NOT NULL,
  body              TEXT NOT NULL,
  phase_id          TEXT REFERENCES phases(id),
  custom_attributes TEXT,
  last_referenced   TEXT
);

-- ---------------------------------------------------------------- typed relations (G-IDS)

CREATE TABLE trace_edges (
  from_id           TEXT NOT NULL REFERENCES entity_index(id),
  to_id             TEXT NOT NULL REFERENCES entity_index(id),
  relation          TEXT NOT NULL CHECK (relation IN
    ('derives_from','mitigates','verifies','supersedes','blocked_by','implements',
     'satisfies','tests','binds_to','discharges','relates_to')),
  PRIMARY KEY (from_id, to_id, relation)
);

CREATE INDEX idx_trace_edges_to ON trace_edges(to_id);

-- ---------------------------------------------------------------- entity_index maintenance
-- Two triggers per entity table keep the derived index exact. Deleting an entity that is
-- still referenced (trace edge, disposition reason, discharge) fails on the index FK — G-IDS.

CREATE TRIGGER trg_requirements_ai AFTER INSERT ON requirements
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'requirement'); END;
CREATE TRIGGER trg_requirements_ad AFTER DELETE ON requirements
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_constraints_ai AFTER INSERT ON constraints
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'constraint'); END;
CREATE TRIGGER trg_constraints_ad AFTER DELETE ON constraints
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_invariants_ai AFTER INSERT ON invariants
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'invariant'); END;
CREATE TRIGGER trg_invariants_ad AFTER DELETE ON invariants
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_assumptions_ai AFTER INSERT ON assumptions
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'assumption'); END;
CREATE TRIGGER trg_assumptions_ad AFTER DELETE ON assumptions
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_dependencies_ai AFTER INSERT ON dependencies
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'dependency'); END;
CREATE TRIGGER trg_dependencies_ad AFTER DELETE ON dependencies
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_open_questions_ai AFTER INSERT ON open_questions
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'open-question'); END;
CREATE TRIGGER trg_open_questions_ad AFTER DELETE ON open_questions
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_decisions_ai AFTER INSERT ON decisions
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'decision'); END;
CREATE TRIGGER trg_decisions_ad AFTER DELETE ON decisions
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_adrs_ai AFTER INSERT ON adrs
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'adr'); END;
CREATE TRIGGER trg_adrs_ad AFTER DELETE ON adrs
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_risks_ai AFTER INSERT ON risks
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'risk'); END;
CREATE TRIGGER trg_risks_ad AFTER DELETE ON risks
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_hypotheses_ai AFTER INSERT ON hypotheses
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'hypothesis'); END;
CREATE TRIGGER trg_hypotheses_ad AFTER DELETE ON hypotheses
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_experiments_ai AFTER INSERT ON experiments
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'experiment'); END;
CREATE TRIGGER trg_experiments_ad AFTER DELETE ON experiments
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_pocs_ai AFTER INSERT ON pocs
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'poc'); END;
CREATE TRIGGER trg_pocs_ad AFTER DELETE ON pocs
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_tests_ai AFTER INSERT ON tests
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'test'); END;
CREATE TRIGGER trg_tests_ad AFTER DELETE ON tests
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_kpis_ai AFTER INSERT ON kpis
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'kpi'); END;
CREATE TRIGGER trg_kpis_ad AFTER DELETE ON kpis
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_stakeholders_ai AFTER INSERT ON stakeholders
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'stakeholder'); END;
CREATE TRIGGER trg_stakeholders_ad AFTER DELETE ON stakeholders
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_phases_ai AFTER INSERT ON phases
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'phase'); END;
CREATE TRIGGER trg_phases_ad AFTER DELETE ON phases
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_milestones_ai AFTER INSERT ON milestones
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'milestone'); END;
CREATE TRIGGER trg_milestones_ad AFTER DELETE ON milestones
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_slices_ai AFTER INSERT ON slices
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'slice'); END;
CREATE TRIGGER trg_slices_ad AFTER DELETE ON slices
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_wbs_items_ai AFTER INSERT ON wbs_items
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'wbs-item'); END;
CREATE TRIGGER trg_wbs_items_ad AFTER DELETE ON wbs_items
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_acceptance_criteria_ai AFTER INSERT ON acceptance_criteria
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'acceptance-criterion'); END;
CREATE TRIGGER trg_acceptance_criteria_ad AFTER DELETE ON acceptance_criteria
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_audit_verdicts_ai AFTER INSERT ON audit_verdicts
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'audit-verdict'); END;
CREATE TRIGGER trg_audit_verdicts_ad AFTER DELETE ON audit_verdicts
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_progress_entries_ai AFTER INSERT ON progress_entries
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'progress-entry'); END;
CREATE TRIGGER trg_progress_entries_ad AFTER DELETE ON progress_entries
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_defects_ai AFTER INSERT ON defects
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'defect'); END;
CREATE TRIGGER trg_defects_ad AFTER DELETE ON defects
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_deferred_work_ai AFTER INSERT ON deferred_work
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'deferred-work'); END;
CREATE TRIGGER trg_deferred_work_ad AFTER DELETE ON deferred_work
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_execution_gates_ai AFTER INSERT ON execution_gates
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'execution-gate'); END;
CREATE TRIGGER trg_execution_gates_ad AFTER DELETE ON execution_gates
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_execution_plans_ai AFTER INSERT ON execution_plans
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'execution-plan'); END;
CREATE TRIGGER trg_execution_plans_ad AFTER DELETE ON execution_plans
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_conventions_ai AFTER INSERT ON conventions
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'convention'); END;
CREATE TRIGGER trg_conventions_ad AFTER DELETE ON conventions
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_scope_changes_ai AFTER INSERT ON scope_changes
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'scope-change'); END;
CREATE TRIGGER trg_scope_changes_ad AFTER DELETE ON scope_changes
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_narrative_documents_ai AFTER INSERT ON narrative_documents
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'narrative-document'); END;
CREATE TRIGGER trg_narrative_documents_ad AFTER DELETE ON narrative_documents
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_document_sections_ai AFTER INSERT ON document_sections
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'document-section'); END;
CREATE TRIGGER trg_document_sections_ad AFTER DELETE ON document_sections
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_diagrams_ai AFTER INSERT ON diagrams
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'diagram'); END;
CREATE TRIGGER trg_diagrams_ad AFTER DELETE ON diagrams
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_prompts_ai AFTER INSERT ON prompts
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'prompt'); END;
CREATE TRIGGER trg_prompts_ad AFTER DELETE ON prompts
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;

-- ---------------------------------------------------------------- immutability (supersession)

-- Approved/Implemented ADRs: content is frozen; only supersession/disposition/telemetry
-- columns may change. Change of meaning = INSERT successor + set superseded_by.
CREATE TRIGGER trg_adrs_immutable BEFORE UPDATE ON adrs
  WHEN OLD.lifecycle_status IN ('Approved','Implemented')
   AND (NEW.title IS NOT OLD.title OR NEW.context IS NOT OLD.context
     OR NEW.decision IS NOT OLD.decision OR NEW.consequences IS NOT OLD.consequences)
  BEGIN SELECT RAISE(ABORT, 'approved ADRs are immutable: supersede, never edit'); END;

CREATE TRIGGER trg_acceptance_criteria_immutable BEFORE UPDATE ON acceptance_criteria
  WHEN OLD.lifecycle_status IN ('Approved','Implemented')
   AND (NEW.title IS NOT OLD.title OR NEW.statement IS NOT OLD.statement
     OR NEW.requirement_id IS NOT OLD.requirement_id OR NEW.slice_id IS NOT OLD.slice_id)
  BEGIN SELECT RAISE(ABORT, 'approved acceptance criteria are immutable: supersede, never edit'); END;

-- ---------------------------------------------------------------- requirement auto-advance (C5)

-- When every non-retired AC of a requirement has a Met verdict, an Approved requirement
-- advances to Implemented (Marid shipped v0.3.0 with 77/78 requirements still Draft).
CREATE TRIGGER trg_requirement_auto_advance AFTER INSERT ON audit_verdicts
  WHEN NEW.verdict = 'Met'
  BEGIN
    UPDATE requirements SET lifecycle_status = 'Implemented'
    WHERE id = (SELECT requirement_id FROM acceptance_criteria WHERE id = NEW.ac_id)
      AND lifecycle_status = 'Approved'
      AND NOT EXISTS (
        SELECT 1 FROM acceptance_criteria ac
        WHERE ac.requirement_id = requirements.id AND ac.retired_in IS NULL
          AND NOT EXISTS (SELECT 1 FROM audit_verdicts av
                          WHERE av.ac_id = ac.id AND av.verdict = 'Met'));
  END;

-- ---------------------------------------------------------------- derived views (C1: never stored)

CREATE VIEW v_identifier_counts AS
  SELECT entity_type, COUNT(*) AS n FROM entity_index GROUP BY entity_type;

CREATE VIEW v_artifact_membership AS
  SELECT et.type_id, et.generation_class,
         EXISTS (SELECT 1 FROM entity_index ei WHERE ei.entity_type = et.type_id) AS present,
         (SELECT reason FROM omissions o WHERE o.entity_type = et.type_id) AS omitted_reason
  FROM entity_types et;

CREATE VIEW v_backlog AS                                  -- 006: the backlog IS this query
  SELECT w.id, w.title, w.phase_id, w.slice_id, w.lifecycle_status
  FROM wbs_items w
  WHERE w.lifecycle_status NOT IN ('Implemented','Superseded','Obsolete','Rejected')
  ORDER BY w.phase_id, w.slice_id, w.id;

CREATE VIEW v_req_links AS                                -- helper: requirement -> linked entity types
  SELECT r.id AS req_id,
         (SELECT entity_type FROM entity_index
          WHERE id = CASE WHEN t.from_id = r.id THEN t.to_id ELSE t.from_id END) AS other_type
  FROM requirements r
  JOIN trace_edges t ON t.from_id = r.id OR t.to_id = r.id;

CREATE VIEW g_trace_failures AS                           -- G-TRACE as a view
  SELECT r.id FROM requirements r
  WHERE r.mvp = 1 AND r.retired_in IS NULL
    AND (NOT EXISTS (SELECT 1 FROM v_req_links l WHERE l.req_id = r.id
                       AND l.other_type IN ('decision','adr'))
      OR NOT EXISTS (SELECT 1 FROM v_req_links l WHERE l.req_id = r.id
                       AND l.other_type IN ('wbs-item','slice'))
      OR NOT EXISTS (SELECT 1 FROM v_req_links l WHERE l.req_id = r.id
                       AND l.other_type = 'test'));

CREATE VIEW g_set_failures AS                             -- G-SET as a view
  SELECT et.type_id FROM entity_types et
  WHERE et.generation_class = 'Always'
    AND NOT EXISTS (SELECT 1 FROM entity_index ei WHERE ei.entity_type = et.type_id)
    AND NOT EXISTS (SELECT 1 FROM omissions o WHERE o.entity_type = et.type_id);

CREATE VIEW g_progress_failures AS                        -- G-PROGRESS as a view
  SELECT ac.id FROM acceptance_criteria ac
  WHERE ac.retired_in IS NULL
    AND EXISTS (SELECT 1 FROM audit_verdicts)
    AND NOT EXISTS (SELECT 1 FROM audit_verdicts av WHERE av.ac_id = ac.id);

CREATE VIEW v_status_report AS
  SELECT 'requirements' AS family, lifecycle_status AS status, COUNT(*) AS n
    FROM requirements GROUP BY lifecycle_status
  UNION ALL SELECT 'decisions', lifecycle_status, COUNT(*) FROM decisions GROUP BY lifecycle_status
  UNION ALL SELECT 'risks', risk_state, COUNT(*) FROM risks GROUP BY risk_state
  UNION ALL SELECT 'acceptance_criteria', lifecycle_status, COUNT(*)
    FROM acceptance_criteria GROUP BY lifecycle_status
  UNION ALL SELECT 'wbs_items', lifecycle_status, COUNT(*) FROM wbs_items GROUP BY lifecycle_status
  UNION ALL SELECT 'deferred_work', status, COUNT(*) FROM deferred_work GROUP BY status
  UNION ALL SELECT 'defects', status, COUNT(*) FROM defects GROUP BY status;

CREATE VIEW v_readiness AS                                -- gate rollup for the readiness report
  SELECT 'G-TRACE' AS gate, COUNT(*) AS failures FROM g_trace_failures
  UNION ALL SELECT 'G-SET', COUNT(*) FROM g_set_failures
  UNION ALL SELECT 'G-PROGRESS', COUNT(*) FROM g_progress_failures;

CREATE VIEW v_phase_exit AS                               -- phase-exit report data (006 add-new, derived)
  SELECT p.id AS phase_id, p.title,
         (SELECT COUNT(*) FROM acceptance_criteria ac JOIN slices s ON ac.slice_id = s.id
           WHERE s.phase_id = p.id AND ac.retired_in IS NULL) AS acs_total,
         (SELECT COUNT(*) FROM acceptance_criteria ac JOIN slices s ON ac.slice_id = s.id
           WHERE s.phase_id = p.id AND ac.retired_in IS NULL
             AND EXISTS (SELECT 1 FROM audit_verdicts av
                         WHERE av.ac_id = ac.id AND av.verdict = 'Met')) AS acs_met,
         (SELECT COUNT(*) FROM defects d WHERE d.found_in = p.id
             AND d.status IN ('Open','In-progress')) AS open_defects
  FROM phases p;
