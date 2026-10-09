---
title: "Feature: Plan Synthesizer"
date: 2026-09-08
tags: [feature, plan-synthesizer, reporting, phase7, nodes, horizontal-graph, hitl-trace]
status: active
---

# Feature: Plan Synthesizer

## 1. Architecture Placement
**Phase 7: Plan Synthesizer** | [[Architecture_v5]]

The Plan Synthesizer is the final node in the Architecture V5 pipeline. It is only reached if the [[architecture/features/radg|Physical RADG]] approves the physical feasibility of at least one candidate path. Its purpose is to compile a full, auditable execution report detailing the decisions made across the entire pipeline.

## 2. Overview
The synthesizer reads the `AgentState` accumulated throughout the graph execution and produces an executive-grade Markdown summary. This summary is optimized for terminal rendering via Rich (`rich.markdown.Markdown`) and provides complete pre-deployment transparency for the network operator.

## 3. How it Works
The node extracts and formats the following sections:
1. **Intent & Alignment Specification**:
   - Extracts clean base intent (decoupling from raw topology dumps and redundant prefixes).
   - Inspects `refinement_history` and `refinement_count`. If operator feedback was incorporated, it lists every HITL refinement turn and presents the **Active Operational Intent** reflecting the deployed constraints.
   - If no refinements were needed, marks the status as `Autonomous Pass (0 Interrupts)`.
2. **Pre-Deployment Safety Verification**:
   - Tabulates the two-gate fail-fast safety outcomes: Semantic RADG ($U_{sem} \le \tau_{sem}$) and Physical RADG ($= \text{APPROVE}$).
3. **Selected Optical Lightpath Topology**:
   - Correlates the recommended route with `candidate_paths` to extract physical link attributes (`length_km`, `amplifiers`).
   - Renders a horizontal ASCII/Unicode graph:
     ```text
     [ Berlin ] ────( 250.0 km | 2 EDFAs )────► [ Hannover ] ────( 310.0 km | 3 EDFAs )────► [ Frankfurt ]
     ```
   - Summarizes cumulative spans, total fiber distance, inline EDFAs, and per-hop link breakdown.
4. **Evaluated Candidate Routes (Physical-Layer Feasibility)**:
   - Formats a comparative Markdown table with computed GSNR, threshold, margin ($\Delta\text{GSNR}$), receiver power ($P_{rx}$), and feasibility status for all candidate paths.
5. **Deployment Recommendation & Testbed Readiness**:
   - Declares the recommended path, physical parameters, and `READY_FOR_PROVISIONING` status for testbed configuration dispatch.

## 4. Associated Files
- **LangGraph Node**: [src/nodes/plan_synthesizer.py](file:///home/felipeab/MultiAgentON/src/nodes/plan_synthesizer.py) — `plan_synthesizer_node()`
- **Unit Tests**: [tests/unit/test_pipeline_nodes.py](file:///home/felipeab/MultiAgentON/tests/unit/test_pipeline_nodes.py) — `TestPlanSynthesizerNode`

## 5. Inputs / Outputs
- **Input (State)**: `messages`, `enriched_intent`, `refinement_history`, `refinement_count`, `usem_score`, `usem_passed`, `radg_decision`, `candidate_paths`, `qot_results`.
- **Output (State)**: `planning_report` (str), `messages` (AIMessage containing the report).

## 6. Pipeline Node Evolution
- **Sprint 2:** Simple stub returning text placeholder.
- **Sprint 3:** Integrated Architecture V5 dual-risk trace (Semantic + Physical Risk).
- **Sprint 4 (BUG-010 Resolution):** Upgraded to an executive-grade Markdown reporting engine with horizontal optical lightpath graph, span physics breakdown, clean intent extraction, and full HITL refinement traceability.

## 7. Cross-References
- [[Architecture_v5]] — Phase 7 description
- [[architecture/features/radg]] — Gate that conditionally routes to this node
- [[architecture/features/qot_tool]] — Generates the QoT results synthesized here
- [[experiments/bugs/bug010_Planning_Report_Intent_and_Topology]] — Resolution of stale intent and raw topology dump

