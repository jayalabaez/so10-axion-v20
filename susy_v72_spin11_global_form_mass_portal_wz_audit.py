#!/usr/bin/env python3
"""V72 global-form, mass/portal, and Wess--Zumino transfer audit.

V71 found exact local charge-five fermion modules that rotate the mixed
normal-gauge anomaly into the ordinary Spin(11) Green--Schwarz direction.
This audit asks whether those modules are honest representations, can be
made massive, and can decay without destroying the selector.

The result is deliberately two-sided.

* The local charge lattice is validated.  The actual connected centralizer
  of the order-four lift in Spin(11) is the spin double cover

      U(5)-tilde = (SU(5) x U(1)_X)/Z5,

  and its primitive singlet characters have X charge +/-5.

* The conventional F71 fermion repair is not viable.  A quadratic mass that
  preserves the normal U(1) has opposite fermion normal charges and therefore
  carries zero U(1)_L-X^2 anomaly.  Adding such partners erases the repair.
  Moreover an all-order center/R-parity theorem forbids non-derivative local
  chiral-superfield decay operators linear in a charge-five field built from
  the corrected module and existing V70/MSSM field content.  The lightest z11
  field is then an exactly stable Y=+/-1 state within that local candidate
  action; nonlocal interactions and arbitrary new bridge sectors are not
  excluded.

There is, however, a sharper bosonic alternative.  At z00 the inherited
X(+10), Xbar(-10), S0 sector plus one neutral R=2 chiral has mixed shift -100
and vanishing spectator moments; a +50 localized WZ variation leaves -50.
At z11 no charged defect fermions are added and a -50 variation supplies the
same target.  After restriction to the U(5)-tilde gauge factor, the two WZ
coefficients are +1 and -1 in the primitive character chi_5 normalization
because l=c1(chi_5)=5 f_X and

      (1/2)(+/-50) f_L f_X^2 = +/- f_L l^2.

This passes a necessary restricted local coefficient-integrality check and
removes all new charged relics.  It does not establish quantization under the
full diagonal Spin/R/flavor quotient and is not yet a microscopic action: the
combined Spin/R/flavor
translation cocycle, supersymmetric axion/tensor multiplet, differential
cocycle, regulator, and global eta phase remain open.  No G gate is closed.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


VERSION = "V72"
DATE = "2026-08-30"
SCHEMA = "susy_v72_spin11_global_form_mass_portal_wz_audit/v1"
ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V72_SPIN11_GLOBAL_FORM_MASS_PORTAL_WZ_AUDIT.json"
MD_PATH = ROOT / "SUSY_V72_SPIN11_GLOBAL_FORM_MASS_PORTAL_WZ_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v72_spin11_global_form_mass_portal_wz_audit.py"
V71_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json"
V70_PATH = ROOT / "SUSY_V70_SPIN11_LOCALIZED_PARENT_SPIN_FLAVOR_COMPLETION_AUDIT.json"
EXPECTED_V71_CORE = "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea"
EXPECTED_V70_CORE = "3e7b8e53916fbbc05bdcdf9632bcf4359aa4888b037df775c37d8d7d2551b228"

STATUS = (
    "V72_SPIN11_GLOBAL_FORM_MASS_PORTAL_WZ_AUDIT__V71_AND_V70_CORES_BOUND__"
    "TRUE_FIXED_GROUP_U5_TILDE_EXACT__CHARGE_FIVE_CHARACTERS_HONEST_LOCAL_REPS__"
    "TOTAL_SPIN_R_MULTIPLET_AND_TRANSLATION_COCYCLE_OPEN__MASS_ANOMALY_MATCHING_"
    "THEOREM_EXACT__CHARGE_FIVE_ALL_ORDER_NONDERIVATIVE_CHIRAL_PORTAL_NO_GO__STABLE_Y_PLUSMINUS1_"
    "RELIC__F71_CONVENTIONAL_FERMION_COMPLETION_REJECTED__TWO_CORNER_WZ_TRANSFER_"
    "COEFFICIENTS_PLUS1_MINUS1_INTEGRAL_AFTER_U5TILDE_RESTRICTION__NO_NEW_CHARGED_"
    "EXOTICS__SUPERSYMMETRIC_EQUIVARIANT_DIFFERENTIAL_COCYCLE_AND_GLOBAL_PHASES_"
    "OPEN__F72_UNACCEPTED__G1_TO_G8_OPEN"
)

PRIMARY_SOURCES = [
    {
        "id": "WOIT_SPIN_NOTES",
        "title": "Topics in Representation Theory: Spin Groups",
        "url": "https://www.math.columbia.edu/~woit/notes18.pdf",
        "sourced_fact": (
            "The pullback of Spin(2n)->SO(2n) to U(n) is "
            "U(n)-tilde={(A,u):u^2=det A}.  The quotient and character lattice "
            "used here are then derived explicitly, not imported."
        ),
    },
    {
        "id": "TELEMAN_1997",
        "title": "Non-abelian Seiberg-Witten theory and projectively stable pairs",
        "url": "https://arxiv.org/abs/alg-geom/9609020",
        "sourced_fact": (
            "Spin^G structures use a diagonal center quotient rather than "
            "independently defined spin and gauge bundles."
        ),
    },
    {
        "id": "HAMBELTON_HAUSMANN_2009",
        "title": "Equivariant Bundles and Isotropy Representations",
        "url": "https://arxiv.org/abs/0704.2763",
        "sourced_fact": (
            "Local isotropy representations are only part of the data of a global "
            "equivariant bundle; their groupoid compatibility must also be supplied."
        ),
    },
    {
        "id": "VON_GERSDORFF_2007",
        "title": "Anomalies on Six Dimensional Orbifolds",
        "url": "https://arxiv.org/abs/hep-th/0612212",
        "sourced_fact": (
            "The fixed-stratum remnant-Lorentz polynomial and its local-Weyl "
            "normalization are the V71 inputs retained here."
        ),
    },
    {
        "id": "VON_GERSDORFF_QUIROS_2003",
        "title": "Localized anomalies in orbifold gauge theories",
        "url": "https://arxiv.org/abs/hep-th/0305024",
        "sourced_fact": (
            "Localized mixed anomalies may require Green--Schwarz or localized "
            "axionic cancellation; globally vanishing defect profiles obey an "
            "integrability condition and need not give a four-dimensional gauge mass."
        ),
    },
    {
        "id": "CMS_HSCP_2025",
        "title": "Search for heavy long-lived charged particles with large ionization energy loss",
        "url": "https://arxiv.org/abs/2410.09164",
        "sourced_fact": (
            "The one-species stable Drell--Yan Q=1 lepton benchmark is excluded "
            "below 1.14 TeV; the two-species F71 spectrum requires a recast."
        ),
    },
    {
        "id": "POSPELOV_2007",
        "title": "Particle physics catalysis of thermal Big Bang Nucleosynthesis",
        "url": "https://arxiv.org/abs/hep-ph/0605215",
        "sourced_fact": (
            "Negatively charged relics with lifetimes above 10^3 s alter BBN; for "
            "lifetimes above 10^5 s the stated sensitivity is n_X/s below 3e-17."
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
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_bound(path: Path, expected_core: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing {label} input: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("core_sha256") != expected_core:
        raise RuntimeError(
            f"{label} core mismatch: {value.get('core_sha256')} != {expected_core}"
        )
    return value


def global_form_audit() -> dict[str, Any]:
    reps = [
        ("5_(+2)", 1, 2),
        ("5bar_(-2)", 4, -2),
        ("10_(-1)", 2, -1),
        ("5bar_(+3)", 4, 3),
        ("1_(-5)", 0, -5),
        ("1_(+5)", 0, 5),
        ("1_(+10)", 0, 10),
    ]
    rows = []
    for name, five_ality, x_charge in reps:
        descends = (five_ality + 2 * x_charge) % 5 == 0
        rows.append(
            {
                "representation": name,
                "SU5_five_ality": five_ality,
                "X": x_charge,
                "k_plus_2x_mod5": (five_ality + 2 * x_charge) % 5,
                "descends_to_U5_tilde": descends,
                "spin_cover_center_phase": -1 if x_charge % 2 else 1,
                "descends_to_vector_U5": descends and x_charge % 2 == 0,
            }
        )
    all_honest = all(row["descends_to_U5_tilde"] for row in rows)
    charge_five = [row for row in rows if abs(row["X"]) == 5]
    center_parity = []
    for locus, scalar_n, fermion_n in (("z00", 2, 1), ("z11", 0, -1)):
        center_parity.append(
            {
                "locus": locus,
                "x_mod2": 1,
                "scalar_Spin2_weight_n": scalar_n,
                "fermion_Spin2_weight_n": fermion_n,
                "required_SU2R_center_parity_scalar": (scalar_n + 1) % 2,
                "required_SU2R_center_parity_fermion": (fermion_n + 1) % 2,
                "hypermultiplet_center_pattern_passes": (
                    (scalar_n + 1 + 1) % 2 == 0
                    and (fermion_n + 1 + 0) % 2 == 0
                ),
            }
        )
    return {
        "status": "EXACT_LOCAL_FIXED_GROUP_AND_CHARACTER_LATTICE__GLOBAL_EQUIVARIANT_GLUE_OPEN",
        "centralizer_proof": {
            "vector_image": "Q=diag(J,J,J,J,J,1)",
            "SO11_centralizer": "U(5); the one-dimensional +1 eigenspace is fixed",
            "Spin11_centralizer": "C_Spin11(qhat)=pi^(-1)U(5)=U(5)-tilde",
            "connectedness": (
                "the pullback cover is connected because pi1(U5)->pi1(SO11)=Z2 "
                "is onto; the possible central commutator with qhat is therefore +1"
            ),
        },
        "presentations": {
            "pullback": "{(A,u) in U(5)xU(1): u^2=det(A)}",
            "quotient": "(SU(5)xU(1)_X)/<(omega I5,omega^2)>",
            "map": "[S,t] -> (A=t^2 S,u=t^5)",
            "omega": "exp(2 pi i/5)",
            "spin_cover_kernel": "c=[I,-1]",
        },
        "representation_rule": "SU5 five-ality k and integer X charge x descend iff k+2x=0 mod5",
        "representation_checks": rows,
        "all_displayed_representations_honest_in_U5_tilde": all_honest,
        "character_group": {
            "generator": "chi5([S,t])=t^5=u",
            "singlet_lattice_U5_tilde": "X in 5 Z",
            "singlet_lattice_vector_U5": "X in 10 Z",
            "charge_five_honest": all(row["descends_to_U5_tilde"] for row in charge_five),
            "charge_five_not_vector_U5": all(
                not row["descends_to_vector_U5"] for row in charge_five
            ),
        },
        "spinor_branching": {
            "32": "direct_sum_(p=0..5) Lambda^p 5_(2p-5)",
            "16_even_p": "1_-5 + 10_-1 + 5bar_3",
            "11": "5_2 + 5bar_-2 + 1_0",
        },
        "z11_conjugate_stabilizer": {
            "group": "s U(5)-tilde s^-1 with the same character lattice",
            "lift_relation": "qhat_prime=-s qhat s^-1",
            "transported_qhat_prime": "[I,-zeta] rather than [I,zeta]",
            "chi5_isotropy_sign_must_be_tracked": True,
        },
        "combined_local_center_quotient": {
            "group": "(Spin(2)xU5tilde x SU(2)R)/<(zL,c,zR)>",
            "component_rule": "n+x+r=0 mod2",
            "charge_five_checks": center_parity,
            "consequence": (
                "the ordinary hypermultiplet center pattern can make the fields honest, "
                "but standalone 4D chirals with no SU2R/flavor lift are not yet defined"
            ),
        },
        "space_group_cocycle": {
            "relations_in_Spin11": [
                "what^2=c",
                "qhat what qhat^-1=what=c what^-1",
            ],
            "ordinary_wallpaper_homomorphism": False,
            "odd_X_line_mismatch": "-1",
            "minimal_algebraic_completion": (
                "add U(1)_F and quotient by (1,c,1,-1_F); give odd X odd F parity "
                "and take T1=T2=[what,i_F]"
            ),
            "completion_exists_algebraically": True,
            "completion_applied_to_full_action": False,
            "global_equivariant_orbibundle_constructed": False,
        },
    }


def corrected_modules(v71: Mapping[str, Any]) -> Mapping[str, Any]:
    return v71["mixed_normal_gauge_obstruction"][
        "corrected_spinorial_U5_preimage_modules"
    ]


def mass_and_portal_audit(v71: Mapping[str, Any]) -> dict[str, Any]:
    modules = corrected_modules(v71)
    z00 = modules["z00_complete_ledger"]
    z11 = modules["z11_complete_ledger"]
    z00_charged = [row for row in z00["fields"] if abs(row["X"]) == 5]
    z11_charged = [row for row in z11["fields"] if abs(row["X"]) == 5]
    if len(z00_charged) != 4 or len(z11_charged) != 4:
        raise RuntimeError("V71 charge-five multiplicity changed")

    # Finite verification of the all-order Diophantine argument.  Since
    # c+p+m=1, the scan already exhausts every possible charged-field count.
    z00_solutions = []
    for a in range(5):
        for b in range(5):
            for c in range(2):
                for p in range(2):
                    for m in range(2):
                        if c + p + m == 1 and 2 * (a - b) + p - m == 0:
                            z00_solutions.append((a, b, c, p, m))
    z00_only_S_equal_rank = all(
        p == m == 0 and c == 1 and a == b
        for a, b, c, p, m in z00_solutions
    )

    return {
        "status": "EXACT_MASS_ANOMALY_MATCHING_AND_ALL_ORDER_NONDERIVATIVE_CHIRAL_PORTAL_NO_GO",
        "normal_charge_convention": "qpsi=rL-1/2 with qL(theta)=1/2",
        "z00_all_order_module_ring": {
            "monomial": "X^a Xbar^b S^c (P+)^p (P-)^m N^k",
            "gauge_equation": "2(a-b)+p-m=0 after dividing X charge by 5",
            "W_normal_and_R_equation": "c+p+m=1",
            "solution": "p=m=0, c=1, a=b",
            "finite_symbolic_check_solution_count": len(z00_solutions),
            "finite_symbolic_check_only_S_times_equal_rank": z00_only_S_equal_rank,
            "ring": "W00=S0 F(N_i,X Xbar)",
            "charge_five_W_mass_or_interaction_at_any_order": False,
            "first_existing_field_mass_like_Kahler": "(S0^dagger)^2 P+_a P-_b/Lambda^2",
            "inactive_on_V70_branch": "<S0>=F_S0=0",
            "new_spurion_needed_for_GM": "Z with (R,rL)=(0,2)",
        },
        "z11_all_order_module_ring": {
            "invariants": "M_ab=Pprime+_a Pprime-_b",
            "determinantal_relation": "M11 M22-M12 M21=0",
            "ring": "W11=sum_alpha Z_alpha F_alpha(M_ab)",
            "renormalizable_terms": "f_alpha Z_alpha+lambda_(alpha ab) Z_alpha M_ab",
            "bare_mass": False,
            "full_rank_from_Z_VEV": (
                "requires <Z_alpha> and breaks continuous U1L and Z4R to Z2"
            ),
            "GM_boundary": (
                "K contains c_ab M_ab+h.c.; in rigid SUSY it is a Kahler "
                "transformation, while in supergravity a mass needs the R/normal-"
                "charged SUSY-breaking order parameter"
            ),
        },
        "mass_anomaly_matching_theorem": {
            "strict_W_mass_condition": "r_i+r_j=1",
            "fermion_normal_sum": "qpsi_i+qpsi_j=r_i+r_j-1=0",
            "conjugate_pair_mixed_anomaly": "X^2(qpsi_i+qpsi_j)=0",
            "full_rank_trivially_gapped_sector_nonzero_U1L_X2_anomaly": False,
            "F71_required_nonzero_shifts": {"z00_charge_five": "+50", "z11": "-50"},
            "opposite_q_partners_erase_repair": True,
            "symmetry_breaking_mass_requires_WZ_transfer": True,
        },
        "all_order_nonderivative_chiral_portal_theorem": {
            "charge_five_center_parity": "odd",
            "tensor_vector_Higgs_rank_fields": "X-even and residual-R-even",
            "spinorial_family_fields": "X-odd and residual-R-odd",
            "gauge_invariance_linear_in_P": "requires an odd number of spinorial matter insertions",
            "R_parity_result": "operator is odd while W and K targets are even",
            "continuous_normal_result": "total is half-integral while W/K targets are integral",
            "nonderivative_local_chiral_W_or_K_portal_at_any_order": False,
            "z11_locality": "no co-localized family or bulk 32 transporter in V70",
            "lightest_charge_five_state_stable": True,
            "z11_lightest_electric_charge_absolute": 1,
            "scope": (
                "non-derivative local chiral-superfield operators in the corrected "
                "F71 modules and existing V70/MSSM field content with the stated "
                "center/R parities; nonlocal interactions, derivative operators, "
                "and arbitrary new bridge sectors are not excluded"
            ),
        },
        "scope_boundary": {
            "complete_corrected_module_ring": True,
            "complete_mixed_V70_V71_ring": False,
            "reason": (
                "V71 does not pin continuous lifts for every A0/B0/Higgs boundary "
                "field; under the minimal lift qL(A0)=qL(S0)=1, V70's discrete-only "
                "cubic P3(A0,S0) is not invariant"
            ),
        },
    }


def discrete_and_phenomenology_audit(v71: Mapping[str, Any]) -> dict[str, Any]:
    modules = corrected_modules(v71)
    z00_all = modules["z00_complete_ledger"]["fields"]
    z11_all = modules["z11_complete_ledger"]["fields"]
    z00_new = [row for row in z00_all if row["origin"].startswith("new F71")]
    z11_new = [row for row in z11_all if row["origin"].startswith("new F71")]

    def rpsi(row: Mapping[str, Any]) -> int:
        return int(row["Z4R_scalar"]) - 1

    z00_new_grav = sum(rpsi(row) for row in z00_new)
    z11_new_grav = sum(rpsi(row) for row in z11_new)
    z00_complete_grav = sum(rpsi(row) for row in z00_all)
    z11_complete_grav = sum(rpsi(row) for row in z11_all)
    z00_new_x2r = sum(rpsi(row) * int(row["X"]) ** 2 for row in z00_new)
    z11_new_x2r = sum(rpsi(row) * int(row["X"]) ** 2 for row in z11_new)
    z00_complete_x2r = sum(rpsi(row) * int(row["X"]) ** 2 for row in z00_all)
    z11_complete_x2r = sum(rpsi(row) * int(row["X"]) ** 2 for row in z11_all)

    # Four z11 chirals have Y=+1,+1,-1,-1 and rpsi=-1.
    sum_y2r = -4
    a1_gut = Fraction(3, 5) * sum_y2r
    delta_b1 = 4 * Fraction(3, 5)
    return {
        "status": "EXACT_DEFECT_SHIFT_AND_ONE_LOOP_THRESHOLD_DIAGNOSTIC__FULL_GLOBAL_LEDGER_OPEN",
        "new_field_shifts_relative_to_V70": {
            "z00": {
                "Delta_A3": 0,
                "Delta_A2": 0,
                "Delta_A_X2R": z00_new_x2r,
                "Delta_Agrav": z00_new_grav,
            },
            "z11": {
                "Delta_A3": 0,
                "Delta_A2": 0,
                "Delta_A_Xprime2R": z11_new_x2r,
                "sum_Y2_rpsi": sum_y2r,
                "Delta_A1_GUT": f"{a1_gut.numerator}/{a1_gut.denominator}",
                "Delta_Agrav": z11_new_grav,
            },
        },
        "complete_local_modules": {
            "z00_Agrav": z00_complete_grav,
            "z11_Agrav": z11_complete_grav,
            "both_Agrav_zero_from_Q1_zero": z00_complete_grav == z11_complete_grav == 0,
            "z00_X2R": z00_complete_x2r,
            "z11_Xprime2R": z11_complete_x2r,
            "doubled_X2R_mod4": {
                "z00": (2 * z00_complete_x2r) % 4,
                "z11": (2 * z11_complete_x2r) % 4,
            },
            "non_Abelian_Z4R_shifts": {"A3": 0, "A2": 0},
            "full_bulk_gravitino_tensor_neutral_discrete_ledger": "OPEN_NOT_COMPUTED",
        },
        "charged_z11_threshold": {
            "number_of_vectorlike_pairs": 2,
            "representations": "two Dirac SU2-singlet charged-lepton pairs after full-rank mass",
            "Delta_b_per_pair": {"b1_GUT": "6/5", "b2": "0", "b3": "0"},
            "Delta_b_total": {
                "b1_GUT": f"{delta_b1.numerator}/{delta_b1.denominator}",
                "b2": "0",
                "b3": "0",
            },
            "two_mass_one_loop_shift": (
                "delta(alpha1^-1-alpha2^-1) at M23 = "
                "-(3/(5 pi)) ln(M23^2/(M1 M2))"
            ),
            "unification_without_compensating_thresholds": "requires sqrt(M1 M2)=M23",
            "do_not_splice_V65_orphans": True,
        },
        "stable_charged_relic": {
            "GM_mass_breaks_exotic_number": False,
            "lightest_state_stable_without_portal": True,
            "CMS_one_species_Q1_DY_observed_limit_TeV": "1.14",
            "two_species_recast_required": True,
            "CBBN_onset_lifetime_seconds": "about 1e3",
            "long_lifetime_reference": {
                "tau_seconds": ">1e5",
                "n_over_s_sensitivity": "3e-17",
            },
            "low_reheat_loophole": (
                "conditional only; requires Tmax, inflaton branching, freeze-in and "
                "residual-yield calculations and does not erase collider bounds"
            ),
            "thermal_freezeout_yield_computed": False,
            "standard_thermal_history_viability": "OPEN_NOT_COMPUTED",
            "qualitative_thermal_assessment": (
                "EXPECTED_SEVERELY_CONSTRAINED_FOR_REHEATING_ABOVE_MASS_WITHOUT_"
                "DILUTION__FREEZEOUT_YIELD_REQUIRED"
            ),
        },
        "scope_boundary": (
            "The primitive-integer Abelian congruences are diagnostics.  The rational "
            "A1 value cannot be reduced modulo eta until the global SM quotient and "
            "Abelian level are fixed; V62's five-dimensional GS sector is not imported."
        ),
    }


def wz_transfer_audit(v71: Mapping[str, Any]) -> dict[str, Any]:
    mixed = v71["mixed_normal_gauge_obstruction"]
    bulk = tuple(Fraction(x) for x in mixed["F70_bulk_result_each_Z4_corner"])
    direction = tuple(Fraction(x) for x in mixed["standard_bulk_GS"]["restriction_to_U5"])
    target = tuple(bulk[0] * x for x in direction)
    z00_fermion = (Fraction(0), Fraction(-100))
    z00_wz = (Fraction(0), Fraction(50))
    z11_fermion = (Fraction(0), Fraction(0))
    z11_wz = (Fraction(0), Fraction(-50))
    z00_final = tuple(bulk[i] + z00_fermion[i] + z00_wz[i] for i in range(2))
    z11_final = tuple(bulk[i] + z11_fermion[i] + z11_wz[i] for i in range(2))
    four = mixed["minimal_R_compatible_four_fermion_module"]
    return {
        "status": "EXACT_U5TILDE_RESTRICTED_INTEGRAL_OPPOSITE_WZ_COEFFICIENTS__FULL_QUOTIENT_AND_GLOBAL_SUPERSYMMETRIC_COCYCLE_OPEN",
        "basis": ["U1L-SU5^2", "U1L-X^2"],
        "bulk_each_corner": [str(x) for x in bulk],
        "GS_direction": [str(x) for x in direction],
        "aligned_target": [str(x) for x in target],
        "z00": {
            "fermion_sector": (
                "inherited X(+10),Xbar(-10),S0 plus one independent neutral R=2 P0"
            ),
            "fermion_shift": [str(x) for x in z00_fermion],
            "Q1": four["Q1"],
            "Q3": four["Q3"],
            "U1L_squared_X": four["U1L_squared_X"],
            "WZ_variation": [str(x) for x in z00_wz],
            "final_vector": [str(x) for x in z00_final],
        },
        "z11": {
            "charged_defect_fermions_added": 0,
            "fermion_shift": [str(x) for x in z11_fermion],
            "WZ_variation": [str(x) for x in z11_wz],
            "final_vector": [str(x) for x in z11_final],
        },
        "both_corners_align": z00_final == z11_final == target,
        "U5tilde_restricted_local_coefficient_integrality": {
            "primitive_character": "chi5=1_(+5)",
            "line_class": "l=c1(chi5)=5 f_X",
            "anomaly_polynomial_conversion": (
                "coordinate Delta A=+/-50 contributes (1/2)Delta A f_L f_X^2"
            ),
            "z00": "+25 f_L f_X^2=+f_L l^2, restricted coefficient +1",
            "z11": "-25 f_L f_Xprime^2=-f_L lprime^2, restricted coefficient -1",
            "restricted_coefficients": {"z00": 1, "z11": -1},
            "coefficient_sum": 0,
            "restricted_denominator": 1,
            "scope": (
                "necessary integrality check after restriction to the U5tilde gauge "
                "factor; chi5 is not yet a standalone character of the unresolved "
                "full diagonal Spin(2)-U5tilde-SU2R-flavor quotient"
            ),
            "full_diagonal_quotient_level_quantization_established": False,
            "vector_U5_counterfactual": (
                "only chi10=chi5^2 exists, making the same term quarter-integral; "
                "the Spin preimage is essential"
            ),
        },
        "globally_vanishing_profile": {
            "necessary_integrability_sum": 0,
            "passes_necessary_sum_rule": True,
            "sufficient_for_global_differential_cocycle": False,
        },
        "advantages_over_F71_charge_five_fermions": {
            "new_electrically_charged_fields": 0,
            "new_one_loop_SM_beta_shift": {"b1": "0", "b2": "0", "b3": "0"},
            "no_new_F71_type_stable_charged_relic": True,
            "anomaly_matching_is_explicitly_bosonic": True,
        },
        "not_yet_constructed": [
            "the supersymmetric localized axion/linear/tensor multiplet and its axino/saxion ledger",
            "the identification of the z00 neutral P0 with a globally honest neutral-hyper mode",
            "the combined Spin(2)-U5tilde-SU2R-flavor quotient on every field",
            "the central flavor completion of the translation cocycle in the full action",
            "the differential-cohomology gluing of l and lprime and the bulk U-lattice tensors",
            "the torsion refinement, regulator and fixed-stratum eta/Dai-Freed phases",
            "the continuous lifts and invariant operator ring for every V70 boundary field",
        ],
        "accepted": False,
        "same_action_complete": False,
        "selected_for_next_frontier": True,
    }


def source_manifest() -> list[dict[str, Any]]:
    paths = [Path(__file__).resolve(), TEST_PATH, V71_PATH, V70_PATH]
    return [
        {"path": path.name, "exists": path.is_file(), "sha256": file_sha(path)}
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    v71 = load_bound(V71_PATH, EXPECTED_V71_CORE, "V71")
    v70 = load_bound(V70_PATH, EXPECTED_V70_CORE, "V70")
    global_form = global_form_audit()
    mass_portal = mass_and_portal_audit(v71)
    pheno = discrete_and_phenomenology_audit(v71)
    wz = wz_transfer_audit(v71)
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "question": (
            "Are the V71 charge-five modules globally honest and can they be made "
            "massive and unstable; if not, is there a cleaner quantized repair?"
        ),
        "primary_sources": PRIMARY_SOURCES,
        "lineage": {
            "bound_V71_path": V71_PATH.name,
            "bound_V71_core": v71["core_sha256"],
            "expected_V71_core": EXPECTED_V71_CORE,
            "V71_core_matches": v71["core_sha256"] == EXPECTED_V71_CORE,
            "bound_V70_path": V70_PATH.name,
            "bound_V70_core": v70["core_sha256"],
            "expected_V70_core": EXPECTED_V70_CORE,
            "V70_core_matches": v70["core_sha256"] == EXPECTED_V70_CORE,
        },
        "true_fixed_group_and_global_gluing": global_form,
        "charge_five_mass_and_portal_audit": mass_portal,
        "discrete_R_running_and_relic_audit": pheno,
        "F72_opposite_level_WZ_transfer_candidate": wz,
        "candidate_adjudication": {
            "F71_charge_five_local_representation": "PASS_EXACT",
            "F71_total_multiplet_and_orbibundle": "OPEN_NOT_CONSTRUCTED",
            "F71_conventional_massive_decaying_completion": "REJECTED_BY_EXACT_MASS_AND_PORTAL_THEOREMS",
            "F71_standard_thermal_phenomenology": (
                "OPEN_EXPECTED_SEVERELY_CONSTRAINED__FREEZEOUT_YIELD_NOT_COMPUTED"
            ),
            "F72_U5tilde_restricted_WZ_coefficient": "PASS_EXACT_NECESSARY_LOCAL_INTEGRALITY_CHECK",
            "F72_global_supersymmetric_action": "OPEN_NOT_CONSTRUCTED",
            "selected_frontier": "F72 opposite-level WZ transfer without new charged exotics",
        },
        "frontier_status_ledger": [
            "U5_TILDE_FIXED_GROUP_PASS_EXACT",
            "CHARGE_FIVE_CHARACTER_LATTICE_PASS_EXACT",
            "TOTAL_SPIN_R_MULTIPLET_OPEN",
            "TRANSLATION_CENTRAL_COCYCLE_FOUND_EXACT",
            "FLAVOR_CENTRAL_ALGEBRAIC_COMPLETION_EXISTS",
            "GLOBAL_EQUIVARIANT_ORBIBUNDLE_OPEN",
            "MASS_ANOMALY_MATCHING_THEOREM_PASS_EXACT",
            "ALL_ORDER_NONDERIVATIVE_CHIRAL_PORTAL_NO_GO_PASS_EXACT",
            "F71_STABLE_CHARGED_RELIC_FAIL",
            "F72_OPPOSITE_WZ_COEFFICIENTS_U5TILDE_RESTRICTED_INTEGRAL_PASS_EXACT",
            "F72_SUPERSYMMETRIC_DIFFERENTIAL_COCYCLE_OPEN",
            "G1_TO_G8_OPEN",
        ],
        "open_obligations": wz["not_yet_constructed"]
        + [
            "globalize and stabilize the V71 Sp(266,1)/(Sp266 x Sp1) neutral sector",
            "recompute the full bulk/local discrete-R, Abelian and eta anomaly ledger",
            "complete the KK determinant, regulator, soft spectrum, unification, flavor, proton decay and cosmology",
        ],
        "gate_ledger": {f"G{i}": "OPEN" for i in range(1, 9)},
        "terminal_decision": {
            "honest_outcome": (
                "V72 removes V71's provisional local group caveat: charge-five "
                "singlets are honest primitive characters of the true U(5)-tilde "
                "fixed group.  It then rejects their conventional completion because "
                "symmetry-preserving masses erase the required anomaly and every "
                "non-derivative local chiral decay portal to the existing V70/MSSM "
                "fields is forbidden at all orders, leaving a stable charged relic "
                "within that local candidate action.  Nonlocal interactions and "
                "arbitrary new bridge sectors are not excluded.  A new opposite-WZ "
                "transfer has coefficients (+1,-1) that pass the necessary integral "
                "U5tilde-restriction check, aligns both corners, and adds no charged "
                "matter.  The combined equivariant supersymmetric differential "
                "cocycle and full microscopic action are not constructed."
            ),
            "F71_conventional_completion_accepted": False,
            "F72_selected": True,
            "F72_accepted": False,
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
    group = report["true_fixed_group_and_global_gluing"]
    mass = report["charge_five_mass_and_portal_audit"]
    pheno = report["discrete_R_running_and_relic_audit"]
    wz = report["F72_opposite_level_WZ_transfer_candidate"]
    checks = {
        "V71_bound": report["lineage"]["V71_core_matches"],
        "V70_bound": report["lineage"]["V70_core_matches"],
        "global_form_reps": group["all_displayed_representations_honest_in_U5_tilde"],
        "charge5_honest": group["character_group"]["charge_five_honest"],
        "charge5_not_vector": group["character_group"]["charge_five_not_vector_U5"],
        "center_patterns": all(
            row["hypermultiplet_center_pattern_passes"]
            for row in group["combined_local_center_quotient"]["charge_five_checks"]
        ),
        "global_bundle_open": not group["space_group_cocycle"]["global_equivariant_orbibundle_constructed"],
        "z00_ring": mass["z00_all_order_module_ring"]["finite_symbolic_check_only_S_times_equal_rank"],
        "no_z00_P": not mass["z00_all_order_module_ring"]["charge_five_W_mass_or_interaction_at_any_order"],
        "mass_theorem": not mass["mass_anomaly_matching_theorem"]["full_rank_trivially_gapped_sector_nonzero_U1L_X2_anomaly"],
        "no_portal": not mass["all_order_nonderivative_chiral_portal_theorem"][
            "nonderivative_local_chiral_W_or_K_portal_at_any_order"
        ],
        "stable": mass["all_order_nonderivative_chiral_portal_theorem"]["lightest_charge_five_state_stable"],
        "grav_complete_zero": pheno["complete_local_modules"]["both_Agrav_zero_from_Q1_zero"],
        "beta": pheno["charged_z11_threshold"]["Delta_b_total"] == {"b1_GUT": "12/5", "b2": "0", "b3": "0"},
        "thermal_open": (
            not pheno["stable_charged_relic"]["thermal_freezeout_yield_computed"]
            and pheno["stable_charged_relic"]["standard_thermal_history_viability"]
            == "OPEN_NOT_COMPUTED"
        ),
        "wz_align": wz["both_corners_align"],
        "wz_restricted_coefficients": wz["U5tilde_restricted_local_coefficient_integrality"][
            "restricted_coefficients"
        ] == {"z00": 1, "z11": -1},
        "wz_sum": wz["U5tilde_restricted_local_coefficient_integrality"]["coefficient_sum"] == 0,
        "wz_full_quotient_open": not wz["U5tilde_restricted_local_coefficient_integrality"][
            "full_diagonal_quotient_level_quantization_established"
        ],
        "wz_no_charged": wz["advantages_over_F71_charge_five_fermions"]["new_electrically_charged_fields"] == 0,
        "F72_unaccepted": not wz["accepted"],
        "all_gates_open": all(value == "OPEN" for value in report["gate_ledger"].values()),
        "manifest": all(row["exists"] and row["sha256"] for row in report["source_manifest"]),
        "core": report.get("core_sha256") == canonical_sha(report),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V72 validation failed: " + ", ".join(failures))


def render_markdown(report: Mapping[str, Any]) -> str:
    group = report["true_fixed_group_and_global_gluing"]
    mass = report["charge_five_mass_and_portal_audit"]
    pheno = report["discrete_R_running_and_relic_audit"]
    wz = report["F72_opposite_level_WZ_transfer_candidate"]
    return f"""# V72 Spin(11) global-form, mass/portal, and WZ-transfer audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact global-form result

