#!/usr/bin/env python3
"""V74 common-K bridge and endpoint-spectator obstruction audit.

V73 proved that the two level-one corner forms leave the free class
``nu*A*B`` on their common ``U(2)xU(3)`` group.  V74 constructs the inverse
level-one differential-cohomology anomaly theory exactly, proves that it is
new K-reducing defect data rather than an existing Spin(11) tensor coupling,
and then tests whether it completes the endpoint anomalies.

It does not.  Every ordinary unit completion of ``P=nu*ell^2`` has a forced
quarter-period spectator on the diagonal cocharacter, whereas the bridge
changes that period only integrally (also on the free-curvature spin
half-level candidate lattice).  A local vector--linear BF scaffold realizes
the bridge variation and has a cancelling smooth perturbative six-dimensional
fermion anomaly polynomial, but it
does not supply the quarter spectator and its mixed normal-supergravity,
orbifold-equivariant action is not constructed.  No gate is closed.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
V73_ROUTE_PATH = ROOT / "SUSY_V73_SPIN11_FULL_QUOTIENT_SUPERSYMMETRIC_WZ_AUDIT.json"
V73_MASTER_PATH = ROOT / "SUSY_V73_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT.json"
OUT_MD = ROOT / "SUSY_V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v74_spin11_bridge_endpoint_obstruction_audit.py"

EXPECTED_CORES = {
    "v73_route": "1ef4890b81885f5a16196865dd8772d9d3b70a20958829481c2397fd9b044c44",
    "v73_master": "3e393acf570a6bc42d406989a0239e2b62e42ff038516d09bb6fc9a0c964f196",
}

SCHEMA = "susy_v74_spin11_bridge_endpoint_obstruction_audit_v1"
VERSION = "V74"
DATE = "2026-08-30"
STATUS = (
    "V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT__V73_ROUTE_AND_MASTER_CORES_BOUND__"
    "COMMON_K_COCHARACTER_LATTICE_EXACT__NU_AB_PRIMITIVE_ORDINARY_INTEGRAL__"
    "LEVEL_ONE_DIFFERENTIAL_CUP_BRIDGE_PASS__SPIN_PERIOD_GCD_TWO__"
    "SMOOTH_SPIN11_TENSOR_RESTRICTION_NO_GO__LOCAL_VECTOR_LINEAR_BF_SCAFFOLD_PASS__"
    "PERTURBATIVE_I8_VECTOR_LINEAR_PAIR_CANCELS__QUARTER_ENDPOINT_SPECTATOR_THEOREM_EXACT__"
    "ORDINARY_AND_FREE_CURVATURE_SPIN_CANDIDATE_BRIDGE_CANNOT_CANCEL_SPECTATOR__"
    "TORSION_ONLY_ETA_REJECTED__"
    "COEFFICIENT_FOUR_OVERSHOOTS_THREE_UNITS__DIRECT_FIVE_REPAIR_PHENOMENOLOGY_REJECTED__"
    "CONDITIONAL_LOCAL_BRIDGE_ONLY__G1_TO_G8_OPEN"
)


def canonical_sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def load_bound(path: Path, expected: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    embedded = data.get("core_sha256")
    canonical = dict(data)
    canonical.pop("core_sha256", None)
    recomputed = canonical_sha(canonical)
    if embedded != recomputed:
        raise RuntimeError(
            f"noncanonical parent core for {path.name}: {embedded} != {recomputed}"
        )
    if embedded != expected:
        raise RuntimeError(
            f"bound core mismatch for {path.name}: "
            f"{embedded} != {expected}"
        )
    return data


def source_catalog() -> list[dict[str, str]]:
    return [
        {
            "title": "Products in Generalized Differential Cohomology",
            "url": "https://arxiv.org/abs/1112.4173",
            "scope": (
                "multiplicative differential cohomology, integration and relative "
                "theories; framework for the differential cup product used here"
            ),
        },
        {
            "title": "Anomaly Inflow and the eta-Invariant",
            "url": "https://arxiv.org/abs/1909.08775",
            "scope": (
                "eta-invariant description of perturbative and nonperturbative "
                "fermion anomaly inflow; it does not construct the V74 defect"
            ),
        },
        {
            "title": "The anomalous current multiplet in 6D minimal supersymmetry",
            "url": "https://arxiv.org/abs/1511.06582",
            "scope": (
                "deformed six-dimensional linear multiplets for chiral anomalies; "
                "the ordinary-YM construction does not supply the normal-SUGRA defect"
            ),
        },
        {
            "title": "Off-Shell N=(1,0) Linear Multiplets in Six Dimensions",
            "url": "https://arxiv.org/abs/2010.14655",
            "scope": (
                "off-shell vector-linear density and four-form linear multiplet; "
                "used only as the local BF scaffold"
            ),
        },
        {
            "title": "Higher dimensional supersymmetry in 4D superspace",
            "url": "https://arxiv.org/abs/hep-th/0101233",
            "scope": (
                "rigid superspace anomaly-inflow and super-Chern-Simons framework; "
                "not a curved six-dimensional normal-bundle completion"
            ),
        },
        {
            "title": "Localized anomalies in orbifold gauge theories",
            "url": "https://arxiv.org/abs/hep-th/0305024",
            "scope": (
                "fixed-locus anomaly and Green--Schwarz/Chern--Simons exchange "
                "conditions; motivates the pointwise and globally-vanishing tests"
            ),
        },
        {
            "title": "Quantization of anomaly coefficients in 6D N=(1,0) supergravity",
            "url": "https://arxiv.org/abs/1711.04777",
            "scope": (
                "integral string-charge and global Green--Schwarz quantization "
                "framework; it does not authorize the new K defect"
            ),
        },
    ]


def common_k_lattice_audit() -> dict[str, Any]:
    # CP2 x CP1: x^3=y^2=0 and integral x^2 y=1.
    primitive_period = 1
    # (S2)^3: x^2=y^2=z^2=0 and integral xyz=1.
    spin_period = 2
    kd00 = (1, 2, 3)
    kd11 = (1, 2, -3)

    return {
        "status": "EXACT_COMMON_K_CHARACTER_AND_COCHARACTER_LATTICE",
        "group": "full common quotient K with Lie algebra u(2)+u(3)+u(1)L+su(2)R",
        "honest_lines": {
            "N": "nu=c1(N)",
            "LA": "A=c1(det E2)",
            "LB": "B=c1(det E3)",
            "S": "s=(nu+A+B)/2",
        },
        "abelian_cocharacter_projection": (
            "Lambda_K={(nu,A,B) in Z^3 | nu-A-B=0 mod2}"
        ),
        "generators": [(1, 1, 0), (0, 1, 1), (0, 0, 2)],
        "diagonal_cocharacters": {"z00": kd00, "z11": kd11},
        "diagonal_relation_checks": {
            "z00": (kd00[0] - kd00[1] - kd00[2]) % 2 == 0,
            "z11": (kd11[0] - kd11[1] - kd11[2]) % 2 == 0,
        },
        "bridge_class": "r=nu A B",
        "ordinary_primitivity_witness": {
            "six_manifold": "CP2 x CP1",
            "allowed_cocharacters": {
                "lambda_x": (1, 1, 0),
                "lambda_y": (0, 1, 1),
            },
            "classes": "nu=x, A=x+y, B=y",
            "period": primitive_period,
            "conclusion": "r is primitive in ordinary integral cohomology",
        },
        "spin_period_theorem": {
            "mod2_relation": "nu=A+B",
            "steenrod_identity": "r=A^2 B+A B^2=Sq^2(A B) mod2",
            "wu_evaluation": "integral Sq^2(AB)=integral v2 AB=0 on spin six-manifolds",
            "all_spin_periods_even": True,
            "sharp_witness": {
                "six_manifold": "(S2)^3",
                "allowed_cocharacters": [
                    (1, 1, 0),
                    (0, 1, 1),
                    (0, 0, 2),
                ],
                "classes": "nu=x, A=x+y, B=y+2z",
                "period": spin_period,
            },
            "free_spin_period_gcd": spin_period,
            "free_curvature_candidate_level_lattice": "(1/2) Z",
            "full_differential_Dai_Freed_refinement": "OPEN",
        },
    }


def differential_bridge_audit() -> dict[str, Any]:
    return {
        "status": (
            "LEVEL_ONE_COMMON_K_ANOMALY_THEORY_PASS__NEW_DEFECT_REQUIRED__"
            "EXISTING_SPIN11_TENSOR_NO_GO"
        ),
        "differential_character": (
            "rcheck_bridge=-c1check(N) cup c1check(det E2) cup c1check(det E3)"
        ),
        "closed_five_manifold_partition_function": (
            "Z_bridge(Y5)=Hol_Y5(rcheck_bridge)"
        ),
        "local_Chern_Simons_form": (
            "-2 pi i integral_Y5 (aN/2pi)(FA/2pi)(FB/2pi)"
        ),
        "large_normal_gauge_transformation": (
            "Delta log Z=-2 pi i integral_Y5 u A B in 2 pi i Z"
        ),
        "ordinary_level_one_quantized": True,
        "optional_flavor_residue": "nu B(A+V), V=2v, also integral",
        "Mayer_Vietoris_scope": {
            "map": "(alpha00,alpha11) -> i00*alpha00-i11*alpha11",
            "mismatch": "r=nu A B is nonzero in free cohomology",
            "degree_five_trivialization_exists": False,
            "interpretation": (
                "the inverse holonomy is a new anomalous K sector, not a "
                "trivialization by fields already present in the smooth bulk"
            ),
        },
        "smooth_Spin11_restriction": {
            "rational_degree_four_image": "Q[p1(V11)/2]",
            "restriction": (
                "p1(V11)=A^2+B^2-2[c2(E2)+c2(E3)]"
            ),
            "AB_coefficient": 0,
            "nu_AB_in_image": False,
            "existing_two_form_tensor_supplies_bridge": False,
        },
        "physical_defect_requirements": {
            "T2_over_Z4_has_codimension_one_K_fixed_stratum": False,
            "new_K_reducing_domain_wall_or_order_parameter": True,
            "Z4_orbit_and_isotropy_lifts": "OPEN_NOT_CONSTRUCTED",
            "second_boundary_cap_or_topological_source": "OPEN_NOT_CONSTRUCTED",
            "flat_H5_and_Dai_Freed_data": "OPEN_NOT_COMPUTED",
        },
        "common_gluing_solved_by_new_sector": True,
        "full_endpoint_anomaly_solved": False,
    }


def endpoint_spectator_audit() -> dict[str, Any]:
    p = Fraction(25, 4)
    s00 = -p % 1
    # Python's Fraction modulo is nonnegative; retain the signed representative.
    s00_signed = Fraction(-1, 4)
    s11_signed = Fraction(1, 4)
    r00 = 1 * 2 * 3
    r11 = 1 * 2 * -3

    correlated_basis = [
        (1, 1, 0),   # P_R
        (1, 0, -1),  # P_N
        (0, 0, 4),   # four normal-cubic units
    ]

    return {
        "status": (
            "EXACT_QUARTER_ENDPOINT_SPECTATOR__ORDINARY_AND_FREE_CURVATURE_"
            "SPIN_CANDIDATE_BRIDGES_CANNOT_CANCEL"
        ),
        "unit_target": {
            "z00": "+P=+nu ell^2",
            "z11": "-Pprime=-nu ellprime^2",
            "P_diagonal_period": fstr(p),
        },
        "general_integral_completion_theorem": {
            "z00": (
                "for integral C00=P+S00, S00(kappaD)=integer-25/4=-1/4 mod Z"
            ),
            "z11": (
                "for integral C11=-Pprime+S11, S11(kappaD)=integer+25/4=+1/4 mod Z"
            ),
            "signed_fractional_spectators": {
                "z00": fstr(s00_signed),
                "z11": fstr(s11_signed),
            },
            "python_mod1_diagnostic_z00": fstr(s00),
            "independent_of_choice_of_integral_completion": True,
        },
        "bridge_endpoint_periods": {"z00": r00, "z11": r11},
        "ordinary_bridge_levels": "Z",
        "ordinary_bridge_shifts_are_integral": True,
        "free_spin_curvature_candidate_bridge_levels": "(1/2) Z",
        "free_spin_bridge_shifts": "3 Z at either endpoint",
        "quarter_class_changed_by_bridge": False,
        "correlated_class_lattice": {
            "class": "nu[g ell^2+rR c2(R)+sN nu^2/4]",
            "diagonal_period": "(25g-rR+sN)/4",
            "integrality_congruence": "g-rR+sN=0 mod4",
            "Z_basis": correlated_basis,
            "basis_index_in_Z3": 4,
            "useful_dependent_integral_class": {
                "vector": (0, 1, 1),
                "identity": "(0,1,1)=(1,1,0)-(1,0,-1)",
                "class": "nu[c2(R)+nu^2/4]",
            },
            "endpoint_symmetric_rR_and_sN_possible_for_g_plus1_minus1": False,
        },
        "eta_scope": {
            "torsion_only_or_zero_curvature_eta_cancels_free_residue": False,
            "torsion_only_or_zero_curvature_eta_cancels_quarter_spectator": False,
            "reason": (
                "flat eta data lie in the curvature kernel and cannot change a "
                "nonzero perturbative polynomial"
            ),
            "allowed_future_eta_route": (
                "an index theory carrying the opposite free curvature plus every "
                "additional correlated term; it is new bridge physics"
            ),
        },
        "coefficient_four_escape": {
            "class": "4P=nu(2ell)^2",
            "diagonal_period": fstr(4 * p),
            "ordinary_integral": True,
            "common_mismatch": "4 nu A B",
            "inverse_bridge_level": -4,
            "required_physical_level": 1,
            "overshoot_units": 3,
            "mixed_ledger_overshoot_DeltaA": 150,
            "repairs_current_action": False,
            "scope": "requires a redesigned matter/anomaly ledger",
        },
    }


def supersymmetric_bridge_scaffold() -> dict[str, Any]:
    p_r = "(7 p1^2-4 p2)/5760+p1 c2(R)/48+c2(R)^2/24"
    return {
        "status": (
            "CONDITIONAL_LOCAL_VECTOR_LINEAR_BF_PASS__COMMON_GLUING_ONLY__"
            "MIXED_NORMAL_SUPERGRAVITY_AND_GLOBAL_ORBIFOLD_OPEN"
        ),
        "bosonic_local_scaffold": {
            "orientation": "boundary(gamma)=z11-z00",
            "source": "J2=PD(boundary(gamma))=delta11-delta00",
            "Chern_Simons_five_form": "omega5_LAB=-(aL/2pi) A B",
            "derivative": "d omega5_LAB=-nu A B",
            "modified_field_strength": "H5=dC4+omega5_LAB",
            "normal_transformation": "delta_L C4=(lambdaL/2pi) A B",
            "invariant_H5": True,
            "BF_GS_term": "S_BF=-2pi i integral_M6 C4 wedge J2",
            "endpoint_variation": (
                "-2pi i[integral_z11(lambdaL/2pi)AB-"
                "integral_z00(lambdaL/2pi)AB]"
            ),
            "equivalent_flux": "J2=F_Delta/2pi for a neutral U(1)_Delta vector",
        },
        "minimal_multiplets": {
            "linear": "L_Delta=(L^ij,phi_-^i,C4)",
            "vector": "V_Delta=(a_Delta,Omega_+^i,Y_Delta^ij)",
            "off_shell_density": (
                "Y_Delta dot L+2 bar(Omega_Delta) phi+(1/4)F_Delta^MN E_MN"
            ),
            "last_term": "C4 wedge F_Delta",
            "singular_flux_ansatz": "F_Delta/2pi=J2",
            "gaugino_variation_condition": (
                "Y_Delta^ij epsilon_j=(1/4)(gamma dot F_Delta) epsilon^i"
            ),
            "component_contraction_to_F56_fixed": False,
            "full_BPS_and_source_equations_solved": False,
            "opposite_endpoint_FI_or_sources": "REQUIRED_NEW_DEFECT_DATA",
        },
        "deformed_linear_constraint": {
            "curvature_target": "dH5=-nu A B",
            "polarized_superfield_source": "W_L W_A W_B symmetrized",
            "Bardeen_assignment": "preserve A and B currents; assign anomaly to L",
            "ordinary_YM_superform_framework_exists": True,
            "normal_L_is_ordinary_YM_vector": False,
            "mixed_normal_SUGRA_K_defect_superform_constructed": False,
        },
        "new_multiplet_anomaly_ledger": {
            "Omega_plus": "+P_R",
            "phi_minus": "-P_R",
            "P_R": p_r,
            "same_orbifold_lift_required": True,
            "sum": "0",
            "irreducible_p2_sum": "0",
            "smooth_perturbative_I8_cancellation": True,
            "pointwise_equivariant_cancellation": "OPEN_PENDING_COMPATIBLE_Z4_LIFTS",
            "single_linear_without_compensating_anomaly_sector_allowed": False,
        },
        "topological_mass": {
            "BF_bilinear": "2m bar(Omega)phi+Y dot L+C4 wedge F",
            "nonchiral_massive_pair_at_level_one": "CONDITIONAL_LOCAL_RESULT",
            "no_massless_axino_or_vector": "CONDITIONAL_ON_PARITIES_AND_CAP_DATA",
        },
        "endpoint_spectator": {
            "vector_linear_pair_contribution": "0",
            "quarter_spectator_cancelled": False,
            "twisting_lifts_to_leave_quarter_is_BF_compatible": False,
            "additional_free_curvature_or_fields_required": True,
        },
        "existing_tensor_distinction": {
            "existing_physical_field": (
                "anti-self-dual tensor-multiplet two-form B_minus, opposite duality "
                "to gravity B_plus"
            ),
            "bridge_field": "four-form linear multiplet",
            "same_field": False,
        },
        "accepted_same_action_completion": False,
    }


def alternative_repairs() -> dict[str, Any]:
    return {
        "status": "ORDINARY_PROFILE_AND_MINIMAL_MATTER_ESCAPES_REJECTED_SCOPED",
        "profile_theorem": {
            "scope": "displayed pure determinant-square ansatz only",
            "identity": (
                "k0 ell^2+k1 ellprime^2=[(k0+k1)(A^2+B^2)+"
                "2(k0-k1)AB]/4"
            ),
            "zero_overlap_coefficients": "k0+k1=0 and k0-k1=0",
            "only_zero_solution": {"k0": 0, "k1": 0},
            "required_profile": {"k0": 1, "k1": -1},
            "required_profile_residue": "A B",
            "remove_flip_consequence": "restores U5 and loses G3211 breaking",
        },
        "direct_local_five": {
            "representation": "formal one-Weyl vector-type 5_(+2) ledger",
            "qL": "1/2",
            "R_Phi": 2,
            "U5tilde_center": "k+2x=1+4=5=0 mod5",
            "scalar_diagonal_parity": "n+x+r=2+2+0=4 even",
            "fermion_diagonal_parity": "n+x+r=1+2+1=4 even",
            "mixed_shift_SU5_X2": ["1/4", "10"],
            "target_residual_SU5_X2": ["-1/4", "-10"],
            "formal_one_Weyl_mixed_residual_cancelled": True,
            "continuous_SU2R_multiplet_constructed": False,
            "multiplicity_warning": (
                "the parity label r=1 is not by itself a literal one-component "
                "SU2R representation; a doublet would have multiplicity two"
            ),
            "full_local_supersymmetric_lift_constructed": False,
            "fatal_obstructions": [
                "an unpaired chiral five contains a colored triplet and weak doublet",
                "it changes the pure local SU5^3 anomaly",
                "a symmetry-preserving massive conjugate has opposite qL and erases the mixed repair",
                "same-R Giudice--Masiero mass is normal-charge blocked or leaves low colored exotics",
                "cross-corner conjugation cannot match both U2 and U3 blocks",
            ],
            "accepted": False,
        },
        "common_group_matter_diagnostic": {
            "fields": "(2,3)_(qL=-1/2)+(2,bar3)_(qL=+1/2)",
            "mixed_bridge_component": "-nu A B",
            "normal_Q1_Q3": [0, 0],
            "full_K_center_and_Z4R_lift_checked": False,
            "explicit_determinant_anomaly_ledger_complete": False,
            "complete_U5_fixed_point_representations": False,
            "determinant_and_mixed_gauge_anomalies_cancelled": False,
            "massive_conjugate_completion_preserves_bridge": False,
            "accepted": False,
        },
        "smooth_bulk_changes": {
            "smooth_unprojected_Spin11_invariant_characteristic_generates_AB": False,
            "projector_weighted_bulk_representation_classification_complete": False,
            "adjoint_hyper": (
                "spoils irreducible six-dimensional gauge cancellation unless the "
                "three vector hypers in the bound parent are removed"
            ),
            "extra_tensor": (
                "Delta T=+1 requires Delta H=-29 at fixed V from H-V+29T=273"
            ),
            "preserves_bound_parent": False,
        },
    }


def candidate_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "F74_K_CS_BRIDGE",
            "name": "primitive common-K differential-cup bridge",
            "status": "PASS_EXACT_COMMON_GLUING_ONLY__NOT_FULL_ENDPOINT_COMPLETION",
            "selected": False,
            "accepted": False,
        },
        {
            "id": "F74_VECTOR_LINEAR_REFINED_BRIDGE",
            "name": "neutral vector-linear BF bridge plus missing refined endpoint sector",
            "status": (
                "SELECTED_STRUCTURAL_SCAFFOLD__LOCAL_VARIATION_AND_NEW_FIELD_"
                "ANOMALY_LEDGER_PASS__QUARTER_SPECTATOR_AND_GLOBAL_ACTION_OPEN"
            ),
            "selected": True,
            "accepted": False,
        },
        {
            "id": "F74_COEFFICIENT_FOUR",
            "name": "ordinary coefficient-four bridge redesign",
            "status": "REJECTED_FOR_CURRENT_LEVEL__OVERSHOOTS_THREE_ANOMALY_UNITS",
            "selected": False,
            "accepted": False,
        },
        {
            "id": "F74_DIRECT_LOCAL_FIVE",
            "name": "direct vector-type local five cancellation",
            "status": "REJECTED_UNPAIRED_CHIRAL_COLORED_FIVE_AND_SU5_CUBIC_ANOMALY",
            "selected": False,
            "accepted": False,
        },
        {
            "id": "F74_COMMON_MATTER_INTERFACE",
            "name": "incomplete common-group bifundamental bridge matter",
            "status": "REJECTED_AS_ENDPOINT_MATTER__INTERFACE_ONLY_AND_GAUGE_ANOMALOUS",
            "selected": False,
            "accepted": False,
        },
    ]


def source_manifest() -> list[dict[str, Any]]:
    paths = [
        V73_ROUTE_PATH,
        V73_MASTER_PATH,
        Path(__file__).resolve(),
        TEST_PATH,
    ]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    v73_route = load_bound(V73_ROUTE_PATH, EXPECTED_CORES["v73_route"])
    v73_master = load_bound(V73_MASTER_PATH, EXPECTED_CORES["v73_master"])
    lattice = common_k_lattice_audit()
    bridge = differential_bridge_audit()
    endpoint = endpoint_spectator_audit()
    susy = supersymmetric_bridge_scaffold()
    alternatives = alternative_repairs()
    candidates = candidate_matrix()

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "lineage": {
            "V73_route_core": v73_route["core_sha256"],
            "V73_master_core": v73_master["core_sha256"],
            "V73_selected_candidate": "F73_TENSOR_BRIDGE",
            "supersession_scope": (
                "tests the V73 bridge frontier; preserves every V73 rejection and gate"
            ),
        },
        "common_K_lattice_and_spin_periods": lattice,
        "differential_cohomology_bridge": bridge,
        "endpoint_spectator_theorem": endpoint,
        "supersymmetric_vector_linear_scaffold": susy,
        "alternative_profile_and_matter_audit": alternatives,
        "F74_candidate_matrix": candidates,
        "candidate_adjudication": {
            "primitive_K_bridge": "PASS_EXACT_COMMON_GLUING_ONLY",
            "existing_Spin11_tensor": "REJECTED_NO_AB_IN_RESTRICTION_IMAGE",
            "vector_linear_BF_scaffold": "CONDITIONAL_LOCAL_PASS",
            "quarter_endpoint_spectator": "FAIL_OPEN_NOT_CANCELLED",
            "torsion_only_eta": "REJECTED_ZERO_CURVATURE_CANNOT_CANCEL_FREE_POLYNOMIAL",
            "coefficient_four": "REJECTED_FOR_UNIT_ACTION",
            "direct_local_five": "REJECTED_PHENOMENOLOGY_AND_PURE_GAUGE_ANOMALY",
        },
        "open_obligations": [
            "construct the mixed normal-supergravity/K-defect deformed linear superform",
            "supply a quotient-quantized refined endpoint sector carrying the opposite quarter free curvature and all correlated terms",
            "construct the Z4-equivariant defect orbit, isotropy lifts, cap/source data and flat Dai--Freed phase",
            "derive parities and the complete spectrum proving the vector-linear BF pair is massive with no chiral remainder",
            "recompute the full pointwise SU2R, normal, gravitational and discrete-R anomaly ledger with the new defect",
            "solve the defect BPS/FI equations, kinetic positivity, moduli stabilization and the full Hessian",
            "retain the V73 KK determinant, regulator, thresholds, flavor, proton and cosmology obligations",
        ],
        "gate_ledger": {f"G{i}": "OPEN" for i in range(1, 9)},
        "terminal_decision": {
            "honest_outcome": (
                "V74 constructs an exact quantized level-one common-K bridge and a "
                "conditional vector-linear BF scaffold with cancelling perturbative I8.  "
                "It proves that the displayed smooth Spin11 invariant-characteristic "
                "tensor coupling cannot generate the bridge and that "
                "the bridge cannot change the forced quarter endpoint spectator.  "
                "Coefficient four and minimal matter routes redesign or spoil the "
                "action.  The selected scaffold is not a complete microscopic action."
            ),
            "common_K_bridge_exists": True,
            "bridge_is_existing_action_content": False,
            "common_gluing_solved": True,
            "quarter_endpoint_spectator_solved": False,
            "supersymmetric_global_orbifold_action_constructed": False,
            "selected_candidate": "F74_VECTOR_LINEAR_REFINED_BRIDGE",
            "selected_candidate_accepted": False,
            "same_action_microscopic_completion_found": False,
            "closed_gates": [],
            "theory_complete": False,
        },
        "primary_sources": source_catalog(),
        "source_manifest": source_manifest(),
        "artifact_hashes": {
            "generator_sha256": file_sha(Path(__file__).resolve()),
            "test_sha256": file_sha(TEST_PATH),
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    lattice = report["common_K_lattice_and_spin_periods"]
    bridge = report["differential_cohomology_bridge"]
    endpoint = report["endpoint_spectator_theorem"]
    susy = report["supersymmetric_vector_linear_scaffold"]
    alternatives = report["alternative_profile_and_matter_audit"]
    sources = "".join(
        f"- [{row['title']}]({row['url']}): {row['scope']}\n"
        for row in report["primary_sources"]
    )
    obligations = "".join(f"- {item}\n" for item in report["open_obligations"])
    return f"""# V74 Spin(11) bridge and endpoint-obstruction audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact common-K bridge

