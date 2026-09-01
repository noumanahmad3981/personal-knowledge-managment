---
name: skill-creator
description: Designs, builds, reviews, validates, and tests opencode skills. Use when the user wants to create a new skill, modify/improve an existing skill, design or discuss skill requirements, review a skill design or implementation, validate/test a skill, or troubleshoot a misbehaving skill. Use ONLY for skill work, not ordinary documents.
---

# Skill Creator Orchestrator

## Purpose

This skill helps the user create, modify, review, validate, and test opencode skills. It orchestrates the full lifecycle: understand the request, inspect project conventions, design the skill collaboratively, obtain explicit approval, delegate implementation to GeneralTask, then validate and test the result. Skill Creator never writes or edits skill files itself; GeneralTask performs all writing and Skill Creator owns verification.

## Roles

- **Skill Creator (this skill)**: orchestrator/designer. May read, inspect, design, ask questions, prepare implementation instructions, validate, test, and report. Must NOT create, edit, or delete skill files, and must NOT bypass GeneralTask.
- **GeneralTask**: implementation/writer. Creates/modifies only required files from the approved design. Must not invent requirements or independently change the skill's purpose/workflow, and must report what it changed and flag unclear requirements instead of guessing.
- **User**: approves the final design before any implementation and resolves conflicts via AskQuestion.

## When to Invoke

Invoke when the user wants to:

- create a new skill;
- modify or improve an existing skill;
- design or discuss requirements for a skill;
- review a skill's design or implementation;
- validate or test a skill;
- troubleshoot a skill that is not behaving as intended.

## When NOT to Invoke

Do not invoke when:

- the user wants to create/edit a normal document that is not a skill;
- the user wants ordinary writing unrelated to skill creation/maintenance;
- the user asks a general question about skills without asking to create, modify, review, validate, or test one;
- the user simply wants to use an existing skill;
- the task is completely unrelated to skills.

## Golden Rules

1. Skill Creator does not write skill files: it may read, inspect, design, ask, prepare instructions, validate, test, and report only.
2. GeneralTask writes only from the approved design.
3. No implementation before explicit user approval.
4. Skill Creator has read/inspect/verify authority but does not own writing.
5. The handoff to GeneralTask must include approved requirements, scope, files, constraints, and validation/testing expectations.
6. GeneralTask reports what it created or modified and any problems encountered.
7. Skill Creator owns verification: it validates and tests the implementation.
8. No bypasses: small changes are not an exception; the writing boundary and approval gate always apply.
9. Revision loop: identify failure, determine cause, user decision or GeneralTask fix, then validate, then test.
10. Do not declare completion until the approved design, validation, testing, and critical-issue requirements are satisfied.

## Execution Workflow

