---
title: "Feature: Reverse Prompting & HITL Clarification Nodes"
date: 2026-09-01
tags: [feature, hitl, reverse-prompting, interrupt, semantic-gate, phase3, nodes]
status: active
---

# Feature: Reverse Prompting & HITL Clarification Nodes

## 1. Architecture Placement
**Phase 3a: Automated Reverse Prompting & Phase 3b: HITL Clarification** | [[Architecture_v5]]

Implements the formal closed-loop validation contract that prevents **semantic drift** in intent refinement without imposing unnecessary human latency on unambiguous intents.
- **Phase 3a (Automated Reverse Prompting):** The system translates PDDL back to natural language $\mathcal{I}_{recon}$ autonomously (zero interrupts), allowing the downstream [[architecture/features/semantic_gate]] to compute $U_{sem} = f(v_{struct}, d_{sem})$.
- **Phase 3b (HITL Clarification):** Triggered *only* when $U_{sem} > \tau_{sem}$ (ambiguous intent or structural syntax failure). It pauses execution via `interrupt()` to request targeted operator clarification.

## 2. Associated Files
- **Phase 3a Node**: [src/nodes/reverse_prompt.py](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py) — `reverse_prompt_node(state) -> dict` (automated, 0 interrupts)
- **Phase 3b Node & Router**: [src/nodes/reverse_prompt.py](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py) — `hitl_clarify_node(state) -> dict`, `hitl_clarify_route(state) -> str` (conditional HITL `interrupt()` and dynamic branch routing)
- **State fields written**: `hitl_reconstruction: str | None`, `hitl_approved: bool | None`, `usem_passed: bool | None`, `error_context: str | None`
- **Tests**: [tests/unit/test_pipeline_nodes.py](file:///home/felipeab/MultiAgentON/tests/unit/test_pipeline_nodes.py)

## 3. How it Works
1. **Phase 3a (`reverse_prompt_node`):**
   - Calls the LLM with `REVERSE_PROMPT_SYSTEM` — translates the formal PDDL constraints into a plain English explanation starting with "I understand you want to..."
   - Saves `hitl_reconstruction` into `AgentState` and passes control directly to `semantic_gate` with **0 human pauses**.
2. **Downstream Gate Evaluation ([[architecture/features/semantic_gate]]):**
   - If $U_{sem} \le \tau_{sem}$ (default 0.3): passes autonomously to `symbolic_solver` (Phase 4).
   - If $U_{sem} > \tau_{sem}$: routes to `hitl_clarify` (Phase 3b).
3. **Phase 3b (`hitl_clarify_node`):**
   - Pauses execution via `interrupt()` presenting the reconstructed intent, uncertainty score, PDDL validity, and error context.
   - **Context Window Protection ($N_{max} = 3$):** If `refinement_count >= 3`, halts with an abort interrupt (`status="aborted"`), preventing infinite conversational loops, attention degradation, and context window saturation as formalized in [[thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gates|Thesis Section 3.4.4]].
   - Resumes with operator decision handled by `hitl_clarify_route`:
     - `approve` (available when `pddl_valid is True`): Operator confirms the system's understanding despite borderline uncertainty. Sets `hitl_approved=True`, `usem_passed=True`, and clears `error_context`. `hitl_clarify_route` routes **directly to `symbolic_solver` (Phase 4)**, avoiding redundant re-parsing.
     - `refine` / textual feedback: Operator clarifies intent or provides corrections. Appends feedback to `refinement_history`, increments `refinement_count`, sets `hitl_approved=False`, and stores instructions in `error_context`. `hitl_clarify_route` loops back to `pddl_parser` (Phase 2).
     - `cancel`: Operator aborts execution (routed to `"__end__"`).

## 4. HITL Strategy Evolution
| Version | Phase 3 HITL Trigger |
|---------|-----------------------|
| V4 | Always-on, 3-way routing (approve/refine/reject) directly in this node. |
| V5 (Initial) | Always-on, pauses on every intent even when $U_{sem} \le \tau_{sem}$. |
| **V5 (Refined / Current)** | **Risk-Adaptive Decoupling & Fast-Track**: Phase 3a is automated (0 interrupts). Phase 3b (`hitl_clarify`) triggers *only* when $U_{sem} > \tau_{sem}$. Operator approval fast-tracks directly to `symbolic_solver` without redundant loop cycles. |

## 5. LangGraph interrupt() Pattern
`interrupt()` requires a **checkpointer** to be configured (e.g. `InMemorySaver()` in `compile_graph()`).

```python
# Options schema adapts dynamically to PDDL structural validity:
options = ["approve", "refine", "cancel"] if pddl_valid else ["refine", "cancel"]

response = interrupt({
    "status": "clarification_required",
    "reconstruction": reconstruction,
    "usem_score": usem_score,
    "pddl_valid": pddl_valid,
    "error_context": error_context,
    "options": options,
    "message": (
        "Semantic uncertainty is high or intent requires clarification. "
        "Please review the system's understanding and provide refined instructions."
    ),
})
```

## 6. How to Test
```bash
uv run pytest tests/unit/test_pipeline_nodes.py -k "reverse_prompt or hitl_clarify" -v
```

## 7. Cross-References
- [[Architecture_v5]] — System architecture and phase workflow
- [[architecture/features/semantic_gate]] — Computes $U_{sem}$ and routes to `hitl_clarify` or `symbolic_solver`
- [[architecture/features/pddl_parser]] — Generates PDDL consumed by Phase 3a; receives feedback from Phase 3b
- [[architecture/features/symbolic_solver]] — Phase 4 executed upon autonomous or clarified pass
- [[architecture/features/pipeline_graph]] — StateGraph topology wiring
