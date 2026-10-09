---
title: "Feature: QoT Tool & Physics Engine"
date: 2026-07-31
tags: [feature, qot, gn-model, physics, tool, core]
status: active
---

# Feature: QoT Tool & Physics Engine

## 1. Architecture Placement
**Phase 5: QoT Validation** | [[Architecture_v5]]

This feature implements the deterministic physics layer — the "System 2" (symbolic) half of the neurosymbolic architecture. The LLM is strictly forbidden from computing SNR values. All physical-layer calculations are delegated to this module.

## 2. Overview
A pure-Python Quality of Transmission (QoT) feasibility calculator assessing whether an optical lightpath can successfully transmit data, implemented as a direct port of the C++ GN-model simulator (`Network::spanSNR` and `Network::calculateDemandSNR`).

The feature has three layers:

| Layer | File | Role |
|-------|------|------|
| **Physics Engine** | `src/core/qot_calculator.py` | GN-model computation (ASE + NLI) |
| **Domain Models** | `src/core/models.py` | Canonical Pydantic model (`FiberLink`, `Amplifier`, `QoTResult`) |
| **Physical Constants** | `src/core/constants.py` | Fiber, EDFA, channel constants from C++ source |
| **LangChain Tool Wrapper** | `src/tools/qot_tool.py` | `@tool`-decorated adapter for agent use |

## 3. How it Works
- **GN Model:** Computes both linear Amplified Spontaneous Emission (ASE) noise from EDFAs and nonlinear interference (NLI) generated in fiber spans.
- **Span propagation:** Tracks signal power [dBm] as it traverses nodes (filter/connector losses) and fiber spans (propagation attenuation + EDFA gain).
- **Feasibility verdict:** Returns `QoTResult` with `snr_dB`, `power_dBm`, and `feasible` (True iff `snr_dB >= snr_threshold` AND `power_dBm >= -18 dBm`).
- **Adaptive Bitrate Thresholds:** Calibrated in `src/core/constants.py`: standard $\text{SNR}_{th} = 14.5\text{ dB}$ (100G/200G QPSK) and high-order $\text{SNR}_{th, 400G} = 21.5\text{ dB}$ (400G 16-QAM). `qot_validation_node` dynamically binds this threshold when evaluating candidate paths with explicit bandwidth requirements.

*Scope: Filtered (ROADM) network mode. Filterless ASE propagation deferred to future work. Zero equalization loss assumed.*

## 4. Associated Files
- **Engine**: [src/core/qot_calculator.py](file:///home/felipeab/MultiAgentON/src/core/qot_calculator.py) — `span_snr()`, `calculate_demand_snr()`, `assess_qot()`
- **Models**: [src/core/models.py](file:///home/felipeab/MultiAgentON/src/core/models.py) — `Amplifier`, `FiberLink` (canonical unificado), `QoTResult`
- **Constants**: [src/core/constants.py](file:///home/felipeab/MultiAgentON/src/core/constants.py) — `FIBER`, `CHANNEL`, `NODE`, `AMPLIFIER`, `THRESHOLD`
- **Tool wrapper**: [src/tools/qot_tool.py](file:///home/felipeab/MultiAgentON/src/tools/qot_tool.py) — `qot_check` LangChain `@tool`
- **Pipeline node**: [src/nodes/qot_validation.py](file:///home/felipeab/MultiAgentON/src/nodes/qot_validation.py) — Phase 5 node (instancia `FiberLink` directamente desde los candidate paths)
- **Unit tests**: [tests/unit/test_qot_calculator.py](file:///home/felipeab/MultiAgentON/tests/unit/test_qot_calculator.py), [tests/unit/test_qot_tool.py](file:///home/felipeab/MultiAgentON/tests/unit/test_qot_tool.py)

## 5. Inputs / Outputs

### `qot_check` @tool
Input (`path: list[dict]`): each dict is a fiber link with `link_id`, `source_node`/`src_node_id`, `target_node`/`dst_node_id`, `length_km`, optional `port_loss_dB`, optional `amplifiers` list.

Output:
```json
{ "feasible": true, "snr_dB": 12.5, "power_dBm": -14.2 }
```
On error:
```json
{ "error": "Unsupported bitrate: 400G..." }
```

## 6. Pipeline Node Status
`src/nodes/qot_validation.py` calls `assess_qot()` directly with real path data from the `candidate_paths` state field. It instantiates `models.FiberLink` objects directly from candidate physics data without requiring a separate bridge module (`qot_bridge.py` fue eliminado al unificar el modelo). Paths without physical configuration are evaluated as infeasible.

## 7. How to Test
```bash
uv run pytest tests/unit/test_qot_calculator.py tests/unit/test_qot_tool.py -v
```

## 8. Cross-References
- [[Architecture_v5]] — Phase 5 description
- [[architecture/features/symbolic_solver]] — Phase 4 that feeds candidate paths into this engine
- [[architecture/features/pipeline_graph]] — LangGraph wiring context
