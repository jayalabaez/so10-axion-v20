#!/usr/bin/env python3
"""V76 correlated-residue and multiplet-realization frontier audit.

V75 found an exact level-four endpoint spectrum but did not construct its
supersymmetric multiplets or its normal-charged mass drivers.  V76 performs
the two next fail-closed tests.

First, a seven-Weyl quotient module cancels the V71 equal-corner
normal/gravitational residue locally.  The cancellation necessarily leaves
``-(5/2) nu ell_i^2`` at each corner.  Because both parent residues have the
same sign, the two endpoint terms add to
``-(5/4) nu (A^2+B^2)``.  This is not the ``nu A B`` class of the V74 bridge;
on two admissible spin witnesses its inverse has quarter periods and is not
in the ordinary determinant or permissive half-index lattice.

Second, every component in the V75 level-four ledger obeys the appropriate
hyper-type or vector/tensor-type quotient-center rule.  That useful component
check is not a six-dimensional multiplet construction.  More decisively, an
everywhere nonzero scalar of normal charge q is a nowhere-zero section of
N^q and hence trivializes N^q.  The q=+/-2 and q=-4 mass drivers therefore
cannot provide a background-covariant full-rank gap on the admissible CP3
normal bundle with c1(N)=H.  Allowing zeros leaves rank-loss divisors and
anomaly matching; locking the normal bundle to a new gauge line changes the
tangential structure and requires a new complete anomaly ledger.

These are exact scoped rejections, not a proof that every interacting or UV
completion is impossible.  No G gate is closed.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
V75_ROUTE_PATH = ROOT / "SUSY_V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT.json"
V75_MASTER_PATH = ROOT / "SUSY_V75_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V76_CORRELATED_RESIDUE_MULTIPLET_REALIZATION_AUDIT.json"
OUT_MD = ROOT / "SUSY_V76_CORRELATED_RESIDUE_MULTIPLET_REALIZATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v76_correlated_residue_multiplet_realization_audit.py"

EXPECTED_CORES = {
    "v75_route": "cd11d5412d0fa9ed28ac1cced7ad8b429bc3ee36b56fcb3cdf418814a6eb96f6",
    "v75_master": "08eff5ecc6e44cd7595c2cdc75de7b28c3d1174fd5cc015031507c5cea9efed2",
}

SCHEMA = "susy_v76_correlated_residue_multiplet_realization_audit_v1"
VERSION = "V76"
DATE = "2026-08-31"
STATUS = (
    "V76_CORRELATED_RESIDUE_MULTIPLET_REALIZATION_AUDIT__V75_ROUTE_AND_MASTER_"
    "CORES_BOUND__UNIVERSAL_CLEAN_QUARTER_HALF_INDEX_NO_GO_EXACT__SEVEN_WEYL_"
    "LOCAL_PARENT_RESIDUE_INVERSE_EXACT__TWO_CORNER_COMMON_SUM_QUARTER_PERIOD_"
    "NO_GO_EXACT__V74_AB_BRIDGE_CANNOT_REPAIR__GENERAL_PURE_GAUGE_TWO_CORNER_"
    "QUARTER_NO_GO_EXACT__TOTAL_TWO_CORNER_FREE_INDEX_ODD_QUARTER_NO_GO_EXACT__"
    "FOUR_LINE_DIAGONAL_CORRELATED_ETA_REPRESENTATIVE_EXACT__V75_LEVEL4_"
    "COMPONENT_CENTERS_PASS__COMPLETE_6D_"
    "MULTIPLETS_ABSENT__MINIMAL_SINGLET_CHIRAL_DRIVERS_EXCLUDED__NORMAL_"
    "CHARGED_NOWHERE_ZERO_DRIVER_"
    "OBSTRUCTION_EXACT__SPIN_GAUGE_LOCKING_CHANGES_ACTION__FULL_EQUIVARIANT_"
    "PARENT_DETERMINANT_SELECTED_OPEN__G1_TO_G8_OPEN"
)


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalized_file_sha(path: Path) -> str:
    """Hash text artifacts independently of checkout LF/CRLF conversion."""
    payload = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def fstr(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def load_bound(path: Path, expected: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    embedded = value.get("core_sha256")
    recomputed = canonical_sha(value)
    if embedded != recomputed:
        raise RuntimeError(
            f"noncanonical parent core for {path.name}: {embedded} != {recomputed}"
        )
    if embedded != expected:
        raise RuntimeError(
            f"bound core mismatch for {path.name}: {embedded} != {expected}"
        )
    return value


def source_catalog() -> list[dict[str, str]]:
    return [
        {
            "title": "Eta-Invariants and Determinant Lines",
            "url": "https://arxiv.org/abs/hep-th/9405012",
            "scope": (
                "eta invariants obey determinant-line variation and gluing laws; "
                "the citation does not construct the missing equivariant orbifold phase"
            ),
        },
        {
            "title": "Anomaly Inflow and the eta-Invariant",
            "url": "https://arxiv.org/abs/1909.08775",
            "scope": (
                "fermion anomalies are encoded by eta-invariant inflow; this supports "
                "the index-period test, not a microscopic V76 endpoint sector"
            ),
        },
        {
            "title": "Anomalies on Six Dimensional Orbifolds",
            "url": "https://arxiv.org/abs/hep-th/0612212",
            "scope": (
                "localized integer residues may be canceled by suitable localized "
                "fermions and remnant gravitational symmetries act on localized fields; "
                "the paper does not supply the present multiplet or mass action"
            ),
        },
        {
            "title": "All Couplings of Minimal Six-dimensional Supergravity",
            "url": "https://arxiv.org/abs/hep-th/0101074",
            "scope": (
                "a 6D (1,0) vector has an SU2R-doublet gaugino, a tensor has an "
                "SU2R-doublet tensorino, and a hyper has an SU2R-singlet hyperino; "
                "complete couplings include all bosonic and fermionic partners"
            ),
        },
        {
            "title": "6D Supersymmetry, Projective Superspace and 4D, N=1 Superfields",
            "url": "https://arxiv.org/abs/hep-th/0508187",
            "scope": (
                "a 6D hypermultiplet requires a complete 4D N=1 superfield pair/CNM "
                "description; an isolated endpoint Weyl ledger is not such a lift"
            ),
        },
        {
            "title": "Quantum Corrections to Non-Abelian SUSY Theories on Orbifolds",
            "url": "https://arxiv.org/abs/hep-th/0602155",
            "scope": (
                "the 6D vector decomposes into V and Sigma with distinct T2/ZN "
                "phases; this fixes the ordinary Z4 projection diagnostic and does "
                "not construct the proposed higher-normal-charge endpoint fields"
            ),
        },
        {
            "title": "Supersymmetric theories with compact extra dimensions in N=1 superfields",
            "url": "https://arxiv.org/abs/hep-th/0106256",
            "scope": (
                "5D vector and hypermultiplets split into opposite-parity N=1 "
                "halves at an orbifold boundary; T2/Z4 has no such fixed wall"
            ),
        },
        {
            "title": "Off-Shell N=(1,0) Linear Multiplets in Six Dimensions",
            "url": "https://arxiv.org/abs/2010.14655",
            "scope": (
                "the off-shell vector-linear density uses full ordinary multiplets; "
                "it does not by itself turn the normal Lorentz connection into an "
                "independent Yang-Mills vector multiplet"
            ),
        },
        {
            "title": "Curvature squared invariants in six-dimensional N=(1,0) supergravity",
            "url": "https://arxiv.org/abs/1808.00459",
            "scope": (
                "supersymmetric curvature invariants require complete Weyl/compensator "
                "multiplets and auxiliary fields, not an isolated normal-curvature term"
            ),
        },
        {
            "title": "Supersymmetry anomalies in N=1 conformal supergravity",
            "url": "https://arxiv.org/abs/1902.06717",
            "scope": (
                "Wess-Zumino consistency ties an R anomaly to a Q-supersymmetry "
                "anomaly; a formal bosonic axion term is not a full superinvariant"
            ),
        },
        {
            "title": "Remarks on the Green-Schwarz terms of six-dimensional supergravity theories",
            "url": "https://arxiv.org/abs/1808.01334",
            "scope": (
                "global 6D Green-Schwarz terms depend on the integral string-charge "
                "lattice and characteristic gravitational coefficient"
            ),
        },
        {
            "title": "The global anomaly of the self-dual field in general backgrounds",
            "url": "https://arxiv.org/abs/1309.6642",
            "scope": (
                "self-dual-field anomalies are refined global theories; adding such a "
                "field changes the complete higher-dimensional anomaly system"
            ),
        },
        {
            "title": "Anomaly of the Electromagnetic Duality of Maxwell Theory",
            "url": "https://arxiv.org/abs/1905.08943",
            "scope": (
                "Maxwell duality can have fractional refined anomalies, but in a "
                "different duality/tangential structure from the required normal-U1 class"
            ),
        },
        {
            "title": "Anomaly Cancellation in Six Dimensions",
            "url": "https://arxiv.org/abs/hep-th/9304104",
            "scope": (
                "six-dimensional anomaly cancellation constrains complete bulk "
                "multiplet spectra and Green-Schwarz couplings"
            ),
        },
    ]


def source_manifest() -> list[dict[str, Any]]:
    return [
        {**row, "record_sha256": canonical_sha(row)} for row in source_catalog()
    ]


def universal_clean_half_index_no_go() -> dict[str, Any]:
    targets = {
        "plus_nu_c2R": Fraction(-1, 4),
        "minus_nu_c2R": Fraction(1, 4),
        "normal_quarter": Fraction(1, 4),
        "inverse_V71_parent_residue": Fraction(5, 8),
    }
    return {
        "status": "EXACT_CP3_HALF_INDEX_NO_GO_FOR_ALL_CLEAN_FREE_FERMION_TARGETS",
        "witness": {
            "manifold": "CP3",
            "spin": True,
            "nu": 1,
            "ell": "5/2",
            "c2R": "-1/4",
            "p1_TCP3": 4,
            "full_diagonal_quotient_bundle": True,
        },
        "target_periods": {name: fstr(value) for name, value in targets.items()},
        "integer_index_membership": {
            name: value.denominator == 1 for name, value in targets.items()
        },
        "half_index_membership": {
            name: (2 * value).denominator == 1 for name, value in targets.items()
        },
        "all_targets_outside_half_index_lattice": all(
            (2 * value).denominator != 1 for value in targets.values()
        ),
        "correlated_allowed_witness": {
            "class": "nu ell^2+nu c2(R)",
            "period": fstr(Fraction(25, 4) - Fraction(1, 4)),
            "integer": True,
        },
        "scope": (
            "honest full-quotient localized complex-Weyl virtual sums and even the "
            "permissive standard signed half-eta image, provided every correlated "
            "gauge, R, flavor and other free-curvature term cancels"
        ),
        "does_not_exclude": [
            "correlated sectors retaining additional free curvature",
            "higher-spin or self-dual anomaly theories",
            "interacting invertible or noninvertible endpoint sectors",
            "a changed tangential structure or parent action",
        ],
    }


def total_two_corner_index_period_no_go() -> dict[str, Any]:
    return {
        "status": "EXACT_REPRESENTATION_INDEPENDENT_TWO_CORNER_ODD_QUARTER_NO_GO",
        "bound_residue_each_corner": "R=-T=-nu(p1+nu^2)/8",
        "common_CP3_witness": {
            "T_each_corner": "5/8",
            "two_corner_residue": "-5/4",
            "fractional_class_mod_Z": "-1/4",
        },
        "spin_cubic_threefold_witness": {
            "integrals": {"nu3": 3, "nu_p1": -12},
            "T_each_corner": "-9/8",
            "two_corner_residue": "9/4",
            "fractional_class_mod_Z": "1/4",
        },
        "allowed_addition_lattices": {
            "finite_honest_localized_Weyl_endpoint_indices": "Z",
            "ordinary_quantized_common_K_bridges_and_counterterms": "Z",
            "permissive_standard_signed_half_eta_extensions": "(1/2)Z",
        },
        "integer_additions_can_cancel": False,
        "half_index_additions_can_cancel": False,
        "V75_level4_endpoint_plus_bridge_common_period": 0,
        "V75_level4_changes_odd_quarter_class": False,
        "scope": (
            "all finite ordinary localized Weyl determinants, ordinary quantized "
            "common-K bridges/counterterms and standard half-eta copies on the "
            "unchanged parent backgrounds, independent of how their gauge, R or "
            "flavor curvature is distributed"
        ),
        "not_excluded": [
            "quarter/eighth-refined self-dual or higher-spin anomaly theories",
            "interacting invertible or noninvertible endpoint physics",
            "a changed parent determinant, tangential structure or UV regulator",
            "bulk flux/cap data that changes the globally admissible background ledger",
        ],
        "ordinary_free_field_two_corner_completion_exists": False,
    }


def four_line_diagonal_eta_representative() -> dict[str, Any]:
    cp3_diagonal = Fraction(13, 4)
    cp3_spectator = Fraction(-1, 4)
    cubic_diagonal = Fraction(39, 4)
    cubic_spectator = Fraction(5, 4)
    return {
        "status": "PASS_EXACT_CORRELATED_FOUR_LINE_INDEX_REPRESENTATIVE",
        "honest_lines": "c_(eps,tau)=(nu+eps A+tau B)/2 for eps,tau=+/-1",
        "sum_of_indices": (
            "sum I(c_eps_tau)=(1/4)nu(A^2+B^2)+"
            "nu(nu^2-p1)/12"
        ),
        "target_diagonal_quarter": "D/4=(1/4)nu(A^2+B^2)",
        "forced_spectator": "S_eta=nu(nu^2-p1)/12",
        "coefficient_derivation": {
            "sum_c": "2nu",
            "sum_c_cubed": "nu^3/2+(3/2)nu(A^2+B^2)",
        },
        "witness_periods": {
            "CP3": {
                "diagonal": fstr(cp3_diagonal),
                "S_eta": fstr(cp3_spectator),
                "total_index": fstr(cp3_diagonal + cp3_spectator),
            },
            "spin_cubic_threefold": {
                "diagonal": fstr(cubic_diagonal),
                "S_eta": fstr(cubic_spectator),
                "total_index": fstr(cubic_diagonal + cubic_spectator),
            },
        },
        "total_is_honest_integral_index": True,
        "pure_diagonal_quarter_refinement_constructed": False,
        "standard_neutral_free_inverse_spectator_exists": False,
        "interpretation": (
            "the desired diagonal quarter has an honest correlated representative, "
            "but stripping its forced S_eta spectator requires physics outside the "
            "ordinary/standard-half free determinant image"
        ),
    }


SEVEN_WEYL_ROWS: tuple[tuple[int, int, Fraction, str], ...] = (
    (1, 5, Fraction(-3, 2), "A_plus"),
    (1, -5, Fraction(-3, 2), "A_minus"),
    (2, 5, Fraction(-1, 2), "B_plus"),
    (2, -5, Fraction(-1, 2), "B_minus"),
    (1, 0, Fraction(2), "N"),
)


def seven_weyl_local_inverse() -> dict[str, Any]:
    q1 = q3 = normal_x2 = normal2_x = Fraction(0)
    gravity_x = cubic_x = 0
    fields = []
    for multiplicity, x_charge, qpsi, name in SEVEN_WEYL_ROWS:
        npsi = int(2 * qpsi)
        nphi = npsi + 1
        hyper_center_pass = (nphi + x_charge) % 2 == 1
        fields.append(
            {
                "name": name,
                "multiplicity": multiplicity,
                "X": x_charge,
                "qpsi": fstr(qpsi),
                "qphi": fstr(qpsi + Fraction(1, 2)),
                "npsi": npsi,
                "nphi": nphi,
                "Z4R_scalar": nphi % 4,
                "standard_hyper_component_center_pass": hyper_center_pass,
            }
        )
        q1 += multiplicity * qpsi
        q3 += multiplicity * qpsi**3
        normal_x2 += multiplicity * qpsi * x_charge**2
        normal2_x += multiplicity * qpsi**2 * x_charge
        gravity_x += multiplicity * x_charge
        cubic_x += multiplicity * x_charge**3
    gauge_coefficient = normal_x2 / 50
    normal_cubic = q3 / 6
    normal_gravity = -q1 / 24
    return {
        "status": "PASS_EXACT_LOCAL_CORRELATED_PARENT_RESIDUE_INVERSE",
        "fields": fields,
        "complex_Weyl_count": sum(row[0] for row in SEVEN_WEYL_ROWS),
        "all_standard_hyper_component_centers_pass": all(
            field["standard_hyper_component_center_pass"] for field in fields
        ),
        "moments": {
            "Q1": fstr(q1),
            "Q3": fstr(q3),
            "normal_X_squared": fstr(normal_x2),
            "normal_squared_X": fstr(normal2_x),
            "gravity_X": gravity_x,
            "X_cubed": cubic_x,
        },
        "polynomial_coefficients": {
            "nu_ell_squared": fstr(gauge_coefficient),
            "nu_cubed": fstr(normal_cubic),
            "nu_p1": fstr(normal_gravity),
        },
        "complete_polynomial": "C7=-(5/2)nu ell^2+(1/8)nu(nu^2+p1)",
        "bound_parent_residue": "R=-(1/8)nu(nu^2+p1)",
        "local_sum": "R+C7=-(5/2)nu ell^2",
        "local_parent_residue_cancelled": (
            q1 == -3 and q3 == Fraction(3, 4)
        ),
        "clean_repair": False,
    }


def two_corner_common_sum_no_go() -> dict[str, Any]:
    cp3_required = Fraction(5, 4) * (2**2 + 3**2)
    cubic_required = 3 * cp3_required
    return {
        "status": "REJECTED_TWO_CORNER_COMMON_SUM_HAS_FORBIDDEN_QUARTER_PERIOD",
        "bundle_relations": ["2ell=A+B", "2ellprime=A-B"],
        "identities": {
            "ell_squared_minus_ellprime_squared": "A B",
            "ell_squared_plus_ellprime_squared": "(A^2+B^2)/2",
        },
        "same_sign_is_forced": {
            "reason": (
                "the bound parent residue is R=-T at both corners, so a local "
                "repair must contain +T at both corners"
            ),
            "z00_post_parent": "-(5/2)nu ell^2",
            "z11_post_parent": "-(5/2)nu ellprime^2",
            "flipped_z11_failure": "R+(-T+(5/2)Pprime)=-2T+(5/2)Pprime",
        },
        "common_signed_sum": "-(5/4)nu(A^2+B^2)",
        "required_inverse": "+(5/4)nu(A^2+B^2)",
        "V74_bridge_class": "k nu A B, k in Z",
        "linear_independence": (
            "A^2+B^2 and A B are independent degree-four polynomials"
        ),
        "witness_periods": {
            "CP3": {
                "integral_h_cubed": 1,
                "nu_A_B": [1, 2, 3],
                "required_inverse": fstr(cp3_required),
                "fractional_part": fstr(cp3_required % 1),
                "integer_AB_bridge_unit": 6,
            },
            "spin_cubic_threefold": {
                "integral_h_cubed": 3,
                "nu_A_B": [1, 2, 3],
                "required_inverse": fstr(cubic_required),
                "fractional_part": fstr(cubic_required % 1),
                "integer_AB_bridge_unit": 18,
            },
        },
        "required_inverse_in_integer_index_lattice": False,
        "required_inverse_in_half_index_lattice": False,
        "any_integer_V74_AB_bridge_repairs": False,
        "both_seven_weyl_route_accepted": False,
    }


def pure_gauge_two_corner_lattice_no_go() -> dict[str, Any]:
    """Classify local T+gP repairs that retain only pure gauge curvature."""
    return {
        "status": "EXACT_GENERAL_PURE_GAUGE_TWO_CORNER_DIAGONAL_QUARTER_NO_GO",
        "local_repair_ansatz": "C_i=T+g_i nu ell_i^2",
        "T": "nu(p1+nu^2)/8",
        "two_admissible_CP3_half_cocharacters": {
            "nu": 1,
            "p1": 4,
            "ell_values": ["5/2", "1/2"],
            "T_period": "5/8",
        },
        "ordinary_integer_endpoint_lattice": {
            "conditions": [
                "5/8+25g/4 is in Z",
                "5/8+g/4 is in Z",
            ],
            "solution_coset": "g=-5/2+4Z",
            "verified_substitution": {
                "g": "4n-5/2",
                "first_period": "25n-15",
                "second_period": "n",
            },
        },
        "permissive_half_index_endpoint_lattice": {
            "conditions": [
                "2(5/8+25g/4) is in Z",
                "2(5/8+g/4) is in Z",
            ],
            "solution_coset": "g=-5/2+2Z",
        },
        "two_corner_common_class": (
            "nu{[(g0+g1)/4](A^2+B^2)+[(g0-g1)/2]A B}"
        ),
        "ordinary_lattice_consequence": {
            "diagonal_coefficient": "(g0+g1)/4=3/4 mod Z",
            "AB_coefficient": "(g0-g1)/2 is an even integer",
            "AB_bridge_can_remove_diagonal_quarter": False,
        },
        "half_index_lattice_consequence": {
            "diagonal_coefficient": "an odd quarter mod Z",
            "AB_coefficient": "(g0-g1)/2 is an integer",
            "AB_bridge_can_remove_diagonal_quarter": False,
        },
        "smallest_absolute_ordinary_remainder": {
            "g0_g1": ["3/2", "-5/2"],
            "common_class": "-(1/4)nu(A^2+B^2)+2nu A B",
            "with_V75_plus4_AB": "-(1/4)nu(A^2+B^2)+6nu A B",
            "required_integer_AB_bridge_level": -6,
            "diagonal_quarter_survives": True,
        },
        "optional_flavor_extension": {
            "odd_X_requires_odd_flavor": True,
            "replacement": "A -> A+2v",
            "common_class": (
                "[(g0+g1)/4]nu[(A+2v)^2+B^2]+"
                "[(g0-g1)/2]nu B(A+2v)"
            ),
            "v_zero_is_admissible": True,
            "evades_no_go": False,
        },
        "scope": (
            "each endpoint cancels T and retains only g_i nu ell_i^2; sectors "
            "retaining SU2R, flavor, gravitational, higher-spin or interacting "
            "correlated curvature require a different classification"
        ),
        "ordinary_or_half_index_pure_gauge_route_exists": False,
    }


def orbifold_chain_and_source_conservation_audit() -> dict[str, Any]:
    return {
        "status": "EXACT_T2_Z4_CHAIN_BOUNDARY_AND_SOURCE_CONSERVATION",
        "square_torus_action": "g:z -> i z",
        "fixed_strata": {
            "order4_points": ["p0=0", "p1=(1+i)/2"],
            "order2_orbit": ["p2=1/2", "p3=i/2"],
            "one_dimensional_fixed_locus_exists": False,
        },
        "four_image_chain": {
            "definition": "Gamma=sum_{j=0}^3 g^j gamma for gamma:p0->p1",
            "boundary": "partial Gamma=4(p1-p0)",
            "supports_level4_opposite_corner_profile": True,
            "within_integral_four_image_cover_orbit_sum_ansatz_primitive_level1_requires_fractional_wall_or_cap": True,
            "quotient_primitive_level1_excluded": False,
            "quotient_delta_normalization_calibrated": False,
            "common_BPS_projector_constructed": False,
        },
        "same_sign_source": {
            "source": "p0+p1",
            "is_boundary_on_compact_T2": False,
            "reason": "a boundary zero-chain has total coefficient zero",
            "required_completion": "compensating -(p2+p3), bulk flux, or changed cap data",
        },
        "V75_level4_geometric_scaffold_plausible": True,
        "V75_level4_global_supersymmetric_profile_constructed": False,
        "equal_corner_one_eighth_inverse_from_two_corner_only_GS_cap": False,
    }


def off_shell_and_exotic_sector_audit() -> dict[str, Any]:
    return {
        "status": "KNOWN_OFF_SHELL_INVARIANTS_DO_NOT_SUPPLY_REQUIRED_REFINED_SECTOR",
        "normal_and_R_connections": {
            "A_N": "omega^(56), a component of the Lorentz connection",
            "SU2R_connection": "part of the 6D Weyl multiplet",
            "ordinary_independent_YM_vectors": False,
        },
        "known_off_shell_scope": {
            "ordinary_vector_linear_density_exists": True,
            "full_curvature_squared_superinvariants_exist": True,
            "isolated_normal_U1_or_nu_c2R_superinvariant_bound_to_current_action": False,
            "formal_4D_N1_axion_term_is_only_spurion_scaffold": True,
            "required_missing_data": [
                "composite superform and its Q-supersymmetry completion",
                "compact axion and chiral-density normalization",
                "accompanying Q-supersymmetry anomaly",
                "T2/Z4 cap, junction and preserved-supercharge projectors",
            ],
        },
        "self_dual_and_refined_loophole": {
            "ordinary_Weyl_and_half_eta_excluded": True,
            "quadratic_refined_self_dual_theory_representation_independently_excluded": False,
            "six_dimensional_self_dual_tensor_changes_I8_and_string_charge_lattice": True,
            "GS_coefficient_is_free_one_eighth_knob": False,
            "standard_Maxwell_duality_structure_is_different": True,
            "required_normal_U1_class_matched_or_constructed": False,
            "explicit_refined_five_dimensional_anomaly_theory_constructed": False,
            "required_free_curvature": "+(1/8)nu(p1+nu^2)",
            "supersymmetric_boundary_and_global_corner_compensation_constructed": False,
        },
        "accepted_exotic_completion": False,
    }


def level4_component_multiplet_audit(v75: Mapping[str, Any]) -> dict[str, Any]:
    level4 = v75["correlated_level4_spectrum_redesign"]
    modules: dict[str, Any] = {}
    for module_name in ("M00", "M11"):
        rows = []
        for field in level4["added_modules"][module_name]["fields"]:
            npsi = int(field["n_equals_2qpsi"])
            nphi = npsi + 1
            x_charge = int(field["X"])
            dimension = int(field["SU2R_dimension"])
            if dimension == 1:
                multiplet_type = "hyperino/hyper-type"
                center_pass = (nphi + x_charge) % 2 == 1
            elif dimension == 2:
                multiplet_type = "gaugino-or-tensorino/vector-type"
                center_pass = (nphi + x_charge) % 2 == 0
            else:
                raise RuntimeError("unexpected SU2R dimension in V75 level-four ledger")
            rows.append(
                {
                    "field_id": field["id"],
                    "multiplicity": field["multiplicity"],
                    "X": x_charge,
                    "SU2R_dimension": dimension,
                    "qpsi": field["qpsi"],
                    "npsi": npsi,
                    "nphi": nphi,
                    "component_multiplet_type": multiplet_type,
                    "component_center_pass": center_pass,
                }
            )
        modules[module_name] = {
            "rows": rows,
            "all_component_centers_pass": all(
                row["component_center_pass"] for row in rows
            ),
        }
    return {
        "status": "COMPONENT_CENTER_PASS__COMPLETE_6D_MULTIPLET_AND_ACTION_ABSENT",
        "source_field_content": {
            "vector": "A_M plus left-handed SU2R-doublet gaugino",
            "tensor": "B_minus plus scalar plus right-handed SU2R-doublet tensorino",
            "hyper": "four scalars plus right-handed SU2R-singlet hyperino",
        },
        "component_rule": {
            "superspace": "npsi=nphi-1 for qtheta=+1/2",
            "hyper_type": "nphi+X odd",
            "vector_or_tensor_type": "nphi+X even",
        },
        "modules": modules,
        "all_V75_level4_component_centers_pass": all(
            module["all_component_centers_pass"] for module in modules.values()
        ),
        "not_supplied_by_component_pass": [
            "complete 6D bosonic and fermionic partner sets",
            "symplectic-Majorana reality and chirality accounting",
            "T2/Z4 translation orbits, parities and isotropy lifts",
            "kinetic terms, auxiliary fields and supersymmetry transformations",
            "bulk irreducible gravitational-anomaly balance",
            "localized defect supergravity couplings and regulator",
        ],
        "ordinary_bulk_realization_diagnostics": {
            "T2_Z4_vector_superfield_rule": "V -> rho V; Sigma -> i rho Sigma",
            "one_rho_keeps_both_V_and_Sigma": False,
            "N1_corner_keeps_full_SU2R_gaugino_doublet": False,
            "intrinsic_covering_normal_charges": {
                "A_mu_qphi": 0,
                "Sigma_A5_plus_iA6_qphi": 1,
                "left_Weyl_gauginos_qpsi": "+1/2 (conjugate orientation reverses signs)",
                "hyper_scalar_qphi": 0,
                "hyperino_absolute_qpsi": "1/2",
            },
            "orbifold_gauge_phase_rho_is_continuous_normal_charge": False,
            "ordinary_bulk_fields_generate_V75_large_q_without_changed_quotient": False,
            "genuine_Sigma_geometric_scalar_charge": "+/-1",
            "genuine_Sigma_supplies_qphi_plus_or_minus2_driver": False,
            "Sigma_has_derivative_gauge_shift": True,
            "arbitrary_local_Z_E_E_operator_automatically_legal_for_Sigma": False,
            "five_dimensional_codimension1_fixed_stratum_exists": False,
            "bulk_projector_anomaly_equals_integer_local_Weyl_ledger_without_recalculation": False,
        },
        "formal_complete_multiplet_gravitational_diagnostic": {
            "formula": "Delta(H-V+29T)",
            "vector_interpretation": {
                "M00_H_V_T": [4, 4, 0],
                "M00_shift": 0,
                "M11_H_V_T": [4, 2, 0],
                "M11_shift": 2,
            },
            "tensor_interpretation": {
                "M00_H_V_T": [4, 0, 4],
                "M00_shift": 120,
                "M11_H_V_T": [4, 0, 2],
                "M11_shift": 62,
            },
            "is_full_bulk_anomaly_calculation": False,
        },
        "local_4D_N1_diagnostic": (
            "a scalar-singlet/fermion-SU2R-doublet package requires a vector/tensor "
            "or N=2-type completion; reducing SU2R to its center removes the c2(R) "
            "curvature used by the V75 anomaly ledger"
        ),
        "bulk_multiplet_realization_constructed": False,
        "localized_defect_action_constructed": False,
        "derivative_or_KK_descendants_counted_as_independent_anomaly_fields": False,
        "same_action_microscopic_completion": False,
    }


def normal_bundle_driver_obstruction() -> dict[str, Any]:
    drivers = [
        {
            "route": "V75 level-four z00 cross mass",
            "field": "Z00",
            "qphi": -2,
            "Z4R": 0,
        },
        {
            "route": "V75 level-four z11 cross mass",
            "field": "Z11",
            "qphi": 2,
            "Z4R": 0,
        },
        {
            "route": "seven-Weyl A/B cross mass",
            "field": "Z2",
            "qphi": 2,
            "Z4R": 0,
        },
        {
            "route": "seven-Weyl neutral Majorana mass",
            "field": "Zminus4",
            "qphi": -4,
            "Z4R": 0,
        },
    ]
    for row in drivers:
        row["nphi"] = 2 * row["qphi"]
        row["npsi_for_minimal_chiral"] = row["nphi"] - 1
        row["scalar_center_pass"] = row["nphi"] % 2 == 0
        row["minimal_neutral_SU2R_singlet_chiral_center_pass"] = (
            row["npsi_for_minimal_chiral"] % 2 == 0
        )
        row["vector_or_tensor_SU2R_doublet_partner_would_pass"] = (
            row["npsi_for_minimal_chiral"] + 1
        ) % 2 == 0
        row["c1_on_CP3"] = f"{row['qphi']} H"
        row["geometric_Z4_phase"] = "-1" if abs(row["qphi"]) == 2 else "+1"
        row["VEV_invariant_under_trivial_intrinsic_Z4_lift"] = (
            row["geometric_Z4_phase"] == "+1"
        )
        row["nowhere_zero_on_CP3"] = False
    return {
        "status": "EXACT_NOWHERE_ZERO_NORMAL_LINE_SECTION_OBSTRUCTION",
        "theorem": {
            "field_bundle": "phi_q is a section of N^q",
            "nowhere_zero_consequence": "a nowhere-zero phi_q trivializes N^q",
            "chern_condition": "q c1(N)=0",
            "covariant_form": "D^2 phi_q=i q F_N phi_q",
            "parallel_nonzero_consequence": "q F_N=0 wherever phi_q is nonzero",
        },
        "admissible_witness": {
            "manifold": "CP3",
            "c1_N": "H",
            "H_non_torsion": True,
        },
        "drivers": drivers,
        "minimal_chiral_lift": {
            "bound_fermion_center_rule": "npsi+X+r=0 mod2",
            "all_neutral_SU2R_singlet_driver_fermions_fail": all(
                not row["minimal_neutral_SU2R_singlet_chiral_center_pass"]
                for row in drivers
            ),
            "repair_options": [
                "an SU2R-doublet vector/tensor-type partner with its full multiplet",
                "odd X or flavor charge with a recomputed gauge/flavor ledger",
                "a composite or non-chiral source with a complete microscopic action",
            ],
            "vector_or_tensor_type_lift_constructed": False,
        },
        "all_proposed_nonzero_charge_drivers_obstructed_on_witness": all(
            not row["nowhere_zero_on_CP3"] for row in drivers
        ),
        "allowing_zero_divisor": {
            "mass_matrix_full_rank_everywhere": False,
            "consequence": (
                "the fermion mass vanishes on the divisor; localized modes, a WZ/eta "
                "phase, or another anomaly-matching sector must remain"
            ),
        },
        "normal_frame_Higgs_interpretation": (
            "a condensate charged only under normal Spin(2) reduces the normal-frame "
            "bundle and is not a symmetry-preserving gap on the original backgrounds"
        ),
        "flat_orbifold_isotropy": {
            "phase_formula": "exp(i pi qphi/2)",
            "qphi_plus_or_minus2_phase": "-1",
            "qphi_minus4_phase": "+1",
            "R0_alone_implies_trivial_geometric_isotropy": False,
            "plus_or_minus2_VEV_requires_new_intrinsic_or_locked_minus1": True,
        },
        "dynamical_chiral_driver_anomaly_ledger": {
            "seven_route_driver_fermions": {
                "Z2_qpsi": "3/2",
                "Zminus4_qpsi": "-9/2",
                "Delta_Q1": "-3",
                "Delta_Q3": "-351/4",
            },
            "seven_module_before_drivers_Q1_Q3": ["-3", "3/4"],
            "seven_module_plus_drivers_Q1_Q3": ["-6", "-87"],
            "still_cancels_intended_parent_residue": False,
            "nondynamical_charged_spurion_is_honest_SUSY_completion": False,
            "F_only_spurion_result": "soft B-term, not the required Weyl mass",
        },
        "anomaly_vectorlike_partner_requirements": {
            "rule": "qphi_partner=1-qphi so qpsi_partner=-qpsi",
            "Z2_partner": {"qphi": -1, "Z4R": 2},
            "Zminus4_partner": {"qphi": 5, "Z4R": 2},
            "V75_plus2_partner": {"qphi": -1, "Z4R": 2},
            "V75_minus2_partner": {"qphi": 3, "Z4R": 2},
            "partners_supply_nonzero_driver_VEV_potential": False,
            "full_F_D_BPS_and_Hessian_still_required": True,
        },
        "neutral_vector_linear_pair_supplies_driver": False,
        "six_dimensional_multiplet_sources": {
            "vector_has_physical_driver_scalar": False,
            "tensor_scalar_normal_charge": 0,
            "linear_scalars_are_arbitrary_N_power_sections": False,
            "existing_V74_vector_linear_pair_supplies_driver": False,
        },
        "spin_gauge_locking_escape": {
            "schema": "phi in N^qN tensor L_g^qg with qN c1(N)+qg c1(L_g)=0",
            "requires_new_U1_g": True,
            "changes_tangential_structure": True,
            "requires_recomputed_anomaly_ledger": True,
            "constructs_current_action": False,
        },
    }


def seven_weyl_mass_audit() -> dict[str, Any]:
    return {
        "status": "LOCAL_OPERATOR_LEDGER_EXACT__GLOBAL_GAP_REJECTED",
        "qtheta": "+1/2",
        "superpotential_normal_charge": "+1",
        "charged_fields": {
            "A_plus_minus": "X=+/-5, qpsi=-3/2, qphi=-1, Z4R=2",
            "two_B_plus_minus": "X=+/-5, qpsi=-1/2, qphi=0, Z4R=0",
        },
        "cross_operator": {
            "formula": "W=Z2(A_plus B_minus+A_minus B_plus)",
            "Z2": "qphi=+2, Z4R=0",
            "normal_charge_check": "+2-1+0=+1",
            "Z4R_check": "0+2+0=2 mod4",
            "two_independent_blocks": True,
            "rank_per_one_by_two_block_at_most": 1,
            "maximum_total_charged_rank": 2,
            "one_B_plus_B_minus_pair_left": True,
        },
        "leftover_B_pair": {
            "bilinear_normal_charge": 0,
            "bilinear_Z4R": 0,
            "Giudice_Masiero_class": True,
            "mass_scale": "conditional m3/2 rather than GUT",
            "symmetry_statement": (
                "the high-scale Kahler selector is Z4R allowed; the generated mass "
                "uses nonzero W and leaves only the Z2 matter parity"
            ),
            "z11_if_light": {
                "hypercharges": [1, -1],
                "Delta_b_GUT": ["6/5", "0", "0"],
                "V72_existing_field_portal_ring_predicts_stability": True,
                "new_driver_sector_requires_portal_reaudit": True,
                "standard_thermal_history_BBN_viability": (
                    "SEVERELY_CONSTRAINED_NOT_CERTIFIED; low reheating remains conditional"
                ),
            },
        },
        "neutral_N": {
            "qpsi": "+2",
            "qphi": "+5/2",
            "Z4R": 1,
            "Majorana_operator": "W=Zminus4 N^2",
            "Zminus4": "qphi=-4, Z4R=0",
            "normal_charge_check": "-4+5/2+5/2=+1",
            "Z4R_check": "0+1+1=2 mod4",
            "standalone_full_quotient_N1_chiral_certified": False,
            "required_physical_hyper_vector_or_tensor_lift": True,
        },
        "combined_with_V75_mass_parity_theorem": {
            "R0_condensate_rule": (
                "an even-normal-charge scalar condensate permits a fermion mass "
                "only when qpsi_i+qpsi_j is even"
            ),
            "z00_per_X_sign": {
                "charges": ["(+3/2)x2", "(+1/2)x2", "(-3/2)x1", "(-1/2)x2"],
                "two_half_charge_class_counts": [4, 3],
                "rank_deficiency_at_least": 1,
            },
            "z11_per_X_sign": {
                "charges": ["(-3/2)x3", "(-1/2)x4"],
                "two_half_charge_class_counts": [3, 4],
                "rank_deficiency_at_least": 1,
            },
            "forced_survivor_can_be_qpsi": "-1/2",
            "one_vectorlike_charge_five_pair_survives": True,
            "R2_odd_normal_condensate_closes_rank": True,
            "R2_condensate_preserves_high_scale_Z4R": False,
            "symmetry_compatible_alternative": "low-scale Giudice-Masiero mass",
        },
        "local_Z4R_operator_checks_pass": True,
        "global_driver_section_obstruction_applies": True,
        "two_corner_gluing_already_rejected": True,
        "accepted_mass_gap": False,
    }


def candidate_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "F76_CLEAN_FREE_ETA_REPAIR",
            "selected": False,
            "accepted": False,
            "exact_advance": True,
            "status": "REJECTED_CP3_HALF_INDEX_PERIOD",
        },
        {
            "id": "F76_SEVEN_WEYL_EQUAL_CORNER_REPAIR",
            "selected": False,
            "accepted": False,
            "exact_advance": True,
            "status": "LOCAL_PASS__REJECTED_TWO_CORNER_COMMON_SUM",
        },
        {
            "id": "F76_FOUR_LINE_DIAGONAL_ETA_REPRESENTATIVE",
            "selected": False,
            "accepted": False,
            "exact_advance": True,
            "status": "CORRELATED_INDEX_PASS__PURE_QUARTER_REFINEMENT_ABSENT",
        },
        {
            "id": "F76_V75_LEVEL4_COMPLETE_MULTIPLET_LIFT",
            "selected": False,
            "accepted": False,
            "exact_advance": True,
            "status": "COMPONENT_CENTER_PASS__GLOBAL_DRIVER_AND_ACTION_FAIL",
        },
        {
            "id": "F76_SPIN_GAUGE_LOCKED_DRIVER",
            "selected": False,
            "accepted": False,
            "exact_advance": False,
            "status": "OPEN_CHANGED_TANGENTIAL_STRUCTURE_AND_LEDGER",
        },
        {
            "id": "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT",
            "selected": True,
            "accepted": False,
            "exact_advance": False,
            "status": "SELECTED_OPEN_SAME_ACTION_RECOMPUTATION",
        },
        {
            "id": "F76_INTERACTING_QUARTER_REFINED_ENDPOINT",
            "selected": False,
            "accepted": False,
            "exact_advance": False,
            "status": "OPEN_NO_BORDISM_CLASS_OR_ACTION",
        },
    ]


def build_report() -> dict[str, Any]:
    v75 = load_bound(V75_ROUTE_PATH, EXPECTED_CORES["v75_route"])
    v75_master = load_bound(V75_MASTER_PATH, EXPECTED_CORES["v75_master"])
    clean = universal_clean_half_index_no_go()
    total_period = total_two_corner_index_period_no_go()
    four_line = four_line_diagonal_eta_representative()
    seven = seven_weyl_local_inverse()
    gluing = two_corner_common_sum_no_go()
    pure_gauge = pure_gauge_two_corner_lattice_no_go()
    orbifold_chain = orbifold_chain_and_source_conservation_audit()
    exotic = off_shell_and_exotic_sector_audit()
    multiplets = level4_component_multiplet_audit(v75)
    drivers = normal_bundle_driver_obstruction()
    mass = seven_weyl_mass_audit()
    candidates = candidate_matrix()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "lineage": {
            "V75_route_core": v75["core_sha256"],
            "V75_master_core": v75_master["core_sha256"],
            "V75_selected_candidate": "F75_GAUGE_CHARGED_SPECTRUM_REDESIGN",
            "supersession_scope": (
                "tests V75's physical multiplet and mass-driver obligations and a "
                "new correlated residue repair without changing frozen V75 artifacts"
            ),
        },
        "universal_clean_half_index_no_go": clean,
        "total_two_corner_index_period_no_go": total_period,
        "four_line_diagonal_eta_representative": four_line,
        "seven_weyl_local_correlated_inverse": seven,
        "two_corner_common_sum_no_go": gluing,
        "pure_gauge_two_corner_lattice_no_go": pure_gauge,
        "orbifold_chain_and_source_conservation_audit": orbifold_chain,
        "off_shell_and_exotic_sector_audit": exotic,
        "V75_level4_component_multiplet_audit": multiplets,
        "normal_bundle_driver_obstruction": drivers,
        "seven_weyl_mass_audit": mass,
        "F76_candidate_matrix": candidates,
        "candidate_adjudication": {
            "clean_free_eta": "REJECTED_EXACT",
            "all_ordinary_free_field_two_corner_repairs": "REJECTED_EXACT",
            "four_line_diagonal_eta_representative": "PASS_EXACT_CORRELATED_ONLY",
            "seven_weyl_local_inverse": "PASS_EXACT_LOCAL",
            "seven_weyl_two_corner_completion": "REJECTED_EXACT",
            "general_pure_gauge_two_corner_completion": "REJECTED_EXACT",
            "level4_four_image_chain": "PASS_EXACT_TOPOLOGICAL_SCAFFOLD_ONLY",
            "ordinary_off_shell_vector_linear_completion": "ABSENT",
            "refined_self_dual_or_interacting_completion": "OPEN_UNCONSTRUCTED",
            "V75_level4_component_centers": "PASS_EXACT",
            "V75_level4_full_multiplet_action": "ABSENT",
            "normal_charged_everywhere_gap": "REJECTED_ON_ADMISSIBLE_WITNESS",
            "spin_gauge_locking": "OPEN_CHANGED_ACTION",
            "full_parent_determinant": "SELECTED_OPEN",
        },
        "open_obligations": [
            "compute one regulator-consistent full parent determinant including gravitino, tensorino, self-dual fields, ghosts, SU2R and every fixed-stratum character",
            "compute the exact equivariant Spin-SU2R-U5(-flavor) bordism group, flat phases and capped T2/Z4 extension",
            "if spin-gauge locking is retained, specify U1_g charges, flux quantization, kinetic terms, Higgs sector and the completely recomputed local/global anomaly polynomial",
            "classify correlated higher-spin, self-dual, Wu-Chern-Simons and interacting quarter-refined endpoint sectors",
            "construct complete bulk or defect supermultiplets, parities, isotropy lifts, F/D/BPS equations and a positive full Hessian",
            "only after a same-action spectrum exists, recompute KK determinants, thresholds, unification, proton operators, flavor, collider limits, reheating, relics and BBN",
        ],
        "gate_ledger": {f"G{i}": "OPEN" for i in range(1, 9)},
        "terminal_decision": {
            "honest_outcome": (
                "V76 closes two tempting free-field continuations without closing a "
                "theory gate.  A representation-independent two-witness theorem "
                "excludes every ordinary localized-Weyl, integer-bridge and standard "
                "half-eta completion of the total equal-corner residue.  A four-line "
                "index gives an exact correlated representative of the required "
                "diagonal quarter but forces an eta-gravity spectator.  The seven-Weyl "
                "module cancels the bound residue at one "
                "corner but its forced same-sign two-corner gauge sum has forbidden "
                "quarter periods and is not an integer/half-index AB bridge.  Every "
                "pure-gauge local inverse has the same two-corner diagonal-quarter "
                "obstruction, including the optional-flavor extension.  Every "
                "V75 level-four component passes its quotient-center multiplet pattern, "
                "but no complete 6D multiplets are present and its normal-charged mass "
                "drivers cannot be nowhere zero on the admissible CP3 bundle.  The "
                "present action remains rejected; the research program remains viable "
                "only through a full same-action equivariant determinant or genuinely "
                "new correlated/changed-structure physics."
            ),
            "clean_free_eta_quarter_routes_closed": True,
            "ordinary_free_field_two_corner_routes_closed": True,
            "four_line_correlated_diagonal_representative_constructed": True,
            "pure_diagonal_quarter_refinement_constructed": False,
            "seven_weyl_local_parent_residue_cancelled": True,
            "seven_weyl_two_corner_route_closed": True,
            "pure_gauge_integer_or_half_index_two_corner_route_closed": True,
            "level4_four_image_orbifold_chain_constructed": True,
            "level4_BPS_profile_constructed": False,
            "V75_level4_component_centers_pass": True,
            "V75_level4_complete_multiplets_constructed": False,
            "V75_level4_global_mass_gap_constructed": False,
            "normal_charged_driver_no_go_on_original_backgrounds": True,
            "spin_gauge_locked_action_constructed": False,
            "full_equivariant_parent_determinant_computed": False,
            "same_action_microscopic_completion_found": False,
            "selected_candidate": "F76_FULL_EQUIVARIANT_PARENT_DETERMINANT",
            "selected_candidate_accepted": False,
            "closed_gates": [],
            "theory_complete": False,
        },
        "primary_sources": source_catalog(),
        "source_manifest": source_manifest(),
        "artifact_hashes": {
            "line_ending_policy": "SHA256 after CRLF-to-LF normalization",
            "generator_sha256": normalized_file_sha(Path(__file__)),
            "test_sha256": normalized_file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    total_period = report["total_two_corner_index_period_no_go"]
    four_line = report["four_line_diagonal_eta_representative"]
    seven = report["seven_weyl_local_correlated_inverse"]
    gluing = report["two_corner_common_sum_no_go"]
    pure_gauge = report["pure_gauge_two_corner_lattice_no_go"]
    orbifold_chain = report["orbifold_chain_and_source_conservation_audit"]
    multiplets = report["V75_level4_component_multiplet_audit"]
    drivers = report["normal_bundle_driver_obstruction"]
    sources = "".join(
        f"- [{row['title']}]({row['url']}): {row['scope']}\n"
        for row in report["primary_sources"]
    )
    obligations = "".join(f"- {row}\n" for row in report["open_obligations"])
    return f"""# V76 correlated-residue and multiplet-realization audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## What survives

