# Trigger phrases in skill descriptions (R11)

## ci-evidence
- condition: Use before stating that CI or a deploy is green, red or done; before recording an audit verdict, a gate-decision journal entry or a done-claim that rests on a CI run; before predicting whether a push or pull request will run jobs; before explaining why a job was skipped; and before listing the gates you ran

## defect-triage
- condition: Invoke when a bug is reported or discovered during execution: the defect row is registered FIRST, then the fix, the evidence, the binding and the status flip

## drift-register
- condition: Invoke when work happened without recording (a rushed session, a hotfix, an agent that forgot) to register every piece of drift between reality and the package

## generate-report
- condition: Invoke to refresh and read the HTML review surface (review

## integrity-check
- condition: Invoke to audit the package read-only: canonical round-trip, gates, counts, trace samples, audit honesty, staleness, unbound commits, readiness - a report that changes nothing

## loop-guard
- condition: Invoke to read the brake for fully-auto execution: the stop conditions an unattended loop evaluates every iteration; scope decisions and forced transitions always need a human

## loop-iteration

## measurement-evidence

## operator-interview

## orient-resume

## package-onboarding

## package-writes
- condition: Use before any write to a Tamheed package (entity_upsert - full-row, substitute or retire items - progress_update, audit_record, work_bind, package_verify with record); before export_html or handoff_emit, which write package files; before any git operation that touches package data (commit, branch, checkout, reset, stash, merge, push); and before writing a commit sha, a digest, or a claim that a row was written, into a row or a commit message

## phase-close
- condition: Invoke to close a phase deliberately: the phase-scope readiness failures resolved or waived on the operator's words, expired waivers, milestones, human gates, then the guarded Implemented transition

## plain-english
- condition: Use before writing English a reader cannot question

## progress-sync

## reading-the-record
- condition: Use before asserting what a requirement, decision, ADR, acceptance criterion or any register row says; before offering the operator an option; before calling a status, count or figure stale; and before measuring anything a requirement specifies

## register-liveness

## release-close-out
- condition: Invoke to close out a release at package scope, blocking-clean: every blocking readiness failure resolved, expired waivers renewed on the operator's words, human gates decided, release notes, bindings

## replan-deferred
- condition: Invoke when deferred-work activation triggers may have fired: judge each trigger's words against current state, propose the scope change, STOP for approval, then activate in order

## session-handoff

## skill-promote
- condition: Invoke when the operator asks to distil confirmed lessons into a reusable project or user skill - the interactive promotion ceremony; the operator decides at every step

## slice-kickoff
- condition: Invoke to start execution of the next open slice, plan-first (semi-auto: the acceptance-criteria-first plan stops for the operator's approval before any code)

## slice-review
- condition: Invoke when a slice is believed complete: per-criterion verdicts against the criterion's own exported text, bindings, the closing entry, then readiness_check at slice scope - the review that moves Review to Implemented

## ste-rewrite
- condition: Invoke to rewrite a package's existing prose into plain English, batch by batch

## tamheed
- quoted: "inception"
- quoted: "plan this project"
- quoted: "turn this idea into a plan"
- quoted: "scope this out"
- quoted: "design before we build"
- quoted: "prepare a handoff"
- quoted: "project charter"
- quoted: "Tamheed"
- condition: Trigger on "plan this project", "turn this idea into a plan", "scope this out", "design before we build", "prepare a handoff", "project charter", or a long pasted project brief — even if the word "Tamheed" is never said

## test-evidence

## written-claims
- quoted: "every remaining consumer"
- condition: Use before writing or merging prose that states a mechanism, a count, a sequence, a scope, a status or a done-claim — a progress entry, a WBS done-clause, an audit verdict's evidence, a findings file, a memory line, a kickoff prompt or any other file a session reads before acting, a code comment, an inventory ("every remaining consumer") — and whenever you retract or correct a claim you or someone else made, or record a ruling that changes what earlier prose assumed

