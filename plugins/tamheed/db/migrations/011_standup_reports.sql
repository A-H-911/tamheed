-- 011_standup_reports.sql (plan 232, v6.6): the standup report, a stored record (ADR-0003).
--
-- A standup report answers three questions for one window of work: what we did, the
-- challenges and decisions, and what we expect to do next. The store keeps current state
-- only, so "what changed" cannot be read back later. Each report row therefore keeps the
-- CHANGES of its window (`state_delta`). The first report, and every 30th one, is a
-- checkpoint that keeps the full state. The state at any report is a replay of the recorded
-- rows from the latest checkpoint, and each row's `state_digest` lets the replay check every
-- link. ADR-0003 supersedes ADR-0001's "never stored snapshots" clause for this family only.
--
-- One family, written by the `standup_report` tool only (entity_upsert refuses it):
--   standup_reports  RPT-  Draft -> Approved (recorded on the operator's word) -> Superseded
--
-- `kind`: a default report starts where the latest recorded default report ended. An
-- override report starts earlier (the operator named a date or a report). It is recorded,
-- but it never starts the next window and the replay never reads it.
-- `pe_to` / `av_to`: the highest journal and verdict numbers when the draft was made. The
-- window end is fixed at draft time, never at record time.
-- `facts`: what the page prints, frozen at draft (ids and titles). `narrative`: the agent's
-- words. The JSON columns are never graded by G-COMPLETE (the server's _REPORT_COLUMNS).
--
-- The family is On-request, so no existing package fails G-SET. A package written before
-- this release learns it through package_migrate's staged registry-sync.

CREATE TABLE standup_reports (
  id                TEXT NOT NULL PRIMARY KEY CHECK (id GLOB 'RPT-[0-9]*'),
  kind              TEXT NOT NULL DEFAULT 'default' CHECK (kind IN ('default','override')),
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Approved','Superseded')),
  base_report       TEXT REFERENCES standup_reports(id),   -- whose end starts this window; NULL = birth
  supersedes        TEXT REFERENCES standup_reports(id),   -- set on the correction; the old row only changes status
  checkpoint        INTEGER NOT NULL DEFAULT 0 CHECK (checkpoint IN (0, 1)),
  pe_to             INTEGER NOT NULL CHECK (pe_to >= 0),
  av_to             INTEGER NOT NULL CHECK (av_to >= 0),
  ended_at          TEXT NOT NULL,                          -- UTC 'YYYY-MM-DDTHH:MM:SSZ' of the draft
  utc_offset        TEXT NOT NULL CHECK (utc_offset GLOB '[+-][0-1][0-9]:[0-5][0-9]'),
  state_digest      TEXT NOT NULL,                          -- sha256 of the state the draft saw
  state_delta       TEXT NOT NULL,                          -- JSON: the window's changes (full state on a checkpoint)
  facts             TEXT NOT NULL,                          -- JSON: what the page prints, frozen at draft
  narrative         TEXT,                                   -- JSON: the agent's words; NULL until attached
  rule_colour       TEXT NOT NULL CHECK (rule_colour IN ('green','amber','red')),
  colour            TEXT CHECK (colour IN ('green','amber','red')),   -- the operator's confirmed colour
  recorded_by       TEXT,
  operator_words    TEXT,                                   -- stored and journaled, never printed
  recorded_at       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (supersedes IS NULL OR supersedes <> id),
  CHECK (base_report IS NULL OR base_report <> id),
  CHECK (lifecycle_status = 'Draft' OR (trim(COALESCE(narrative, '')) <> '' AND colour IS NOT NULL
         AND recorded_at IS NOT NULL AND trim(COALESCE(recorded_by, '')) <> ''
         AND trim(COALESCE(operator_words, '')) <> ''))
);

-- One live draft per package (SR24), and one recorded default report per chain link.
CREATE UNIQUE INDEX idx_standup_reports_one_draft ON standup_reports(lifecycle_status)
  WHERE lifecycle_status = 'Draft';
CREATE UNIQUE INDEX idx_standup_reports_chain ON standup_reports(pe_to)
  WHERE kind = 'default' AND lifecycle_status = 'Approved';

CREATE TRIGGER trg_standup_reports_ai AFTER INSERT ON standup_reports
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'standup-report'); END;
CREATE TRIGGER trg_standup_reports_ad AFTER DELETE ON standup_reports
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;

-- A recorded report is immutable (SR23). The only move after Draft is Approved ->
-- Superseded, and `last_referenced` stays writable because work_bind stamps every table.
-- A test checks that this trigger names every column but those two.
CREATE TRIGGER trg_standup_reports_immutable BEFORE UPDATE ON standup_reports
  WHEN OLD.lifecycle_status <> 'Draft'
   AND (NEW.id IS NOT OLD.id OR NEW.kind IS NOT OLD.kind
     OR NEW.base_report IS NOT OLD.base_report OR NEW.supersedes IS NOT OLD.supersedes
     OR NEW.checkpoint IS NOT OLD.checkpoint OR NEW.pe_to IS NOT OLD.pe_to
     OR NEW.av_to IS NOT OLD.av_to OR NEW.ended_at IS NOT OLD.ended_at
     OR NEW.utc_offset IS NOT OLD.utc_offset OR NEW.state_digest IS NOT OLD.state_digest
     OR NEW.state_delta IS NOT OLD.state_delta OR NEW.facts IS NOT OLD.facts
     OR NEW.narrative IS NOT OLD.narrative OR NEW.rule_colour IS NOT OLD.rule_colour
     OR NEW.colour IS NOT OLD.colour OR NEW.recorded_by IS NOT OLD.recorded_by
     OR NEW.operator_words IS NOT OLD.operator_words OR NEW.recorded_at IS NOT OLD.recorded_at
     OR NEW.custom_attributes IS NOT OLD.custom_attributes
     OR NOT (NEW.lifecycle_status = OLD.lifecycle_status
             OR (OLD.lifecycle_status = 'Approved' AND NEW.lifecycle_status = 'Superseded')))
  BEGIN SELECT RAISE(ABORT, 'a recorded standup report is immutable: correct it with a new report that supersedes it'); END;

-- A recorded report is superseded only by a correction that names it, so a chain link is
-- never left empty. The correction's draft names it first; then the old row moves; then the
-- draft is recorded, in one transaction.
CREATE TRIGGER trg_standup_reports_successor BEFORE UPDATE OF lifecycle_status ON standup_reports
  WHEN OLD.lifecycle_status = 'Approved' AND NEW.lifecycle_status = 'Superseded'
   AND NOT EXISTS (SELECT 1 FROM standup_reports WHERE supersedes = OLD.id AND id <> OLD.id)
  BEGIN SELECT RAISE(ABORT, 'a recorded standup report is superseded only by a correction that names it in supersedes'); END;

CREATE TRIGGER trg_standup_reports_draft_moves BEFORE UPDATE OF lifecycle_status ON standup_reports
  WHEN OLD.lifecycle_status = 'Draft' AND NEW.lifecycle_status NOT IN ('Draft', 'Approved')
  BEGIN SELECT RAISE(ABORT, 'a draft standup report is recorded (Approved) or discarded, never superseded'); END;

CREATE TRIGGER trg_standup_reports_keep BEFORE DELETE ON standup_reports
  WHEN OLD.lifecycle_status <> 'Draft'
  BEGIN SELECT RAISE(ABORT, 'only a draft standup report can be discarded'); END;
