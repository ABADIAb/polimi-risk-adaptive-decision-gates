# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260926_175018`
- **Date:** 2026-09-26 17:50:18
- **Provider / Model:** `ollama` / `qwen2.5:3b`
- **Corpus:** `full`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **94.6%** | 94.6% | 94.6% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **95.0%** | 95.0% | 97.5% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.866** | 0.415 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\%$** | **0.0%** | 0.0% | **100.0%** | **Strict Pre-Deployment Integrity Invariant**: zero un-gated risky approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **83.3%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | Contextual | **12.91s** [21.73s] | 14.27s [25.79s] | 21.84s [66.35s] | Median [Mean] turnaround duration |
| | Token Footprint ($T_{tokens}$) | Monitored | **9,092 tok** [7768] | 9,084 tok [8831] | 15,070 tok [12075] | Median [Mean] prompt accumulation |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.74** | **0.97** | 0.72 | **Zero-fatigue autonomous nominal pass** |
| | Task Completion Rate (TCR) | $100\%$ | **97.5%** | 97.5% | 95.8% | Successfully finished execution |
| | Timeout / Aborted Demands | $0$ | **3** | 3 | 5 | Demands reaching timeout or turn limits |
| **Pillar 4: Gate Reliability & Autonomy** | Gate Decision Accuracy (GDA) | $> 98\%$ | **95.0%** | 96.7% | 25.0% | Multi-class routing fidelity |
| | Selective HITL Precision | $100\%$ | **97.8%** | 74.4% | N/A (Bypassed) | Precision targeting non-nominal intents |
