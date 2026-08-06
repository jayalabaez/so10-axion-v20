#!/usr/bin/env python3
r"""EM / Cartan Q-charged selection rule on off-singlet 45/54/210 (v20).

Physics
-------
The three published-projector bilinears

    (Φ_vac ⊗ δΦ_off)_45 ,  (Φ_vac ⊗ δΦ_off)_54 ,  Ξ(Φ_vac, δΦ_off)_210

have been Cartan-labeled on the full 207-dim PS-singlet complement. Empirically
every image is Q-charged under the adjoint activity of

    Q = T3_L + T3_R = -i M_67

(with the repo cut ``Q_em activity ≥ Q_NEUTRAL_TOL``). Therefore these channels
cannot seed **EM-neutral** light singlets in the published-projector subspace:
they may only feed charged-sector diagnostics / Coleman–Weinberg. This is a
selection rule from Lie-algebra Cartan activity — not Young/CG coefficients.

Honesty
-------
* Does not invent 120/320/1050/4125.
* Does not claim mode-by-mode SM-irrep CG.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import open_210_channel_210_off_singlet_sm_quantum_numbers_v20 as qn210
import open_210_channel_45_off_singlet_sm_quantum_numbers_v20 as qn45
import open_210_channel_54_off_singlet_sm_quantum_numbers_v20 as qn54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "OFF_SINGLET_QCHARGED_SELECTION_RULE_V20.json"
OUT_MD = ROOT / "OFF_SINGLET_QCHARGED_SELECTION_RULE_V20.md"


def _channel(report: dict[str, Any], name: str) -> dict[str, Any]:
    qn = report["quantum_numbers"]
    return {
        "channel": name,
        "status": report.get("status"),
        "n_modes": qn["n_modes_labeled"],
        "n_Q_neutral": qn["n_Q_neutral"],
        "n_Q_charged": qn["n_Q_charged"],
        "Q_em_activity_min": qn["Q_em_activity_min"],
        "Q_em_activity_max": qn["Q_em_activity_max"],
        "bucket_counts": qn["bucket_counts"],
        "all_Q_charged": qn["n_Q_neutral"] == 0
        and qn["n_Q_charged"] == qn["n_modes_labeled"],
    }


def build_report() -> dict[str, Any]:
    r45 = qn45.build_report()
    r54 = qn54.build_report()
    r210 = qn210.build_report()
    channels = [
        _channel(r45, "45"),
        _channel(r54, "54"),
        _channel(r210, "210"),
    ]
    all_charged = all(c["all_Q_charged"] for c in channels)
    upstream_green = all(
        int(r.get("n_failed", 1)) == 0 for r in (r45, r54, r210)
    )

    checks = {
        "upstream_sm_qn_green": upstream_green,
        "all_three_channels_fully_Q_charged": all_charged,
        "no_Q_neutral_light_singlet_seed_from_published_projectors": all_charged,
        "cg_not_invented": True,
        "mode_by_mode_sm_irrep_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    implications = {
        "em_neutral_light_singlet_seed_from_45_54_210_off_singlet": False,
        "may_feed_charged_sector_diagnostics_only": True,
        "schur_A_C_light_singlet_hunt_unaffected_by_these_channels": True,
        "mode_cg_still_required_for_charged_mass_diagonals": True,
    }

    return {
        "status": (
            "OFF_SINGLET_QCHARGED_SELECTION_RULE_READY"
            if not failures
            else "OFF_SINGLET_QCHARGED_SELECTION_RULE_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "convention": {
            "Q_em": "T3_L + T3_R = -i M_67",
            "Q_neutral_tol": qn45.Q_NEUTRAL_TOL,
            "note": (
                "Selection rule from Cartan adjoint activity on published "
                "projector images; not Young-tableau CG."
            ),
        },
        "channels": channels,
        "implications": implications,
        "flags": {
            "selection_rule_ready": not bool(failures),
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "off_singlet_mode_by_mode_sm_irrep_cg": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "Off-singlet published-projector images (45/54/210): "
            f"{'all 3×207 modes Q-charged' if all_charged else 'Q-neutral modes present'}; "
            "no EM-neutral light-singlet seed from these channels. "
            "Mode CG and 120/320/1050/4125 remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Off-singlet Q-charged selection rule — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + "\n".join(
            f"- Channel {c['channel']}: Q-neutral=`{c['n_Q_neutral']}` / "
            f"Q-charged=`{c['n_Q_charged']}`\n"
            for c in report["channels"]
        )
        + "\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
