#!/usr/bin/env python3
"""Audit the claimed intermediate-scale H10 vacuum used by legacy locking code.

Under the Pati-Salam subgroup,

    10_H -> (6,1,1) + (1,2,2).

Neither summand is a Pati-Salam or Standard-Model singlet. Therefore an
``H10_eff = M_I`` background cannot be interpreted as a physical vacuum
expectation value without breaking colour or electroweak symmetry at M_I.

This audit does not remove the exact 10x10->54 or 126x126->54 projectors.
It withdraws only physical scalar-mass and phase-locking conclusions that
inserted an intermediate-scale H10 VEV proxy into those projectors.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import component_lift_210_126_10_v20 as component_lift
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "H10_INTERMEDIATE_VEV_CONSISTENCY_AUDIT_V20.json"
OUT_MD = ROOT / "H10_INTERMEDIATE_VEV_CONSISTENCY_AUDIT_V20.md"

PATI_SALAM_BRANCHING = {
    "representation": "10_H",
    "decomposition": ["(6,1,1)", "(1,2,2)"],
    "dimensions": [6, 4],
    "contains_PS_singlet": False,
    "contains_SM_singlet": False,
    "physical_interpretation": {
        "(6,1,1)": "colour sector; a VEV breaks colour",
        "(1,2,2)": "electroweak bidoublet; a VEV breaks SU(2)L x U(1)Y",
    },
}


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    ledger = component_lift.component_ledger(anchor)
    by_name = {row["name"]: row for row in ledger["components"]}
    h_proxy = by_name["H10_eff"]
    h_ew = by_name["h_EW"]
    m_i = float(anchor["M_I_GeV"])

    proxy_at_mi = abs(float(h_proxy["vev_GeV"]) - m_i) <= 1e-12 * max(m_i, 1.0)
    ew_is_174 = abs(float(h_ew["vev_GeV"]) - 174.0) < 1e-12

    checks = {
        "pati_salam_dimensions_sum_to_10": sum(PATI_SALAM_BRANCHING["dimensions"]) == 10,
        "10H_contains_no_PS_singlet": not PATI_SALAM_BRANCHING["contains_PS_singlet"],
        "10H_contains_no_SM_singlet": not PATI_SALAM_BRANCHING["contains_SM_singlet"],
        "legacy_ledger_contains_H10_eff_MI_proxy": proxy_at_mi,
        "physical_EW_vev_is_174_GeV": ew_is_174,
        "proxy_not_promoted_to_physical_vacuum": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "H10_MI_PROXY_IDENTIFIED__LOCKING_MASS_CLAIMS_WITHDRAWN"
            if not failures
            else "H10_MI_PROXY_AUDIT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "pati_salam_branching": PATI_SALAM_BRANCHING,
        "ledger_observation": {
            "H10_eff_name": h_proxy["name"],
            "H10_eff_declared_ps": h_proxy["ps"],
            "H10_eff_declared_role": h_proxy["role"],
            "H10_eff_vev_GeV": float(h_proxy["vev_GeV"]),
            "M_I_GeV": m_i,
            "h_EW_vev_GeV": float(h_ew["vev_GeV"]),
            "classification": "bookkeeping proxy only; not an allowed physical PS/SM-singlet VEV",
        },
        "affected_results": {
            "extended_ttbar_54_locking_A54_with_v10eff_eq_MI": "WITHDRAWN_AS_PHYSICAL",
            "component_lift_H10_eff_radial_vacuum": "PROXY_ONLY",
            "diagonal_isotropic_54_locking_mass_seed": "WITHDRAWN",
            "exact_10_to_54_projector": "RETAINED",
            "exact_126_to_54_projector": "RETAINED",
            "phase_locking_operator_existence": "ALLOWED_BUT_PHYSICAL_VEV_EVALUATION_OPEN",
        },
        "required_replacement": {
            "physical_background": "use actual H10 electroweak doublet VEV hEW=174 GeV",
            "calculation": (
                "differentiate the charge-allowed locking invariant in the exact "
                "H10 and Sigmabar component basis; do not divide an MI-proxy phase "
                "amplitude by MI^2 to manufacture an isotropic positive mass"
            ),
            "remaining_status": "OPEN",
        },
        "flags": {
            "physical_H10_intermediate_scale_singlet_vev_exists": False,
            "H10_eff_MI_is_bookkeeping_proxy_only": True,
            "legacy_A54_v10eff_MI_physical": False,
            "legacy_isotropic_54_mass_seed_physical": False,
            "exact_54_projectors_retained": True,
            "exact_54_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "10_H has no Pati-Salam or Standard-Model singlet. The repository's "
            "H10_eff=M_I entry is a bookkeeping proxy, not a physical vacuum. "
            "Any 54-locking scalar mass or phase amplitude that used v10=M_I is "
            "withdrawn. Exact group-theory projectors remain valid, and the "
            "physical hEW=174 GeV component Hessian remains to be derived."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# H10 intermediate-VEV consistency audit — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
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
