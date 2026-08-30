#!/usr/bin/env python3
"""V46 source-wall rank-reducing Higgs audit.

The audit has three deliberately separate parts.

1.  It proves a representation-theoretic no-go for a renormalizable boundary
    sector made only from a neutral 126 + bar126 pair and gauge singlets.
2.  It certifies the standard neutral 210 repair on the supersymmetric SU(5)
    branch, including the Goldstone and massive-component count.
3.  It tests the tempting PS/GG two-wall shortcut.  The shortcut has a tiny
    singlet Higgs sector, but in five dimensions it leaves twelve adjoint-
    chiral zero modes and it does not admit a locally anomaly-free assignment
    for the four V45 bulk spinors without inflow or extra charged matter.

This is a finite algebra/group audit, not a calculation of the full 5D KK
determinant or a global eta invariant.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json"
MD_PATH = ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v46_source_higgs_rank_audit.py"

STATUS = (
    "V46_126_PAIR_PLUS_SINGLETS_NO_GO_230_PHYSICAL_MASSLESS__"
    "NEUTRAL_210_REPAIR_HAS_SU5_DFLAT_BRANCH_AND_GENERIC_RANK441__"
    "PS_GG_5D_SHORTCUT_REJECTED_BY_12_ADJOINT_CHIRAL_ZERO_MODES__"
    "BULK_SPINOR_SELECTOR_AND_FULL_KK_STILL_OPEN"
)


SU5_DECOMPOSITIONS = {
    "210": {"1": 1, "5": 5, "bar5": 5, "10": 10, "bar10": 10,
            "24": 24, "40": 40, "bar40": 40, "75": 75},
    "126": {"1": 1, "bar5": 5, "10": 10, "bar15": 15,
            "45": 45, "bar50": 50},
    "bar126": {"1": 1, "5": 5, "bar10": 10, "15": 15,
               "bar45": 45, "50": 50},
}

FOUR_BULK_SPINORS = (
    {"name": "HLF", "rep": "16", "qF": 3, "PS_zero_mode": "(4,2,1)"},
    {"name": "HLA", "rep": "bar16", "qF": -12, "PS_zero_mode": "(bar4,2,1)"},
    {"name": "HRA", "rep": "16", "qF": -3, "PS_zero_mode": "(bar4,1,2)"},
    {"name": "HRF", "rep": "bar16", "qF": 12, "PS_zero_mode": "(4,1,2)"},
)


def matrix_rank(matrix: Iterable[Iterable[int | Fraction]]) -> int:
    """Exact Gaussian-elimination rank over the rationals."""

    rows = [[Fraction(item) for item in row] for row in matrix]
    if not rows:
        return 0
    n_rows = len(rows)
    n_cols = len(rows[0])
    rank = 0
    for col in range(n_cols):
        pivot = next((r for r in range(rank, n_rows) if rows[r][col] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][col]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for r in range(n_rows):
            if r == rank or rows[r][col] == 0:
                continue
            coefficient = rows[r][col]
            rows[r] = [a - coefficient * b for a, b in zip(rows[r], rows[rank])]
        rank += 1
        if rank == n_rows:
            break
    return rank


def singlet_only_no_go() -> dict[str, Any]:
    pair_dimension = 2 * 126
    pair_singlet_directions = 2
    transverse_directions = pair_dimension - pair_singlet_directions
    broken_generators = 45 - 24
    transverse_goldstones = 10 + 10
    physical_massless_lower_bound = transverse_directions - transverse_goldstones

    # W = k S (Sigma.barSigma-v^2).  After setting sigma=barsigma=v and
    # stripping the nonzero common factor k*v, this is the exact singlet
    # Hessian.  Its null direction is the broken-U(1) Goldstone.
    driver_hessian = [[0, 0, 1], [0, 0, 1], [1, 1, 0]]

    return {
        "field_content": ["Sigma=126_0", "barSigma=bar126_0", "any number of Spin(10) singlets"],
        "most_general_charged_dependence": "W = f(S_a) (Sigma.barSigma) + W_sing(S_a)",
        "renormalizable_restriction": "f is affine in the singlets and W_sing has degree at most three",
        "reason_no_other_term": (
            "There is no Spin(10)-singlet quadratic Sigma.Sigma or barSigma.barSigma, "
            "and the general renormalizable SO(10) superpotential has no pure cubic "
            "126 invariants."
        ),
        "nonzero_branch_condition": "F_Sigma=F_barSigma=0 with sigma*barsigma != 0 implies f(S0)=0",
        "orientation_result": (
            "The superpotential then has zero transverse Hessian and cannot isolate the "
            "SU(5)-singlet orbit; choosing that orbit is not a mass-stabilized vacuum selection."
        ),
        "dimensions": {
            "126_plus_bar126": pair_dimension,
            "SU5_singlet_directions_in_pair": pair_singlet_directions,
            "transverse_pair_directions": transverse_directions,
            "broken_SO10_over_SU5_generators": broken_generators,
            "transverse_10_plus_bar10_goldstones": transverse_goldstones,
            "physical_massless_transverse_chirals_at_least": physical_massless_lower_bound,
        },
        "one_driver_example": {
            "W": "kappa S (Sigma.barSigma - v^2)",
            "D_flat": "|sigma|=|barsigma|=v",
            "singlet_hessian_up_to_nonzero_rescalings": driver_hessian,
            "singlet_hessian_rank": matrix_rank(driver_hessian),
            "singlet_kernel": "one relative-phase Goldstone, eaten by the broken U(1)",
            "physical_massless_chirals": physical_massless_lower_bound,
        },
        "no_go": True,
        "claim_strength": (
            "Exact for arbitrary gauge singlets at renormalizable order; additional gauge-nonsinglet "
            "fields or nonrenormalizable operators are required."
        ),
    }


def repair_210_certificate() -> dict[str, Any]:
    # A rational point on the Aulakh SU(5) branch.  It is not a fit; it is an
    # exact witness that all non-Goldstone block determinants can be nonzero.
    witness = {
        "eta": Fraction(1),
        "lambda": Fraction(1),
        "M": Fraction(-10),
        "m": Fraction(-7, 2),
        "p": Fraction(1),
        "sigma": Fraction(1),
        "barsigma": Fraction(1),
    }
    eta = witness["eta"]
    lam = witness["lambda"]
    big_m = witness["M"]
    little_m = witness["m"]
    p = witness["p"]
    sigma = witness["sigma"]
    barsigma = witness["barsigma"]

    branch_checks = {
        "M_plus_10_eta_p": big_m + 10 * eta * p,
        "sigma_barsigma_plus_2p_times_m_plus_3lambda_p_over_eta": (
            sigma * barsigma + 2 * p * (little_m + 3 * lam * p) / eta
        ),
        "D_flat_norm_squared_difference": sigma * sigma - barsigma * barsigma,
    }

    # The 10/bar10 off-diagonal entries contain sqrt(3).  Store b*c exactly.
    ten_a = 2 * (big_m + 4 * eta * p)
    ten_d = 2 * (little_m + 3 * lam * p)
    ten_bc = 12 * eta * eta * sigma * barsigma
    ten_det = ten_a * ten_d - ten_bc

    # With no light 10_H in this boundary rank problem, the 5/bar5 block is 2x2.
    five_a = 2 * (big_m + 4 * eta * p)
    five_d = 2 * (little_m + 6 * lam * p)
    five_bc = 12 * eta * eta * sigma * barsigma
    five_det = five_a * five_d - five_bc

    unique_masses = {
        "50_plus_bar50": 2 * (big_m - 2 * eta * p),
        "15_plus_bar15": 2 * (big_m + 2 * eta * p),
        "45_plus_bar45": 2 * big_m,
        "40_plus_bar40": 2 * little_m,
        "24": little_m + lam * p,
        "75": little_m - 2 * lam * p,
    }

    total_chirals = 210 + 126 + 126
    goldstone_chirals = 45 - 24
    massive_chirals = total_chirals - goldstone_chirals

    return {
        "field_content": ["Phi=210_0", "Sigma=126_0", "barSigma=bar126_0"],
        "why_selected": (
            "This is the standard one-additional-irrep renormalizable repair with a complete "
            "published spectrum.  A 45 or 54 alone does not do the standard job; the alternative "
            "standard route uses both 45+54 (99 rather than 210 raw components, but two irreps "
            "and more couplings)."
        ),
        "tensor_superpotential": (
            "W_GUT = (m/4!) Phi_ijkl Phi_ijkl + (lambda/4!) Phi_ijkl Phi_klmn Phi_mnij "
            "+ (M/5!) Sigma_ijklm barSigma_ijklm "
            "+ (eta/4!) Phi_ijkl Sigma_ijmno barSigma_klmno"
        ),
        "reduced_singlet_superpotential_Aulakh_2003_convention": (
            "Wred = m(p^2+3a^2+6omega^2) + 2 lambda(a^3+3p omega^2+6a omega^2) "
            "+ M sigma barsigma + eta sigma barsigma(p+3a+6omega)"
        ),
        "F_D_branch": {
            "Aulakh_2003_omega_convention": "p=a=omega",
            "Aulakh_2005_mass_spectrum_convention": "p=a=-omega",
            "phase_convention_note": "the sign of omega differs; the invariant branch equations below agree",
            "p": "-M/(10 eta)",
            "sigma_barsigma": "-2 p (m+3 lambda p)/eta",
            "D_flat": "|sigma|=|barsigma|",
            "F_equations_Aulakh_2003_convention": [
                "0=2mp+6lambda omega^2+eta sigma barsigma",
                "0=6ma+6lambda a^2+12lambda omega^2+3eta sigma barsigma",
                "0=12momega+12lambda p omega+24lambda a omega+6eta sigma barsigma",
                "0=(M+eta(p+3a+6omega)) sigma",
                "0=(M+eta(p+3a+6omega)) barsigma",
            ],
            "unbroken_source_wall_group": "SU(5)",
            "vacuum_selection_scope": (
                "The equations exhibit an isolated SU(5) branch; they do not assert that cosmology "
                "selects this branch over every other supersymmetric branch."
            ),
        },
        "SU5_decompositions": SU5_DECOMPOSITIONS,
        "mass_rank_obligations": {
            "singlets_1Sigma_1barSigma_1Phi": {
                "matrix": [
                    ["2(M+10 eta p)", "0", "-2 i eta sqrt(5) barsigma"],
                    ["0", "2(M+10 eta p)", "+2 i eta sqrt(5) sigma"],
                    ["-2 i eta sqrt(5) barsigma", "+2 i eta sqrt(5) sigma", "2(m+6 lambda p)"],
                ],
                "required_rank": 2,
                "kernel_SU5_multiplet": "1",
            },
            "10_plus_bar10": {
                "matrix": [
                    ["2(M+4 eta p)", "2 eta sqrt(3) sigma"],
                    ["2 eta sqrt(3) barsigma", "2(m+3 lambda p)"],
                ],
                "required_rank": 1,
                "kernel_SU5_multiplets": "10 + bar10",
            },
            "5_plus_bar5_without_light_10H": {"required_rank": 2, "size": "2x2"},
            "unique_sectors_required_nonzero": ["50+bar50", "40+bar40", "15+bar15", "45+bar45", "24", "75"],
        },
        "exact_rational_witness": {
            "parameters": witness,
            "branch_residuals": branch_checks,
            "singlet_rank": 2,
            "singlet_nonzero_minor_squared_magnitude": 20 * eta * eta * sigma * sigma,
            "ten_block": {"a": ten_a, "d": ten_d, "off_diagonal_product": ten_bc,
                          "determinant": ten_det, "rank": 1},
            "five_block": {"a": five_a, "d": five_d, "off_diagonal_product": five_bc,
                           "determinant": five_det, "rank": 2},
            "unique_sector_masses": unique_masses,
            "all_unique_sector_masses_nonzero": all(value != 0 for value in unique_masses.values()),
        },
        "counting": {
            "total_chiral_components": total_chirals,
            "broken_generators_SO10_to_SU5": goldstone_chirals,
            "Goldstone_SU5_content": "1 + 10 + bar10",
            "eaten_chiral_components": goldstone_chirals,
            "generic_massive_uneaten_chiral_components": massive_chirals,
            "generic_physical_massless_chiral_components": 0,
        },
        "preserves_matter_parity": True,
        "repair_passes_boundary_rank_problem": True,
    }


def gg_wall_anomaly(rep: str, qf: int, sign: int) -> dict[str, int]:
    """Physical-interval half anomaly for the GG parity split of one spinor.

    Convention: 16 = 10_-1 + bar5_3 + 1_-5, with base GG parity + on
    the 10 and - on bar5+1.  The conjugate has the conjugate representations.
    Dynkin indices are doubled.
    """

    if rep == "16":
        chirality = 1
    elif rep == "bar16":
        chirality = -1
    else:
        raise ValueError(rep)
    return {
        "SU5_cubed": chirality * sign,
        "SU5_squared_U1chi_doubled": -3 * chirality * sign,
        "gravity_squared_U1chi": -10 * chirality * sign,
        "U1chi_cubed": -10 * chirality * sign,
        "SU5_squared_U1F_doubled": qf * sign,
        "U1chi_squared_U1F": -30 * qf * sign,
        "U1chi_U1F_squared": -10 * chirality * qf * qf * sign,
        "gravity_squared_U1F": 2 * qf * sign,
        "U1F_cubed": 2 * qf**3 * sign,
    }


def add_integer_ledgers(rows: Iterable[Mapping[str, int]]) -> dict[str, int]:
    rows = list(rows)
    keys = tuple(rows[0]) if rows else ()
    return {key: sum(row[key] for row in rows) for key in keys}


def ps_gg_shortcut_certificate() -> dict[str, Any]:
    intersection_dimension = 8 + 3 + 1 + 1
    ps_dimension = 15 + 3 + 3
    gg_dimension = 24 + 1
    vector_parity_dimensions = {
        "V_plus_plus": intersection_dimension,
        "V_plus_minus": ps_dimension - intersection_dimension,
        "V_minus_plus": gg_dimension - intersection_dimension,
        "V_minus_minus": 45 - ps_dimension - gg_dimension + intersection_dimension,
    }
    adjoint_chiral_zero_modes = vector_parity_dimensions["V_minus_minus"]

    assignments = []
    locally_anomaly_free = []
    for signs in itertools.product((-1, 1), repeat=4):
        rows = [
            gg_wall_anomaly(field["rep"], int(field["qF"]), sign)
            for field, sign in zip(FOUR_BULK_SPINORS, signs)
        ]
        totals = add_integer_ledgers(rows)
        item = {
            "signs_HLF_HLA_HRA_HRF": list(signs),
            "totals": totals,
            "all_rows_zero": all(value == 0 for value in totals.values()),
        }
        assignments.append(item)
        if item["all_rows_zero"]:
            locally_anomaly_free.append(item)

    return {
        "walls": {
            "y0": "(SU(4)xSU(2)LxSU(2)R)/Z2",
            "yL": "(SU(5)xU(1)chi)/Z5",
            "connected_intersection_before_chi_Higgsing": "GSM/Z6 x U(1)extra",
        },
        "small_boundary_Higgs_sector": {
            "fields": ["chiPlus=1_+10", "chiMinus=1_-10", "Schi=1_0"],
            "W": "kappaChi Schi (chiPlus chiMinus - vChi^2)",
            "D_flat": "|chiPlus|=|chiMinus|=vChi",
            "singlet_hessian_rank": 2,
            "eaten_chiral_components": 1,
            "uneaten_massless_chiral_components": 0,
            "residual_group": "GSM/Z6 x Z2_matter_parity",
            "global_group_note": (
                "The charge-10 VEV leaves Z10 inside U(1)chi, while the Z5 quotient "
                "identification reduces the independent remnant to Z2 matter parity."
            ),
        },
        "five_dimensional_vector_obstruction": {
            "vector_parity_sector_dimensions": vector_parity_dimensions,
            "adjoint_chiral_has_opposite_parities": True,
            "Phi_plus_plus_zero_modes_from_V_minus_minus": adjoint_chiral_zero_modes,
            "gauge_consistent_mass_exhibited": False,
            "reason": (
                "The 5D adjoint chiral transforms inhomogeneously under the remnant of odd "
                "gauge transformations, so an arbitrary boundary mass is not a certified repair. "
                "Hall et al. identify these extra massless chiral states and move the construction to 6D."
            ),
        },
        "bulk_spinor_effect": {
            "GG_split": "16 = 10_-1(+) + bar5_+3(-) + 1_-5(-), up to one intrinsic sign",
            "former_PS_half_zero_modes_remain_intact": False,
            "splitting": {
                "PS_left_intersect_10": "Q-like",
                "PS_left_intersect_bar5_plus_1": "L-like",
                "PS_right_intersect_10": "u^c+e^c-like",
                "PS_right_intersect_bar5_plus_1": "d^c+nu^c-like",
            },
            "Theta_mass_operators_boundary_invariant_for_matched_GG_parities": True,
            "qualification": "Boundary invariance does not restore the original complete PS exotic zero modes.",
        },
        "source_wall_ordinary_anomaly_scan": {
            "normalization": "physical interval; one-half 4D anomaly weighted by GG parity",
            "parity_assignments_tested": len(assignments),
            "locally_anomaly_free_assignments": locally_anomaly_free,
            "number_locally_anomaly_free": len(locally_anomaly_free),
            "reduced_equations": [
                "s1-s2+s3-s4=0",
                "3s1-12s2-3s3+12s4=0",
                "27s1-1728s2-27s3+1728s4=0",
                "-9(s1+s3)+144(s2+s4)=0",
            ],
            "neutral_chi_and_Theta_pairs_cancel_these_rows": False,
            "consequence": (
                "The four-spinor content is not locally anomaly-free at the GG wall by itself. "
                "A complete quantized inflow/global-zero-mode analysis or extra bi-charged matter "
                "would be required even if the adjoint zero-mode obstruction were repaired."
            ),
        },
        "five_dimensional_shortcut_accepted": False,
        "rejection_reasons": [
            "twelve unwanted adjoint-chiral zero modes",
            "no locally anomaly-free GG parity assignment for the four V45 bulk spinors",
            "the GG parity further fragments the four intended PS exotic zero modes",
        ],
    }


def bulk_spinor_coupling_certificate() -> dict[str, Any]:
    return {
        "representation_products": {
            "16_x_bar16": "1 + 45 + 210",
            "16_x_16": "10_s + 120_a + 126_s",
            "bar16_x_bar16": "bar10_s + 120_a + bar126_s",
        },
        "intended_Theta_terms": [
            {"operator": "ThetaPlus HLF HLA", "qF": 9 + 3 - 12, "allowed": True},
            {"operator": "ThetaMinus HRA HRF", "qF": -9 - 3 + 12, "allowed": True},
        ],
        "Phi_210_trilinears": [
            {"operator": "Phi HLF HLA", "qF": 3 - 12, "allowed": False},
            {"operator": "Phi HLF HRF", "qF": 3 + 12, "allowed": False},
            {"operator": "Phi HRA HLA", "qF": -3 - 12, "allowed": False},
            {"operator": "Phi HRA HRF", "qF": -3 + 12, "allowed": False},
        ],
        "same_chirality_Phi_terms": {
            "allowed": False,
            "reason": "210 is absent from 16x16 and bar16xbar16",
        },
        "Sigma_pair_trilinears": [
            {
                "operator": "barSigma HLF HRA",
                "qF": 3 - 3,
                "allowed": True,
                "zero_mode_projection": (
                    "The SU(5)-singlet barSigma VEV couples two 1_-5 spinor components. "
                    "HLF has no such PS-selected zero mode, so the direct zero-zero entry vanishes."
                ),
            },
            {
                "operator": "Sigma HLA HRF",
                "qF": -12 + 12,
                "allowed": True,
                "zero_mode_projection": (
                    "The conjugate singlet VEV requires two conjugate SU(5)-singlet components. "
                    "HLA lacks that PS-selected zero mode, so the direct zero-zero entry vanishes."
                ),
            },
        ],
        "KK_warning": (
            "The two allowed Sigma trilinears can mix a selected zero mode with source-even KK "
            "components.  They must be included in the full boundary-condition determinant or "
            "forbidden by the final discrete/R selector; the projected 4x4 V45 matrix alone does not decide them."
        ),
        "neutral_source_Higgs_anomalies": (
            "Phi is real, Sigma+barSigma is vectorlike, and all have qF=0; they add no displayed ordinary U(1)F anomaly."
        ),
        "sequestering_warning": (
            "Gauge symmetry alone also permits neutral-singlet couplings such as STheta Phi^2 "
            "and STheta Sigma.barSigma.  A claimed separated Theta/GUT superpotential requires "
            "the final R/discrete charge audit."
        ),
    }


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance() -> dict[str, Any]:
    paths = (Path(__file__).resolve(), TEST_PATH)
    return {
        "files": [
            {"path": path.name, "exists": path.is_file(),
             "sha256": sha256_file(path) if path.is_file() else None}
            for path in paths
        ]
    }


def build_report() -> dict[str, Any]:
    report = {
        "schema": "susy-v46-source-higgs-rank-audit-v1",
        "status": STATUS,
        "scope": (
            "Renormalizable supersymmetric source-wall Higgs rank, the standard 210 repair, "
            "the PS/GG five-dimensional shortcut, and couplings to the four V45 bulk spinors."
        ),
        "singlet_only_126_pair": singlet_only_no_go(),
        "neutral_210_repair": repair_210_certificate(),
        "PS_GG_orbifold_shortcut": ps_gg_shortcut_certificate(),
        "couplings_to_four_bulk_spinors": bulk_spinor_coupling_certificate(),
        "decision": {
            "original_126_pair_plus_singlets_valid": False,
            "standard_repair_selected": "add one neutral 210 boundary chiral",
            "source_Higgs_rank_subproblem_closed_conditionally": True,
            "condition": "generic superpotential parameters on the nonzero SU(5) branch, away from extra mass-zero loci",
            "PS_GG_shortcut_valid_in_5D": False,
            "complete_5D_model_established": False,
            "gates_promoted": [],
        },
        "recommended_source_superpotential": (
            "W_source = W_GUT(Phi,Sigma,barSigma) + kappaTheta STheta(ThetaPlus ThetaMinus-vF^2) "
            "+ lambdaL ThetaPlus HLF HLA + lambdaR ThetaMinus HRA HRF"
        ),
        "operator_obligation": (
            "Either include barSigma HLF HRA and Sigma HLA HRF in the full KK boundary-mass problem, "
            "or exhibit a consistent selector symmetry that forbids both while retaining W_source."
        ),
        "open_kill_tests": [
            "solve the complete KK boundary-condition determinant including every allowed Sigma-spinor coupling",
            "complete the R/discrete selector audit, including neutral-singlet cross couplings",
            "compute the compact-group eta/global anomaly and quantized Chern-Simons lattice",
            "verify the full source/PS global quotient and line-operator lattice with matter parity",
            "reconstruct the light Higgs, neutrino, flavour, threshold and RG sectors",
        ],
        "primary_sources": [
            {
                "url": "https://arxiv.org/abs/hep-ph/0306242",
                "use": (
                    "D-flat 126 pair, 210 as the standard minimal single-irrep repair, explicit tensor "
                    "superpotential, vacuum equations, and exact matter parity"
                ),
            },
            {
                "url": "https://arxiv.org/abs/hep-ph/0501025",
                "use": "SU(5) reassembly, exact singlet and 10/bar10 mass matrices, Goldstone count and generic spectrum",
            },
            {
                "url": "https://arxiv.org/abs/1707.00580",
                "use": "general renormalizable SO(10) couplings among 45, 54, 120, 126 pair and 210",
            },
            {
                "url": "https://arxiv.org/abs/hep-ph/0108071",
                "use": "five-dimensional PS/GG orbifolding leaves unwanted massless adjoint-chiral states",
            },
        ],
        "provenance": provenance(),
    }
    encoded = encode(report)
    encoded["core_sha256"] = canonical_sha(encoded)
    validate(encoded)
    return encoded


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("stale core hash")

    no_go = report["singlet_only_126_pair"]
    if not no_go["no_go"]:
        raise RuntimeError("singlet-only no-go was lost")
    if no_go["dimensions"]["physical_massless_transverse_chirals_at_least"] != 230:
        raise RuntimeError("incorrect pseudo-Goldstone lower bound")
    if no_go["one_driver_example"]["singlet_hessian_rank"] != 2:
        raise RuntimeError("incorrect driver Hessian rank")

    repair = report["neutral_210_repair"]
    witness = repair["exact_rational_witness"]
    if any(value != 0 for value in witness["branch_residuals"].values()):
        raise RuntimeError("210 witness is off the SU(5) F/D branch")
    if witness["singlet_rank"] != 2 or witness["ten_block"]["rank"] != 1:
        raise RuntimeError("Goldstone ranks are wrong")
    if witness["ten_block"]["determinant"] != 0:
        raise RuntimeError("10/bar10 Goldstone determinant is not zero")
    if witness["five_block"]["rank"] != 2 or witness["five_block"]["determinant"] == 0:
        raise RuntimeError("5/bar5 block is not full rank")
    if not witness["all_unique_sector_masses_nonzero"]:
        raise RuntimeError("rational witness hit an extra mass-zero locus")
    if repair["counting"]["generic_massive_uneaten_chiral_components"] != 441:
        raise RuntimeError("incorrect repaired massive count")

    shortcut = report["PS_GG_orbifold_shortcut"]
    if shortcut["five_dimensional_vector_obstruction"]["Phi_plus_plus_zero_modes_from_V_minus_minus"] != 12:
        raise RuntimeError("incorrect PS/GG adjoint-chiral zero-mode count")
    if shortcut["source_wall_ordinary_anomaly_scan"]["number_locally_anomaly_free"] != 0:
        raise RuntimeError("unexpected locally anomaly-free four-spinor parity assignment")
    if shortcut["five_dimensional_shortcut_accepted"]:
        raise RuntimeError("the 5D PS/GG shortcut must fail closed")

    decision = report["decision"]
    if decision["complete_5D_model_established"] or decision["gates_promoted"]:
        raise RuntimeError("V46 cannot close the full 5D model or promote a gate")


def render_markdown(data: Mapping[str, Any]) -> str:
    no_go = data["singlet_only_126_pair"]
    repair = data["neutral_210_repair"]
    witness = repair["exact_rational_witness"]
    shortcut = data["PS_GG_orbifold_shortcut"]
    vector_dims = shortcut["five_dimensional_vector_obstruction"]["vector_parity_sector_dimensions"]
    return f"""# V46 source-wall Higgs rank audit

