#!/usr/bin/env python3
"""V73 full diagonal-quotient and supersymmetric WZ audit.

V72 proved that the charge-five character is honest on the local
``U(5)-tilde`` fixed group and found a formally attractive pair of localized
Wess--Zumino variations.  This audit performs the global-form test that V72
left open.  It keeps the V71 convention ``f_L=c1(N)`` for the normal vector
line and distinguishes a rational spin/eta anomaly polynomial from an
ordinary integral differential-cohomology counterterm.

The result is fail closed.  The pure V72 class has exact denominator four on the
diagonal cocharacter, and the two corner forms differ by a nonzero class on
the common U(2)xU(3) subgroup.  A correlated level-one class exists after
including the SU(2)_R bundle, but it necessarily brings a new mixed R
anomaly.  Its N=1 axion realization also brings an axino; in the minimal
no-extra-coupling repair, preserving the V71 normal-gravity factorization
requires an R=2 neutral partner.  The plain
opposite-slope tensor is rejected by the same common-subgroup residue.  The
preferred frontier therefore reuses the existing six-dimensional tensor only
together with a new bridge/inflow sector.  A spin/eta realization counts as
that bridge only if its perturbative curvature is exactly the missing free
class.  No gate is closed.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


VERSION = "V73"
DATE = "2026-08-30"
SCHEMA = "susy_v73_spin11_full_quotient_supersymmetric_wz_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT.json"
MD_PATH = ROOT / "SUSY_V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v73_spin11_full_quotient_supersymmetric_wz_audit.py"
V72_ROUTE_PATH = ROOT / "SUSY_V72_SPIN11_GLOBAL_FORM_MASS_PORTAL_WZ_AUDIT.json"
V72_MASTER_PATH = ROOT / "SUSY_V72_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V71_ROUTE_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json"
EXPECTED_V72_ROUTE_CORE = "46edf8f0943316356f0d5f8f918cc9953f00a10471a65e9c95e92f85904ccec3"
EXPECTED_V72_MASTER_CORE = "eb77fff51a96155a1f162889ae4e073db8837a87bfe4cc804e498dac1eda5530"
EXPECTED_V71_ROUTE_CORE = "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea"

STATUS = (
    "V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT__V72_ROUTE_AND_MASTER_"
    "CORES_BOUND__EXACT_CHARACTER_AND_COCHARACTER_LATTICES__INHERITED_NORMAL_"
    "VECTOR_NORMALIZATION_PINNED__KAPPA_D_PURE_WZ_PERIOD_25_OVER_4__MINIMUM_"
    "PURE_MULTIPLIER_FOUR__F72_PURE_ORDINARY_WZ_REJECTED__CORRELATED_E5R_"
    "LEVEL_ONE_CLASS_INTEGRAL_BUT_FORCES_SU2R_TERM__OPTIONAL_FLAVOR_TERMS_EXACT__"
    "COMMON_U2_U3_RESIDUE_NU_AB_NONZERO__P0_NOT_AFFINE_AXION__AXINO_PARTNER_"
    "LEDGER_EXACT__PLAIN_OPPOSITE_SLOPE_TENSOR_REJECTED__TENSOR_BRIDGE_INFLOW_"
    "FRONTIER_SELECTED_UNACCEPTED__G1_TO_G8_OPEN"
)

PRIMARY_SOURCES = [
    {
        "id": "MONNIER_MOORE_PARK_2018",
        "title": "Quantization of anomaly coefficients in 6D N=(1,0) supergravity",
        "url": "https://arxiv.org/abs/1711.04777",
        "sourced_fact": (
            "Global-form quantization is tested on the cocharacter lattice; "
            "quotient cocharacters can give half- and quarter-integral periods."
        ),
    },
    {
        "id": "DE_RYDT_ET_AL_2007",
        "title": "Symplectic structure of N=1 supergravity with anomalies and Chern-Simons terms",
        "url": "https://arxiv.org/abs/0705.4216",
        "sourced_fact": (
            "N=1 Peccei--Quinn, generalized Chern--Simons and quantum-anomaly "
            "terms have correlated gauge- and supersymmetry-consistency conditions."
        ),
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "sourced_fact": (
            "Bulk Green--Schwarz forms distinguish globally vanishing localized "
            "profiles from mixed U(1) anomalies that survive in four dimensions."
        ),
    },
    {
        "id": "KLEIN_2000",
        "title": "Anomaly cancellation in D=4, N=1 orientifolds and linear/chiral multiplet duality",
        "url": "https://arxiv.org/abs/hep-th/9910143",
        "sourced_fact": (
            "Four-dimensional N=1 Green--Schwarz axions admit chiral/linear "
            "multiplet descriptions; only the appropriate linear multiplets "
            "participate in anomaly cancellation."
        ),
    },
    {
        "id": "OHMORI_SHIMIZU_TACHIKAWA_YONEKURA_2014",
        "title": "Anomaly polynomial of general 6d SCFTs",
        "url": "https://arxiv.org/abs/1408.5572",
        "sourced_fact": (
            "Tensor-branch Green--Schwarz data are theory-dependent anomaly-"
            "matching coefficients, not coefficients fixed by supersymmetry alone."
        ),
    },
    {
        "id": "MONNIER_MOORE_2018",
        "title": "Remarks on the Green--Schwarz terms of six-dimensional supergravity theories",
        "url": "https://arxiv.org/abs/1808.01334",
        "sourced_fact": (
            "A global six-dimensional Green--Schwarz term is tied to the string-"
            "charge lattice and can leave residual global anomalies on nontrivial bundles."
        ),
    },
]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def fstr(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def load_bound(path: Path, expected_core: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"stale canonical core for {label}: {path.name}")
    if actual != expected_core:
        raise RuntimeError(f"unexpected {label} core: {actual} != {expected_core}")
    return value


def quotient_lattice_audit() -> dict[str, Any]:
    rows = []
    examples = [
        ("chi5_standalone", 0, 0, 5, 0, 0),
        ("chiL_chi5", 1, 0, 5, 0, 0),
        ("E5R", 0, 0, 5, 1, 0),
        ("E5RF", 0, 0, 5, 1, 1),
        ("chi5_squared", 0, 0, 10, 0, 0),
    ]
    for name, n, k, x_charge, r, flavor in examples:
        u5_condition = (k + 2 * x_charge) % 5 == 0
        diagonal_condition = (n + x_charge + r) % 2 == 0
        flavor_condition = (x_charge + flavor) % 2 == 0
        rows.append(
            {
                "name": name,
                "n": n,
                "SU5_five_ality": k,
                "X": x_charge,
                "SU2R_highest_weight_parity": r,
                "F": flavor,
                "U5tilde_descends": u5_condition,
                "full_diagonal_descends_without_flavor_quotient": (
                    u5_condition and diagonal_condition
                ),
                "full_diagonal_descends_with_flavor_quotient": (
                    u5_condition and diagonal_condition and flavor_condition
                ),
            }
        )

    return {
        "status": "EXACT_WEIGHT_AND_COCHARACTER_LATTICES",
        "group_without_flavor": (
            "(Spin(2)xU5tilde x SU(2)R)/<(zL,c,zR)>"
        ),
        "group_with_flavor": (
            "(Spin(2)xU5tilde x SU(2)R x U(1)F)/"
            "<(zL,c,zR,1),(1,c,1,-1F)>"
        ),
        "weight_rules": {
            "U5tilde": "k+2x=0 mod5",
            "diagonal_center": "n+x+r=0 mod2",
            "optional_flavor_center": "x+f=0 mod2",
            "normal_charge": "qL=n/2",
        },
        "full_weight_lattice": (
            "{(n,lambda5,x,r[,f]): k(lambda5)+2x=0 mod5, "
            "n+x+r=0 mod2[, x+f=0 mod2]}"
        ),
        "cocharacter_lattice_generators_beyond_the_cover": {
            "kappa5": "(0,varpi5_dual,2/5,0[,0])",
            "kappaD": "(1/2,0,1/2,varpiR_dual[,0])",
            "kappaF_optional": "(0,0,1/2,0,-1/2)",
        },
        "abelian_character_lattice_without_flavor": (
            "x=5b and n+b=0 mod2; generated by (n,x)=(2,0),(1,5)"
        ),
        "abelian_cocharacter_projection_without_flavor": (
            "Z^2 union (Z+1/2)^2 in the cover roots (sigma,ell)"
        ),
        "abelian_character_lattice_with_flavor": (
            "x=5b and n congruent b congruent f mod2"
        ),
        "abelian_cocharacter_projection_with_flavor": (
            "(p,q,s) in (1/2 Z)^3 with p+q+s integral"
        ),
        "representation_checks": rows,
        "chi5_standalone_full_quotient_character": False,
        "chi5_squared_full_quotient_character": True,
        "chiL_chi5_full_quotient_character": True,
    }


def pure_and_correlated_wz_audit() -> dict[str, Any]:
    delta_a = 50
    restricted_level = Fraction(1, 2) * delta_a / 25
    nu = Fraction(1)
    ell = Fraction(5, 2)
    rho = Fraction(1, 2)
    pure_period = nu * ell * ell
    pure_integral_multipliers = [
        multiplier
        for multiplier in range(1, 17)
        if (multiplier * pure_period).denominator == 1
    ]
    spin_root_period = Fraction(1, 2) * pure_period
    spin_root_multipliers = [
        multiplier
        for multiplier in range(1, 17)
        if (multiplier * spin_root_period).denominator == 1
    ]
    c2_r = -(rho * rho)
    correlated_period = nu * (ell * ell + c2_r)

    return {
        "status": (
            "PURE_F72_ORDINARY_WZ_REJECTED__CORRELATED_E5R_CLASS_INTEGRAL_"
            "WITH_FORCED_R_TERM"
        ),
        "normalization": {
            "V71_definition": "fL=x=c1(N)=nu, the normal vector root",
            "primitive_Spin2_root": "sigma=nu/2",
            "physical_charge": "qL=n/2",
            "V72_conversion": "(1/2) DeltaA fL fX^2 with DeltaA=50 and ell=5 fX",
            "restricted_U5tilde_level": fstr(restricted_level),
            "pure_full_quotient_class": "P=nu ell^2",
        },
        "diagonal_cocharacter_test": {
            "cocharacter": "kappaD ending at (zL,c,zR)",
            "nu": fstr(nu),
            "ell": fstr(ell),
            "rhoR": fstr(rho),
            "P_period": fstr(pure_period),
            "P_integral": pure_period.denominator == 1,
            "integral_multipliers_through_16": pure_integral_multipliers,
            "minimal_pure_multiplier": pure_integral_multipliers[0],
            "sufficiency_identity": "4 P=nu (2 ell)^2",
            "sufficiency_reason": (
                "nu and 2 ell are first Chern classes of honest full-quotient "
                "lines, so their integral cup product proves that 4P is integral"
            ),
            "CP3_witness": "pullback to spin CP3 has integral z^3 but coefficient 25/4",
        },
        "alternate_spin_root_convention_not_inherited": {
            "class": "(nu/2) ell^2",
            "period": fstr(spin_root_period),
            "minimal_pure_multiplier": spin_root_multipliers[0],
            "ledger_warning": (
                "holding DeltaA=50 while replacing fL=nu by sigma=nu/2 is a "
                "hybrid diagnostic, not a second physical normalization"
            ),
            "consistent_conversion": (
                "using sigma instead of nu requires integer Spin weights "
                "n=2qL, which doubles DeltaA from 50 to 100"
            ),
            "consistent_physical_class": (
                "(1/2)(100)(nu/2)fX^2=nu ell^2"
            ),
            "consistent_minimal_multiplier": pure_integral_multipliers[0],
        },
        "ordinary_vs_spin_eta_scope": {
            "ordinary_integral_H6_counterterm": "FAIL",
            "rational_perturbative_spin_anomaly_polynomial": "ALLOWED_AS_LOCAL_DATA",
            "eta_or_Wu_refined_invertible_theory": "OPEN_NOT_CONSTRUCTED",
            "inference_for_F72": (
                "an integer coefficient after U5tilde restriction does not define "
                "an isolated bosonic WZ term for every full-quotient bundle"
            ),
        },
        "correlated_E5R_repair": {
            "representation": "E5R=1_(+5) tensor 2_R",
            "center_check": "x+r=5+1=0 mod2",
            "Chern_roots": "ell+rhoR, ell-rhoR",
            "c2": "ell^2+c2(R)=ell^2-rhoR^2",
            "kappaD_c2_period": fstr(ell * ell + c2_r),
            "kappaD_nu_c2_period": fstr(correlated_period),
            "integral_by_associated_bundle": True,
            "desired_component": "+nu ell^2",
            "forced_component": "+nu c2(R), equivalently -nu rhoR^2 on the Cartan",
            "full_R_anomaly_ledger_computed": False,
        },
        "correlated_normal_line_repair": {
            "honest_characters_without_optional_flavor_quotient": [
                "chi_plus=chi_sigma chi5 with c1=ell+sigma",
                "chi_minus=chi_sigma^(-1) chi5 with c1=ell-sigma",
            ],
            "class": "nu c1(chi_plus)c1(chi_minus)=nu(ell^2-nu^2/4)",
            "kappaD_period": fstr(nu * (ell * ell - Fraction(1, 4))),
            "integral_by_product_of_honest_lines": True,
            "desired_component": "+nu ell^2",
            "forced_component": "-nu^3/4",
            "existing_V71_symmetric_normal_cubic_ledger_supplies_it": False,
            "reason": (
                "the forced terms have signs (-1/4,+1/4) at z00,z11, while "
                "the inherited normal-cubic residue is (-1/8,-1/8)"
            ),
            "optional_flavor_quotient_scope": (
                "odd-X lines additionally need odd flavor charge and then acquire "
                "the corresponding flavor characteristic terms"
            ),
        },
        "optional_flavor_completion": {
            "representation": "E5RF=1_(+5) tensor 2_R tensor F_(odd)",
            "center_checks": ["x+r=0 mod2", "x+f=0 mod2"],
            "c2": "(ell+v)^2+c2(R)",
            "expanded_forced_terms": [
                "nu c2(R)",
                "2 nu ell v",
                "nu v^2",
            ],
            "if_F_is_flat": (
                "de Rham flavor terms vanish, but torsion holonomy and the R term remain"
            ),
            "pure_term_rescued_without_correlated_terms": False,
        },
        "F72_pure_ordinary_WZ_accepted": False,
    }


def corner_gluing_audit() -> dict[str, Any]:
    # Let C=c2(E2)+c2(E3).  Then c2(E)=C+AB and
    # c2(Eprime)=C-AB.  For
    #
    #   W00=ell^2+a c2(E),  W11=-ellprime^2+b c2(Eprime),
    #
    # vanishing on the common subgroup requires independent cancellation of
    # C and AB: a+b=0 and 1+a-b=0.  Equivalently 1-2b=0.
    b = Fraction(1, 2)
    a = -b
    common_c2_coefficient = a + b
    common_ab_coefficient = 1 + a - b
    return {
        "status": "EXACT_NONZERO_COMMON_SUBGROUP_RESIDUE__SINGLE_TRANSFER_COCYCLE_FAILS",
        "common_group": "U(2)xU(3) in the vector decomposition",
        "definitions": {
            "A": "c1(det E2)",
            "B": "c1(det E3)",
            "z00": "2 ell=A+B from E5=E2 direct_sum E3",
            "z11": "2 ellprime=A-B from E5prime=E2 direct_sum conjugate(E3)",
        },
        "exact_identity": "ell^2-ellprime^2=A B",
        "opposite_profile_common_restriction_inherited_normalization": "nu A B",
        "opposite_profile_common_restriction_spin_root_convention": "(nu/2) A B",
        "optional_flavor_identity": (
            "(ell+v)^2-(ellprime+v)^2=A B+2 B v"
        ),
        "ordinary_single_transfer_glues": False,
        "coefficient_sum_zero_sufficient": False,
        "z11_conjugation": {
            "lift": "qhatprime=c s qhat s^-1",
            "odd_X_isotropy_phase_flips": True,
            "curvature_square_gets_automatic_minus_sign": False,
            "normal_derivative_orientation": "the t1 theta stabilizer still acts by +i",
        },
        "scope": (
            "This rejects a single ordinary opposite-slope transfer constructed only "
            "from the displayed local forms.  Two independent stratum axions or a new "
            "bridge/transgression sector are not excluded."
        ),
        "missing_bridge_variation": "-nu A B in the inherited normalization",
        "SU5_characteristic_correction_theorem": {
            "bundle_Chern_classes": {
                "E": "E2 direct_sum E3",
                "Eprime": "E2 direct_sum conjugate(E3)",
                "c2(E)": "c2(E2)+c2(E3)+A B",
                "c2(Eprime)": "c2(E2)+c2(E3)-A B",
                "difference": "c2(E)-c2(Eprime)=2 A B",
            },
            "Pontryagin_identity": (
                "p1(V10)=4 ell^2-2 c2(E)=4 ellprime^2-2 c2(Eprime)"
            ),
            "ansatz": {
                "W00": "ell^2+a c2(E)",
                "W11": "-ellprime^2+b c2(Eprime)",
            },
            "common_subgroup_equations": ["a+b=0", "1+a-b=0", "1-2b=0"],
            "unique_solution": {"a": fstr(a), "b": fstr(b)},
            "solution_checks": {
                "common_c2_coefficient": fstr(common_c2_coefficient),
                "common_AB_coefficient": fstr(common_ab_coefficient),
            },
            "corrected_forms": {
                "W00": "+p1(V10)/4",
                "W11": "-p1(V10)/4",
            },
            "physics_consequence": (
                "within the displayed degree-four SU5-characteristic ansatz, the "
                "only correction that removes the common residue is the bulk "
                "Spin11 gauge direction, so it cannot repair the anomaly component "
                "orthogonal to that direction"
            ),
            "p1_over_4_ordinary_integrality": "OPEN_REQUIRES_FULL_QUOTIENT_OR_REFINED_PROOF",
            "rescues_F72_orthogonal_transfer": False,
        },
    }


def component_center_audit() -> dict[str, Any]:
    def row(name: str, n_phi: int, x_charge: int) -> dict[str, Any]:
        n_psi = n_phi - 1
        hyper_scalar = (n_phi + x_charge + 1) % 2 == 0
        hyper_fermion = (n_psi + x_charge) % 2 == 0
        vector_scalar = (n_phi + x_charge) % 2 == 0
        vector_fermion = (n_psi + x_charge + 1) % 2 == 0
        return {
            "name": name,
            "n_phi": n_phi,
            "n_psi": n_psi,
            "X": x_charge,
            "standard_hyper_center_pass": hyper_scalar and hyper_fermion,
            "vector_type_center_pass": vector_scalar and vector_fermion,
            "flavor_parity_required": x_charge % 2,
        }

    charge_five = [
        row("F71_charge5_z00", 2, 5),
        row("F71_charge5_z11", 0, 5),
    ]
    f72 = [
        row("X_plus10", 0, 10),
        row("Xbar_minus10", 0, -10),
        row("S0", 2, 0),
        row("P0", 2, 0),
    ]
    return {
        "status": "EXACT_COMPONENT_CENTER_CLASSIFICATION__F72_STANDARD_HYPER_LIFT_FAILS",
        "component_rule": "n+x+r=0 mod2",
        "superspace_relation": "n_psi=n_phi-1 for qL(theta)=1/2",
        "standard_hyper_pattern": {
            "center_parities_scalar_fermion": [1, 0],
            "criterion": "n_phi+x is odd",
        },
        "vector_type_pattern": {
            "center_parities_scalar_fermion": [0, 1],
            "criterion": "n_phi+x is even",
        },
        "charge_five_rows": charge_five,
        "F72_z00_rows": f72,
        "all_F71_charge_five_standard_hypers_pass": all(
            item["standard_hyper_center_pass"] for item in charge_five
        ),
        "all_F72_z00_fields_standard_hypers_pass": all(
            item["standard_hyper_center_pass"] for item in f72
        ),
        "all_F72_z00_fields_vector_type_centers_pass": all(
            item["vector_type_center_pass"] for item in f72
        ),
        "P0_as_ordinary_neutral_hyper": False,
        "P0_minimal_repair": (
            "source P0 from a Sigma/vector-type full multiplet or change its normal "
            "lift and recompute its partners and anomaly moments"
        ),
        "flavor_completion_effect": (
            "odd X requires odd F and even X requires even F; the original diagonal "
            "condition is unchanged and P0 is not repaired"
        ),
    }


def existing_su2r_spectator_audit(v71: Mapping[str, Any]) -> dict[str, Any]:
    c1 = tuple(
        Fraction(row["series_coefficients_1_x_x2_x3"][1])
        for row in v71["spin_half_equivariant_index"]["rows"]
    )
    phase_dimensions = tuple(
        v71["charged_bulk_normal_gravity_ledger"]["adjoint"][
            "phase_dimensions_m0123"
        ]
    )
    doublet_nu_rho2 = tuple(
        (c1[(m - 1) % 4] + c1[m]) / 4 for m in range(4)
    )
    adjoint_same_chirality = sum(
        phase_dimensions[m] * doublet_nu_rho2[m] for m in range(4)
    )
    gaugino_nu_rho2 = -adjoint_same_chirality
    gaugino_nu_c2r = -gaugino_nu_rho2
    gravity_tensor_linear_nu = (Fraction(-3, 4), Fraction(-3, 4))
    gravity_tensor_nu_rho2 = sum(gravity_tensor_linear_nu) / 4
    gravity_tensor_nu_c2r = -gravity_tensor_nu_rho2
    attempted_total = gaugino_nu_c2r + gravity_tensor_nu_c2r
    attempted_after_pr = (attempted_total + 1, attempted_total - 1)
    return {
        "status": (
            "SU2R_COEFFICIENT_ATTEMPT_NOT_CERTIFIED__PHASE_REALITY_AND_GHOST_"
            "CHARACTERS_UNBOUND__COMMON_C_NO_GO_EXACT"
        ),
        "normalization": "nu=x=c1(N), c2(R)=-rho^2",
        "exact_bound_inputs": {
            "V71_spin_half_linear_coefficients_c_m0123": [
                fstr(value) for value in c1
            ],
            "Spin11_adjoint_phase_dimensions_m0123": list(phase_dimensions),
            "gravity_tensor_virtual_bundle": v71[
                "gravity_tensor_equivariant_index"
            ]["fermionic_virtual_bundle"],
        },
        "uncertified_11_over_16_attempt": {
            "SU2R_half_character_ansatz": (
                "Fcal_m=(1/2)[exp(rho)F_(m-1)+exp(-rho)F_m]"
            ),
            "nu_rho2_coefficients_m0123": [
                fstr(value) for value in doublet_nu_rho2
            ],
            "adjoint_same_chirality_nu_rho2": fstr(adjoint_same_chirality),
            "gaugino_nu_c2R": fstr(gaugino_nu_c2r),
            "assumed_gravity_tensor_R_eigenlift_linear_nu": [
                fstr(value) for value in gravity_tensor_linear_nu
            ],
            "assumed_gravity_tensor_nu_c2R": fstr(gravity_tensor_nu_c2r),
            "attempted_total_each_corner": fstr(attempted_total),
            "attempted_after_PR_z00_z11": [
                fstr(value) for value in attempted_after_pr
            ],
            "certified": False,
            "blocking_reason": (
                "V71's F_m already uses the total phase h_m=zeta i^m; the "
                "additional SU2R phase, Pfaffian reality factor, Rarita/tensor "
                "ghost characters and both-corner lifts have not been derived "
                "from one raw equivariant character"
            ),
        },
        "bulk_total_each_Z4_corner_nu_c2R": "OPEN_NOT_CERTIFIED",
        "inherited_bulk_sources_have_identical_corner_lift": True,
        "hyperini": (
            "all charged and neutral hyperini are SU2R singlets; the weighted "
            "gravitational count is 3*11+266=299 and their c2(R) shift is zero"
        ),
        "localized_V70_F72_continuous_SU2R_representations_constructed": False,
        "common_bulk_R_GS_solution_exists": False,
        "proof": (
            "any inherited identical-corner contribution C leaves (C+1,C-1), "
            "which cannot vanish at both corners"
        ),
        "required_new_antisymmetric_source": ["-nu c2(R)", "+nu c2(R)"],
        "adding_smooth_c2R_GS_is_free_parameter": False,
        "smooth_GS_warning": (
            "a new string-lattice coefficient changes p1*c2R, trF^2*c2R and "
            "c2R^2 terms and must match the complete smooth one-loop polynomial"
        ),
    }


def supersymmetric_completion_audit() -> dict[str, Any]:
    q_axino = Fraction(-1, 2)
    q_partner = Fraction(1, 2)

    def weyl_polynomial(q: Fraction) -> tuple[Fraction, Fraction]:
        return q**3 / 6, -q / 24

    axino = weyl_polynomial(q_axino)
    partner = weyl_polynomial(q_partner)
    total = tuple(axino[index] + partner[index] for index in range(2))

    return {
        "status": (
            "LOCAL_N1_AXION_GCS_STRUCTURE_IDENTIFIED__AXINO_PARTNER_LEDGER_EXACT__"
            "MICROSCOPIC_ACTION_AND_GLOBAL_COCYCLE_OPEN"
        ),
        "N1_structure": {
            "status": (
                "SCHEMATIC_FLAT_N1_DESCENT_ONLY__CURVED_NORMAL_R_SUPERGRAVITY_"
                "EMBEDDING_AND_LARGE_GAUGE_NORMALIZATION_OPEN"
            ),
            "affine_chiral_axion": (
                "A has homogeneous R=0 and an inhomogeneous imaginary shift"
            ),
            "supersymmetric_terms_required": [
                "holomorphic A-dependent gauge kinetic/Peccei--Quinn term",
                "the correlated generalized Chern--Simons term when required",
                "Kahler/Stueckelberg data implementing the affine shift",
            ],
            "consistency_scope": (
                "0705.4216 supplies the N=1 consistency framework, not the missing "
                "F73 coefficient tensor or orbifold action"
            ),
            "linear_chiral_duality_scope": (
                "hep-th/9910143 supports a linear/chiral description of the GS "
                "multiplet; it does not construct this compactification"
            ),
            "local_chiral_action_schema": {
                "gauge_transformations": [
                    "V_L -> V_L+(i/2)(Lambda_L-Lambda_L^dagger)",
                    "A_i -> A_i-i m_i Lambda_L",
                ],
                "Kahler_Stueckelberg": (
                    "integral d4theta K_i(A_i+A_i^dagger+2 m_i V_L)"
                ),
                "gauge_kinetic": (
                    "(1/4) integral d2theta [tau_i+k_i A_i] "
                    "W(E_i)^2+h.c.; E_i=E5R for the integral correlated route"
                ),
                "Bardeen_GCS": (
                    "c_i^GCS integral d4theta V_L Omega(E_i), with "
                    "barD^2 Omega(E_i)=W(E_i)^2"
                ),
                "why_GCS_is_required": (
                    "the consistent mixed triangle varies both currents; the "
                    "GCS term assigns the anomaly to U1L while preserving the "
                    "fixed-group gauge current"
                ),
                "scope": (
                    "schematic local N1 descent: V_L is actually the normal/Lorentz-R "
                    "connection, and E5R contains SU2R curvature; the required off-shell "
                    "supergravity multiplets and curved-superspace completion are absent"
                ),
            },
            "provisional_compact_level_normalization": {
                "z00": "m00 k00=+1",
                "z11": "m11 k11=-1",
                "formal_integer_solution_after_unit_normalization": (
                    "|m_i|=|k_i|=1 for one compact multiplet"
                ),
                "normalization_pinned": False,
                "scope": (
                    "conditional on a 2pi axion period, unit large normal rotation, "
                    "and trace normalization that have not been installed; it applies "
                    "only to an integral correlated class, while the isolated pure "
                    "full-quotient class has already failed"
                ),
            },
            "linear_dual_schema": {
                "modified_linearity": "barD^2 L_i=k_i W(E_i)^2",
                "BF_term": "m_i integral d4theta L_i V_L",
                "fermion_warning": (
                    "chiral-linear duality retains the axino/tensorino and is not "
                    "a fermion-free localized escape"
                ),
            },
            "supersymmetric_partner_couplings": [
                "Re(A_i) F(E_i)^2 and the resulting boundary gauge threshold",
                "axino-gaugino-field-strength interactions",
                "F_A lambda_E lambda_E",
            ],
            "gauge_kinetic_positivity_and_stabilization": "OPEN_NOT_COMPUTED",
        },
        "axino": {
            "homogeneous_R": 0,
            "qL_scalar": "0",
            "qL_fermion": fstr(q_axino),
            "I6_coefficients_x3_xp1": [fstr(value) for value in axino],
            "I6": "(-x^3+x p1)/48",
        },
        "neutral_R2_partner": {
            "homogeneous_R": 2,
            "qL_scalar": "1",
            "qL_fermion": fstr(q_partner),
            "I6_coefficients_x3_xp1": [fstr(value) for value in partner],
            "I6": "(x^3-x p1)/48",
        },
        "pair_ledger": {
            "Q1": fstr(q_axino + q_partner),
            "Q3": fstr(q_axino**3 + q_partner**3),
            "I6_coefficients_x3_xp1": [fstr(value) for value in total],
            "preserves_local_Delta_minus10_normal_gravity_factorization": total == (0, 0),
            "rule": (
                "minimal repair: one qL=+1/2 neutral R2 partner per newly "
                "localized axion"
            ),
            "minimality_assumptions": [
                "no new classical axion couplings to nu^3 or nu p1(T)",
                "no additional compensating fermions",
                "the inherited local Delta=-10 normal-gravity ledger is unchanged",
            ],
            "unique_consequence_of_supersymmetry_alone": False,
        },
        "two_independent_localized_axion_route": {
            "z00": (
                "new affine A00 plus a new neutral R2 partner P00; the provisional "
                "F72 P0 is already counted in the Q1=Q3=0 base module and cannot "
                "cancel the new axino a second time"
            ),
            "z11": "new affine A11 plus one new neutral R2 partner P11",
            "new_axinos": 2,
            "new_R2_partners_beyond_the_provisional_F72_P0": 2,
            "partner_count_scope": (
                "minimal under the pair-ledger assumptions; extra fields or "
                "classical normal/gravitational GS couplings can change the repair"
            ),
            "correlated_R_and_flavor_anomalies_cancelled": False,
            "accepted": False,
        },
        "P0_is_not_the_axion": {
            "P0": "homogeneous R=2 with qpsi=+1/2",
            "A": "homogeneous R=0 with qpsi=-1/2 and an affine shift",
            "log_P0": (
                "singular at P0=0; a nonzero charge-two P0 background breaks "
                "Z4R to Z2R, re-admitting the mu and 16^4 operator classes, and "
                "cannot be imported as a regular affine axion"
            ),
            "identification_valid": False,
        },
        "preferred_existing_tensor_route": {
            "candidate": (
                "reuse the existing six-dimensional tensor/linear multiplet plus "
                "a new bridge/transgression/inflow sector"
            ),
            "potential_advantage": (
                "the pre-existing tensor itself adds no new localized axino; the "
                "unconstructed supersymmetric bridge/inflow may still require "
                "new boundary multiplets"
            ),
            "complete_bridge_field_content_known": False,
            "globally_vanishing_profile_source_scope": "hep-th/0305024",
            "common_residue": "nu A B",
            "common_residue_is_nonzero_free_de_Rham_class": True,
            "torsion_or_zero_curvature_eta_refinement_can_cancel_residue": False,
            "required_bridge_curvature_or_anomaly_polynomial": "-nu A B",
            "spin_eta_scope": (
                "a spin/eta theory is admissible here only if its perturbative "
                "curvature/anomaly polynomial is -nu A B; it then is the bridge/inflow sector"
            ),
            "single_ordinary_transfer_cocycle_exists": False,
            "ordinary_opposite_slope_tensor_subcandidate_rejected": True,
            "modified_linearity_target": (
                "barD^2 L_T=(bulk Spin11 GS source)+delta00 W(E00)^2-"
                "delta11 W(E11)^2+(required bridge/inflow with curvature -nu A B)"
            ),
            "selected_for_next_frontier": True,
            "accepted": False,
        },
    }


def candidate_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "F72_PURE",
            "name": "V72 pure opposite localized WZ levels",
            "status": "REJECTED_AS_ORDINARY_FULL_QUOTIENT_COUNTERTERM",
            "exact_result": "kappaD period 25/4; minimal pure multiplier four",
            "selected": False,
            "accepted": False,
        },
        {
            "id": "F73_AXION",
            "name": "two localized N=1 affine axions with correlated E5R classes",
            "status": "LOCAL_INTEGRAL_CLASS_PASS__R_LEDGER_AND_GLOBAL_ORBIFOLD_ACTION_OPEN",
            "exact_result": (
                "nu c2(E5R) is integral, but it forces nu c2(R), two axinos, "
                "and neutral R2 anomaly partners"
            ),
            "selected": False,
            "accepted": False,
        },
        {
            "id": "F73_NORMAL",
            "name": "normal-line correlated completion",
            "status": "LOCAL_INTEGRAL_CLASS_PASS__FORCED_ASYMMETRIC_NORMAL_CUBIC_LEDGER_FAILS",
            "exact_result": (
                "nu(ell^2-nu^2/4) is integral but adds opposite-sign nu^3/4 "
                "terms not supplied by V71's symmetric normal residue"
            ),
            "selected": False,
            "accepted": False,
        },
        {
            "id": "F73_FLAVOR",
            "name": "flavor-central correlated E5RF completion",
            "status": "LOCAL_INTEGRAL_CLASS_PASS__FLAVOR_R_TORSION_AND_GLUE_OPEN",
            "exact_result": "nu[(ell+v)^2+c2(R)] adds R, X-F and F^2 terms",
            "selected": False,
            "accepted": False,
        },
        {
            "id": "F73_TENSOR_BRIDGE",
            "name": "existing 6D tensor/linear multiplet plus required bridge/inflow sector",
            "status": "SELECTED_STRUCTURAL_FRONTIER__PURE_OPPOSITE_SLOPE_SUBCANDIDATE_REJECTED__BRIDGE_FIELD_CONTENT_OPEN",
            "exact_result": (
                "the displayed slopes leave nu A B, so a new bridge/transgression "
                "with perturbative curvature -nu A B is mandatory; any spin-eta "
                "realization with that curvature is the bridge, not an alternative"
            ),
            "selected": True,
            "accepted": False,
        },
    ]


def source_manifest() -> list[dict[str, Any]]:
    paths = [
        V71_ROUTE_PATH,
        V72_ROUTE_PATH,
        V72_MASTER_PATH,
        Path(__file__).resolve(),
        TEST_PATH,
    ]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    v71_route = load_bound(V71_ROUTE_PATH, EXPECTED_V71_ROUTE_CORE, "V71 route")
    v72_route = load_bound(V72_ROUTE_PATH, EXPECTED_V72_ROUTE_CORE, "V72 route")
    v72_master = load_bound(V72_MASTER_PATH, EXPECTED_V72_MASTER_CORE, "V72 master")
    lattice = quotient_lattice_audit()
    quantization = pure_and_correlated_wz_audit()
    gluing = corner_gluing_audit()
    centers = component_center_audit()
    r_spectator = existing_su2r_spectator_audit(v71_route)
    susy = supersymmetric_completion_audit()
    candidates = candidate_matrix()

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": (
            "Do the V72 opposite WZ levels descend through the full diagonal "
            "quotient and admit a complete N=1 realization?"
        ),
        "primary_sources": PRIMARY_SOURCES,
        "lineage": {
            "bound_V71_route_path": V71_ROUTE_PATH.name,
            "bound_V71_route_core": v71_route["core_sha256"],
            "expected_V71_route_core": EXPECTED_V71_ROUTE_CORE,
            "V71_route_core_matches": v71_route["core_sha256"] == EXPECTED_V71_ROUTE_CORE,
            "bound_V72_route_path": V72_ROUTE_PATH.name,
            "bound_V72_route_core": v72_route["core_sha256"],
            "expected_V72_route_core": EXPECTED_V72_ROUTE_CORE,
            "V72_route_core_matches": v72_route["core_sha256"] == EXPECTED_V72_ROUTE_CORE,
            "bound_V72_master_path": V72_MASTER_PATH.name,
            "bound_V72_master_core": v72_master["core_sha256"],
            "expected_V72_master_core": EXPECTED_V72_MASTER_CORE,
            "V72_master_core_matches": v72_master["core_sha256"] == EXPECTED_V72_MASTER_CORE,
            "V72_restricted_coefficients": v72_route[
                "F72_opposite_level_WZ_transfer_candidate"
            ]["U5tilde_restricted_local_coefficient_integrality"]["restricted_coefficients"],
            "V72_all_gates_open": all(
                state == "OPEN" for state in v72_route["gate_ledger"].values()
            ),
        },
        "full_diagonal_quotient_lattice": lattice,
        "ordinary_WZ_quantization_and_correlated_repair": quantization,
        "z00_z11_common_subgroup_gluing": gluing,
        "scalar_fermion_center_patterns": centers,
        "existing_bulk_SU2R_spectator": r_spectator,
        "N1_axion_GCS_and_tensor_completion": susy,
        "F73_candidate_matrix": candidates,
        "candidate_adjudication": {
            "F72_U5tilde_restricted_coefficient": "RETAINED_PASS_EXACT",
            "F72_pure_full_quotient_ordinary_WZ": "REJECTED_PERIOD_25_OVER_4",
            "F73_correlated_E5R_local_class": "PASS_EXACT_INTEGRAL_WITH_FORCED_R_TERM",
            "F73_existing_bulk_SU2R_spectator": (
                "OPEN_11_OVER_16_ATTEMPT_NOT_CERTIFIED__COMMON_C_NO_GO_EXACT"
            ),
            "F73_correlated_normal_line_class": "PASS_EXACT_INTEGRAL_WITH_UNMATCHED_NORMAL_CUBIC_TERM",
            "F73_local_axion_supermultiplet": "OPEN_MICROSCOPIC_ACTION_NOT_CONSTRUCTED",
            "F73_plain_opposite_slope_tensor": "REJECTED_NONZERO_COMMON_RESIDUE",
            "F73_tensor_bridge_inflow_route": "SELECTED_PREFERRED_BUT_UNACCEPTED",
            "F73_global_equivariant_differential_cocycle": "FAIL_OPEN_NONZERO_COMMON_RESIDUE",
        },
        "frontier_status_ledger": [
            "FULL_WEIGHT_LATTICE_PASS_EXACT",
            "FULL_COCHARACTER_LATTICE_PASS_EXACT",
            "INHERITED_NORMAL_VECTOR_NORMALIZATION_PASS_EXACT",
            "PURE_WZ_PERIOD_25_OVER_4_PASS_EXACT",
            "MINIMAL_PURE_MULTIPLIER_FOUR_PASS_EXACT",
            "F72_PURE_ORDINARY_WZ_REJECTED",
            "CORRELATED_E5R_INTEGRAL_CLASS_PASS_EXACT",
            "EXISTING_BULK_SU2R_NUMERICAL_COEFFICIENT_OPEN_NOT_CERTIFIED",
            "PR_ANTISYMMETRIC_R_SOURCE_ABSENT",
            "CORRELATED_NORMAL_LINE_CLASS_PASS_EXACT_SPECTATOR_UNMATCHED",
            "FORCED_SU2R_TERM_OPEN_LEDGER",
            "COMMON_RESIDUE_NU_AB_PASS_EXACT",
            "P0_NOT_AFFINE_AXION_PASS_EXACT",
            "AXINO_PARTNER_LEDGER_PASS_EXACT",
            "EXISTING_TENSOR_ROUTE_SELECTED_UNACCEPTED",
            "G1_TO_G8_OPEN",
        ],
        "open_obligations": [
            "derive the raw gaugino, gravitino, tensorino and ghost SU2R equivariant characters and the complete localized R ledger",
            "add and quantize an antisymmetric (-1,+1) nu c2(R) source if the E5R route is retained",
            "construct either two honest localized axion/linear multiplets or a regular existing-tensor coupling",
            "supply a bridge/transgression that cancels the common nu A B residue, or redesign the profile",
            "construct the full equivariant differential cocycle including torsion and fixed-stratum data",
            "compute the regulator and eta/Dai-Freed phases on the actual combined quotient",
            "identify a global vector-type source for P0 and all its projected partners",
            "retain the complete V72 KK, vacuum, soft, unification, flavor, proton and cosmology obligations",
        ],
        "gate_ledger": {f"G{i}": "OPEN" for i in range(1, 9)},
        "terminal_decision": {
            "honest_outcome": (
                "V73 retains V72's correctly scoped U5tilde-restricted result and rejects "
                "its extension to a pure full-quotient ordinary WZ counterterm.  The exact "
                "diagonal-cocharacter period is 25/4.  Correlated SU2R and normal-line "
                "completions are locally integral, and the N=1 axino/partner ledger can be "
                "balanced exactly, but their forced spectator anomalies are not cancelled. "
                "The plain opposite-slope tensor also fails by the nonzero common residue. "
                "The selected frontier is therefore the existing tensor plus a genuinely "
                "new bridge/inflow sector of curvature -nu A B.  A spin-eta "
                "realization is admissible only as such a bridge, not as a torsion escape."
            ),
            "F72_pure_WZ_accepted": False,
            "F73_correlated_local_class_accepted_as_full_action": False,
            "F73_plain_tensor_subcandidate_rejected": True,
            "F73_tensor_bridge_inflow_route_selected": True,
            "F73_tensor_bridge_inflow_route_accepted": False,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "theory_complete": False,
        },
        "source_manifest": source_manifest(),
        "artifact_hashes": {
            "generator_sha256": file_sha(Path(__file__).resolve()),
            "test_sha256": file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    lineage = report["lineage"]
    lattice = report["full_diagonal_quotient_lattice"]
    quant = report["ordinary_WZ_quantization_and_correlated_repair"]
    glue = report["z00_z11_common_subgroup_gluing"]
    centers = report["scalar_fermion_center_patterns"]
    susy = report["N1_axion_GCS_and_tensor_completion"]
    r_spectator = report["existing_bulk_SU2R_spectator"]
    checks = {
        "V71_route_bound": lineage["V71_route_core_matches"],
        "V72_route_bound": lineage["V72_route_core_matches"],
        "V72_master_bound": lineage["V72_master_core_matches"],
        "V72_coefficients": lineage["V72_restricted_coefficients"] == {"z00": 1, "z11": -1},
        "chi5_not_full": not lattice["chi5_standalone_full_quotient_character"],
        "E5R_full": next(
            row for row in lattice["representation_checks"] if row["name"] == "E5R"
        )["full_diagonal_descends_without_flavor_quotient"],
        "period": quant["diagonal_cocharacter_test"]["P_period"] == "25/4",
        "multiplier": quant["diagonal_cocharacter_test"]["minimal_pure_multiplier"] == 4,
        "pure_rejected": not quant["F72_pure_ordinary_WZ_accepted"],
        "correlated_integral": quant["correlated_E5R_repair"]["integral_by_associated_bundle"],
        "normal_correlated_integral": quant["correlated_normal_line_repair"][
            "integral_by_product_of_honest_lines"
        ],
        "forced_R_open": not quant["correlated_E5R_repair"]["full_R_anomaly_ledger_computed"],
        "bulk_R_number_open": r_spectator["bulk_total_each_Z4_corner_nu_c2R"]
        == "OPEN_NOT_CERTIFIED",
        "bulk_R_attempt_unaccepted": not r_spectator[
            "uncertified_11_over_16_attempt"
        ]["certified"],
        "bulk_R_symmetric_structure": r_spectator[
            "inherited_bulk_sources_have_identical_corner_lift"
        ],
        "PR_R_no_common_solution": not r_spectator["common_bulk_R_GS_solution_exists"],
        "gluing_identity": glue["exact_identity"] == "ell^2-ellprime^2=A B",
        "gluing_fails": not glue["ordinary_single_transfer_glues"],
        "charge5_hyper": centers["all_F71_charge_five_standard_hypers_pass"],
        "P0_not_hyper": not centers["P0_as_ordinary_neutral_hyper"],
        "axino_pair": susy["pair_ledger"]["I6_coefficients_x3_xp1"] == ["0", "0"],
        "P0_not_axion": not susy["P0_is_not_the_axion"]["identification_valid"],
        "tensor_selected": susy["preferred_existing_tensor_route"]["selected_for_next_frontier"],
        "plain_tensor_rejected": susy["preferred_existing_tensor_route"][
            "ordinary_opposite_slope_tensor_subcandidate_rejected"
        ],
        "tensor_unaccepted": not susy["preferred_existing_tensor_route"]["accepted"],
        "candidate_one_selected": sum(row["selected"] for row in report["F73_candidate_matrix"]) == 1,
        "candidate_none_accepted": not any(row["accepted"] for row in report["F73_candidate_matrix"]),
        "all_gates_open": all(value == "OPEN" for value in report["gate_ledger"].values()),
        "manifest": all(row["exists"] and row["sha256"] for row in report["source_manifest"]),
        "core": report.get("core_sha256") == canonical_sha(report),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V73 validation failed: " + ", ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    quant = report["ordinary_WZ_quantization_and_correlated_repair"]
    glue = report["z00_z11_common_subgroup_gluing"]
    centers = report["scalar_fermion_center_patterns"]
    susy = report["N1_axion_GCS_and_tensor_completion"]
    r_spectator = report["existing_bulk_SU2R_spectator"]
    return f"""# V73 Spin(11) full-quotient supersymmetric WZ audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact full-quotient result

