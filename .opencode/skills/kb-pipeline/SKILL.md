---
name: kb-pipeline
description: Orchestrates the knowledge base documentation pipeline (epic → subtask → draft → validation → review → approval). Use when starting an epic, subtask, or document draft in this project.
---

# kb-pipeline Orchestrator

This skill orchestrates the workflow defined in **AGENTS.md**. AGENTS.md is
the single source of truth; read it before executing and follow its section
rules. Do not restate workflow logic here.

Execution steps:

1. **Intake** — record the epic/subtask/document request.
2. **Draft** — delegate all writing to a GeneralTask subagent (AGENTS.md §1).
3. **Validate** — run Auto Validation (AGENTS.md §2); on fail, return to
   GeneralTask and re-validate.
4. **Review** — launch kb-editor, kb-tech-lead, kb-architect in parallel and
   merge into a Combined Review Report (AGENTS.md §3).
5. **History** — update Review History (AGENTS.md §4).
6. **Decide** — apply Decision Logic; escalate via AskQuestion only per
   AGENTS.md §5 (AGENTS.md §6).
7. **Approve** — run final validation and issue an Approval Summary
   (AGENTS.md §7).
