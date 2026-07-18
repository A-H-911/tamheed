-- Migration 002 — the community-extension worked example (plan 015/B9).
--
-- This file doubles as the TEMPLATE for adding a new artifact family: one table
-- (TEXT primary key in the governed ID scheme, provenance columns, plus the two
-- columns every entity table carries — custom_attributes and last_referenced) and
-- the entity_index trigger pair that makes G-IDS hold for the new family.
--
-- The other half of the recipe lives in server/tamheed_server.py: one entry in
-- ENTITY_TABLES (tool routing) and one in BASELINE_ENTITY_TYPES (the registry row
-- seeded into new packages, carrying the ID prefix and generation class).
-- check.py's lint gate keeps registry <-> table map <-> DDL in sync — never exempt
-- an extension type from it. Migrations are append-only: never edit 001_init.sql
-- (schema.sql's frozen twin) or any shipped migration; the loader applies 002+ in
-- lexical order on every connect.

CREATE TABLE glossary_terms (
  id                TEXT PRIMARY KEY CHECK (id GLOB 'GT-[0-9]*'),
  term              TEXT NOT NULL,
  definition        TEXT,
  source_kind       TEXT CHECK (source_kind IN ('brief','clarification','code','inferred')),
  source_span       TEXT,
  custom_attributes TEXT,
  last_referenced   TEXT
);

CREATE TRIGGER trg_glossary_terms_ai AFTER INSERT ON glossary_terms
  BEGIN INSERT INTO entity_index(id, entity_type) VALUES (NEW.id, 'glossary-term'); END;
CREATE TRIGGER trg_glossary_terms_ad AFTER DELETE ON glossary_terms
  BEGIN DELETE FROM entity_index WHERE id = OLD.id; END;
