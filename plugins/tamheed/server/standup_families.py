"""Plain words for each family of the record (plan 251, R11, D10): the standup page's fold "What
the record holds" and its names for counts. Written for a reader who does not know Tamheed.

Keyed by table. Each value is (id prefix, one, many, definition). A test ties the keys to the
server's registry, so a new family cannot ship without its plain words. Each definition claims
only what the schema or a guard enforces: an optional column is "can", a required one "each".
"""
from __future__ import annotations

FAMILIES: dict[str, tuple[str, str, str, str]] = {
    "requirements": ("FR-", "requirement", "requirements",
                     "A need the product must meet. Each requirement names its source, so we know"
                     " who asked for it. Each one in the first release links to a decision, a"
                     " task and a test."),
    "constraints": ("CON-", "constraint", "constraints",
                    "A limit from outside the project, such as a law, a budget or a platform. The"
                    " design must fit inside it and cannot change it."),
    "invariants": ("INV-", "fixed rule", "fixed rules",
                   "A property of the product that must always stay true. It can say how it is"
                   " enforced. Work that breaks one is wrong, even when its tests pass."),
    "assumptions": ("ASM-", "assumption", "assumptions",
                    "Something the plan takes as true without proof yet. It can say what goes"
                    " wrong if it is false, and when to check it again."),
    "dependencies": ("DEP-", "dependency", "dependencies",
                     "A person, team or system outside the project that the work waits on. It can"
                     " name an owner. Work that depends on it can stop while it is not met."),
    "open_questions": ("OQ-", "open question", "open questions",
                       "A question raised in the planning. While it has no answer, it can have an"
                       " owner and a due date, and text that depends on it carries a marker. An"
                       " answered question stays in the record with its answer."),
    "decisions": ("DEC-", "decision", "decisions",
                  "A choice about the project, with its reason. Only an approved decision steers"
                  " the work. A decision that waits for approval steers nothing yet."),
    "adrs": ("ADR-", "architecture decision", "architecture decisions",
             "A recorded choice about the structure of the system, with its context and its"
             " effects. After approval it is never edited. A new one replaces it when the choice"
             " changes."),
    "risks": ("RISK-", "risk", "risks",
              "Something that could go wrong, with how likely it is and how much harm it does. It"
              " can have an owner and a response. An open risk blocks a release until a named test"
              " or acceptance check answers it, or the team marks it reduced, accepted or"
              " closed."),
    "hypotheses": ("HYP-", "hypothesis", "hypotheses",
                   "A statement the team wants to test. It can name the measure and the target,"
                   " set before the test. The result shows if the idea holds."),
    "experiments": ("EXP-", "experiment", "experiments",
                    "A short, timed test of a hypothesis. Its result says if the idea held, failed"
                    " or stayed unclear."),
    "pocs": ("POC-", "proof of concept", "proofs of concept",
             "A small build that shows if an approach works before the team commits to it. Its"
             " result says if the approach held, failed or stayed unclear."),
    "tests": ("TEST-", "test", "tests",
              "A planned test of the product. It records if it passed or failed, so the plan can"
              " show which needs have proof."),
    "kpis": ("KPI-", "success measure", "success measures",
             "A number that shows if the project succeeds, with its target. It tells the team what"
             " good looks like after the release."),
    "stakeholders": ("STK-", "stakeholder", "stakeholders",
                     "A person or group with an interest in the project, and what they care about."
                     " Their needs and approvals shape the plan."),
    "phases": ("PH-", "phase", "phases",
               "A stage of the plan, such as discovery or the first release. It closes when its"
               " release rules pass, or when the operator forces it and the record notes that."),
    "milestones": ("MS-", "milestone", "milestones",
                   "A named date in a phase. It is a label for planning only, and it stops no"
                   " work."),
    "slices": ("SL-", "slice", "slices",
               "A small part of the product that is built, tested and delivered on its own. Tasks"
               " and acceptance checks belong to a slice. It closes when its release rules pass,"
               " or when the operator forces it and the record notes that."),
    "wbs_items": ("WBS-", "task", "tasks",
                  "One piece of planned work. A task can hold smaller tasks. When the agent says a"
                  " task is finished, it shows as claimed done. It counts as done only after"
                  " someone marks it done."),
    "acceptance_criteria": ("AC-", "acceptance check", "acceptance checks",
                            "The condition that shows one requirement is done, written before the"
                            " work. It usually belongs to one slice. A person, a machine or the"
                            " agent runs it and records a result. After approval its text never"
                            " changes."),
    "audit_verdicts": ("AV-", "check result", "check results",
                       "The result of one acceptance check: passed, partly passed, failed or not"
                       " graded yet. It can name its evidence and who checked it. The newest"
                       " result counts."),
    "progress_entries": ("PE-", "journal entry", "journal entries",
                         "One line of the project's work log: work done, a status move, a"
                         " decision at a gate or a note. Entries are never changed. A mistake is"
                         " corrected by a new entry."),
    "defects": ("DEF-", "defect", "defects",
                "A fault found in the work, with its severity. An open critical or high defect"
                " stops a release. A lower one is a warning only."),
    "deferred_work": ("DW-", "postponed item", "postponed items",
                      "Work the team chose to do later, with the event that brings it back. It"
                      " keeps known gaps visible instead of lost."),
    "execution_gates": ("GATE-", "approval gate", "approval gates",
                        "A point where a person decides if the work goes on: go, hold, redirect or"
                        " stop. Only that person's decision opens the gate."),
    "execution_plans": ("EP-", "slice work plan", "slice work plans",
                        "The plan for how one slice is built: the steps, the order and the"
                        " checks."),
    "conventions": ("CONV-", "working rule", "working rules",
                    "A rule of the team that every session follows, such as how to name branches"
                    " or how to commit. It keeps the work the same from day to day."),
    "scope_changes": ("SC-", "scope change", "scope changes",
                      "A proposed change to the plan: what it adds, changes or removes. The"
                      " operator approves it, and then its changes are applied. It keeps a reason"
                      " beside each change to the plan."),
    "waivers": ("WVR-", "waiver", "waivers",
                "The operator's written permission to pass one release rule, for a named reason."
                " It can carry an end date. The release rules report it as waived, never in"
                " silence."),
    "narrative_documents": ("DOC-", "document", "documents",
                            "A document of the plan, such as the charter or the architecture. Its"
                            " text lives in its sections."),
    "document_sections": ("SEC-", "document section", "document sections",
                          "One section of a document, with its heading and its text."),
    "diagrams": ("DIA-", "diagram", "diagrams",
                 "A picture of the system, such as its parts or its data flow, kept as text in the"
                 " record."),
    "glossary_terms": ("GT-", "glossary term", "glossary terms",
                       "A word of the project's field, with its meaning, so everyone reads it the"
                       " same way."),
    "lessons": ("LL-", "lesson", "lessons",
                "Something the work taught, with a recommendation for next time. The operator"
                " confirms each lesson before it counts."),
    "skills": ("SKL-", "skill", "skills",
               "A way of working made from confirmed lessons, which the agent loads in later"
               " sessions. The operator approves it."),
    "feedback": ("FB-", "feedback row", "feedback rows",
                 "A note from the project to the makers of its planning tool: a gap, a fault or a"
                 " question. It can also register a small tool the project uses. The operator"
                 " confirms or rejects each row."),
    "prompts": ("PRT-", "prompt", "prompts",
                "Standing words the agent reads when it starts a session or a step, such as the"
                " kickoff of the work."),
    "registers": ("REG-", "project register", "project registers",
                  "A list kind that this project defined for itself, with the fields each entry"
                  " must carry."),
    "register_entries": ("ENT-", "register entry", "register entries",
                         "One entry of a project register. The record refuses an entry that lacks"
                         " a required field."),
    "standup_reports": ("RPT-", "standup report", "standup reports",
                        "A report like this one for one stretch of work: what was done, the"
                        " challenges and what comes next. The operator approves it before it is"
                        " recorded."),
}

OTHER = "A kind of row that this project added for itself. Its own name says what it holds."


def by_prefix() -> dict[str, str]:
    """{prefix without the dash: table}, with NFR beside FR."""
    out = {spec[0].rstrip("-"): table for table, spec in FAMILIES.items()}
    out["NFR"] = "requirements"
    return out
