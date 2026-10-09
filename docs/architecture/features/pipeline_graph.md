---
title: "Feature: LangGraph Pipeline & AgentState"
date: 2026-09-01
tags: [feature, langgraph, state, graph, pipeline, core, sprint3]
status: active
---

# Feature: LangGraph Pipeline & AgentState

## 1. Architecture Placement
**Pipeline Wiring (All Phases)** | [[Architecture_v5]]

This feature defines the backbone of the entire orchestrator: the LangGraph `StateGraph` and the shared `AgentState`. Every pipeline node communicates exclusively through `AgentState` — there are no direct function calls between nodes.

## 2. Associated Files
- **Graph**: [src/core/graph.py](file:///home/felipeab/MultiAgentON/src/core/graph.py) — `build_graph()`, `compile_graph(checkpointer)`
- **State**: [src/core/state.py](file:///home/felipeab/MultiAgentON/src/core/state.py) — `AgentState` TypedDict + topology domain models
- **Entry point**: [src/main.py](file:///home/felipeab/MultiAgentON/src/main.py) — CLI runner with HITL interrupt/resume loop
- **Tests**: [tests/unit/test_graph_v5.py](file:///home/felipeab/MultiAgentON/tests/unit/test_graph_v5.py), [tests/unit/test_state_v5.py](file:///home/felipeab/MultiAgentON/tests/unit/test_state_v5.py), [tests/unit/test_e2e_pipeline_flow.py](file:///home/felipeab/MultiAgentON/tests/unit/test_e2e_pipeline_flow.py)

## 3. AgentState Schema

```python
class AgentState(TypedDict):
    # Core message history (append-only via operator.add reducer)
    messages: Annotated[list, operator.add]

    # Phase 1 — Intent Ingest (Optical RAG)
    enriched_intent: str | None
    topology_context: str | None
    subtopology_snapshot: TopologySnapshot | None

    # Phase 2 — PDDL Parser
    pddl_constraints: str | None
    pddl_valid: bool | None
    pddl_parsed_constraints: dict | None  # structured: source, dest, avoid_links, max_hops

    # Phase 3 — Automated Reverse Prompting & Semantic RADG
    hitl_reconstruction: str | None
    hitl_approved: bool | None
    usem_score: float | None
    usem_passed: bool | None

    # Phase 4 — Symbolic Solver (topology input)
    topology_snapshot: TopologySnapshot | None
    candidate_paths: list | None

    # Phase 5 & 6 — QoT Validation & Physical RADG
    qot_results: list | None
    radg_decision: str | None

    # Phase 7 — Plan Synthesizer
    planning_report: str | None

    # Error tracking
    error_context: str | None
```

## 4. Graph Topology (V5)

```
START → intent_ingest → pddl_parser → reverse_prompt → semantic_gate
  → (usem_passed == True)  → symbolic_solver → qot_validation → radg
      → (approve) → plan_synthesizer → END
      → (replan)  → [HITL interrupt in radg] → pddl_parser (loop)
  → (usem_passed == False) → hitl_clarify [Phase 3b HITL interrupt]
      → (approve & pddl_valid) → symbolic_solver (direct bypass to Phase 4)
      → (refine / feedback)   → pddl_parser (clarification loop)
```

Key V5 components in `src/core/graph.py`:
- `reverse_prompt_node` — Phase 3a automated PDDL $\to$ NL reconstruction (zero interrupts).
- `semantic_gate_node` + `semantic_gate_route` — Phase 3 mathematical evaluation of $U_{sem} = f(v_{struct}, d_{sem})$. Routes to `symbolic_solver` (pass) or `hitl_clarify` (fail).
- `hitl_clarify_node` + `hitl_clarify_route` — Phase 3b human clarification via `interrupt()`. Conditionally routes directly to `symbolic_solver` if operator approves an already valid PDDL constraint set, or loops back to `pddl_parser` with `error_context`.
- `radg_node` + `radg_route` — Phase 6 Physical RADG, evaluating $\text{QoT}_{valid}$ and executing auto-approve or replan `interrupt()`.

## 5. Checkpointer & Serialization
`compile_graph(checkpointer=...)` is required for `interrupt()` to work. Without a checkpointer, `interrupt()` will raise a `RuntimeError`.

To support complex domain models (such as `TopologySnapshot`) across checkpoints without triggering LangGraph msgpack serialization warnings, `ALLOWED_MSGPACK_MODULES` is defined in `src/core/state.py` and passed to `JsonPlusSerializer`:

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from src.core.state import ALLOWED_MSGPACK_MODULES

checkpointer = InMemorySaver(
    serde=JsonPlusSerializer(allowed_msgpack_modules=ALLOWED_MSGPACK_MODULES)
)
graph = compile_graph(checkpointer=checkpointer)

# Happy path with clear intent runs from START to END with 0 interrupts!
final_result = graph.invoke(initial_state, config={"configurable": {"thread_id": "session-1"}})
```

## 6. How to Test
```bash
uv run pytest tests/unit/test_graph_v5.py tests/unit/test_state_v5.py tests/unit/test_e2e_pipeline_flow.py -v
```

## 7. Cross-References
- [[Architecture_v5]] — Full pipeline diagram and phase descriptions
- [[architecture/features/reverse_prompt]] — Automated reverse prompting and HITL clarify node
- [[architecture/features/semantic_gate]] — Semantic uncertainty evaluation and routing
- [[architecture/features/symbolic_solver]] — Wired into StateGraph from `src/core/`
