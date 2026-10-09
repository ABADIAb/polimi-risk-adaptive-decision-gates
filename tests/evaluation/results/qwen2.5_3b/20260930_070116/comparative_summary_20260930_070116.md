# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260930_070116`
- **Date:** 2026-09-30 07:01:16
- **Provider / Model:** `ollama` / `qwen2.5:3b`
- **Corpus:** `full`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **96.0%** | 94.6% | 96.0% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **95.8%** | 95.8% | 95.0% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.858** | 0.408 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\%$** | **1.1%** | 1.1% | **100.0%** | **Strict Pre-Deployment Integrity Invariant**: zero un-gated risky approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **83.3%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | Contextual | **13.19s** [25.76s] | 13.99s [25.77s] | 21.96s [76.46s] | Median [Mean] turnaround duration |
| | Token Footprint ($T_{tokens}$) | Monitored | **9,118 tok** [7764] | 9,118 tok [8871] | 15,105 tok [12108] | Median [Mean] prompt accumulation |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.73** | **0.97** | 0.72 | **Zero-fatigue autonomous nominal pass** |
| | Task Completion Rate (TCR) | $100\%$ | **98.3%** | 98.3% | 96.7% | Successfully finished execution |
| | Timeout / Aborted Demands | $0$ | **2** | 2 | 4 | Demands reaching timeout or turn limits |
| **Pillar 4: Gate Reliability & Autonomy** | Gate Decision Accuracy (GDA) | $> 98\%$ | **96.7%** | 97.5% | 25.0% | Multi-class routing fidelity |
| | Selective HITL Precision | $100\%$ | **98.9%** | 74.4% | N/A (Bypassed) | Precision targeting non-nominal intents |
