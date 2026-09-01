---
name: kb-pipeline
description: Orchestrates the knowledge base documentation pipeline (epic → subtask → draft → validation → review → approval) defined in AGENTS.md. Use when starting an epic, subtask, or document draft in this project, or when drafting, revising, validating, reviewing, or approving a PKM document.
---

# kb-pipeline Orchestrator

## Purpose

This skill orchestrates the PKM documentation workflow defined in **AGENTS.md**.

- AGENTS.md is the single source of truth for the pipeline, contracts,
  validation rules, reviewer rules, escalation rules, and approval criteria.
- Read AGENTS.md fully before executing anything.
- This skill executes that workflow; it does not restate or replace its rules.

## When to Invoke

Invoke when the user:

- starts a new PKM document;
- requests drafting, revision, validation, review, or approval of a PKM
  document;
- starts an Epic or Subtask that follows the PKM documentation pipeline.

## When NOT to Invoke

Do not invoke for:

- general questions, explanations, or discussion;
- reading, searching, or inspecting documents without pipeline execution;
- unrelated file changes;
- running a single reviewer or validator task outside the pipeline;
- work unrelated to PKM documentation.

## Execution Workflow

1. **Read AGENTS.md** before execution. Follow its pipeline, contracts,
   validation rules, reviewer rules, escalation rules, and approval criteria
   exactly.
2. **Intake** — before starting, collect all required values using the
   question tool:
   - Section: Knowledge | Research | Projects | Ideas
   - Area: subdirectory name (e.g., FastAPI)
   - Topic: filename stem (e.g., fastapi-introduction)
   - Title: human-readable title
   - Status: initial status valid for the section

   If any value is missing or ambiguous, ask before proceeding.
3. **Delegate all writing** — launch GeneralTask (Task tool) for every draft
   and every revision, passing the handoff values above. Never write or edit
   vault documents yourself.
4. **Auto Validation** — run
   `python3 pkm/scripts/validator.py <document.md>` before reviews and again
   before approval (AGENTS.md §2). On FAIL, return findings to GeneralTask
   and re-validate until PASS; cycle limits come from AGENTS.md.
5. **Independent Reviews** — launch kb-editor, kb-tech-lead, and kb-architect
   as three concurrent, independent Task calls. Each agent defines its own
   output format. Merge their outputs into one deduplicated Combined Review
   Report (AGENTS.md §3).
6. **Review History** — record resolved/recurring/unresolved findings per
   cycle in `pkm/.review-history.json` (AGENTS.md §4); use it to detect
   recurring issues.
7. **Decisions & Escalation** — apply AGENTS.md §5–§6: continue correction/
   review cycles automatically; use AskQuestion only under the escalation
   conditions defined there. Never bypass validation, review, escalation, or
   approval steps.
8. **Final Approval** — approve only when the AGENTS.md §7 criteria are met,
   then produce the Approval Summary defined there.

## Error Handling

- Missing required intake information → ask the user before continuing.
- A required tool or agent fails → stop the affected step and report the
  failure; never report success after a failed required step.
- Validation fails → return the findings to GeneralTask for fixes and
  re-validate per AGENTS.md §2.
- Use AskQuestion only under the AGENTS.md §5 conditions: reviewer conflicts,
  recurring issues, adjudication needs, the cycle limit, or genuine human
  decisions.
- Never skip or bypass required validation, review, escalation, or approval.

## Completion

Complete only when the AGENTS.md final approval criteria are satisfied.
Before reporting completion, confirm:

- [ ] Final validation passed;
- [ ] Review requirements passed;
- [ ] No unresolved critical findings remain;
- [ ] Required approval state/history has been updated.

If any condition fails, continue the correction/review process or escalate
per AGENTS.md — do not report success.
