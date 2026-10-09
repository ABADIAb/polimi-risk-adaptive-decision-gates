---
title: "Feature: Symbolic Solver & Mock GraphRAG"
date: 2026-07-31
tags: [feature, symbolic-solver, graphrag, networkx, pddl, phase4, core]
status: active
---

# Feature: Symbolic Solver & Mock GraphRAG

## 1. Architecture Placement
**Phase 4: Symbolic Solver & Mock GraphRAG** | [[Architecture_v5]]

This is the "System 2" deterministic engine — the LLM is strictly forbidden from touching this phase. Given validated PDDL constraints and a topology snapshot, it extracts 3–5 candidate paths that satisfy all topological constraints, preventing token saturation by working only on a locally compressed k-hop subgraph.

**Key architectural property**: Zero LLM calls. All computation is deterministic and reproducible.

## 2. Associated Files
- **Solver (LangGraph node)**: [src/core/symbolic_solver.py](file:///home/felipeab/MultiAgentON/src/core/symbolic_solver.py) — `symbolic_solver_node(state) -> dict`
- **GraphRAG utilities**: [src/core/mock_graphrag.py](file:///home/felipeab/MultiAgentON/src/core/mock_graphrag.py) — `build_adjacency_graph()`, `extract_k_hop_neighborhood()`, `graph_to_context_string()`
- **State fields read**: `pddl_constraints`, `subtopology_snapshot` (fallback: `topology_snapshot`)
- **State fields written**: `candidate_paths: list | None`, `pddl_parsed_constraints: dict | None`
- **Tests**: [tests/unit/test_symbolic_solver.py](file:///home/felipeab/MultiAgentON/tests/unit/test_symbolic_solver.py), [tests/unit/test_mock_graphrag.py](file:///home/felipeab/MultiAgentON/tests/unit/test_mock_graphrag.py)

> **Note on placement**: `symbolic_solver.py` lives in `src/core/` (not `src/nodes/`) because it makes zero LLM calls and contains pure algorithm logic. Per the `src/` methodology, the deciding criterion is: "Would this module exist without LangGraph?" → Yes. It also exports a `symbolic_solver_node()` function that `graph.py` wires directly.

## 3. How it Works

### Step 1 — PDDL Constraint Parsing
`_parse_pddl_constraints(pddl_text)` extracts:
- `(source <name>)` → source node name
- `(destination <name>)` → destination node name
- `(avoid-node <id|name>)` → list of prohibited node names/IDs
- `(avoid-link <id>)` → list of prohibited link IDs
- `(max-hops <n>)` → maximum hop count constraint
- `(min-gsnr <val>)` → minimum GSNR threshold
- `(bandwidth <val>)` → optical capacity demand in Gbps (e.g., 100, 200, 400)

### Step 2 — Sub-Topology Reuse & Mock GraphRAG
`symbolic_solver_node` reuses `subtopology_snapshot` directly if already extracted by Phase 1 (`intent_ingest_node` via Mock GraphRAG), avoiding redundant sub-graph extraction and preventing re-querying the full testbed graph.
If not present, `build_adjacency_graph(topology)` converts the `TopologySnapshot` into a `networkx.Graph` and `extract_k_hop_neighborhood(graph, source_id, dest_id, k=2)` extracts the $k$-hop neighborhood.

### Step 3 — Topological Graph Pruning ($\widetilde{V}_{sub}, \widetilde{E}_{sub}$)
Before finding paths, the solver prunes the search graph:
- Prohibited nodes in `avoid_nodes` are removed from the graph: $\widetilde{V}_{sub} = V_{sub} \setminus \{ u \mid \text{avoid-node}(u) \}$.
- If source or destination is prohibited, the solver fails fast.
- If pruning disconnects the $k$-hop subgraph, it falls back to the pruned full graph to find detours.

### Step 4 — Yen's K-Shortest Paths
`nx.shortest_simple_paths(pruned_subgraph, source_id, dest_id, weight="length_km")` enumerates paths by ascending total fiber length. Up to `_K_PATHS=5` candidate paths are returned.

### Step 5 — PDDL Constraint Filtering
Each candidate path is checked against:
- **max-hops**: path hop count ≤ constraint
- **avoid-node**: no intermediate path node matches any prohibited node
- **avoid-link**: no path edge matches any prohibited link ID

Only paths passing all constraints are added to `candidate_paths`.

## 4. Output Format
Each entry in `candidate_paths` is a dict:
```python
{
    "nodes": ["Milano-A", "Milano-B", "Milano-C"],  # human-readable names
    "links": ["link_ab", "link_bc"],                # link IDs traversed
    "total_length_km": 60.0,                        # total fiber length
    "hops": 2                                       # hop count
}
```

## 5. How to Test
```bash
uv run pytest tests/unit/test_symbolic_solver.py tests/unit/test_mock_graphrag.py -v
```

## 6. Cross-References
- [[Architecture_v5]] — Phase 4 description
- [[architecture/features/pddl_parser]] — Produces `pddl_constraints` consumed here
- [[architecture/features/qot_tool]] — Phase 5 will validate the `candidate_paths` produced here
- [[architecture/features/testbed_client]] — Produces `topology_snapshot` consumed here
