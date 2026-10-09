---
title: "Architecture Workflow (LangGraph)"
date: 2026-04-27
tags: [architecture, workflow, multi-agent, langgraph]
status: active
---
# Proposed Architecture: Sequential Multi-Agent Workflow (V2 - LangGraph Implementation)

This document details the step-by-step workflow of the "Slow Loop" Orchestrator in an Intent-Based Optical Network. It defines how semantic intents are translated, validated, and delegated to specialized multi-agent sub-systems using a **LangGraph** topology, supported by Hybrid Memory and Dynamic Skills.

## Phase 0: Memory & Knowledge Substrate
Before parsing intents, the system relies on a [[Hybrid_Memory_Architecture|Hybrid Memory Architecture]] foundation to manage state and scalability without exploding the context window.
1. **Structural Memory (LLM Wiki):** Acts as the deterministic, structured state memory (Procedural Rules and Skills).
2. **Knowledge Graph (State Tracker):** A technology-agnostic graph system explicitly tracks the current live topology, agent dependencies, and numerical SLA constraints.
3. **Vector Memory (RAG):** RAG is utilized as an episodic memory for retrieving extended unstructured documentation (e.g., optical hardware manuals) and dynamically fetching specific tool schemas (Tool-RAG Registry) to avoid prompt bloat.

## Phase 1: Intent Parsing & Translation
1. **The Human Intent:** A network operator inputs a high-level semantic command (e.g., *"Provide a highly reliable, low-latency network slice to stream 4K VR data from the central database to an edge node for rendering"*).
2. **Context Retrieval:** The Orchestrator queries the Knowledge Substrate for established topological rules and past similar SLA matrices.
3. **LLM Translation:** The Orchestrator Agent parses the text. It translates abstract concepts into numerical [[Concepts_and_Terminology|Service Level Agreement (SLA)]] constraints (e.g., `< 10ms` latency, `5 Gbps` bandwidth), generating a provisional structured constraint matrix in the LangGraph `State`.

## Phase 2: Human-in-the-Loop (HITL) Refinement
4. **Reverse Prompting (Validation Node):** To prevent [[ProblemStatement_20260427_Felipe_Abadia|Garbage In, Garbage Out (GIGO)]], the graph halts at a validation node. It explains its mathematical interpretation of the intent back to the user.
5. **Authorization:** The user validates or adjusts the matrix. The `StateGraph` only proceeds to execution once the human operator gives explicit authorization, changing the state flag `is_authorized = True`.

## Phase 3: LangGraph-Driven Multi-Agent Delegation
The Orchestrator avoids solving the placement simultaneously by operating as a **Supervisor Node**, delegating tasks to ephemeral sub-agents.

6. **Supervisor Node Routing:** The Orchestrator reads the SLA matrix and routes the `State` to the necessary specialist node.
7. **Ephemeral Sub-Agent Nodes:** The Supervisor spawns isolated sub-agents to preserve context window limits. 
   - **Dynamic Skill Injection:** When spawning a node (e.g., `Optical_Agent_Node`), the Supervisor injects the relevant `Optical_Skill.md` file into the sub-agent's prompt, strictly defining its cognitive scope and granting it access to specific tool schemas retrieved from the Tool-RAG.

## Phase 4: Tool Nodes & Deterministic Execution
8. **Deterministic ToolNodes:** Sub-Agents are reasoning engines, not calculators. When the `Optical_Agent_Node` needs to evaluate a path, it formats a JSON payload and triggers a `ToolNode`.
9. **Execution:** The `ToolNode` executes deterministic Python scripts (e.g., [[Concepts_and_Terminology|Quality of Transmission (QoT)]] calculators, Dijkstra algorithms) against the physical network simulator/controller and returns the physical constraints (e.g., Optical SNR or Delay) back into the LangGraph `State`.

## Phase 5: State Management & Conflict Resolution
10. **Conditional Edges:** Conflict resolution is natively handled by LangGraph's routing. If the `Compute_Agent_Node` determines via its `ToolNode` that an edge server lacks the VRAM required for a proposed optical path, it flags a conflict in the shared `State`.
11. **Iterative Feedback:** A `Conditional Edge` routes the graph back to the `Optical_Agent_Node` with the error context, triggering a re-calculation. This loop iterates until the state condition `is_resolved == True`.

## Phase 6: Fast Loop Handoff
12. **Final Configuration Tuple:** Once the multi-agent graph resolves all constraints, the Supervisor synthesizes the final optimal configuration tuple: $A^* = (r^*, b^*, c^*)$.
13. **Execution:** The Orchestrator formats this tuple into a strict API payload and pushes it down to the SDN Controller (The Fast Loop), physically configuring optical switches and VMs.
