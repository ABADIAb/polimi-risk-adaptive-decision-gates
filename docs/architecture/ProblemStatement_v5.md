---
title: "Problem Statement V5: LLM-Assisted Risk-Adaptive Decision Gates for Intent Based Optical Networks"
date: 2026-07-17
tags: [thesis, definition, objective, planning-loop, hitl, neurosymbolic, pddl, risk-adaptive, qot, evaluation]
status: active
supersedes: "[[architecture/archive/ProblemStatement_v4]]"
---

# Problem Statement V5: LLM-Assisted Risk-Adaptive Decision Gates for Intent Based Optical Networks

## 1. Context

- **Thesis Title:** LLM-Assisted Risk-Adaptive Decision Gates for Intent Based Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment.
- **Keywords:** Generative AI, Intent-Based Networking, Quality of Transmission (QoT), Human-in-the-Loop (HITL), Neurosymbolic AI, PDDL, Risk-Adaptive Decision, Semantic Uncertainty, Pre-Deployment Validation.
- **Academic Setting:** Master's thesis in Telecommunications Engineering, conducted in collaboration with the Software-Defined Optical Networking (SDON) research laboratory.

## 2. The Problem

The translation of high-level operator intent into physical optical network configurations is severely bottlenecked by five interconnected challenges:

1. **Token Budget Saturation.** Injecting massive optical topologies (RESTConf JSON payloads) into LLM context windows causes attention degradation — the "lost-in-the-middle" phenomenon — leading to missed constraints and inflated inference costs.

2. **Hallucinated Physics.** LLMs are probabilistic text generators; they do not natively respect nonlinear optical constraints such as Generalized Signal-to-Noise Ratio (GSNR) margins or Stimulated Raman Scattering. Allowing an LLM to heuristically propose lightpaths produces structurally invalid and physically infeasible routes.

3. **Semantic Drift in HITL Refinement.** Unstructured conversational loops for intent refinement lack convergence guarantees. A correction in one turn may cause the LLM to inadvertently drop constraints from prior turns, creating an infinite loop of unverified plan states.

4. **Reactive Post-Deployment Verification.** Existing LLM-based networking systems rely on **heuristic trial-and-error loops after a deployment failure**: the system generates a configuration, deploys it, observes a controller error, and retries. This reactive pattern allows physically infeasible or unfeasible configurations to reach the network controller before any corrective action is taken.

5. **Suboptimal HITL Engagement.** Current systems offer only two extremes: **always-on HITL** (every intent requires human review, creating severe bottlenecks, cognitive overload, and operator fatigue) or **no HITL** (fully autonomous, risking unfeasible approvals). There is no mechanism to engage the human operator **proportionally to the assessed risk** of a given intent, leading to a highly unoptimized workflow.

## 3. The Fundamental Gap

**The fundamental gap:** No existing system combines **semantic uncertainty assessment** (did the LLM correctly understand the intent?) with **physical-layer QoT risk evaluation** (is the proposed lightpath physically feasible?) into a **fail-fast, sequential pre-deployment decision** that adaptively minimizes human intervention while guaranteeing network safety. The lack of such a mechanism leads to unoptimized workflows where operators are either overwhelmed by redundant validations or bypassed entirely, risking catastrophic deployment failures.

## 4. The Proposed Solution

A **Neurosymbolic Intent Planning Pipeline** with a **Risk-Adaptive Decision Pipeline** that sequentially evaluates two orthogonal risk signals **before deployment** to determine the appropriate action for each intent.

### 4.1 Neurosymbolic Pipeline

The pipeline enforces a strict "LLMs reason, tools calculate" separation:

1. **Intent Ingestion + Optical RAG.** The natural language request is semantically enriched with domain standards (e.g., ITU-T specifications, transponder data) before LLM processing.
2. **PDDL Intent Parsing.** The LLM translates the enriched intent into formal PDDL constraints.
3. **Semantic RADG ($U_{sem}$).** Before complex computation, the system checks structural (CFG) and semantic (Reverse Prompting) validity. If uncertainty is high, it immediately requests the operator to clarify missing data.
4. **Symbolic Solver + Context Bounding.** A Python-based symbolic solver dynamically extracts a localized $k$-hop subtopology to bound LLM context, and then mathematically computes 3–5 structurally valid candidate paths.
5. **QoT Validation.** Candidate paths are evaluated by a deterministic Python QoT Tool (GN-model port) to compute precise GSNR and receiver power feasibility.
6. **Physical RADG.** Evaluates the binary QoT feasibility to decide if the plan should be auto-approved or if the operator must be engaged to relax constraints via HITL.

### 4.2 Risk-Adaptive Decision Pipeline

The system acts upon two orthogonal risk signals in a sequential, fail-fast manner:

