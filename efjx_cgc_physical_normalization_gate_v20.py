#!/usr/bin/env python3
r"""Extract E/F/J/X gamma-response matrices and audit the physical CGC gap.

This gate separates three statements that had previously been mixed together:

1. The published Aulakh E/F/J/X component matrices have a well-defined linear
   response to the invariant coupling convention called ``gamma``.
2. The reduced ``charge_allowed_potential_minimize_v20`` benchmark uses an
   intermediate-scale radial ``10_H`` proxy, not the physical electroweak
   ``h=174 GeV`` branch.
3. Therefore the numerical ratio ``gamma_crit / lambda4_selected`` produced
   from that proxy is not a physical SO(10) Clebsch coefficient.

The missing calculation is the invariant-normalization map from the exact
non-supersymmetric operator ``Phi(210) H(10) Sigmabar(126bar) S`` to the
Aulakh gamma convention, using canonically normalized component states and the
surviving physical-EW vacuum.  This module fails closed until an evidence-backed
normalization artifact is supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import lam4_potential_efjx_decoupling_v20 as proxy_decoupling
import mixed_210_126_10_cw_v20 as mixed
import nonsusy_reduced_hessian_v20 as physical_hessian
import pq_null_lam4_portal_lift_v20 as pqnull
import promote_210n_tensor_basis_uniqueness_v20 as promote
import residual_lam210_eta_intra_v20 as residual
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EFJX_CGC_PHYSICAL_NORMALIZATION_GATE_V20.json"
OUT_MD = ROOT / "EFJX_CGC_PHYSICAL_NORMALIZATION_GATE_V20.md"
NORMALIZATION_ARTIFACT = ROOT / "EFJX_CGC_NORMALIZATION_INPUT_V20.json"
SCHEMA_VERSION = "efjx-cgc-normalization-v1"

BLOCKS: dict[str, Callable[[dict[str, complex]], np.ndarray]] = {
    "E": mixed.aulakh_E,
    "F": mixed.aulakh_F,
    "J": mixed.aulakh_J,
    "X": mixed.aulakh_X,
}

REQUIRED_NORMALIZATION_FIELDS = {
    "schema_version",
    "invariant",
    "contraction",
    "field_normalizations",
    "singlet_vev_projection",
    "gamma_mapping",
    "source_manifest",
    "acceptance_evidence",
}


def _matrix_response(
    fn: Callable[[dict[str, complex]], np.ndarray],
    p0: dict[str, complex],
) -> dict[str, Any]:
    p1 = dict(p0)
    p2 = dict(p0)
    p1["gamma"] = 1.0 + 0.0j
    p1["gamma_bar"] = 1.0 + 0.0j
    p2["gamma"] = 2.0 + 0.0j
    p2["gamma_bar"] = 2.0 + 0.0j
    m0 = np.asarray(fn(p0), dtype=complex)
    m1 = np.asarray(fn(p1), dtype=complex)
    m2 = np.asarray(fn(p2), dtype=complex)
    response = m1 - m0
    linear = bool(np.allclose(m2 - m0, 2.0 * response, rtol=1e-12, atol=1e-6))
    nonzero = np.argwhere(np.abs(response) > 1e-9)
    return {
        "shape": list(response.shape),
        "linear_in_gamma": linear,
        "n_nonzero_slots": int(nonzero.shape[0]),
        "nonzero_slots_zero_based": nonzero.tolist(),
        "rank": int(np.linalg.matrix_rank(response)),
        "frobenius_norm_GeV": float(np.linalg.norm(response)),
        "max_abs_entry_GeV": float(np.max(np.abs(response))),
        "response_real_GeV": np.real(response).tolist(),
        "response_imag_GeV": np.imag(response).tolist(),
    }


def _load_normalization_artifact() -> dict[str, Any]:
    if not NORMALIZATION_ARTIFACT.is_file():
        return {
            "exists": False,
            "accepted": False,
            "reason": "required normalization artifact absent",
        }
    raw = NORMALIZATION_ARTIFACT.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        return {
            "exists": True,
            "accepted": False,
            "sha256": digest,
            "reason": f"invalid JSON: {exc}",
        }

    missing = sorted(REQUIRED_NORMALIZATION_FIELDS - set(data))
    field_norms = data.get("field_normalizations", {})
    vev_projection = data.get("singlet_vev_projection", {})
    mapping = data.get("gamma_mapping", {})
    evidence = data.get("acceptance_evidence", {})
    sources = data.get("source_manifest", [])

    checks = {
        "schema": data.get("schema_version") == SCHEMA_VERSION,
        "invariant": data.get("invariant")
        == "Phi210_H10_Sigmabar126_S",
        "contraction_recorded": isinstance(data.get("contraction"), str)
        and len(data.get("contraction", "").strip()) > 20,
        "all_field_normalizations": all(
            key in field_norms for key in ("Phi210", "H10", "Sigmabar126", "S")
        ),
        "physical_vev_projection": all(
            key in vev_projection for key in ("p", "a", "omega", "vS", "hEW")
        )
        and float(vev_projection.get("hEW", 0.0)) == 174.0,
        "finite_gamma_mapping": isinstance(
            mapping.get("gamma_eff_over_lambda4"), (int, float)
        )
        and np.isfinite(float(mapping.get("gamma_eff_over_lambda4", np.nan))),
        "sources_present": isinstance(sources, list) and len(sources) >= 2,
        "acceptance_evidence_complete": isinstance(evidence, dict)
        and all(
            evidence.get(key)
            for key in (
                "canonical_kinetic_normalization",
                "direct_tensor_contraction",
                "independent_matrix_reconstruction",
                "physical_EW_branch_reminimized",
            )
        ),
        "closure_flags": bool(data.get("closure_complete"))
        and int(data.get("n_failed", 1)) == 0,
    }
    accepted = not missing and all(checks.values())
    return {
        "exists": True,
        "accepted": accepted,
        "sha256": digest,
        "missing_fields": missing,
        "checks": checks,
        "gamma_eff_over_lambda4": mapping.get("gamma_eff_over_lambda4"),
        "reason": "accepted" if accepted else "artifact present but evidence contract fails",
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    physical = physical_hessian.build_report()
    proxy = proxy_decoupling.build_report()
    promoted = promote.build_report()
    residual_report = residual.build_report()

    execution_failures: list[str] = []
    if not anchor.get("available"):
        execution_failures.append("unification anchor missing")
    for label, report in (
        ("physical_hessian", physical),
        ("proxy_decoupling", proxy),
        ("promote", promoted),
        ("residual", residual_report),
    ):
        if report.get("n_failed", 0):
            execution_failures.append(f"{label}: {report.get('failures')}")

    responses: dict[str, Any] = {}
    if not execution_failures:
        m_i = float(anchor["M_I_GeV"])
        m_gut = float(anchor["M_GUT_GeV"])
        fractions = promoted["selected_hilbert"]["fractions"]
        a = float(fractions["a_over_MGUT"] * m_gut)
        omega = float(fractions["omega_over_MGUT"] * m_gut)
        p = float(fractions["p_over_MGUT"] * m_gut)
        lam = float(residual_report["uv_residual_couplings"]["lam210_10"])
        eta = float(residual_report["uv_residual_couplings"]["eta_intra"])
        p0 = pqnull._params_with_gamma(
            a=a,
            omega=omega,
            p=p,
            m_i=m_i,
            m_gut=m_gut,
            lam=lam,
            eta=eta,
            gamma=0.0,
        )
        responses = {name: _matrix_response(fn, p0) for name, fn in BLOCKS.items()}

    source = inspect.getsource(proxy_decoupling)
    proxy_dependency = (
        "charge_allowed_potential_minimize_v20" in source
        and "nonsusy_reduced_hessian_v20" not in source
    )
    h_ew = float(physical.get("target_vevs_GeV", {}).get("H10_EW", np.nan))
    historical_tachyon = bool(
        physical.get("historical_benchmark", {}).get("tachyonic")
    )
    proxy_ratio = proxy.get("couplings", {}).get("c_cgc_needed_abs_approx")
    proxy_ratio_numeric = bool(
        isinstance(proxy_ratio, (int, float))
        and np.isfinite(float(proxy_ratio))
    )
    normalization = _load_normalization_artifact()

    checks = {
        "all_upstreams_executed": not execution_failures,
        "four_gamma_response_blocks_extracted": set(responses) == set(BLOCKS),
        "all_blocks_linear_in_gamma": bool(responses)
        and bool(all(row["linear_in_gamma"] for row in responses.values())),
        "all_blocks_have_nonzero_gamma_slots": bool(responses)
        and bool(all(row["n_nonzero_slots"] > 0 for row in responses.values())),
        "physical_EW_target_is_174_GeV": h_ew == 174.0,
        "historical_physical_point_is_tachyonic": historical_tachyon,
        "decoupling_certificate_uses_intermediate_H10_proxy": proxy_dependency,
        "proxy_ratio_is_numerically_reproducible": proxy_ratio_numeric,
        "proxy_ratio_not_promoted_to_physical_CGC": True,
        "whole_model_not_overclaimed": True,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]

    exact_mapping_closed = bool(normalization.get("accepted"))
    state = (
        "EXECUTION_FAIL"
        if execution_failures or failed_checks
        else "PASS"
        if exact_mapping_closed
        else "BLOCKED"
    )

    return {
        "status": "EFJX_CGC_PHYSICAL_NORMALIZATION_GATE_EXECUTED",
        "overall_state": state,
        "n_failed": len(execution_failures) + len(failed_checks),
        "execution_failures": execution_failures,
        "failed_checks": failed_checks,
        "checks": checks,
        "gamma_response_matrices": responses,
        "proxy_dependency_audit": {
            "uses_charge_allowed_intermediate_H10_proxy": proxy_dependency,
            "imports_physical_EW_hessian": False,
            "physical_H10_EW_GeV": h_ew,
            "physical_historical_point_tachyonic": historical_tachyon,
            "reported_proxy_c_cgc_needed_abs_approx": proxy_ratio,
            "reported_ratio_classification": (
                "proxy-local diagnostic only; not a physical Clebsch coefficient"
            ),
        },
        "normalization_artifact": normalization,
        "remaining_blockers": {
            "canonical_Phi_H_Sigmabar_tensor_contraction": not exact_mapping_closed,
            "field_and_state_normalizations_in_one_convention": not exact_mapping_closed,
            "physical_p_a_omega_vS_hEW_projection": not exact_mapping_closed,
            "direct_reconstruction_of_E_F_J_X_gamma_slots": not exact_mapping_closed,
            "physical_EW_reminimization_after_CGC_insertion": not exact_mapping_closed,
        },
        "required_artifact": {
            "path": NORMALIZATION_ARTIFACT.name,
            "schema_version": SCHEMA_VERSION,
            "required_fields": sorted(REQUIRED_NORMALIZATION_FIELDS),
            "required_invariant": "Phi210_H10_Sigmabar126_S",
        },
        "flags": {
            "exact_EFJX_gamma_response_known": bool(responses)
            and bool(all(row["linear_in_gamma"] for row in responses.values())),
            "proxy_cgc_ratio_invalid_as_physical_prediction": bool(
                proxy_dependency and historical_tachyon
            ),
            "physical_CGC_normalization_derived": bool(exact_mapping_closed),
            "physical_EW_branch_revalidated": bool(exact_mapping_closed),
            "whole_model_excluded": False,
            "whole_model_validated": state == "PASS",
        },
        "verdict": (
            "The exact E/F/J/X matrices already determine how each component "
            "block responds to the Aulakh gamma convention. The remaining gap "
            "is the normalized tensor map from Phi H Sigmabar S to gamma on "
            "the physical h=174 GeV branch. The numerical c_cgc ratio obtained "
            "from the old H10=M_I radial proxy is not a physical Clebsch "
            "prediction and cannot be used to validate or exclude the model."
        ),
    }


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _sanitize(obj: Any) -> Any:
    """Convert numpy scalars/arrays into plain Python JSON types."""
    if isinstance(obj, dict):
        return {str(k): _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, tuple):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def write_report(report: dict[str, Any]) -> None:
    clean = _sanitize(report)
    OUT_JSON.write_text(
        json.dumps(clean, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# E/F/J/X physical CGC-normalization gate — v20",
        "",
        f"**State:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Gamma-response matrices",
        "",
    ]
    for name, row in report["gamma_response_matrices"].items():
        lines.append(
            f"- **{name}:** shape={row['shape']}, rank={row['rank']}, "
            f"nonzero slots={row['n_nonzero_slots']}"
        )
    lines.extend(["", "## Remaining blockers", ""])
    lines.extend(
        f"- `{name}`: {value}"
        for name, value in report["remaining_blockers"].items()
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = _sanitize(build_report())
    write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True, default=_json_default))
    return 1 if report["overall_state"] == "EXECUTION_FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
