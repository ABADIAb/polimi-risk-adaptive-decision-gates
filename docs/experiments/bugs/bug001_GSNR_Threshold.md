---
title: "BUG-001: GSNR Threshold Ignored in Symbolic Solver & QoT Calculator"
date: 2026-08-07
tags: [bugs, qot, symbolic-solver, pddl, physics]
status: resolved
---

# BUG-001: GSNR Threshold Ignored in Symbolic Solver & QoT Calculator

## 1. Metadata
- **Bug ID:** `BUG-001`
- **Component / Phase:** `src/core/qot_calculator.py` / `src/core/symbolic_solver.py` / Phase 4 & 5
- **Status:** Resolved
- **Date Resolved:** 2026-08-07
- **Commit:** `c441318`
- **Discovered By:** User CLI testing (`Route traffic from Milano-A to Milano-C requiring 40 dB GSNR`).

---

## 2. Problem Description & Symptoms
When an operator intent explicitly demanded a high GSNR threshold (e.g. 40 dB), the [[architecture/features/semantic_gate|Semantic Gate]] approved the intent, but the [[architecture/features/radg|RADG]] node also approved the physical path even though the calculated GSNR was only **21.76 dB** (unfeasible).

---

## 3. Root Cause Analysis
1. `src/core/symbolic_solver.py` did not extract `min-gsnr` from the PDDL string regex.
2. `src/core/qot_calculator.py` (`assess_qot`) ignored `target_snr_dB` and defaulted to a static 15.0 dB safety threshold.
3. `src/nodes/qot_validation.py` failed to forward the extracted `min_gsnr` constraint from `pddl_constraints` to the physics engine.

---

## 4. Resolution Steps
- Updated PDDL constraint extraction in `symbolic_solver.py` to parse `(>= (gsnr-db) X)` and `(min-gsnr X)`.
- Updated `assess_qot()` in `qot_calculator.py` to accept `target_snr_dB` and enforce `max(target_snr_dB, DEFAULT_THRESHOLD)`.
- Updated `qot_validation_node` to pass `min_gsnr` directly to `assess_qot()`.

---

## 5. Verification
- Added test cases in `tests/unit/test_symbolic_solver.py` and `tests/unit/test_qot_calculator.py`.
- Verified via `uv run pytest`.