The strongest result is representation-independent.  The two bound residues
have total period
`{total_period['common_CP3_witness']['two_corner_residue']}` on CP3 and
`{total_period['spin_cubic_threefold_witness']['two_corner_residue']}` on the
spin cubic threefold.  Honest local Weyl indices and ordinary bridges add
integers; standard signed half-eta copies add only half-integers.  The
remaining odd quarter cannot vanish.

There is nevertheless an exact correlated target: summing the four honest
line indices `c_(eps,tau)=(nu+eps A+tau B)/2` gives

`{four_line['sum_of_indices']}`.

It has integral periods `3` and `11` on the two witnesses.  The desired
diagonal quarter therefore exists only together with the forced
`S_eta=nu(nu^2-p1)/12` spectator; V75's exact theorem excludes removing that
spectator with ordinary neutral determinants or standard half-eta copies.

The seven-Weyl full-quotient module has exact moments
`Q1={seven['moments']['Q1']}`, `Q3={seven['moments']['Q3']}` and
`normal-X^2={seven['moments']['normal_X_squared']}`.  Its polynomial is

`{seven['complete_polynomial']}`,

so it cancels the bound V71 normal/gravitational residue locally.  All seven
entries pass the standard hyper-type component-center rule.  This is a real
local result, not yet a two-corner theory.

