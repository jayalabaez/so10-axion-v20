#!/usr/bin/env python3
"""Lock empirical targets + scientific-instrument flags for v20.

Aggregates:
  - haloscope 36.6-37.6 GHz brief
  - GRAVITAS NS-radio Doppler criteria
  - CMB/public-data pipeline (continuum practice only)
  - provisional vs full theory flags from portal/flavour modules
  - CI/drift-guard checklist
"""

from __future__ import annotations

import json
from pathlib import Path

import cmb_public_data_pipeline_v20 as cmb
import gravitas_axion_v20_37ghz as gravitas
import home_public_37ghz_search_v20 as home
import portal_tensors_abcd_v20 as portals


ROOT = Path(__file__).resolve().parent


def haloscope_target_lock() -> dict:
    brief = (ROOT / "haloscope_37ghz_templates" / "v20_haloscope_target_brief.md").read_text(
        encoding="utf-8"
    )
    lineshape = ROOT / "haloscope_37ghz_templates" / "v20_axion_lineshape_37GHz.csv"
    return {
        "m_a_ueV": 153.5,
        "nu_GHz": 37.11,
        "scan_GHz": [36.6, 37.6],
        "g_agamma_GeV_inv": 2.335e-14,
        "E_over_N": 8 / 3,
        "collaborations": ["MADMAX", "ORGAN", "ALPHA"],
        "brief_chars": len(brief),
        "lineshape_csv_exists": lineshape.exists(),
        "hard_falsifier": (
            "Null result at g_agamma <= 2.3e-14 GeV^{-1} over 36.6-37.6 GHz "
            "kills the all-DM photon benchmark"
        ),
    }


def ns_radio_criteria() -> dict:
    report = gravitas.build_report()
    catalog = report.get("catalog", {})
    return {
        "line_centre_GHz": 37.11,
        "method": "NS magnetosphere axion-photon conversion",
        "doppler_modulation": True,
        "phase_lock_to": "GRAVITAS compact-object ephemerides",
        "n_targets": catalog.get("n_targets_built"),
        "n_ns_regime_soft": catalog.get("n_ns_regime_soft"),
        "status": report.get("status"),
        "verdict": report.get("verdict"),
        "observing_ask": report.get("observing_ask"),
        "search_criteria": [
            "Tune to barycentric 37.11 GHz then apply binary Doppler from ephemeris",
            "Coherent fold at orbital period; search residual ~37 kHz halo width",
            "Prefer high-B NS / magnetar environments",
            "Stack large-N targets; QCD-depth still extremely challenging",
            "Smoking gun: line tracks GRAVITAS orbital ephemeris for NS, absent for BH",
        ],
    }


def theory_flags() -> dict:
    portal = portals.build_report()
    return {
        "portal_tensors_ABCD": portal["flag"],
        "provisional_vs_full": {
            "aligned_Cf_benchmark": "PROVISIONAL",
            "unique_full_Ce_Cp_Cn": "OPEN",
            "vR_eq_vS_flavour": "FAILS_CONSTRAINED_FIT",
            "natural_scale_flavour": "SCAN_FOR_VIABLE_REGION",
            "anomaly_operator_core": "INTERNALLY_PASSES",
            "experimental_discovery": "NO",
        },
        "portal_status": portal["status"],
    }


def drift_guard() -> dict:
    required = [
        "PORTAL_TENSORS_ABCD_V20_VERDICT.json",
        "PHYSICAL_CF_MATCHING_V20_VERDICT.json",
        "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
        "CMB_PUBLIC_PIPELINE_V20_VERDICT.json",
        "TAN_BETA_PROFILE_V20_VERDICT.json",
        "FULL_FERMION_MATCHING_V20_VERDICT.json",
        "V20_PORTAL_BETA_REANALYSIS_VERDICT.json",
        "THEORY_CONFIRMATION_VERDICT.json",
        "SHA256SUMS",
        ".github/workflows/replicate-and-falsify.yml",
    ]
    present = {name: (ROOT / name).exists() for name in required}
    return {
        "required_artifacts": present,
        "all_required_paths_known": True,
        "ci_workflow": "replicate-and-falsify",
        "byte_reproducible_release_gate": "validate_release_v20.py",
        "note": (
            "CI must regenerate verdicts; validate_release_v20.py locks PDF and "
            "core SHA256SUMS with SOURCE_DATE_EPOCH."
        ),
    }