1. **Understand Request**: read the request; determine purpose, scope, expected behavior, inputs, outputs, constraints, and integrations. Do not assume important missing requirements; ask when unclear. Preserve established rules unless the user explicitly approves a change. Do not write files at this stage.
2. **Check Existing Rules & Resources**: inspect AGENTS.md, existing SKILL.md files, agents, tools, workflows, project structure, and similar skills. Determine conventions to reuse. Do not modify anything during inspection.
3. **Identify Missing/New Requirements**: classify requirements as existing, new, unclear, or conflicting. Never silently invent important requirements; ask about important new or unclear ones; ask the user to resolve conflicts; continue only when required decisions are clear.
4. **Design the Skill**: cover purpose, scope, when to invoke, when not to invoke, workflow, inputs, outputs, tools/agents/skills, rules, constraints, error handling, escalation, validation, testing, and completion criteria. Discuss with the user.
5. **Final Design Approval**: present the complete design, clearly identifying agreed requirements, new requirements, assumptions, and unresolved questions. Require explicit user approval. No approval = no implementation.
6. **Handoff to GeneralTask**: prepare complete implementation instructions including approved requirements and constraints, skill name/location, required files, expected SKILL.md content/structure, validation and testing requirements, and defined allowed scope. GeneralTask performs the writing. If it finds an unclear requirement, return to the user/design stage rather than guessing.
7. **Validate**: after GeneralTask finishes, confirm files exist, read the implementation, compare against the approved design, verify all approved requirements and invocation/non-invocation rules and project conventions, and run available validation checks. On failure, identify the exact cause: implementation error goes to GeneralTask, design/new requirement goes to the user, then revalidate. Never silently ignore a failure.
8. **Test**: test actual behavior, not just structure: when-to-invoke scenarios, when-not-to-invoke scenarios, main workflow, important edge cases, required tool/agent/skill interactions, and the GeneralTask writing boundary. On failure, record expected vs actual behavior and classify the cause (implementation/design/missing requirement/environment). Implementation goes to GeneralTask; design/missing requirement goes to the user; environment is reported honestly. Validate again after implementation fixes before retesting.
9. **Final Approval & Completion**: mark complete only when the approved design is implemented, validation passes, required tests pass, no unresolved critical issues remain, and no unapproved requirements were introduced. Report what was created/updated, validation result, test result, remaining warnings/limitations, and skill location.

## Error Handling & Escalation

- Requirements unclear: stop and ask; do not guess.
- Existing-rule conflict: identify it and ask which requirement takes priority; do not silently override.
- GeneralTask failure: determine whether it is an unclear requirement, implementation problem, missing tool/resource, or existing-rule conflict. Ask the user when a design decision is needed; otherwise provide corrected instructions. Never bypass the GeneralTask writing boundary.
- Validation failure: compare with the approved design. Implementation problem goes to GeneralTask; design/new requirement goes to the user. Then validate again.
- Testing failure: classify as implementation, design, missing requirement, or environment/tool limitation. Fix or escalate appropriately, and validate again before retesting after implementation changes.
- Testing discovers a new requirement: stop, explain it, and ask the user whether to add it. Testing cannot authorize a new requirement by itself. If approved, update design, send to GeneralTask, validate, and test again.
- GeneralTask makes an unapproved change: do not silently accept it. If unnecessary, have GeneralTask remove/revert it; if it represents a genuinely new requirement, ask the user. Then validate and test again.
- Validation and testing disagree: do not declare success. Determine whether the disagreement comes from implementation, validation rules, test design, or requirements, resolve it, and rerun the affected checks.

## Validation

Perform structural checks on the target SKILL.md after GeneralTask writes it:

- File exists at `.opencode/skills/<name>/SKILL.md` and `name` matches the folder.
- Frontmatter is valid YAML and includes a `name` and `description`.
- Required sections are present (Purpose, When to Invoke, When NOT to Invoke, workflow, error handling, completion).
- No duplicated workflow logic already defined elsewhere (AGENTS.md or other skills).
- No PKM-only contamination (no status field, no Changelog, no template headings).
- References resolve and the file adheres to opencode skill conventions.

On failure, follow the Error Handling rules above.

## Testing

Test actual behavior using throwaway artifacts only (no production changes):

- Positive invocation: a skill task triggers the orchestrator.
- Negative invocation: a non-skill task does not trigger the orchestrator.
- Main workflow: a real create/modify task runs end to end.
- GeneralTask boundary: verify the orchestrator never writes the target SKILL.md.
- One controlled error path (e.g., unclear requirements or an approval refusal).

Clean up all throwaway artifacts afterward and confirm the working tree matches its pre-test state.

## Completion Gate

Declare completion only when ALL of these hold:

- The approved design is implemented.
- Validation passes.
- Required tests pass.
- No unresolved critical issues remain.
- No unapproved requirements were introduced.

Report what was created/updated, the validation result, the test result, any remaining warnings/limitations, and the skill location.

## Note to User

After a skill is created or modified, quit and restart opencode for the changes to take effect.
