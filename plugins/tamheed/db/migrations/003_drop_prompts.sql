-- Migration 003 (v3.0.0, plan 027/B23) — prompts leave the database.
-- Handoff prompts are now .md files in <package>/prompts/ (the operator reads the
-- folder and picks); package_open converts a legacy data/prompts.jsonl once, loudly
-- (see tamheed_server._convert_legacy_prompts). DROP TABLE also drops the
-- trg_prompts_ai/ad triggers; entity_index is empty at migration time (migrations
-- run before the JSONL load) and no view references prompts (verified, plan 027).
-- IF EXISTS keeps re-application over an already-migrated schema harmless.
-- NOTE: schema.sql / 001_init.sql are frozen byte-twins; the stale 'prompt' mention
-- in their header comment (line 25) is frozen history — never edit 001.
DROP TABLE IF EXISTS prompts;
