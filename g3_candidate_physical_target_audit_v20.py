#!/usr/bin/env python3
"""Physical-target audit of the certified SU(5)+Delta chiral-H G3 candidate.

The G3 route certifies an exactly stationary point with a strict
physical-quotient minimum at

    (Phi, Sigma, H, S, Phi17) = (F, r Delta_R, H_chi, r, 1),  r = 1/5,
    H_chi = (e6 + i e7)/sqrt(2).

This module asks whether that point can be the physical vacuum.  It cannot.
Every number below comes from the repository's live 51-parameter exact-X
derivative compiler on the canonical 486-real field chart; mass-squared
values are Hessian eigenvalues in units of the benchmark scale M (|Phi|=1).

* The 10_H splits as (6,1,1)+(1,2,2) with components 0..5 and 6..9.  H_chi
  lies entirely in the (1,2,2) electroweak-doublet block and
  |<H>|/|<Phi>| = 1, so electroweak symmetry is broken at the GUT scale.
* At the GUT point (F, r Delta_R, H=0, r, 1) the 10_H mass matrix is purely
  Hermitian and SM block diagonal, and all ten complex modes are tachyonic:
  doublets at -2 and -4/5, colour triplets at -1.998 and -0.802.
* Inside each SU(5) five-plet the doublet-triplet splitting is exactly
  beta r^2 = 1/500.  Phi=F is an SU(5) singlet with no 54 component, so the
  54 channel gives no H mass, and only beta O35_45 splits a five-plet.
* O06 enters as the identity.  Tuning only O06 from -2 to 0 leaves exactly
  one massless doublet, with its colour-triplet partner at m_T^2 = beta r^2
  M^2, i.e. M_T ~ 0.045 M, which G8 must accommodate.
* Every S and Phi17 portal coefficient vanishes.  This includes kappa_H, the
  SARAH ``kappaH H10.H10.S`` term, census orbit O12.  The axion singlet S
  therefore decouples from the GUT fields in the benchmark.
* The certified vevs are not at the repository's physical hierarchy.  Sigma
  and S sit at r = 1/5 of M_GUT, so PQ and B-L break near 2e15 GeV instead of
  M_I ~ 6.3e11 GeV.  At the physical hierarchy the tuned triplet partner would
  sit at sqrt(beta) M_I ~ 1.4e11 GeV.

The physical G3 target is the tuned point (F, r Delta_R, H ~ v_EW).  Its
effective Higgs quartic is audited in
``g3_tuned_target_effective_higgs_quartic_v20``.  This module closes no gate
and excludes nothing.
"""
from __future__ import annotations

import argparse
import json
import math
from collections.abc import Callable, Mapping
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_gauged_u1x_g3_su5_delta_hsx_extension_v20 as candidate_source
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_CANDIDATE_PHYSICAL_TARGET_AUDIT_V20.json"
OUT_MD = ROOT / "G3_CANDIDATE_PHYSICAL_TARGET_AUDIT_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
BETA = candidate_source.BETA
R = candidate_source.R
BETA_R2 = BETA * R * R
O06_ID = "lambda::O06_B01_Hdag_H_norm"
O35_45_ID = "lambda::O35_B02_H_Sigma_hermitian"
O46_54_ID = "lambda::O46_B03_Phi2_HdagH_channels"
FIELD_ORDER = potential.FIELD_ORDER
GUT_FIELDS = ("P", "H", "Hb", "D", "Db")
SINGLET_FIELDS = ("S", "Sb", "X", "Xb")
H_FIELDS = ("H", "Hb")
TRIPLET_BLOCK = slice(0, 6)
DOUBLET_BLOCK = slice(6, 10)
STATIONARITY_ATOL = 1.0e-10
SPECTRUM_ATOL = 1.0e-12
DIGITS = 12
UNITS = "Hessian eigenvalues of the canonical 486-real chart, units of the benchmark scale M (|Phi|=1)"

DirectionFilter = Callable[[potential.Direction], bool]


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, float):
        return round(value, DIGITS) + 0.0
    return value


def involves_fields(fields: tuple[str, ...]) -> DirectionFilter:
    indices = tuple(FIELD_ORDER.index(name) for name in fields)
    return lambda direction: any(direction.counts[index] for index in indices)


