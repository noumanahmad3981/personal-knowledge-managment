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
- `.opencode/skills/kb-pipeline/SKILL.md` — documentation-pipeline Skill; governed by `AGENTS.md` §Agent Skills.
- `.opencode/skills/` — directory containing all Agent Skills; each Skill is a subdirectory with a `SKILL.md`.
- `AGENTS.md` — this file. **Single source of truth** for the workflow and Skill governance.

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
7. `AGENTS.md` governs all Skills.
8. Agents must discover available Skills when a task may match an existing Skill.

## Agent Skills

### What Is an Agent Skill?

An Agent Skill is a reusable, specialized capability defined by a `SKILL.md`
file with YAML frontmatter (`name`, `description`). Each Skill provides
domain-specific instructions for a well-defined purpose. Skills are the
mechanism by which agents access specialized workflows without recreating them
from memory.

### Governance

- `AGENTS.md` defines Skill governance and tells agents how to discover and
  invoke Skills. The actual specialized behavior comes from the corresponding
  `SKILL.md`.
- Every Skill must clearly define its purpose and boundaries, including when
  it should and should not be invoked.
- Skills must be unique: a new Skill must not duplicate or substantially overlap
  an existing Skill.
- Skills must not perform unrelated tasks outside their defined responsibility.
- Skills must not silently create, modify, install, or remove other Skills
  unless explicitly authorized.
- Skill invocation must not bypass project safety, validation, approval, or
  human-decision requirements.
- Every `SKILL.md` must include `When to Invoke` and `When NOT to Invoke` sections.

### Single Responsibility

Each Skill must have ONE clearly defined responsibility. A Skill that tries to
do more than one thing is violating this rule. The `SKILL.md` must state what
the Skill does and what it does not do.

### Uniqueness

A new Skill must not duplicate or substantially overlap an existing Skill.
Before introducing a new Skill, the agent must verify that no existing Skill
already covers the same responsibility. If overlap exists, the existing Skill
must be extended or the new requirement must be reconciled rather than creating
a duplicate Skill.

### Boundaries

Every Skill must define its purpose and boundaries. This includes:
- When the Skill should be invoked.
- When the Skill must NOT be invoked.
- What tasks fall outside the Skill's defined responsibility.

## Skill Discovery & Invocation

### Discovery

Agents discover Skills by scanning `.opencode/skills/*/SKILL.md` files. Each
`SKILL.md` has YAML frontmatter containing `name` and `description` fields.
The agent compares the task description against each Skill's `name` and
`description` to identify matches.

### Invocation

1. Read `AGENTS.md` to understand project rules and Skill governance before
   discovering Skills.
2. Scan `.opencode/skills/*/SKILL.md` to discover available Skills.
3. When a task matches a Skill's `name` or `description`, read the matching
   `SKILL.md` in full.
4. Follow the `SKILL.md`'s instructions rather than recreating the Skill's
   workflow independently.
5. Ensure all `AGENTS.md` governance rules (validation, approval, human-decision
   requirements) are satisfied during execution.

### When No Skill Matches

If no existing Skill matches the task, the agent may proceed using the normal
project rules (`AGENTS.md`) rather than inventing a Skill automatically. The
agent must not create a new Skill on the fly; it must use existing project
rules and workflows.

### When Multiple Skills Appear to Match

If multiple Skills appear to match the same task, the agent must identify the
overlap and resolve it according to project rules (e.g., `AskQuestion` if
needed). The agent must not arbitrarily combine conflicting Skills.

## Skill Boundaries & Safety

Skills operate under `AGENTS.md`. The governance and boundary rules defined
in §Agent Skills above are authoritative. If a Skill's instructions conflict
with `AGENTS.md`, `AGENTS.md` prevails.

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

Vault-wide validation: `python3 pkm/scripts/validator.py --all` (optionally `--section <Name>` to scan one section).

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
- `AGENTS.md` defines Skill governance and invocation rules; `SKILL.md` contains specialized Skill instructions. Do not duplicate the complete `kb-pipeline` workflow inside `AGENTS.md`.
- Do not create another Skill. Do not redesign `kb-pipeline`.
