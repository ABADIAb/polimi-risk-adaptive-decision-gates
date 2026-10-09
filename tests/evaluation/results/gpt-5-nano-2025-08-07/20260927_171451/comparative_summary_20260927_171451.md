# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260927_171451`
- **Date:** 2026-09-27 17:14:51
- **Provider / Model:** `openai` / `gpt-5-nano-2025-08-07`
- **Corpus:** `full`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **90.5%** | 90.5% | 94.6% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **95.0%** | 94.2% | 95.0% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.955** | 0.457 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\%$** | **16.7%** | 16.7% | **100.0%** | **Strict Pre-Deployment Integrity Invariant**: zero un-gated risky approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **86.7%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | Contextual | **10.22s** [8.83s] | 10.66s [10.11s] | 17.68s [14.94s] | Median [Mean] turnaround duration |
| | Token Footprint ($T_{tokens}$) | Monitored | **8,784 tok** [7002] | 8,784 tok [8113] | 15,313 tok [12591] | Median [Mean] prompt accumulation |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.62** | **0.88** | 0.75 | **Zero-fatigue autonomous nominal pass** |
| | Task Completion Rate (TCR) | $100\%$ | **100.0%** | 100.0% | 100.0% | Successfully finished execution |
| | Timeout / Aborted Demands | $0$ | **0** | 0 | 0 | Demands reaching timeout or turn limits |
| **Pillar 4: Gate Reliability & Autonomy** | Gate Decision Accuracy (GDA) | $> 98\%$ | **84.2%** | 84.2% | 25.0% | Multi-class routing fidelity |
| | Selective HITL Precision | $100\%$ | **100.0%** | 71.4% | N/A (Bypassed) | Precision targeting non-nominal intents |
