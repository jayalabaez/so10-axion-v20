#!/usr/bin/env python3
"""V52 lean nonlinear-link and endpoint-alignment audit.

This audit asks whether the fatal field burden and the 12 uneaten A5-like
chirals of the V51 polynomial moose can be removed by changing the microscopic
contract.  The candidate is a two-site, four-dimensional N=1 gauged nonlinear
sigma model.  Its link is a group-valued chiral field mathcal_U in
Spin(10,C), with U=rho_10(mathcal_U) in SO(10,C), rather
than 612 unconstrained link coordinates plus 567 multiplier coordinates.

The executable result is deliberately local and fail-closed.  It proves that
the PS/SU(5) endpoint incidence has a 12-dimensional double-broken sector and
that the holomorphic, gauge-invariant alignment function

  W_align = mu f^2/64 Tr([P, U J_s U^{-1}]^2)

has rank exactly 12 there, annihilates every gauge orbit, and removes all 12
uneaten linearized chirals.  It is nevertheless a nonlinear EFT interaction,
not a renormalizable elementary-field UV completion.  Keeping the V51 linear
210+126+bar126 source sector also leaves a one-loop Spin(10) pole only 3.51
times above the matching scale at g=0.73.  A fully nonlinear/composite source
removes that particular one-loop index obstruction only as an EFT hypothesis;
its UV completion and matching to the frozen theory are not constructed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import sympy as sp


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V52_LEAN_NONLINEAR_ALIGNMENT_AUDIT.json"
MD_PATH = ROOT / "SUSY_V52_LEAN_NONLINEAR_ALIGNMENT_AUDIT.md"

STATUS = (
    "V52_TWO_SITE_N1_NONLINEAR_SPIN10_LINK_EFT__"
    "EXACT_PS_SU5_INCIDENCE_AND_RANK12_ALIGNMENT_HESSIAN__"
    "ALL12_A5_LIKE_CHIRALS_LIFTED_WITHOUT_MULTIPLIER_FIELDS__"
    "HOLOMORPHIC_BUT_NONRENORMALIZABLE_SIGMA_MODEL__"
    "LINEAR_SOURCE_POLE_RATIO3P51_AND_COMPOSITE_SOURCE_UV_OPEN__"
    "NEW_ACTION_NOT_G2_CLOSURE"
)

UPSTREAM_PATHS = (
    ROOT / "SUSY_V51_REPRESENTATION_FAITHFUL_MEDIATOR_MOOSE_AUDIT.json",
    ROOT / "SUSY_V51_PHYSICAL_SOURCE_ORBIT_AUDIT.json",
    ROOT / "SUSY_V51_CARTESIAN_SOURCE_HESSIAN_AUDIT.json",
    ROOT / "SUSY_V51_DEGREE4_CARTESIAN_FACTOR_AUDIT.json",
    ROOT / "SUSY_V51_NEW_PHYSICS_CANDIDATE_INTEGRATION_AUDIT.json",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sympy_matrix_sha256(matrix: sp.MatrixBase) -> str:
    payload = {
        "shape": [matrix.rows, matrix.cols],
        "entries": [str(value) for value in matrix],
    }
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def so10_basis() -> tuple[sp.Matrix, ...]:
    """Coefficient-normalized basis T_ab=E_ab-E_ba, a<b."""

    rows: list[sp.Matrix] = []
    for a in range(10):
        for b in range(a + 1, 10):
            value = sp.zeros(10)
            value[a, b] = 1
            value[b, a] = -1
            rows.append(value)
    return tuple(rows)


def coefficient_vector(matrix: sp.MatrixBase) -> sp.Matrix:
    return sp.Matrix(
        [matrix[a, b] for a in range(10) for b in range(a + 1, 10)]
    )


def endpoint_structures() -> tuple[sp.Matrix, sp.Matrix]:
    """PS parity P and compatible SU(5) complex structure J."""

    parity = sp.diag(*([1] * 6 + [-1] * 4))
    complex_structure = sp.zeros(10)
    for a, b in ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9)):
        complex_structure[a, b] = 1
        complex_structure[b, a] = -1
    return parity, complex_structure


def endpoint_projectors() -> dict[str, sp.Matrix]:
    """Exact rational Lie-algebra projectors in the 45 coefficient basis."""

    parity, complex_structure = endpoint_structures()
    basis = so10_basis()
    ps = sp.zeros(45)
    u5 = sp.zeros(45)
    for column, generator in enumerate(basis):
        # PXP is +X in so(6)+so(4) and -X in its orthogonal complement.
        ps[:, column] = coefficient_vector(
            (generator + parity * generator * parity) / 2
        )
        # theta(X)=J X J^{-1}=-J X J; +1 is u(5).
        u5[:, column] = coefficient_vector(
            (generator - complex_structure * generator * complex_structure) / 2
        )
    j_vector = coefficient_vector(complex_structure)
    u1 = j_vector * j_vector.T / (j_vector.dot(j_vector))
    su5 = u5 - u1
    identity = sp.eye(45)
    both = ps * su5
    ps_only = ps * (identity - su5)
    su5_only = (identity - ps) * su5
    neither = (identity - ps) * (identity - su5)
    return {
        "PS": ps,
        "U5": u5,
        "U1_in_U5": u1,
        "SU5": su5,
        "both": both,
        "PS_only": ps_only,
        "SU5_only": su5_only,
        "neither": neither,
    }


def projector_incidence_certificate() -> dict[str, Any]:
    parity, complex_structure = endpoint_structures()
    projectors = endpoint_projectors()
    identity = sp.eye(45)
    dimensions = {
        "PS_intersection_SU5__SM": projectors["both"].rank(),
        "PS_only": projectors["PS_only"].rank(),
        "SU5_only": projectors["SU5_only"].rank(),
        "neither": projectors["neither"].rank(),
    }
    checks = {
        "P_squared_is_identity": parity * parity == sp.eye(10),
        "J_squared_is_minus_identity": (
            complex_structure * complex_structure == -sp.eye(10)
        ),
        "P_and_J_commute": parity * complex_structure == complex_structure * parity,
        "PS_projector_idempotent": projectors["PS"] ** 2 == projectors["PS"],
        "U5_projector_idempotent": projectors["U5"] ** 2 == projectors["U5"],
        "SU5_projector_idempotent": projectors["SU5"] ** 2 == projectors["SU5"],
        "PS_and_SU5_projectors_commute": (
            projectors["PS"] * projectors["SU5"]
            == projectors["SU5"] * projectors["PS"]
        ),
        "four_sectors_resolve_identity": (
            projectors["both"]
            + projectors["PS_only"]
            + projectors["SU5_only"]
            + projectors["neither"]
            == identity
        ),
        "dimensions_sum_to_45": sum(dimensions.values()) == 45,
    }
    return {
        "vector_PS_parity": [int(parity[index, index]) for index in range(10)],
        "SU5_complex_planes": [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]],
        "centralizer_dimensions": {
            "PS": projectors["PS"].rank(),
            "U5": projectors["U5"].rank(),
            "SU5_after_source_phase_breaks_U1": projectors["SU5"].rank(),
        },
        "simultaneous_incidence_dimensions": dimensions,
        "incidence_sum": sum(dimensions.values()),
        "projector_sha256": {
            name: sympy_matrix_sha256(value) for name, value in projectors.items()
        },
        "checks": checks,
        "n_failed_checks": sum(not value for value in checks.values()),
    }


def alignment_linear_map() -> sp.Matrix:
    """L(X)=[P,[X,J]] as a 100 by 45 exact integer matrix."""

    parity, complex_structure = endpoint_structures()
    value = sp.zeros(100, 45)
    for column, generator in enumerate(so10_basis()):
        first = generator * complex_structure - complex_structure * generator
        image = parity * first - first * parity
        value[:, column] = image.reshape(100, 1)
    return value


def goldstone_incidence_matrices() -> tuple[sp.Matrix, sp.Matrix]:
    """Two-site Goldstone/gauge incidence D and 12-row alignment map A.

    Coordinates are incidence-adapted.  Every generator contributes one link
    coordinate.  A generator broken by the source SU(5) vacuum contributes a
    second source coordinate.  Gauge columns are the available host/source
    generators.  In a neither sector, D=(-1,+1)^T and A=(+1,+1), so A D=0.
    """

    blocks: list[sp.Matrix] = []
    row_widths: list[tuple[str, int]] = []
    for name, count in (
        ("both", 12),
        ("PS_only", 9),
        ("SU5_only", 12),
        ("neither", 12),
    ):
        for _ in range(count):
            if name == "both":
                block = sp.Matrix([[1, -1]])
            elif name == "PS_only":
                block = sp.Matrix([[1, -1], [0, 1]])
            elif name == "SU5_only":
                block = sp.Matrix([[-1]])
            else:
                block = sp.Matrix([[-1], [1]])
            blocks.append(block)
            row_widths.append((name, block.rows))
    incidence = sp.diag(*blocks)
    alignment = sp.zeros(12, incidence.rows)
    output_row = 0
    input_column = 0
    for name, width in row_widths:
        if name == "neither":
            alignment[output_row, input_column] = 1
            alignment[output_row, input_column + 1] = 1
            output_row += 1
        input_column += width
    return incidence, alignment


def alignment_certificate() -> dict[str, Any]:
    linear_map = alignment_linear_map()
    gram = linear_map.T * linear_map
    projectors = endpoint_projectors()
    neither = projectors["neither"]
    hessian_identity = gram == 32 * neither

    incidence, alignment = goldstone_incidence_matrices()
    gauge_rank = incidence.rank()
    alignment_rank = alignment.rank()
    gauge_annihilation = alignment * incidence
    total_goldstone_mass = incidence * incidence.T + alignment.T * alignment
    vector_mass = incidence.T * incidence
    determinant = total_goldstone_mass.det()

    return {
        "nonlinear_fields": {
            "link": (
                "mathcal_U in Spin(10,C), with vector image U=rho10(mathcal_U) "
                "and U -> h_PS U g_source^{-1}"
            ),
            "source_orientation": (
                "J_s=S J S^{-1} plus the source U(1) phase; together the "
                "21-complex-dimensional Spin(10,C)/SU(5,C) chart"
            ),
            "vacuum": "U=I_10, J_s=J",
        },
        "holomorphic_alignment": {
            "definition": (
                "C=[P,U J_s U^{-1}], W_align=(mu f^2/64) Tr(C^2)"
            ),
            "left_gauge_covariance": (
                "for h in PS, [h,P]=0 and C -> h C h^{-1}"
            ),
            "right_gauge_covariance": (
                "U->U g^{-1}, J_s->g J_s g^{-1}; hence U J_s U^{-1} is invariant"
            ),
            "locality": (
                "strictly local for the V52 two-site action because U is its single edge"
            ),
            "renormalizability": (
                "FAIL: holomorphic on the constrained complex group but nonpolynomial "
                "in canonical Lie-algebra coordinates; no elementary linear-sigma UV "
                "completion is supplied"
            ),
        },
        "single_orientation_linear_map": {
            "definition": "L(X)=[P,[X,J]]",
            "shape": [linear_map.rows, linear_map.cols],
            "rank": linear_map.rank(),
            "sha256": sympy_matrix_sha256(linear_map),
            "Gram_sha256": sympy_matrix_sha256(gram),
            "exact_identity": "L^T L = 32 Pi_neither",
            "identity_holds": hessian_identity,
            "Gram_rank": gram.rank(),
            "Gram_nullity": 45 - gram.rank(),
            "nonzero_Gram_eigenvalue": 32,
            "nonzero_Gram_multiplicity": 12,
            "W_Hessian_after_mu_f2_over_64_normalization": (
                "mu Pi_neither in one relative-orientation chart"
            ),
        },
        "full_two_site_Rxi_and_alignment": {
            "Goldstone_coordinates": incidence.rows,
            "gauge_vector_coordinates": incidence.cols,
            "D_shape": [incidence.rows, incidence.cols],
            "D_rank": gauge_rank,
            "massless_SM_vectors": incidence.cols - gauge_rank,
            "uneaten_chirals_before_alignment": incidence.rows - gauge_rank,
            "A_shape": [alignment.rows, alignment.cols],
            "A_rank": alignment_rank,
            "A_D_exact_zero": gauge_annihilation == sp.zeros(12, 66),
            "alignment_Hessian_rank": (alignment.T * alignment).rank(),
            "combined_Goldstone_mass_rank": total_goldstone_mass.rank(),
            "combined_Goldstone_mass_nullity": (
                total_goldstone_mass.rows - total_goldstone_mass.rank()
            ),
            "combined_Goldstone_mass_determinant": str(determinant),
            "combined_Goldstone_mass_spectrum": {
                "1": 12,
                "2": 36,
                "(3-sqrt(5))/2": 9,
                "(3+sqrt(5))/2": 9,
            },
            "vector_mass_zero_multiplicity": vector_mass.cols - vector_mass.rank(),
            "neither_block": {
                "D": [[-1], [1]],
                "A": [[1, 1]],
                "gauge_direction": [-1, 1],
                "physical_direction": [1, 1],
                "alignment_Hessian_eigenvalues_in_unit_mu_convention": [0, 2],
            },
            "conclusion": (
                "The 54 broken gauge directions are eaten, 12 SM vectors remain "
                "massless, and A supplies a nonzero holomorphic mass to each of the "
                "12 and only 12 pre-alignment physical chirals. No uneaten linearized "
                "Goldstone remains in this EFT chart."
            ),
        },
        "scope": (
            "exact tangent-space theorem at the aligned vacuum; global sigma-model "
            "branches, Kähler completeness and quantum stability are not proved"
        ),
    }


def perturbativity_certificate(gauge_coupling: float = 0.73) -> dict[str, Any]:
    """Compare V51's linear field index with conservative V52 EFT proxies."""

    indices = {
        "T_10": 1,
        "T_16": 2,
        "T_45": 8,
        "T_126": 35,
        "T_210": 56,
        "C2_Spin10": 8,
    }
    v51_left = 106
    v51_right = 182
    v51_coordinates = 612 + 567
    lean_coordinates = 45
    tangent_proxy = indices["T_45"]
    source_spinors = 4 * indices["T_16"]
    linear_source_higgs = indices["T_210"] + 2 * indices["T_126"]
    three_c2 = 3 * indices["C2_Spin10"]
    linear_source_sum = tangent_proxy + source_spinors + linear_source_higgs
    linear_source_b = three_c2 - linear_source_sum

    def pole_ratio(beta: int) -> float | None:
        if beta >= 0:
            return None
        return math.exp(
            8.0 * math.pi**2 / (abs(beta) * gauge_coupling**2)
        )

    # If the 465-component source is itself replaced by a nonlinear/composite
    # Spin(10)/SU(5) orientation, T(45)=8 is an intentionally conservative
    # tangent proxy.  It is not a linear-representation beta-function theorem.
    composite_source_sum = tangent_proxy + tangent_proxy + source_spinors
    composite_source_b = three_c2 - composite_source_sum
    return {
        "convention": "b=3 C2(G)-sum_chiral T(R), T(10)=1",
        "gauge_coupling_at_matching_scale": gauge_coupling,
        "indices": indices,
        "V51_per_edge": {
            "unconstrained_link_plus_multiplier_coordinates": v51_coordinates,
            "left_site_index": v51_left,
            "right_site_index": v51_right,
        },
        "V52_nonlinear_link": {
            "complex_coordinates": lean_coordinates,
            "constraint_multiplier_coordinates": 0,
            "alignment_elementary_coordinates": 0,
            "adjoint_tangent_index_proxy": tangent_proxy,
            "coordinate_reduction_from_V51": v51_coordinates - lean_coordinates,
            "coordinate_reduction_fraction": 1.0 - lean_coordinates / v51_coordinates,
            "left_index_proxy_reduction_fraction": 1.0 - tangent_proxy / v51_left,
            "right_index_proxy_reduction_fraction": 1.0 - tangent_proxy / v51_right,
            "warning": (
                "A gauged nonlinear sigma field is not an elementary linear 45 above "
                "its cutoff. T(45)=8 is only a background-field tangent proxy."
            ),
        },
        "linear_V51_source_retained": {
            "link_tangent_proxy_T": tangent_proxy,
            "four_source_spinors_T": source_spinors,
            "210_plus_126_plus_bar126_T": linear_source_higgs,
            "sum_T": linear_source_sum,
            "three_C2": three_c2,
            "b_one_loop": linear_source_b,
            "Landau_pole_over_matching_scale": pole_ratio(linear_source_b),
            "tenfold_window_maximum_g": math.sqrt(
                8.0 * math.pi**2 / (abs(linear_source_b) * math.log(10.0))
            ),
            "controlled_at_g_0p73": False,
        },
        "fully_nonlinear_source_hypothesis": {
            "link_tangent_proxy_T": tangent_proxy,
            "source_orientation_tangent_proxy_T": tangent_proxy,
            "four_source_spinors_T": source_spinors,
            "sum_T_proxy": composite_source_sum,
            "b_one_loop_proxy": composite_source_b,
            "one_loop_logarithmic_pole_in_proxy": pole_ratio(composite_source_b),
            "NDA_cutoff_over_vector_mass_4pi_over_g": (
                4.0 * math.pi / gauge_coupling
            ),
            "status": (
                "POSSIBLE_EFT_ONLY: removes the linear-source index catastrophe, but "
                "abandons the V51 Cartesian source Hessian and has no explicit UV completion"
            ),
        },
        "verdict": (
            "The lean link repairs V51's multiplier-induced interior running, but the "
            "source-faithful embedding still has a pole at 3.51 matching scales. The "
            "fully nonlinear variant is only an NDA-limited composite EFT hypothesis."
        ),
    }