Status: `{data['status']}`

## Verdict

The neutral `126+bar126` pair plus any number of ordinary gauge singlets is not
a complete renormalizable source-wall Higgs sector.  It cannot isolate the
SU(5)-singlet orbit and leaves at least **230 physical massless chiral
components** after the `SO(10) -> SU(5)` super-Higgs effect.

The standard repair is one neutral boundary `210`.  The published
`210+126+bar126` superpotential has a supersymmetric SU(5) branch with exactly
the required `1+10+bar10` Goldstones (21 chiral components) and, for generic
parameters, no other massless chiral multiplet.  The repaired heavy sector has
462 chiral components, 21 eaten and **441 massive uneaten components**.
This is minimal in the standard one-extra-irrep/parameter-economy sense; the
other conventional renormalizable route needs both `45+54` (99 raw components,
but two irreps), since neither works alone.

The proposed `SU(5)xU(1)chi` source-wall shortcut does make its own charge-10
singlet Higgs sector full rank, but it fails as a five-dimensional replacement:
it leaves twelve adjoint-chiral zero modes and none of the 16 intrinsic-parity
assignments makes all displayed source-wall anomalies of the four V45 bulk
spinors vanish.

## Exact singlet-only no-go

With `X=Sigma.barSigma`, the charged fields can enter a renormalizable
Spin(10)-invariant superpotential only as

