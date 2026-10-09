---
title: "Tool Registry (Archived / Historical)"
date: 2026-09-19
tags: [tools, registry, historical, architecture]
status: archived
---

# Tool Registry

> **Historical Context:** In early iterations (Architecture V1–V3), deterministic tools were tracked in a monolithic registry note (`Tool_Registry.md`). Following the scope pivot to the V4/V5 Neurosymbolic Intent Planning Loop, tools were modularized into native Python `@tool` wrappers in `src/tools/` and core domain logic in `src/core/`.

### Active Implementations
- **QoT Tool:** [[architecture/features/qot_tool]] (`src/tools/qot_tool.py`, wrapping `src/core/qot_calculator.py`)
- **Symbolic Solver:** [[architecture/features/symbolic_solver]] (`src/core/symbolic_solver.py`)
- **GraphRAG Scoping:** [[architecture/features/intent_ingest]] (`src/core/mock_graphrag.py`)
- **PDDL Validation:** [[architecture/features/pddl_parser]] (`src/core/pddl_validator.py`)
