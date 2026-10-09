---
title: "BUG-007: Semantic Gate Refinement Loopback Infinite Cycle"
date: 2026-08-21
tags: [bugs, semantic-gate, reverse-prompt, hitl, routing, langgraph, graph]
status: resolved
---

# BUG-007: Semantic Gate Refinement Loopback Infinite Cycle

## 1. Metadata
- **Bug ID:** `BUG-007`
- **Component / Phase:** `src/nodes/semantic_gate_node.py` / `src/core/graph.py` / Phase 3 & Phase 3b
- **Status:** Resolved
- **Date Discovered:** 2026-08-21
- **Date Resolved:** 2026-08-21
- **Discovered By:** QA Pipeline Architecture Flow Audit.

---

## 2. Problem Description & Symptoms

When an operator requests intent refinement during the Reverse Prompting HITL interrupt (or when the Semantic Gate determines that Semantic Uncertainty $U_{sem} > \tau_{sem}$ due to structural syntax errors or high semantic divergence):
1. The operator submits refinement feedback via `Command(resume={"action": "refine", "feedback": "Add avoid link constraint"})`.
2. The `reverse_prompt_node` writes `state["error_context"] = feedback` and `state["hitl_approved"] = False`.
3. The graph transitions to `semantic_gate_node`, which computes $U_{sem} > \tau_{sem}$ and invokes `semantic_gate_route`.
4. `semantic_gate_route` was hardcoded to return `"reverse_prompt"`.
5. Because the directed edge from `reverse_prompt` points to `semantic_gate`, the pipeline entered a closed two-node infinite loop:
   $$\text{reverse\_prompt} \longrightarrow \text{semantic\_gate} \longrightarrow \text{reverse\_prompt} \longrightarrow \text{semantic\_gate}$$
6. The pipeline **never returned to `pddl_parser`**, meaning `pddl_parser_node` was never invoked to consume `state["error_context"]` and regenerate the corrected PDDL constraints.

---

## 3. Diagnostic & Root Cause Analysis

### 3.1 Routing Target Mismatch
In [Architecture_v5.md](file:///docs/LLM_Wiki/wiki/architecture/Architecture_v5.md) (Section 3.1 & Phase 3) and [reverse_prompt.md](file:///docs/LLM_Wiki/wiki/architecture/features/reverse_prompt.md) (line 25), the specification explicitly requires:
> "refine $\to$ `hitl_approved=False`, `error_context=feedback`, graph continues to Semantic Gate which will route back to `pddl_parser`"

However, [semantic_gate_node.py](file:///home/felipeab/MultiAgentON/src/nodes/semantic_gate_node.py) defined `semantic_gate_route` as:
```python
def semantic_gate_route(state: AgentState) -> str:
    if state.get("usem_passed"):
        return "symbolic_solver"
    return "reverse_prompt"
```
Because the edge connecting `reverse_prompt` was linear to `semantic_gate` (`builder.add_edge("reverse_prompt", "semantic_gate")`), returning `"reverse_prompt"` bypassed `pddl_parser` entirely.

---

## 4. Resolution Plan & Implementation

1. **Update `semantic_gate_route` in [semantic_gate_node.py](file:///home/felipeab/MultiAgentON/src/nodes/semantic_gate_node.py):**
   Change the return value on gate failure (`not usem_passed`) from `"reverse_prompt"` to `"pddl_parser"`.
2. **Update Graph Routing Comments in [graph.py](file:///home/felipeab/MultiAgentON/src/core/graph.py):**
   Document that `semantic_gate_route` branches to `"symbolic_solver"` (on pass) or `"pddl_parser"` (on clarify/refine loop).
3. **Synchronize Unit Tests:**
   Update [test_graph_v5.py](file:///home/felipeab/MultiAgentON/tests/unit/test_graph_v5.py) and [test_semantic_gate.py](file:///home/felipeab/MultiAgentON/tests/unit/test_semantic_gate.py) to assert `"pddl_parser"` on gate failure.
4. **End-to-End QA Validation:**
   Add test in `test_e2e_pipeline_flow.py` exercising the complete multi-pass clarification loop with refinement feedback.

---

## 5. Verification
- Strict TDD reproduction and resolution verified with `uv run pytest tests/unit/test_e2e_pipeline_flow.py` and `uv run pytest`.