## Exact two-corner rejection

The two bundle identities are `{gluing['bundle_relations'][0]}` and
`{gluing['bundle_relations'][1]}`.  Since the parent residue has the same sign
at both corners, the post-cancellation terms add to

`{gluing['common_signed_sum']}`.

This is linearly independent of the V74 bridge class
`{gluing['V74_bridge_class']}`.  Its required inverse has period
`{gluing['witness_periods']['CP3']['required_inverse']}` on CP3 and
`{gluing['witness_periods']['spin_cubic_threefold']['required_inverse']}` on
the spin cubic threefold, with fractional parts `1/4` and `3/4`.  It is in
neither the ordinary index lattice nor the permissive half-index lattice.
Flipping one endpoint also fails because it doubles rather than cancels that
corner's parent residue.

The result is not peculiar to the seven-Weyl representative.  For any local
repair `T+g nu ell^2` that retains only pure gauge curvature, integrality on
the two admissible CP3 half-cocharacters forces
`{pure_gauge['ordinary_integer_endpoint_lattice']['solution_coset']}`.  Even
the deliberately permissive half-index image only enlarges this to
`{pure_gauge['permissive_half_index_endpoint_lattice']['solution_coset']}`.
At two corners the coefficient of `nu(A^2+B^2)` is therefore respectively
`3/4 mod Z` or an odd quarter.  An integer `nu A B` bridge cannot remove it,
and the optional flavor quotient cannot help because `v=0` remains an
admissible subbackground.

