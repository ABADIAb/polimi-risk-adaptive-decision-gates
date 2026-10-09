---
title: "BUG-008: Inadmissible Operator Approval on Semantic Gate Clarification Failure"
date: 2026-09-05
tags: [bugs, semantic-gate, reverse-prompt, hitl, routing, langgraph, graph]
status: resolved
---

# BUG-008: Inadmissible Operator Approval on Semantic Gate Clarification Failure

## 1. Metadata
- **Bug ID:** `BUG-008`
- **Component / Phase:** `src/nodes/reverse_prompt.py` / Phase 3b (`hitl_clarify_node`)
- **Status:** Resolved
- **Date Discovered:** 2026-09-05
- **Date Resolved:** 2026-09-05
- **Discovered By:** Pipeline Flow Hardening and Thesis Formalization Audit.

---

## 2. Problem Description & Symptoms

In the Phase 3b Human-in-the-Loop clarification node (`hitl_clarify_node`), when the execution engine halted due to high semantic uncertainty ($U_{sem} > \tau_{sem}$) or structural PDDL failure, the interrupt payload exposed the following options:
```python
"options": ["clarify", "refine", "approve"]
```
If an operator resumed execution selecting `"approve"` without providing clarification feedback:
1. `hitl_clarify_node` evaluated `approved = action == "approve"`, setting `state["hitl_approved"] = True`.
2. The graph proceeded to loop back to `pddl_parser`.
3. Because no corrective feedback was provided (`error_context` was empty or generic), the PDDL parser had no basis to alter its generation.
4. Furthermore, approving a plan that the Semantic Gate already rejected as syntactically malformed or linguistically contradictory created an illegal state transition, threatening an infinite loop or deploying unvalidated constraints.

---

## 3. Diagnostic & Root Cause Analysis

### 3.1 Inadmissible Action State
In [[Architecture_v5]] and [[semantic_gate]], Phase 3b is reached **strictly conditionally**:
$$\text{Triggered iff } U_{sem} > \tau_{sem} \lor \neg v_{struct}$$
An intent reaching this phase has **failed** automated verification. Unlike Phase 6 (Physical Risk Gate / RADG), where an operator might review alternative candidate paths and make a calculated risk tradeoff, Phase 3b deals with syntax and semantic integrity. An operator cannot "approve" malformed PDDL or an unparseable intent; the operator must either **clarify** (provide feedback to re-parse) or **cancel** (abort the intent).

Exposing `"approve"` was a relic of early prototyping and violated the fail-fast principle.

---

## 4. Resolution Plan & Implementation

1. **Sanitize Interrupt Options in `src/nodes/reverse_prompt.py`:**
   Restricted the interrupt choices to valid recovery actions:
   ```python
   "options": ["clarify", "refine", "cancel"]
   ```

2. **Enforce Invariant `hitl_approved = False` in Clarification:**
   Removed `approved = action == "approve"`. In `hitl_clarify_node`, `hitl_approved` is unconditionally set to `False`, forcing the pipeline through `pddl_parser` with explicit `error_context`. If an unsupported action is submitted, it safely falls back to clarification.

3. **Synchronize Unit Tests in `tests/unit/test_pipeline_nodes.py`:**
   Updated `test_approve_sets_hitl_approved_true` to `test_unsupported_action_sets_hitl_approved_false`, verifying that attempting to pass `"approve"` defaults to `hitl_approved=False`.

4. **Synchronize Thesis Documentation:**
   Updated the code snippet in Chapter 3 Section 3.5.3 (`docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/3_5_Formal_HITL_Reverse_Prompting.md`) to mirror `"options": ["clarify", "refine", "cancel"]`.

---

## 5. Verification
- Strict TDD verification via `uv run pytest tests/unit/test_pipeline_nodes.py`.
- Full regression verification: 268 passing tests (`uv run pytest`).