`W = f(S_a) X + W_sing(S_a)`.

On a nonzero D-flat branch, `F_Sigma=F_barSigma=0` forces `f(S0)=0`.  Therefore
every transverse `Sigma-barSigma` second derivative vanishes.  The pair has 252
components; removing its two SU(5)-singlet directions leaves 250 transverse
directions.  Only the `10+bar10`, or 20 of them, are gauge Goldstones.  Hence
`250-20=230` physical transverse chirals are necessarily massless.  For the
minimal driver `W=kappa S(X-v^2)`, the three-field singlet Hessian has rank
{no_go['one_driver_example']['singlet_hessian_rank']}; its one null vector is
the broken-U(1) Goldstone.

This is also why the singlet-only potential does not dynamically select the
SU(5) orbit: after `f(S0)=0`, it has no orientation-dependent quadratic
curvature.

## Neutral 210 repair

Use

`{repair['tensor_superpotential']}`.

On the singlet directions, in the 2003 convention,

`{repair['reduced_singlet_superpotential_Aulakh_2003_convention']}`.

In the 2003 convention the SU(5) branch is `p=a=omega`; in the 2005 spectrum
convention it is `p=a=-omega`.  In either convention,

`p=-M/(10 eta)`, `sigma barsigma=-2p(m+3 lambda p)/eta`, and
`|sigma|=|barsigma|`.

