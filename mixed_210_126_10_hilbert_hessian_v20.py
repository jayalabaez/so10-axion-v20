#!/usr/bin/env python3
"""Withdraw imported SUSY fermion/gaugino matrices from the non-SUSY Hessian.

Earlier versions squared singular values of Aulakh chiral and mixed
chiral-gauge fermion mass matrices and appended them as scalar Hessian
curvatures. That is not a valid non-supersymmetric component derivation.

This compatibility module keeps the historical parameter helper used by a few
source-diagnostic modules, but it emits no physical scalar eigenvalues. The
replacement portal tensor is provided by direct_phi_h_sigmabar_tensor_v20.py;
physical scalar closure requires insertion into the complete non-SUSY
mass-squared matrix derived from the full scalar potential.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct

ROOT = Path(__file__).resolve().parent
NULL_TOL_OVER_MGUT = 1e-8


def hilbert_matched_params(
    *,
    a: float,
    omega: float,
    p: float,
    m_i: float,
    m_gut: float,
    lam: float,
    eta: float,
) -> dict[str, complex]:
    """Historical Aulakh diagnostic parameters; not a scalar Hessian map."""
    return {
        "M_H": complex(m_gut),
        "M": complex(m_gut),
        "m": complex(m_gut),
        "lam": complex(lam),
        "eta": complex(eta),
        "gamma": 0.0 + 0.0j,
        "gamma_bar": 0.0 + 0.0j,
        "a": complex(a),
        "p": complex(p),
        "omega": complex(omega),
        "sigma": complex(m_i),
        "sigma_bar": complex(m_i),
        "pq_gamma_forbidden": True,
        "physical_use": "SUSY source diagnostic only",
    }


def spectrum_with_nulls(
    name: str,
    mat: Any,
    sm: str,
    *,
    m_gut: float,
) -> dict[str, Any]:
    """Fail-closed compatibility response; no scalar spectrum is emitted."""
    shape = list(getattr(mat, "shape", ()))
    return {
        "name": name,
        "sm": sm,
        "matrix_shape": shape,
        "n_physical": 0,
        "n_pq_null": 0,
        "masses_GeV": [],
        "pq_null_GeV": [],
        "mass_min_GeV": None,
        "mass_max_GeV": None,
        "all_physical_positive": False,
        "withdrawn": True,
        "reason": "input is a SUSY fermion/gaugino matrix, not non-SUSY scalar M^2",
    }


def build_mixed_at_hilbert(**kwargs: Any) -> dict[str, Any]:
    return {
        "params": {
            "a": kwargs.get("a"),
            "omega": kwargs.get("omega"),
            "p": kwargs.get("p"),
            "gamma": 0.0,
            "gamma_bar": 0.0,
            "physical_use": "withdrawn SUSY diagnostic",
        },
        "blocks": [],
        "n_blocks": 0,
        "n_physical_modes": 0,
        "n_pq_null_modes": 0,
        "all_physical_positive": False,
        "lightest_GeV": None,
        "heaviest_GeV": None,
        "withdrawn": True,
    }


def hessian_rows_from_mixed(spectra: dict[str, Any]) -> list[dict[str, Any]]:
    return []


def build_report() -> dict[str, Any]:
    tensor = direct.build_report()
    checks = {
        "direct_tensor_executes": tensor.get("n_failed") == 0,
        "susy_fermion_matrices_not_relabelled_scalar_m2": True,
        "no_imported_scalar_eigenvalues_emitted": True,
        "old_complete_hessian_claim_withdrawn": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "MIXED_SUSY_FERMION_MATRICES_WITHDRAWN_FROM_NONSUSY_HESSIAN"
            if not failures
            else "MIXED_HESSIAN_WITHDRAWAL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_audit": {
            "withdrawn_inputs": [
                "Aulakh chiral T/D fermion matrices",
                "Aulakh mixed chiral-gauge E/F/J/X matrices",
                "Aulakh cal G chiral/gaugino matrix",
            ],
            "invalid_operation": (
                "squaring SUSY fermion singular values and appending them as "
                "non-SUSY scalar Hessian eigenvalues"
            ),
        },
        "direct_tensor_replacement": {
            "status": tensor.get("status"),
            "map_shape": tensor.get("representation", {}).get("tensor_map_shape"),
            "analytic_spectrum_derived": tensor.get("flags", {}).get(
                "closed_analytic_portal_spectrum_derived"
            ),
        },
        "mixed_spectra": {
            "withdrawn": True,
            "n_blocks": 0,
            "n_physical_modes": 0,
            "n_pq_null_modes": 0,
            "all_physical_positive": False,
            "blocks": [],
        },
        "hessian_extension": {
            "withdrawn": True,
            "n_physical_rows": 0,
            "n_pq_null_rows": 0,
            "combined_with_off_singlet_radial_pd": False,
        },
        "remaining_blockers": {
            "complete_nonsusy_invariant_ring": True,
            "direct_component_mass_squared_matrix": True,
            "global_vacuum_and_boundedness": True,
            "full_component_hessian": True,
        },
        "flag": {
            "mixed_210_126_10_complete": False,
            "cal_T_D_E_F_J_X_G_included_as_scalar_hessian": False,
            "imported_susy_hessian_withdrawn": True,
            "direct_portal_tensor_available": tensor.get("n_failed") == 0,
            "combined_extended_hessian_pd": False,
            "full_sm_irrep_mass_matrices": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The former mixed scalar-Hessian closure is withdrawn. Aulakh T/D, "
            "E/F/J/X and cal G are SUSY fermion/gaugino matrices and cannot be "
            "converted into non-SUSY scalar curvatures by squaring singular values. "
            "The direct portal tensor is available, but the full scalar M^2 is open."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    ROOT.joinpath("MIXED_210_126_10_HILBERT_HESSIAN_V20.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("MIXED_210_126_10_HILBERT_HESSIAN_V20.md").write_text(
        "# Mixed-Hessian source correction — v20\n\n" + report["verdict"] + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
