---
title: "BUG-010: Stale Initial Intent and Raw Subtopology Dump in Planning Report"
date: 2026-09-08
tags: [bug, bug-010, plan-synthesizer, hitl, refinement, optical-topology, reporting]
status: resolved
---

# BUG-010: Stale Initial Intent and Raw Subtopology Dump in Planning Report

## 1. Metadata
- **Bug ID:** `BUG-010`
- **Component:** `src/nodes/plan_synthesizer.py` (Phase 7: Plan Synthesis)
- **Discovered By:** Felipe Abadia (Interactive CLI validation)
- **Date Discovered:** 2026-09-08
- **Date Resolved:** 2026-09-08
- **Severity:** High (Operational Clarity & Auditability Risk)
- **Status:** Resolved

---

## 2. Problem Description & Symptoms

During interactive multi-turn testing of the [[Architecture_v5|Architecture V5]] pipeline, an operator submitted an intent with stringent physical-layer constraints designed to intentionally violate QoT feasibility. The system correctly triggered a Human-in-the-Loop (HITL) replan interrupt at Phase 6 ([[architecture/features/radg|RADG]]), and the operator submitted refined/relaxed constraints via `Command(resume=...)`.

While the feedback successfully looped back to Phase 2 ([[architecture/features/pddl_parser|pddl_parser]]) and passed the [[architecture/features/semantic_gate|Semantic Gate]] via Effective Reference Intent evaluation ([[experiments/bugs/bug009_Semantic_Gate_Refinement_Drift|BUG-009]]), the final **Planning Report** synthesized by Phase 7 exhibited critical deficiencies:

1. **Stale Intent Display:** The Planning Report printed the static initial intent from iteration $k=0$, completely omitting the operator's refinement feedback and giving the false impression that operator instructions were disregarded.
2. **Keyword Repetition:** Rendered `Intent      : Intent: ...` due to unstripped `"Intent: "` prefix from Phase 1 (`intent_ingest`).
3. **Raw Subtopology Dump:** The entire $k$-hop subtopology JSON/text context was dumped directly into the report body (`Topology Context:\n...`).
4. **Lack of Visual Path Depiction:** The report lacked a clear, human-readable topological representation of the selected lightpath showing physical link distances and inline EDFA counts.

---

## 3. Diagnostic & Root Cause Analysis (RCA)

Investigation of `src/nodes/plan_synthesizer.py` revealed:

1. **State Blindness:** `plan_synthesizer_node` extracted the intent string exclusively via `state.get('enriched_intent')`. This variable was populated during Phase 1 (`intent_ingest_node`) and remained static across multi-turn executions. The node never inspected `state.get('refinement_history')` or `state.get('refinement_count')`, which had been introduced to resolve [[experiments/bugs/bug009_Semantic_Gate_Refinement_Drift|BUG-009]].
2. **Unsanitized Enriched Intent:** In `intent_ingest_node`, `enriched_intent` is constructed as:
   $$\text{enriched} = \text{"Intent: "} \oplus \text{summary} \oplus \text{" | Source: "} \oplus \text{src} \oplus \dots \oplus \text{"\nTopology Context:\n"} \oplus \mathcal{G}_{sub}$$
   `plan_synthesizer.py` formatted this directly with `f"Intent      : {state.get('enriched_intent')}"`, causing both the repeated keyword and the raw graph dump.
3. **Missing Topological Extraction:** `plan_synthesizer.py` did not cross-reference `state.get('candidate_paths')` with the selected route to extract hop-by-hop physical link parameters (`length_km`, `amplifiers`).

---

## 4. Resolution Plan & Implementation Details

1. **Clean Intent Extraction (`_extract_clean_base_intent`):**
   - Prioritizes extracting the original clean operator intent from `state["messages"]` (HumanMessage).
   - If falling back to `enriched_intent`, strips all raw `\nTopology Context:` text and redundant `"Intent: "` prefixes.

