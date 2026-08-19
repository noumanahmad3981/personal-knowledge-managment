---
name: kb-pipeline
description: Orchestrates the knowledge base documentation pipeline (epic → subtask → draft → validation → review → approval). Use when starting an epic, subtask, or document draft in this project.
---

# kb-pipeline Orchestrator

This skill orchestrates the workflow defined in **AGENTS.md**. AGENTS.md is
the single source of truth; read it before executing and follow its section
rules. Do not restate workflow logic here.

## Execution Protocol

### Step 1: Intake

Ask the user for these values using the question tool:
- Section: Knowledge | Research | Projects | Ideas
- Area: subdirectory name (e.g., "FastAPI")
- Topic: filename without .md (e.g., "fastapi-introduction")
- Title: human-readable title
- Status: initial status for the section

Store these values for subsequent steps.

### Step 2: Draft (AGENTS.md §1)

Use the Task tool to launch a **GeneralTask** subagent with this prompt:

```
Create a knowledge base document:
- Path: pkm/<Section>/<Area>/<topic>.md
- Template: <section>.md from pkm/Templates/
- Title: "<title>"
- Status: <status>
- Date: <today's date>
- Author: pkm

Requirements:
- All YAML frontmatter fields from template
- H1 matches filename stem
- All template body headings present
- Changelog with dated entry
- Substantive content in each section
```

Wait for GeneralTask to complete. Verify the file was created.

### Step 3: Auto Validation (AGENTS.md §2)

Run validation using bash:

```bash
python3 pkm/scripts/validator.py pkm/<Section>/<Area>/<topic>.md
```

Parse the output. Look for `OVERALL: PASS` or `OVERALL: FAIL`.

If `OVERALL: PASS` → continue to Step 4.

If `OVERALL: FAIL` → go to Step 3a.

### Step 3a: Fix Validation Failures

1. Read the validator output to identify all `[FAIL]` lines
2. Launch GeneralTask with this prompt:

```
Fix these validation errors in pkm/<Section>/<Area>/<topic>.md:
<paste each [FAIL] line from validator output>

After fixing, ensure the document passes all 9 validation checks.
```

3. Re-run validator.py (Step 3)
4. Repeat until PASS or maximum 10 attempts reached

### Step 4: Parallel Independent Reviews (AGENTS.md §3)

Read the document content using the read tool.

Launch three reviewers **concurrently** by making three Task tool calls in the same message:

**kb-editor:**
```
Review this knowledge base document for content quality:

<paste full document content here>

Output your review as a numbered findings list in the form:
[severity] location → issue → rationale

Where severity is: critical, major, or minor.
If you have no findings, output exactly: APPROVED
```

**kb-tech-lead:**
```
Review this knowledge base document for technical correctness:

<paste full document content here>

Output your review as a numbered findings list in the form:
[severity] location → issue → rationale

Where severity is: critical, major, or minor.
If you have no findings, output exactly: APPROVED
```

**kb-architect:**
```
Review this knowledge base document for structure and information architecture:

<paste full document content here>

Output your review as a numbered findings list in the form:
[severity] location → issue → rationale

Where severity is: critical, major, or minor.
If you have no findings, output exactly: APPROVED
```

Wait for all three reviewers to complete.

### Step 5: Combined Review Report (AGENTS.md §3)

After all three reviewers complete, merge their outputs:

1. Collect findings from each reviewer
2. Deduplicate identical or near-identical findings
3. Preserve attribution (which reviewer found each issue)
4. Count by severity: critical, major, minor

Format the Combined Review Report:

```
## Combined Review Report

### Summary
- Total findings: X
- Critical: X
- Major: X
- Minor: X

### Findings
1. [severity] location → issue → rationale (from kb-editor)
2. [severity] location → issue → rationale (from kb-tech-lead)
...

### Verdict
APPROVED (if no findings) or REVISE (if findings exist)
```

### Step 6: Review History (AGENTS.md §4)

Read existing history from `pkm/.review-history.json` using the read tool.

If file doesn't exist or is empty, initialize as `{}`.

Add/update entry for this document:

```json
{
  "pkm/<Section>/<Area>/<topic>.md": {
    "current_cycle": <N>,
    "total_cycles": <N>,
    "status": "in_review",
    "cycles": [
      {
        "cycle": <N>,
        "date": "<today>",
        "findings": {
          "kb-editor": [<findings from kb-editor>],
          "kb-tech-lead": [<findings from kb-tech-lead>],
          "kb-architect": [<findings from kb-architect>]
        },
        "resolved": [],
        "recurring": [],
        "unresolved": [<list of finding indices that remain open>]
      }
    ]
  }
}
```

Detect recurring issues: if same or similar finding appears in ≥2 cycles, add to `recurring` list.

Write the updated JSON using the write tool.

### Step 7: Decision Logic (AGENTS.md §5, §6)

Evaluate conditions:

| Condition | Action |
|-----------|--------|
| Validation failed | → Step 3a (fix required) |
| Any reviewer found critical issues | → Step 8 (fix required) |
| Reviewers directly conflict (contradictory findings) | → AskQuestion tool |
| Recurring issue (≥2 cycles) | → AskQuestion tool |
| Cycle count ≥ 10 with open findings | → AskQuestion tool |
| No critical/unresolved findings | → Step 9 (approval) |

If multiple conditions apply, handle in this order: validation first, then critical findings, then conflicts, then recurring, then cycle limit.

### Step 8: Fix and Re-validate Cycle

1. Launch GeneralTask with all findings to fix:

```
Fix the following issues in pkm/<Section>/<Area>/<topic>.md:
<paste findings from Combined Review Report>

After fixing, the document should address all reviewer concerns.
```

2. Run validation (Step 3)
3. Run reviews (Step 4)
4. Update history (Step 6)
5. Increment cycle count
6. Go to Step 7

### Step 9: Final Validation (AGENTS.md §7)

Run validator.py one final time:

```bash
python3 pkm/scripts/validator.py pkm/<Section>/<Area>/<topic>.md
```

Must return `OVERALL: PASS`. If not, go to Step 3a.

### Step 10: Final Approval (AGENTS.md §7)

Verify ALL conditions:
- [ ] Final validation: PASS (from Step 9)
- [ ] Combined review: no critical findings
- [ ] Review history: no unresolved critical findings

If all conditions met:

1. Update `pkm/.review-history.json` to set status to "approved"
2. Output **Approval Summary**:

```
## Approval Summary

**Document**: pkm/<Section>/<Area>/<topic>.md
**Date**: <today>
**Cycles used**: <N>

### Reviewer Verdicts
- kb-editor: <APPROVED / X findings>
- kb-tech-lead: <APPROVED / X findings>
- kb-architect: <APPROVED / X findings>

### Validation Report
<paste validator.py output>

### Review History
- Resolved: X issues
- Recurring: X issues
- Unresolved: 0 issues

### Status: APPROVED
```

If any condition fails, go to Step 8 to fix the remaining issues.
