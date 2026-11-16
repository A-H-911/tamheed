-- 012_standup_withdraw.sql (plan 246, v6.7): a recorded standup report can be withdrawn
-- (ADR-0004, which supersedes ADR-0003's clause that a recorded report never leaves).
--
-- The operator asked to withdraw a report. The newest place in the chain can leave the record
-- whole: the newest daily report together with every report it corrects (R144), or an override
-- report with the reports it corrects. A report that another report names as its base stays,
-- and so does a report with a later daily report. A correction leaves only after the report it
-- corrects, and that report cannot leave first on its own: its correction names it, and the
-- foreign key refuses. So the place leaves only whole, inside one transaction whose foreign
-- keys are checked at its end: the tool removes the oldest report of the place first. The tool
-- checks every row that names a report before the delete, and the journal keeps a note of each
-- withdrawal. Git history keeps the removed rows. A recorded report is still never EDITED:
-- trg_standup_reports_immutable holds.
--
-- Triggers only: no table and no column changes, so no stored file changes and an older
-- release opens the same store. The trigger keeps its name, so the guide keeps one entry.
DROP TRIGGER trg_standup_reports_keep;
CREATE TRIGGER trg_standup_reports_keep BEFORE DELETE ON standup_reports
  WHEN OLD.lifecycle_status <> 'Draft' AND (
    EXISTS (SELECT 1 FROM standup_reports r WHERE r.id <> OLD.id AND r.base_report = OLD.id)
    OR (OLD.supersedes IS NOT NULL
        AND EXISTS (SELECT 1 FROM standup_reports o WHERE o.id = OLD.supersedes))
    OR (OLD.kind = 'default' AND EXISTS (SELECT 1 FROM standup_reports r WHERE r.id <> OLD.id
            AND r.kind = 'default' AND r.seq > OLD.seq)))
  BEGIN SELECT RAISE(ABORT, 'only a draft, or a recorded report that nothing depends on, can be removed: the newest place in the chain, whole, or an override report'); END;
