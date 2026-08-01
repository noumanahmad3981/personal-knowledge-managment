# AGENTS.md — Knowledge Base Documentation Pipeline

## Purpose

Production workflow for authoring epics, subtasks, and PKM vault documents.
Every document is drafted by GeneralTask, validated, independently reviewed,
history-tracked, and approved. Human adjudication is reserved for genuine
decisions only.

## Project Architecture

- `pkm/` — git-based PKM vault: `Knowledge/`, `Research/`, `Projects/`,
  `Ideas/`, `Templates/` (section templates).
- `.opencode/agents/kb-editor.md` — content reviewer (read-only).
- `.opencode/agents/kb-tech-lead.md` — technical reviewer (read-only).
- `.opencode/agents/kb-architect.md` — architecture reviewer (read-only).
- `.opencode/skills/kb-pipeline/SKILL.md` — lightweight orchestrator; invokes
  this file; never duplicates it.
- `AGENTS.md` — this file. **Single source of truth** for the workflow.

## Golden Rules

1. All writing is performed by **GeneralTask**. No other agent may directly
   create or rewrite documents.
2. Reviewer agents (`kb-editor`, `kb-tech-lead`, `kb-architect`) are
   independent and read-only; they never edit.
3. **Auto Validation** runs automatically before reviewer execution and again
   before final approval.
4. **AskQuestion** is used ONLY for reviewer conflicts, recurring issues,
   adjudication, the 10-cycle limit, or a genuine human decision.
5. Review cycles are capped at **10** per document.
6. `SKILL.md` orchestrates; `AGENTS.md` defines. Never duplicate workflow logic.

## Pipeline

```
Epic
  → Subtask
  → GeneralTask Draft
  → Auto Validation
  → Parallel Independent Reviews (kb-editor, kb-tech-lead, kb-architect)
  → Combined Review Report
  → Review History
  → Decision
  → Final Validation
  → Approval
```

## 1. Drafting — GeneralTask Contract

- Every draft, revision, and fix is written by a GeneralTask subagent.
- The orchestrator provides the epic/subtask specification; GeneralTask
  produces the draft using the matching section template.
- Handoff contract: document path, section template, initial `status`, and
  required metadata fields (title, date, author, tags, sources, references).
- GeneralTask is responsible for revisions after every review cycle.

## 2. Auto Validation

Run automatically (a) before reviewers execute and (b) before final approval.

Checks:

- **Discoverable** — filename/path follows convention and is locatable.
- **Atomic** — one topic per document.
- **Audited** — changelog entry present and current.
- **YAML frontmatter** — valid, well-formed YAML.
- **Template compliance** — matches the section template structure.
- **Required headings** — all template body headings present.
- **Required metadata** — all template fields present and typed.
- **References** — internal [[wikilinks]] and sources resolve. Convention: frontmatter `references` holds internal [[wikilinks]] only; frontmatter `sources` holds external links/DOIs; the body `## References` section may also hold external links for readers.
- **Valid status** — value belongs to the section's status enum.

Output: a **Validation Report** (check, pass/fail, notes).

On failure: return the work to GeneralTask, then validate again automatically.
Loop until PASS.

## 3. Reviewer Pipeline

- Run `kb-editor`, `kb-tech-lead`, and `kb-architect` concurrently and
  independently. No reviewer sees or is influenced by another's output.
- Each returns an **Independent Review**: a numbered findings list
  (`[severity] location → issue → rationale`) or `APPROVED` when clean.
- Merge findings into one **Combined Review Report**: deduplicated,
  severity-tagged, attributed to each reviewer.

## 4. Review History

Maintain per-document history across review cycles:

- **Resolved** issues — fixed and confirmed gone.
- **Recurring** issues — same or related finding in ≥2 cycles.
- **Unresolved** issues — still open at end of a cycle.

History drives recurrence detection and the Decision Logic below.

## 5. Escalation — AskQuestion

Use AskQuestion ONLY when one of these applies:

1. Reviewers directly **conflict** (contradictory findings).
2. A **recurring** issue appears (≥2 cycles).
3. **Adjudication** is required (judgment call, tradeoff, ambiguity).
4. The **10-cycle** limit is reached with open findings.
5. A **genuine human decision** is required.

Never ask unnecessary questions. All other decisions continue automatically.

## 6. Decision Logic

| Condition | Action |
|---|---|
| Validation fails | GeneralTask fixes → validate again |
| Reviewers request revisions | GeneralTask revises → new review cycle |
| Reviewers disagree | AskQuestion |
| Same issue repeats across cycles | AskQuestion |
| Otherwise | Continue automatically |

## 7. Final Approval

Approval requires ALL of:

- Validation **PASS** (final validation).
- Review **PASS** (combined review with no blocking findings).
- **No unresolved critical findings** in Review History.

Generate a final **Approval Summary**: document, cycles used, resolved/
recurring/unresolved issues, reviewer verdicts, validation report.

## Constraints

- Keep this document concise and modular.
- Preserve the existing project architecture.
- Improve the workflow rather than replacing it.
- `SKILL.md` must reference this file, not restate it.