def parameter_rows(
    state: potential.FieldState, *, include: DirectionFilter | None = None
) -> dict[str, derivatives.ParameterDerivative]:
    """Exact-X parameter rows (value, gradient, Hessian) at ``state``.

    ``include`` restricts the evaluation to some live directions; rows of the
    omitted directions are simply absent.
    """
    selection = g2_audit.contract_selection()
    live = set(selection["direction_ids"])
    q = chart.pack(state)
    directions = {
        row.direction_id: row
        for row in potential.evaluate_directions(state)
        if row.direction_id in live and (include is None or include(row))
    }
    owners = g2_audit._adapter_modules_by_family()
    rows = tuple(
        owners[directions[direction_id].base_family].direction_derivative(
            q, directions[direction_id]
        )
        for direction_id in sorted(directions)
    )
    return {row.parameter_id: row for row in derivatives.parameter_derivatives(rows)}


def assemble(
    rows: Mapping[str, derivatives.ParameterDerivative],
    coefficients: Mapping[str, float],
) -> tuple[float, np.ndarray, np.ndarray]:
    missing = sorted(set(coefficients).difference(rows))
    if missing:
        raise KeyError(f"coefficients without compiled rows: {missing}")
    value = 0.0
    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for parameter_id, coefficient in coefficients.items():
        row = rows[parameter_id]
        value += coefficient * float(row.value)
        gradient += coefficient * np.asarray(row.gradient, dtype=float)
        hessian += coefficient * np.asarray(row.hessian, dtype=float)
    return value, gradient, 0.5 * (hessian + hessian.T)


def hermitian_h_mass_matrix(hessian: np.ndarray) -> tuple[np.ndarray, float]:
    """Return M with V = h^dag M h, and the holomorphic (h h) residual.

    The chart stores h_k = (x_k + i y_k)/sqrt(2) with interleaved (x, y), so
    a Hermitian mass term has the real block form [[Re M, -Im M], [Im M, Re M]].
    """
    block = np.asarray(hessian, dtype=float)[chart.H_SLICE, chart.H_SLICE]
    xs, ys = slice(0, None, 2), slice(1, None, 2)
    matrix = block[xs, xs] + 1j * block[ys, xs]
    holomorphic = max(
        float(np.max(np.abs(block[ys, ys] - block[xs, xs]))),
        float(np.max(np.abs(block[xs, ys] + block[ys, xs]))),
    )
    return matrix, holomorphic


def _grouped(values: np.ndarray) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for value in np.sort(np.asarray(values, dtype=float)):
        if groups and abs(value - groups[-1]["mass_squared"]) <= 1.0e-9:
            groups[-1]["complex_multiplicity"] += 1
        else:
            groups.append({"mass_squared": float(value), "complex_multiplicity": 1})
    return groups


def sm_branch_spectrum(matrix: np.ndarray) -> dict[str, Any]:
    """Eigenvalues of the colour-triplet and weak-doublet blocks of 10_H."""
    triplet = np.linalg.eigvalsh(matrix[TRIPLET_BLOCK, TRIPLET_BLOCK])
    doublet = np.linalg.eigvalsh(matrix[DOUBLET_BLOCK, DOUBLET_BLOCK])
    return {
        "hermiticity_residual": float(np.max(np.abs(matrix - matrix.conj().T))),
        "triplet_doublet_mixing_residual": float(
            np.max(np.abs(matrix[TRIPLET_BLOCK, DOUBLET_BLOCK]))
        ),
        "colour_triplets": _grouped(triplet),
        "weak_doublets": _grouped(doublet),
        "maximum_eigenvalue": float(max(triplet.max(), doublet.max())),
    }


def _values(groups: list[dict[str, Any]]) -> list[float]:
    return [group["mass_squared"] for group in groups]


def _close(observed: list[float], expected: list[float]) -> bool:
    return len(observed) == len(expected) and all(
        abs(a - b) <= SPECTRUM_ATOL for a, b in zip(observed, expected)
    )


def candidate_coefficients() -> dict[str, float]:
    return dict(candidate_source.numerical_coefficient_map())


def gut_point_state() -> potential.FieldState:
    """The certified candidate with H removed: (F, r Delta_R, 0, r, 1)."""
    state = candidate_source.candidate_state()
    return potential.FieldState(
        phi=state.phi,
        h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex),
        sigma=state.sigma,
        s=state.s,
        x=state.x,
    ).validated()


@lru_cache(maxsize=1)
def candidate_rows() -> dict[str, derivatives.ParameterDerivative]:
    return parameter_rows(candidate_source.candidate_state())


@lru_cache(maxsize=1)
def gut_point_rows() -> dict[str, derivatives.ParameterDerivative]:
    return parameter_rows(gut_point_state())


