---
title: "Bug Registry & Resolution Index"
date: 2026-08-21
tags: [experiments, bugs, index, neurosymbolic, qot, radg, pddl]
status: active
---

# Bug Registry & Resolution Index

This document serves as the centralized index for tracking technical bugs, edge cases, semantic drifts, and physical-layer anomalies discovered during interactive testing and execution of the [[architecture/Architecture_v5|Neurosymbolic Intent Orchestration Pipeline]].

Detailed diagnostic analyses, root causes, reproduction steps, and verified resolutions are maintained in dedicated bug documents within `docs/LLM_Wiki/wiki/experiments/bugs/`.

---

## 1. Active & Resolved Bug Index

| Bug ID | Component / Phase | Summary | Status | Date Resolved | Detailed Note |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | `qot_calculator` / `symbolic_solver` | GSNR threshold from PDDL constraints ignored during QoT validation | **Resolved** | 2026-08-07 | [[experiments/bugs/bug001_GSNR_Threshold|BUG-001 Report]] |
| **BUG-002** | `radg_node` / `pddl_parser` | Refinement loopback ignored human `interrupt()` input and retained stale constraints | **Resolved** | 2026-08-07 | [[experiments/bugs/bug002_Refinement_Loopback|BUG-002 Report]] |
| **BUG-003** | `qot_calculator` / `models` | GN-model NLI explosion (-47 dB GSNR) on short spans due to fixed +43 dB EDFA gain | **Resolved** | 2026-08-07 | [[experiments/bugs/bug003_NLI_Explosion|BUG-003 Report]] |
| **BUG-004** | `mock_graphrag` / `pddl_parser` | Synthetic node ID leakage (`node_1`) in Reverse Prompting instead of human-readable names | **Resolved** | 2026-08-07 | [[experiments/bugs/bug004_Node_ID_Leakage|BUG-004 Report]] |
| **BUG-005** | `core/state.py` & `core/models.py` | Schema duplication & type warnings between domain models and state schema | **Resolved** | 2026-08-07 | [[experiments/bugs/bug005_Schema_Duplication|BUG-005 Report]] |
| **BUG-006** | `symbolic_solver` / `pddl_parser` | Source & Target loss in solver causing fallback to arbitrary default nodes (Hannover/Leipzig) | **Resolved** | 2026-08-19 | [[experiments/bugs/bug006_Source_Target_Loss|BUG-006 Report]] |
| **BUG-007** | `semantic_gate_node` / `graph` | Refinement loopback routed to reverse_prompt instead of pddl_parser, creating infinite cycle | **Resolved** | 2026-08-21 | [[experiments/bugs/bug007_Semantic_Gate_Refinement_Loop|BUG-007 Report]] |
| **BUG-008** | `reverse_prompt` / Phase 3b | Inadmissible operator approval on Semantic Gate clarification failure in Phase 3b interrupt | **Resolved** | 2026-09-05 | [[experiments/bugs/bug008_Inadmissible_HITL_Approval_on_Gate_Failure|BUG-008 Report]] |
| **BUG-009** | `semantic_gate_node` / Phase 3 | Monotonic Semantic Gate drift on multi-turn refinement comparing against stale initial intent | **Resolved** | 2026-09-08 | [[experiments/bugs/bug009_Semantic_Gate_Refinement_Drift|BUG-009 Report]] |
| **BUG-010** | `plan_synthesizer` / Phase 7 | Stale initial intent, raw subtopology dump, and keyword repetition in Planning Report | **Resolved** | 2026-09-08 | [[experiments/bugs/bug010_Planning_Report_Intent_and_Topology|BUG-010 Report]] |

---

## 2. Cross-References
- [[Architecture_v5]] — System architecture and pipeline phases.
- [[experiments/MVP_Roadmap]] — Experimental sprints and baseline evaluation plan.
