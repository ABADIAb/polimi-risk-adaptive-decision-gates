# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260928_111332`
- **Date:** 2026-09-28 11:13:32
- **Provider / Model:** `openai` / `gpt-6-luna`
- **Corpus:** `full`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **100.0%** | 100.0% | 100.0% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **95.0%** | 95.0% | 93.3% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.955** | 0.462 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\%$** | **4.4%** | 4.4% | **100.0%** | **Strict Pre-Deployment Integrity Invariant**: zero un-gated risky approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **90.0%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | Contextual | **15.89s** [14.31s] | 16.84s [16.77s] | 29.52s [25.17s] | Median [Mean] turnaround duration |
| | Token Footprint ($T_{tokens}$) | Monitored | **9,200 tok** [7768] | 9,200 tok [8930] | 15,908 tok [13113] | Median [Mean] prompt accumulation |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.72** | **0.97** | 0.75 | **Zero-fatigue autonomous nominal pass** |
| | Task Completion Rate (TCR) | $100\%$ | **100.0%** | 100.0% | 100.0% | Successfully finished execution |
| | Timeout / Aborted Demands | $0$ | **0** | 0 | 0 | Demands reaching timeout or turn limits |
| **Pillar 4: Gate Reliability & Autonomy** | Gate Decision Accuracy (GDA) | $> 98\%$ | **96.7%** | 96.7% | 25.0% | Multi-class routing fidelity |
| | Selective HITL Precision | $100\%$ | **100.0%** | 74.1% | N/A (Bypassed) | Precision targeting non-nominal intents |
