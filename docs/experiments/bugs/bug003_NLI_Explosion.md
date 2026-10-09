---
title: "BUG-003: GN-Model NLI Explosion (-47 dB GSNR) on Short Spans"
date: 2026-08-07
tags: [bugs, qot, gn-model, edfa, physical-layer]
status: resolved
---

# BUG-003: GN-Model NLI Explosion (-47 dB GSNR) on Short Spans

## 1. Metadata
- **Bug ID:** `BUG-003`
- **Component / Phase:** `src/core/qot_calculator.py` / `src/core/models.py` / Phase 5
- **Status:** Resolved
- **Date Resolved:** 2026-08-07
- **Commit:** `d79e400`
- **Discovered By:** Automated unit tests & physical verification of testbed topology.

---

## 2. Problem Description & Symptoms
Short fiber spans (e.g., 5 km – 10 km) yielded negative GSNR values (-47 dB) or crashed the GN-model calculation due to extreme Non-Linear Interference (NLI).

---

## 3. Root Cause Analysis
- Amplifier gains (EDFA boosters and preamps) were hardcoded to fixed +43 dB gains regardless of span attenuation.
- On a 10 km span with ~2 dB attenuation, a +43 dB gain boosted optical channel power to ~2 Watts (33 dBm), pushing the fiber deep into non-linear saturation where NLI noise dominated the signal.

---

## 4. Resolution Steps
- Calibrated booster and preamp gains in `src/core/models.py` and `qot_calculator.py` to match exact span attenuation (~7 dB for short spans), ensuring channel launch power remains near optimal (~0 dBm / 1 mW).

---

## 5. Verification
- Added tests in `tests/unit/test_qot_calculator.py` passing with realistic GSNR values (20 dB – 28 dB).
- Verified via `uv run pytest`.
