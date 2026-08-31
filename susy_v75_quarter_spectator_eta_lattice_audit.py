#!/usr/bin/env python3
"""V75 correlated eta representatives and quarter-spectator lattice audit.

V74 constructed the primitive common-K bridge but proved that ordinary and
free-curvature half-level multiples of that bridge cannot change the forced
quarter endpoint class.  V75 now constructs explicit *correlated* quotient
fermion index representatives of that class and asks whether their spectator
curvatures can be removed by the standard neutral supersymmetric free-field
image.

There is a real advance: two differences of honest line-fermion Dai--Freed
theories define a closed-spin phase with curvature
``nu*ell^2 + nu*(nu^2-p1)/12``.  Thus the previously unnamed eta possibility
has an exact correlated representative.  It does not finish the theory.  The
gravitational spectator is compulsory, and a mod-eight argument proves that
arbitrary signed integer/half-integer combinations of the standard neutral
Spin(2) singlet and SU(2)_R-doublet fermion determinants cannot produce its
inverse without additional curvature.  The same argument excludes clean
isolated ``nu*c2(R)`` and ``nu^3/4`` spectators in that scoped image.

An exact gauge-charged level-four redesign removes the quarter coset and admits
conditional proton-safe cross-mass operators.  Its vector-type SU(2)_R sector,
VEV action, neutral masses, anomaly matching and orbifold caps are not built.
A closed-index period theorem also excludes every honest localized Weyl or
standard half-eta module whose other gauge/R curvature cancels cleanly from
repairing the bound V71 residue.  Correlated higher-spin eta theories and
interacting invertible sectors are not classified.  No gate is closed.
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
V71_ROUTE_PATH = ROOT / "SUSY_V71_SPIN11_NORMAL_BUNDLE_EQUIVARIANT_GS_AUDIT.json"
V74_ROUTE_PATH = ROOT / "SUSY_V74_SPIN11_BRIDGE_ENDPOINT_OBSTRUCTION_AUDIT.json"
V74_MASTER_PATH = ROOT / "SUSY_V74_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
OUT_JSON = ROOT / "SUSY_V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT.json"
OUT_MD = ROOT / "SUSY_V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v75_quarter_spectator_eta_lattice_audit.py"

EXPECTED_CORES = {
    "v71_route": "0162828ebd2b1e28d4fcbcf4ea1e6c61178d305cec79abd6d36a55719bb0f1ea",
    "v74_route": "853833b9206e0eacb3a57ef72b7615c4d8c2b28b87a99155c93dc46d803e5603",
    "v74_master": "3d51a7c13060dad547d8bedffb7f8299c0e24e67a21c8e121dd98b0efcbc57f9",
}

SCHEMA = "susy_v75_quarter_spectator_eta_lattice_audit_v1"
VERSION = "V75"
DATE = "2026-08-31"
STATUS = (
    "V75_QUARTER_SPECTATOR_ETA_LATTICE_AUDIT__V74_ROUTE_AND_MASTER_CORES_BOUND__"
    "HONEST_LINE_ETA_REPRESENTATIVE_EXACT__ETA_CURVATURE_P_PLUS_GRAVITY_SPECTATOR__"
    "COMMON_NU_AB_BRIDGE_UNCHANGED__CORRELATED_R_AND_NORMAL_MODULES_EXACT__"
    "BOUND_V71_EQUAL_CORNER_RESIDUE_MISMATCH_EXACT__"
    "STANDARD_NEUTRAL_FREE_ETA_INVERSE_SPECTATOR_MOD8_NO_GO__"
    "CLEAN_GAUGE_CHARGED_PARENT_RESIDUE_INVERSE_INDEX_PERIOD_NO_GO__"
    "CORRELATED_LEVEL4_SPECTRUM_AND_MASS_OPERATOR_ALGEBRA_EXACT__"
    "VECTOR_TYPE_VEV_ACTION_AND_BOUND_PARENT_RESIDUE_OPEN__"
    "LEVEL4_REDESIGN_SELECTED_UNACCEPTED__G1_TO_G8_OPEN"
)


def canonical_sha(value: Any) -> str:
    body = copy.deepcopy(value)
    if isinstance(body, dict):
        body.pop("core_sha256", None)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
                "the exponentiated eta invariant is a determinant-line section "
                "with gluing and variation laws; this supports the exact closed-spin "
                "virtual line phase, not its missing orbifold extension"
            ),
        },
        {
            "title": "Anomaly Inflow and the eta-Invariant",
            "url": "https://arxiv.org/abs/1909.08775",
            "scope": (
                "Dai--Freed/eta phases supply the global anomaly theory of fermion "
                "determinants; this does not identify the V75 microscopic sector"
            ),
        },
        {
            "title": "Reflection positivity and invertible topological phases",
            "url": "https://arxiv.org/abs/1604.06527",
            "scope": (
                "invertible phases are classified using bordism spectra; the exact "
                "Spin-SU2R-U5 orbifold bordism group is not computed here"
            ),
        },
        {
            "title": "Anomalies on Six Dimensional Orbifolds",
            "url": "https://arxiv.org/abs/hep-th/0612212",
            "scope": (
                "equivariant localized spin-half anomalies and remnant Lorentz "
                "charges; higher-spin and global eta data require separate treatment"
            ),
        },
        {
            "title": "Anomalies on Orbifolds",
            "url": "https://arxiv.org/abs/hep-th/0103135",
            "scope": (
                "five-dimensional chiral boundary conditions split anomaly onto "
                "orbifold fixed planes; used to bound the permissive half-copy "
                "convention, not to construct the V75 six-dimensional defect"
            ),
        },
        {
            "title": "Higher dimensional supersymmetry in 4D superspace",
            "url": "https://arxiv.org/abs/hep-th/0101233",
            "scope": (
                "five-dimensional supersymmetric Chern--Simons and anomaly-inflow "
                "terms admit 4D N=1 superspace descriptions; the normal Lorentz "
                "connection is not thereby promoted to an ordinary vector multiplet"
            ),
        },
        {
            "title": "Five-dimensional supersymmetric Chern-Simons action as a hypermultiplet quantum correction",
            "url": "https://arxiv.org/abs/hep-th/0609078",
            "scope": (
                "massive hypermultiplets generate sign-dependent supersymmetric "
                "Chern--Simons terms; V75 deliberately allows an even larger signed "
                "half-level lattice in its neutral no-go"
            ),
        },
        {
            "title": "Quantization of anomaly coefficients in 6D N=(1,0) supergravity",
            "url": "https://arxiv.org/abs/1711.04777",
            "scope": (
                "global gauge form and cocharacter lattices constrain anomaly "
                "quantization; it does not construct the singular V75 defect"
            ),
        },
        {
            "title": "Anomaly interplay in U(2) gauge theories",
            "url": "https://arxiv.org/abs/2001.07731",
            "scope": (
                "quotient/generalized-spin structures correlate perturbative and "
                "global anomalies; used as structural precedent, not a U5 calculation"
            ),
        },
        {
            "title": "Off-Shell N=(1,0) Linear Multiplets in Six Dimensions",
            "url": "https://arxiv.org/abs/2010.14655",
            "scope": (
                "the vector-linear density and four-form multiplet support V74's "
                "local scaffold, not the missing equivariant eta completion"
            ),
        },
        {
            "title": "Supersymmetry anomalies in N=1 conformal supergravity",
            "url": "https://arxiv.org/abs/1902.06717",
            "scope": (
                "R and supersymmetry anomalies obey coupled Wess--Zumino consistency; "
                "the paper is four-dimensional conformal supergravity, not this model"
            ),
        },
        {
            "title": "Interacting Topological Superconductors and possible Origin of 16n Chiral Fermions in the Standard Model",
            "url": "https://arxiv.org/abs/1402.4151",
            "scope": (
                "sixteen-fold symmetric mass generation is model- and symmetry-"
                "dependent and is not an automatic gap for the V75 quotient module"
            ),
        },
    ]


def source_manifest() -> list[dict[str, Any]]:
    return [
        {"url": row["url"], "title": row["title"], "scope": row["scope"]}
        for row in source_catalog()
    ]


def line_index_cubic(line: Sequence[Fraction]) -> dict[str, Fraction]:
    """Index of a line with c1=a*ell+b*nu, retaining relevant monomials."""
    a, b = map(Fraction, line)
    return {
        "ell3": a**3 / 6,
        "nu_ell2": a * a * b / 2,
        "nu2_ell": a * b * b / 2,
        "nu3": b**3 / 6,
        "ell_p1": -a / 24,
        "nu_p1": -b / 24,
    }


def add_polynomials(*rows: Mapping[str, Fraction]) -> dict[str, Fraction]:
    keys = sorted({key for row in rows for key in row})
    return {key: sum(Fraction(row.get(key, 0)) for row in rows) for key in keys}


def scale_polynomial(row: Mapping[str, Fraction], factor: Fraction) -> dict[str, Fraction]:
    return {key: factor * value for key, value in row.items()}


def eta_line_representative() -> dict[str, Any]:
    plus = line_index_cubic((1, Fraction(1, 2)))
    minus = line_index_cubic((1, Fraction(-1, 2)))
    curvature = add_polynomials(
        scale_polynomial(plus, Fraction(2)),
        scale_polynomial(minus, Fraction(-2)),
    )
    nonzero = {key: fstr(value) for key, value in curvature.items() if value}
    diagonal_p = Fraction(25, 4)
    p1_cp3 = 4
    spectator = Fraction(1 - p1_cp3, 12)
    cp3_plus_index = Fraction(3**3, 6) - Fraction(3 * p1_cp3, 24)
    cp3_minus_index = Fraction(2**3, 6) - Fraction(2 * p1_cp3, 24)
    cubic_degree = 3
    cubic_p1_period = -12
    cubic_plus_index = Fraction(3**3 * cubic_degree, 6) - Fraction(
        3 * cubic_p1_period, 24
    )
    cubic_minus_index = Fraction(2**3 * cubic_degree, 6) - Fraction(
        2 * cubic_p1_period, 24
    )
    return {
        "status": (
            "EXACT_CLOSED_SMOOTH_SPIN_H_DAI_FREED_LINE_RATIO__"
            "FULL_BORDISM_CLASSIFICATION_AND_ORBIFOLD_EQUIVARIANCE_OPEN"
        ),
        "scope_without_optional_flavor_quotient": True,
        "honest_endpoint_lines": {
            "L_plus": {
                "c1": "ell+nu/2",
                "weight_n_x_r": (1, 5, 0),
                "center_checks": {"U5tilde": "0+2*5=0 mod5", "diagonal": "1+5+0=0 mod2"},
            },
            "L_minus": {
                "c1": "ell-nu/2",
                "weight_n_x_r": (-1, 5, 0),
                "center_checks": {"U5tilde": "0+2*5=0 mod5", "diagonal": "-1+5+0=0 mod2"},
            },
        },
        "index_curvature_combination": "C_eta=2[I6(L_plus)-I6(L_minus)]",
        "virtual_sector": "2[D_L_plus]-2[D_L_minus] in fermion group completion",
        "tau_normalization": "tau(D)=exp[2 pi i xi(D)], xi=(eta+dim ker D)/2",
        "closed_five_dimensional_phase": (
            "Z_eta(Y5)=exp{2 pi i*2[xi(D_L_plus)-xi(D_L_minus)]}="
            "[tau(D_L_plus)/tau(D_L_minus)]^2, up to chirality/inverse convention"
        ),
        "closed_smooth_spin_H_Dai_Freed_phase_constructed": True,
        "full_H_bordism_classification_computed": False,
        "Z4_equivariant_orbifold_extension_constructed": False,
        "line_index": "I6(w)=w^3/6-w p1(T4)/24",
        "curvature": "C_eta=nu ell^2+nu(nu^2-p1(T4))/12",
        "computed_coefficients": nonzero,
        "spectator": "S_eta=nu(nu^2-p1(T4))/12",
        "CP3_diagonal_witness": {
            "nu": 1,
            "ell": "5/2",
            "p1_TCP3": p1_cp3,
            "L_plus_c1": 3,
            "L_minus_c1": 2,
            "I6_L_plus": fstr(cp3_plus_index),
            "I6_L_minus": fstr(cp3_minus_index),
            "P_period": fstr(diagonal_p),
            "S_eta_period": fstr(spectator),
            "C_eta_period": fstr(diagonal_p + spectator),
        },
        "spin_cubic_threefold_witness": {
            "construction": "smooth degree-three hypersurface X3 in CP4",
            "spin_reason": "c1(TX3)=2h, hence w2=0",
            "nu3_period_X": cubic_degree,
            "nu_p1_period_Y": cubic_p1_period,
            "L_plus_c1": "3h",
            "L_minus_c1": "2h",
            "I6_L_plus": fstr(cubic_plus_index),
            "I6_L_minus": fstr(cubic_minus_index),
            "C_eta_period": fstr(2 * (cubic_plus_index - cubic_minus_index)),
        },
        "diagonal_spin_normal_gravity_lattice": {
            "witness_rows_X_Y": [[1, 4], [3, -12]],
            "determinant_absolute": 24,
            "congruence": "Y=4X mod24",
            "dual_integrality_for_a_nu3_plus_b_nu_p1": [
                "24b in Z",
                "a+4b in Z",
            ],
            "C_eta_diagonal_coefficients_a_b": ["19/3", "-1/12"],
            "C_eta_passes_dual_lattice": True,
        },
        "z11_inverse": (
            "-C_eta(ellprime)=-nu ellprime^2-"
            "nu(nu^2-p1(T4))/12"
        ),
        "common_overlap_difference": (
            "C_eta(ell)-C_eta(ellprime)=nu(ell^2-ellprime^2)=nu A B"
        ),
        "V74_common_bridge_changed": False,
        "pure_P_refinement_constructed": False,
        "reason_not_pure": "the eta representative necessarily carries S_eta",
        "optional_flavor_quotient": {
            "used_in_displayed_formula": False,
            "minimal_flavor_charge": 1,
            "additional_center_check": "x+f=5+1=0 mod2",
            "honest_lines": "Lhat_plus/minus have c1=ell+v+/-nu/2",
            "required_change": (
                "give both lines odd flavor charge and replace ell by ell+v; "
                "the overlap becomes nu B(A+2v)"
            ),
            "complete_flavor_anomaly_ledger": False,
        },
    }


def bound_parent_residue_audit(v71: Mapping[str, Any]) -> dict[str, Any]:
    bound = v71["neutral_266_phase_classification"][
        "bulk_gravitational_trace_factorization"
    ]
    if bound["unique_Delta"] != -10:
        raise RuntimeError("V71 bound parent residue changed")
    ahat = v71["spin_half_equivariant_index"]["definitions"]["Ahat_T4"]
    if ahat != "1-p/24+...":
        raise RuntimeError("V71 Ahat convention changed")
    return {
        "status": "EXACT_EQUAL_CORNER_PARENT_RESIDUE_CANNOT_MATCH_ANTISYMMETRIC_ETA_SPECTATOR",
        "bound_V71_input": bound["factored_polynomial"],
        "bound_V71_Ahat_T4_convention": ahat,
        "notation": "p=p1(T4), so p1(T6)|fixed=p+nu^2",
        "equal_corner_residue": "R=-(1/8)nu[p+nu^2] at z00 and z11",
        "eta_spectator_profile": {
            "z00": "+S_eta=+nu(nu^2-p)/12",
            "z11": "-S_eta=-nu(nu^2-p)/12",
        },
        "combined_residuals": {
            "z00_R_plus_S": "-nu[nu^2+5p]/24",
            "z11_R_minus_S": "-nu[5nu^2+p]/24",
        },
        "CP3_periods": {
            "R_each_corner": "-5/8",
            "S_z00": "-1/4",
            "S_z11": "+1/4",
            "R_plus_S_z00": "-7/8",
            "R_minus_S_z11": "-3/8",
        },
        "primitive_AB_bridge_contains_normal_gravity_curvature": False,
        "equal_nonzero_parent_residue_cancelled": False,
        "orientation_independent_reason": (
            "the eta spectators are antisymmetric while the bound parent residue "
            "is equal at the two corners"
        ),
    }


def singlet_polynomial(q: Fraction) -> dict[str, Fraction]:
    return {
        "nu3": q**3 / 6,
        "nu_c2R": Fraction(0),
        "nu_p1": -q / 24,
    }


def doublet_polynomial(q: Fraction) -> dict[str, Fraction]:
    return {
        "nu3": q**3 / 3,
        "nu_c2R": -q,
        "nu_p1": -q / 12,
    }


def correlated_fermion_modules() -> dict[str, Any]:
    charged = scale_polynomial(singlet_polynomial(Fraction(1, 2)), Fraction(4))
    r_neutral = scale_polynomial(doublet_polynomial(Fraction(-1, 2)), Fraction(2))
    n_neutral = scale_polynomial(singlet_polynomial(Fraction(-1)), Fraction(2))
    r_total = add_polynomials(charged, r_neutral)
    n_total = add_polynomials(charged, n_neutral)

    d_doublets = scale_polynomial(doublet_polynomial(Fraction(-1, 2)), Fraction(2))
    d_singlets = scale_polynomial(singlet_polynomial(Fraction(1)), Fraction(2))
    d_total = add_polynomials(d_doublets, d_singlets)

    return {
        "status": "EXACT_HONEST_QUOTIENT_FREE_FERMION_CORRELATED_MODULES",
        "R_completion": {
            "content": (
                "2 x [1_(+5),qL=+1/2]+2 x [1_(-5),qL=+1/2]+"
                "2 x [SU2R doublet,qL=-1/2]"
            ),
            "complex_Weyl_count": 8,
            "all_full_quotient_center_checks_pass": True,
            "SU2R_doublet_count": 2,
            "Witten_SU2_global_parity_even": True,
            "normal_moments_Q1_Q3": ["0", "0"],
            "normal_X2": 50,
            "polynomial_coefficients_beyond_gauge": {
                key: fstr(value) for key, value in r_total.items()
            },
            "complete_polynomial": "C_R=nu[ell^2+c2(R)]",
            "diagonal_period": 6,
            "pure_gauge_target_obtained": False,
        },
        "normal_line_completion": {
            "content": (
                "2 x [1_(+5),qL=+1/2]+2 x [1_(-5),qL=+1/2]+"
                "2 x [singlet,qL=-1]"
            ),
            "complex_Weyl_count": 6,
            "all_full_quotient_center_checks_pass": True,
            "normal_moments_Q1_Q3": ["0", "-3/2"],
            "normal_X2": 50,
            "polynomial_coefficients_beyond_gauge": {
                key: fstr(value) for key, value in n_total.items()
            },
            "complete_polynomial": "C_N=nu[ell^2-nu^2/4]",
            "diagonal_period": 6,
            "pure_gauge_target_obtained": False,
        },
        "integral_spectator_shift_module": {
            "content": "2 x [SU2R doublet,qL=-1/2]+2 x [singlet,qL=+1]",
            "complex_Weyl_count": 6,
            "all_full_quotient_center_checks_pass": True,
            "SU2R_doublet_count": 2,
            "Witten_SU2_global_parity_even": True,
            "polynomial_coefficients": {
                key: fstr(value) for key, value in d_total.items()
            },
            "complete_polynomial": "D=C_R-C_N=nu[c2(R)+nu^2/4]",
            "ordinary_integral": True,
        },
        "conclusion": (
            "honest free fermions realize the correlated completions and their "
            "integral difference, not an isolated inverse quarter spectator"
        ),
    }


def standard_neutral_free_eta_no_go() -> dict[str, Any]:
    return {
        "status": "EXACT_MOD8_NO_GO_IN_STANDARD_NEUTRAL_FREE_ETA_IMAGE",
        "scope": (
            "finite signed combinations of ordinary 4D Weyl determinants and "
            "standard 5D parity/eta half-copies, using gauge-neutral Spin2 singlets "
            "and SU2R doublets only"
        ),
        "allowed_charges": {
            "SU2R_singlet": "q=m in Z",
            "SU2R_doublet": "q=n/2 with n odd",
            "index_unit": "I_s and I_d denote one positive complex 4D Weyl determinant",
            "ordinary_4D_determinant_multiplicity": "t in Z",
            "signed_multiplicity": "t=u/2 with u in Z (an overgenerous half-level lattice)",
            "five_dimensional_convention": (
                "an individual parity/eta half-copy is permitted at t=+/-1/2; "
                "a regulator mass-sign difference is integer"
            ),
        },
        "single_field_polynomials": {
            "singlet": "I_s=q^3 nu^3/6-q nu p1(T4)/24",
            "doublet": (
                "I_d=q^3 nu^3/3-q nu c2(R)-q nu p1(T4)/12"
            ),
        },
        "modular_identities": ["n^3=n mod8 for odd n", "m^3=m mod2 for every integer m"],
        "pure_R_spectator": {
            "target": "-nu c2(R), with zero nu^3 and nu p1(T4)",
            "necessary_equations": [
                "sum_d u n=4",
                "sum_s u m=-4",
                "sum_d u n^3+4 sum_s u m^3=0",
            ],
            "cubic_left_mod8": 4,
            "cubic_right_mod8": 0,
            "solution_exists": False,
            "both_signs_excluded": True,
        },
        "pure_normal_quarter": {
            "target": "+/- nu^3/4, with zero c2(R) and nu p1(T4)",
            "necessary_linear_equations": ["sum_d u n=0", "sum_s u m=0"],
            "cubic_equation": "sum_d u n^3+4 sum_s u m^3=+/-12",
            "cubic_left_mod8": 0,
            "cubic_right_mod8": 4,
            "solution_exists": False,
        },
        "eta_gravity_spectator": {
            "target": "+/- S_eta=+/-nu(nu^2-p1(T4))/12, with zero c2(R)",
            "one_orientation_equations": [
                "sum_d u n=0",
                "sum_s u m=-4",
                "sum_d u n^3+4 sum_s u m^3=-4",
            ],
            "cubic_left_mod8": 0,
            "cubic_right_mod8": 4,
            "solution_exists": False,
            "both_signs_excluded": True,
        },
        "eta_spectator_plus_bound_V71_residue": {
            "z00_inverse_target_equations": [
                "sum_d u n=0",
                "sum_s u m=-10",
                "sum_d u n^3+4 sum_s u m^3=2",
            ],
            "z11_inverse_target_equations": [
                "sum_d u n=0",
                "sum_s u m=-2",
                "sum_d u n^3+4 sum_s u m^3=10",
            ],
            "cubic_left_mod8": 0,
            "cubic_right_mod8": 2,
            "solution_exists": False,
        },
        "not_a_no_go_for": [
            "gauge-charged modules whose complete gauge anomaly ledger cancels",
            "higher-spin/tangent-twisted eta theories",
            "classical axionic normal/gravitational WZ terms",
            "interacting invertible or noninvertible topological sectors",
        ],
    }


def gauge_charged_neutral_theorem_loophole() -> dict[str, Any]:
    rows = [
        {"representation": "5_(-3)", "k": 1, "x": -3, "r_hw": 1, "n": 2},
        {"representation": "5bar_(+3)", "k": -1, "x": 3, "r_hw": 1, "n": 2},
    ]
    for row in rows:
        row["U5tilde_center_pass"] = (row["k"] + 2 * row["x"]) % 5 == 0
        row["diagonal_center_pass"] = (
            row["n"] + row["x"] + row["r_hw"]
        ) % 2 == 0
    return {
        "status": "EXACT_ODD_X_COUNTEREXAMPLE_TO_EXTENDING_THE_NEUTRAL_MOD8_PREMISE",
        "parity_flip": (
            "n+x+r_hw=0 mod2: for odd x an SU2R doublet has integral q=n/2, "
            "while a singlet has half-integral q"
        ),
        "formal_module": (
            "(5_(-3)+5bar_(+3)) tensor 2_R, q_N=1, signed eta weight t=1/2"
        ),
        "quotient_rows": rows,
        "all_center_checks_pass": all(
            row["U5tilde_center_pass"] and row["diagonal_center_pass"] for row in rows
        ),
        "pure_U5_anomalies_cancel": [
            "SU5^3",
            "X SU5^2",
            "X^3",
            "X-gravity",
            "X c2(R)",
            "nu^2 X",
        ],
        "gauge_independent_curvature": (
            "(5/3)nu^3-5nu c2(R)-(5/12)nu p1(T4)"
        ),
        "neutral_mod8_R_coefficient_evasion": "-5=-1 mod4",
        "surviving_mixed_gauge_curvature": {
            "normal_SU5_squared": (
                "2 nu ch2(5), nonzero; equivalent coefficients depend on trace normalization"
            ),
            "normal_X_squared": "45 nu f_X^2",
        },
        "symmetry_mass_obstruction": (
            "same-normal-charge conjugates are gauge-vectorlike but normal/R-chiral; "
            "opposite normal charges allow an invariant mass but cancel the spectator"
        ),
        "same_action_repair": False,
        "full_odd_X_representation_ring_classified": False,
    }


def clean_parent_residue_index_period_no_go() -> dict[str, Any]:
    inverse_period = Fraction(4 + 1, 8)
    target_q1 = Fraction(-3)
    target_q3 = Fraction(3, 4)
    scaled_n1 = 2 * target_q1
    scaled_n3 = 8 * target_q3
    return {
        "status": (
            "EXACT_REPRESENTATION_INDEPENDENT_CP3_INDEX_PERIOD_NO_GO_FOR_"
            "CLEAN_LOCAL_WEYL_AND_STANDARD_HALF_ETA_PARENT_RESIDUE_INVERSE"
        ),
        "target": {
            "inverse_bound_V71_residue": "+(1/8)nu[p1(T4)+nu^2]",
            "local_Weyl_moments": {
                "Q1": fstr(target_q1),
                "Q3": fstr(target_q3),
            },
            "scaled_n_moments": {"N1_equals_2Q1": fstr(scaled_n1), "N3_equals_8Q3": fstr(scaled_n3)},
        },
        "CP3_full_quotient_witness": {
            "spin": True,
            "admissibility": (
                "the diagonal kappa_D is an honest cocharacter of the full quotient H; "
                "c1=H induces an H bundle although ell=5H/2 and rho=H/2 split fractionally"
            ),
            "nu_period": 1,
            "ell_period": "5/2",
            "c2R_period": "-1/4",
            "p1_TCP3_period": 4,
            "inverse_residue_period": fstr(inverse_period),
        },
        "index_lattices": {
            "finite_integer_virtual_sum_of_honest_localized_complex_Weyl_indices": "Z",
            "permissive_signed_standard_half_eta_sum": "(1/2)Z",
            "inverse_period_belongs_to_integer_lattice": inverse_period.denominator == 1,
            "inverse_period_belongs_to_half_integer_lattice": (
                2 * inverse_period
            ).denominator
            == 1,
            "ordinary_integral_counterterms_change_conclusion": False,
            "level4_completed_endpoint_periods": [24, -24],
            "V74_free_spin_half_bridge_period_shift": "3Z",
        },
        "mod48_singlet_doublet_cross_check": {
            "species_data": (
                "multiplicity m, SU5 dimension d, SU2R component count s=1 or 2, "
                "normal n=2q, X charge x, epsilon=0 or 1"
            ),
            "honesty_parity": "n+x+epsilon=0 mod2",
            "singlet_identity": "for z=n+x even, z^3-4z=0 mod48",
            "doublet_identity": "for z=n+x odd, 2(z^3-z)=0 mod48",
            "summed_identity": (
                "F=N3-4N1-4X1+6(D_n+D_x)=0 mod48 after clean Abelian moments"
            ),
            "clean_constraints": [
                "X1=sum m d s x=0",
                "sum m d s x^3=0",
                "sum m d s n x^2=0",
                "sum m d s n^2 x=0",
                "D_n=sum_doublet m d n=0",
                "D_x=sum_doublet m d x=0",
            ],
            "target_residue_mod48": int(scaled_n3 - 4 * scaled_n1) % 48,
            "required_zero_mod48": 0,
            "solution_exists": False,
        },
        "theorem_scope": (
            "all finite integer virtual sums of honest localized Weyl representations "
            "when every gauge, SU2R, flavor and other free-curvature coefficient "
            "cancels identically; standard signed half-eta copies are also excluded"
        ),
        "forced_correlated_remainder": {
            "ordinary_Weyl_module": "G=-5/8 mod Z=3/8 mod Z",
            "standard_half_eta_module": "G=-5/8 mod (1/2)Z",
            "meaning": (
                "any candidate hitting Q1=-3,Q3=3/4 must retain gauge, SU2R, "
                "flavor or other free curvature that restores the total index lattice"
            ),
        },
        "correlated_scope_witnesses_not_repairs": {
            "neutral": (
                "2 singlets q=+1 plus 5 SU2R doublets q=-1/2 hit Q1=-3,Q3=3/4 "
                "but retain +(5/2)nu c2(R) and odd Witten parity"
            ),
            "charge_five": (
                "one each 1_(+/-5) at q=-3/2, two each 1_(+/-5) at q=-1/2, "
                "and one neutral q=+2 hit Q1=-3,Q3=3/4 with seven Weyls but "
                "retain -(5/2)nu ell^2; CP3 index=-15"
            ),
        },
        "optional_flavor_quotient": {
            "evades_theorem": False,
            "reason": (
                "kappa_D extends with v=0; honest flavor-quotient representations "
                "still have integral index, while surviving flavor curvature is a spectator"
            ),
        },
        "not_excluded": [
            "a correlated completion retaining new gauge, SU2R or flavor curvature",
            "projector-distributed bulk anomalies completed across other fixed points",
            "quarter/eighth-refined higher-spin, self-dual, GS or interacting anomaly theories",
            "a changed parent action or a different globally admissible background ledger",
        ],
        "flat_or_torsion_phase_changes_free_period": False,
        "clean_parent_residue_inverse_exists": False,
    }


def _spectrum_module_ledger(
    raw: Sequence[tuple[int, int, int, Fraction]],
) -> dict[str, Any]:
    fields = []
    q1 = q3 = q2x = gravity_x = cubic_x = x_c2r = Fraction(0)
    normal_x2 = Fraction(0)
    normal_c2r = Fraction(0)
    discrete_gravity = 0
    discrete_x2 = 0
    discrete_c2r = 0
    doublet_count = 0
    component_count = 0
    for index, (multiplicity, x, dimension, qpsi) in enumerate(raw, start=1):
        qpsi = Fraction(qpsi)
        n_value = 2 * qpsi
        if n_value.denominator != 1:
            raise RuntimeError("nonintegral normal character n=2qpsi")
        n = n_value.numerator
        r_hw = 1 if dimension == 2 else 0
        scalar_q = qpsi + Fraction(1, 2)
        scalar_r = int(2 * scalar_q) % 4
        u5_pass = (2 * x) % 5 == 0
        diagonal_pass = (n + x + r_hw) % 2 == 0
        fields.append(
            {
                "id": f"field_{index}",
                "multiplicity": multiplicity,
                "U5_representation": f"1_({x:+d})",
                "X": x,
                "SU2R_dimension": dimension,
                "qpsi": fstr(qpsi),
                "n_equals_2qpsi": n,
                "qphi_if_local_N1_lift_exists": fstr(scalar_q),
                "Z4R_scalar_if_diagonal_lift": scalar_r,
                "U5tilde_center_pass": u5_pass,
                "diagonal_center_pass": diagonal_pass,
            }
        )
        q1 += multiplicity * dimension * qpsi
        q3 += multiplicity * dimension * qpsi**3
        q2x += multiplicity * dimension * qpsi**2 * x
        gravity_x += multiplicity * dimension * x
        cubic_x += multiplicity * dimension * x**3
        normal_x2 += multiplicity * dimension * qpsi * x**2
        discrete_gravity += multiplicity * dimension * n
        discrete_x2 += multiplicity * dimension * n * x**2
        component_count += multiplicity * dimension
        if dimension == 2:
            doublet_count += multiplicity
            x_c2r += multiplicity * x
            normal_c2r -= multiplicity * qpsi
            discrete_c2r += multiplicity * n
    g = normal_x2 / 50
    r_coefficient = normal_c2r
    return {
        "fields": fields,
        "complex_Weyl_component_count": component_count,
        "SU2R_doublet_count": doublet_count,
        "Witten_SU2_global_parity_even": doublet_count % 2 == 0,
        "all_full_quotient_center_checks_pass": all(
            row["U5tilde_center_pass"] and row["diagonal_center_pass"] for row in fields
        ),
        "continuous_moments": {
            "Q1_sum_mdq": fstr(q1),
            "Q3_sum_mdq3": fstr(q3),
            "U1L_squared_X_sum_mdq2x": fstr(q2x),
            "gravity_X_sum_mdx": fstr(gravity_x),
            "X_cubed_sum_mdx3": fstr(cubic_x),
            "X_c2R_sum_mxIR": fstr(x_c2r),
        },
        "target_coefficients_g_r_s": [fstr(g), fstr(r_coefficient), "0"],
        "discrete_checks": {
            "gravity_sum_mdn": discrete_gravity,
            "X_squared_sum_mdnx2": discrete_x2,
            "X_squared_mod4": discrete_x2 % 4,
            "SU2R_sum_mnIR": discrete_c2r,
            "SU2R_mod2": discrete_c2r % 2,
        },
    }


def correlated_level4_spectrum_redesign() -> dict[str, Any]:
    m00_raw = [
        (2, 5, 1, Fraction(3, 2)),
        (2, -5, 1, Fraction(3, 2)),
        (1, 0, 2, Fraction(-5, 2)),
        (2, 0, 2, Fraction(-3, 2)),
        (1, 0, 2, Fraction(5, 2)),
    ]
    m11_raw = [
        (2, 5, 1, Fraction(-3, 2)),
        (2, -5, 1, Fraction(-3, 2)),
        (2, 0, 2, Fraction(3, 2)),
    ]
    m00 = _spectrum_module_ledger(m00_raw)
    m11 = _spectrum_module_ledger(m11_raw)
    return {
        "status": (
            "PASS_EXACT_ALGEBRAIC_LEVEL4_AND_MASS_OPERATOR__"
            "VECTOR_TYPE_VEV_ACTION_OPEN"
        ),
        "scope_without_optional_flavor_quotient": True,
        "baseline_correlated_classes": {
            "z00": ["1", "1", "0"],
            "z11": ["-1", "-1", "0"],
            "meaning": "(g,r,s) in nu[g ell^2+r c2(R)+s nu^2/4]",
        },
        "added_modules": {"M00": m00, "M11": m11},
        "completed_classes": {
            "z00": ["4", "4", "0"],
            "z11": ["-4", "-4", "0"],
            "diagonal_periods": [24, -24],
            "period_formula": "(25g-r+s)/4",
            "quarter_coset_removed_algebraically": True,
        },
        "common_overlap_and_bridge": {
            "mismatch_without_flavor": "4 nu A B",
            "required_V74_bridge_level": -4,
            "level_is_quantized": True,
            "optional_flavor_mismatch": "4 nu B(A+2v)",
            "optional_flavor_bridge_built": False,
        },
        "conditional_cross_mass_operator": {
            "old_charge_five_qpsi": {"z00": "+1/2", "z11": "-1/2"},
            "new_charge_five_qpsi": {"z00": "+3/2", "z11": "-3/2"},
            "vector_type_scalars": {
                "Z00": {"Qphi": -2, "Z4R": 0},
                "Z11": {"Qphi": 2, "Z4R": 0},
            },
            "operator": (
                "W includes Z(E_old_plus E_new_minus+E_old_minus E_new_plus)"
            ),
            "z00_charge_check": {
                "normal": "-2+1+2=1",
                "Z4R": "0+2+0=2 mod4",
            },
            "z11_charge_check": {
                "normal": "+2+0-1=1",
                "Z4R": "0+0+2=2 mod4",
            },
            "Z4R_preserved_by_condensates": True,
            "mu_or_16_four_regenerated_by_selection_rule": False,
            "two_by_two_cross_blocks_full_rank_proven": False,
        },
        "beta_function_branches": {
            "both_cross_blocks_GUT_rank_two": ["0", "0", "0"],
            "new_charge_five_fields_light": ["12/5", "0", "0"],
            "old_plus_new_charge_five_fields_light": ["24/5", "0", "0"],
        },
        "unresolved_bound_parent": {
            "V71_equal_corner_normal_gravity_residue_cancelled": False,
            "reason": "M00 and M11 have Q1=Q3=0 and do not alter R=-(1/8)nu(p+nu^2)",
        },
        "microscopic_blockers": [
            "construct a vector/Sigma-type local N=1 origin for every neutral SU2R-doublet Weyl",
            "derive the Qphi=+/-2 scalar potential, radial drivers, F/D/BPS equations and positive Hessian",
            "prove both charged cross-mass matrices have rank two and mass every neutral remnant",
            "match anomalies after continuous normal-U1 breaking",
            "construct the Z4 orbifold profiles, defect caps and preserved-supercharge lifts",
            "complete proton, flavor, unification, collider, reheating, relic and BBN audits",
        ],
        "same_action_microscopic_completion": False,
        "accepted": False,
    }


def endpoint_coset_audit() -> dict[str, Any]:
    return {
        "status": "QUARTER_COSET_RECONSTRUCTED_AND_UNCHANGED",
        "targets": {"z00": "+P=+nu ell^2", "z11": "-Pprime=-nu ellprime^2"},
        "diagonal_periods": {"z00": "25/4", "z11": "-25/4"},
        "ordinary_correlated_lattice": {
            "class": "nu[g ell^2+rR c2(R)+sN nu^2/4]",
            "integrality": "g-rR+sN=0 mod4",
            "z00_target_coset": 1,
            "z11_target_coset": 3,
            "coset_difference_mod4": 2,
        },
        "ordinary_integral_additions_change_coset": False,
        "V74_bridge_periods": {"z00": 6, "z11": -6},
        "V74_bridge_changes_quarter_coset": False,
        "flat_or_torsion_phase_changes_free_curvature": False,
        "required_object": (
            "an inverse anomaly theory with the opposite free curvature and every "
            "forced correlated term, plus a same-action microscopic realization"
        ),
    }


def supersymmetry_and_mass_audit() -> dict[str, Any]:
    return {
        "status": "CORRELATED_ETA_SECTOR_NOT_A_SUPERSYMMETRIC_MASSIVE_DEFECT",
        "local_N1_implications": {
            "q_theta": "+1/2",
            "normal_charge_units": "q_N=1 corresponds to conventional continuous R=2",
            "z00_charged_qpsi_plus_half_scalar_normal_charge": "+1 (R=+2)",
            "charged_holomorphic_bilinear_normal_charge": "+2",
            "z00_Kahler_GM_bilinear": (
                "REQUIRES_A_Q_N_MINUS2_SECTION_WITH_R_MINUS4_EQUIVALENT_ZERO_MOD4"
            ),
            "z00_superpotential_mass": (
                "REQUIRES_A_Q_N_MINUS1_SECTION_WITH_R_MINUS2_EQUIVALENT_TWO_MOD4; "
                "ITS_VEV_BREAKS_Z4R"
            ),
            "z00_certified_high_scale_mass": False,
            "z11_preserved_supercharge_and_isotropy_lift": "UNBUILT__NO_MASS_CLAIM",
            "continuous_SU2R_doublets_as_local_N1_multiplets_constructed": False,
        },
        "eta_domain_wall_scope": {
            "closed_smooth_spin_H_Dai_Freed_phase_exact": True,
            "full_H_bordism_and_flat_ambiguity_classification_computed": False,
            "orbifold_relative_capped_Dai_Freed_theory_constructed": False,
            "Z4_equivariant_caps_and_isotropy_lifts_constructed": False,
            "symmetry_preserving_gap_proven": False,
            "boundary_zero_modes_or_topological_order_audited": False,
            "literal_4D_N1_realization": (
                "four chiral multiplets: two each with (x,qpsi)=(+5,+1/2) "
                "and (-5,+1/2); gauge-vectorlike but normal/R-chiral"
            ),
            "permissive_individual_5D_half_eta_realization": (
                "four hypermultiplet half-copies per sign; a regulator mass-sign "
                "difference instead shifts the level integrally"
            ),
        },
        "sixteen_fold_interaction_scope": {
            "model_specific_sixteen_Weyl_symmetric_mass_generation_proposal_exists": True,
            "applies_automatically_to_V75_gauge_and_R_quotient": False,
            "explicit_local_Hamiltonian_or_SUSY_action": "ABSENT",
            "continuous_free_anomaly_matched": False,
        },
        "V74_vector_linear_pair_supplies_eta_spectator": False,
        "accepted_same_action_completion": False,
    }


def candidate_matrix() -> list[dict[str, Any]]:
    return [
        {
            "id": "F75_VIRTUAL_LINE_ETA_REPRESENTATIVE",
            "kind": "exact correlated free-fermion eta curvature",
            "exact_advance": True,
            "selected": False,
            "accepted": False,
            "blocker": "carries S_eta and lacks the global equivariant supersymmetric defect",
        },
        {
            "id": "F75_CORRELATED_R_OR_NORMAL_FERMION_MODULE",
            "kind": "honest quotient endpoint fermions",
            "exact_advance": True,
            "selected": False,
            "accepted": False,
            "blocker": "realizes an integral completion, not the isolated inverse spectator",
        },
        {
            "id": "F75_STANDARD_NEUTRAL_FREE_ETA_SPECTATOR",
            "kind": "neutral singlet/doublet determinants and eta half-levels",
            "exact_advance": False,
            "selected": False,
            "accepted": False,
            "blocker": "excluded by the mod-eight congruence",
        },
        {
            "id": "F75_GAUGE_CHARGED_SPECTRUM_REDESIGN",
            "kind": "correlated level-four endpoint matter and conditional cross-mass operator",
            "exact_advance": True,
            "selected": True,
            "accepted": False,
            "status": (
                "PASS_EXACT_ALGEBRAIC_LEVEL4_AND_MASS_OPERATOR__"
                "VECTOR_TYPE_VEV_ACTION_OPEN"
            ),
            "blocker": (
                "the vector-type SU2R multiplets, VEV dynamics, neutral masses, "
                "bound V71 residue, caps and phenomenology are unconstructed"
            ),
        },
        {
            "id": "F75_ODD_X_NEUTRAL_MOD8_EVASION",
            "kind": "formal gauge-charged half-eta module",
            "exact_advance": True,
            "selected": False,
            "accepted": False,
            "blocker": "nonzero mixed normal-SU5 and normal-X-squared curvature",
        },
        {
            "id": "F75_CLEAN_GAUGE_CHARGED_PARENT_RESIDUE_INVERSE",
            "kind": "honest localized Weyl or standard half-eta clean residue repair",
            "exact_advance": True,
            "selected": False,
            "accepted": False,
            "blocker": "excluded by the CP3 integer/half-index period and mod-48 theorems",
        },
        {
            "id": "F75_INTERACTING_REFINED_ENDPOINT_SECTOR",
            "kind": "interacting invertible/noninvertible endpoint physics",
            "exact_advance": False,
            "selected": False,
            "accepted": False,
            "blocker": "no bordism class, action, supersymmetric lift, gap, or cap construction",
        },
    ]


def build_report() -> dict[str, Any]:
    v71_route = load_bound(V71_ROUTE_PATH, EXPECTED_CORES["v71_route"])
    v74_route = load_bound(V74_ROUTE_PATH, EXPECTED_CORES["v74_route"])
    v74_master = load_bound(V74_MASTER_PATH, EXPECTED_CORES["v74_master"])
    eta = eta_line_representative()
    modules = correlated_fermion_modules()
    no_go = standard_neutral_free_eta_no_go()
    odd_x = gauge_charged_neutral_theorem_loophole()
    clean_residue_no_go = clean_parent_residue_index_period_no_go()
    level4 = correlated_level4_spectrum_redesign()
    candidates = candidate_matrix()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "date": DATE,
        "status": STATUS,
        "lineage": {
            "V71_route_core_for_equal_corner_residue": v71_route["core_sha256"],
            "V74_route_core": v74_route["core_sha256"],
            "V74_master_core": v74_master["core_sha256"],
            "V74_selected_candidate": "F74_VECTOR_LINEAR_REFINED_BRIDGE",
            "supersession_scope": (
                "constructs and tests the correlated eta endpoint sector while "
                "preserving V74's exact bridge and every fail-closed gate"
            ),
        },
        "quarter_target_coset": endpoint_coset_audit(),
        "virtual_line_eta_representative": eta,
        "bound_parent_equal_corner_residue": bound_parent_residue_audit(v71_route),
        "exact_correlated_fermion_modules": modules,
        "standard_neutral_free_eta_no_go": no_go,
        "gauge_charged_neutral_theorem_loophole": odd_x,
        "clean_parent_residue_index_period_no_go": clean_residue_no_go,
        "correlated_level4_spectrum_redesign": level4,
        "supersymmetry_and_mass_audit": supersymmetry_and_mass_audit(),
        "F75_candidate_matrix": candidates,
        "candidate_adjudication": {
            "correlated_eta_representative": (
                "PASS_EXACT_CLOSED_SPIN_PHASE__ORBIFOLD_EXTENSION_OPEN"
            ),
            "pure_P_eta_refinement": "FAIL_FOR_CONSTRUCTED_REPRESENTATIVE",
            "standard_neutral_free_inverse_spectator": "REJECTED_MOD8",
            "odd_X_mod8_evasion": "PASS_EXACT_FORMAL__MIXED_GAUGE_ANOMALIES_SURVIVE",
            "clean_gauge_charged_parent_residue_inverse": (
                "REJECTED_CP3_INDEX_PERIOD_AND_MOD48"
            ),
            "gauge_charged_level4_redesign": (
                "SELECTED_PASS_EXACT_ALGEBRAIC__MICROSCOPIC_ACTION_OPEN"
            ),
            "interacting_refined_sector": "OPEN_UNCONSTRUCTED",
        },
        "open_obligations": [
            "compute the full raw parent fixed-point determinant including SU2R, normal, gravitational and ghost characters to identify its actual correlated eta class",
            "compute the exact Spin-SU2R-U5-flavor orbifold bordism/anomaly group, flat ambiguities and Z4-equivariant capped extension of the exact closed-spin Dai--Freed phase",
            "classify correlated odd-X quotient sectors that retain compensating gauge/R curvature; the clean parent-residue inverse is now excluded",
            "construct the selected level-four vector/Sigma multiplets, Qphi=+/-2 VEV sector, full-rank mass matrices, anomaly matching and neutral mass gap",
            "construct a curved-supergravity and Z4-equivariant defect action with caps, isotropy lifts and a symmetry-preserving mass gap",
            "prove that any interacting/topological sector matches the continuous free anomaly and does not merely cancel torsion",
            "derive the resulting spectrum, thresholds, proton operators, flavor, reheating, relics and cosmology",
            "retain every V74 KK determinant, regulator, BPS, soft-breaking and phenomenology obligation",
        ],
        "gate_ledger": {f"G{i}": "OPEN" for i in range(1, 9)},
        "terminal_decision": {
            "honest_outcome": (
                "V75 constructs an exact closed-spin correlated eta phase and exact "
                "quotient fermion modules.  Its forced spectator neither cancels "
                "V71's equal-corner residue nor lies in the standard neutral free eta "
                "image, by exact sign and mod-eight theorems.  A new correlated "
                "level-four spectrum removes the quarter coset algebraically and "
                "admits symmetry-safe cross-mass operators, but its vector-type VEV "
                "action, neutral gap, bound residue, caps and phenomenology are absent. "
                "A representation-independent CP3 index-period theorem excludes all "
                "clean localized-Weyl and standard half-eta repairs of that residue. "
                "The current action is therefore still rejected."
            ),
            "correlated_eta_representative_constructed": True,
            "closed_smooth_spin_H_Dai_Freed_phase_constructed": True,
            "Z4_equivariant_orbifold_extension_constructed": False,
            "pure_quarter_spectator_cancelled_by_eta_route": False,
            "standard_neutral_free_eta_route_closed": True,
            "odd_X_neutral_mod8_loophole_exhibited": True,
            "clean_local_Weyl_or_standard_half_eta_parent_residue_route_closed": True,
            "level4_quarter_coset_removed_algebraically": True,
            "level4_mass_operator_charge_checks_pass": True,
            "level4_microscopic_action_constructed": False,
            "bound_V71_equal_corner_residue_cancelled": False,
            "gauge_charged_routes_exhaustively_classified": False,
            "interacting_endpoint_action_constructed": False,
            "same_action_microscopic_completion_found": False,
            "selected_candidate": "F75_GAUGE_CHARGED_SPECTRUM_REDESIGN",
            "selected_candidate_accepted": False,
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
    eta = report["virtual_line_eta_representative"]
    parent = report["bound_parent_equal_corner_residue"]
    no_go = report["standard_neutral_free_eta_no_go"]
    modules = report["exact_correlated_fermion_modules"]
    clean_residue = report["clean_parent_residue_index_period_no_go"]
    level4 = report["correlated_level4_spectrum_redesign"]
    sources = "".join(
        f"- [{row['title']}]({row['url']}): {row['scope']}\n"
        for row in report["primary_sources"]
    )
    obligations = "".join(f"- {row}\n" for row in report["open_obligations"])
    return f"""# V75 quarter-spectator eta-lattice audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Exact correlated eta representative