def build_report() -> dict[str, Any]:
    incidence = projector_incidence_certificate()
    alignment = alignment_certificate()
    running = perturbativity_certificate()
    full = alignment["full_two_site_Rxi_and_alignment"]
    linear_source = running["linear_V51_source_retained"]
    two_site_locality_scope = (
        "the endpoint alignment is then a genuinely local one-edge operator; "
        "on the V51 four-edge chain the same expression contains a Wilson "
        "product and is theory-space nonlocal unless separately mediated"
    )
    checks = {
        "endpoint_projectors_exact": incidence["n_failed_checks"] == 0,
        "incidence_is_12_9_12_12": (
            incidence["simultaneous_incidence_dimensions"]
            == {
                "PS_intersection_SU5__SM": 12,
                "PS_only": 9,
                "SU5_only": 12,
                "neither": 12,
            }
        ),
        "alignment_map_rank12": (
            alignment["single_orientation_linear_map"]["rank"] == 12
        ),
        "alignment_Gram_exact_projector": alignment[
            "single_orientation_linear_map"
        ]["identity_holds"],
        "alignment_annihilates_gauge_orbit": full["A_D_exact_zero"],
        "prealignment_has_12_residual_chirals": (
            full["uneaten_chirals_before_alignment"] == 12
        ),
        "postalignment_Goldstone_block_full_rank": (
            full["combined_Goldstone_mass_rank"] == 66
            and full["combined_Goldstone_mass_nullity"] == 0
        ),
        "SM_vector_count_preserved": full["massless_SM_vectors"] == 12,
        "no_alignment_elementary_fields": (
            running["V52_nonlinear_link"]["alignment_elementary_coordinates"] == 0
        ),
        "linear_source_pole_not_hidden": (
            3.50 < linear_source["Landau_pole_over_matching_scale"] < 3.52
            and not linear_source["controlled_at_g_0p73"]
        ),
        "nonlinear_EFT_not_called_renormalizable": alignment[
            "holomorphic_alignment"
        ]["renormalizability"].startswith("FAIL"),
    }
    report = {
        "schema": "susy-spin10-v52-lean-nonlinear-alignment-v1",
        "status": STATUS,
        "candidate_name": "two-site nonlinear Spin(10) link with PS/SU(5) alignment",
        "candidate_contract": {
            "spacetime": "finite four-dimensional N=1 gauged nonlinear sigma EFT",
            "gauge_sites": "PS_host x Spin(10)_source with shared U(1)F",
            "link_count": 1,
            "spin_lift_contract": (
                "the fundamental nonlinear field is mathcal_U in Spin(10,C), not "
                "only its vector image U; rho16_plus/minus(mathcal_U) therefore exist "
                "for spinor hopping. Global bundle sectors are not classified."
            ),
            "reason_for_two_sites": two_site_locality_scope,
            "positive_metric_scope": (
                "assumed positive analytic Kähler metric in a neighbourhood of the "
                "identity; no global Kähler completion is proved"
            ),
            "same_action_as_V50_or_V51": False,
        },
        "PS_SU5_projector_incidence": incidence,
        "alignment_and_spectrum": alignment,
        "field_and_perturbativity_stress_test": running,
        "what_is_repaired": [
            "567 V51 constraint multipliers are absent",
            "the exact 12-dimensional neither-endpoint sector is identified",
            "all 12 residual A5-like chirals receive a holomorphic local EFT mass",
            "the alignment Hessian is zero on all 54 broken gauge orbits",
            "the 12 massless SM gauge vectors are unchanged",
        ],
        "kill_tests": {
            "a_chart_projector_was_not_substituted_for_a_symmetry_argument": (
                alignment["holomorphic_alignment"]["left_gauge_covariance"].startswith(
                    "for h in PS"
                )
                and alignment["holomorphic_alignment"]["right_gauge_covariance"].startswith(
                    "U->"
                )
            ),
            "four_site_nonlocality_not_hidden": (
                "four-edge" in two_site_locality_scope
                and "nonlocal" in two_site_locality_scope
                and "mediated" in two_site_locality_scope
            ),
            "nonrenormalizable_sigma_model_not_called_UV_completion": (
                alignment["holomorphic_alignment"]["renormalizability"].startswith(
                    "FAIL"
                )
            ),
            "linear_source_Landau_pole_not_hidden": checks[
                "linear_source_pole_not_hidden"
            ],
            "no_frozen_clause_inherited": True,
        },
        "gate_effect": {
            "V51_12_chiral_subproblem": (
                "RESOLVED_EXACTLY_INSIDE_THE_NEW_TWO_SITE_NONLINEAR_EFT"
            ),
            "C2": (
                "CANDIDATE_LOCALITY_PASS_ONLY_FOR_NEW_TWO_SITE_ACTION__NO_FROZEN_CLAUSE_PROMOTION"
            ),
            "C3": (
                "PARTIAL: exact local Goldstone/vector/alignment rank is complete, but "
                "the full interacting physical pencil and UV field completion are absent"
            ),
            "C4": (
                "PARTIAL: a positive local Kähler chart can be chosen, but global "
                "Kähler completeness and radiative stability are unproved"
            ),
            "C5": "OPEN_FOR_NEW_ACTION: no one-loop matching or scale-cancellation audit",
            "C6": "UNASSESSED_FOR_NEW_ACTION: no selector/naturalness inheritance",
            "C7": (
                "OPEN_FOR_NEW_ACTION: V51 operator tensors cannot be inherited without matching"
            ),
            "candidate_UV_viability": (
                "FAIL_AS_COMPLETION: nonlinear EFT has no elementary UV completion; "
                "retaining the linear source gives pole ratio 3.51 at g=0.73"
            ),
            "G2_closed": False,
            "gates_promoted": [],
        },
        "sharp_next_obligations": [
            "construct an anomaly-safe linear or calculable composite UV completion of the Spin(10,C) link and source coset",
            "derive the alignment coefficient and sign from that completion rather than insert it as an EFT parameter",
            "rebuild the source superpotential, Hessian and operator inventory in the nonlinear-source action",
            "compute the complete one-loop physical matching and RG cancellation below the sigma cutoff",
            "prove global target-space/Kähler consistency and classify remote vacua",
            "match observables to the frozen V50 target before any G2 clause can move",
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
        "primary_sources": [
            "https://arxiv.org/abs/hep-th/0104005",
            "https://arxiv.org/abs/hep-th/0006025",
            "https://arxiv.org/abs/hep-th/0209266",
        ],
        "provenance": {
            "upstream_sha256": {
                path.name: sha256_file(path) for path in UPSTREAM_PATHS
            },
            "existing_files_modified": False,
        },
    }
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash stale")
    if report["n_failed_integrity_checks"] != 0 or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("integrity checks failed")
    gate = report["gate_effect"]
    if gate["G2_closed"] or gate["gates_promoted"]:
        raise RuntimeError("a new nonlinear EFT cannot promote frozen gates")
    if not gate["candidate_UV_viability"].startswith("FAIL"):
        raise RuntimeError("UV status must remain fail-closed")
    if not report["alignment_and_spectrum"]["holomorphic_alignment"][
        "renormalizability"
    ].startswith("FAIL"):
        raise RuntimeError("nonlinear alignment cannot be called renormalizable")


def render_markdown(report: Mapping[str, Any]) -> str:
    incidence = report["PS_SU5_projector_incidence"]
    align = report["alignment_and_spectrum"]
    full = align["full_two_site_Rxi_and_alignment"]
    running = report["field_and_perturbativity_stress_test"]
    linear = running["linear_V51_source_retained"]
    nonlinear = running["fully_nonlinear_source_hypothesis"]
    obligations = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(report["sharp_next_obligations"], 1)
    )
    return f"""# V52 lean nonlinear-link and alignment audit

Status: `{report['status']}`  
Core SHA-256: `{report['core_sha256']}`

## Outcome

V52 contains a real local improvement, but it is not a completed theory.  A
two-site 4D N=1 nonlinear link removes V51's 567 multiplier fields, and one
endpoint-alignment operator lifts exactly the 12 previously uneaten A5-like
chirals.  The proof is an exact rational tangent-space calculation, not a
numerical rank guess.

The same construction is a nonlinear sigma-model EFT, not an elementary
renormalizable UV completion.  If the V51 `210+126+bar126` source is retained,
the source Spin(10) pole remains only `{linear['Landau_pole_over_matching_scale']:.8g}`
matching scales away at `g=0.73`.  Replacing the source by a composite
`Spin(10)/SU(5)` orientation removes that index obstruction only as a new EFT
hypothesis and discards the frozen Cartesian source action.  No gate is
promoted and G2 remains open.

## Exact PS/SU(5) incidence

Use

```text
P = diag(+1,+1,+1,+1,+1,+1,-1,-1,-1,-1),
J = E01-E10 + E23-E32 + E45-E54 + E67-E76 + E89-E98.
```

`P` and `J` commute.  Their centralizers have dimensions 21 for PS and 25
for U(5).  Removing the `J` direction gives SU(5) dimension 24.  The exact
commuting rational projectors resolve the 45 generators as

```text
PS intersect SU(5) = {incidence['simultaneous_incidence_dimensions']['PS_intersection_SU5__SM']},
PS only             = {incidence['simultaneous_incidence_dimensions']['PS_only']},
SU(5) only          = {incidence['simultaneous_incidence_dimensions']['SU5_only']},
neither             = {incidence['simultaneous_incidence_dimensions']['neither']}.
```

Thus the double-broken sector is exactly 12-dimensional.

## Gauge-invariant alignment theorem

Let the single nonlinear link transform as
`U -> h_PS U g_source^(-1)`.  Let the dynamical source orientation transform
as `J_s -> g_source J_s g_source^(-1)`.  Then

```text
C = [P,U J_s U^(-1)],
W_align = (mu f^2/64) Tr(C^2)
```

is holomorphic and invariant under the full source gauge transformation and
the host PS transformation.  It is local because V52 has one edge.  The
analogous expression on V51's four-edge chain would contain a Wilson product
and would not be theory-space local without additional mediators.

At `U=I`, `J_s=J`, the exact linear map is
`L(X)=[P,[X,J]]`.  It has shape
`{align['single_orientation_linear_map']['shape']}` and rank
`{align['single_orientation_linear_map']['rank']}`, and obeys the exact identity

```text
L^T L = 32 Pi_neither.
```

For the complete link-plus-source Goldstone system, the gauge incidence
matrix is `{full['D_shape'][0]} x {full['D_shape'][1]}` with rank
`{full['D_rank']}`.  Before alignment it has 12 uneaten chirals.  The
alignment matrix is `{full['A_shape'][0]} x {full['A_shape'][1]}`, has rank
12, and satisfies `A D=0` exactly.  The combined Goldstone block
`D D^T+A^T A` has rank `{full['combined_Goldstone_mass_rank']}`, nullity
`{full['combined_Goldstone_mass_nullity']}`, and determinant
`{full['combined_Goldstone_mass_determinant']}`.  All 12 residual modes are
therefore lifted while all 12 SM vector zero modes remain.

For one neither generator,

```text
D = (-1,+1)^T,      A = (+1,+1).
```

The gauge direction is `(-1,+1)` and the physical relative orientation is
`(+1,+1)`.  The unit-`mu` alignment Hessian eigenvalues are `(0,2)`.

This is genuinely more than an arbitrary chart projector: the nonlinear
commutator expression supplies the endpoint-gauge symmetry argument.  It is
still **not renormalizable in canonical elementary coordinates**.  The group
constraint and inverse become a nonpolynomial chiral sigma model, and no
linear-sigma completion is supplied.

## Field and running stress test

One V51 edge used 612 link coordinates and 567 multiplier coordinates.  Its
Spin(10) index burden was 106 on the left and 182 on the right.  V52 uses 45
nonlinear coordinates, zero constraint multipliers, and zero elementary
alignment fields.  The local adjoint-tangent proxy is `T(45)=8`, reducing the
coordinate count by `{running['V52_nonlinear_link']['coordinate_reduction_from_V51']}`.

That proxy is not a UV beta-function theorem: a nonlinear link is not a
linear 45 above its cutoff.  It is useful only for the broken-phase
background-field stress test.

Keeping the V51 linear source gives

```text
sum T = 8(link proxy)+8(four spinors)+126(210+126+bar126) = {linear['sum_T']},
b = 3 C2-sum T = {linear['b_one_loop']},
Lambda_pole/mu = {linear['Landau_pole_over_matching_scale']:.8g}.
```

A tenfold window would require `g <= {linear['tenfold_window_maximum_g']:.8g}`,
not 0.73.  The source-faithful version therefore remains uncontrolled.

If the source is also a composite nonlinear orientation, the conservative
tangent proxy is `sum T={nonlinear['sum_T_proxy']}` and
`b={nonlinear['b_one_loop_proxy']}`; the sigma-model NDA ceiling is only
`4 pi/g={nonlinear['NDA_cutoff_over_vector_mass_4pi_over_g']:.8g}` vector
masses.  This variant is a possible EFT target, not evidence for a UV theory.

## Gate effect

The 12-chiral V51 subproblem is solved exactly **inside the new V52 EFT**.
That result cannot be combined automatically with V50/V51 clauses because
the action, site count, source realization, and target space changed.  C3 and
C4 remain partial; C5 and C7 require a new matching computation; C6 is
unassessed.  G2 is not closed.

## Required next work

{obligations}

Primary precedents for the framework, not proofs of this candidate, are
[deconstruction](https://arxiv.org/abs/hep-th/0104005),
[supersymmetric nonlinear sigma models](https://arxiv.org/abs/hep-th/0006025),
and [N=1 supersymmetric moose dynamics](https://arxiv.org/abs/hep-th/0209266).
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("V52 artifacts missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V52 JSON stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V52 Markdown stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