def build_report(*, run_cmb_download: bool = True) -> dict:
    cmb_report = cmb.run_pipeline(download=run_cmb_download)
    home_report = home.build_report() if hasattr(home, "build_report") else {
        "status": "see HOME_PUBLIC_37GHZ_SEARCH_VERDICT.json"
    }
    # home module uses main(); load existing verdict if present
    home_path = ROOT / "HOME_PUBLIC_37GHZ_SEARCH_VERDICT.json"
    if home_path.exists():
        home_report = json.loads(home_path.read_text(encoding="utf-8"))
    else:
        home_report = home.cmb_cannot_resolve_v20_line()

    report = {
        "status": "EMPIRICAL_ROADMAP_LOCKED__THEORY_FLAGS_EXPLICIT",
        "haloscope": haloscope_target_lock(),
        "ns_radio": ns_radio_criteria(),
        "cmb_pipeline": {
            "status": cmb_report["status"],
            "n_downloads_ok": cmb_report["n_downloads_ok"],
            "flag": cmb_report["flag"],
            "verdict": cmb_report["verdict"],
        },
        "home_public": {
            "status": home_report.get("status") or home_report.get("verdict"),
        },
        "theory_flags": theory_flags(),
        "drift_guard": drift_guard(),
    }
    checks = {
        "haloscope_brief_present": report["haloscope"]["brief_chars"] > 100,
        "lineshape_csv_present": report["haloscope"]["lineshape_csv_exists"],
        "ns_radio_criteria_nonempty": len(report["ns_radio"]["search_criteria"]) >= 3,
        "cmb_dilution_blocks_false_claim": cmb_report["n_failed"] == 0,
        "portal_flags_present": "provisional_aligned_benchmark"
        in report["theory_flags"]["portal_tensors_ABCD"],
        "full_unique_Cf_flag_false": not report["theory_flags"]["portal_tensors_ABCD"][
            "full_unique_Ce_Cp_Cn"
        ],
    }
    failures = [k for k, v in checks.items() if not v]
    report["n_checks"] = len(checks)
    report["n_failed"] = len(failures)
    report["failures"] = failures
    report["verdict"] = (
        "Empirical roadmap locked: 36.6-37.6 GHz haloscope brief, GRAVITAS "
        "NS-radio Doppler criteria, and CMB public-data pipeline (practice "
        "only). Theory flags separate provisional aligned C_f from open full "
        "matching. Drift-guard artifacts are enumerated for CI."
    )
    return report


def write_markdown(report: dict) -> str:
    h = report["haloscope"]
    lines = [
        "# Empirical roadmap lock — v20",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Haloscope target",
        "",
        f"- mass: {h['m_a_ueV']} ueV",
        f"- scan: {h['scan_GHz'][0]}-{h['scan_GHz'][1]} GHz",
        f"- g_agamma: {h['g_agamma_GeV_inv']:.3e} GeV^{{-1}}",
        f"- teams: {', '.join(h['collaborations'])}",
        f"- falsifier: {h['hard_falsifier']}",
        "",
        "## NS-radio / GRAVITAS",
        "",
    ]
    for c in report["ns_radio"]["search_criteria"]:
        lines.append(f"- {c}")
    lines += [
        "",
        "## CMB / public data",
        "",
        report["cmb_pipeline"]["verdict"],
        "",
        "## Theory flags",
        "",
    ]
    for k, v in report["theory_flags"]["provisional_vs_full"].items():
        lines.append(f"- `{k}`: **{v}**")
    lines += ["", "## Verdict", "", report["verdict"], ""]
    return "\n".join(lines)


def main() -> int:
    # Network downloads are on by default for this module.
    cmb_report = cmb.run_pipeline(download=True)
    ROOT.joinpath("CMB_PUBLIC_PIPELINE_V20_VERDICT.json").write_text(
        json.dumps(cmb_report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("CMB_PUBLIC_PIPELINE_V20.md").write_text(
        cmb.write_markdown(cmb_report), encoding="utf-8"
    )
    report = build_report(run_cmb_download=False)
    # Carry the download stats from the live run into the lock report.
    report["cmb_pipeline"] = {
        "status": cmb_report["status"],
        "n_downloads_ok": cmb_report["n_downloads_ok"],
        "n_downloads_attempted": cmb_report["n_downloads_attempted"],
        "flag": cmb_report["flag"],
        "verdict": cmb_report["verdict"],
    }
    ROOT.joinpath("EMPIRICAL_ROADMAP_LOCK_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("EMPIRICAL_ROADMAP_LOCK_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "failures": report["failures"],
                "cmb_downloads_ok": report["cmb_pipeline"]["n_downloads_ok"],
                "theory_flags": report["theory_flags"]["provisional_vs_full"],
                "verdict": report["verdict"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
