#!/usr/bin/env python3
"""Close the remaining renormalizable H10--126bar holomorphic families.

Under the live SO(10) x Z17/PQ contract (continuous X is not imposed), three
previously omitted Hermitian operator classes are allowed through dimension 4:

  O54 = [Hdag Hdag]_54 : [Sigmabar Sigmabar]_54 + h.c.
  O+  = Phi Hdag Sigmabar Phi17 + h.c.
  O-  = Phi Hdag Sigmabar Phi17dag + h.c.

The first class is unique because Sym^2(10)=1+54 and
Sym^2(126bar)=54+1050bar+2772bar+4125 share only one 54.  The charge-dressed
quartics inherit the unique 210 contraction already proved for the cubic
Phi Hdag Sigmabar.

On the canonical Delta_R background, P54(Delta_R,Delta_R)=0, so O54 gives no
H10 holomorphic mass block there.  If Phi17 has a VEV, O+ and O- combine with
the cubic coefficient into mu_D_eff = mu_D + eta_plus phi17
+ eta_minus phi17*, while introducing no H--Phi17 block because the
p+Delta_R H tadpole contraction vanishes.

This closes these finite G1 families only.  The full mixed invariant ring,
full component potential, electroweak backreaction, and whole-model validation
remain open.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phi_hdag_sigmabar_cubic_audit_v20 as cubic_audit
import nonsusy_z17_pq_potential_filter_v20 as operator_filter
import physical_h10_54_mass_block_from_deltar_v20 as deltar54
import so10_126_to_54_projector_v20 as sigma54

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_HSIGMA_HOLOMORPHIC_CHARGE_DRESSED_COMPLETION_V20.json"
OUT_MD = ROOT / "EXACT_HSIGMA_HOLOMORPHIC_CHARGE_DRESSED_COMPLETION_V20.md"

O54 = "10_H_dag^2 126bar_H^2 :: 54"
OPLUS = "210_H 10_H_dag 126bar_H Phi17"
OMINUS = "210_H 10_H_dag 126bar_H Phi17_dag"

ADDITIONS = (
    {
        "name": O54,
        "counts": {"10_H_dag": 2, "126bar_H": 2},
        "dim": 4,
        "multiplicity": 1,
        "coefficient": "complex dimensionless kappa_54",
        "so10": "unique common 54 in Sym^2(10) and Sym^2(126bar)",
    },
    {
        "name": OPLUS,
        "counts": {
            "210_H": 1,
            "10_H_dag": 1,
            "126bar_H": 1,
            "Phi17": 1,
        },
        "dim": 4,
        "multiplicity": 1,
        "coefficient": "complex dimensionless eta_plus",
        "so10": "same unique 210 contraction as Phi Hdag Sigmabar cubic",
    },
    {
        "name": OMINUS,
        "counts": {
            "210_H": 1,
            "10_H_dag": 1,
            "126bar_H": 1,
            "Phi17_dag": 1,
        },
        "dim": 4,
        "multiplicity": 1,
        "coefficient": "complex dimensionless eta_minus",
        "so10": "same unique 210 contraction as Phi Hdag Sigmabar cubic",
    },
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


def form_to_combo_vector(form: direct.Form) -> np.ndarray:
    combos, index = sigma54._combo_tables()
    vector = np.zeros(len(combos), dtype=complex)
    for indices, coefficient in form.items():
        vector[index[indices]] = coefficient
    return vector


def sigma_pair_54(left: direct.Form, right: direct.Form) -> np.ndarray:
    left_v = form_to_combo_vector(left)
    right_v = form_to_combo_vector(right)
    raw = np.einsum(
        "abIJ,I,J->ab",
        sigma54.contraction_kernel(),
        left_v,
        right_v,
        optimize=True,
    )
    return sigma54.apply_p54(raw)


def hdag_pair_54(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left_c = np.conjugate(np.asarray(left, dtype=complex))
    right_c = np.conjugate(np.asarray(right, dtype=complex))
    return sigma54.apply_p54(np.outer(left_c, right_c))


def holomorphic_54_invariant(sigma: direct.Form, h: np.ndarray) -> complex:
    return complex(np.sum(hdag_pair_54(h, h) * sigma_pair_54(sigma, sigma)))


def charge_audit() -> dict[str, Any]:
    rows = {}
    for addition in ADDITIONS:
        totals = operator_filter._total_charge(addition["counts"])
        rows[addition["name"]] = {
            **addition,
            "charge_totals": totals,
            "declared_allowed": operator_filter._allowed(
                totals, require_x=False
            ),
            "historical_X_comparison": operator_filter._allowed(
                totals, require_x=True
            ),
        }
    return rows


def representation_audit() -> dict[str, Any]:
    sym10 = {"1": 1, "54": 1}
    sym126bar = {"54": 1, "1050bar": 1, "2772bar": 1, "4125": 1}
    common = {
        name: min(sym10[name], sym126bar[name])
        for name in sym10
        if name in sym126bar
    }
    cubic = cubic_audit.representation_audit()
    return {
        "Sym2_10": sym10,
        "Sym2_126bar": sym126bar,
        "common_channels": common,
        "holomorphic_quartic_channel_count": sum(common.values()),
        "charge_dressed_cubic_decomposition": cubic["decomposition"],
        "charge_dressed_210_multiplicity": cubic["210_multiplicity"],
        "cubic_character_residual": cubic["maximum_character_residual"],
    }


def generic_tensor_audit() -> dict[str, Any]:
    _, sigma, h = cubic_audit.generic_fields()
    value = holomorphic_54_invariant(sigma, h)
    q_sigma = sigma_pair_54(sigma, sigma)
    q_h = hdag_pair_54(h, h)

    rows: dict[str, Any] = {}
    maximum = 0.0
    for a, b in ((0, 1), (1, 7), (4, 9), (6, 8)):
        generator = cubic_audit.vector_generator_matrix(a, b)
        delta_h = generator @ h
        delta_sigma = direct.generator_action(sigma, a, b)
        delta_qh = hdag_pair_54(delta_h, h) + hdag_pair_54(
            h, delta_h
        )
        delta_qsigma = sigma_pair_54(delta_sigma, sigma) + sigma_pair_54(
            sigma, delta_sigma
        )
        derivative = np.sum(delta_qh * q_sigma + q_h * delta_qsigma)
        residual = float(abs(derivative))
        maximum = max(maximum, residual)
        rows[f"{a}{b}"] = {
            "derivative": derivative,
            "absolute_residual": residual,
        }

    cubic_generic = cubic_audit.invariance_audit()
    return {
        "O54_generic_value": value,
        "O54_generic_abs": float(abs(value)),
        "O54_qH_frobenius": float(np.linalg.norm(q_h)),
        "O54_qSigma_frobenius": float(np.linalg.norm(q_sigma)),
        "O54_generator_rows": rows,
        "O54_maximum_invariance_residual": maximum,
        "cubic_generic_abs": cubic_generic["generic_cubic_abs"],
        "cubic_maximum_invariance_residual": cubic_generic[
            "maximum_infinitesimal_invariance_residual"
        ],
    }


def selected_vacuum_audit() -> dict[str, Any]:
    delta = direct.delta_r()
    q_delta = sigma_pair_54(delta, delta)
    cubic_background = cubic_audit.background_impact()
    tadpole = cubic_background[
        "p_plus_DeltaR_H_tadpole_norm_per_unit_coefficient"
    ]
    return {
        "Q_Delta_frobenius": float(np.linalg.norm(q_delta)),
        "Q_Delta_matrix": q_delta,
        "physical_upstream_Q_Delta_frobenius": float(
            np.linalg.norm(deltar54.delta_54_matrix(v_delta_gev=1.0))
        ),
        "O54_H_holomorphic_mass_block_present": bool(
            np.linalg.norm(q_delta) > 1.0e-12
        ),
        "p_Delta_H_tadpole_norm": float(tadpole),
        "charge_dressed_H_Phi17_cross_block_present": bool(tadpole > 1.0e-12),
        "mu_D_effective_formula": (
            "mu_D_eff = mu_D + eta_plus*<Phi17> "
            "+ eta_minus*<Phi17>^*"
        ),
        "consequence": (
            "O54 is generically nonzero but vanishes on Delta_R^2. "
            "The two Phi17-dressed operators rescale the existing cubic "
            "mixed blocks through mu_D_eff and do not create an H--Phi17 "
            "block at H=0 on p+Delta_R."
        ),
    }


def completed_catalogue_overlay() -> dict[str, Any]:
    base = operator_filter.operator_catalogue(require_x=False)
    names = {row["name"] for row in base}
    appended = []
    for row in ADDITIONS:
        if row["name"] not in names:
            appended.append(dict(row))
            names.add(row["name"])
    return {
        "base_count": len(base),
        "base_names": sorted(row["name"] for row in base),
        "appended": appended,
        "completed_count": len(base) + len(appended),
        "all_three_were_missing": len(appended) == 3,
        "canonical_filter_source_update_still_required": True,
    }


def build_report() -> dict[str, Any]:
    charges = charge_audit()
    reps = representation_audit()
    generic = generic_tensor_audit()
    vacuum = selected_vacuum_audit()
    overlay = completed_catalogue_overlay()

    checks = {
        "three_omitted_classes_identified": overlay["all_three_were_missing"],
        "all_declared_charge_allowed": all(
            row["declared_allowed"]["all"] for row in charges.values()
        ),
        "Phi17_dressed_terms_fail_superseded_X_only": (
            not charges[OPLUS]["historical_X_comparison"]["all"]
            and not charges[OMINUS]["historical_X_comparison"]["all"]
        ),
        "unique_holomorphic_54_channel": (
            reps["common_channels"] == {"54": 1}
            and reps["holomorphic_quartic_channel_count"] == 1
        ),
        "unique_charge_dressed_210_contraction": (
            reps["charge_dressed_210_multiplicity"] == 1
            and reps["cubic_character_residual"] < 1.0e-40
        ),
        "generic_O54_nonzero": generic["O54_generic_abs"] > 1.0e-8,
        "generic_O54_SO10_invariant": (
            generic["O54_maximum_invariance_residual"] < 1.0e-10
        ),
        "generic_cubic_tensor_nonzero_and_invariant": (
            generic["cubic_generic_abs"] > 1.0e-8
            and generic["cubic_maximum_invariance_residual"] < 1.0e-10
        ),
        "DeltaR_squared_54_exact_zero": vacuum["Q_Delta_frobenius"] < 1.0e-12,
        "independent_DeltaR_zero_implementation_agrees": (
            vacuum["physical_upstream_Q_Delta_frobenius"] < 1.0e-12
        ),
        "no_selected_vacuum_O54_H_mass_block": (
            not vacuum["O54_H_holomorphic_mass_block_present"]
        ),
        "no_H_Phi17_cross_block_on_p_Delta": (
            not vacuum["charge_dressed_H_Phi17_cross_block_present"]
        ),
        "full_G1_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "HSIGMA_HOLOMORPHIC_AND_CHARGE_DRESSED_FAMILIES_CLOSED"
                if not failures
                else "HSIGMA_HOLOMORPHIC_CHARGE_DRESSED_GATE_FAILED"
            ),
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "charge_audit": charges,
            "representation_audit": reps,
            "generic_tensor_audit": generic,
            "selected_vacuum_audit": vacuum,
            "catalogue_overlay": overlay,
            "flags": {
                "unique_Hdag2_Sigma2_54_family_closed": not failures,
                "two_Phi17_dressed_cubic_companions_closed": not failures,
                "selected_DeltaR_O54_mass_block_zero": not failures,
                "muD_eff_replacement_required": not failures,
                "complete_mixed_invariant_ring": False,
                "complete_component_potential": False,
                "nonzero_electroweak_backreaction_solved": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "verdict": (
                "The remaining renormalizable H10--126bar holomorphic sector "
                "contains one unique 54 quartic and two Phi17-dressed copies "
                "of the unique Phi Hdag Sigmabar contraction. The 54 quartic "
                "is generically nonzero but vanishes on Delta_R^2. The "
                "dressed terms replace mu_D by mu_D_eff after Phi17 condenses. "
                "These finite families are closed; full G1 remains open."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact H10–126bar holomorphic and charge-dressed completion\n\n"
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