def candidate_vacuum_audit() -> dict[str, Any]:
    state = candidate_source.candidate_state()
    q = chart.pack(state)
    _, gradient, _ = assemble(candidate_rows(), candidate_coefficients())
    h = np.asarray(state.h, dtype=complex)
    h_norm = float(np.linalg.norm(h))
    phi_norm = float(np.linalg.norm(q[chart.PHI_SLICE]))
    doublet_weight = float(np.sum(np.abs(h[DOUBLET_BLOCK]) ** 2)) / h_norm**2
    return {
        "state": "(F, r Delta_R, H_chi, r, 1) with r=1/5",
        "H_components": {
            "nonzero": {
                str(index): {"re": float(value.real), "im": float(value.imag)}
                for index, value in enumerate(h)
                if abs(value) > 0
            },
            "labelling": "10_H = (6,1,1)+(1,2,2): components 0..5 colour, 6..9 electroweak",
        },
        "gradient_max_abs": float(np.max(np.abs(gradient))),
        "N_H": h_norm**2,
        "Phi_norm": phi_norm,
        "H_over_Phi_complex_norm_ratio": h_norm / phi_norm,
        "H_over_Phi_canonical_real_chart_ratio": float(
            np.linalg.norm(q[chart.H_SLICE]) / phi_norm
        ),
        "H_weight_in_electroweak_doublet_block": doublet_weight,
        "H_weight_in_colour_block": 1.0 - doublet_weight,
        "electroweak_symmetry_broken_at_gut_scale": bool(
            doublet_weight > 1.0 - SPECTRUM_ATOL and h_norm / phi_norm > 0.1
        ),
    }


def gut_point_h10_audit() -> dict[str, Any]:
    rows = gut_point_rows()
    coefficients = candidate_coefficients()
    _, gradient, hessian = assemble(rows, coefficients)
    matrix, holomorphic = hermitian_h_mass_matrix(hessian)
    spectrum = sm_branch_spectrum(matrix)

    contributions: dict[str, Any] = {}
    for parameter_id, coefficient in sorted(coefficients.items()):
        _, _, term = assemble(rows, {parameter_id: coefficient})
        term_matrix, _ = hermitian_h_mass_matrix(term)
        if np.max(np.abs(term_matrix)) > SPECTRUM_ATOL:
            term_spectrum = sm_branch_spectrum(term_matrix)
            contributions[parameter_id] = {
                "colour_triplets": _values(term_spectrum["colour_triplets"]),
                "weak_doublets": _values(term_spectrum["weak_doublets"]),
            }
    _, _, o06_hessian = assemble(rows, {O06_ID: 1.0})
    o06_matrix, _ = hermitian_h_mass_matrix(o06_hessian)
    _, _, o46_54_hessian = assemble(rows, {O46_54_ID: 1.0})
    o46_54_matrix, _ = hermitian_h_mass_matrix(o46_54_hessian)
    _, _, beta_hessian = assemble(rows, {O35_45_ID: coefficients[O35_45_ID]})
    beta_spectrum = sm_branch_spectrum(hermitian_h_mass_matrix(beta_hessian)[0])

    doublets = _values(spectrum["weak_doublets"])
    triplets = _values(spectrum["colour_triplets"])
    pairwise = [abs(t - d) for t, d in zip(triplets, doublets)] if len(triplets) == len(doublets) else []
    return {
        "state": "(F, r Delta_R, H=0, r, 1): certified couplings, H removed",
        "gradient_max_abs": float(np.max(np.abs(gradient))),
        "holomorphic_h_mass_residual": holomorphic,
        "spectrum": spectrum,
        "doublet_triplet_splitting_per_five_plet": pairwise,
        "beta_r_squared": BETA_R2,
        "O06_block_identity_residual": float(np.max(np.abs(o06_matrix - np.eye(10)))),
        "O46_54_channel_block_max_abs_at_F": float(np.max(np.abs(o46_54_matrix))),
        "beta_O35_45_block": {
            "colour_triplets": _values(beta_spectrum["colour_triplets"]),
            "weak_doublets": _values(beta_spectrum["weak_doublets"]),
        },
        "h_mass_contributions_by_parameter": contributions,
    }


