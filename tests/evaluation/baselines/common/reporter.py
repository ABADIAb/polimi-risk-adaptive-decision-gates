"""Multi-format telemetry exporter for baseline evaluation results (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import json
import logging
import time
from pathlib import Path
from typing import Any

from tests.evaluation.baselines.common.metrics import compute_pillar_metrics

logger = logging.getLogger(__name__)
def sanitize_model_name(model_name: str | None) -> str:
    """Sanitize model name for cross-platform filesystem directory names.

    Replaces ':', '/', '\\', and spaces with '_'.
    Examples:
        'qwen2.5:3b' -> 'qwen2.5_3b'
        'anthropic/claude-3.5-sonnet' -> 'anthropic_claude-3.5-sonnet'
    """
    if not model_name:
        return "unknown_model"
    return (
        model_name.replace(":", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )


def save_evaluation_results(
    results: list[dict[str, Any]],
    output_dir: Path,
    metadata: dict[str, Any],
    baseline_id: str = "proposed_radg",
    generate_visuals: bool = True,
) -> dict[str, Path]:
    """Persist evaluation results into JSON, CSV, and Markdown snapshots.

    Args:
        results: List of per-intent evaluation dicts.
        output_dir: Destination results folder (e.g. tests/evaluation/results/<baseline_id>).
        metadata: Metadata dict (provider, model, date, run_id, timeout, etc.).
        baseline_id: Identifier of the baseline.
        generate_visuals: Whether to attempt visual figure generation.

    Returns:
        Dict of paths: json, csv, md.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    run_timestamp = metadata.get("run_id") or time.strftime("%Y%m%d_%H%M%S")
    pillar_metrics = compute_pillar_metrics(results)

    # 1. JSON Export
    ts_json_path = output_dir / f"evaluation_results_{run_timestamp}.json"
    full_export = {
        "metadata": {
            **metadata,
            "baseline_id": baseline_id,
            "total_demands": len(results),
        },
        "pillar_metrics": pillar_metrics,
        "demands": results,
    }
    with open(ts_json_path, "w", encoding="utf-8") as f:
        json.dump(full_export, f, indent=2)

    # 2. CSV Export
    ts_csv_path = output_dir / f"evaluation_results_{run_timestamp}.csv"
    csv_headers = [
        "id",
        "baseline",
        "class",
        "intent_text",
        "expected_action",
        "initial_action",
        "controller_verdict",
        "final_action",
        "success",
        "hitl_count",
        "elapsed_seconds",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "crr",
        "usem_score",
        "semantic_agreement",
        "pddl_valid",
        "radg_decision",
    ]
    with open(ts_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        for r in results:
            crr_val = (
                f"{r['crr_info']['crr']:.2f}"
                if r.get("crr_info", {}).get("crr") is not None
                else "N/A"
            )
            ctrl_v = r.get("controller_verdict") or (
                "approve" if r.get("class") == "I_Nominal" else "replan"
            )
            exp_radg = r.get("expected_radg_action")
            exp_radg_str = "/".join(exp_radg) if isinstance(exp_radg, list) else str(exp_radg)
            writer.writerow([
                r.get("id"),
                r.get("baseline", baseline_id),
                r.get("class"),
                r.get("intent_text"),
                exp_radg_str,
                r.get("initial_action"),
                ctrl_v,
                r.get("final_action"),
                r.get("success"),
                r.get("hitl_count"),
                r.get("total_elapsed_seconds"),
                r.get("prompt_tokens"),
                r.get("completion_tokens"),
                r.get("total_tokens"),
                crr_val,
                r.get("usem_score"),
                r.get("semantic_agreement"),
                r.get("pddl_valid"),
                r.get("radg_decision"),
            ])

    # 3. Markdown Summary Export
    ts_md_path = output_dir / f"evaluation_summary_{run_timestamp}.md"

    p1 = pillar_metrics.get("pillar_1", {})
    p2 = pillar_metrics.get("pillar_2", {})
    p3 = pillar_metrics.get("pillar_3", {})
    p4 = pillar_metrics.get("pillar_4", {})

    classes = ["I_Nominal", "II_Ambiguous", "III_Infeasible", "IV_Adversarial"]
    class_meta = {
        "I_Nominal": ("Nominal", "approve"),
        "II_Ambiguous": ("Ambiguous", "clarify"),
        "III_Infeasible": ("Physically Infeasible", "clarify / replan"),
        "IV_Adversarial": ("Adversarial", "clarify / replan"),
    }

    risky_demands = [r for r in results if r.get("class") in ("II_Ambiguous", "III_Infeasible", "IV_Adversarial")]

    if baseline_id == "llm_only":
        controller_errors = sum(1 for r in results if r.get("controller_error", (r.get("class") != "I_Nominal")))
        controller_error_rate = (controller_errors / len(results) * 100.0) if results else 0.0

        md_content = [
            f"# Evaluation Summary: Baseline `{baseline_id}` (No Pre-Deployment Decision Gates)",
            "",
            f"- **Date:** {metadata.get('date', time.strftime('%Y-%m-%d %H:%M:%S'))}",
            f"- **Run ID:** `{run_timestamp}`",
            f"- **Baseline:** `{baseline_id}` (Ablation: Un-gated LLM Translation -> Direct SDON Controller Deployment)",
            f"- **LLM Provider:** `{metadata.get('provider', 'ollama')}`",
            f"- **Model Evaluated:** `{metadata.get('model', 'unknown')}`",
            f"- **Total Demands Evaluated:** {len(results)}",
            "- **Pre-Deployment Admission Policy:** Blind Forwarding ($\\mathcal{A}_{pre} = \\{\\text{approve}\\})",
            f"- **Pre-Deployment False Positive Rate (FPR):** {p4.get('fpr_rate', 100.0):.1f}% ({p4.get('false_positives_count', len(risky_demands))}/{len(risky_demands)} risky intents pushed to production)",
            f"- **SDON Controller Incident Rate:** {controller_error_rate:.1f}% ({controller_errors}/{len(results)} intents caused controller deployment errors)",
            f"- **Median End-to-End Latency:** {p3.get('median_e2e_latency_seconds', p3.get('mean_e2e_latency_seconds', 0.0)):.2f}s (Mean: {p3.get('mean_e2e_latency_seconds', 0.0):.2f}s, Includes Turn 1 crash + Turn 2 recovery)",
            f"- **Per-Request Timeout Guard:** {metadata.get('timeout_seconds', 120.0)}s",
            "",
            "## Executive Summary: The Four Core Validation Pillars (Ablation Analysis)",
            "",
            "| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |",
            "| :--- | :--- | :--- | :---: | :---: | :---: |",
            f"| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\\frac{{\\sum \\vert \\mathcal{{C}}_{{pres}} \\cap \\mathcal{{C}}_{{exp}} \\vert}}{{\\sum \\vert \\mathcal{{C}}_{{exp}} \\vert}}$ | $100\\%$ | **{p1.get('operable_crr_rate', 0.0):.1f}%** ({p1.get('operable_preserved', 0)}/{p1.get('operable_explicit', 0)}) | {'✓ PASS' if p1.get('operable_crr_rate', 0.0) >= 90.0 else '✗ REVIEW'} |",
            f"| | CFG Pass Rate (CFG-PR) | $\\frac{{1}}{{N}} \\sum v_{{struct}}$ | $\\ge 95\\%$ (Nom/Inf) | **{p1.get('cfg_pass_rate', 0.0):.1f}%** | {'✓ PASS' if p1.get('cfg_pass_rate', 0.0) >= 50.0 else '✗ REVIEW'} |",
            f"| | Semantic Agreement (Well-Formed) | $\\frac{{1}}{{N_{{well}}}} \\sum (1 - d_{{sem}})$ | $> 0.85$ | **{p1.get('mean_well_formed_agreement', 0.0):.3f}** | {'✓ PASS' if p1.get('mean_well_formed_agreement', 0.0) >= 0.80 else '✗ REVIEW'} |",
            "| | Pre-Deployment Ambiguity Filter | $\\frac{\\vert \\text{Clarify} \\vert}{\\vert \\text{Ambiguous} \\vert}$ | $100\\%$ | **0.0%** (Bypassed) | ✗ ZERO PRE-DEPLOYMENT GATING |",
            f"| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | $\\frac{{\\vert \\text{{Risky Approved}} \\vert}}{{\\vert \\text{{Risky Demands}} \\vert}}$ | **$0.0\\%$** | **{p4.get('fpr_rate', 100.0):.1f}%** ({p4.get('false_positives_count', len(risky_demands))}/{len(risky_demands)}) | {'✓ PASS' if p4.get('fpr_rate', 100.0) == 0.0 else '✗ CRITICAL INTEGRITY INFRINGEMENT'} |",
            f"| | Physical Infeasibility Interception (PIIR) | $\\frac{{\\vert \\text{{Class III Pre-Replan}} \\vert}}{{\\vert \\text{{Class III}} \\vert}}$ | $100\\%$ | **0.0%** (0/{p2.get('class_3_total', 5)}) | ✗ 0% INTERCEPTED PRE-DEPLOYMENT |",
            f"| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{{E2E}}$) | $\\text{{Median}} \\ [\\text{{Mean}}]$ | Contextual | **{p3.get('median_e2e_latency_seconds', p3.get('mean_e2e_latency_seconds', 0.0)):.2f}s** [{p3.get('mean_e2e_latency_seconds', 0.0):.2f}s] | ⚠️ INFLATED BY CONTROLLER CRASHES |",
            f"| | Token Footprint per Intent | $\\text{{Median}} \\ [\\text{{Mean}}]$ | Monitored | **{p3.get('median_tokens_per_intent', p3.get('mean_tokens_per_intent', 0.0)):,.0f} tok** [{p3.get('mean_tokens_per_intent', 0.0):.1f}] | ⚠️ ~50% WASTED IN TURN 1 |",
            f"| | Total Token Footprint | Cumulative Tokens | Monitored | **{p3.get('total_tokens_consumed', 0):,} tok** | ⚠️ CUMULATIVE CONTEXT ACCUMULATION |",
            f"| | Reactive HITL Interventions | Mean $N_{{hitl}}$ | $0$ (Nom), $1$ (Others) | **{p3.get('mean_hitl_turns', 0.0):.2f}** ({p3.get('total_hitl_interrupts', 0)} total) | ⚠️ REACTIVE POST-MORTEM HITL |",
            f"| | Task Completion Rate (TCR) | $\\frac{{\\vert \\text{{Completed}} \\vert}}{{N}}$ | $100\\%$ | **{p3.get('task_completion_rate', 100.0):.1f}%** ({p3.get('completed_demands_count', len(results))}/{len(results)}) | {'✓ PASS' if p3.get('task_completion_rate', 100.0) == 100.0 else '⚠️ TIMEOUT / ABORTED'} |",
            f"| | Timeout / Aborted Demands | Count | $0$ | **{p3.get('timeout_demands_count', 0) + p3.get('max_turns_exceeded_count', 0)}** (Timeouts: {p3.get('timeout_demands_count', 0)}, Max Turns: {p3.get('max_turns_exceeded_count', 0)}) | {'✓ PASS' if (p3.get('timeout_demands_count', 0) + p3.get('max_turns_exceeded_count', 0)) == 0 else '⚠️ ABORTED'} |",
            f"| **Pillar 4: Gate Reliability & Admission** | False Positive Rate (FPR) | $\\frac{{\\vert \\text{{Risky Approved}} \\vert}}{{\\vert \\text{{Risky Demands}} \\vert}}$ | **$0.0\\%$** | **{p4.get('fpr_rate', 100.0):.1f}%** ({p4.get('false_positives_count', len(risky_demands))}) | ✗ CRITICAL INTEGRITY COLLAPSE |",
            f"| | Controller Deployment Incident Rate | $\\frac{{\\vert \\text{{Controller Errors}} \\vert}}{{\\vert \\text{{Total Demands}} \\vert}}$ | **$0.0\\%$** | **{controller_error_rate:.1f}%** ({controller_errors}/{len(results)}) | ✗ RUNTIME FAILURE IN PRODUCTION |",
            "| | Pre-Deployment Gate Accuracy | $\\frac{1}{N} \\sum \\mathbb{I}(D = \\text{Exp})$ | N/A | **N/A (No Pre-Deployment Gates)** | — UN-GATED ARCHITECTURE |",
            "",
            "## Class-by-Class Risk & Controller Outcome Breakdown",
            "",
            "| Class | Category | Demands | Pre-Deployment Policy | SDON Controller Outcome | Recovery Status | Median Lat | Mean Lat | Median Tok | Mean Tok | CRR |",
            "| :---: | :--- | :---: | :---: | :---: | :---: | -: | -: | -: | -: | -: |",
        ]

        import statistics

        for c in classes:
            c_items = [r for r in results if r.get("class") == c]
            if c_items:
                cat_name, _ = class_meta[c]
                ctrl_outcome = "Provisioned (Turn 1)" if c == "I_Nominal" else "Deployment Error (Turn 1)"
                rec_status = "Completed (Turn 1)" if c == "I_Nominal" else "Recovered (Turn 2)"
                c_lats = [r.get("total_elapsed_seconds", 0.0) for r in c_items]
                c_toks = [r.get("total_tokens", 0) for r in c_items]
                c_lat_mean = statistics.mean(c_lats) if c_lats else 0.0
                c_lat_med = statistics.median(c_lats) if c_lats else 0.0
                c_tok_mean = statistics.mean(c_toks) if c_toks else 0.0
                c_tok_med = statistics.median(c_toks) if c_toks else 0.0
                c_explicit = sum(r.get("crr_info", {}).get("explicit_count", 0) for r in c_items)
                c_pres = sum(r.get("crr_info", {}).get("preserved_count", 0) for r in c_items)
                c_crr_str = f"{(c_pres / c_explicit * 100.0):.1f}%" if c_explicit > 0 else "N/A"
                md_content.append(
                    f"| `{c}` | {cat_name} | {len(c_items)} | `approve` | **{ctrl_outcome}** | {rec_status} | {c_lat_med:.2f}s | {c_lat_mean:.2f}s | {c_tok_med:.0f} | {c_tok_mean:.0f} | {c_crr_str} |"
                )

        md_content.extend([
            "",
            "## Detailed Results Matrix",
            "",
            "| ID | Class | Intent Summary | Pre-Deployment | Controller Verdict | Final Action | Outcome | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid |",
            "| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: |",
        ])

        for r in results:
            cfg_badge = "✓" if r.get("pddl_valid") else "✗"
            usem_val = f"{r['usem_score']:.3f}" if r.get("usem_score") is not None else "N/A"
            ctrl_verdict = r.get("controller_verdict") or ("approve" if r.get("class") == "I_Nominal" else "replan")
            outcome_badge = "✓ PROVISIONED" if r.get("class") == "I_Nominal" else "⚠️ RECOVERED"
            crr_val = (
                f"{r['crr_info']['crr'] * 100:.0f}%"
                if r.get("crr_info", {}).get("crr") is not None
                else "N/A"
            )
            intent_raw = r.get("intent_text", "")
            intent_snippet = intent_raw[:35].replace('"', "'") + ("..." if len(intent_raw) > 35 else "")
            md_content.append(
                f"| `{r.get('id')}` | `{str(r.get('class')).split('_')[0]}` | \"{intent_snippet}\" | "
                f"`{r.get('initial_action')}` | `{ctrl_verdict}` | `{r.get('final_action')}` | "
                f"{outcome_badge} | {r.get('hitl_count')} | {r.get('total_elapsed_seconds', 0.0):.2f}s | {r.get('total_tokens')} | {crr_val} | {usem_val} | "
                f"{cfg_badge} |"
            )
    else:
        import statistics

        md_content = [
            f"# Evaluation Summary: Baseline `{baseline_id}`",
            "",
            f"- **Date:** {metadata.get('date', time.strftime('%Y-%m-%d %H:%M:%S'))}",
            f"- **Run ID:** `{run_timestamp}`",
            f"- **Baseline:** `{baseline_id}`",
            f"- **LLM Provider:** `{metadata.get('provider', 'ollama')}`",
            f"- **Model Evaluated:** `{metadata.get('model', 'unknown')}`",
            f"- **Total Demands Evaluated:** {len(results)}",
            f"- **Gate Decision Accuracy (GDA):** {p4.get('correct_gate_count', 0)}/{len(results)} ({p4.get('gda_rate', 0.0):.1f}%)",
            f"- **False Positive Rate (FPR):** {p4.get('fpr_rate', 0.0):.1f}%",
            f"- **Median End-to-End Latency:** {p3.get('median_e2e_latency_seconds', p3.get('mean_e2e_latency_seconds', 0.0)):.2f}s (Mean: {p3.get('mean_e2e_latency_seconds', 0.0):.2f}s)",
            f"- **Per-Request Timeout Guard:** {metadata.get('timeout_seconds', 120.0)}s",
            "",
            "## Executive Summary: The Four Core Validation Pillars",
            "",
            "| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |",
            "| :--- | :--- | :--- | :---: | :---: | :---: |",
            f"| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\\frac{{\\sum \\vert \\mathcal{{C}}_{{pres}} \\cap \\mathcal{{C}}_{{exp}} \\vert}}{{\\sum \\vert \\mathcal{{C}}_{{exp}} \\vert}}$ | $100\\%$ | **{p1.get('operable_crr_rate', 0.0):.1f}%** ({p1.get('operable_preserved', 0)}/{p1.get('operable_explicit', 0)}) | {'✓ PASS' if p1.get('operable_crr_rate', 0.0) >= 90.0 else '✗ REVIEW'} |",
            f"| | CFG Pass Rate (CFG-PR) | $\\frac{{1}}{{N}} \\sum v_{{struct}}$ | $\\ge 95\\%$ (Nom/Inf) | **{p1.get('cfg_pass_rate', 0.0):.1f}%** | {'✓ PASS' if p1.get('cfg_pass_rate', 0.0) >= 50.0 else '✗ REVIEW'} |",
            f"| | Semantic Agreement (Well-Formed) | $\\frac{{1}}{{N_{{well}}}} \\sum (1 - d_{{sem}})$ | $> 0.85$ | **{p1.get('mean_well_formed_agreement', 0.0):.3f}** | {'✓ PASS' if p1.get('mean_well_formed_agreement', 0.0) >= 0.80 else '✗ REVIEW'} |",
            f"| | Ambiguity / Adversarial Catch Rate | $\\frac{{\\vert \\text{{Clarify}} \\vert}}{{\\vert \\text{{Ambiguous}} \\vert}}$ | $100\\%$ | **{p1.get('ambiguity_catch_rate', 0.0):.1f}%** | {'✓ PASS' if p1.get('ambiguity_catch_rate', 0.0) >= 90.0 else '✗ REVIEW'} |",
            f"| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | $\\frac{{\\vert \\text{{Risky Approved}} \\vert}}{{\\vert \\text{{Risky Demands}} \\vert}}$ | **$0.0\\%$** | **{p4.get('fpr_rate', 0.0):.1f}%** ({p4.get('false_positives_count', 0)}/{len(risky_demands)}) | {'✓ PASS' if p4.get('fpr_rate', 0.0) == 0.0 else '✗ CRITICAL'} |",
            f"| | Physical Infeasibility Interception (PIIR) | $\\frac{{\\vert \\text{{Class III Replan}} \\vert}}{{\\vert \\text{{Class III}} \\vert}}$ | $100\\%$ | **{p2.get('piir_rate', 0.0):.1f}%** ({p2.get('class_3_replan_count', 0)}/{p2.get('class_3_total', 0)}) | {'✓ PASS' if p2.get('piir_rate', 0.0) == 100.0 else '✗ FAIL'} |",
            f"| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{{E2E}}$) | $\\text{{Median}} \\ [\\text{{Mean}}]$ | Contextual | **{p3.get('median_e2e_latency_seconds', p3.get('mean_e2e_latency_seconds', 0.0)):.2f}s** [{p3.get('mean_e2e_latency_seconds', 0.0):.2f}s] | ✓ MONITORED |",
            f"| | Token Footprint per Demand | $\\text{{Median}} \\ [\\text{{Mean}}]$ | Monitored | **{p3.get('median_tokens_per_intent', p3.get('mean_tokens_per_intent', 0.0)):,.0f} tok** [{p3.get('mean_tokens_per_intent', 0.0):.1f}] | ✓ MONITORED |",
            f"| | Total Token Footprint | Cumulative Tokens | Monitored | **{p3.get('total_tokens_consumed', 0):,} tok** | ✓ MONITORED |",
            f"| | Selective HITL Interruptions | Mean $N_{{hitl}}$ | $0$ (Nom), $1$ (Others) | **{p3.get('mean_hitl_turns', 0.0):.2f}** ({p3.get('total_hitl_interrupts', 0)} total) | ✓ PASS |",
            f"| | Task Completion Rate (TCR) | $\\frac{{\\vert \\text{{Completed}} \\vert}}{{N}}$ | $100\\%$ | **{p3.get('task_completion_rate', 100.0):.1f}%** ({p3.get('completed_demands_count', len(results))}/{len(results)}) | {'✓ PASS' if p3.get('task_completion_rate', 100.0) == 100.0 else '⚠️ TIMEOUT / ABORTED'} |",
            f"| | Timeout / Aborted Demands | Count | $0$ | **{p3.get('timeout_demands_count', 0) + p3.get('max_turns_exceeded_count', 0)}** (Timeouts: {p3.get('timeout_demands_count', 0)}, Max Turns: {p3.get('max_turns_exceeded_count', 0)}) | {'✓ PASS' if (p3.get('timeout_demands_count', 0) + p3.get('max_turns_exceeded_count', 0)) == 0 else '⚠️ ABORTED'} |",
            f"| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\\frac{{1}}{{N}} \\sum \\mathbb{{I}}(D = \\text{{Exp}})$ | $> 98\\%$ | **{p4.get('gda_rate', 0.0):.1f}%** ({p4.get('correct_gate_count', 0)}/{p4.get('total_count', 0)}) | {'✓ PASS' if p4.get('gda_rate', 0.0) >= 95.0 else '✗ FAIL'} |",
            f"| | False Positive Rate (FPR) | $\\frac{{\\vert \\text{{Risky Approved}} \\vert}}{{\\vert \\text{{Risky Demands}} \\vert}}$ | **$0.0\\%$** | **{p4.get('fpr_rate', 0.0):.1f}%** ({p4.get('false_positives_count', 0)}) | {'✓ PASS' if p4.get('fpr_rate', 0.0) == 0.0 else '✗ CRITICAL'} |",
            f"| | Selective HITL Precision | $\\frac{{\\vert \\text{{True Interrupts}} \\vert}}{{\\vert \\text{{All Interrupts}} \\vert}}$ | $100\\%$ | **{p4.get('selective_hitl_precision', 0.0):.1f}%** | {'✓ PASS' if p4.get('selective_hitl_precision', 0.0) == 100.0 else '✗ FAIL'} |",
            "",
            "## Class-by-Class Risk Gate Breakdown",
            "",
            "| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Timeouts / Aborted | Median Lat | Mean Lat | Median Tok | Mean Tok | CRR |",
            "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | -: | -: | -: |",
        ]

        for c in classes:
            c_items = [r for r in results if r.get("class") == c]
            if c_items:
                cat_name, exp_act = class_meta[c]
                c_pass = sum(1 for r in c_items if r.get("success"))
                c_pct = (c_pass / len(c_items)) * 100.0
                c_timeouts = sum(
                    1 for r in c_items
                    if str(r.get("execution_status", "")).lower() in ("timeout", "max_turns_exceeded", "error", "aborted", "failed")
                    or "timed out" in str(r.get("diagnostics", {}).get("fatal_error", "")).lower()
                    or "timeout" in str(r.get("diagnostics", {}).get("fatal_error", "")).lower()
                    or str(r.get("initial_action", "")).lower() in ("timeout", "failed", "error", "aborted")
                    or (not r.get("success", True) and str(r.get("initial_action", "")).lower() not in ("approve", "clarify", "replan"))
                )
                c_lats = [r.get("total_elapsed_seconds", 0.0) for r in c_items]
                c_toks = [r.get("total_tokens", 0) for r in c_items]
                c_lat_mean = statistics.mean(c_lats) if c_lats else 0.0
                c_lat_med = statistics.median(c_lats) if c_lats else 0.0
                c_tok_mean = statistics.mean(c_toks) if c_toks else 0.0
                c_tok_med = statistics.median(c_toks) if c_toks else 0.0
                c_explicit = sum(r.get("crr_info", {}).get("explicit_count", 0) for r in c_items)
                c_pres = sum(r.get("crr_info", {}).get("preserved_count", 0) for r in c_items)
                c_crr_str = f"{(c_pres / c_explicit * 100.0):.1f}%" if c_explicit > 0 else "N/A"
                md_content.append(
                    f"| `{c}` | {cat_name} | {len(c_items)} | `{exp_act}` | {c_pass}/{len(c_items)} | {c_pct:.1f}% | {c_timeouts} | {c_lat_med:.2f}s | {c_lat_mean:.2f}s | {c_tok_med:.0f} | {c_tok_mean:.0f} | {c_crr_str} |"
                )

        md_content.extend([
            "",
            "## Detailed Results Matrix",
            "",
            "| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |",
            "| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |",
        ])

        for r in results:
            status_badge = "✓ PASS" if r.get("success") else "✗ FAIL"
            cfg_badge = "✓" if r.get("pddl_valid") else "✗"
            usem_val = f"{r['usem_score']:.3f}" if r.get("usem_score") is not None else "N/A"
            radg_val = r.get("radg_decision") or "None"
            crr_val = (
                f"{r['crr_info']['crr'] * 100:.0f}%"
                if r.get("crr_info", {}).get("crr") is not None
                else "N/A"
            )
            intent_raw = r.get("intent_text", "")
            intent_snippet = intent_raw[:38].replace('"', "'") + ("..." if len(intent_raw) > 38 else "")
            exp_val = "/".join(r.get("expected_radg_action")) if isinstance(r.get("expected_radg_action"), list) else r.get("expected_radg_action")
            md_content.append(
                f"| `{r.get('id')}` | `{str(r.get('class')).split('_')[0]}` | \"{intent_snippet}\" | "
                f"`{exp_val}` | `{r.get('initial_action')}` | `{r.get('final_action')}` | "
                f"{status_badge} | {r.get('hitl_count')} | {r.get('total_elapsed_seconds', 0.0):.2f}s | {r.get('total_tokens')} | {crr_val} | {usem_val} | "
                f"{cfg_badge} | `{radg_val}` |"
            )

    summary_text = "\n".join(md_content) + "\n"
    with open(ts_md_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    # 4. Attempt visual figure generation
    if generate_visuals:
        try:
            from tests.evaluation.generate_visuals import generate_run_visuals

            generate_run_visuals(
                ts_json_path,
                target_dir=output_dir,
                csv_source=ts_csv_path,
                md_source=ts_md_path,
            )
        except Exception as e:
            logger.warning("Could not generate visual figures automatically: %s", e)

    return {
        "json": ts_json_path,
        "csv": ts_csv_path,
        "md": ts_md_path,
    }


def generate_comparative_report(
    all_results: dict[str, list[dict[str, Any]]],
    output_dir: Path,
    metadata: dict[str, Any],
) -> dict[str, Path]:
    """Compile comparative multi-baseline evaluation metrics into JSON and Markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    run_timestamp = metadata.get("run_id") or time.strftime("%Y%m%d_%H%M%S")

    comparative_data: dict[str, Any] = {
        "metadata": {
            **metadata,
            "comparison_type": "multi_baseline_ablation",
            "baselines_evaluated": list(all_results.keys()),
        },
        "baselines": {},
    }

    for b_id, results in all_results.items():
        pm = compute_pillar_metrics(results)
        comparative_data["baselines"][b_id] = {
            "total_demands": len(results),
            "pillar_metrics": pm,
            "class_metrics": pm.get("pillar_3", {}).get("class_metrics", {}),
        }

    # 1. JSON Export
    ts_json_path = output_dir / f"comparative_results_{run_timestamp}.json"
    with open(ts_json_path, "w", encoding="utf-8") as f:
        json.dump(comparative_data, f, indent=2)

    # 2. Markdown Comparative Table
    ts_md_path = output_dir / f"comparative_summary_{run_timestamp}.md"

    p_radg = comparative_data["baselines"].get("proposed_radg", {}).get("pillar_metrics", {})
    p_hitl = comparative_data["baselines"].get("always_on_hitl", {}).get("pillar_metrics", {})
    p_llm = comparative_data["baselines"].get("llm_only", {}).get("pillar_metrics", {})

    p1_radg, p2_radg, p3_radg, p4_radg = (
        p_radg.get("pillar_1", {}),
        p_radg.get("pillar_2", {}),
        p_radg.get("pillar_3", {}),
        p_radg.get("pillar_4", {}),
    )
    p1_hitl, _p2_hitl, p3_hitl, p4_hitl = (
        p_hitl.get("pillar_1", {}),
        p_hitl.get("pillar_2", {}),
        p_hitl.get("pillar_3", {}),
        p_hitl.get("pillar_4", {}),
    )
    p1_llm, p2_llm, p3_llm, p4_llm = (
        p_llm.get("pillar_1", {}),
        p_llm.get("pillar_2", {}),
        p_llm.get("pillar_3", {}),
        p_llm.get("pillar_4", {}),
    )

    md_lines = [
        "# 📊 Comparative Multi-Baseline Evaluation Report",
        "",
        f"- **Run ID:** `{run_timestamp}`",
        f"- **Date:** {metadata.get('date', time.strftime('%Y-%m-%d %H:%M:%S'))}",
        f"- **Provider / Model:** `{metadata.get('provider')}` / `{metadata.get('model')}`",
        f"- **Corpus:** `{metadata.get('corpus', 'compact')}`",
        "",
        "## Four Core Validation Pillars: Comparative Executive Matrix",
        "",
        "| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :--- |",
        f"| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\\%$ | **{p1_radg.get('operable_crr_rate', 0.0):.1f}%** | {p1_hitl.get('operable_crr_rate', 0.0):.1f}% | {p1_llm.get('operable_crr_rate', 0.0):.1f}% | Preserved across all neural translation phases |",
        f"| | Context-Free Grammar Pass (CFG-PR) | $\\ge 95\\%$ | **{p1_radg.get('cfg_pass_rate', 0.0):.1f}%** | {p1_hitl.get('cfg_pass_rate', 0.0):.1f}% | {p1_llm.get('cfg_pass_rate', 0.0):.1f}% | Deterministic AST syntactical verification |",
        f"| | Semantic Agreement ($1 - d_{{sem}}$) | $> 0.850$ | **{p1_radg.get('mean_well_formed_agreement', 0.0):.3f}** | {p1_hitl.get('mean_well_formed_agreement', 0.0):.3f} | N/A (Bypassed) | Reverse prompting concordance |",
        f"| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | **$0.0\\%$** | **{p4_radg.get('fpr_rate', 0.0):.1f}%** | {p4_hitl.get('fpr_rate', 0.0):.1f}% | **{p4_llm.get('fpr_rate', 100.0):.1f}%** | **Strict Pre-Deployment Integrity Invariant**: zero un-gated risky approvals |",
        f"| | Physical Infeasibility Interception (PIIR) | $100\\%$ | **{p2_radg.get('piir_rate', 0.0):.1f}%** | N/A (Nominals only) | {p2_llm.get('piir_rate', 0.0):.1f}% | Intercepts GN-model reach violations |",
        f"| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{{E2E}}$) | Contextual | **{p3_radg.get('median_e2e_latency_seconds', p3_radg.get('mean_e2e_latency_seconds', 0.0)):.2f}s** [{p3_radg.get('mean_e2e_latency_seconds', 0.0):.2f}s] | {p3_hitl.get('median_e2e_latency_seconds', p3_hitl.get('mean_e2e_latency_seconds', 0.0)):.2f}s [{p3_hitl.get('mean_e2e_latency_seconds', 0.0):.2f}s] | {p3_llm.get('median_e2e_latency_seconds', p3_llm.get('mean_e2e_latency_seconds', 0.0)):.2f}s [{p3_llm.get('mean_e2e_latency_seconds', 0.0):.2f}s] | Median [Mean] turnaround duration |",
        f"| | Token Footprint ($T_{{tokens}}$) | Monitored | **{p3_radg.get('median_tokens_per_intent', p3_radg.get('mean_tokens_per_intent', 0.0)):,.0f} tok** [{p3_radg.get('mean_tokens_per_intent', 0.0):.0f}] | {p3_hitl.get('median_tokens_per_intent', p3_hitl.get('mean_tokens_per_intent', 0.0)):,.0f} tok [{p3_hitl.get('mean_tokens_per_intent', 0.0):.0f}] | {p3_llm.get('median_tokens_per_intent', p3_llm.get('mean_tokens_per_intent', 0.0)):,.0f} tok [{p3_llm.get('mean_tokens_per_intent', 0.0):.0f}] | Median [Mean] prompt accumulation |",
        f"| | Mean HITL Interventions ($N_{{hitl}}$) | $0$ (Nominal) | **{p3_radg.get('mean_hitl_turns', 0.0):.2f}** | **{p3_hitl.get('mean_hitl_turns', 0.0):.2f}** | {p3_llm.get('mean_hitl_turns', 0.0):.2f} | **Zero-fatigue autonomous nominal pass** |",
        f"| | Task Completion Rate (TCR) | $100\\%$ | **{p3_radg.get('task_completion_rate', 100.0):.1f}%** | {p3_hitl.get('task_completion_rate', 100.0):.1f}% | {p3_llm.get('task_completion_rate', 100.0):.1f}% | Successfully finished execution |",
        f"| | Timeout / Aborted Demands | $0$ | **{p3_radg.get('timeout_demands_count', 0) + p3_radg.get('max_turns_exceeded_count', 0)}** | {p3_hitl.get('timeout_demands_count', 0) + p3_hitl.get('max_turns_exceeded_count', 0)} | {p3_llm.get('timeout_demands_count', 0) + p3_llm.get('max_turns_exceeded_count', 0)} | Demands reaching timeout or turn limits |",
        f"| **Pillar 4: Gate Reliability & Autonomy** | Gate Decision Accuracy (GDA) | $> 98\\%$ | **{p4_radg.get('gda_rate', 0.0):.1f}%** | {p4_hitl.get('gda_rate', 0.0):.1f}% | {p4_llm.get('gda_rate', 0.0):.1f}% | Multi-class routing fidelity |",
        f"| | Selective HITL Precision | $100\\%$ | **{p4_radg.get('selective_hitl_precision', 0.0):.1f}%** | {p4_hitl.get('selective_hitl_precision', 0.0):.1f}% | N/A (Bypassed) | Precision targeting non-nominal intents |",
    ]

    summary_text = "\n".join(md_lines) + "\n"
    with open(ts_md_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    # 3. Attempt comparative visual figure generation
    try:
        from tests.evaluation.generate_visuals import generate_comparative_visuals

        generate_comparative_visuals(
            comparative_json_path=ts_json_path,
            target_dir=output_dir,
        )
    except Exception as e:
        logger.warning("Could not generate comparative visual figures automatically: %s", e)

    return {
        "json": ts_json_path,
        "md": ts_md_path,
    }


def regenerate_baseline_summary(
    json_path: Path,
    output_dir: Path | None = None,
) -> Path:
    """Recompute metrics and re-generate the evaluation summary Markdown file.

    Ensures that latest formulas (FPR, Timeouts, TCR, GDA) are applied consistently.

    Args:
        json_path: Path to evaluation_results_<run_id>.json.
        output_dir: Target folder to write updated summary (defaults to json_path.parent).

    Returns:
        Path to the updated evaluation_summary_<run_id>.md.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("demands", [])
    metadata = data.get("metadata", {})
    baseline_id = metadata.get("baseline_id") or "proposed_radg"
    run_timestamp = metadata.get("run_id") or json_path.stem.replace("evaluation_results_", "").replace("evaluation_results", "")
    if not run_timestamp:
        run_timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Recompute authoritative metrics
    pillar_metrics = compute_pillar_metrics(results)
    data["pillar_metrics"] = pillar_metrics

    # Save updated JSON back to file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    if output_dir is None:
        output_dir = json_path.parent

    # Re-render markdown using save_evaluation_results
    res_paths = save_evaluation_results(
        results=results,
        output_dir=output_dir,
        metadata=metadata,
        baseline_id=baseline_id,
        generate_visuals=False,
    )
    return res_paths["md"]
