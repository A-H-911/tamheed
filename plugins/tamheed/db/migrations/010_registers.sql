-- 010_registers.sql (plan 226, v6.5): project registers.
--
-- A project keeps record types that the plugin has no family for: a source authorization, an
-- evidence finding, an interview topic. One field stored three such registers as dependency,
-- section and open-question rows with their fields in `custom_attributes`. Nothing checked the
-- fields, the rows filled registers that mean something else, and a section had no status.
--
-- Two families, and no rule of any one project in the plugin:
--   registers         REG-  the register itself. It DECLARES its fields.
--   register_entries  ENT-  one row per record. Its field values are checked at write.
--
-- The declaration lives under the register's `custom_attributes.fields`: a list of
-- {name, required?, values?, refs?}. An entry's values live in its own `custom_attributes`.
-- No new JSON column: the content gate grades every other TEXT column (an allowed value such
-- as `TBD` would fail it), and the engine already reads and writes `custom_attributes` as JSON.
-- The write guard and the advisory `register-entries-conform` are in the server.
--
-- Both families are On-request, so no existing package fails G-SET. A package written before
-- this release learns them through package_migrate's staged registry-sync.

CREATE TABLE registers (
  id                TEXT NOT NULL PRIMARY KEY CHECK (id GLOB 'REG-[0-9]*'),
  title             TEXT NOT NULL,
  purpose           TEXT,                                -- what one entry records, and why
  lifecycle_status  TEXT NOT NULL DEFAULT 'Draft' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,                                -- holds `fields`, the declaration
  last_referenced   TEXT,
  CHECK (source_span IS NULL OR source_kind IS NOT NULL)
);

CREATE TABLE register_entries (
  id                TEXT NOT NULL PRIMARY KEY CHECK (id GLOB 'ENT-[0-9]*'),
  register_id       TEXT NOT NULL REFERENCES registers(id),
  title             TEXT NOT NULL,
  body              TEXT,                                -- free prose about the record
  lifecycle_status  TEXT NOT NULL DEFAULT 'Proposed' CHECK (lifecycle_status IN
    ('Draft','Proposed','Approved','Rejected','Deferred','Implemented','Superseded','Obsolete')),
  custom_attributes TEXT,                                -- the declared fields' values
  last_referenced   TEXT
);

CREATE INDEX idx_register_entries_register ON register_entries(register_id);

CREATE TRIGGER trg_registers_ai AFTER INSERT ON registers
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'register'); END;
CREATE TRIGGER trg_registers_ad AFTER DELETE ON registers
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
CREATE TRIGGER trg_register_entries_ai AFTER INSERT ON register_entries
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'register-entry'); END;
CREATE TRIGGER trg_register_entries_ad AFTER DELETE ON register_entries
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
