-- 002: the lessons-learned entity family (plan 035, v4.3.0).
-- LL- rows record what execution taught (kind: improve = a mistake and how to avoid
-- it; sustain = a practice that worked and must be repeated). Born Proposed by the
-- executing agent; ONLY operator-Approved lessons bind future sessions (the
-- Reflexion failure mode — persisting a wrong lesson — is screened by the operator
-- interview + G-INJECT at emission). Approved content is immutable: supersede,
-- never edit; pinned/lifecycle/superseded_by/custom_attributes/last_referenced stay
-- operator-mutable (curation and closure are not content edits).
-- Shape sources: NASA LLIS (driving event / lesson / recommendation), PMI lessons
-- register (category, continuous capture), US Army AAR (both polarities).

CREATE TABLE lessons (
  id                 TEXT PRIMARY KEY CHECK (id GLOB 'LL-[0-9]*'),
  title              TEXT NOT NULL,
  statement          TEXT NOT NULL,                      -- the lesson itself
  context            TEXT,                               -- the driving event (what happened)
  recommendation     TEXT,                               -- how to act on it
  rationale          TEXT,                               -- why the lesson holds
  kind               TEXT NOT NULL CHECK (kind IN ('improve','sustain')),
  category           TEXT,                               -- free-text retrieval key (PMI keywords)
  impact_if_followed TEXT,
  impact_if_ignored  TEXT,
  -- No Draft (the decisions pattern): a lesson is born Proposed, awaiting the
  -- operator's interview. Deferred is deliberately absent — an undecided lesson
  -- SHOULD keep nagging (lessons-confirmed advisory); Rejected is the decided-no.
  lifecycle_status   TEXT NOT NULL DEFAULT 'Proposed' CHECK (lifecycle_status IN
    ('Proposed','Approved','Rejected','Superseded','Obsolete')),
  recorded_at        TEXT,                               -- when the agent recorded it
  confirmed_by       TEXT,                               -- operator attribution, set at confirmation
  confirmed_at       TEXT,                               --   (facts about a person: never back-filled)
  pinned             INTEGER NOT NULL DEFAULT 0 CHECK (pinned IN (0, 1)),
  superseded_by      TEXT REFERENCES lessons(id),
  custom_attributes  TEXT,
  last_referenced    TEXT
);

CREATE TRIGGER trg_lessons_ai AFTER INSERT ON lessons
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'lesson'); END;
CREATE TRIGGER trg_lessons_ad AFTER DELETE ON lessons
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;

-- Content columns freeze at approval (the trg_adrs_immutable shape); pinned,
-- lifecycle_status, superseded_by, custom_attributes, last_referenced stay mutable.
CREATE TRIGGER trg_lessons_immutable BEFORE UPDATE ON lessons
  WHEN OLD.lifecycle_status = 'Approved'
   AND (NEW.title IS NOT OLD.title OR NEW.statement IS NOT OLD.statement
     OR NEW.context IS NOT OLD.context OR NEW.recommendation IS NOT OLD.recommendation
     OR NEW.rationale IS NOT OLD.rationale OR NEW.kind IS NOT OLD.kind
     OR NEW.category IS NOT OLD.category
     OR NEW.impact_if_followed IS NOT OLD.impact_if_followed
     OR NEW.impact_if_ignored IS NOT OLD.impact_if_ignored
     OR NEW.recorded_at IS NOT OLD.recorded_at
     OR NEW.confirmed_by IS NOT OLD.confirmed_by
     OR NEW.confirmed_at IS NOT OLD.confirmed_at)
  BEGIN SELECT RAISE(ABORT, 'approved lessons are immutable: supersede, never edit'); END;

-- trace_edges gains the learned_from relation (lesson -> its source). SQLite cannot
-- ALTER a CHECK; the recreation is safe because migrations apply at connect() on a
-- fresh in-memory DB BEFORE the JSONL load — the table is always empty here, and it
-- carries no triggers (verified at plan 035). Same PK/FKs; the index is recreated.
DROP TABLE trace_edges;
CREATE TABLE trace_edges (
  from_id           TEXT NOT NULL REFERENCES entity_index(id),
  to_id             TEXT NOT NULL REFERENCES entity_index(id),
  relation          TEXT NOT NULL CHECK (relation IN
    ('derives_from','mitigates','verifies','supersedes','blocked_by','implements',
     'satisfies','tests','discharges','scope_adds','scope_modifies','scope_removes',
     'learned_from','relates_to')),
  PRIMARY KEY (from_id, to_id, relation)
);
CREATE INDEX idx_trace_edges_to ON trace_edges(to_id);
