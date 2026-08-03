#!/usr/bin/env python3
"""Consolidated fail-closed portal/flavour reanalysis verdict."""

from __future__ import annotations

import json
from pathlib import Path

import audit_v20_errors as audit
import full_fermion_matching_v20 as matching


ROOT = Path(__file__).resolve().parent


def _load(name: str) -> dict:
    return json.loads(ROOT.joinpath(name).read_text(encoding="utf-8"))


def build_report() -> dict:
    ferm = matching.build_report()
    profile = _load("TAN_BETA_PROFILE_V20_VERDICT.json")
    flavour = _load("flavour_clebsch_fit_v20.json")
    extensive = _load("EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json")
    independent = audit.build_audit()

    checks = {
        "independent_error_audit_pass": independent["status"] == "PASS",
        "extensive_campaign_pass": extensive["status"] == "PASS",
        "moving_frame_identity_verified": ferm["checks"][
            "moving_frame_identity_verified"
        ],
        "physical_portal_dependence_detected": ferm["checks"][
            "physical_portal_dependence_detected"
        ],
        "possible_FCNC_detected": ferm["checks"]["possible_FCNC_detected"],
        "complete_C_portal_included": ferm["checks"]["allowed_C_portal_included"],
        "full_model_coefficients_not_overclaimed": not ferm[
            "full_model_status"
        ]["unique_symbolic_full_model_Ce_Cp_Cn"],
        "corrected_Takagi_PMNS_used": flavour["fit_validity"][
            "Takagi_Majorana_diagonalization"
        ]
        and flavour["fit_validity"]["charged_lepton_basis_in_PMNS"],
        "corrected_single_scale_profile_not_viable": not profile[
            "any_profile_point_viable_chi2_lt_30"
        ],
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "IN_REPO_REANALYSIS_PASS__FIELD_THEORY_CANDIDATE__"
            "FERMION_AND_SINGLE_SCALE_FLAVOUR_OPEN"
            if not failures
            else "REANALYSIS_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "corrected_conclusions": {
            "moving_frame_identity": "Q_proj + Berry = I (basis dependent)",
            "physical_regular_current": "Q_proj = I - 4W (portal dependent)",
            "tree_FCNC_absence_proved": False,
            "aligned_Cf_benchmark_reproducible": True,
            "unique_full_model_Ce_Cp_Cn": False,
            "corrected_vR_equals_vS_flavour_viable": False,
            "photon_37GHz_benchmark_experimentally_open": True,
        },
        "portal_matching": ferm["portal_current_result"],
        "aligned_examples_not_full_predictions": ferm[
            "aligned_numerical_examples_not_full_predictions"
        ],
        "flavour_status": {
            "corrected_multistart": flavour["v20_single_scale_point"],
            "corrected_profile": profile,
            "fit_validity": flavour["fit_validity"],
        },
        "approval_scope": (
            "The repository passes internal anomaly/operator/release gates as a "
            "candidate field-theory construction. It is not approved as a "
            "complete phenomenological model: exact fermion matching and the "
            "v_R=v_S flavour benchmark remain unresolved/failing."
        ),
        "remaining_high_value_work": [
            "UV-fix unique portal Yukawas for exact unique C_e,C_p,C_n",
            "proof of tree-level FCNC absence (ledger shows possible FCNCs)",
            "full common-scale Yukawa RG global 10+126(+210) fit",
            "real laboratory/astrophysical 37 GHz conversion detection",
        ],
    }


def write_markdown(report: dict) -> str:
    lines = [
        "# v20 portal-current and flavour reanalysis",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Corrected verdict",
        "",
        report["approval_scope"],
        "",
        "- Moving-frame identity: **verified but not physical proof**",
        "- Physical portal dependence: **detected**",
        "- Tree FCNC absence: **not proved**",
        "- Exact full `C_e,C_p,C_n`: **open**",
        "- Corrected `v_R=v_S` constrained flavour fit: **not viable**",
        "- 37 GHz photon target: **experimentally open**",
        "",
        "## Validation",
        "",
    ]
    for name, passed in report["checks"].items():
        lines.append(f"- `{name}`: {passed}")
    lines += [
        "",
        "## Remaining work",
        "",
        *[f"- {item}" for item in report["remaining_high_value_work"]],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    ROOT.joinpath("V20_PORTAL_BETA_REANALYSIS_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("V20_PORTAL_BETA_REANALYSIS.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "n_failed": report["n_failed"],
                "unique_full_model_Ce_Cp_Cn": False,
                "vR_equals_vS_flavour_viable": False,
                "approval_scope": report["approval_scope"],
            },
            indent=2,
        )
    )
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
