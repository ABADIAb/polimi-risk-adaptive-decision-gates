---
title: "Experiment 1.1: QoT C++ to Python Port"
date: 2026-07-06
tags: [experiments, sprint1, qot, python, physical-layer]
status: active
---

# Experiment 1.1: QoT C++ to Python Port

## 1. Objective
Translate the core physics equations from the C++ simulator (`Code_for_Felipe/Network.cpp`) into pure Python. This port provides a deterministic, latency-optimized "Physics Engine" for the [[archive/Architecture_v4|Neurosymbolic Pipeline]] without relying on heavy third-party graph databases or external C++ processes.

## 2. Context
- **Roadmap Mapping**: [[MVP_Roadmap|Sprint 1, Exp 1.1 and 1.2]]
- **Target Location**: `src/core/qot_calculator.py` and `src/tools/qot_tool.py`
- **Dependencies**: Mathematical validation against the original C++ code (GSNR and Receiver Power thresholds).

## 3. Success Criteria
1. **Functional Parity**: Python functions for SNR and Receiver Power exactly match the C++ outputs for identical inputs.
2. **Component Isolation**: The physics calculations are fully decoupled from any monolithic optimizers (e.g. Genetic Algorithms in C++).
3. **LangChain Tool Exposure**: The QoT physics engine is cleanly wrapped as a LangChain `@tool` (`qot_check`) that can be ingested by the LangGraph orchestrator.
4. **Test Coverage**: A baseline test suite in `tests/` successfully asserts known-good scenarios (e.g. exact expected SNR for a 50km path with 1 amplifier).

## 4. Execution Steps (For LLM / Developer)
1. Read `docs/LLM_Wiki/wiki/architecture/tools_wiki/QoT_Tool.md` to understand the mathematical thresholds (`Receiver Power > -18 dBm` and dynamic `SNR_threshold`).
2. Inspect the C++ source in `docs/LLM_Wiki/raw/Code_for_Felipe/Network.cpp` (if available, or request it) focusing on: `calculateDemandSNR`, `calculatePropagatedSNR`, and `spanSNR`.
3. Create `src/core/qot_calculator.py` with the extracted pure-Python logic.
4. Create `src/tools/qot_tool.py` to wrap the calculator into a LangChain `@tool`. The tool should accept a path (list of nodes/links) and return a dictionary: `{"feasible": bool, "snr": float, "power": float}`.
5. Write unit tests in `tests/test_qot_tool.py` enforcing Strict TDD.

## 5. Deliverables
- `src/core/qot_calculator.py`
- `src/tools/qot_tool.py`
- `tests/test_qot_tool.py`
- A short summary report of the test results.
