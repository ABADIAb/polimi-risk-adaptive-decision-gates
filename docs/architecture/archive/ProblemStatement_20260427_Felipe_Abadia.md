---
title: "Problem Statement"
date: 2026-04-27
tags: [thesis, definition, objective]
status: active
---
# Problem Statement: Agentic AI for Joint Routing and Compute Scheduling

## Context
- **Topic:** Agentic AI for Intent-Driven Optical Networks (Thesis title pending update; formerly joint routing and compute scheduling).
- **Keywords:** Generative AI, Multi-agent LLM, Intent-based networking, Quality of Transmission (QoT), Human-in-the-Loop (HITL).
- **The Problem:** The translation of high-level operator intent into physical optical network configurations is heavily bottlenecked by complex physical-layer constraints (e.g., SNR, GN model) and the risk of LLM hallucination. Current methods hopelessly fail to flexibly integrate natural language service intent with deterministic physical-layer validation across the network lifecycle (Day-0 to Day-N).
- **The Solution Architecture:** A multi-agent LLM system designed to decompose tasks and coordinate optical routing utilizing specialized agents, deterministic tool calling (QoT validation), formal HITL protocols (`interrupt()`), and a Tri-Partite Hybrid Memory.
- **Scope Note:** Compute scheduling has been explicitly deferred to future work due to time constraints, allowing a deeper focus on the Routing Agent, QoT tool creation, and formal HITL implementation.

## Given
The orchestration agent is given three distinct, dynamic layers of input:
1. **The Natural Language Intent:** A high-level, unstructured semantic request from a human operator (e.g., "I want to establish a 400G service between node one and node three").
2. **The Physical Network Graph $G(V,E)$:** A serialized representation of the underlying topology, encompassing vertices (optical nodes, transponders) and edges (optical fiber characteristics, link capacities, span lengths).
3. **Dynamic State Observations:** Continuous, real-time environment telemetry, including link utilization, [[Concepts_and_Terminology|Quality of Transmission (QoT)]] metrics like SNR, EDFA power profiles, and physical constraints across Day-0 to Day-N operations.

## Decide
The agentic AI system employs a sequential coordination protocol to translate human intent into an optimal configuration. The algorithm decides the precise allocation in a structured, multi-stage workflow:
1. Intent Translation & Parsing: The Orchestrator LLM parses the natural language input to deduce numerical [[Concepts_and_Terminology|Service Level Agreement (SLA)]] boundaries, generating a provisional constraint matrix (`sla_matrix`) detailing required bandwidth, latency, and endpoints.
2. Formal HITL Refinement (Reverse Prompting): To prevent Garbage-In, Garbage-Out (GIGO), the Orchestrator enters a formal Human-in-the-Loop refinement stage via an `interrupt()` protocol. It uses reverse prompting to present the interpreted constraint matrix back to the human operator for validation before proceeding.
3. Sequential Handoff to Specialized Agents: Once approved, the Orchestrator delegates the problem to specialized multi-agent sub-systems (e.g., the Routing Agent). Following strict [[Constraint_Isolation|neurosymbolic separation]], LLMs act purely as reasoning engines and strictly delegate all mathematical operations, physics-bound constraint checks (QoT estimation via GN model), and spectrum pathfinding to deterministic Python external tools. No hallucination allowed.

The final output of the agentic system might depend on the operator intent. For example if the operator intent is to establish a service between two nodes, the output of the agentic system is a structured configuration tuple $A^* = (r^*, b^*)$, where:
- $r^*$ is the selected optical path (routing) that satisfies the QoT constraints.
- $b^*$ is the allocated spectrum band or wavelength.
*(Note: The compute node allocation $c^*$ is deferred to future work).*

This final configuration is mapped directly into an automated RESTConf API call to the physical SDN controller.

But if the operator intent is to consult the network state or documentation or make some queries, the output of the agentic system is a structured response to the operator's query. Response that is crafted after having executed the necessary actions (e.g. having called the tools or agents needed to satisfy the operator's query).

## Objective
As optical networks transition from bit-centric to intent-centric operations, the objective shifts to maximizing the [[Concepts_and_Terminology|Goal-Oriented Task (GoT) utility]] while minimizing system-level resource costs. 

The objective function of the Orchestrator LLM is to maximize:
$$ \max_{A^*} \sum_{i \in I} \Big( U_i(TSR_i) - w_c \cdot C_{sys}(r_i^*, b_i^*) \Big) $$

Where:
- $U_i(TSR_i)$ is the utility derived from the successful execution of task $i$ ([[Concepts_and_Terminology|Task Success Rate]]).
- $C_{sys}$ represents the total system costs, coupling optical variables (e.g., spectrum fragmentation, EDFA power consumption, physical path latency) for the assigned configuration $A^*$.
- $w_c$ is a weighting parameter balancing utility and cost.

## Constraints
Deploying LLMs at the orchestration layer shifts the bottleneck from purely optical bandwidth constraints to strict compute, cognitive, and latency boundaries:
1. **Task-Dependent Inference Latency Budget ($T_{total, i} \le T_{budget}(type(i))$):** Latency is modeled as a task-dependent budget rather than a fixed threshold. Intent parsing may tolerate relaxed budgets (seconds), while operational reactions (e.g., failure recovery) require strict, sub-second real-time bounds.
2. **Semantic Distortion Bound ($D_{sem} \le D_{max}$):** The loss of decision-relevant information during the telemetry-to-prompt transformation is strictly bounded. $D_{sem}$ is quantified as the reconstruction error on key state variables (e.g., QoT, load): $|| S_{true} - \hat{S}_{LLM} ||^2 \le D_{max}$, or as the measured degradation in task-level performance when using compressed vs. full telemetry.
3. **Context Window Saturation ($N_{tokens} \le N_{max}$):** Raw telemetry must be pre-compressed into a semantic Knowledge Graph or compact prompt template prior to inference to avoid context limits and hallucination.
4. **VRAM and Compute Limits ($M_{LLM} \le M_{Server}$):** The orchestrator is strictly constrained by the available GPU VRAM at the deployment site.
5. **Policy Safety & Grammar Validation:** Output policies must pass strict schema verification (grammar/syntax checks) before being deployed to physical optical controllers.