The full common Abelian cocharacter lattice is

`{lattice['abelian_cocharacter_projection']}`.

The honest line classes `nu`, `A=c1(det E2)` and `B=c1(det E3)` therefore
define the integral class `r=nu A B`.  Its CP2 x CP1 period is
`{lattice['ordinary_primitivity_witness']['period']}`, so it is primitive.
The inverse level-one anomaly theory is

`{bridge['differential_character']}`,

with holonomy `{bridge['closed_five_manifold_partition_function']}`.  This is
an exact quantized common-K bridge.  It is new physics, not an existing tensor
trivialization: `r` is nonzero free and the restriction

`{bridge['smooth_Spin11_restriction']['restriction']}`

contains no `A B` term.  The T2/Z4 action also has no codimension-one K fixed
stratum, so a physical implementation needs a K-reducing defect, its Z4 orbit,
and cap/source data.

## Spin periods and the endpoint theorem

On spin six-manifolds `r=Sq^2(AB)` modulo two, hence all periods are even.
The `(S2)^3` witness has period
`{lattice['spin_period_theorem']['sharp_witness']['period']}`, proving that the
free-curvature candidate level lattice is half-integral.  This period argument
does not construct the full differential/Dai--Freed refinement.

This does not solve the endpoints.  The unit corner class has period
`{endpoint['unit_target']['P_diagonal_period']}`.  Any ordinary integral local
completion therefore leaves spectators

