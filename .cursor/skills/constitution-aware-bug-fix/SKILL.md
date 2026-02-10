---
name: constitution-aware-bug-fix
description: Structured bug verification and remediation workflow that enforces project constitution compliance. Use when receiving a bug report, fixing reported issues, resolving hardcoded values, or addressing violations of project conventions. Reads the project constitution before designing fixes to ensure all changes respect established principles.
---

# Constitution-Aware Bug Remediation

## Overview

Bug fixes that ignore project conventions introduce technical debt faster than they resolve it. In a multi-LLM project, each agent may "fix" a bug differently — one hardcodes a value, another restructures the API contract, another skips error handling. This skill enforces a structured workflow that produces constitution-compliant fixes.

**Core principle:** Every fix MUST respect the project constitution. A fix that works but violates a principle is not a fix — it's a new bug.

## The Iron Law

```
NO FIX WITHOUT VERIFICATION → TRACING → CONSTITUTION CHECK → DESIGN → IMPLEMENTATION → CASCADE CHECK → VALIDATION → DOCUMENTATION
```

Skipping any phase produces incomplete or convention-violating fixes.

## When to Use

- Received a bug report (from human, CI, or another LLM)
- Found a hardcoded value, inconsistent pattern, or convention violation
- Fixing an error that spans multiple files
- Addressing a P0/P1 issue from the development plan

**Use ESPECIALLY when:**
- The bug touches config, API responses, or cross-file data flow
- Multiple files share the same hardcoded value
- The fix seems "obvious" (obvious fixes skip constitution checks)

## The Eight Phases

### Phase 1: Verify

**Never trust the report blindly.** Read the actual code at the reported location.

1. Read the file and line numbers mentioned in the report
2. Confirm the bug exists as described
3. If the bug does NOT exist or is different from reported → state actual finding
4. Note the exact scope: which lines, which values, which behavior

```
✅ "Confirmed: line 493 contains hardcoded '2026-01-20'"
❌ "The report says it's hardcoded, so let's fix it"
```

### Phase 2: Trace

**Follow the data flow across all related files.**

1. Identify what the buggy value/pattern connects to
2. Search the codebase for all occurrences of the same value/pattern
3. Map the dependency chain (e.g., config → server → sync → frontend)
4. List ALL files that need changes — not just the reported one

```
Tool usage: Grep for the hardcoded value, then read each matching file's context
```

### Phase 3: Constrain

**Read the project constitution BEFORE designing the fix.**

1. Read `.specify/memory/constitution.md`
2. Identify which principles apply to this fix
3. List the constraints the fix MUST satisfy
4. Note any existing violations that should be fixed opportunistically

```
Example constraints:
- Principle I → value must come from config.json, not hardcoded
- Principle II → API response must use {"status": "success", "data": {...}}
- Principle VII → failure must degrade gracefully, not crash
```

### Phase 4: Design

**Design a fix that addresses root cause AND respects constraints.**

1. Identify the root cause (not the symptom)
2. Design a solution that satisfies ALL constraints from Phase 3
3. If the fix requires changes in multiple files, determine dependency order
4. Consider: does this fix introduce any new edge cases?

```
Design checklist:
- [ ] Fixes root cause, not symptom
- [ ] Satisfies all applicable constitution principles
- [ ] Has a clear dependency order for multi-file changes
- [ ] Single Source of Truth is maintained (Principle VI)
```

### Phase 5: Implement

**Execute changes in dependency order.**

1. Start from the source of truth (usually `config.json`)
2. Work outward through the dependency chain
3. Each file change should be independently coherent
4. Use TODO tracking for multi-file changes

```
Typical order: config → backend → sync/scripts → frontend
```

### Phase 6: Cascade-Check

**Actively look for secondary issues introduced by the fix.**

This is the most commonly skipped phase. Ask:
- Does the fix create a new failure mode? (e.g., bootstrap failure → blank page)
- Does the fix depend on something that might not be available? (e.g., network fetch)
- Does the fix handle the unhappy path? (e.g., missing field, timeout, 404)

If secondary issues are found → apply Phases 3-5 to fix them too.

```
✅ "Bootstrap failure leaves users with blank page — adding error UI and retry"
❌ "Fix is done" (without checking failure modes)
```

### Phase 7: Validate

**Verify the fix is complete with evidence.**

1. Grep for any residual instances of the buggy pattern
2. Run linter on all modified files
3. Confirm zero violations remain

```
✅ grep returns "No matches found" for the hardcoded value
❌ "Should be fixed now"
```

### Phase 8: Document

**Create a development log entry.**

Per Constitution Principle V, record in `docs/dev/logs/YYYY-MM-DD-{description}.md`:
- Problem description (what was reported vs what was found)
- Root cause analysis
- Solution design and rationale
- All files modified
- Any cascade issues found and fixed

## Quick Reference

| Phase | Key Action | Output |
|-------|-----------|--------|
| 1. Verify | Read actual code | Bug confirmed or corrected |
| 2. Trace | Grep + read related files | Full file list + dependency map |
| 3. Constrain | Read constitution | List of applicable principles |
| 4. Design | Root cause + constraints → solution | Fix design with dependency order |
| 5. Implement | Edit in dependency order | Code changes |
| 6. Cascade-check | Check for secondary issues | New edge cases found/fixed |
| 7. Validate | Grep + lint | Evidence of completeness |
| 8. Document | Write dev log | `docs/dev/logs/` entry |

## Red Flags — STOP and Follow Process

If you catch yourself:
- Fixing the reported file without checking other files → **Phase 2**
- Designing a fix without reading the constitution → **Phase 3**
- Hardcoding a fallback value instead of reading from config → **Phase 3**
- Claiming "fixed" without grepping for residuals → **Phase 7**
- Skipping documentation "because it's a small fix" → **Phase 8**
- Not checking what happens when the fix fails → **Phase 6**

## Related Skills

- **systematic-debugging** — For root cause investigation (Phase 2 overlap)
- **verification-before-completion** — For validation evidence (Phase 7 overlap)

## Related Project Files

- **Constitution**: `.specify/memory/constitution.md` (MUST read in Phase 3)
- **Development Plan**: `docs/dev/plans/2026-02-11-development-plan.md`
- **Dev Logs**: `docs/dev/logs/` (output of Phase 8)
