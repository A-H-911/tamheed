-- 012_standup_withdraw.sql (plan 246, v6.7): a recorded standup report can be withdrawn
-- (ADR-0004, which supersedes ADR-0003's clause that a recorded report never leaves).
--
-- The operator asked to withdraw a report. A report that nothing depends on can leave the
-- record: the newest daily report, or an override report. A correction cannot, because its
-- place in the chain would stay empty. A report that a later report names as its base, or
-- that has a same-seq twin, cannot either. The tool checks every row that names the report
-- before the delete, and the journal keeps a note of the withdrawal. Git history keeps the
-- removed row. A recorded report is still never EDITED: trg_standup_reports_immutable holds.
--
-- Triggers only: no table and no column changes, so no stored file changes and an older
-- release opens the same store. The trigger keeps its name, so the guide keeps one entry.
DROP TRIGGER trg_standup_reports_keep;
CREATE TRIGGER trg_standup_reports_keep BEFORE DELETE ON standup_reports
  WHEN OLD.lifecycle_status <> 'Draft' AND (
    OLD.lifecycle_status <> 'Approved' OR OLD.supersedes IS NOT NULL
    OR EXISTS (SELECT 1 FROM standup_reports r WHERE r.id <> OLD.id
               AND (r.base_report = OLD.id OR r.supersedes = OLD.id))
    OR (OLD.kind = 'default' AND EXISTS (SELECT 1 FROM standup_reports r WHERE r.id <> OLD.id
               AND r.kind = 'default' AND r.seq >= OLD.seq)))
  BEGIN SELECT RAISE(ABORT, 'only a draft, or a recorded report that nothing depends on, can be removed: the newest daily report or an override report'); END;
