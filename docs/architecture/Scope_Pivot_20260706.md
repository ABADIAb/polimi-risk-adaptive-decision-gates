---
title: "Scope Pivot: The Journey to Risk-Adaptive Neurosymbolic Intent Planning (V2 → V5)"
date: 2026-07-17
tags: [architecture, scope, pivot, planning-loop, neurosymbolic, risk-adaptive, radg, thesis]
status: active
supersedes: "[[archive/Scope_Pivot_20260621]]"
---

# Scope Pivot: The Journey to Risk-Adaptive Neurosymbolic Intent Planning (V2 → V5)

## 1. Executive Summary

This document consolidates the complete architectural evolution of the thesis from its initial V2 conception to the current V5 design. It details the three major scope pivots driven by State of the Art (SOTA) research, technical limitations discovered during development, and advisor feedback.

The progression follows:
- **V2 (Full MAS)**: End-to-end multi-agent orchestration for Day-0 to Day-N.
- **V3 (Planning Loop Focus)**: Narrowed scope to the Intent Planning phase due to SOTA saturation.
- **V4 (Neurosymbolic Pipeline)**: Introduction of deterministic PDDL, GraphRAG, and formal Reverse Prompting to solve physical hallucinations and token saturation.
- **V5 (Risk-Adaptive Decision Gates)**: Introduction of a pre-deployment joint semantic + QoT risk assessment mechanism that adaptively determines HITL engagement, replanning, or rejection.

## 2. First Pivot: V2 to V3 (SOTA-Driven Scope Reduction)

**Date:** 2026-06-21
**Transition:** From "Agentic AI for Joint Routing and Compute Scheduling" (V2) to "QoT-Informed Intent Planning" (V3).

### 2.1 The Problem
In early 2026, the architecture aimed to be a full Multi-Agent System (MAS) covering the entire lifecycle of optical networks. However, a rigorous SOTA analysis revealed that this broad framing was no longer novel:
- **Confucius (Meta, SIGCOMM 2025):** Validated multi-agent orchestration at hyperscale (60+ applications, 4k+ users, 31.62M messages), proving that MAS architectures in networking are solved at scale.
- **AutoLight (SJTU, ECOC 2025):** Demonstrated an L4 autonomous optical network using a LangGraph-based hierarchical MAS, proving that MAS is already applied successfully to the optical domain.

### 2.2 The V3 Solution
Since full MAS was no longer a novel contribution, the thesis scope was narrowed specifically to the **Planning Phase**. The system would no longer provision network paths directly (no RESTConf writes). Instead, it focused on the novel intersection of:
1. Natural Language Intent Parsing.
2. Multi-turn Human-in-the-Loop (HITL) refinement.
3. [[QoT_Awareness|QoT-aware]] path evaluation.

The output shifted from a network configuration command to a validated **Planning Report** containing candidate paths and SLA trade-offs.

## 3. Second Pivot: V3 to V4 (Technical Feasibility & Hallucination)

**Date:** 2026-07-06
**Transition:** From a "Generative Planning Loop" (V3) to a "Neurosymbolic Intent Orchestration Pipeline" (V4).

### 3.1 The Problem
While V3 successfully isolated the planning phase, prototyping revealed severe bottlenecks inherent to purely generative LLM pipelines:
- **Token Budget Saturation:** Extracting an entire optical topology via RESTConf and placing it in a JSON string within the LLM context caused context saturation, the lost-in-the-middle phenomenon, and massive inference costs.
- **The "Hallucinated Physics" Dilemma:** LLMs are probabilistic text engines; they do not natively respect physical constraints (e.g., Stimulated Raman Scattering, Generalized SNR margins). Allowing an LLM to heuristically query a heavy simulator like GNPy to find valid paths is computationally unscalable and prone to generating structurally invalid paths.
- **Semantic Drift in Multi-Turn HITL:** Using unstructured conversational interactions for intent refinement lacked convergence guarantees. A user's correction could lead the LLM to inadvertently drop prior constraints, creating an infinite loop of unverified plan states.

### 3.2 The V4 Solution (Neurosymbolic Pipeline)
The planning intelligence was restructured into a rigid "Sistema 1 (Generative) + Sistema 2 (Symbolic)" pipeline to enforce strict boundaries between reasoning and calculation:
1. **Intent Ingestion + Optical RAG:** The NL request is semantically enriched with specific constraints (e.g., ITU-T standards) before LLM processing.
2. **PDDL Intent Parsing (CFG Validated):** The LLM acts purely as a translator, outputting formal Planning Domain Definition Language (PDDL) states instead of a naive Pydantic SLA matrix.
3. **Formal HITL (Reverse Prompting):** The PDDL state is translated back into natural language by an inverse model, forcing the operator to explicitly approve the exact logical constraints the system understood, thereby mathematically bounding convergence.
4. **Symbolic Solver + GraphRAG:** A deterministic symbolic solver extracts 3–5 valid path candidates from a locally compressed GraphRAG topology based on the PDDL constraints.
5. **QoT Validation:** Only these mathematically bounded candidates are sent to the Python GNPy port for precise physical-layer QoT viability checks.