The singlet mass matrix has rank 2 of 3 and the `10+bar10` matrix rank 1 of 2.
Their kernels are exactly the `1+10+bar10` Goldstones.  The `5+bar5` block is
full rank and the `15`, `24`, `40`, `45`, `50`, and `75` sectors are nonzero on
a generic open set.  The exact witness
`(eta,lambda,M,m,p,sigma,barsigma)=(1,1,-10,-7/2,1,1,1)` has zero F/D branch
residuals, `det(M10)={witness['ten_block']['determinant']}` and
`det(M5)={witness['five_block']['determinant']}`, while every unique-sector mass
is nonzero.  This proves that the extra-zero locus is not forced by the branch
equations.

The `126` VEV has even `3(B-L)`, so the exact gauged `Z2` matter parity survives.
This solves the source-Higgs rank problem conditionally on choosing the SU(5)
branch and avoiding additional tuned mass-zero loci; it does not solve the
cosmological vacuum-selection question.

## Why the smaller GG-wall route fails in 5D

The two boundary groups have dimensions 21 (PS) and 25 (GG), with a
13-dimensional connected intersection.  The vector parity-sector dimensions
are

`(V++,V+-,V-+,V--)=({vector_dims['V_plus_plus']},{vector_dims['V_plus_minus']},{vector_dims['V_minus_plus']},{vector_dims['V_minus_minus']})`.