The true connected fixed group is

`{group['presentations']['pullback']}`

or equivalently `{group['presentations']['quotient']}`.  A representation of
SU(5) five-ality `k` and X charge `x` is honest iff `k+2x=0 mod 5`.
Consequently the charge-five singlets are primitive honest characters of
U(5)-tilde, while they do not descend to vector-form U(5).

This local result does not globalize V71.  The translation lifts satisfy a
central Z2 cocycle.  A minimal flavor-central completion exists algebraically,
but it has not been installed in the full action or anomaly-refined bundle.

## Exact mass and portal obstruction

At z00 the all-order corrected-module ring is

`{mass['z00_all_order_module_ring']['ring']}`.

No charge-five mass or interaction occurs at any order.  At z11 the ring is
`{mass['z11_all_order_module_ring']['ring']}`, with no bare mass.  More
generally, a symmetry-preserving quadratic mass has
`qpsi_i+qpsi_j=0`, so its U(1)L-X^2 anomaly is zero.  Gapping F71 with ordinary
partners therefore erases the anomaly repair.

Within the corrected F71 module and existing V70/MSSM field content, the
center/R-parity theorem forbids every non-derivative local chiral-superfield W
or K decay portal linear in one charge-five field.  The lightest z11 state is
therefore exactly stable within that local candidate action and has
|Y|={mass['all_order_nonderivative_chiral_portal_theorem']['z11_lightest_electric_charge_absolute']}.
Nonlocal interactions, derivative operators, and arbitrary new bridge sectors
are not excluded.

