#!/usr/bin/env python3
"""Integrate the full complex orientation-sphere result into the v20 gap ledger.

This runs after ``close_open_gaps_v20.py``.  It preserves the mature base gap
schema consumed by the ultimate gate while adding fail-closed checks and a
machine-readable summary for the full complex C^3 orientation sphere.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
BASE_PATH = ROOT / "OPEN_GAPS_CLOSURE_V20_VERDICT.json"
SPHERE_PATH = ROOT / "PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json"
MD_PATH = ROOT / "OPEN_GAPS_CLOSURE_V20.md"


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def augment_report(base: dict[str, Any], sphere: dict[str, Any]) -> dict[str, Any]:
    flags = sphere.get("flag") or {}
    scan = sphere.get("scan") or {}
    counts = scan.get("aggregate_counts") or {}
    diagnostics = scan.get("replicate_fraction_diagnostics") or {}
    extrema = scan.get("sampled_extrema") or {}
    anchors = scan.get("anchors") or {}
    checks = {
        "sphere_artifact_passes": sphere.get("n_failed") == 0,
        "full_complex_three_family_orientation_sampled": flags.get(
            "full_complex_three_family_orientation_sphere_sampled", False
        ),
        "rotational_measure_explicit": flags.get(
            "rotationally_invariant_orientation_measure_explicit", False
        ),
        "scrambled_replicates_executed": flags.get(
            "scrambled_sobol_replicates_executed", False
        ),
        "exact_sample_counts": counts.get("n_total_points") == 16384
        and counts.get("n_NA62_excluded") == 16286
        and counts.get("n_NA62_surviving") == 98
        and counts.get("n_TWIST_excluded") == 0
        and counts.get("n_TWIST_surviving") == 16384,
        "exact_chosen_measure_fraction": counts.get(
            "NA62_excluded_fraction_under_chosen_geometric_measure"
        )
        == 0.9940185546875,
        "replicate_range_recorded": diagnostics.get("NA62_min")
        == 0.99169921875
        and diagnostics.get("NA62_max") == 0.99658203125,
        "excluded_and_surviving_orientations_exist": flags.get(
            "NA62_has_excluded_samples", False
        )
        and flags.get("NA62_has_surviving_samples", False),
        "all_sampled_orientations_pass_twist": not flags.get(
            "TWIST_has_excluded_samples", True
        )
        and flags.get("TWIST_has_surviving_samples", False),
        "geometric_fraction_not_uv_probability": not flags.get(
            "geometric_fraction_is_uv_probability", True
        )
        and not counts.get("geometric_fraction_is_uv_probability", True),
        "remaining_portal_magnitudes_open": not flags.get(
            "all_portal_magnitudes_and_phases_scanned", False
        ),
        "uv_posterior_open": not flags.get(
            "portal_yukawa_posterior_derived", False
        ),
        "component_currents_open": not flags.get(
            "component_specific_uv_chiral_currents_derived", False
        ),
        "continuous_likelihoods_open": not flags.get(
            "continuous_experimental_likelihoods_implemented", False
        ),
        "whole_model_not_excluded": not flags.get(
            "whole_v20_model_excluded", False
        ),
    }
    failures = [name for name, ok in checks.items() if not ok]
    base_failures = list(base.get("failures") or [])
    combined_failures = base_failures + [
        f"full_complex_orientation::{name}" for name in failures
    ]
    base_checks = int(base.get("n_checks", 0))
    base_failed = int(base.get("n_failed", len(base_failures)))
    result = dict(base)
    result["n_checks"] = base_checks + len(checks)
    result["n_failed"] = base_failed + len(failures)
    result["failures"] = combined_failures
    result["status"] = (
        "OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE"
        if result["n_failed"] == 0
        else "OPEN_GAP_AUDIT_FAILED"
    )
    result["full_complex_orientation_sphere"] = {
        "status": sphere.get("status"),
        "sampling_measure": (scan.get("configuration") or {}).get(
            "sampling_measure"
        ),
        "n_total_points": counts.get("n_total_points"),
        "n_NA62_excluded": counts.get("n_NA62_excluded"),
        "n_NA62_surviving": counts.get("n_NA62_surviving"),
        "NA62_excluded_fraction_under_chosen_geometric_measure": counts.get(
            "NA62_excluded_fraction_under_chosen_geometric_measure"
        ),
        "NA62_replicate_fraction_range": [
            diagnostics.get("NA62_min"),
            diagnostics.get("NA62_max"),
        ],
        "NA62_replicate_mean": diagnostics.get("NA62_mean"),
        "NA62_replicate_standard_error": diagnostics.get(
            "NA62_standard_error_of_replicate_mean"
        ),
        "n_TWIST_excluded": counts.get("n_TWIST_excluded"),
        "sampled_min_NA62_ratio": (
            extrema.get("min_NA62_ratio") or {}
        ).get("NA62_ratio"),
        "sampled_max_NA62_ratio": (
            extrema.get("max_NA62_ratio") or {}
        ).get("NA62_ratio"),
        "sampled_max_TWIST_ratio": (
            extrema.get("max_TWIST_ratio") or {}
        ).get("TWIST_ratio"),
        "original_direction": anchors.get("original_direction"),
        "family_axis_anchors": {
            name: anchors.get(name) for name in ("F1", "F2", "F3")
        },
        "equal_component_anchors": {
            name: anchors.get(name) for name in ("equal_real", "equal_120deg")
        },
        "geometric_fraction_is_uv_probability": False,
        "replicate_spread_is_uv_posterior_uncertainty": False,
        "all_portal_magnitudes_and_phases_scanned": False,
        "portal_yukawa_posterior_derived": False,
    }
    gap_status = dict(result.get("gap_status") or {})
    gap_status.update(
        {
            "full_complex_three_family_orientation_geometric_sample": not failures,
            "rotationally_invariant_orientation_measure_explicit": flags.get(
                "rotationally_invariant_orientation_measure_explicit", False
            ),
            "NA62_excluded_and_surviving_complex_orientations": flags.get(
                "NA62_has_excluded_samples", False
            )
            and flags.get("NA62_has_surviving_samples", False),
            "all_sampled_complex_orientations_survive_TWIST": not flags.get(
                "TWIST_has_excluded_samples", True
            ),
            "chosen_geometric_fraction_is_UV_probability": False,
            "joint_orientation_magnitude_portal_scan": False,
            "UV_portal_orientation_posterior": False,
            "component_specific_threshold_currents": False,
            "continuous_FCNC_likelihoods": False,
        }
    )
    result["gap_status"] = gap_status
    result["verdict"] = (
        "The full complex three-family orientation sphere is sampled at fixed "
        "portal norm and ordered-heavy y_Q. Under the explicit rotationally "
        "invariant geometric measure, 16286/16384 orientations exceed NA62, "
        "98 survive, and all samples pass the published TWIST benchmarks. "
        "This geometric fraction is not a UV probability. Joint portal "
        "magnitudes, threshold currents, a UV posterior, precision RG, and "
        "experimental detection remain open."
    )
    result["full_complex_orientation_checks"] = {
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    return result


def write_markdown(report: dict[str, Any]) -> str:
    sphere = report.get("full_complex_orientation_sphere") or {}
    return "\n".join(
        [
            "# Open-gap audit — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Full complex orientation sphere",
            "",
            f"- Samples: {sphere.get('n_total_points')}",
            f"- NA62 excluded: {sphere.get('n_NA62_excluded')}",
            f"- NA62 surviving: {sphere.get('n_NA62_surviving')}",
            f"- Chosen-measure fraction: {sphere.get('NA62_excluded_fraction_under_chosen_geometric_measure')}",
            f"- TWIST excluded: {sphere.get('n_TWIST_excluded')}",
            "- The chosen geometric fraction is not a UV probability or posterior.",
            "",
        ]
    )


def main() -> int:
    base = json.loads(BASE_PATH.read_text(encoding="utf-8"))
    sphere = json.loads(SPHERE_PATH.read_text(encoding="utf-8"))
    report = augment_report(base, sphere)
    BASE_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    MD_PATH.write_text(write_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_checks": report["n_checks"],
                "n_failed": report["n_failed"],
                "full_complex_orientation_sphere": report[
                    "full_complex_orientation_sphere"
                ],
                "full_complex_orientation_checks": report[
                    "full_complex_orientation_checks"
                ],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
