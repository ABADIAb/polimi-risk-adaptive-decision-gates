---
title: "BUG-002: Refinement Feedback Loop Ignored Human interrupt() Input"
date: 2026-08-07
tags: [bugs, hitl, radg, pddl-parser, refinement]
status: resolved
---

# BUG-002: Refinement Feedback Loop Ignored Human `interrupt()` Input

## 1. Metadata
- **Bug ID:** `BUG-002`
- **Component / Phase:** `src/nodes/radg_node.py` / `src/nodes/pddl_parser.py` / Phase 6 & Phase 2 Loop
- **Status:** Resolved
- **Date Resolved:** 2026-08-07
- **Commit:** `c441318`
- **Discovered By:** User CLI testing during HITL refinement (`Not 40dB but 15dB`).

---

## 2. Problem Description & Symptoms
When the [[architecture/features/radg|RADG]] node flagged an unfeasible GSNR and triggered `interrupt()` for operator refinement, the user provided updated constraints. However, the pipeline re-executed using the **old** 40 dB constraint, generating an endless failure loop.

---

## 3. Root Cause Analysis
- `src/nodes/radg_node.py` called `interrupt()`, but failed to capture the return value (the user's response string) and did not update `state["error_context"]`.
- When routing back to `pddl_parser_node`, `error_context` was empty, causing the parser to regenerate constraints without incorporating the user's intent refinement.

---

## 4. Resolution Steps
- Captured `user_response = interrupt(...)` inside `radg_node.py`.
- Formatted a comprehensive error/refinement message and updated `state["error_context"]`.
- Allowed `pddl_parser_node` to read `error_context` and prompt the LLM to refine the PDDL parameters dynamically.

---

## 5. Verification
- Unit tests added in `tests/unit/test_radg.py`.
- Verified via `uv run pytest` and loopback execution test.
