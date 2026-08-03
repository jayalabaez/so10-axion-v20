#!/usr/bin/env python3
"""Apply TWIST massless two-body muon limits to v20 mu -> e a rates.

TWIST reported 90% CL branching-ratio upper limits for a massless invisible
boson under three angular-asymmetry hypotheses, A=-1, 0, +1.  The v20 axion is
153.5 micro-eV, effectively massless for the muon endpoint.  This module checks
both repository portal scenarios against all three published benchmark limits.

It deliberately does not interpolate an arbitrary-A likelihood or infer the
TWIST asymmetry from the current matrices. Passing all three published cases is
stronger than selecting whichever benchmark is most convenient, but it remains
a benchmark-table comparison rather than a full angular likelihood.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import channel_fcnc_rates_v20 as rates


ROOT = Path(__file__).resolve().parent
ANCHOR_PATH = ROOT / "data" / "twist_massless_endpoint_limits_v20.json"
EXPECTED_PAYLOAD_SHA256 = (
    "7e9719b0254180164a15e33aa79871b0e3730973fd44b58935675cf72909c826"
)


def _canonical_payload_hash(payload: dict[str, Any]) -> str:
    value = dict(payload)
    value.pop("canonical_payload_sha256", None)
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_limits(path: Path = ANCHOR_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("TWIST limit anchor must be a JSON object")
    recorded = str(payload.get("canonical_payload_sha256", ""))
    computed = _canonical_payload_hash(payload)
    if recorded != computed or computed != EXPECTED_PAYLOAD_SHA256:
        raise ValueError("TWIST benchmark-limit provenance hash mismatch")
    source = payload.get("source") or {}
    if source.get("doi") != "10.1103/PhysRevD.91.052020":
        raise ValueError("unexpected TWIST publication DOI")
    rows = payload.get("limits")
    if not isinstance(rows, list) or len(rows) != 3:
        raise ValueError("TWIST anchor must contain exactly three benchmark rows")
    asymmetries = sorted(float(row["asymmetry_A"]) for row in rows)
    if asymmetries != [-1.0, 0.0, 1.0]:
        raise ValueError("TWIST anchor must contain A=-1,0,+1")
    for row in rows:
        limit = float(row["branching_ratio_upper_limit_90cl"])
        ppm = float(row["published_ppm"])
        if not math.isclose(limit, ppm * 1.0e-6, rel_tol=1.0e-12):
            raise ValueError("TWIST ppm and branching-ratio columns disagree")
    return payload


def compare_scenario(
    scenario: dict[str, Any],
    limits: dict[str, Any],
) -> dict[str, Any]:
    predicted = float(scenario["mu_to_e_a"]["branching_ratio"])
    rows = []
    for source_row in sorted(limits["limits"], key=lambda row: row["asymmetry_A"]):
        limit = float(source_row["branching_ratio_upper_limit_90cl"])
        ratio = predicted / limit
        rows.append(
            {
                "asymmetry_A": float(source_row["asymmetry_A"]),
                "observed_br_upper_limit_90cl": limit,
                "published_ppm": float(source_row["published_ppm"]),
                "prediction_over_limit": ratio,
                "survives_benchmark_limit": predicted <= limit,
                "safety_factor_limit_over_prediction": (
                    limit / predicted if predicted > 0.0 else math.inf
                ),
            }
        )
    strongest = min(rows, key=lambda row: row["observed_br_upper_limit_90cl"])
    return {
        "predicted_branching_ratio": predicted,
        "benchmark_results": rows,
        "survives_all_three_published_hypotheses": all(
            row["survives_benchmark_limit"] for row in rows
        ),
        "strongest_published_benchmark": strongest,
    }


def build_report() -> dict[str, Any]:
    limits = load_limits()
    channel = rates.build_report()
    hierarchical = compare_scenario(channel["hierarchical_benchmark"], limits)
    counterexample = compare_scenario(
        channel["generation_dependent_counterexample"], limits
    )
    strongest = counterexample["strongest_published_benchmark"]

    checks = {
        "provenance_hash_verified": (
            _canonical_payload_hash(limits) == EXPECTED_PAYLOAD_SHA256
        ),
        "v20_axion_is_endpoint_massless": rates.MA_V20_GEV / rates.M_MU_GEV < 1e-9,
        "hierarchical_survives_all_three": hierarchical[
            "survives_all_three_published_hypotheses"
        ],
        "generation_dependent_survives_all_three": counterexample[
            "survives_all_three_published_hypotheses"
        ],
        "strongest_case_is_A_plus_one": strongest["asymmetry_A"] == 1.0,
        "arbitrary_A_likelihood_not_claimed": True,
        "whole_model_exclusion_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "TWIST_MASSLESS_BENCHMARK_LIMITS_APPLIED__BOTH_SCENARIOS_SURVIVE"
            if not failures
            else "TWIST_MASSLESS_LIMIT_APPLICATION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "source": {
            **limits["source"],
            "canonical_payload_sha256": EXPECTED_PAYLOAD_SHA256,
            "scope": limits["scope"],
        },
        "target": {
            "axion_mass_GeV": rates.MA_V20_GEV,
            "mass_over_muon_mass": rates.MA_V20_GEV / rates.M_MU_GEV,
            "endpoint_massless_approximation": True,
        },
        "hierarchical_universal_benchmark": hierarchical,
        "generation_dependent_counterexample": counterexample,
        "flag": {
            "three_published_asymmetry_limits_ingested": True,
            "offline_provenance_hash_verified": True,
            "hierarchical_survives_all_three_TWIST_benchmarks": hierarchical[
                "survives_all_three_published_hypotheses"
            ],
            "generation_dependent_survives_all_three_TWIST_benchmarks": counterexample[
                "survives_all_three_published_hypotheses"
            ],
            "continuous_arbitrary_A_likelihood_implemented": False,
            "TWIST_asymmetry_predicted_from_uv_currents": False,
            "full_muon_channel_likelihood_implemented": False,
            "whole_v20_model_excluded": False,
        },
        "interpretation": (
            "The hierarchical benchmark is negligible. The generation-dependent "
            f"portal point predicts BR(mu->ea)={counterexample['predicted_branching_ratio']:.6e} "
            f"and remains below the strongest published TWIST massless benchmark "
            f"limit {strongest['observed_br_upper_limit_90cl']:.6e} by a safety "
            f"factor {strongest['safety_factor_limit_over_prediction']:.3f}. "
            "It therefore survives the three published A=-1,0,+1 hypotheses. "
            "No arbitrary-A or full angular-likelihood statement is made."
        ),
        "remaining_for_full_muon_likelihood": [
            "derive the TWIST asymmetry A from the component-specific chiral currents",
            "obtain or reconstruct the continuous mass/asymmetry likelihood",
            "propagate the complete portal-Yukawa posterior",
        ],
    }


def write_markdown(report: dict[str, Any]) -> str:
    h = report["hierarchical_universal_benchmark"]
    c = report["generation_dependent_counterexample"]
    lines = [
        "# TWIST massless muon limits — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- Hierarchical BR(mu -> e a): {h['predicted_branching_ratio']:.6e}",
        f"- Hierarchical survives A=-1,0,+1: **{h['survives_all_three_published_hypotheses']}**",
        f"- Generation-dependent BR(mu -> e a): {c['predicted_branching_ratio']:.6e}",
        f"- Generation-dependent survives A=-1,0,+1: **{c['survives_all_three_published_hypotheses']}**",
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("TWIST_MASSLESS_LIMIT_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("TWIST_MASSLESS_LIMIT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