## Multiplets and the mass-driver obstruction

Every V75 level-four component passes the appropriate quotient rule:
SU2R-singlet fermions have the hyper-type pattern and SU2R doublets have the
vector/tensor-type pattern.  The aggregate result is
`{multiplets['status']}`.  Complete six-dimensional partner fields, reality
conditions, orbifold profiles, kinetic terms and supersymmetry transformations
are still absent.

The square-torus chain check does preserve one useful part of V75: for a path
between the two order-four points, the four-image cover chain obeys
`{orbifold_chain['four_image_chain']['boundary']}`.  It is a plausible
topological scaffold for a level-four opposite-corner profile.  It supplies
neither the missing quotient delta normalization nor a common BPS projector;
same-sign corner sources also require compensating order-two sources or bulk
flux.

More strongly, a nonzero normal-charge `q` scalar is a section of `N^q`.
A nowhere-zero section trivializes that line.  On the admissible CP3 witness
`c1(N)=H`, none of the proposed `q=+/-2,-4` drivers can therefore be
everywhere nonzero.  Allowing a zero divisor makes the mass matrix lose rank
there and leaves modes or an anomaly-matching WZ/eta phase.  Spin-gauge
locking could evade this only by adding a new gauge line and changing the
tangential structure and complete anomaly ledger; it is not a completion of
the current action.
The scalar representations themselves are honest, but their minimal neutral
SU2R-singlet N=1 chiral fermion partners fail the bound center rule.  A
vector/tensor-type SU2R-doublet lift could pass only with all of its additional
fields and anomalies, which have not been built.

