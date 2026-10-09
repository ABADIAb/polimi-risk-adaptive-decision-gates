# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260928_124751`
- **Date:** 2026-09-28 12:47:51
- **Provider / Model:** `openai` / `gpt-5-nano-2025-08-07`
- **Corpus:** `full`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **93.2%** | 94.6% | 93.2% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **93.3%** | 94.2% | 96.7% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.963** | 0.483 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\%$** | **10.0%** | 10.0% | **100.0%** | **Strict Pre-Deployment Integrity Invariant**: zero un-gated risky approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **90.0%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | Contextual | **14.05s** [12.40s] | 14.33s [14.05s] | 21.17s [18.27s] | Median [Mean] turnaround duration |
| | Token Footprint ($T_{tokens}$) | Monitored | **8,702 tok** [7271] | 8,703 tok [8341] | 15,262 tok [12596] | Median [Mean] prompt accumulation |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.68** | **0.93** | 0.75 | **Zero-fatigue autonomous nominal pass** |
| | Task Completion Rate (TCR) | $100\%$ | **100.0%** | 100.0% | 100.0% | Successfully finished execution |
| | Timeout / Aborted Demands | $0$ | **0** | 0 | 0 | Demands reaching timeout or turn limits |
| **Pillar 4: Gate Reliability & Autonomy** | Gate Decision Accuracy (GDA) | $> 98\%$ | **88.3%** | 89.2% | 25.0% | Multi-class routing fidelity |
| | Selective HITL Precision | $100\%$ | **98.8%** | 73.0% | N/A (Bypassed) | Precision targeting non-nominal intents |
