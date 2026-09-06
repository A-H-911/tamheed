-- 004: the `amends` relation + the `integrity-verified` journal event (plan 039, v4.5.0,
-- findings_22 / field-evidence C43).
--
-- `amends` (scope-change -> decision | adr): a scope change that carves an exception
-- out of a RULING, narrows a standing rule, or re-scopes a decision's applicability.
-- The scope_* deltas stay plan-only (a ruling is not a plan row); before this relation
-- such edges collapsed to relates_to — the untyped bucket — and the scope-changes-merged
-- advisory could not see them (ACMP carried three). Merge semantics live in the server
-- and the teaching surfaces: a DEC- target merges by full-row upsert of the ruling; an
-- ADR- target merges by SUPERSESSION (ADRs are immutable — the successor ADR is the
-- merge).
--
-- `integrity-verified`: appended by package_verify(record=true) ONLY (actor
-- system:package-verify) — the canonical round-trip digest becomes a citable journal
-- fact instead of an undocumented property. Server-only: progress_update refuses it
-- (with forced-override / lesson-confirmed / lesson-promoted) so a narrated "verified"
-- can never be journaled by hand (the C7 hole in a new column).
--
-- Recreations are safe (the 002/003 precedent): migrations apply at connect() on a
-- fresh in-memory DB BEFORE the JSONL load, so both tables are empty here.

DROP TABLE trace_edges;
CREATE TABLE trace_edges (
  from_id           TEXT NOT NULL REFERENCES entity_index(id),
  to_id             TEXT NOT NULL REFERENCES entity_index(id),
  relation          TEXT NOT NULL CHECK (relation IN
    ('derives_from','mitigates','verifies','supersedes','blocked_by','implements',
     'satisfies','tests','discharges','scope_adds','scope_modifies','scope_removes',
     'learned_from','amends','relates_to')),
  PRIMARY KEY (from_id, to_id, relation)
);
CREATE INDEX idx_trace_edges_to ON trace_edges(to_id);

DROP TABLE progress_entries;
CREATE TABLE progress_entries (                          -- append-only journal, typed events (plan 031)
  id                TEXT PRIMARY KEY CHECK (id GLOB 'PE-[0-9]*'),
  event_type        TEXT NOT NULL DEFAULT 'note' CHECK (event_type IN
    ('work-done','verdict-recorded','transition','forced-override','gate-decision',
     'escalation','correction','note','lesson-confirmed','lesson-promoted',
     'integrity-verified')),
  entry             TEXT NOT NULL,
  subject_id        TEXT REFERENCES entity_index(id),
  actor             TEXT,
  corrects          TEXT REFERENCES progress_entries(id),
  phase_id          TEXT REFERENCES phases(id),
  slice_id          TEXT REFERENCES slices(id),
  occurred_at       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TRIGGER trg_progress_entries_ai AFTER INSERT ON progress_entries
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'progress-entry'); END;
CREATE TRIGGER trg_progress_entries_ad AFTER DELETE ON progress_entries
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
