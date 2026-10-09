# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260926_154258`
- **Date:** 2026-09-26 15:42:58
- **Provider / Model:** `ollama` / `qwen2.5:3b`
- **Corpus:** `compact`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **94.6%** | 94.6% | 96.0% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **98.3%** | 98.3% | 98.3% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.863** | 0.412 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\%$** | **1.1%** | 1.1% | **100.0%** | **Strict Pre-Deployment Integrity Invariant**: zero un-gated risky approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **86.7%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | Contextual | **12.36s** [25.95s] | 12.82s [24.76s] | 20.02s [38.71s] | Median [Mean] turnaround duration |
| | Token Footprint ($T_{tokens}$) | Monitored | **8,846 tok** [7565] | 8,846 tok [8598] | 14,756 tok [11954] | Median [Mean] prompt accumulation |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.74** | **0.97** | 0.73 | **Zero-fatigue autonomous nominal pass** |
| | Task Completion Rate (TCR) | $100\%$ | **98.3%** | 98.3% | 98.3% | Successfully finished execution |
| | Timeout / Aborted Demands | $0$ | **2** | 2 | 2 | Demands reaching timeout or turn limits |
| **Pillar 4: Gate Reliability & Autonomy** | Gate Decision Accuracy (GDA) | $> 98\%$ | **92.5%** | 94.2% | 25.0% | Multi-class routing fidelity |
| | Selective HITL Precision | $100\%$ | **97.8%** | 74.4% | N/A (Bypassed) | Precision targeting non-nominal intents |