`S00={endpoint['general_integral_completion_theorem']['signed_fractional_spectators']['z00']}`
and
`S11={endpoint['general_integral_completion_theorem']['signed_fractional_spectators']['z11']}`
modulo integers.  The bridge evaluates to
`{endpoint['bridge_endpoint_periods']}`; integer levels shift by multiples of
six and free-curvature candidate spin half-levels by multiples of three.
Neither changes a
quarter class.  A flat/torsion eta phase cannot change nonzero perturbative
curvature; a viable eta theory must add the opposite free index density and
all of its correlated terms.

The coefficient-four class is integral, but it cancels four anomaly units
rather than the required one and overshoots by
`{endpoint['coefficient_four_escape']['mixed_ledger_overshoot_DeltaA']}` in the
V71/V72 mixed ledger.  It is a spectrum redesign, not a repair of the bound
action.

## Conditional supersymmetric scaffold

Let `J2=delta11-delta00`.  The local four-form construction uses

`{susy['bosonic_local_scaffold']['modified_field_strength']}`

and

`{susy['bosonic_local_scaffold']['BF_GS_term']}`.

Its variation is exactly the missing opposite endpoint `A B` inflow.  One
neutral vector plus one four-form linear multiplet has the off-shell
vector--linear density and opposite-chirality fermions with smooth
perturbative anomaly polynomial `+P_R-P_R=0`.  Pointwise equivariant
cancellation is still open until compatible Z4 lifts are constructed.  With
compatible parities the BF coupling can make the pair massive.  This is only
a local scaffold: the normal Lorentz/R connection is
not an ordinary Yang--Mills vector, the mixed normal-supergravity deformed
linear superform is absent, the equivariant defect is unbuilt, and the pair
contributes zero to the quarter spectator.