def o06_tuning_audit() -> dict[str, Any]:
    coefficients = candidate_coefficients()
    rest = {key: value for key, value in coefficients.items() if key != O06_ID}
    _, _, hessian = assemble(gut_point_rows(), rest)
    matrix, _ = hermitian_h_mass_matrix(hessian)
    rest_spectrum = sm_branch_spectrum(matrix)
    lightest_doublet = _values(rest_spectrum["weak_doublets"])[0]
    tuned = -lightest_doublet
    tuned_spectrum = sm_branch_spectrum(matrix + tuned * np.eye(10))
    partner = _values(tuned_spectrum["colour_triplets"])[0]
    exact = candidate_source.fixed_pd_equal_norm_h_orientation_certificate()[
        "Hermitian_alignment_plus_current_spectrum"
    ]
    exact_doublets = sorted(
        float(row["eigenvalue"]) for name, row in exact.items() if "EW" in name
    )
    exact_triplets = sorted(
        float(row["eigenvalue"]) for name, row in exact.items() if "colour" in name
    )
    return {
        "certified_O06": coefficients[O06_ID],
        "tuned_O06": tuned,
        "spectrum_without_O06": rest_spectrum,
        "exact_source_spectrum": {
            "weak_doublets": exact_doublets,
            "colour_triplets": exact_triplets,
            "source": (
                "exact_gauged_u1x_g3_su5_delta_hsx_extension_v20."
                "fixed_pd_equal_norm_h_orientation_certificate"
            ),
        },
        "tuned_spectrum": tuned_spectrum,
        "massless_doublets": sum(
            group["complex_multiplicity"]
            for group in tuned_spectrum["weak_doublets"]
            if abs(group["mass_squared"]) <= SPECTRUM_ATOL
        )
        // 2,
        "partner_triplet_mass_squared_over_M2": partner,
        "partner_triplet_mass_over_M": math.sqrt(max(partner, 0.0)),
    }


def singlet_portal_audit() -> dict[str, Any]:
    coefficients = candidate_coefficients()
    live = set(g2_audit.contract_selection()["direction_ids"])
    portals: dict[str, Any] = {}
    singlet_only: dict[str, Any] = {}
    for direction in potential.evaluate_directions(gut_point_state()):
        if direction.direction_id not in live:
            continue
        counts = dict(zip(FIELD_ORDER, direction.counts))
        has_singlet = any(counts[name] for name in SINGLET_FIELDS)
        has_gut = any(counts[name] for name in GUT_FIELDS)
        if not has_singlet:
            continue
        prefixes = ("lambda",) if direction.self_conjugate else ("re", "im")
        values = {
            f"{prefix}::{direction.direction_id}": coefficients.get(
                f"{prefix}::{direction.direction_id}", 0.0
            )
            for prefix in prefixes
        }
        row = {"monomial": direction.representative, "coefficients": values}
        (portals if has_gut else singlet_only)[direction.direction_id] = row
    return {
        "S_and_Phi17_portals": portals,
        "singlet_self_couplings": singlet_only,
        "kappa_H_SARAH_term": "kappaH H10.H10.S = census orbit O12 (10_H^dag^2 S^dag)",
        "all_portals_vanish": all(
            value == 0.0
            for row in portals.values()
            for value in row["coefficients"].values()
        ),
    }


def hierarchy_audit() -> dict[str, Any]:
    """Compare the certified vevs with the repository's physical hierarchy."""
    candidate = chart.pack(candidate_source.candidate_state())
    physical_state = g2_audit.physical_hierarchy_state()
    physical = chart.pack(physical_state)
    metadata = g2_audit._physical_hierarchy_metadata(physical_state)
    blocks = {
        "Phi210": chart.PHI_SLICE,
        "H10": chart.H_SLICE,
        "Sigma126bar": chart.SIGMA_SLICE,
        "S": chart.S_SLICE,
        "Phi17": chart.X_SLICE,
    }
    norms = {}
    for name, block in blocks.items():
        certified = float(np.linalg.norm(candidate[block]))
        reference = float(np.linalg.norm(physical[block]))
        norms[name] = {
            "certified_candidate": certified,
            "physical_hierarchy": reference,
            "ratio": certified / reference,
        }
    phi_c = candidate[chart.PHI_SLICE] / np.linalg.norm(candidate[chart.PHI_SLICE])
    phi_p = physical[chart.PHI_SLICE] / np.linalg.norm(physical[chart.PHI_SLICE])
    m_gut = float(metadata["M_GUT_GeV"])
    m_i = float(metadata["M_I_GeV"])
    beta = float(BETA)
    return {
        "physical_hierarchy_source": "gauged_u1x_g2_derivative_audit_v20.physical_hierarchy_state",
        "M_GUT_GeV": m_gut,
        "M_I_GeV": m_i,
        "block_norms": norms,
        "Phi_direction_overlap_certified_F_vs_reference": abs(float(phi_c @ phi_p)),
        "Sigma_and_S_scale_over_M_GUT": {"certified": float(R), "physical": m_i / m_gut},
        "certified_PQ_and_B_minus_L_breaking_scale_GeV": float(R) * m_gut,
        "triplet_partner_mass_GeV": {
            "certified_hierarchy": math.sqrt(beta) * float(R) * m_gut,
            "physical_hierarchy": math.sqrt(beta) * m_i,
            "formula": "M_T = sqrt(beta) <Sigma> when O06 is tuned for a massless doublet",
        },
        "certified_candidate_at_physical_hierarchy": bool(
            all(0.5 < row["ratio"] < 2.0 for row in norms.values())
        ),
    }


