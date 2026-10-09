---
title: "Scope Pivot: From Full MAS to QoT-Informed Intent Planning Loop"
date: 2026-06-21
tags: [architecture, scope, pivot, planning-loop, thesis]
status: active
---

# Scope Pivot: From Full MAS to QoT-Informed Intent Planning Loop

## 1. Decision Summary

On 2026-06-21, after completing a rigorous SOTA analysis of the agentic AI landscape for optical networks (2024–2026), the thesis scope was formally narrowed from:

- **Previous scope**: "Agentic AI for Joint Routing and Compute Scheduling in Optical Networks" — a full multi-agent system covering Day-0 through Day-N optical lifecycle management.

To:

- **New scope**: **"QoT-Informed Intent Planning for Optical Networks: A Neurosymbolic Human-in-the-Loop Approach"** — focused on the *planning phase* where operator intent is parsed, validated against physical-layer constraints, and iteratively refined through HITL until an approved plan is produced.

---

## 2. SOTA Evidence Motivating the Pivot

Three key works demonstrated that the "full MAS for optical networks" framing is no longer novel:

### 2.1 Confucius (Meta, SIGCOMM 2025)
- Production-grade multi-agent LLM framework with 60+ network management applications, 4,160 users, and 31.62M messages.
- DAG-based workflow orchestration with RAG long-term memory.
- Validates multi-agent orchestration at hyperscale — we cannot compete on MAS novelty in general networking.
- See [[Confucius_SIGCOMM2025]] for full analysis.

### 2.2 AutoLight (SJTU, ECOC 2025)
- First field-trial demonstration of L4 autonomous optical network using a hierarchical multi-agent system **built on LangGraph**.
- ~98% task completion rate (3.2× single-agent improvement).
- Novel Chain of Identity (CoI) technique for inter-agent coordination.
- Validates multi-agent LangGraph architectures specifically in the optical domain — our framework choice is confirmed but not novel.
- See [[AutoLight_ECOC2025]] for full analysis.

### 2.3 SJTU Invited Tutorial (JOCN 2026)
- Comprehensive 225+ reference survey covering the entire agentic AI stack for autonomous optical networks.
- Advocates hierarchical MAS, Digital Twin toolsets, and MCP interoperability.
- Acknowledges [[HITL_Refinement|HITL]] as essential for the transition to autonomy but does **not** formally specify it.
- See [[SJTU_Invited_Tutorial_JOCN2026]] for full analysis.

### 2.4 Conclusion

The MAS architecture, LangGraph framework, and optical-domain application are validated but no longer novel in isolation. The novelty lies in the **specific intersection** of capabilities that no existing work addresses — all of which reside in the **planning phase**.

---

## 3. What Stays (In Scope)

These elements remain core to the thesis under the new scope:

| Element | Role in Planning Loop |
|:---|:---|
| **NL Intent Parsing** | Entry point — operator writes free-text intent, system parses to `sla_matrix` |
| **Reverse Prompting / HITL** | Multi-turn refinement loop — operator validates and refines the plan |
| **Topology Agent** | Fetches network topology to inform path candidates |
| **Routing Agent + QoT Tool** | Evaluates candidate paths via GN model for physical-layer feasibility |
| **Orchestrator (Supervisor)** | Coordinates the planning loop, synthesizes results, presents to operator |
| **LangGraph StateGraph** | Execution framework for the planning loop workflow |
| **Neurosymbolic Separation** | "LLMs reason, tools calculate" — core design principle |
| **Wiki Memory (Pillar 1)** | Boot-time skill injection, schema loading |
| **Pydantic State (Pillar 2 MVP)** | In-memory topology and planning state |
| **Planning Report** | NEW structured output — the primary artifact of the planning loop |

## 4. What Goes to Future Work

These elements are documented but explicitly deferred:

| Element | Reason |
|:---|:---|
| **Lightpath Provisioning Agent** | The system OUTPUT is a validated `approved_plan`, not a RESTConf call |
| **Compute Scheduling** | Already deferred (previous pivot); orthogonal to planning focus |
| **Full Lifecycle Day-N Ops** | Operational management (failure recovery, reoptimization) is out of scope |
| **Conflict Resolution Loops** | No multi-agent contention in the planning-only scope |
| **Vector RAG (Pillar 3)** | Not needed for the planning loop MVP |
| **Knowledge Graph DB** | Pydantic state is sufficient; Neo4j/Memgraph is future graduation |
| **Real Testbed Integration** | Planning loop can be validated on mock testbed; SSH access is a bonus |

## 5. New Output Definition

The system output changes from:

**Before (V2):** A configuration tuple $A^* = (r^*, b^*)$ mapped to a RESTConf API call.

**After (V3):** A validated **Planning Report** containing:
- Candidate optical paths with QoT feasibility scores (SNR, power, feasible/infeasible)
- SLA constraint satisfaction matrix
- Trade-off analysis presented to the operator
- Operator-approved routing decision with justification trace
- HITL conversation history (refinement iterations)

The Planning Report is a structured Pydantic artifact that a downstream provisioning system (future work) could consume.

## 6. New Experiment Roadmap

| Experiment | Focus | Dependencies |
|:---|:---|:---|
| **001: Topology Query MVP** | ✅ Completed | — |
| **002: Intent Parsing + HITL** | NL → `sla_matrix` with multi-turn reverse prompting | — |
| **003: QoT-Informed Path Selection** | Routing Agent + QoT tool evaluating candidate paths | 001 (topology data) |
| **004: Full Planning Loop** | End-to-end integration: intent → topology → QoT → HITL → approved plan | 002 + 003 |

---

## 7. Cross-References

- [[Architecture_v3]] — New unified architecture (supersedes [[architecture/archive/Architecture_v2|V2]])
- [[ProblemStatement_v3]] — Updated problem definition
- [[sota_gap_analysis]] — Gap analysis with updated positioning
- [[lit_comparison]] — SOTA comparison
- [[Presentation_20260621_Scope_Pivot]] — Presentation for professor
