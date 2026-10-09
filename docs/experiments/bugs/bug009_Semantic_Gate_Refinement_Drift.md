---
title: "BUG-009: Monotonic Semantic Gate Drift on Refinement Loopback"
date: 2026-09-08
tags: [bugs, semantic-gate, reverse-prompt, hitl, usem, refinement, loopback]
status: resolved
---

# BUG-009: Monotonic Semantic Gate Drift on Refinement Loopback

## 1. Metadata
- **Bug ID:** `BUG-009`
- **Component / Phase:** `src/nodes/semantic_gate_node.py` / `src/nodes/reverse_prompt.py` / `src/core/state.py` / Phase 3, Phase 3b, Phase 6
- **Status:** Resolved
- **Date Discovered:** 2026-09-08
- **Date Resolved:** 2026-09-08
- **Discovered By:** Pipeline Flow Testing & Operator Intent Refinement Audit.

---

## 2. Problem Description & Symptoms

When an operator entered the Phase 3b Human-in-the-Loop clarification loop (or the Phase 6 RADG replan loop) and submitted refinement feedback (such as relaxing GSNR thresholds, avoiding new links/nodes, or modifying routing endpoints):
1. The `pddl_parser_node` successfully received the feedback via `state["error_context"]` and generated updated PDDL constraints.
2. The `reverse_prompt_node` accurately reconstructed the updated PDDL into an updated natural language summary.
3. However, upon reaching `semantic_gate_node`, the evaluated Semantic Uncertainty ($U_{sem}$) monotonically *increased* rather than decreased with each refinement turn.
4. Because $U_{sem} > \tau_{sem}$ (default 0.3), the Semantic Gate repeatedly failed, re-triggering the `hitl_clarify` interrupt indefinitely. The operator was trapped in an inescapable clarification cycle even when the system's PDDL and reverse-prompting reconstruction adhered 100% to the operator's instructions.

---

## 3. Diagnostic & Root Cause Analysis

### 3.1 Disconnected Semantic State (Structural Flaw)
In `src/nodes/semantic_gate_node.py`, Layer 2 evaluation (`_score_semantic_agreement`) compared the LLM reconstruction against `state.get("enriched_intent")`.
However, `enriched_intent` was generated once at $k=0$ in `intent_ingest_node` and remained static. The operator's refinement feedback (`error_context`) was consumed and cleared by `pddl_parser_node` without being preserved in state or passed down to the Semantic Gate. Consequently, the Semantic Gate was evaluating the *new, refined* reconstruction against the *unmodified, stale* turn-0 intent.

### 3.2 Misaligned Evaluator Prompt (Prompt Engineering Flaw)
The agreement judge prompt (`_AGREEMENT_SYSTEM_PROMPT`) instructed the evaluator LLM to rate how closely the reconstruction captured the `ORIGINAL INTENT` and explicitly penalized modified constraints:
`"0.6 = Some constraints are missing or changed."`
When the operator legitimately relaxed GSNR from 20 dB to 12 dB or added `avoid-node Munich`, the evaluator LLM observed these changes relative to the turn-0 prompt and classified them as unrequested alterations, assigning high divergence ($d_{sem} \ge 0.6$).

### 3.3 Lack of Loop Termination Guard ($N_{max} = 3$)
As defined in [[thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gates|Thesis Section 3.4.4]], the system requires an explicit iteration bound $N_{max} = 3$ to prevent infinite negotiation cycles and protect the LLM context window from token saturation and attention degradation. No counter or cancellation boundary existed in `AgentState` or `hitl_clarify_node`.

---

## 4. Resolution Plan & Implementation

A joint **structural state** and **prompt engineering** solution was enacted:

1. **State Schema Extension (`src/core/state.py`):**
   Added `refinement_history: list[str] | None` and `refinement_count: int | None` to `AgentState` to record the cumulative feedback trail across all clarification and replan cycles.

2. **Refinement Accumulation & Context Window Protection (`src/nodes/reverse_prompt.py`):**
   - In `hitl_clarify_node`, when an operator chooses `refine`, the feedback is appended to `refinement_history` and `refinement_count` is incremented.
   - Enforced $N_{max} = 3$: If `refinement_count >= 3`, the node halts execution with a cancellation `interrupt(status="aborted")` explaining that the maximum refinement limit was reached to prevent context window saturation and token budget exhaustion.
   - Updated `hitl_clarify_route` to route to `"__end__"` upon cancellation or abort.

3. **RADG Replan Synchronization (`src/nodes/radg_node.py`):**
   Synchronized `radg_node` so that constraint relaxation feedback during Phase 6 replans also appends to `refinement_history` and increments `refinement_count`.

4. **Parser Prompt Context Propagation (`src/nodes/pddl_parser.py`):**
   Updated `pddl_parser_node` to supply the full accumulated `refinement_history` into the PDDL generation prompt.

5. **Effective Intent Construction & Evaluator Prompt Tuning (`src/nodes/semantic_gate_node.py`):**
   - Constructed the **effective reference intent** combining `enriched_intent` with the accumulated `refinement_history`.
   - Updated `_AGREEMENT_SYSTEM_PROMPT` to evaluate agreement against the operator's current intended goals, clarifying that reflecting requested refinements is faithful adherence ($d_{sem} \to 0.0$), not divergence.

---

## 5. Verification

- **Unit Tests:**
  - `tests/unit/test_semantic_gate.py`: Verified `semantic_gate_node` constructs effective intent incorporating `refinement_history` and passes gate.
  - `tests/unit/test_pipeline_nodes.py`: Verified `hitl_clarify_node` accumulates `refinement_history`, increments `refinement_count`, and triggers context-window protection abort at $N_{max}=3$.
- **End-to-End Tests (`tests/unit/test_e2e_pipeline_flow.py`):**
  - Verified multi-turn refinement loop convergence with accumulated feedback.
  - Verified $N_{max}=3$ cancellation interrupt and graceful termination.
- **Full Test Suite:** 275 passing tests across all modules (`uv run pytest`).
- **Code Quality:** Zero lint errors across `src/` (`uv run ruff check src/`).

---

## 6. Cross-References
- [[Architecture_v5]] — System architecture and Phase 3 workflow.
- [[architecture/features/semantic_gate]] — Semantic gate feature documentation.
- [[architecture/features/reverse_prompt]] — Reverse prompting and HITL feature documentation.
- [[thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gates]] — Formal Monotonic Constraint Preservation and convergence proofs.
- [[experiments/Bug_Registry]] — Bug index.
