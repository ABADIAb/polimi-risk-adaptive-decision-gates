---
title: "Problem Statement V4: Neurosymbolic Intent Orchestration for Optical Networks"
date: 2026-07-06
tags: [thesis, definition, objective, planning-loop, hitl, neurosymbolic, pddl]
status: active
supersedes: "[[archive/ProblemStatement_v3]]"
---

# Problem Statement V4: Neurosymbolic Intent Orchestration for Optical Networks

## Context
- **Thesis Title:** Neurosymbolic Orchestration of Intents for Optical Networks: A Graph-Aware Human-in-the-Loop Approach.
- **Keywords:** Generative AI, Multi-agent LLM, Intent-based networking, Quality of Transmission (QoT), Human-in-the-Loop (HITL), Neurosymbolic AI, PDDL.
- **The Problem:** Purely generative LLM frameworks fail in optical network planning due to three critical bottlenecks: (1) **Token Budget Saturation** when injecting massive optical topologies into the prompt; (2) **Hallucinated Physics**, where the LLM proposes paths that violate nonlinear optical constraints (like GSNR); and (3) **Semantic Drift** during Human-in-the-Loop (HITL) refinement, where conversational ambiguity leads to infinite loops and dropped constraints.
- **The Solution:** A Neurosymbolic Pipeline that enforces a strict "LLMs reason, tools calculate" separation. Intent is parsed into deterministic PDDL constraints; Optical GraphRAG limits topology exposure; Reverse Prompting mathematically bounds HITL convergence; and a Symbolic Solver filters valid topologies before delegating exact physical-layer calculations to a deterministic QoT tool.

## Given
The planning system receives:
1. **The Natural Language Intent:** A high-level, unstructured semantic request from a human operator.
2. **The Physical Network Graph $G(V,E)$:** Extracted from the SDON testbed via RESTConf/SSH.
3. **QoT Physical Parameters:** Fiber attenuation coefficients, OA gains, and channel configurations to compute deterministic GN model feasibility.

## Decide
The pipeline operates through the following deterministic sequence:

1. **Optical RAG + Intent Parsing:** The LLM receives the operator intent, enriched with ITU-T or specific domain standards, and translates it into formal PDDL (Planning Domain Definition Language) constraints, protected by a CFG validator.
2. **Formal HITL (Reverse Prompting):** The PDDL state is translated back into natural language by an inverse function. The operator approves this precise reconstruction, eliminating semantic drift and guaranteeing intent convergence.
3. **Symbolic Solver + GraphRAG:** A Python-based symbolic solver fetches only the necessary $k$-hop sub-graph from the topology (Mock GraphRAG) to avoid context saturation, then extracts a bounded set of structurally valid paths satisfying the PDDL.
4. **QoT Validation:** Only these structurally valid paths are sent to the Python QoT Tool (GNPy port) to calculate precise GSNR and receiver power feasibility, preventing computational explosion.
5. **Synthesis:** The Orchestrator produces a final, auditable Planning Report for testbed provisioning.

## Output
The output of the Neurosymbolic Intent Pipeline is a validated **Planning Report** containing:
- **Structurally Valid Paths** with verified QoT feasibility scores ($snr_{dB}$, $P_{rx,dBm}$).
- **PDDL Constraint Map** guaranteeing the logic applied to the path search.
- **Reverse Prompting Trace** — the formal conversation history documenting the operator's mathematical agreement to the plan.
- **Approved Routing Decision** — ready to be pushed to the SDON testbed.

## Objective
The objective of the Neurosymbolic Intent Orchestration is to maximize planning fidelity while minimizing token exposure and computational overhead:

$$ \max_{\text{plan}} \Big( F_{intent}(\text{plan}) \cdot Q_{qot}(\text{plan}) \Big) \quad \text{subject to} \quad \text{Token Exposure} \le T_{max} \text{ and } N_{hitl} \le N_{max} $$

Where:
- $F_{intent}(\text{plan})$ is the intent fidelity, mathematically bound by Reverse Prompting.
- $Q_{qot}(\text{plan})$ is the QoT physical quality verified by the GNPy port.
- $T_{max}$ is the bounded context window protected by Optical GraphRAG.
- $N_{hitl}$ is the bounded number of HITL refinement iterations.

## Cross-References
- [[Scope_Pivot_20260706]] — Rationale for abandoning the purely generative loop.
- [[Architecture_v4]] — System architecture mapping for the neurosymbolic pipeline.
