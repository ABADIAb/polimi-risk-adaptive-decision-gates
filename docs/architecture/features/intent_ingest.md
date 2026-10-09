---
title: "Feature: Intent Ingest Node"
date: 2026-08-07
tags: [feature, intent, ingest, llm, phase1, nodes, rag, graphrag]
status: active
---

# Feature: Intent Ingest Node

## 1. Architecture Placement
**Phase 1: Intent Ingestion & Optical RAG** | [[Architecture_v5]]

Entry point of the neurosymbolic pipeline. The operator submits a natural language request; this node parses it into a structured `IntentSummary`, performs Optical RAG subgraph context extraction using `Mock GraphRAG`, and populates `enriched_intent` and `topology_context` in the shared `AgentState`.

## 2. Associated Files
- **Node**: [src/nodes/intent_ingest.py](file:///home/felipeab/MultiAgentON/src/nodes/intent_ingest.py) — `intent_ingest_node(state) -> dict`
- **Optical RAG engine**: [src/core/mock_graphrag.py](file:///home/felipeab/MultiAgentON/src/core/mock_graphrag.py) — `extract_k_hop_neighborhood()`, `graph_to_context_string()`
- **State fields written**: `enriched_intent: str | None`, `topology_context: str | None`
- **Tests**: [tests/unit/test_intent_ingest.py](file:///home/felipeab/MultiAgentON/tests/unit/test_intent_ingest.py)

## 3. How it Works
1. Extracts the latest `HumanMessage` from `state["messages"]`.
2. Calls the Kimi LLM with `with_structured_output(IntentSummary)` — guarantees a Pydantic-validated response with `summary`, `source_node`, and `target_node`.
3. If `topology_snapshot` exists in state, calls `Mock GraphRAG` (`build_adjacency_graph()` → `extract_k_hop_neighborhood(source, target, k=2)` → `graph_to_context_string()`) to produce a serialized text summary of the relevant sub-topology (`topology_context`).
4. Builds an `enriched_intent` string appending the `Topology Context:` section.
5. Returns a partial state update with `enriched_intent`, `topology_context`, and an `AIMessage` named `"intent_ingest"`.

### IntentSummary Schema
```python
class IntentSummary(BaseModel):
    summary: str          # One-sentence intent description
    source_node: str | None  # e.g., "Milano-A"
    target_node: str | None  # e.g., "Milano-C"
```

## 4. LLM & RAG Usage
- **Model**: Kimi (`moonshot-v1-8k`) via `langchain_openai.ChatOpenAI`
- **Pattern**: `structured_output` — no free-form parsing required
- **System prompt**: Generic `INTENT_SYSTEM_PROMPT` — no hardcoded testbed topologies.
- **RAG Subgraph Radius**: $k=2$ hop neighborhood around source/target nodes.

## 5. Status
- **Optical RAG integrated**: Topology subgraph is dynamically extracted and serialized via `graph_to_context_string()`, preventing token saturation and hardcoded topologies in downstream nodes.

## 6. How to Test
```bash
uv run pytest tests/unit/test_intent_ingest.py -v
```

## 7. Cross-References
- [[Architecture_v5]] — Phase 1 description
- [[architecture/features/pddl_parser]] — Phase 2 consumes `enriched_intent` and `topology_context`
- [[architecture/features/symbolic_solver]] — Phase 4 uses networkx graph extraction for path solving
- [[architecture/features/pipeline_graph]] — Graph wiring
