## plugins/tamheed/references/artifact-catalog.md
- tokens gone (3): `<package>/prompts/*.md`, `<package>/prompts/`, `README.md`
- tokens new (2): `<package>/README.md`, `prompt`

## plugins/tamheed/references/artifact-rules.md
- tokens gone (1): `<package>/prompts/`
- tokens new (2): `PRT-`, `prompt`

## plugins/tamheed/references/handoff.md
- tokens gone (5): 5.0, `.md`, `README.md`, `data/prompts.jsonl`, `prompts/*.md`
- tokens new (17): 196, FILES, `<package>/README.md`, `PRT-NNN.body`, `PRT-`, `converted_from`, `custom_attributes`, `entry_point`, `kickoff`, `phase`, `plugin_skill`, `prompt-ids-resolve`, `prompt`, `prompts-v5-backup/`, `prose-plain-english`, `refresh_stock`, `situational`
- modal words that FELL (review stop): never 13->12

## plugins/tamheed/references/modes.md
- tokens gone (1): `<package>/prompts/`
- tokens new (1): `<package>/README.md`

## plugins/tamheed/references/prompt-templates.md
- tokens gone (6): 028, `.md`, `kickoff.md`, `phase3-resume.md`, `prm-NNN-<kind>.md`, `prompts/README.md`
- tokens new (12): 196, `<package>/README.md`, `PRT-`, `entry_point`, `kickoff`, `kind`, `phase_id`, `phase`, `plugin_skill`, `prompt-ids-resolve`, `prompt`, `situational`
- modal words that FELL (review stop): must 3->2, never 7->5

## plugins/tamheed/references/quality-gates.md
- tokens gone (4): FILES, `<package>/prompts/*.md`, `<package>/prompts/`, `unit: files`
- tokens new (3): ROWS, `prompt`, `unit: rows`
- modal words that FELL (review stop): never 13->12

## plugins/tamheed/references/vocabulary.md
- tokens new (3): 1, 21, 22

## plugins/tamheed/references/workflow.md
- tokens gone (2): `<package>/prompts/*.md`, `<package>/prompts/`
- tokens new (7): 196, `PRT-`, `entry_point`, `kickoff`, `plugin_skill`, `prompt`, `situational`

## plugins/tamheed/skills/defect-triage/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="defect-triage")`

## plugins/tamheed/skills/drift-register/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="drift-register")`

## plugins/tamheed/skills/generate-report/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="generate-report")`

## plugins/tamheed/skills/integrity-check/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="integrity-check")`

## plugins/tamheed/skills/loop-iteration/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="loop-iteration")`

## plugins/tamheed/skills/orient-resume/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="orient-resume")`

## plugins/tamheed/skills/package-onboarding/SKILL.md
- tokens gone (1): `<package>/prompts/README.md`
- tokens new (6): `<package>/README.md`, `entity_query("prompt", id=<entry_point>)`, `entity_query("prompt", status="Approved")`, `entity_query("prompt", status="Approved", plugin_skill="package-onboarding")`, `entry_point`, `prompt`

## plugins/tamheed/skills/phase-close/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="phase-close")`

## plugins/tamheed/skills/progress-sync/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="progress-sync")`

## plugins/tamheed/skills/register-liveness/SKILL.md
- tokens gone (1): `prompts/*.md`
- tokens new (2): `entity_query("prompt", status="Approved", plugin_skill="register-liveness")`, `prompt`

## plugins/tamheed/skills/release-close-out/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="release-close-out")`

## plugins/tamheed/skills/replan-deferred/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="replan-deferred")`

## plugins/tamheed/skills/skill-promote/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="skill-promote")`

## plugins/tamheed/skills/slice-kickoff/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="slice-kickoff")`

## plugins/tamheed/skills/slice-review/SKILL.md
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="slice-review")`

## plugins/tamheed/skills/ste-rewrite/SKILL.md
- tokens gone (1): `prompts/`
- tokens new (1): `entity_query("prompt", status="Approved", plugin_skill="ste-rewrite")`

## plugins/tamheed/skills/tamheed/SKILL.md
- tokens gone (3): `.md`, `/tamheed:<name>`, `<package>/prompts/`
- tokens new (8): `<package>/README.md`, `PRT-`, `entry_point`, `kickoff`, `plugin_skill`, `prompt`, `prompts-v5-backup/`, `situational`
- modal words that FELL (review stop): never 26->25

## plugins/tamheed/templates/README.md
- tokens gone (1): `<package>/prompts/`
- tokens new (3): `kickoff`, `phase`, `situational`

## plugins/tamheed/templates/agent-control.template.md
- tokens gone (1): `<package-name>/prompts/README.md`
- tokens new (1): `<package-name>/README.md`

## plugins/tamheed/templates/contributing.template.md
- tokens gone (1): `<package>/prompts/`
- tokens new (1): `situational`

## plugins/tamheed/templates/follow-up-prompts.template.md
- tokens gone (4): PROJECT, `<package>/prompts/`, `<package>/prompts/defect-triage.md`, `<package>/prompts/release-close-out.md`
- tokens new (6): BODIES, `/tamheed:defect-triage`, `/tamheed:release-close-out`, `PRT-`, `phase`, `situational`

## plugins/tamheed/templates/initial-prompt.template.md
- tokens gone (2): PROJECT, `<package>/prompts/`
- tokens new (3): BODY, `PRT-`, `kickoff`

## plugins/tamheed/templates/naming-conventions.template.md
- tokens gone (4): `.md`, `<package>/prompts/`, `kickoff.md`, `phase3-resume.md`
- tokens new (5): `kickoff`, `phase`, `plugin_skill`, `prompt`, `situational`

## plugins/tamheed/templates/package-readme.template.md
- tokens gone (1): `prompts/README.md`
- tokens new (3): `README.md`, `entry_point`, `prompt`

## plugins/tamheed/templates/review-prompts.template.md
- tokens gone (2): PROJECT, `<package>/prompts/`
- tokens new (3): BODIES, `PRT-`, `situational`

37 changed prose/code files, 33 with a token or modal difference to review.
