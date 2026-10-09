---
title: "Feature: PDDL Parser & CFG Validator"
date: 2026-08-07
tags: [feature, pddl, parser, validator, llm, phase2, core, nodes]
status: active
---

# Feature: PDDL Parser & CFG Validator

## 1. Architecture Placement
**Phase 2: PDDL Parsing (CFG Validated)** | [[Architecture_v5]]

Implements the neurosymbolic "LLM as translator" principle: the LLM acts ONLY as a natural language → formal PDDL converter. It does NOT decide routes or compute physics. A deterministic CFG regex validator then checks structural correctness, catching the most common LLM hallucination patterns before any downstream computation.

## 2. Associated Files
- **Node**: [src/nodes/pddl_parser.py](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) — `pddl_parser_node(state) -> dict`
- **Validator**: [src/core/pddl_validator.py](file:///home/felipeab/MultiAgentON/src/core/pddl_validator.py) — `validate_pddl_syntax()`, `extract_pddl_sections()`
- **State fields written**: `pddl_constraints: str | None`, `pddl_valid: bool | None`, `error_context: str | None`
- **Tests**: [tests/unit/test_pipeline_nodes.py](file:///home/felipeab/MultiAgentON/tests/unit/test_pipeline_nodes.py), [tests/unit/test_pddl_validator.py](file:///home/felipeab/MultiAgentON/tests/unit/test_pddl_validator.py)

## 3. PDDL Subset Used
The system uses a simplified PDDL problem domain for optical routing:

```pddl
(define (problem <name>)
  (:domain optical-network)
  (:objects <nodes> - node)
  (:init <topology predicates: (connected A B), (link-active A B), ...>)
  (:goal
    (and
      (route <source> <target>)
      (min-gsnr <value>)       ; optional
      (bandwidth <value>)      ; optional (e.g. 100, 200, 400 Gbps)
      (avoid-node <node>)      ; optional
      (avoid-link <src> <dst>) ; optional
      (max-hops <n>)           ; optional
    )
  )
)
```

## 4. How it Works
1. Reads `enriched_intent` (which contains the dynamically injected `Topology Context:` from Phase 1 Optical RAG) from state. If `error_context` exists (refinement loop), appends operator feedback to the prompt.
2. Calls Kimi LLM with `PDDL_SYSTEM_PROMPT` — instructs the model to use the topology provided dynamically in `enriched_intent` and output ONLY PDDL, no markdown.
3. Strips markdown code fences if the LLM wraps the output (common LLM behavior).
4. Validates via `validate_pddl_syntax()` — performs S-expression tokenization and AST parsing: checks balanced parentheses, `(define ...)` wrapper, presence of `:domain`, `:objects`, `:init`, `:goal` sections, and goal predicate production rules (arities and numeric types).
5. Returns `pddl_valid=True/False` and `error_context` with any CFG error messages.

### Refinement Loop Support (Intent Reconciler Integration)
When the operator submits refinement feedback via HITL (Phase 3b [[architecture/features/reverse_prompt|reverse_prompt]] or Phase 6 [[architecture/features/radg|radg_node]] replan), `pddl_parser_node` detects the presence of feedback in `error_context` or `refinement_history`. Rather than naively concatenating raw feedback strings, it delegates to [[architecture/features/intent_reconciler]] (`reconcile_and_enrich_intent`):
1. An LLM reasoning step classifies the update scope (`FULL_REPLACEMENT` vs `PARTIAL_UPDATE`) and calculates the constraint delta.
2. If endpoints changed, Mock GraphRAG re-extracts the $k$-hop subtopology.
3. The reconciled operational goal is saved as `active_intent`.
4. `pddl_parser_node` generates PDDL from this unified, non-contradictory `active_intent`.

## 5. CFG Validator Details (`src/core/pddl_validator.py`)
- **Layer 1 (Structural)**: Feeds into $U_{sem}$ Layer 1 check
- Checks performed via AST tokenization:
  1. Non-empty string and balanced parentheses depth
  2. `(define (problem <name>)...)` outer wrapper
  3. All required sections: `:domain`, `:objects`, `:init`, `:goal`
  4. Predicate grammar rules: `(route <src> <dst>)`, `(avoid-node <node>)`, `(avoid-link ...)`, `(max-hops <int>)`, `(min-gsnr <num>)`
- Design: permissive on unknown optional sections (`:constraints`, `:metric`) for domain extensibility

## 6. How to Test
```bash
uv run pytest tests/unit/test_pddl_validator.py tests/unit/test_pipeline_nodes.py::TestPDDLParserNode -v
```

## 7. Cross-References
- [[Architecture_v5]] — Phase 2 description
- [[architecture/features/intent_ingest]] — Produces `enriched_intent` consumed here
- [[architecture/features/reverse_prompt]] — Phase 3: validates semantic correctness after CFG validation
- [[architecture/features/symbolic_solver]] — Consumes `pddl_constraints` for path search
