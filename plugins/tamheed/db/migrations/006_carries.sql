-- 006: the `carries` relation (plan 113, v5.0.0; the field's FB-018, findings_31).
--
-- `carries` (wbs-item -> deferred-work): the work item that carries an ACTIVATED deferred
-- row. Since v4.14 the `deferred-work-reviewed` advisory lists Open and Scheduled rows only,
-- on the doctrine that an Activated row "is work now — its WBS rows carry it". No typed
-- relation could say which rows carried it: `implements` targets requirements, decisions
-- and acceptance criteria; a deferred row was a legal target of the scope_* deltas alone.
-- "Carries" was prose, and the field measured the cost — two Activated rows whose only
-- carriers were Implemented work items were invisible to every rule. The edge makes the
-- sentence measurable: the `deferred-work-carried` advisory (server) lists Activated rows
-- with no OPEN carrier (Review counts as open), so a finished activation is a row to close.
-- `replan-deferred` writes the edge in the activating batch, beside the WBS rows.
--
-- Recreation is safe (the 002/004 precedent): migrations apply at connect() on a fresh
-- in-memory DB BEFORE the JSONL load, so the table is empty here; a package's stored
-- edges load unchanged. No operator step: `schema_version` reads 6 on the next open.

DROP TABLE trace_edges;
CREATE TABLE trace_edges (
  from_id           TEXT NOT NULL REFERENCES entity_index(id),
  to_id             TEXT NOT NULL REFERENCES entity_index(id),
  relation          TEXT NOT NULL CHECK (relation IN
    ('derives_from','mitigates','verifies','supersedes','blocked_by','implements',
     'satisfies','tests','discharges','scope_adds','scope_modifies','scope_removes',
     'learned_from','amends','carries','relates_to')),
  PRIMARY KEY (from_id, to_id, relation)
);
CREATE INDEX idx_trace_edges_to ON trace_edges(to_id);
