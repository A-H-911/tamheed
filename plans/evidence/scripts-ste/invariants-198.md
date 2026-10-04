## CHANGELOG.md
- tokens new (16): 5.9, 6.0, `4.0.0`, `<package>/README.md`, `custom_attributes.converted_from`, `entity_index`, `execution half`, `loop-guard`, `package_version`, `phase_id`, `planning half`, `prompts-v5-backup/`, `prompts.body`, `prompts.jsonl`, `tamheed:note v7`, `v7`

## README.md
- tokens gone (1): 9.0

## docs/install.md
- tokens new (1): 6.0.0

## generated-samples/support-triage-agent-v2/prompts/follow-up-prompts.md
- tokens gone (18): FIRST, `Merged`, `SC-`, `WVR-`, `against_commit`, `audit_record`, `entity_query("progress-entry")`, `execution-plan`, `gate_run()`, `git log`, `package_open("support-triage-agent-v2")`, `progress_update`, `readiness_check("phase", "<PH-x>")`, `subject_id`, `verification_method`, `verified_by`, `work-done`, `work_bind`
- modal words that FELL (review stop): never 1->0, only 1->0

## generated-samples/support-triage-agent-v2/prompts/initial-prompt.md
- tokens gone (14): CLAUDE, QUERIES, STOP, `("acceptance-criterion")`, `("slice")`, `OQ-`, `Review`, `[NEEDS-CLARIFICATION: OQ-NNN]`, `audit_record`, `entity_query("invariant")`, `entity_query("phase")`, `entity_query("requirement", status="Approved")`, `package_open("support-triage-agent-v2")`, `review.html`
- modal words that FELL (review stop): must 1->0, never 2->0

## generated-samples/support-triage-agent-v2/prompts/review-prompts.md
- tokens gone (7): G-REL, MVP, `audit_record`, `entity_query("acceptance-criterion")`, `gate_run()`, `package_open("support-triage-agent-v2")`, `readiness_check("package")`
- modal words that FELL (review stop): never 1->0, only 1->0

## lab/scenario.md
- tokens new (17): 008, 34, 6.0.0, CONFIRM, G-SET, PREVIEW, `<!-- tamheed:note v7 -->`, `PRT-001`, `agent:lab-beat-34`, `converted_from`, `count prompt --col kind=kickoff --col lifecycle_status=Approved --min 1`, `prompts-v5-backup/`, `prompts`, `review_exported_by: "6.0.0"`, `rule prompt-ids-resolve`, `section id="prompts"`, `tamheed v6.0.0`

## plugins/tamheed/prompts/README.md
- tokens gone (1): 9.0

## plugins/tamheed/references/artifact-catalog.md
- tokens gone (1): 9.0
- tokens new (1): 0.0

## plugins/tamheed/server/README.md
- tokens gone (1): 9.0
- tokens new (1): 0.0

## plugins/tamheed/server/export_html.py
- tokens new (3): 020, 198, `entry_point`

## plugins/tamheed/server/tamheed_server.py
- tokens new (3): 198, 6.0.0, `handoff/initial-prompt.md`

## plugins/tamheed/skills/tamheed/SKILL.md
- tokens gone (1): 9.0
- tokens new (1): 0.0

## tests/test_export_html.py
- tokens new (2): 198, PRT-

## tests/test_mcp_contract.py
- tokens new (2): 198, `handoff/initial-prompt.md`

## tests/test_user_guide.py
- tokens gone (1): 10
- tokens new (2): 11, 198

19 changed prose/code files, 16 with a token or modal difference to review.