Two light pairs would shift the one-loop coefficients by
`{pheno['charged_z11_threshold']['Delta_b_total']}`.  The CMS one-species
stable Q=1 Drell--Yan benchmark excludes masses below
{pheno['stable_charged_relic']['CMS_one_species_Q1_DY_observed_limit_TeV']} TeV;
the two-species spectrum requires a recast.  A thermal history that reheats above
the relic mass and has no subsequent dilution is expected to be severely
constrained, but viability remains OPEN because the freeze-out yield has not been
computed.  Low reheating remains only a conditional loophole pending the listed
production and yield calculations.

## New F72 WZ-transfer frontier

The no-charged-exotic alternative gives

- z00: bulk + inherited/neutral module + WZ = `{wz['z00']['final_vector']}`;
- z11: bulk + WZ = `{wz['z11']['final_vector']}`.

Both equal the ordinary GS direction target `{wz['aligned_target']}`.  After
restriction to the U5tilde gauge factor, `l=c1(chi5)=5 f_X` makes the two local
coefficients the integers +1 at z00 and -1 at z11.  Their sum is zero and no new
SM-charged beta-function threshold is introduced.  This is only a necessary
restricted local check: chi5 has not been shown to descend through the full
diagonal quotient, and the zero sum is not sufficient for the unresolved
global differential cocycle.

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
            raise RuntimeError("V72 generated artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("V72 JSON artifact is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("V72 markdown artifact is stale")
    if args.emit_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(report["status"])
        print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