The honest quotient lines are `L_plus=ell+nu/2` and `L_minus=ell-nu/2`.
Their virtual index-curvature combination is

`{eta['index_curvature_combination']}`

and evaluates exactly to

`{eta['curvature']}`.

On the spin CP3 diagonal witness its periods are
`P={eta['CP3_diagonal_witness']['P_period']}`,
`S_eta={eta['CP3_diagonal_witness']['S_eta_period']}`, and
`C_eta={eta['CP3_diagonal_witness']['C_eta_period']}`.  Thus an exact
closed-spin Dai--Freed phase completing the correlated quarter target exists,
but it is not a refinement of pure `P`: the gravitational spectator is
required.  The full bordism classification and the Z4-equivariant, capped
orbifold extension remain open.
At the other endpoint the inverse representative has the opposite spectator,
and their overlap remains precisely `nu A B`; V74's primitive bridge is
unchanged.

## Bound-parent comparison

V71's directly bound equal-corner residue is
`{parent['equal_corner_residue']}`.  Combining it with the antisymmetric eta
spectators leaves `{parent['combined_residuals']['z00_R_plus_S']}` at z00 and
`{parent['combined_residuals']['z11_R_minus_S']}` at z11.  On the CP3 witness
these are respectively `{parent['CP3_periods']['R_plus_S_z00']}` and
`{parent['CP3_periods']['R_minus_S_z11']}`.  The primitive `nu A B` bridge has
no normal-gravitational curvature, so it cannot change this mismatch.

