-- 003: lesson -> skill promotion + the confirm-guard substrate (plan 036, v4.4.0).
-- Skills are PROCEDURAL memory distilled from declarative lessons in an operator
-- interview (Voyager's skill library; Soar's chunking; ECC's instinct->skill
-- promotion with human confirmation). A skill row holds METADATA + provenance
-- only — the BODY lives solely in the written SKILL.md file (project level:
-- <target-repo>/.claude/skills/<name>/SKILL.md, the default; user level:
-- ~/.claude/skills/<name>/SKILL.md), operator-owned after creation — the v3
-- files-doctrine: the server never writes or reads skill files.
-- Recreations below are safe: migrations apply at connect() on a fresh in-memory
-- DB BEFORE the JSONL load, so every table is empty here (the 002 precedent).
-- Order matters: skills FIRST — lessons.promoted_to references it.

CREATE TABLE skills (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'SKL-[0-9]*'),
  name              TEXT NOT NULL,                       -- kebab-case; the skill folder name
  title             TEXT NOT NULL,
  description       TEXT,                                -- the frontmatter trigger (WHEN it fires)
  level             TEXT NOT NULL DEFAULT 'project' CHECK (level IN ('project','user')),
  target_path       TEXT,                                -- where the SKILL.md was written
  -- Born Approved out of the operator interview (the interview IS the approval);
  -- a re-distilled skill supersedes its predecessor. Domain lifecycle (the
  -- defect/deferred-work pattern). Rows stay mutable — metadata, not content;
  -- the operator owns the FILE.
  lifecycle_status  TEXT NOT NULL DEFAULT 'Approved' CHECK (lifecycle_status IN
    ('Approved','Superseded','Obsolete')),
  superseded_by     TEXT REFERENCES skills(id),
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TRIGGER trg_skills_ai AFTER INSERT ON skills
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'skill'); END;
CREATE TRIGGER trg_skills_ad AFTER DELETE ON skills
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;

-- lessons gains the Promoted state (Approved -> Promoted only, confirm-guarded in
-- the server) and the promotion link. Content stays FROZEN in Promoted — without
-- extending the trigger's WHEN, promotion would re-open the one-write-too-late
-- class findings_19 §2 taught (immutability must cover every bound state), and a
-- Promoted row's promoted_to freezes too (re-pointing a recorded promotion is an
-- edit of the record).
DROP TABLE lessons;
CREATE TABLE lessons (
  id                 TEXT PRIMARY KEY CHECK (id GLOB 'LL-[0-9]*'),
  title              TEXT NOT NULL,
  statement          TEXT NOT NULL,
  context            TEXT,
  recommendation     TEXT,
  rationale          TEXT,
  kind               TEXT NOT NULL CHECK (kind IN ('improve','sustain')),
  category           TEXT,
  impact_if_followed TEXT,
  impact_if_ignored  TEXT,
  lifecycle_status   TEXT NOT NULL DEFAULT 'Proposed' CHECK (lifecycle_status IN
    ('Proposed','Approved','Promoted','Rejected','Superseded','Obsolete')),
  recorded_at        TEXT,
  confirmed_by       TEXT,
  confirmed_at       TEXT,
  pinned             INTEGER NOT NULL DEFAULT 0 CHECK (pinned IN (0, 1)),
  promoted_to        TEXT REFERENCES skills(id),         -- the DEC- -> ADR- promotion idiom
  superseded_by      TEXT REFERENCES lessons(id),
  custom_attributes  TEXT,
  last_referenced    TEXT
);

CREATE TRIGGER trg_lessons_ai AFTER INSERT ON lessons
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'lesson'); END;
CREATE TRIGGER trg_lessons_ad AFTER DELETE ON lessons
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;

CREATE TRIGGER trg_lessons_immutable BEFORE UPDATE ON lessons
  WHEN (OLD.lifecycle_status IN ('Approved','Promoted')
   AND (NEW.title IS NOT OLD.title OR NEW.statement IS NOT OLD.statement
     OR NEW.context IS NOT OLD.context OR NEW.recommendation IS NOT OLD.recommendation
     OR NEW.rationale IS NOT OLD.rationale OR NEW.kind IS NOT OLD.kind
     OR NEW.category IS NOT OLD.category
     OR NEW.impact_if_followed IS NOT OLD.impact_if_followed
     OR NEW.impact_if_ignored IS NOT OLD.impact_if_ignored
     OR NEW.recorded_at IS NOT OLD.recorded_at
     OR NEW.confirmed_by IS NOT OLD.confirmed_by
     OR NEW.confirmed_at IS NOT OLD.confirmed_at))
   OR (OLD.lifecycle_status = 'Promoted'
       AND NEW.promoted_to IS NOT OLD.promoted_to)
  BEGIN SELECT RAISE(ABORT,
    'approved/promoted lessons are immutable: supersede, never edit'); END;

-- The typed journal gains the lesson-guard events (server-appended, the
-- forced-override pattern).
DROP TABLE progress_entries;
CREATE TABLE progress_entries (                          -- append-only journal, typed events (plan 031)
  id                TEXT PRIMARY KEY CHECK (id GLOB 'PE-[0-9]*'),
  event_type        TEXT NOT NULL DEFAULT 'note' CHECK (event_type IN
    ('work-done','verdict-recorded','transition','forced-override','gate-decision',
     'escalation','correction','note','lesson-confirmed','lesson-promoted')),
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