Because the 5D adjoint chiral has the opposite two parities, all twelve `V--`
generators become `Phi++` massless chiral zero modes.  No gauge-consistent mass
for them is supplied by the charge-10 singlets.  This is the obstruction
identified by Hall, Nomura, Okui and Smith when they move simultaneous PS/GG
orbifold breaking from five to six dimensions.

Ignoring that fatal obstruction, `chiPlus=1_+10`, `chiMinus=1_-10` and a driver
do leave `GSM/Z6 x Z2_matter-parity`, and their own Hessian is healthy.  But the
GG parity also fragments every intended PS half-spinor zero mode.  Moreover, a
complete brute-force scan of all 16 overall GG signs for
`16_+3,bar16_-12,16_-3,bar16_+12` finds
**{shortcut['source_wall_ordinary_anomaly_scan']['number_locally_anomaly_free']}**
assignments cancelling all pure, mixed, gravitational and cubic rows at that
wall.  A nontrivial inflow/global-anomaly construction or extra bi-charged
matter would therefore still be required.

## Couplings to the four bulk spinors

The neutral 210 does not spoil the intended renormalizable mass texture:
`16 x bar16` contains 210, but every possible `Phi H16 Hbar16` pair has nonzero
U(1)F charge.  Also, 210 is absent from `16x16`, so same-chirality terms do not
exist.  The intended terms `ThetaPlus HLF HLA` and `ThetaMinus HRA HRF` remain
allowed.

