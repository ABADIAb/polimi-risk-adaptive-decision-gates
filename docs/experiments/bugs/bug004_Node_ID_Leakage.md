---
title: "BUG-004: Node ID Leakage (node_1) in Reverse Prompting"
date: 2026-08-07
tags: [bugs, reverse-prompt, graphrag, hitl, state]
status: resolved
---

# BUG-004: Node ID Leakage (`node_1`) in Reverse Prompting

## 1. Metadata
- **Bug ID:** `BUG-004`
- **Component / Phase:** `src/core/mock_graphrag.py` / `src/nodes/pddl_parser.py` / Phase 2 & 3
- **Status:** Resolved
- **Date Resolved:** 2026-08-07
- **Commit:** `d79e400`
- **Discovered By:** E2E pipeline runs during Phase 3 (Reverse Prompting).

---

## 2. Problem Description & Symptoms
LLM reconstructed natural language intent using synthetic internal IDs like `node_1` and `node_2` instead of human-readable topology locations (e.g. `Milano-A`, `Munich`).

---

## 3. Root Cause Analysis
- `src/core/mock_graphrag.py` and internal topology snapshots exposed generic node IDs (`node_1`, `node_2`), which propagated into PDDL constraint generation and reverse prompt templates.

---

## 4. Resolution Steps
- Standardized node naming across `mock_graphrag.py`, `pddl_parser.py`, and `state.py` to strictly use human-readable optical site labels.

---

## 5. Verification
- Verified via `tests/unit/test_pipeline_nodes.py` and CLI execution logs.
- Verified via `uv run pytest`.
