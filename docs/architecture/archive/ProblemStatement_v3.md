---
title: "Problem Statement V3: QoT-Informed Intent Planning for Optical Networks"
date: 2026-06-21
tags: [thesis, definition, objective, planning-loop, hitl, qot]
status: active
supersedes: "[[concepts/archive/ProblemStatement_20260427_Felipe_Abadia]]"
---

# Problem Statement V3: QoT-Informed Intent Planning for Optical Networks

## Context
- **Thesis Title:** QoT-Informed Intent Planning for Optical Networks: A Neurosymbolic Human-in-the-Loop Approach.
- **Keywords:** Generative AI, Multi-agent LLM, Intent-based networking, Quality of Transmission (QoT), Human-in-the-Loop (HITL), Planning Loop, Neurosymbolic AI.
- **The Problem:** Translating high-level, unstructured operator intent into a *validated optical routing plan* that satisfies physical-layer constraints (SNR, GN model) remains unsolved. Existing SOTA systems either lack natural language input (AutoLight), lack formal operator validation (SJTU), or operate outside the optical domain entirely (Confucius). The planning phase — where intent is parsed, candidate paths are evaluated, and the operator iteratively refines the plan — is the critical bottleneck where LLM hallucination poses the greatest risk to network safety.
- **The Solution:** A neurosymbolic Intent Planning Loop that combines LLM-driven intent parsing with deterministic QoT evaluation and multi-turn HITL refinement. The loop produces a validated Planning Report — a structured artifact containing QoT-feasible candidate paths, trade-off analysis, and operator-approved routing decisions — that downstream provisioning systems can consume.
- **Scope Note:** This thesis focuses exclusively on the *planning phase*. Lightpath provisioning, compute scheduling, and full lifecycle Day-N operations are explicitly documented as future work. See [[Scope_Pivot_20260621]] for the rationale.

## Given
The planning system receives three dynamic layers of input:
1. **The Natural Language Intent:** A high-level, unstructured semantic request from a human operator (e.g., *"Provide a highly reliable, low-latency network slice to stream 4K VR data from the central database to an edge node for rendering"*).
2. **The Physical Network Graph $G(V,E)$:** A serialized representation of the underlying topology, encompassing vertices (optical nodes, transponders) and edges (optical fiber characteristics, link capacities, span lengths). Retrieved by the Topology Agent via RESTConf NBI.
3. **QoT Physical Parameters:** Fiber attenuation coefficients, OA gains and noise figures, span lengths, and channel configurations — the inputs to the deterministic GN model tool that evaluates path feasibility.

## Decide
The Intent Planning Loop employs a multi-turn, multi-agent coordination protocol to translate operator intent into a validated routing plan:

1. **Intent Translation & Parsing:** The Orchestrator LLM parses the natural language input to deduce numerical [[Concepts_and_Terminology|SLA]] constraints, generating a provisional constraint matrix (`sla_matrix`) detailing required bandwidth, latency, reliability, and endpoints.

2. **Topology Acquisition:** The Orchestrator delegates to the Topology Agent, which fetches the current network state via the testbed NBI. The topology snapshot populates the planning context with available nodes, links, and their physical parameters.

3. **QoT-Informed Path Evaluation:** The Orchestrator delegates to the Routing Agent, which identifies candidate paths through $G(V,E)$ and evaluates each using the deterministic QoT tool (Python GN model port). Each candidate path receives a feasibility assessment: $\{snr_{dB}, P_{rx,dBm}, feasible\}$.

4. **Planning Report Synthesis:** The Orchestrator synthesizes the results into a structured Planning Report: candidate paths ranked by QoT score, SLA constraint satisfaction, trade-off analysis, and a recommendation.

5. **Multi-Turn HITL Refinement (Reverse Prompting):** The Orchestrator presents the Planning Report to the operator via `interrupt()`. The operator may:
   - **Approve** → the plan is finalized as `approved_plan`
   - **Refine** → provide feedback (e.g., "exclude path 2", "prioritize latency over reliability") → the loop returns to step 3 with updated constraints
   - **Reject** → the loop returns to step 1 with new or clarified intent

   This cycle repeats until convergence or the iteration bound $N_{max}$ is reached.

Following strict [[Constraint_Isolation|neurosymbolic separation]], LLMs act purely as reasoning engines throughout this loop. All physical-layer math (SNR calculation, power propagation) is delegated to deterministic Python tools. No hallucination allowed for numerical outputs.

## Output
The output of the Intent Planning Loop is a validated **Planning Report** containing:
- **Candidate paths** with QoT feasibility scores ($snr_{dB}$, $P_{rx,dBm}$, feasible/infeasible)
- **SLA constraint satisfaction matrix** — which constraints each candidate path meets or violates
- **Trade-off analysis** — operator-facing comparison of viable paths
- **Approved routing decision** — the operator's final selection with justification
- **HITL refinement trace** — the conversation history documenting how the plan evolved

This Planning Report is a structured Pydantic artifact that a downstream provisioning system (future work) could consume to generate RESTConf API calls.

## Objective
The objective of the Intent Planning Loop is to maximize planning quality:

$$ \max_{\text{plan}} \Big( F_{intent}(\text{plan}) \cdot Q_{qot}(\text{plan}) \Big) \quad \text{subject to} \quad N_{hitl} \le N_{max} $$

Where:
- $F_{intent}(\text{plan})$ is the **intent fidelity** — how accurately the plan reflects the operator's original intent, measured by SLA constraint coverage and validated by HITL approval.
- $Q_{qot}(\text{plan})$ is the **QoT quality** — the physical-layer feasibility score of the selected path, determined by the deterministic GN model tool.
- $N_{hitl}$ is the number of HITL refinement iterations before convergence, bounded by $N_{max}$.

## Constraints
1. **Task-Dependent Inference Latency Budget ($T_{total, i} \le T_{budget}(type(i))$):** The planning loop operates under a "Slow Loop" paradigm — seconds to minutes are acceptable for planning, as operator interaction is inherently asynchronous. This contrasts with operational tasks (e.g., failure recovery) that would require real-time bounds.
2. **Semantic Distortion Bound ($D_{sem} \le D_{max}$):** The loss of decision-relevant information during the telemetry-to-prompt transformation is strictly bounded: $|| S_{true} - \hat{S}_{LLM} ||^2 \le D_{max}$.
3. **Context Window Saturation ($N_{tokens} \le N_{max}$):** Topology data and QoT results must be pre-compressed into compact representations to avoid context limits. The Pydantic state models serve this purpose.
4. **HITL Convergence Bound ($N_{hitl} \le N_{max}$):** The planning loop must converge within a bounded number of refinement iterations to prevent infinite loops.
5. **Policy Safety & Grammar Validation:** All structured outputs (SLA matrix, Planning Report) must pass Pydantic schema validation before being presented to the operator.

## Cross-References
- [[Scope_Pivot_20260621]] — Rationale for the scope change
- [[Architecture_v3]] — System architecture for the Intent Planning Loop
- [[Concepts_and_Terminology]] — Glossary
- [[QoT_Awareness]] — QoT feasibility concepts
- [[Constraint_Isolation]] — Neurosymbolic separation principle