## Exact quotient fermion modules

Two further honest modules realize

- `{modules['R_completion']['complete_polynomial']}` with eight Weyl components;
- `{modules['normal_line_completion']['complete_polynomial']}` with six Weyl components.

Their difference is the ordinary integral class
`{modules['integral_spectator_shift_module']['complete_polynomial']}`.
These computations demonstrate the correlation rather than remove it.

## Standard neutral free-eta no-go

For a neutral SU2R singlet, `q=m` is integral.  For a doublet,
`q=n/2` with odd `n`.  Even after allowing every signed half-multiplicity
`t=u/2`, the pure-R equations force the cubic congruence `4=0 mod 8`.
The pure-normal-quarter equations and the inverse `{eta['spectator']}` force
`0=4 mod 8`.  Hence all three isolated spectators are absent from the scoped
standard neutral free-fermion/eta image.

This theorem does not cover gauge-charged redesigns.  Indeed, an explicit
odd-X formal module reverses the neutral charge-parity premise and evades the
congruence, but leaves nonzero mixed normal-SU5 and normal-X-squared curvature.
Higher-spin eta theories, classical normal/gravitational axions, and
interacting sectors also lie outside the theorem.

## Clean parent-residue inverse no-go

The remaining V71 inverse would require `Q1=-3`, `Q3=3/4`.  On the admissible
full-quotient spin CP3 witness its period is
`{clean_residue['CP3_full_quotient_witness']['inverse_residue_period']}`.
Every honest localized complex-Weyl virtual index is integral there, and even
the deliberately permissive standard half-eta lattice lies in `(1/2)Z`.
Therefore no gauge-charged module can leave every gauge, SU2R, flavor and other
free-curvature coefficient zero while supplying this inverse.  The independent
singlet/doublet expansion gives `30=0 mod48`.