def build_report() -> dict[str, Any]:
    candidate = candidate_vacuum_audit()
    gut = gut_point_h10_audit()
    tuning = o06_tuning_audit()
    portals = singlet_portal_audit()
    hierarchy = hierarchy_audit()
    spectrum = gut["spectrum"]
    beta_r2 = float(BETA_R2)
    checks = {
        "candidate_is_exactly_stationary": candidate["gradient_max_abs"] < STATIONARITY_ATOL,
        "candidate_H_lies_in_electroweak_doublet_block": (
            candidate["H_weight_in_electroweak_doublet_block"] > 1.0 - SPECTRUM_ATOL
        ),
        "candidate_H_to_Phi_vev_ratio_is_one": abs(
            candidate["H_over_Phi_complex_norm_ratio"] - 1.0
        )
        <= SPECTRUM_ATOL,
        "gut_point_is_stationary": gut["gradient_max_abs"] < STATIONARITY_ATOL,
        "gut_point_h10_mass_is_hermitian_and_sm_block_diagonal": (
            gut["holomorphic_h_mass_residual"] <= SPECTRUM_ATOL
            and spectrum["hermiticity_residual"] <= SPECTRUM_ATOL
            and spectrum["triplet_doublet_mixing_residual"] <= SPECTRUM_ATOL
        ),
        "gut_point_all_h10_modes_tachyonic": spectrum["maximum_eigenvalue"] < 0.0,
        "gut_point_doublets_at_minus_2_and_minus_4_over_5": _close(
            _values(spectrum["weak_doublets"]), [-2.0, -0.8]
        ),
        "gut_point_triplets_at_minus_1_998_and_minus_0_802": _close(
            _values(spectrum["colour_triplets"]), [-2.0 + beta_r2, -0.8 - beta_r2]
        ),
        "doublet_triplet_splitting_equals_beta_r_squared": _close(
            gut["doublet_triplet_splitting_per_five_plet"], [beta_r2, beta_r2]
        ),
        "only_beta_O35_45_splits_five_plets": (
            _close(gut["beta_O35_45_block"]["colour_triplets"], [-beta_r2, beta_r2])
            and _close(gut["beta_O35_45_block"]["weak_doublets"], [0.0])
        ),
        "F_has_no_54_channel_h_mass": gut["O46_54_channel_block_max_abs_at_F"] <= SPECTRUM_ATOL,
        "O06_enters_as_identity": gut["O06_block_identity_residual"] <= SPECTRUM_ATOL,
        "numerical_spectrum_matches_exact_source_spectrum": (
            _close(
                _values(tuning["spectrum_without_O06"]["weak_doublets"]),
                tuning["exact_source_spectrum"]["weak_doublets"],
            )
            and _close(
                _values(tuning["spectrum_without_O06"]["colour_triplets"]),
                tuning["exact_source_spectrum"]["colour_triplets"],
            )
        ),
        "tuning_only_O06_to_zero_leaves_one_massless_doublet": (
            abs(tuning["tuned_O06"]) <= SPECTRUM_ATOL and tuning["massless_doublets"] == 1
        ),
        "tuned_partner_triplet_at_beta_r_squared": (
            abs(tuning["partner_triplet_mass_squared_over_M2"] - beta_r2) <= SPECTRUM_ATOL
        ),
        "all_S_and_Phi17_portals_vanish": portals["all_portals_vanish"],
        "physical_hierarchy_reference_is_hierarchical": (
            hierarchy["Sigma_and_S_scale_over_M_GUT"]["physical"] < 1.0e-3
        ),
        "no_gate_closed_or_model_excluded": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    ok = not failures
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": (
            "G3_CERTIFIED_CANDIDATE_BREAKS_ELECTROWEAK_SYMMETRY_AT_GUT_SCALE__TUNED_PHYSICAL_TARGET_OPEN"
            if ok
            else "G3_CANDIDATE_PHYSICAL_TARGET_AUDIT_FAILED"
        ),
        "overall_state": "PHYSICAL_TARGET_MISMATCH_IDENTIFIED" if ok else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "units": UNITS,
        "certified_candidate": candidate,
        "gut_point_h10": gut,
        "o06_tuning": tuning,
        "singlet_portals": portals,
        "hierarchy": hierarchy,
        "physical_target": {
            "state": "(Phi, Sigma, H, S, Phi17) = (F, r Delta_R, H ~ v_EW along the massless doublet, r, 1)",
            "hierarchy_caveat": (
                "The certified point puts Sigma and S at r = 1/5 of M_GUT, so PQ and B-L break "
                "near 2e15 GeV; the repository's physical hierarchy puts them at M_I ~ 6.3e11 GeV. "
                "There the tuned triplet partner sits at sqrt(beta) M_I ~ 1.4e11 GeV, a G8 input."
            ),
            "coefficient_change": {O06_ID: {"certified": "-2", "tuned": "0"}},
            "doublet_triplet_splitting": "m_T^2 = beta r^2 M^2 = M^2/500",
            "next": "effective Higgs quartic at the tuned point: g3_tuned_target_effective_higgs_quartic_v20.py",
        },
        "flags": {
            "certified_candidate_is_physical_vacuum": False,
            "certified_candidate_breaks_electroweak_symmetry_at_gut_scale": ok
            and candidate["electroweak_symmetry_broken_at_gut_scale"],
            "gut_point_h10_fully_tachyonic": checks["gut_point_all_h10_modes_tachyonic"],
            "axion_singlet_decoupled_in_candidate": checks["all_S_and_Phi17_portals_vanish"],
            "certified_candidate_at_physical_hierarchy": hierarchy[
                "certified_candidate_at_physical_hierarchy"
            ],
            "g3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The certified G3 point is a mathematically valid strict minimum of the "
            "benchmark potential but not a physical vacuum: its 10_H vev lies in an "
            "electroweak doublet with |<H>|/|<Phi>| = 1. At (F, r Delta_R, H=0) every "
            "10_H mode is tachyonic and each five-plet is split only by beta r^2 = 1/500. "
            "Retuning O06 alone to 0 gives one massless doublet with a triplet partner "
            "at M_T = M/sqrt(500). The axion singlet has no portal to the GUT fields in "
            "the benchmark, and Sigma and S sit at M_GUT/5 rather than at the "
            "intermediate scale M_I. G3 should be aimed at the tuned point at the "
            "physical hierarchy; nothing is closed or excluded here."
        ),
    }