The full representation rules are `k+2x=0 mod 5` and `n+x+r=0 mod 2`,
with `x+f=0 mod 2` when the optional flavor quotient is installed.  The local
charge-five character is not a standalone line of the diagonal quotient.

V71's inherited convention is `fL=c1(N)=nu`, with the primitive Spin(2) root
equal to `nu/2`.  On the exact diagonal cocharacter,

`nu=1, ell=5/2, rhoR=1/2`.

Therefore the V72 pure class has period
`{quant['diagonal_cocharacter_test']['P_period']}` and its minimal pure
integral multiplier is
`{quant['diagonal_cocharacter_test']['minimal_pure_multiplier']}`.  The
U5tilde-restricted level-one check remains correct, but the isolated ordinary
full-quotient WZ term is rejected.  A spin/eta-refined invertible theory could
change this conclusion only after it is explicitly constructed.

The apparent period `25/8` obtained by inserting the primitive Spin root
`sigma=nu/2` while retaining `DeltaA=50` is only a hybrid convention.  A
consistent Spin-weight ledger uses `n=2qL`, doubles `DeltaA` to `100`, and
returns the same physical class `nu ell^2` and multiplier four.

## Correlated local repair

The honest associated bundle `E5R=1_(+5) tensor 2_R` has

`c2(E5R)=ell^2+c2(R)`.

