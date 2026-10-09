# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260927_144208`
- **Date:** 2026-09-27 14:42:08
- **Provider / Model:** `openai` / `gpt-6-luna`
- **Corpus:** `full`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **98.7%** | 98.7% | 100.0% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **93.3%** | 93.3% | 92.5% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.963** | 0.468 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\%$** | **3.3%** | 3.3% | **100.0%** | **Strict Pre-Deployment Integrity Invariant**: zero un-gated risky approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **90.0%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | Contextual | **12.48s** [11.06s] | 12.75s [12.68s] | 19.69s [16.76s] | Median [Mean] turnaround duration |
| | Token Footprint ($T_{tokens}$) | Monitored | **9,154 tok** [7832] | 9,154 tok [8986] | 15,823 tok [13045] | Median [Mean] prompt accumulation |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.72** | **0.97** | 0.75 | **Zero-fatigue autonomous nominal pass** |
| | Task Completion Rate (TCR) | $100\%$ | **100.0%** | 100.0% | 100.0% | Successfully finished execution |
| | Timeout / Aborted Demands | $0$ | **0** | 0 | 0 | Demands reaching timeout or turn limits |
| **Pillar 4: Gate Reliability & Autonomy** | Gate Decision Accuracy (GDA) | $> 98\%$ | **96.7%** | 96.7% | 25.0% | Multi-class routing fidelity |
| | Selective HITL Precision | $100\%$ | **100.0%** | 74.4% | N/A (Bypassed) | Precision targeting non-nominal intents |