## 4. Third Pivot: V4 to V5 (Risk-Adaptive Pre-Deployment Decision)

**Date:** 2026-07-17
**Transition:** From a "Neurosymbolic Intent Orchestration Pipeline" (V4) to "Risk-Adaptive Neurosymbolic Intent Planning" (V5).

### 4.1 The Problem
While V4 successfully introduced the neurosymbolic separation and Reverse Prompting convergence, advisor feedback and further literature analysis revealed a critical framing issue:

- **Multi-turn clarification is not novel.** The PoliMi/CNSM 2025 paper (*"Flow-Rule Generation for SDN Using LLMs with Retry-Based Deployment Validation"*, El Hachimi et al.) already implements iterative clarification and retry-based correction, achieving 96.7% deployment accuracy. Framing multi-turn HITL or Reverse Prompting convergence as the primary contribution would overlap with established prior art.
- **V4's HITL was always-on.** Every intent triggered a Reverse Prompting HITL interrupt, regardless of the system's confidence in its own interpretation. This is operationally expensive and unnecessary for unambiguous, physically feasible intents.
- **No risk differentiation.** V4 treated all intents equally — a trivially simple routing request received the same level of human scrutiny as a physically marginal or semantically ambiguous one.

### 4.2 The V5 Solution (Risk-Adaptive Decision Gates)
The novelty was reframed from "how the system clarifies" to "how the system decides WHETHER and HOW to act." V5 introduces the **Risk-Adaptive Decision Gates (RADGs)** that jointly evaluate two orthogonal signals:

1. **Semantic Uncertainty ($U_{sem}$)**: A two-layer assessment combining CFG structural validation (Layer 1) and embedding-based disagreement between the original intent and the Reverse Prompting reconstruction (Layer 2).
2. **QoT Feasibility ($\text{QoT}_{valid}$)**: Binary evaluation of physical-layer feasibility ($\text{GSNR}_{computed} \ge \text{GSNR}_{threshold}$).

The RADGs map these signals to four possible outcomes: **auto-approve**, **clarify** (trigger HITL), **suggest replan** (propose alternatives to operator), or **reject + request reformulation** (block deployment and notify operator).

### 4.3 Key Distinction from Prior Art
| Aspect | PoliMi/CNSM 2025 (El Hachimi et al.) | MultiAgentON V5 (Ours) |
|--------|---------------------------------------|------------------------|
| **When** | Post-deployment (after controller failure) | Pre-deployment (before any configuration reaches the network) |
| **Mechanism** | Fixed N retries | Risk-proportional decision ($D(U_{sem}, \text{QoT}_{valid})$) |
| **Risk Assessment** | None — retries blindly | Joint semantic + QoT risk evaluation |
| **HITL** | Always-on intent clarification | Conditional — only when $U_{sem}$ is high |
| **Physics Awareness** | Controller error codes | Deterministic GSNR margin computation |
| **Domain** | SDN (IP flow rules) | Optical networks (GSNR, GN model) |

## 5. Novelty and Added Value (Unique Selling Points)

The evolution through V4 to V5 establishes a highly focused, academically novel contribution:

1. **Risk-Adaptive Pre-Deployment Decision Gates (RADGs).** Unlike post-deployment retry systems (PoliMi/CNSM 2025) or always-on HITL approaches, V5 jointly evaluates semantic uncertainty and QoT risk margin BEFORE deployment to determine the minimally invasive corrective action. This is the core novelty.
2. **Neurosymbolic Constraint Isolation.** The LLM is restricted to linguistics (Intent → PDDL). A deterministic Symbolic Solver and GN-model tool handle the physics, guaranteeing 100% physically viable route proposals in the approved set.
3. **Formal HITL via Reverse Prompting.** When the RADGs determine clarification is needed, the Reverse Prompting mechanism mathematically bounds the operator's approval to the exact logical constraints the system will execute.
4. **Formal Evaluation Framework.** V5 includes a structured comparison against No-HITL, Always-HITL, and Fixed-Retry baselines using five metrics (UAR, HIC, QFR, E2EL, TC) — ensuring the contribution is measurably validated.

## 6. MVP Roadmap Constraint

Given the August 25 deadline, the V5 MVP will utilize a **simplified Python symbolic solver**, a **mock GraphRAG** structure (Python dictionary traversals), and a **lightweight RADG implementation** (threshold-based decision function with embedding similarity for $U_{sem}$). This ensures a functional, verifiable prototype with formal baseline evaluation.

## 7. Cross-References

- [[Architecture_v5]] — The active V5 architecture document.
- [[ProblemStatement_v5]] — The thesis problem definition with evaluation framework.
- [[experiments/MVP_Roadmap]] — Sprint plan including RADG and baseline evaluation experiments.
- [[literature/sota_gap_analysis]] — Gap analysis including PoliMi/CNSM 2025.
- [[archive/Scope_Pivot_20260621]] — Original V2 to V3 pivot document.
- [[architecture/archive/Architecture_v4]] — Archived V4 architecture.
- [[archive/Architecture_v3]] — Archived V3 architecture.
- [[archive/Architecture_v2]] — Archived V2 architecture.