Thus `nu c2(E5R)` is integral at level one, but it necessarily adds the
mixed normal-R term `nu c2(R)`.  With the flavor completion the class becomes
`nu[(ell+v)^2+c2(R)]`, adding X-F and F-squared terms as well.  These omitted
anomaly ledgers prevent acceptance.

The numerical bulk R coefficient remains open.  A provisional `11/16` attempt
is not certified because the total SU2R/isotropy phases, symplectic-Majorana
factor, and Rarita/tensor ghost characters have not been derived in one raw
equivariant calculation.  One conclusion is coefficient-independent: every
inherited bulk R source has the same corner lift, so a common coefficient `C`
leaves `(C+1,C-1)` after the correlated levels and cannot cancel both.  The E5R
route therefore requires a genuinely new antisymmetric `(-1,+1)` source and a
complete R-character computation.

## Exact corner mismatch

On the common U(2)xU(3),

`2 ell=A+B`, `2 ellprime=A-B`, and therefore
`{glue['exact_identity']}`.

The opposite profile leaves `{glue['opposite_profile_common_restriction_inherited_normalization']}`.
Consequently a zero numerical coefficient sum does not construct one global
ordinary transfer cocycle.

Adding SU(5) characteristic terms cannot evade this result.  The unique
two-corner correction that glues is `+p1(V10)/4` at z00 and `-p1(V10)/4`
at z11.  That is the bulk Spin(11) gauge direction itself, so it cannot repair
the orthogonal anomaly.  Ordinary integrality of `p1(V10)/4` is not assumed.

