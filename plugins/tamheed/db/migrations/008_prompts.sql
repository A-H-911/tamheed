-- 008: the `prompts` family - project prompts return to the store as rows (plan 192,
-- v6.0.0; the operator's ruling of 2026-10-04 after the user-guide review).
--
-- WHY. Since v3 (plan 027) the kickoff, per-phase and situational prompts an executing
-- agent starts from were `.md` files in `<package>/prompts/`, so that "the operator reads
-- the folder and picks" from a stock library. That library became the plugin's slash
-- skills in v5.0.0. In the field the kickoff file shrank, by its own rules, to pointers
-- that restate the SessionStart hook and `/tamheed:orient-resume`, and the other project
-- prompt files were each the project-specific half of one scenario skill. A file carries
-- no status, no provenance, no binding to the skill it serves, and nothing in the record
-- names it. A row carries all four: the operator approves it, the review page shows it,
-- `prompt-ids-resolve` and `prose-plain-english` read it, G-INJECT screens it, and
-- `plugin_skill` binds it to the scenario skill that reads it.
--
-- SHAPE. `kind` is kickoff (the one `packages.entry_point` names; `handoff_emit` demands
-- it Approved), phase (one per phase gate, `phase_id` set) or situational. `plugin_skill`
-- names the plugin's scenario skill the row accompanies; the server refuses a name that
-- is not a bundled skill. Approved rows are edited in place (the requirements class), so
-- there is no supersession column and no immutability trigger. The SRC block carries the
-- provenance a migration writes for a converted file.
--
-- Recreation is safe (the 002/003/005 precedent): migrations apply at connect() on a
-- fresh in-memory DB BEFORE the JSONL load, so the table is empty here. A package that
-- predates this migration has no prompts.jsonl and the load skips it; `package_migrate`
-- converts its prompt files into rows on the operator's word.

CREATE TABLE prompts (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'PRT-[0-9]*'),
  kind              TEXT NOT NULL CHECK (kind IN ('kickoff','phase','situational')),
  title             TEXT NOT NULL,
  body              TEXT NOT NULL,
  phase_id          TEXT REFERENCES phases(id),           -- a `phase` prompt names its gate
  plugin_skill      TEXT,                                 -- the scenario skill that reads this row
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  disposition       TEXT CHECK (disposition IN ('superseded','accepted-with-deviation','void')),
  disposition_reason_ref TEXT REFERENCES entity_index(id),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT,
  CHECK (disposition IS NULL OR disposition_reason_ref IS NOT NULL),
  CHECK (source_span IS NULL OR source_kind IS NOT NULL)
);

CREATE TRIGGER trg_prompts_ai AFTER INSERT ON prompts
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'prompt'); END;
CREATE TRIGGER trg_prompts_ad AFTER DELETE ON prompts
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