The existing physical anti-self-dual tensor-multiplet two-form (opposite
duality to gravity `B+`) and the new four-form linear multiplet are distinct
fields.

## Alternative repairs

The profile identity is

`{alternatives['profile_theorem']['identity']}`.

Within the displayed pure `(ell^2,ellprime^2)` determinant-square ansatz, only
the zero profile vanishes on the overlap.  A formal one-Weyl vector-type
`5_(+2)` ledger cancels the local mixed residual algebraically, but no literal
continuous SU2R multiplet or local supersymmetric lift has been constructed;
the row already leaves an unpaired chiral colored five and a pure SU5 cubic
anomaly, while a massive conjugate erases the desired mixed index.  The common
bifundamental diagnostic produces `-nu A B` only as incomplete,
gauge-anomalous interface matter.  Smooth unprojected Spin11-invariant
characteristic/GS couplings cannot generate `A B`; projector-weighted bulk
matter was not exhaustively classified here.

## Fail-closed decision

{report['terminal_decision']['honest_outcome']}

Remaining obligations:

{obligations}
G1-G8 remain OPEN.

## Primary sources

{sources}"""


def validate_report(report: Mapping[str, Any]) -> None:
    copy = dict(report)
    core = copy.pop("core_sha256")
    if canonical_sha(copy) != core:
        raise RuntimeError("V74 core hash is not canonical")
    if report["lineage"]["V73_route_core"] != EXPECTED_CORES["v73_route"]:
        raise RuntimeError("V73 route lineage mismatch")
    if report["lineage"]["V73_master_core"] != EXPECTED_CORES["v73_master"]:
        raise RuntimeError("V73 master lineage mismatch")
    if not report["differential_cohomology_bridge"]["ordinary_level_one_quantized"]:
        raise RuntimeError("primitive K bridge did not quantize")
    if report["terminal_decision"]["quarter_endpoint_spectator_solved"]:
        raise RuntimeError("quarter spectator was overclaimed")
    if report["terminal_decision"]["closed_gates"]:
        raise RuntimeError("a gate was closed")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    report = write_artifacts() if args.write else check_artifacts() if args.check else build_report()
    print(report["status"])
    print(report["core_sha256"])


if __name__ == "__main__":
    main()
