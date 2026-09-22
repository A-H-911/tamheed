-- 005: the `feedback` family - upstream feedback and local tools on the operator's word
-- (plan 087, v4.11.0; maintainer rulings 2026-09-22 after ACMP's findings_27 cycle).
--
-- WHY. The field built its own utilities around the package (slate generators over
-- exports/, a JSONL-reading id resolver, scratch probes) because tamheed lacked four
-- functions and nothing told upstream. A capability the plugin lacks, a defect in it, a
-- doc error, a question - or a LOCAL TOOL the project keeps over the package - is now a
-- row in the package: exported with `entity_export("feedback")`, named by `handoff_emit`
-- while it awaits the operator, collected by the maintainer from the field's findings.
--
-- ON THE OPERATOR'S WORD. A row is born Proposed (the agent's draft; it binds nothing and
-- leaves the package nowhere). It becomes Confirmed only with `operator_confirm` on the
-- write - the lessons guard, applied to what the project tells upstream and to what it
-- keeps. A `local-tool` row is refused at INSERT without `operator_confirm`: a tool over
-- the package exists only on the operator's word, reads `exports/` only and writes
-- nowhere tool-owned. Those guards live in the server (plan 087); the table holds the
-- vocabulary. Feedback rows QUOTE broken ids by nature (`SEC-8`, `DEC-208`), so the
-- table is exempt from the prose-id scan, like the journal.
--
-- Recreation is safe: migrations apply at connect() on a fresh in-memory DB BEFORE the
-- JSONL load, so the table is empty here (the 002/003 precedent); a package that predates
-- this migration has no feedback.jsonl and the load skips it.

CREATE TABLE feedback (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'FB-[0-9]*'),
  kind              TEXT NOT NULL CHECK (kind IN
    ('missing-capability','defect','doc-error','question','local-tool')),
  title             TEXT NOT NULL,
  detail            TEXT,                                -- what was needed, what happened
  workaround        TEXT,                                -- what the agent did INSTEAD (the column that catches side tools)
  tool_path         TEXT,                                -- a local-tool row names its file
  tool_or_rule      TEXT,                                -- the tamheed tool / rule / doc concerned
  plugin_version    TEXT,                                -- server_info().version when recorded
  lifecycle_status  TEXT NOT NULL DEFAULT 'Proposed' CHECK (lifecycle_status IN
    ('Proposed','Confirmed','Reported','Resolved','Rejected')),
  confirmed_by      TEXT,
  confirmed_at      TEXT,
  resolved_in       TEXT,                                -- the plugin version that answered it
  upstream_ref      TEXT,                                -- the maintainer's plan / findings pointer
  recorded_at       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (kind <> 'local-tool' OR tool_path IS NOT NULL)  -- a tool row without its file is not a register
);

CREATE TRIGGER trg_feedback_ai AFTER INSERT ON feedback
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'feedback'); END;
CREATE TRIGGER trg_feedback_ad AFTER DELETE ON feedback
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
