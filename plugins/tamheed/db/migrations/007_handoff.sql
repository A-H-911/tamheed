-- 007: the `handoff` journal event + `skills.upstreamed_to` (plans 121/122, v5.1.0; the
-- field's findings_32 and FB-020).
--
-- `handoff` (caller-written): the typed place for "where this session stopped" — resume
-- point, in-flight ids, what awaits the operator, the verified facts with the query that
-- measured each, what NOT to carry. Before this kind a project carried that state in
-- prose `note` entries and in a 3,600-line kickoff prompt that went stale on every write.
-- The server returns the latest `handoff` (with its `correction` chain) in the `resume`
-- block of `package_open` / `server_info`, the SessionStart hook prints it, and the
-- `handoff-current` advisory names a handoff that is behind the journal. A stale
-- handoff is corrected (`corrects`), never edited — the journal stays append-only.
--
-- `skills.upstreamed_to`: where a retired PROJECT skill's content now lives when it was
-- absorbed by a plugin skill (a name such as `tamheed:package-writes`). `superseded_by`
-- can only name another SKL- row; a plugin skill has none. With the pointer set, the
-- `lessons-stranded` advisory stops naming the Promoted lessons the retired row carries.
-- Nullable; every existing package's skills.jsonl gains `"upstreamed_to": null` on its
-- first flush (CANONICAL rule 4: every column serialises) — the one-time rewrite the
-- 4.4.0 lessons column also caused.
--
-- Recreation is safe (the 002/004/006 precedent): migrations apply at connect() on a
-- fresh in-memory DB BEFORE the JSONL load, so the table is empty here. No operator
-- step: `schema_version` reads 7 on the next open.

DROP TABLE progress_entries;
CREATE TABLE progress_entries (                          -- append-only journal, typed events (plan 031)
  id                TEXT PRIMARY KEY CHECK (id GLOB 'PE-[0-9]*'),
  event_type        TEXT NOT NULL DEFAULT 'note' CHECK (event_type IN
    ('work-done','verdict-recorded','transition','forced-override','gate-decision',
     'escalation','correction','note','lesson-confirmed','lesson-promoted',
     'integrity-verified','handoff')),
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

ALTER TABLE skills ADD COLUMN upstreamed_to TEXT;        -- the plugin skill that absorbed a retired row
