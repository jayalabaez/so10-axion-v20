#!/usr/bin/env python3
r"""Compare the v20 37 GHz benchmark to published / design experimental limits.

This is direct experimental *verification bookkeeping*, not a detection.
It places the all-DM photon benchmark

    m_a ≃ 153.5 µeV ,  ν ≃ 37.11 GHz ,  g_aγγ ≃ 2.335×10^{-14} GeV^{-1}

against literature and design-reach entries already curated in
``literature_sweep_150uev_v20`` plus the repository forecast package.

Discovery remains false until real 36.6–37.6 GHz conversion data are ingested.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import haloscope_scan_37ghz_v20 as halo
import literature_sweep_150uev_v20 as lit


ROOT = Path(__file__).resolve().parent


def build_report() -> dict[str, Any]:
    window = halo.benchmark_window()
    forecast = halo.scan_forecast()
    literature = lit.build_report()
    entries = literature.get("entries") or lit.literature_entries()
    classification = literature.get("classification") or lit.classify(entries)
    covering = [e for e in entries if e.get("covers_v20_mass")]
    excluding = [e for e in entries if e.get("excludes_v20_coupling")]
    open_at_v20 = [
        e for e in entries if str(e.get("status_at_v20", "")).startswith("OPEN")
    ]
    checks = {
        "benchmark_window_defined": window["recommended_scan_GHz"] == [36.6, 37.6],
        "literature_does_not_exclude_all_dm_benchmark": len(excluding) == 0,
        "forecast_is_not_detection": True,
        "discovery_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "HALOSCOPE_37GHZ_LIMIT_COMPARISON_COMPLETE__NO_DETECTION"
            if not failures
            else "HALOSCOPE_37GHZ_COMPARISON_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "benchmark": window,
        "forecast_summary": {
            "n_channels": forecast.get("n_channels"),
            "total_integration_days": forecast.get("total_integration_days"),
            "expected_SNR": forecast.get("expected_SNR"),
            "reaches_v20_coupling_in_forecast": forecast.get(
                "reaches_v20_coupling"
            ),
            "note": "Dicke radiometer forecast only; not experimental data.",
        },
        "literature_comparison": {
            "n_entries": len(entries),
            "n_covering_mass": len(covering),
            "n_excluding_v20_coupling": len(excluding),
            "n_open_at_v20": len(open_at_v20),
            "theory_fails_from_published_bounds": bool(
                classification.get("theory_fails_from_published_bounds", False)
            ),
            "hard_falsifier": (
                "A published null reaching g_aγγ ≤ 2.3e-14 GeV^{-1} over "
                "36.6–37.6 GHz under the all-local-DM assumption kills the "
                "photon benchmark."
            ),
        },
        "flag": {
            "lab_limit_comparison_executed": True,
            "real_37GHz_detection": False,
            "experimental_discovery": False,
            "all_dm_photon_benchmark_currently_open": len(excluding) == 0,
        },
        "verdict": (
            "The 37 GHz all-DM benchmark remains experimentally open against "
            "the curated published/design ledger. Repository forecasts and "
            "templates are ready for collaboration use; no real conversion "
            "detection is claimed."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    b = report["benchmark"]
    litc = report["literature_comparison"]
    return "\n".join([
        "# 37 GHz experimental limit comparison — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- ν: {b['nu_central_GHz']:.4g} GHz",
        f"- scan: {b['recommended_scan_GHz']} GHz",
        f"- g_aγγ: {b['g_agamma_GeV_inv']:.4g} GeV⁻¹",
        f"- published exclusions of v20 coupling: {litc['n_excluding_v20_coupling']}",
        f"- detection claimed: **False**",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
    ])


def main() -> int:
    report = build_report()
    ROOT.joinpath("HALOSCOPE_37GHZ_LIMIT_COMPARE_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("HALOSCOPE_37GHZ_LIMIT_COMPARE_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "n_failed": report["n_failed"],
        "flag": report["flag"],
        "literature_comparison": report["literature_comparison"],
        "verdict": report["verdict"],
    }, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