This representation-independent theorem does not exclude a correlated sector
that retains new gauge/R curvature, a projector-distributed bulk completion,
or a quarter/eighth-refined higher-spin, GS, self-dual or interacting theory.

## Correlated level-four redesign

The selected algebraic candidate adds `M00=(3,3,0)` and `M11=(-3,-3,0)`
to the correlated baselines.  Every field passes the full quotient centers;
both modules have zero `Q1`, `Q3`, `U1L^2-X`, pure-X and `X-SU2R` spectators,
and even SU2R Witten parity.  The totals are `(4,4,0)` and `(-4,-4,0)`,
with diagonal periods `+24` and `-24`.  Their mismatch is `4 nu A B`, so the
already quantized V74 bridge works at level
`{level4['common_overlap_and_bridge']['required_V74_bridge_level']}` and the
quarter coset disappears algebraically.

The candidate also has exact charge-allowed cross-mass operators using
Z4R-neutral vector-type scalars of normal charge `-2` and `+2`; those VEVs do
not re-admit `mu` or `16^4`.  But the vector/Sigma multiplet origin, VEV
dynamics, rank-two mass matrices, neutral gap, anomaly matching, orbifold caps,
and the equal-corner V71 residue remain unbuilt.  This is a selected design,
not an action.

## Fail-closed decision