- **$U_{sem}$: Semantic Uncertainty (Evaluated Early).**
  - *Layer 1 (Structural)*: Binary pass/fail from the CFG PDDL validator — catches gross hallucinations.
  - *Layer 2 (Semantic)*: Disagreement score between the original operator intent and the Reverse Prompting natural language reconstruction. High $U_{sem}$ triggers early **Clarify** (HITL).

- **QoT Feasibility (Evaluated Later).** 
Binary check: $\text{GSNR}_{computed} \ge \text{GSNR}_{threshold} \land P_{rx} \ge P_{rx, min}$

Assuming $U_{sem}$ is low (resolved in the Semantic RADG), the Physical RADG maps to two outcomes:

| Decision | Condition | Action |
|----------|-----------|--------|
| **Auto-Approve** | Valid (Feasible) | Deploy without human review |
| **Suggest Replan** | Invalid (Unfeasible) | Physics failed. Notify operator and suggest relaxing constraints via HITL (loops back to Phase 2) |

### 4.3 Formalizing the Risk-Adaptive Decision Gates (RADGs)

The RADGs are formulated as a piecewise decision function $D$ that evaluates two constraints sequentially:

1. **Semantic Uncertainty ($U_{sem}$):** A function of structural validity ($v_{struct} \in \{0, 1\}$) and semantic divergence ($d_{sem} \in [0, 1]$).
   $$U_{sem} = \begin{cases} 1 & \text{if } v_{struct} = 0 \text{ (Structural Failure)} \\ d_{sem} & \text{if } v_{struct} = 1 \text{ (Semantic Divergence)} \end{cases}$$
   Given a tolerance threshold $\tau_{sem}$, if $U_{sem} > \tau_{sem}$, the intent is considered ambiguous.

2. **Physical Viability ($QoT_{valid}$):** A binary indicator based on deterministic physics:
   $$QoT_{valid} = \mathbb{I}(\text{GSNR}_{computed} \ge \text{GSNR}_{threshold} \land P_{rx} \ge P_{rx, min})$$

The decision function maps the state to an action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$:

$$D(U_{sem}, \text{QoT}_{valid}) = \begin{cases} \text{clarify} & \text{if } U_{sem} > \tau_{sem} \\ \text{replan} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0 \\ \text{approve} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1 \end{cases}$$

This formalization enforces the **pre-deployment fail-fast** mechanism.

## 5. Given

The planning system receives:
1. **The Natural Language Intent.** A high-level, unstructured semantic request from a human operator (e.g., "Route traffic from Hamburg to Munich with at least 15 dB GSNR, avoiding Frankfurt").
2. **The Physical Network Graph $G(V,E)$.** Extracted from the SDON testbed via RESTConf/SSH.
3. **QoT Physical Parameters.** Fiber attenuation coefficients, optical amplifier gains, and channel configurations for deterministic GN-model computation.

## 6. Output

The output of the pipeline is a validated **Planning Report** containing:
- **Structurally Valid Paths** with verified QoT feasibility scores ($\text{GSNR}_{dB}$, $P_{rx,dBm}$, $\text{QoT}_{valid}$).
- **PDDL Constraint Map** guaranteeing the logic applied to the path search.
- **RADG Decision Trace** — the risk assessment that led to the final decision (approve/clarify/replan), including $U_{sem}$ and $\text{QoT}_{valid}$ values.
- **Reverse Prompting Trace** (when applicable) — the formal conversation history documenting the operator's agreement to the plan.
- **Approved Routing Decision** — ready to be pushed to the SDON testbed.

## 7. The Optimization Objective

The primary objective of the LLM-Assisted Risk-Adaptive Decision Gates architecture is **to optimize network operator interventions (HITL)** subject to strict feasibility constraints. The system seeks to **minimize operational friction and cognitive overload** by engaging the human strictly when semantic ambiguity or physical infeasibility demands it, rather than enforcing blanket reviews or relying on trial-and-error.

$$\min_{\text{plan}} \Big( \alpha \cdot N_{hitl}(\text{plan}) + \beta \cdot T_{tokens}(\text{plan}) \Big)$$

$$\text{subject to:} \quad D(U_{sem}, \text{QoT}_{valid}) = \text{approve}$$

Where:
- $N_{hitl}(\text{plan})$ is the number of human-in-the-loop interruptions (operational friction).
- $T_{tokens}(\text{plan})$ is the LLM token consumption (computational friction).
- $\alpha, \beta$ are weighting coefficients for human time vs. API cost.
- $D(U_{sem}, \text{QoT}_{valid}) = \text{approve}$ is the strict hard constraint guaranteeing that the plan satisfies both the semantic threshold ($\tau_{sem}$) and the physical physics threshold ($\text{GSNR}_{threshold}$) before deployment.

