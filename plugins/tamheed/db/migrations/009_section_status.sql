-- 009_section_status.sql (plan 225, v6.5): a document section can be retired.
--
-- A section had no lifecycle column, so a section that a later one replaced stayed in every
-- scan for good: the content gate graded its text, and the prose-id rule read its ids. The
-- field stored records as sections and could not retire a duplicate.
--
-- One nullable column, appended (the 007 pattern: the JSONL key lands last, and each
-- package's document_sections.jsonl re-serialises once). Empty means LIVE: a section follows
-- its document, and it takes a status only to leave. The column is nullable by necessity. The
-- loader binds an explicit NULL for a column that an older row lacks, so NOT NULL would
-- refuse every package written before this release.
--
-- The kept section is named by a `supersedes` trace edge (same-type rule). No row leaves the
-- store.

ALTER TABLE document_sections ADD COLUMN lifecycle_status TEXT
  CHECK (lifecycle_status IN ('Superseded','Obsolete'));