{report['terminal_decision']['honest_outcome']}

Remaining obligations:

{obligations}
G1-G8 remain OPEN.

## Primary sources

{sources}"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("V75 route core hash is not canonical")
    if report["lineage"]["V74_route_core"] != EXPECTED_CORES["v74_route"]:
        raise RuntimeError("V74 route lineage mismatch")
    if report["lineage"]["V74_master_core"] != EXPECTED_CORES["v74_master"]:
        raise RuntimeError("V74 master lineage mismatch")
    if report["lineage"]["V71_route_core_for_equal_corner_residue"] != EXPECTED_CORES[
        "v71_route"
    ]:
        raise RuntimeError("V71 route lineage mismatch")
    if report["standard_neutral_free_eta_no_go"]["eta_gravity_spectator"][
        "solution_exists"
    ]:
        raise RuntimeError("the mod-eight eta obstruction was overruled")
    clean_no_go = report["clean_parent_residue_index_period_no_go"]
    if clean_no_go["clean_parent_residue_inverse_exists"]:
        raise RuntimeError("the clean parent-residue index-period no-go was overruled")
    if clean_no_go["mod48_singlet_doublet_cross_check"]["target_residue_mod48"] != 30:
        raise RuntimeError("the mod-48 parent-residue contradiction changed")
    level4 = report["correlated_level4_spectrum_redesign"]
    if level4["added_modules"]["M00"]["target_coefficients_g_r_s"] != [
        "3",
        "3",
        "0",
    ]:
        raise RuntimeError("M00 level-four redesign ledger changed")
    if level4["added_modules"]["M11"]["target_coefficients_g_r_s"] != [
        "-3",
        "-3",
        "0",
    ]:
        raise RuntimeError("M11 level-four redesign ledger changed")
    if level4["same_action_microscopic_completion"]:
        raise RuntimeError("the algebraic level-four redesign was overpromoted")
    if report["terminal_decision"]["closed_gates"]:
        raise RuntimeError("a gate was closed")
    if report["terminal_decision"]["theory_complete"]:
        raise RuntimeError("the theory was overclaimed")


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