## N=1 multiplet result

An affine axion chiral has homogeneous R=0 and an axino of normal charge
-1/2, with `I6=(-x^3+x p1)/48`.  One neutral R=2 fermion of charge +1/2 has
the opposite polynomial.  Their exact pair ledger is
`{susy['pair_ledger']['I6_coefficients_x3_xp1']}`, preserving the local
Delta=-10 condition.

A schematic flat-N1 descent contains the affine Kahler/Stueckelberg
combination, an A-dependent gauge kinetic term for the full correlated bundle,
and the Bardeen/generalized Chern--Simons term that preserves the fixed-group
gauge current.  In a provisional unit normalization it gives
`m00 k00=+1` and `m11 k11=-1`.  This is not yet the required curved
normal/Lorentz-R supergravity action: the axion period, large-rotation unit,
trace normalization, and off-shell embedding remain open.  The real axion
partner also shifts the boundary gauge kinetic function, whose positivity and
stabilization are uncomputed.

The provisional P0 is not the axion: it has the R=2/qpsi=+1/2 representation
type of a partner, but it is already counted in F72's base anomaly ledger and
cannot cancel a newly added axino.  With no new classical `nu^3` or
`nu p1(T)` axion couplings, no extra compensating fermions, and the inherited
Delta=-10 ledger unchanged, the minimal two-axion repair uses two new R=2
partners.  This field choice is not forced by supersymmetry alone.  Also,
`{susy['P0_is_not_the_axion']['log_P0']}`.
Moreover P0 fails
the ordinary neutral-hyper center pattern:
`{centers['P0_as_ordinary_neutral_hyper']}`.

The selected structural frontier reuses the existing 6D tensor/linear
multiplet and explicitly includes a required new bridge/inflow sector with
perturbative curvature `-nu A B`.  Because `nu A B` is a nonzero free de-Rham
class, a torsion or zero-curvature eta refinement cannot erase it.  A spin/eta
realization carrying `-nu A B` is itself the bridge.  The pre-existing tensor
adds no new localized axino, but the unknown supersymmetric bridge may require
new boundary multiplets.  The plain opposite-slope tensor is rejected.

## Fail-closed decision

{report['terminal_decision']['honest_outcome']}

Remaining obligations:

""" + "".join(f"- {item}\n" for item in report["open_obligations"]) + "\nG1-G8 remain OPEN.\n"


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("V73 generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V73 JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V73 markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
