---
title: "BUG-006: Source and Target Loss in Symbolic Solver Leading to Erroneous Routes"
date: 2026-08-19
tags: [bugs, symbolic-solver, pddl-parser, intent, graphrag, nobel-germany]
status: resolved
---

# BUG-006: Source and Target Loss in Symbolic Solver Leading to Erroneous Routes

## 1. Metadata
- **Bug ID:** `BUG-006`
- **Component / Phase:** `src/core/symbolic_solver.py` / `src/nodes/pddl_parser.py` / Phase 2 & Phase 4
- **Status:** Resolved
- **Date Discovered:** 2026-08-19
- **Date Resolved:** 2026-08-19
- **Discovered By:** User interactive CLI testing (`Establish a service between Munich and Cologne`).

---

## 2. Problem Description & Symptoms

When an operator executes a query specifying source and target endpoints on the Nobel-Germany topology:
```text
Intent: Establish a service between Munich and Cologne.
```
1. **Phase 1 (`intent_ingest_node`)** correctly parses the natural language request and extracts:
   ```text
   Source: Munich | Target: Cologne
   ```
2. However, downstream in **Phase 4 (`symbolic_solver_node`)**, the solver logs:
   ```text
   [symbolic_solver] Symbolic solver found 5 candidate path(s) from 'None' to 'None'.
   ```
3. At the end of the pipeline, the synthesizer presents paths starting at **Hannover** and ending at **Leipzig** (the default first and last nodes in `MockTestbedClient`), completely ignoring the operator's Munich $\to$ Cologne intent.

---

## 3. Diagnostic & Root Cause Analysis

An architectural trace of the pipeline identified three interconnected root causes:

### 3.1 PDDL Goal Grammar Mismatch
- In [pddl_parser.py](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py), the `PDDL_SYSTEM_PROMPT` instructs the LLM to output routing goals in the standard PDDL format:
  ```pddl
  (:goal
    (and
      (route Munich Cologne)
    )
  )
  ```
  (or variations like `routed`, `route-traffic`, `path`).
- In [symbolic_solver.py](file:///home/felipeab/MultiAgentON/src/core/symbolic_solver.py), `_parse_pddl_constraints` **only** contained regular expressions searching for `(source <node>)` and `(destination <node>)`.
- Because the LLM followed the system prompt and emitted `(route Munich Cologne)` inside `:goal`, `_parse_pddl_constraints` failed to extract both endpoints and returned `constraints["source"] = None` and `constraints["destination"] = None`.

### 3.2 Insecure Silent Fallback in Symbolic Solver
- When `source_id` or `dest_id` resolved to `None`, lines 234–239 of `symbolic_solver.py` fell back to:
  ```python
  if source_id is None:
      node_ids = list(full_graph.nodes)
      source_id = node_ids[0] if node_ids else None
  if dest_id is None:
      node_ids = list(full_graph.nodes)
      dest_id = node_ids[-1] if node_ids else None
  ```
- In the SNDlib Nobel-Germany topology, `node_ids[0]` corresponds to `Hannover` and `node_ids[-1]` to `Leipzig`. This silent fallback computed paths for arbitrary endpoints rather than triggering a clean error or inspecting pipeline state fallbacks.

### 3.3 Strict Node Name Resolution
- `_resolve_node_id` in `symbolic_solver.py` only evaluated exact string equality against `attrs.get("name")`. It lacked case-insensitive matching and did not check if the string was already a valid `node_id`.

---

## 4. Resolution Plan & Implementation

1. **Enhanced PDDL Parsing (`symbolic_solver.py`):**
   - Expand `_parse_pddl_constraints()` with multi-pattern regex matching:
     - Combined route predicates: `(route <src> <dst>)`, `(routed <src> <dst>)`, `(path <src> <dst>)`, `(route-traffic <src> <dst>)`, `(service <src> <dst>)`, `(connect <src> <dst>)`.
     - Individual endpoint predicates: `(source <src>)`, `(destination <dst>)`, `(target <dst>)`, `(sink <dst>)`, `(src <src>)`, `(dst <dst>)`.
2. **Robust Case-Insensitive Node Resolution:**
   - Enhance `_resolve_node_id()` to support case-insensitivity and direct `node_id` keys.
3. **State Defense Fallback:**
   - If PDDL extraction fails to yield endpoints, extract `Source` and `Target` from `state.get("enriched_intent")`.
   - If endpoints are still missing, fail gracefully with an explicit warning rather than routing between arbitrary nodes.
4. **Prompt Harmonization (`pddl_parser.py`):**
   - Ensure `PDDL_SYSTEM_PROMPT` provides clear examples for `:goal (and (route <src> <dst>))`.

---

## 5. Verification
- Strict TDD unit tests added to `tests/unit/test_symbolic_solver.py`:
  - Regex validation across all PDDL goal variations (`route`, `routed`, `target`, `destination`).
  - Nobel-Germany 17-node pathfinding test confirming candidate paths specifically connect `Munich` $\to$ `Cologne`.
  - Enriched intent fallback verification.
- Test execution verified with `uv run pytest`.