2. **Refinement & Operational Intent Tracking:**
   - Reads `state.get("refinement_history")` and `state.get("refinement_count")`.
   - If refinements exist:
     - Reports `Refinement Status: Refined via Operator HITL (N iterations)`.
     - Explicitly enumerates applied HITL refinements turn-by-turn.
     - Formulates and displays the **Active Operational Intent** reflecting the deployed constraints.
   - If no refinements exist, reports `Refinement Status: Autonomous Pass (0 Interrupts)`.

3. **Horizontal Optical Lightpath Graph (`_format_horizontal_path`):**
   - Matches the selected feasible route (`best_path["path"]`) against `candidate_paths` to retrieve physical `link_physics`.
   - Renders a clean horizontal ASCII/Unicode path diagram:
     ```text
     [ Berlin ] ────( 250.0 km | 2 EDFAs )────► [ Hannover ] ────( 310.0 km | 3 EDFAs )────► [ Frankfurt ]
     ```
   - Appends cumulative metrics (Total Spans, Total Fiber Distance, Total Inline EDFAs) and hop-by-hop span specifications.

4. **Executive Markdown Report Redesign:**
   - Reorganized into 5 structured sections:
     1. *Intent & Alignment Specification*
     2. *Pre-Deployment Safety Verification* (Semantic Gate $U_{sem}$ and RADG Decision Matrix)
     3. *Selected Optical Lightpath Topology*
     4. *Evaluated Candidate Routes (Physical-Layer Feasibility Table)*
     5. *Deployment Recommendation & Testbed Status*

---

## 5. Verification & TDD Evidence

### 5.1 Strict TDD Reproduction (RED)
Added three test cases to `tests/unit/test_pipeline_nodes.py`:
- `test_report_reflects_refinement_history_and_updated_intent`
- `test_report_eliminates_repeated_intent_and_topology_dump`
- `test_report_renders_horizontal_optical_path_with_links_and_edfas`

Ran `uv run pytest tests/unit/test_pipeline_nodes.py -k "TestPlanSynthesizerNode"`:
```text
FAILED test_report_reflects_refinement_history_and_updated_intent - AssertionError
FAILED test_report_eliminates_repeated_intent_and_topology_dump - AssertionError
FAILED test_report_renders_horizontal_optical_path_with_links_and_edfas - AssertionError
3 failed, 4 passed
```

### 5.2 Post-Fix Validation (GREEN)
Implemented the redesigned `plan_synthesizer_node` in `src/nodes/plan_synthesizer.py`.
Re-ran test suite:
```text
tests/unit/test_pipeline_nodes.py::TestPlanSynthesizerNode::test_returns_planning_report PASSED [ 14%]
tests/unit/test_pipeline_nodes.py::TestPlanSynthesizerNode::test_report_includes_feasible_paths PASSED [ 28%]
tests/unit/test_pipeline_nodes.py::TestPlanSynthesizerNode::test_report_handles_no_feasible_paths PASSED [ 42%]
tests/unit/test_pipeline_nodes.py::TestPlanSynthesizerNode::test_returns_ai_message PASSED [ 57%]
tests/unit/test_pipeline_nodes.py::TestPlanSynthesizerNode::test_report_reflects_refinement_history_and_updated_intent PASSED [ 71%]
tests/unit/test_pipeline_nodes.py::TestPlanSynthesizerNode::test_report_eliminates_repeated_intent_and_topology_dump PASSED [ 85%]
tests/unit/test_pipeline_nodes.py::TestPlanSynthesizerNode::test_report_renders_horizontal_optical_path_with_links_and_edfas PASSED [100%]
7 passed, 32 deselected in 0.13s
```

Full test suite verification:
```text
278 passed, 14 deselected, 3 warnings in 2.62s
```

Code quality verification:
```text
uv run ruff check src/
All checks passed!
```

---

## 6. Cross-References
- [[experiments/Bug_Registry]] — Registered as BUG-010.
- [[architecture/features/plan_synthesizer]] — Updated Phase 7 feature documentation.
- [[experiments/bugs/bug009_Semantic_Gate_Refinement_Drift]] — Upstream effective reference intent tracking.