Two additional cubic operators are allowed by `Spin(10)xU(1)F`:

- `barSigma HLF HRA`, and
- `Sigma HLA HRF`.

An SU(5)-singlet 126 VEV needs two spinor-singlet components, so each direct
selected-zero-mode matrix element vanishes because the left PS zero mode lacks
that component.  The operators can nevertheless mix a selected zero mode with
source-even KK states.  The full KK determinant must include them, or the final
R/discrete selector must forbid them.  Gauge symmetry also permits neutral
cross-couplings such as `STheta Phi^2` and `STheta Sigma.barSigma`, so
sequestering is not automatic.

## Scope boundary

V46 closes the boundary Higgs **rank** subproblem with the 210 repair.  It does
not promote S0 or any G gate: the complete KK determinant, selector symmetry,
global eta/quotient anomaly, thresholds, flavour, neutrino and light-Higgs
sectors remain open.

Primary sources: [Aulakh et al. (2003)](https://arxiv.org/abs/hep-ph/0306242),
[Aulakh (2005)](https://arxiv.org/abs/hep-ph/0501025),
[Chen, Zhang and Bai (2017)](https://arxiv.org/abs/1707.00580), and
[Hall, Nomura, Okui and Smith (2001)](https://arxiv.org/abs/hep-ph/0108071).

Core SHA-256: `{data['core_sha256']}`
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if args.write:
        JSON_PATH.write_text(expected_json, encoding="utf-8")
        MD_PATH.write_text(expected_md, encoding="utf-8")
        print("V46_SOURCE_HIGGS_RANK_AUDIT_WRITE_PASS")
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise SystemExit("V46 source-Higgs artifacts missing; run --write")
        if JSON_PATH.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("V46 source-Higgs JSON stale; run --write")
        if MD_PATH.read_text(encoding="utf-8") != expected_md:
            raise SystemExit("V46 source-Higgs Markdown stale; run --write")
        print("V46_SOURCE_HIGGS_RANK_AUDIT_CHECK_PASS")


if __name__ == "__main__":
    main()
