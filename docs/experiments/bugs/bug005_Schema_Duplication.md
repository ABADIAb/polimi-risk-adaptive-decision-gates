---
title: "BUG-005: Schema Duplication Across state.py and models.py"
date: 2026-08-07
tags: [bugs, state, models, typing, architecture]
status: resolved
---

# BUG-005: Schema Duplication Across `state.py` and `models.py`

## 1. Metadata
- **Bug ID:** `BUG-005`
- **Component / Phase:** `src/core/state.py` / `src/core/models.py` / Core Schema
- **Status:** Resolved
- **Date Resolved:** 2026-08-07
- **Commit:** `d79e400`
- **Discovered By:** Static type checker (`pyright` / `mypy`) audit.

---

## 2. Problem Description & Symptoms
Type warnings and schema drift caused by dual definitions of `FiberLink` and `NetworkNode` in both `src/core/state.py` and `src/core/models.py`.

---

## 3. Root Cause Analysis
- `state.py` created independent dataclasses/TypedDicts instead of importing canonical Pydantic domain models from `models.py`.

---

## 4. Resolution Steps
- Centralized domain models into `src/core/models.py`.
- Updated `src/core/state.py` to import and reference models from `models.py`.

---

## 5. Verification
- Verified via `uv run pytest` (227+ passing unit tests).
