# Trigger phrases in skill descriptions (R11)

## ci-evidence
- condition: Use before stating that CI or a deploy is green, red or done
- condition: Use before recording an audit verdict, a gate-decision journal entry or a done-claim that rests on a CI run
- condition: Use before predicting whether a push or pull request will run jobs, and before explaining why a job was skipped

## defect-triage
- condition: Invoke when a bug is reported or discovered during execution

## drift-register
- condition: Invoke when work happened without recording (a rushed session, a hotfix, an agent that forgot)

## generate-report
- condition: Invoke to refresh and read the HTML review surface (review

## integrity-check
- condition: Invoke to audit the package read-only: canonical round-trip, gates, counts, trace samples, audit honesty, staleness, unbound commits, readiness

## loop-guard
- condition: Invoke to read the brake for fully-auto execution: the stop conditions an unattended loop evaluates every iteration

## loop-iteration

## measurement-evidence

## operator-interview

## orient-resume

## package-onboarding

## package-writes
- condition: Use before any write to a Tamheed package (entity_upsert - full-row, substitute or retire items - progress_update, audit_record, work_bind, package_verify with record)
- condition: Use before export_html or handoff_emit, which write package files
- condition: Use before any git operation that touches package data (commit, branch, checkout, reset, stash, merge, push)
- condition: Use before writing a commit sha, a digest, or a claim that a row was written, into a row or a commit message

## phase-close
- condition: Invoke to close a phase deliberately

## plain-english
- condition: Use before writing English a reader cannot question

## progress-sync

## reading-the-record
- condition: Use before asserting what a requirement, decision, ADR, acceptance criterion or any register row says
- condition: Use before offering the operator an option, before calling a status, count or figure stale, and before measuring anything a requirement specifies

## register-liveness

## release-close-out
- condition: Invoke to close out a release at package scope, blocking-clean

## replan-deferred
- condition: Invoke when deferred-work activation triggers may have fired

## session-handoff

## skill-promote
- condition: Invoke when the operator asks to distil confirmed lessons into a reusable project or user skill

## slice-kickoff
- condition: Invoke to start execution of the next open slice, plan-first (semi-auto: the acceptance-criteria-first plan stops for the operator's approval before any code)

## slice-review
- condition: Invoke when a slice is believed complete

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
- condition: Trigger on "plan this project", "turn this idea into a plan", "scope this out", "design before we build", "prepare a handoff", "project charter", or a long pasted project brief, even if the word "Tamheed" is never said

## test-evidence
- condition: Use before recording a Met verdict whose evidence is a passing test or suite
- condition: Use before accepting that an existing test proves what its name claims

## written-claims
- quoted: "every remaining consumer"
- condition: Use before writing or merging prose that states a mechanism, a count, a sequence, a scope, a status or a done-claim