## Fail-closed decision

{report['terminal_decision']['honest_outcome']}

Remaining obligations:

{obligations}
G1-G8 remain OPEN.

## Primary sources

{sources}"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V76 route core hash is not canonical")
    if report["lineage"]["V75_route_core"] != EXPECTED_CORES["v75_route"]:
        raise RuntimeError("V75 route lineage mismatch")
    if report["lineage"]["V75_master_core"] != EXPECTED_CORES["v75_master"]:
        raise RuntimeError("V75 master lineage mismatch")
    clean = report["universal_clean_half_index_no_go"]
    if not clean["all_targets_outside_half_index_lattice"]:
        raise RuntimeError("clean quarter half-index no-go changed")
    total_period = report["total_two_corner_index_period_no_go"]
    if total_period["ordinary_free_field_two_corner_completion_exists"]:
        raise RuntimeError("representation-independent odd-quarter no-go changed")
    four_line = report["four_line_diagonal_eta_representative"]
    if four_line["pure_diagonal_quarter_refinement_constructed"]:
        raise RuntimeError("correlated four-line index was overpromoted")
    if not four_line["total_is_honest_integral_index"]:
        raise RuntimeError("four-line correlated index integrality changed")
    seven = report["seven_weyl_local_correlated_inverse"]
    if not seven["local_parent_residue_cancelled"]:
        raise RuntimeError("seven-Weyl local inverse moments changed")
    gluing = report["two_corner_common_sum_no_go"]
    if gluing["both_seven_weyl_route_accepted"]:
        raise RuntimeError("two-corner seven-Weyl no-go was overruled")
    if gluing["any_integer_V74_AB_bridge_repairs"]:
        raise RuntimeError("AB bridge was incorrectly promoted")
    pure_gauge = report["pure_gauge_two_corner_lattice_no_go"]
    if pure_gauge["ordinary_or_half_index_pure_gauge_route_exists"]:
        raise RuntimeError("general pure-gauge two-corner no-go was overruled")
    multiplets = report["V75_level4_component_multiplet_audit"]
    if not multiplets["all_V75_level4_component_centers_pass"]:
        raise RuntimeError("V75 component-center pass changed")
    if multiplets["same_action_microscopic_completion"]:
        raise RuntimeError("component pass was overpromoted to an action")
    drivers = report["normal_bundle_driver_obstruction"]
    if not drivers["all_proposed_nonzero_charge_drivers_obstructed_on_witness"]:
        raise RuntimeError("normal line-section obstruction changed")
    if not drivers["minimal_chiral_lift"][
        "all_neutral_SU2R_singlet_driver_fermions_fail"
    ]:
        raise RuntimeError("minimal driver center obstruction changed")
    if report["off_shell_and_exotic_sector_audit"]["accepted_exotic_completion"]:
        raise RuntimeError("unconstructed exotic sector was overpromoted")
    if report["terminal_decision"]["closed_gates"]:
        raise RuntimeError("a G gate was closed")
    if report["terminal_decision"]["theory_complete"]:
        raise RuntimeError("theory completeness was overclaimed")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    OUT_JSON.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if OUT_JSON.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError(f"stale generated artifact: {OUT_JSON.name}")
    if OUT_MD.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError(f"stale generated artifact: {OUT_MD.name}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    report = (
        write_artifacts()
        if args.write
        else check_artifacts()
        if args.check
        else build_report()
    )
    print(report["status"])
    print(report["core_sha256"])


if __name__ == "__main__":
    main()