def _clean(value: float) -> float:
    return round(float(value), DIGITS) + 0.0


def _markdown(report: dict[str, Any]) -> str:
    gut = report["gut_point_h10"]["spectrum"]
    tuning = report["o06_tuning"]
    return "\n".join(
        [
            "# G3 certified-candidate physical-target audit -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- |<H>|/|<Phi>| at the certified point: `{report['certified_candidate']['H_over_Phi_complex_norm_ratio']:.12g}` (H in the (1,2,2) block);",
            f"- GUT-point doublets: `{[_clean(g['mass_squared']) for g in gut['weak_doublets']]}`;",
            f"- GUT-point colour triplets: `{[_clean(g['mass_squared']) for g in gut['colour_triplets']]}`;",
            f"- tuned O06: `{_clean(tuning['tuned_O06'])}`; partner triplet m^2/M^2: `{_clean(tuning['partner_triplet_mass_squared_over_M2'])}`;",
            f"- S/Phi17 portals all zero: `{report['singlet_portals']['all_portals_vanish']}`;",
            f"- Sigma, S scale / M_GUT: certified `{report['hierarchy']['Sigma_and_S_scale_over_M_GUT']['certified']:.3g}`, "
            f"physical `{report['hierarchy']['Sigma_and_S_scale_over_M_GUT']['physical']:.3g}`; "
            f"triplet partner at the physical hierarchy `{report['hierarchy']['triplet_partner_mass_GeV']['physical_hierarchy']:.3g}` GeV;",
            "- G3: `OPEN`; whole model: neither validated nor excluded.",
            "",
        ]
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
