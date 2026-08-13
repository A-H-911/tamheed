-- Migration 004 (v3.0.0, plan 027/B23) — readiness views, latest-verdict semantics.
--
-- Two flaws fixed in one move:
--   1. v_phase_exit counted an AC as met on ANY 'Met' verdict EVER (EXISTS) — verdicts
--      APPEND, so an AC re-judged Not-met still counted met.
--   2. "latest" computed by string ORDER BY id misorders past 1000 rows (AV-1000 sorts
--      before AV-999 as text; plan 025 made ids past 999 reachable) — the shared
--      v_latest_verdicts view orders NUMERICALLY.
-- v_slice_exit is new: the slice-scope readiness substrate (readiness_check).
-- Idempotent via DROP VIEW IF EXISTS; user_version is stamped by store.py.

DROP VIEW IF EXISTS v_latest_verdicts;
CREATE VIEW v_latest_verdicts AS                          -- ac_id -> its LATEST verdict
  SELECT av.ac_id, av.verdict, av.evidence
  FROM audit_verdicts av
  WHERE av.id = (SELECT av2.id FROM audit_verdicts av2 WHERE av2.ac_id = av.ac_id
                 ORDER BY CAST(SUBSTR(av2.id, 4) AS INTEGER) DESC LIMIT 1);

DROP VIEW IF EXISTS v_phase_exit;
CREATE VIEW v_phase_exit AS                               -- phase-exit report data
  SELECT p.id AS phase_id, p.title,
         (SELECT COUNT(*) FROM acceptance_criteria ac JOIN slices s ON ac.slice_id = s.id
           WHERE s.phase_id = p.id AND ac.retired_in IS NULL) AS acs_total,
         (SELECT COUNT(*) FROM acceptance_criteria ac JOIN slices s ON ac.slice_id = s.id
           JOIN v_latest_verdicts lv ON lv.ac_id = ac.id
           WHERE s.phase_id = p.id AND ac.retired_in IS NULL
             AND lv.verdict = 'Met') AS acs_met,
         (SELECT COUNT(*) FROM defects d WHERE d.found_in = p.id
             AND d.status IN ('Open','In-progress')) AS open_defects
  FROM phases p;

DROP VIEW IF EXISTS v_slice_exit;
CREATE VIEW v_slice_exit AS                               -- slice-scope readiness data
  SELECT s.id AS slice_id, s.title, s.phase_id,
         (SELECT COUNT(*) FROM acceptance_criteria ac
           WHERE ac.slice_id = s.id AND ac.retired_in IS NULL) AS acs_total,
         (SELECT COUNT(*) FROM acceptance_criteria ac
           JOIN v_latest_verdicts lv ON lv.ac_id = ac.id
           WHERE ac.slice_id = s.id AND ac.retired_in IS NULL
             AND lv.verdict = 'Met') AS acs_met,
         (SELECT COUNT(*) FROM wbs_items w WHERE w.slice_id = s.id
           AND w.lifecycle_status NOT IN
               ('Implemented','Superseded','Obsolete','Rejected')) AS wbs_open,
         (SELECT COUNT(*) FROM defects d WHERE d.found_in = s.id
             AND d.status IN ('Open','In-progress')) AS open_defects
  FROM slices s;
