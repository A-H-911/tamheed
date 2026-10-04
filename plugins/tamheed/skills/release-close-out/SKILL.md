---
name: release-close-out
description: >-
  Invoke to close out a release at package scope, blocking-clean. Every blocking readiness failure
  is resolved, expired waivers are renewed on the operator's words, human gates are decided, then
  release notes and bindings.
disable-model-invocation: true
argument-hint: "[package]"
---

# Release close-out: package scope, blocking-clean

Invoke this (`/tamheed:release-close-out`) to close out a release of `<package>` (semi-auto: forced
transitions and human gates need your explicit words).

---

> `<package>` below is the package this project's `CLAUDE.md` Tamheed note names; an argument to
> the slash command names another (`$ARGUMENTS`). Recording obligations: the note's table.
Close out the release against the `<package>` Tamheed package:

1. `package_open("<package>")` if not already open.
   Then read the prompt rows bound to this skill: `entity_query("prompt", status="Approved", plugin_skill="release-close-out")`. Each carries what is true of this project for this ceremony.
2. `readiness_check("package")`. Resolve EVERY blocking failure before anything else:
   - decisions/ADRs still Proposed/Draft → approve, reject, or supersede them (the
     close cannot rest on proposed decisions).
   - ACs whose latest verdict is not Met → verify and `audit_record` with evidence
     plus `verified_by`/`verification_method`/`against_commit`, or retire/supersede
     deliberately.
   - open critical/high defects → fix, disposition, or convert to `deferred-work`
     (a `scope-change` first if that changes scope). Medium/low only surface as the
     defects-minor advisory. Decide each, never downgrade severity to pass.
   - undischarged risks → discharge (`discharged_by` the proving AC/test) or move the
     risk_state deliberately.
   - a rule that genuinely cannot be met this release → a `WVR-` waiver, on the
     operator's explicit words only. The waiver names rule, entity, justification,
     approver and expiry. Readiness reports it "waived", never silently.
3. **Expired waivers**: the readiness report lists `expired_waivers`. An expired
   waiver no longer satisfies its rule. For each: prefer RESOLVING the underlying
   item now. Re-approval is a fresh operator-worded `WVR-` row (or a full-row
   upsert with a new `expires`), never a silent carry-over into the release.
4. Advisory findings (`/tamheed:register-liveness` is the full playbook): review each and
   say what you decided. Carrying one is legal. Silence is not.
5. `human_required` gates: read each `GATE-` definition to the operator and take their
   explicit decision. Upsert the gate row's `outcome` (Go/Hold/Redirect/Kill), and
   record it as a `progress_update` (event_type "gate-decision", subject_id the
   `GATE-` id).
6. `gate_run()` must pass.
7. Release notes from `entity_query("progress-entry")` since the last release.
   `work_bind` the release tag/commit to the phase and headline entities.
8. `export_html()`: the review surface ships with the release, exported AFTER the
   bind so the page carries it. `package_verify()` reads `review_current: true`.
   Then `package_close()` and commit the package `data/` and the page with the release.
