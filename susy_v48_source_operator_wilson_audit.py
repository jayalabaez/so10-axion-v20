#!/usr/bin/env python3
"""V48 fixed-order source-wall operator and cross-wall Wilson audit.

This audit deliberately does *not* claim an all-order sparse boundary action.
It fixes a Wilsonian scheme at the matching scale Lambda, enumerates the full
holomorphic source/portal basis through four-dimensional chiral degree four
(modulo one neutral-singlet shift), records the leading quadratic brane
response terms, and derives the exact tree-level boundary-to-boundary response
from the V47 four-spinor characteristic.

The finite collar convention agrees with the source condition g+B f=0.  For a
Hermitian Nambu matrix A, a square collar of width eps has transfer

    T_eps(m) = exp([[0, eps*m I], [A-eps*m I, 0]])
             = [[D,U],[C,D]],

and the reduced boundary kernel is B_eps=D^{-1} C.  At m=0, B_eps=A.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

import susy_v47_four_spinor_mixed_kk_audit as v47


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V48_SOURCE_OPERATOR_WILSON_AUDIT.json"
MD_PATH = ROOT / "SUSY_V48_SOURCE_OPERATOR_WILSON_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v48_source_operator_wilson_audit.py"

STATUS = (
    "V48_FIXED_ORDER_SOURCE_PORTAL_BASIS_COMPLETE__"
    "FINITE_SELF_ADJOINT_COLLAR_MAP_EXACT__"
    "FULL_FOUR_SPINOR_CROSS_WALL_WILSON_KERNEL_MATCHED__"
    "NO_FINITE_SELECTOR_REQUIRED_FOR_DECLARED_WILSONIAN_EFT__"
    "ALL_ORDER_UV_COEFFICIENT_PREDICTION_AND_PHYSICAL_GATES_OPEN"
)

FIELDS = {
    "S": {"rep": "1", "qF": 0, "kind": "source"},
    "ThetaPlus": {"rep": "1", "qF": 3, "kind": "source"},
    "ThetaMinus": {"rep": "1", "qF": -3, "kind": "source"},
    "Phi": {"rep": "210", "qF": 0, "kind": "source"},
    "Sigma": {"rep": "126", "qF": 0, "kind": "source"},
    "barSigma": {"rep": "bar126", "qF": 0, "kind": "source"},
    "A": {"long_name": "HLF", "rep": "16", "qF": 1, "kind": "bulk_trace"},
    "B": {"long_name": "HLA", "rep": "bar16", "qF": -4, "kind": "bulk_trace"},
    "C": {"long_name": "HRA", "rep": "16", "qF": -1, "kind": "bulk_trace"},
    "D": {"long_name": "HRF", "rep": "bar16", "qF": 4, "kind": "bulk_trace"},
}

UPSTREAM_INPUTS = (
    ROOT / "SUSY_V47_G1_CLOSURE_FRONTIER_AUDIT.json",
    ROOT / "SUSY_V47_FOUR_SPINOR_MIXED_KK_AUDIT.json",
    ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.json",
)

PRIMARY_SOURCES = (
    {
        "url": "https://arxiv.org/abs/hep-th/0106256",
        "use": "5D N=1 hypermultiplets in 4D superspace and local boundary superpotentials",
    },
    {
        "url": "https://arxiv.org/abs/hep-th/0109116",
        "use": "complete 16/bar16 cubic and quartic SO(10) tensor channels",
    },
    {
        "url": "https://arxiv.org/abs/1707.00580",
        "use": "complete renormalizable 10/120/126/bar126/210 SO(10) coupling inventory",
    },
    {
        "url": "https://arxiv.org/abs/hep-th/0302023",
        "use": "localized kinetic and normal-derivative operators require a regulator and renormalization scheme",
    },
    {
        "url": "https://arxiv.org/abs/1408.1852",
        "use": "thin-brane and infinite-KK limits do not commute without an explicit prescription",
    },
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = dict(value)
    payload.pop("core_sha256", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def charge(fields: Sequence[str]) -> int:
    return sum(int(FIELDS[field]["qF"]) for field in fields)


def op(name: str, fields: Sequence[str], channel: str, degree: int) -> dict[str, Any]:
    return {
        "name": name,
        "fields": list(fields),
        "degree_4D_chiral": degree,
        "qF": charge(fields),
        "SO10_channel": channel,
    }


def renormalizable_basis() -> dict[str, Any]:
    """Complete holomorphic basis through chiral degree three.

    The list includes a field-independent constant.  It is relevant in
    supergravity but not to the rigid-SUSY Hessian.  With nonzero coefficient
    of S Theta+ Theta-, one affine shift of S removes the quadratic
    Theta+Theta- coefficient; the raw and shifted counts are both recorded.
    """

    rows = [
        op("W0", (), "1", 0),
        op("f1 S", ("S",), "1", 1),
        op("f2 S^2/2", ("S", "S"), "1", 2),
        op("muTheta ThetaPlus ThetaMinus", ("ThetaPlus", "ThetaMinus"), "1", 2),
        op("m Phi^2/2", ("Phi", "Phi"), "210x210->1", 2),
        op("M Sigma barSigma", ("Sigma", "barSigma"), "126xbar126->1", 2),
        op("f3 S^3/3", ("S", "S", "S"), "1", 3),
        op("kappa S ThetaPlus ThetaMinus", ("S", "ThetaPlus", "ThetaMinus"), "1", 3),
        op("m1 S Phi^2/2", ("S", "Phi", "Phi"), "210x210->1", 3),
        op("M1 S Sigma barSigma", ("S", "Sigma", "barSigma"), "126xbar126->1", 3),
        op("lambda Phi^3/3", ("Phi", "Phi", "Phi"), "210^3->1", 3),
        op("eta Phi Sigma barSigma", ("Phi", "Sigma", "barSigma"), "210x126xbar126->1", 3),
        op("tL ThetaPlus A B", ("ThetaPlus", "A", "B"), "16xbar16->1", 3),
        op("tR ThetaMinus C D", ("ThetaMinus", "C", "D"), "16xbar16->1", 3),
        op("s16 barSigma A C", ("barSigma", "A", "C"), "16x16->126", 3),
        op("sbar16 Sigma B D", ("Sigma", "B", "D"), "bar16xbar16->bar126", 3),
    ]
    return {
        "raw_basis": rows,
        "raw_count_including_constant": len(rows),
        "raw_count_excluding_constant": len(rows) - 1,
        "all_charge_neutral": all(row["qF"] == 0 for row in rows),
        "shifted_scheme": {
            "condition": "kappa != 0",
            "field_redefinition": "S -> S-muTheta/kappa",
            "removed_basis_element": "muTheta ThetaPlus ThetaMinus",
            "independent_count_including_constant": len(rows) - 1,
            "independent_count_excluding_constant": len(rows) - 2,
            "coefficient_redefinitions": "f1,f2,f3,m,M and W0 shift; no operator is forbidden",
        },
        "completeness_reason": (
            "Spin10 tensor products are 16xbar16=1+45+210 and "
            "16x16=10+120+126. U1F neutrality leaves exactly the four displayed "
            "two-spinor portals; the neutral 210+126+bar126 source terms are the "
            "standard complete retained-irrep renormalizable superpotential, with "
            "all neutral-singlet dressings through degree three included."
        ),
    }


def leading_dimension_four_portals() -> list[dict[str, Any]]:
    """Complete two-bulk-trace holomorphic basis at chiral degree four.

    There are ten contractions.  For 16x16 (and its conjugate), insertion of
    Phi opens the three gamma-form channels 10, 120 and 126.  A and C (or B
    and D) are distinct fields, so the antisymmetric 120 contraction does not
    vanish.
    """

    rows = [
        op("S ThetaPlus (A B)_1", ("S", "ThetaPlus", "A", "B"), "1", 4),
        op("ThetaPlus Phi (A B)_210", ("ThetaPlus", "Phi", "A", "B"), "210", 4),
        op("S ThetaMinus (C D)_1", ("S", "ThetaMinus", "C", "D"), "1", 4),
        op("ThetaMinus Phi (C D)_210", ("ThetaMinus", "Phi", "C", "D"), "210", 4),
        op("S barSigma (A C)_126", ("S", "barSigma", "A", "C"), "126", 4),
        op("Phi barSigma (A C)_10", ("Phi", "barSigma", "A", "C"), "10", 4),
        op("Phi barSigma (A C)_120", ("Phi", "barSigma", "A", "C"), "120", 4),
        op("Phi barSigma (A C)_126", ("Phi", "barSigma", "A", "C"), "126", 4),
        op("S Sigma (B D)_bar126", ("S", "Sigma", "B", "D"), "bar126", 4),
        op("Phi Sigma (B D)_10", ("Phi", "Sigma", "B", "D"), "10", 4),
        op("Phi Sigma (B D)_120", ("Phi", "Sigma", "B", "D"), "120", 4),
        op("Phi Sigma (B D)_bar126", ("Phi", "Sigma", "B", "D"), "bar126", 4),
    ]
    # There are twelve rather than ten: four S dressings, two Theta-Phi
    # insertions and three Phi channels for each same-chirality pair.
    return rows


def portal_charge_exhaustion() -> dict[str, Any]:
    pair_rows = {
        "AA": charge(("A", "A")),
        "AC": charge(("A", "C")),
        "CC": charge(("C", "C")),
        "BB": charge(("B", "B")),
        "BD": charge(("B", "D")),
        "DD": charge(("D", "D")),
        "AB": charge(("A", "B")),
        "AD": charge(("A", "D")),
        "CB": charge(("C", "B")),
        "CD": charge(("C", "D")),
    }
    source_pair_charges = (-6, -3, 0, 3, 6)
    survivors = sorted(name for name, value in pair_rows.items() if -value in source_pair_charges)
    return {
        "two_bulk_trace_charge_table": pair_rows,
        "two_source_field_available_charges": list(source_pair_charges),
        "charge_survivors_before_SO10": survivors,
        "SO10_survivors": ["AB with ThetaPlus(S or Phi)", "CD with ThetaMinus(S or Phi)", "AC with barSigma(S or Phi)", "BD with Sigma(S or Phi)"],
        "excluded_by_SO10_or_center": ["AA", "CC", "BB", "DD", "AD", "CB"],
    }


def leading_response_basis() -> dict[str, Any]:
    return {
        "scheme": (
            "4D-normalized boundary traces h_i=H_i/sqrt(Lambda), supersymmetric "
            "operator basis modulo integration by parts, leading bulk equations of "
            "motion and the affine S shift"
        ),
        "localized_quadratic_terms_that_must_be_declared": {
            "canonical_kinetic": [f"int d4theta r_{name} h_{name}^dagger h_{name}" for name in "ABCD"],
            "linear_neutral_source_kinetic": [
                f"int d4theta [(zS_{name} S/Lambda)+(h.c.)] h_{name}^dagger h_{name}"
                for name in "ABCD"
            ],
            "linear_210_kinetic": [
                f"int d4theta [(zPhi_{name}/Lambda) h_{name}^dagger Phi h_{name}+(h.c.)]"
                for name in "ABCD"
            ],
            "normal_derivative_or_wrong_chirality": (
                "encoded without a thin-brane field-value convention by the analytic "
                "matrix boundary response B_eps(m)=B0+m B1+...; in the square-collar "
                "scheme B1=-eps(I+B0^2/3)"
            ),
            "gauge_kinetic": [
                "int d2theta tau10 Tr W10_alpha W10^alpha",
                "int d2theta tauF WF_alpha WF^alpha",
                "int d2theta (cS10 S/Lambda) Tr W10_alpha W10^alpha",
                "int d2theta (cSF S/Lambda) WF_alpha WF^alpha",
                "int d2theta (cPhi/Lambda) [Phi W10_alpha W10^alpha]_1",
            ],
            "FI_term": (
                "int d4theta xiF V_F is allowed on the full-Spin10 x U1F source "
                "wall; xiF(Lambda) is a renormalized boundary datum. Its effect on "
                "D-flatness and the selected vacuum belongs to G3, not this tree "
                "quadratic portal match. No non-Abelian FI term exists."
            ),
        },
        "off_diagonal_one_insertion_Kahler_terms": (
            "none: pairs in the same Spin10 chirality have U1F differences +/-2 or "
            "+/-8, and opposite-chirality pairs cannot form a singlet with one S or Phi"
        ),
        "remainder": (
            "All additional local terms are O(Lambda^-2) in this fixed response scheme "
            "or have at least two extra source insertions. This is a truncation error, "
            "not a symmetry zero. Normal-derivative terms outside the collar scheme are "
            "independent counterterms and must be rematched if the regulator is changed."
        ),
        "exhaustiveness_boundary": (
            "The holomorphic source and two-bulk-trace lists are exhaustive at the "
            "stated chiral degrees. This is not advertised as the regulator-independent "
            "complete distributional 5D dimension-five basis: operators containing odd "
            "traces and normal derivatives are convention-dependent and can be singular. "
            "Instead the finite collar is the definition of that quadratic response."
        ),
    }


def ps_wall_response_basis() -> dict[str, Any]:
    """Leading host-wall terms needed to define the cross-wall current."""

    return {
        "renormalizable_superpotential": {
            "generic": "Y_AB L_A H R_B with L=(Q1,Q2,Q3,LF), R=(Qc1,Qc2,Qc3,RA)",
            "mirror": "y_m LA H RF",
            "complementary_even_trace_terms": [
                "y_c HRAc_L H HLFc_R",
                "y_cb HRFc_L H HLAc_R",
            ],
            "complementary_trace_quantum_numbers": {
                "HLFc_R": "(4,1,2)_-1",
                "HLAc_R": "(bar4,1,2)_+4",
                "HRAc_L": "(bar4,2,1)_+1",
                "HRFc_L": "(4,2,1)_-4",
            },
            "family_resolved_count": 19,
            "count_breakdown": "9 local QHQc + 6 one-bulk currents + 2 desired/mirror two-bulk vertices + 2 complementary-Hc vertices",
        },
        "localized_Kahler": {
            "left_block": "int d4theta L^dagger Z_L L, arbitrary positive Hermitian 4x4 Z_L",
            "right_block": "int d4theta R^dagger Z_R R, arbitrary positive Hermitian 4x4 Z_R",
            "explicitly_included_mixings": ["Q_i^dagger HLF+h.c. (i=1,2,3)", "Qc_i^dagger HRA+h.c. (i=1,2,3)"],
            "isolated_blocks": [
                "z_LA LA^dagger LA",
                "z_RF RF^dagger RF",
                "z_AcR HLFc_R^dagger HLFc_R",
                "z_BcR HLAc_R^dagger HLAc_R",
                "z_CcL HRAc_L^dagger HRAc_L",
                "z_DcL HRFc_L^dagger HRFc_L",
                "z_H H^dagger H",
            ],
            "effect": "canonical normalization rotates Y_4x4 and the current vector Y_0; the K^-1 formula is basis covariant",
        },
        "boundary_gauge_terms": [
            "int d2theta tau4 Tr W4^2",
            "int d2theta tau2L Tr W2L^2",
            "int d2theta tau2R Tr W2R^2",
            "int d2theta tauF0 WF^2",
            "int d4theta xiF0 V_F",
            "int d4theta zhat Tr Zhat^2 for the gauge-covariant PS-broken Spin10 boundary superfield Zhat",
        ],
        "locality_statement": (
            "A source-wall field and a PS-wall field never occur in one local monomial. "
            "Every tree cross-wall coefficient factors through a bulk current Y_0, the "
            "regulated K_reg^-1 kernel and a source current Y_L."
        ),
    }


def renormalization_and_nda_contract() -> dict[str, Any]:
    return {
        "renormalization_scale": "mu_match=Lambda",
        "renormalized_data": [
            "four holomorphic portal tensors tL,tR,s16,sbar16 including their degree-four background corrections",
            "positive PS-wall matrices Z_L,Z_R and positive diagonal source-wall trace metrics",
            "source and PS boundary gauge kinetic coefficients with positive real parts",
            "source and PS U1F FI coefficients xiF_L,xiF_0",
            "finite-collar derivative counterterm Z_ct if a scheme other than the minimal square collar is chosen",
        ],
        "conditions": {
            "B0": "B_R(0;mu_match)=A_R",
            "B1_minimal_collar": "dB_R/dm|0=-epsilon(I+A_R^2/3)",
            "B1_general_scheme": "dB_R/dm|0=-epsilon(I+A_R^2/3)+Z_ct/Lambda",
            "metrics": "all physical boundary Kähler eigenvalues >0",
            "gauge": "Re tau_a>0",
            "FI": "xiF_0 and xiF_L are declared renormalized coefficients; solving their D equation is a G3 obligation",
        },
        "NDA_domain": {
            "geometry": "Lambda L >>1 and Lambda epsilon>=1",
            "derivative_expansion": "|p|/Lambda<1 and |p| epsilon<1 when the collar is expanded; the exact collar may be retained instead",
            "background_expansion": "max(|S|,|Phi|,|Sigma|,|barSigma|,|Theta|)/Lambda<1",
            "boundary_couplings": "dimensionless eigenvalues of A_R and 4D boundary couplings remain perturbative (no assumed cancellation between unrelated coefficients)",
            "bulk_gauge_condition": "g5^2 Lambda/(24 pi^3)<1 (declared domain; numerical verification belongs to G6)",
            "benchmark_units": "Lambda=20/L and epsilon=1/Lambda, so Lambda L=20 and p_max/Lambda=0.4 in the displayed Euclidean checks",
        },
        "scheme_warning": (
            "Changing the wall profile changes A_R,Z_ct and local contact terms, but not "
            "an observable after all coefficients are rematched. The audit proves tree "
            "matching in one scheme; it does not calculate the UV values."
        ),
        "FI_supergravity_warning": (
            "Constant FI coordinates are admissible data in the declared rigid 5D SUSY "
            "boundary EFT. A locally supersymmetric completion must replace or justify "
            "them (for example by field-dependent moment-map data); that belongs to G4."
        ),
    }


def scalar_collar_kernel(mass: complex, bare: float, epsilon: float) -> complex:
    """Eigenvalue of B_eps=D^{-1}C for the finite square collar."""

    delta = complex(mass) * epsilon
    x = delta * (bare - delta)
    root = cmath.sqrt(x)
    if abs(root) < 1.0e-8:
        # tanh(root)/root = 1-x/3+2x^2/15+...
        ratio = 1.0 - x / 3.0 + 2.0 * x * x / 15.0
    else:
        ratio = cmath.tanh(root) / root
    return (bare - delta) * ratio


def scalar_collar_series(mass: complex, bare: float, epsilon: float) -> complex:
    return (
        bare
        - mass * epsilon * (1.0 + bare * bare / 3.0)
        + mass * mass * epsilon * epsilon * (2.0 * bare / 3.0 + 2.0 * bare**3 / 15.0)
    )


def collar_kernel_matrix(mass: complex, bare: Sequence[Sequence[complex]], epsilon: float) -> np.ndarray:
    matrix = np.asarray(bare, dtype=np.complex128)
    if not np.allclose(matrix, matrix.conjugate().T, atol=1.0e-12):
        raise ValueError("the collar/Nambu bare matrix must be Hermitian")
    eigenvalues, vectors = np.linalg.eigh(matrix)
    diagonal = np.diag([scalar_collar_kernel(mass, float(value), epsilon) for value in eigenvalues])
    return vectors @ diagonal @ vectors.conjugate().T


def scalar_collar_blocks(
    mass: complex, bare: float, epsilon: float
) -> tuple[complex, complex, complex]:
    """Return D,U,C for one eigenchannel of the finite collar."""

    delta = complex(mass) * epsilon
    x = delta * (bare - delta)
    root = cmath.sqrt(x)
    if abs(root) < 1.0e-8:
        hfun = 1.0 + x / 6.0 + x * x / 120.0
        dfun = 1.0 + x / 2.0 + x * x / 24.0
    else:
        hfun = cmath.sinh(root) / root
        dfun = cmath.cosh(root)
    return dfun, delta * hfun, (bare - delta) * hfun


def collar_transfer_blocks(
    mass: complex, bare: Sequence[Sequence[complex]], epsilon: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Matrix spectral calculus for the exact D,U,C collar blocks."""

    matrix = np.asarray(bare, dtype=np.complex128)
    if not np.allclose(matrix, matrix.conjugate().T, atol=1.0e-12):
        raise ValueError("the collar/Nambu bare matrix must be Hermitian")
    eigenvalues, vectors = np.linalg.eigh(matrix)
    scalar_blocks = [
        scalar_collar_blocks(mass, float(value), epsilon) for value in eigenvalues
    ]

    def lift(index: int) -> np.ndarray:
        diagonal = np.diag([row[index] for row in scalar_blocks])
        return vectors @ diagonal @ vectors.conjugate().T

    return lift(0), lift(1), lift(2)


def symplectic_residual(bare: Sequence[Sequence[complex]]) -> float:
    """Check the zero-mass collar shear T=[[I,0],[A,I]] is J-unitary."""

    a = np.asarray(bare, dtype=np.complex128)
    n = a.shape[0]
    eye = np.eye(n, dtype=np.complex128)
    zero = np.zeros_like(eye)
    transfer = np.block([[eye, zero], [a, eye]])
    jform = np.block([[zero, -eye], [eye, zero]])
    residual = transfer.conjugate().T @ jform @ transfer - jform
    return float(np.max(np.abs(residual)))


def characteristic_numpy(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    boundary: Sequence[Sequence[complex]],
    even: Sequence[bool],
) -> np.ndarray:
    return np.asarray(
        v47.characteristic_matrix(mass, bulk_masses, length, boundary, even),
        dtype=np.complex128,
    )


def cross_wall_kernel(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    boundary: Sequence[Sequence[complex]],
    even: Sequence[bool],
) -> np.ndarray:
    """Linear response from a source-wall f-current to the PS-wall datum a.

    With g(L)+B f(L)+J_L=0, K(m)a=-J_L, hence
    a=-K^{-1}J_L.  The sign is kept in the Wilson coefficient below; this
    function returns K^{-1} itself.
    """

    return np.linalg.inv(characteristic_numpy(mass, bulk_masses, length, boundary, even))


def source_value_transfer(
    mass: complex, bulk_masses: Sequence[float], length: float, even: Sequence[bool]
) -> np.ndarray:
    s_values, f_values, _ = v47.transfer_blocks(mass, bulk_masses, length)
    size = len(bulk_masses)
    result = np.zeros((size, size), dtype=np.complex128)
    for index in range(size):
        result[index, index] = f_values[index] if even[index] else mass * s_values[index]
    return result


def inner_residual_transfer(
    mass: complex, bulk_masses: Sequence[float], length: float, even: Sequence[bool]
) -> np.ndarray:
    """Q a=g(L), complementary to R a=f(L)."""

    s_values, _, g_values = v47.transfer_blocks(mass, bulk_masses, length)
    size = len(bulk_masses)
    result = np.zeros((size, size), dtype=np.complex128)
    for index in range(size):
        result[index, index] = -mass * s_values[index] if even[index] else g_values[index]
    return result


def initial_conjugate_transfers(
    mass: complex, bulk_masses: Sequence[float], length: float, even: Sequence[bool]
) -> tuple[np.ndarray, np.ndarray]:
    """Return P,T in f(L)=R a+P b, g(L)=Q a+T b.

    At y=0 use f(0)=E a-O b and g(0)=O a+E b, where b is the
    conjugate boundary datum sourced by a PS-wall superpotential.
    """

    s_values, f_values, g_values = v47.transfer_blocks(mass, bulk_masses, length)
    size = len(bulk_masses)
    pblock = np.zeros((size, size), dtype=np.complex128)
    tblock = np.zeros((size, size), dtype=np.complex128)
    for index in range(size):
        if even[index]:
            pblock[index, index] = mass * s_values[index]
            tblock[index, index] = g_values[index]
        else:
            pblock[index, index] = -f_values[index]
            tblock[index, index] = mass * s_values[index]
    return pblock, tblock


def regulated_characteristic_numpy(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    bare: Sequence[Sequence[complex]],
    even: Sequence[bool],
    epsilon: float,
) -> np.ndarray:
    """Undivided collar characteristic K_reg=C R+D Q.

    This is entire in m.  It retains zeros of D that would be lost or turned
    into artificial poles by using B_eps=D^{-1}C alone.
    """

    dblock, _ublock, cblock = collar_transfer_blocks(mass, bare, epsilon)
    rblock = source_value_transfer(mass, bulk_masses, length, even)
    qblock = inner_residual_transfer(mass, bulk_masses, length, even)
    return cblock @ rblock + dblock @ qblock


def regulated_host_pair(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    bare: Sequence[Sequence[complex]],
    even: Sequence[bool],
    epsilon: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return K_reg,N_reg in K_reg a+N_reg b=0."""

    dblock, _ublock, cblock = collar_transfer_blocks(mass, bare, epsilon)
    rblock = source_value_transfer(mass, bulk_masses, length, even)
    qblock = inner_residual_transfer(mass, bulk_masses, length, even)
    pblock, tblock = initial_conjugate_transfers(mass, bulk_masses, length, even)
    return cblock @ rblock + dblock @ qblock, cblock @ pblock + dblock @ tblock


def host_to_host_kernel(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    bare: Sequence[Sequence[complex]],
    even: Sequence[bool],
    epsilon: float,
    host_bilinear: Sequence[Sequence[complex]] | None = None,
) -> np.ndarray:
    """Return G00=(K_reg+N_reg V0)^-1 N_reg.

    A PS current sets b=J0+V0 a.  Thus
    a=-(K_reg+N_reg V0)^-1 N_reg J0 and the tree effective term is
    -1/2 J0^T G00 J0 in the real/Nambu convention.
    """

    kblock, nblock = regulated_host_pair(
        mass, bulk_masses, length, bare, even, epsilon
    )
    if host_bilinear is None:
        vblock = np.zeros_like(kblock)
    else:
        vblock = np.asarray(host_bilinear, dtype=np.complex128)
    return np.linalg.solve(kblock + nblock @ vblock, nblock)


def symmetric_edge(size: int, first: int, second: int, value: float = 1.0) -> np.ndarray:
    result = np.zeros((size, size), dtype=np.complex128)
    result[first, second] = value
    result[second, first] = value
    return result


def block_diagonal(*blocks: np.ndarray) -> np.ndarray:
    total = sum(block.shape[0] for block in blocks)
    result = np.zeros((total, total), dtype=np.complex128)
    offset = 0
    for block in blocks:
        size = block.shape[0]
        result[offset : offset + size, offset : offset + size] = block
        offset += size
    return result


def representative_full_ps_kernel(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    theta_left: float,
    theta_right: float,
    sigma_16: float,
    sigma_bar16: float,
    epsilon: float,
    host_higgs_vertices: Sequence[float],
) -> np.ndarray:
    """Eight-coordinate left/right PS pair including all four H-bilinears.

    Coordinate order is
      (A_L,B_L,Cc_L,Dc_L | Ac_R,Bc_R,C_R,D_R).
    The right member is chosen to be the SU5-singlet channel, so the Sigma
    entries are present there.  The other seven pairs use the same formula
    with sigma_16=sigma_bar16=0 and the appropriate PS Clebsch signs.
    """

    left_boundary = np.asarray(
        v47.theta_sigma_boundary_matrix(
            theta_left, theta_right, 0.0, 0.0, su5_singlet=False
        ),
        dtype=np.complex128,
    )
    right_boundary = np.asarray(
        v47.theta_sigma_boundary_matrix(
            theta_left, theta_right, sigma_16, sigma_bar16, su5_singlet=True
        ),
        dtype=np.complex128,
    )
    k_left, n_left = regulated_host_pair(
        mass, bulk_masses, length, left_boundary, v47.E_LEFT, epsilon
    )
    k_right, n_right = regulated_host_pair(
        mass, bulk_masses, length, right_boundary, v47.E_RIGHT, epsilon
    )
    k_full = block_diagonal(k_left, k_right)
    n_full = block_diagonal(n_left, n_right)
    y44, y_mirror, y_complement_16, y_complement_bar16 = host_higgs_vertices
    v0 = np.zeros((8, 8), dtype=np.complex128)
    # A_L--C_R, B_L--D_R, Cc_L--Ac_R, Dc_L--Bc_R.
    for first, second, value in (
        (0, 6, y44),
        (1, 7, y_mirror),
        (2, 4, y_complement_16),
        (3, 5, y_complement_bar16),
    ):
        v0[first, second] = value
        v0[second, first] = value
    return np.linalg.solve(k_full + n_full @ v0, n_full)


def regulated_cross_wall_kernel(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    bare: Sequence[Sequence[complex]],
    even: Sequence[bool],
    epsilon: float,
) -> np.ndarray:
    """Exact response a=-K_reg^-1 J_outer (returning K_reg^-1)."""

    return np.linalg.inv(
        regulated_characteristic_numpy(mass, bulk_masses, length, bare, even, epsilon)
    )


def adjugate(matrix: np.ndarray) -> np.ndarray:
    n = matrix.shape[0]
    result = np.zeros_like(matrix, dtype=np.complex128)
    for row in range(n):
        for column in range(n):
            minor = np.delete(np.delete(matrix, column, axis=0), row, axis=1)
            result[row, column] = ((-1) ** (row + column)) * np.linalg.det(minor)
    return result


def spectral_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def complex_matrix_json(matrix: np.ndarray, digits: int = 12) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for row in matrix:
        encoded: list[Any] = []
        for value in row:
            item = complex(value)
            if abs(item.imag) < 10 ** (-(digits - 2)):
                encoded.append(round(item.real, digits))
            else:
                encoded.append([round(item.real, digits), round(item.imag, digits)])
        rows.append(encoded)
    return rows


def _bisect_real(function: Any, low: float, high: float) -> float:
    f_low = float(function(low))
    f_high = float(function(high))
    if f_low == 0.0:
        return low
    if f_high == 0.0:
        return high
    if f_low * f_high > 0.0:
        raise ValueError("root is not bracketed")
    for _ in range(100):
        mid = (low + high) / 2.0
        f_mid = float(function(mid))
        if abs(f_mid) < 1.0e-13 or high - low < 1.0e-12:
            return mid
        if f_low * f_mid <= 0.0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid
    return (low + high) / 2.0


def first_positive_roots(function: Any, maximum: float, steps: int, count: int) -> list[float]:
    roots: list[float] = []
    previous_x = 0.0
    previous = float(function(previous_x))
    for step in range(1, steps + 1):
        x = maximum * step / steps
        value = float(function(x))
        if previous * value < 0.0:
            root = _bisect_real(function, previous_x, x)
            if not roots or abs(root - roots[-1]) > 1.0e-7:
                roots.append(root)
                if len(roots) == count:
                    break
        previous_x = x
        previous = value
    return roots


def benchmark() -> dict[str, Any]:
    length = 1.0
    masses = (0.0, 0.0, 0.0, 0.0)
    theta_left = 0.4
    theta_right = 0.6
    sigma_16 = 0.2
    sigma_bar16 = -1.0 / 6.0
    boundary = np.asarray(
        v47.theta_sigma_boundary_matrix(
            theta_left, theta_right, sigma_16, sigma_bar16, su5_singlet=True
        ),
        dtype=np.complex128,
    )
    epsilon = 0.05

    # Exact outer-current response through the finite collar.
    b0 = collar_kernel_matrix(0.0, boundary, epsilon)
    left0 = regulated_cross_wall_kernel(
        0.0, masses, length, boundary, v47.E_LEFT, epsilon
    )
    right0 = regulated_cross_wall_kernel(
        0.0, masses, length, boundary, v47.E_RIGHT, epsilon
    )

    pole_checks: dict[str, Any] = {}
    for label, even in (("left", v47.E_LEFT), ("right_singlet", v47.E_RIGHT)):
        mass = 0.37
        k_matrix = regulated_characteristic_numpy(
            mass, masses, length, boundary, even, epsilon
        )
        determinant = np.linalg.det(k_matrix)
        adj = adjugate(k_matrix)
        residual = k_matrix @ adj - determinant * np.eye(4)
        pole_checks[label] = {
            "det_K": [round(float(determinant.real), 14), round(float(determinant.imag), 14)],
            "adjugate_identity_max_residual": float(np.max(np.abs(residual))),
            "inverse_equals_adj_over_det_max_residual": float(
                np.max(np.abs(np.linalg.inv(k_matrix) - adj / determinant))
            ),
        }

    # Euclidean locality: m=i p.  The exact norm ratio approaches exp(-Delta p L).
    euclidean_norms: dict[str, float] = {}
    for p in (1.0, 2.0, 4.0, 8.0):
        kernel = regulated_cross_wall_kernel(
            1j * p, masses, length, boundary, v47.E_RIGHT, epsilon
        )
        euclidean_norms[str(p)] = spectral_norm(kernel)
    scaled = {
        key: euclidean_norms[key] * math.exp(float(key) * (length + epsilon))
        for key in euclidean_norms
    }

    # Separation locality at p=2.
    separation_norms: dict[str, float] = {}
    for trial_length in (0.5, 1.0, 1.5, 2.0):
        kernel = regulated_cross_wall_kernel(
            2j, masses, trial_length, boundary, v47.E_RIGHT, epsilon
        )
        separation_norms[str(trial_length)] = spectral_norm(kernel)

    # Off-shell large-source decoupling.  It is deliberately stated at p>0;
    # the limit is nonuniform at a spectrally flowing pole.
    large_b_norms: dict[str, float] = {}
    for scale in (1.0, 2.0, 4.0, 8.0, 16.0):
        kernel = regulated_cross_wall_kernel(
            2j, masses, length, scale * boundary, v47.E_RIGHT, epsilon
        )
        large_b_norms[str(scale)] = spectral_norm(kernel)

    determinant_function = lambda trial: float(
        np.linalg.det(
            regulated_characteristic_numpy(
                trial, masses, length, boundary, v47.E_RIGHT, epsilon
            )
        ).real
    )
    roots = first_positive_roots(determinant_function, 12.0, 24000, 3)
    first_root = roots[0]
    k_root = regulated_characteristic_numpy(
        first_root, masses, length, boundary, v47.E_RIGHT, epsilon
    )
    hdiff = 1.0e-6
    derivative_det = (
        determinant_function(first_root + hdiff) - determinant_function(first_root - hdiff)
    ) / (2.0 * hdiff)
    residue_formula = adjugate(k_root) / derivative_det
    near_residue = hdiff * regulated_cross_wall_kernel(
        first_root + hdiff, masses, length, boundary, v47.E_RIGHT, epsilon
    )

    sample_bare = 0.7
    sample_mass = 0.11
    exact_collar = scalar_collar_kernel(sample_mass, sample_bare, epsilon)
    series_collar = scalar_collar_series(sample_mass, sample_bare, epsilon)

    host_vertices = (0.03, -0.02, 0.025, -0.015)
    full_g00 = representative_full_ps_kernel(
        0.0,
        masses,
        length,
        theta_left,
        theta_right,
        sigma_16,
        sigma_bar16,
        epsilon,
        host_vertices,
    )
    # Representative composite-current coefficients for
    # J_A=H sum_j Y_4j Qc_j and J_C=H sum_i Y_i4 Q_i.
    current = np.zeros(8, dtype=np.complex128)
    current[0] = 0.7
    current[6] = -0.4
    base_weff = -0.5 * (current.T @ full_g00 @ current)
    parameter_values = {
        "theta_left": theta_left,
        "theta_right": theta_right,
        "sigma_16": sigma_16,
        "sigma_bar16": sigma_bar16,
    }
    derivative_wilsons: dict[str, float] = {}
    derivative_norms: dict[str, float] = {}
    source_step = 1.0e-6
    for parameter_name in parameter_values:
        plus = dict(parameter_values)
        minus = dict(parameter_values)
        plus[parameter_name] += source_step
        minus[parameter_name] -= source_step
        g_plus = representative_full_ps_kernel(
            0.0, masses, length, epsilon=epsilon, host_higgs_vertices=host_vertices, **plus
        )
        g_minus = representative_full_ps_kernel(
            0.0, masses, length, epsilon=epsilon, host_higgs_vertices=host_vertices, **minus
        )
        derivative = (g_plus - g_minus) / (2.0 * source_step)
        derivative_norms[parameter_name] = spectral_norm(derivative)
        coefficient = -0.5 * (current.T @ derivative @ current)
        derivative_wilsons[parameter_name] = float(coefficient.real)

    return {
        "parameters": {
            "L": length,
            "bulk_masses": list(masses),
            "theta_left": theta_left,
            "theta_right": theta_right,
            "sigma_16": sigma_16,
            "sigma_bar16": sigma_bar16,
            "collar_epsilon": epsilon,
        },
        "boundary_matrix": [[round(float(value.real), 14) for value in row] for row in boundary],
        "boundary_determinant": float(np.linalg.det(boundary).real),
        "boundary_rank": int(np.linalg.matrix_rank(boundary)),
        "collar": {
            "B_epsilon_at_zero_equals_A_max_residual": float(np.max(np.abs(b0 - boundary))),
            "zero_mass_transfer_symplectic_residual": symplectic_residual(boundary),
            "scalar_exact": [float(exact_collar.real), float(exact_collar.imag)],
            "scalar_quadratic_series": [float(series_collar.real), float(series_collar.imag)],
            "scalar_exact_minus_series_abs": abs(exact_collar - series_collar),
        },
        "zero_energy_cross_kernel": {
            "left_spectral_norm": spectral_norm(left0),
            "right_singlet_spectral_norm": spectral_norm(right0),
            "both_finite": bool(np.isfinite(left0).all() and np.isfinite(right0).all()),
            "left_matrix_original_ABCD_order": complex_matrix_json(left0),
            "right_singlet_matrix_original_ABCD_order": complex_matrix_json(right0),
        },
        "pole_certificate": pole_checks,
        "euclidean_locality": {
            "kernel_norms": euclidean_norms,
            "exp_pL_scaled_norms": scaled,
            "successive_large_p_ratios": {
                "norm8_over_norm4": euclidean_norms["8.0"] / euclidean_norms["4.0"],
                "expected_exp_minus4": math.exp(-4.0),
            },
        },
        "regulated_spectral_kernel": {
            "first_three_positive_signed_roots": roots,
            "determinant_at_first_root_abs": abs(determinant_function(first_root)),
            "first_root_is_simple_det_derivative": derivative_det,
            "residue_formula": "Res K_reg^-1=adj(K_reg(m_n))/C_reg'(m_n)",
            "near_pole_residue_max_residual": float(
                np.max(np.abs(near_residue - residue_formula))
            ),
        },
        "separation_locality_at_p2": {
            "kernel_norms": separation_norms,
            "monotone_decrease": all(
                later < earlier
                for earlier, later in zip(
                    separation_norms.values(), list(separation_norms.values())[1:]
                )
            ),
        },
        "large_boundary_off_shell_decoupling_at_p2": {
            "kernel_norms": large_b_norms,
            "norm16_less_than_norm1": large_b_norms["16.0"] < large_b_norms["1.0"],
            "scope": "fixed Euclidean p=2 inside |p| epsilon<1; not uniform at p=0 or at the B=infinity spectral-flow endpoint",
        },
        "actual_PS_to_PS_matching": {
            "representative_coordinate_order": [
                "A_L",
                "B_L",
                "Cc_L",
                "Dc_L",
                "Ac_R",
                "Bc_R",
                "C_R",
                "D_R",
            ],
            "host_Higgs_bilinear_vertices": {
                "A_L--C_R": host_vertices[0],
                "B_L--D_R": host_vertices[1],
                "Cc_L--Ac_R": host_vertices[2],
                "Dc_L--Bc_R": host_vertices[3],
            },
            "G00_matrix": complex_matrix_json(full_g00),
            "G00_finite": bool(np.isfinite(full_g00).all()),
            "representative_J0": complex_matrix_json(current.reshape(1, -1))[0],
            "W_eff_minus_half_JGJ": float(base_weff.real),
            "source_projector_derivative_norms": derivative_norms,
            "source_projector_Wilson_coefficients": derivative_wilsons,
            "all_four_source_projectors_are_seen": all(value > 1.0e-8 for value in derivative_norms.values()),
        },
    }


def build_report() -> dict[str, Any]:
    renorm = renormalizable_basis()
    dimension_four = leading_dimension_four_portals()
    exhaustion = portal_charge_exhaustion()
    response = leading_response_basis()
    ps_response = ps_wall_response_basis()
    renormalization = renormalization_and_nda_contract()
    witness = benchmark()

    checks = {
        "renormalizable_basis_has_16_raw_rows_including_constant": renorm["raw_count_including_constant"] == 16,
        "renormalizable_rows_are_charge_neutral": renorm["all_charge_neutral"],
        "shifted_basis_has_14_nonconstant_coefficients": renorm["shifted_scheme"]["independent_count_excluding_constant"] == 14,
        "leading_dimension_four_portal_count_is_12": len(dimension_four) == 12,
        "leading_dimension_four_portals_are_charge_neutral": all(row["qF"] == 0 for row in dimension_four),
        "charge_exhaustion_has_four_pair_types": exhaustion["charge_survivors_before_SO10"] == ["AB", "AC", "BD", "CD"],
        "specified_B_is_full_rank": witness["boundary_rank"] == 4,
        "collar_matches_B_at_zero": witness["collar"]["B_epsilon_at_zero_equals_A_max_residual"] < 1.0e-12,
        "collar_is_self_adjoint": witness["collar"]["zero_mass_transfer_symplectic_residual"] < 1.0e-12,
        "collar_series_matches_exact": witness["collar"]["scalar_exact_minus_series_abs"] < 1.0e-6,
        "cross_wall_zero_energy_kernel_is_finite": witness["zero_energy_cross_kernel"]["both_finite"],
        "adjugate_pole_identity": all(
            row["adjugate_identity_max_residual"] < 1.0e-10
            and row["inverse_equals_adj_over_det_max_residual"] < 1.0e-10
            for row in witness["pole_certificate"].values()
        ),
        "euclidean_high_momentum_is_exponentially_local": witness["euclidean_locality"]["successive_large_p_ratios"]["norm8_over_norm4"] < 0.03,
        "separation_locality_is_monotone": witness["separation_locality_at_p2"]["monotone_decrease"],
        "large_boundary_exchange_decouples_off_shell": witness["large_boundary_off_shell_decoupling_at_p2"]["norm16_less_than_norm1"],
        "regulated_characteristic_has_three_replayed_roots": len(witness["regulated_spectral_kernel"]["first_three_positive_signed_roots"]) == 3,
        "regulated_first_pole_is_simple": abs(witness["regulated_spectral_kernel"]["first_root_is_simple_det_derivative"]) > 1.0e-3,
        "regulated_residue_matches": witness["regulated_spectral_kernel"]["near_pole_residue_max_residual"] < 2.0e-6,
        "actual_PS_to_PS_kernel_is_finite": witness["actual_PS_to_PS_matching"]["G00_finite"],
        "all_four_source_projectors_enter_actual_Wilson_kernel": witness["actual_PS_to_PS_matching"]["all_four_source_projectors_are_seen"],
        "PS_wall_census_includes_complementary_even_Hc_terms": ps_response["renormalizable_superpotential"]["family_resolved_count"] == 19,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("V48 source/operator/Wilson integrity failure: " + ", ".join(failed))

    report: dict[str, Any] = {
        "schema": "susy-v48-source-operator-wilson-audit-v1",
        "status": STATUS,
        "scope_contract": {
            "matching_scale": "Lambda",
            "field_scheme": "4D-normalized boundary traces, affine S shift, leading-EOM/IBP reduced",
            "holomorphic_order": "complete source action through renormalizable chiral degree three; complete two-bulk-trace portal sector through degree four",
            "quadratic_response_order": "complete declared source and PS wall quadratic data in the finite square-collar scheme; exact collar response retained instead of expanding odd-trace distributions",
            "remainder": (
                "pure-source chiral degree >=4 belongs to the G3 vacuum functional; "
                "two-bulk-trace chiral degree >=5 is the next portal order; additional "
                "regulator-independent distributional dimension-five claims are not made"
            ),
            "not_claimed": [
                "all-order sparsity",
                "UV-calculated Wilson coefficients",
                "loop matching or RG closure",
                "numerical proton/flavour/unification predictions",
            ],
        },
        "field_table": FIELDS,
        "renormalizable_source_wall_basis": renorm,
        "leading_degree_four_two_bulk_trace_basis": {
            "count": len(dimension_four),
            "operators": dimension_four,
            "coefficient_rule": "one independent coefficient per displayed SO10 contraction at Lambda",
        },
        "portal_exhaustion": exhaustion,
        "leading_quadratic_response_basis": response,
        "PS_wall_current_and_response_basis": ps_response,
        "renormalization_and_NDA_contract": renormalization,
        "selector_decision": {
            "finite_selector_required_for_fixed_order_EFT": False,
            "reason": (
                "Every gauge-allowed coefficient is admitted as independent matching data. "
                "No small forbidden coefficient is used in the exotic-lifting proof: finite "
                "nonzero Theta blocks lift the zero modes for arbitrary finite Sigma mixing."
            ),
            "all_order_sparse_selector_exists_in_declared_fields": False,
            "all_order_reason": (
                "Neutral monomials such as ThetaPlus ThetaMinus, S, Phi^2 and "
                "Sigma barSigma dress every allowed portal indefinitely. Gauge symmetry "
                "therefore generates an infinite tower; a finite symmetry does not assign "
                "their numerical Wilson coefficients."
            ),
            "naturalness_boundary": (
                "Generic O(1) coefficients are legitimate EFT data. Any phenomenological "
                "need for a parametrically small coefficient would require a symmetry, "
                "localization estimate or UV matching and is not assumed here."
            ),
        },
        "finite_collar_matching": {
            "generator": "eps G=[[0,eps m I],[A-eps m I,0]]",
            "X": "X=eps m (A-eps m I)",
            "transfer_blocks": "D=cosh(sqrt X), H=sinh(sqrt X)/sqrt X, C=(A-eps m I)H, U=eps m H",
            "renormalized_kernel": "B_eps(m)=D^-1 C",
            "zero_energy_map": "B_eps(0)=A",
            "derivative_expansion": "B_eps=A-eps m(I+A^2/3)+eps^2 m^2(2A/3+2A^3/15)+O((eps m)^3)",
            "self_adjointness": "A=A^dagger makes the complete collar transfer J-unitary; the reduced energy-dependent problem must retain det(D) wall poles",
            "thin_limit": "B_eps(m)->A uniformly on compact m sets as eps->0",
        },
        "exact_cross_wall_wilson_matching": {
            "V47_characteristic_matrix": "K(m)=(-mS+B F)E+(G+m B S)O",
            "PS_initial_data": "f(0)=E a-O b, g(0)=O a+E b",
            "bulk_transfers": "f(L)=R a+P b, g(L)=Q a+T b",
            "collar_blocks": "K_reg=C R+D Q, N_reg=C P+D T; no division by D",
            "generic_outer_current_diagnostic": "K_reg a+N_reg b=-J_L, so the formal outer-current response is -K_reg^-1 J_L",
            "actual_model_fact": "there is no independent source-wall term linear in one bulk H; Theta/Sigma/source fluctuations enter the quadratic collar matrix A",
            "actual_PS_current": [
                "J_A=H sum_(j=1)^3 Y_4j Qc_j",
                "J_C=H sum_(i=1)^3 Y_i4 Q_i",
                "all other entries vanish before bilinear host vertices",
            ],
            "PS_bilinear_vertices": [
                "Y_44 A_L H C_R",
                "y_m B_L H D_R",
                "y_c Cc_L H Ac_R",
                "y_cb Dc_L H Bc_R",
            ],
            "actual_host_kernel": "G_00[A,H]=(K_reg+N_reg V_0(H))^-1 N_reg",
            "actual_tree_effective_action": "W_eff=-1/2 J_0^T G_00[A,H] J_0 plus the nine local Q_i H Qc_j terms",
            "source_fluctuation_Wilson": "delta_X W_eff=-1/2 J_0^T (partial G_00/partial A : partial A/partial X) J_0",
            "full_component_product": "use E_L for 8 PS-left components, E_R for 7 PS-right nonsinglets, and E_R with the full Theta+Sigma B for the SU5 singlet",
            "complementary_trace_note": "the two Hc cubics couple the f/g component sectors but vanish when H=0, so the V47 zero-mode characteristic is unchanged",
            "pole_identity": "K_reg^-1=adj(K_reg)/C_reg(m), C_reg=det K_reg; every Wilson pole is a root of the undivided resolved-wall characteristic",
            "locality": "for M_i=0 and m=ip the exact collar kernel falls as exp[-p(L+epsilon)] when its leading matrix is nonsingular",
            "decoupling": "at fixed off-shell Euclidean p inside the NDA domain, increasing an invertible source matrix suppresses exchange; the limit is nonuniform at physical poles and at a distinct infinite-boundary extension",
        },
        "numerical_certificate": witness,
        "G2_assessment": {
            "fixed_order_boundary_EFT_subgate": "CLOSED_IN_THE_DECLARED_COLLAR_SCHEME",
            "full_theory_G2": "FAIL_CLOSED_PENDING_ACCEPTANCE_OF_THE_SCOPED_GATE_CONTRACT",
            "why_not_unqualified": (
                "The renormalizable source action, leading exotic-lifting portal sector, "
                "resolved response and actual tree source-dependent PS Wilson kernel are "
                "complete in one explicit Wilsonian scheme. A claim that G2 means the "
                "regulator-independent all-order boundary action is not proved and is not "
                "a finite EFT gate. The integration audit must freeze which contract G2 uses."
            ),
            "does_not_promote": ["G3", "G4", "G5", "G6", "G7", "G8"],
        },
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "primary_sources": list(PRIMARY_SOURCES),
        "source_manifest": [
            {"path": path.name, "sha256": sha256_file(path)} for path in UPSTREAM_INPUTS
        ]
        + [{"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH) if TEST_PATH.is_file() else None}],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    renorm = report["renormalizable_source_wall_basis"]
    dim4 = report["leading_degree_four_two_bulk_trace_basis"]
    renorm_rows = "\n".join(
        f"| {row['degree_4D_chiral']} | `{row['name']}` | `{row['SO10_channel']}` | {row['qF']} |"
        for row in renorm["raw_basis"]
    )
    dim4_rows = "\n".join(
        f"| `{row['name']}` | `{row['SO10_channel']}` | {row['qF']} |"
        for row in dim4["operators"]
    )
    return f"""# V48 fixed-order source operator and cross-wall Wilson audit

Status: `{report['status']}`

## Verdict

The retained V47 source wall now has a complete **scoped fixed-order
Wilsonian** definition for the renormalizable action and the first
two-bulk-trace portal order.  In the 4D-normalized boundary-trace scheme there are
{renorm['raw_count_including_constant']} raw holomorphic structures through
degree three including the constant, or
{renorm['shifted_scheme']['independent_count_excluding_constant']} nonconstant
coefficients after the allowed affine `S` shift.  The complete leading
two-bulk-trace degree-four portal sector has {dim4['count']} independent
SO(10) contractions.  Leading localized kinetic, neutral-source kinetic,
210-kinetic, two independent U(1)F FI data, gauge-kinetic and
normal-derivative responses are also declared.

This is not an all-order or regulator-independent dimension-five basis claim.
The matching action is defined at `Lambda`, modulo IBP, leading equations of
motion and the `S` shift.  Pure-source quartics belong to the G3 vacuum
functional; two-bulk-trace degree-five terms are the next portal remainder.

## Complete renormalizable source-wall basis

| Degree | Operator | SO(10) contraction | qF |
|---:|---|---|---:|
{renorm_rows}

When `kappa!=0`, `S -> S-muTheta/kappa` removes the displayed quadratic
`ThetaPlus ThetaMinus` coefficient and redefines the other neutral
coefficients.  It is a coordinate choice, not a selection rule.

## Leading two-bulk-trace portal basis

| Operator | SO(10) channel | qF |
|---|---|---:|
{dim4_rows}

The three `Phi barSigma A C` and three conjugate contractions are distinct:
`16 x 16 = 10_s + 120_a + 126_s`.  Since `A,C` and `B,D` are distinct
hypermultiplets, the 120 channels do not vanish.

## Why no new finite selector is needed

At fixed order every displayed coefficient is ordinary matching data.  The
V47 zero theorem needs only finite nonzero Theta even-even blocks and is valid
for arbitrary finite Sigma mixing, so this audit does not set an allowed
coefficient unnaturally to zero.

An all-order sparse action is impossible in the declared field content:
`ThetaPlus ThetaMinus`, `S`, `Phi^2` and `Sigma barSigma` are neutral and can
dress allowed portals indefinitely.  A finite symmetry labels operators; it
does not calculate their coefficients.  Any later need for a small coefficient
must be justified by UV matching, locality or a new symmetry.

## Resolved collar and induced terms

For a Hermitian Nambu source matrix `A`, choose a square collar of width
`epsilon` with

`epsilon G=[[0,epsilon m I],[A-epsilon m I,0]]`.

Writing its exact transfer as `[[D,U],[C,D]]`, the inner boundary condition is

`g+B_epsilon(m)f=0`, `B_epsilon=D^-1 C`.

The exact zero-energy map and derivative expansion are

`B_epsilon(0)=A`,

`B_epsilon=A-epsilon m(I+A^2/3)+epsilon^2 m^2(2A/3+2A^3/15)+...`.

Thus the regulator supplies the kinetic/wrong-chirality response that a bare
delta coefficient alone does not define.  The complete collar is
self-adjoint; poles of `D` are retained as wall states rather than divided
away.

The renormalization conditions are imposed at `mu=Lambda` on `B_R(0)`, its
first momentum derivative, both wall metrics, both FI coefficients and all
boundary gauge couplings.  The declared NDA domain is `Lambda L>>1`,
`Lambda epsilon>=1`, `p/Lambda<1`, source backgrounds below `Lambda`, positive
Kähler/gauge metrics and `g5^2 Lambda/(24 pi^3)<1`.  The benchmark uses
`Lambda L=20`, `epsilon=1/Lambda` and `p_max/Lambda=0.4`.

## Complete PS-wall current census

The earlier 17-term zero-mode census is not the complete boundary-trace
census.  The conjugate hypermultiplet traces even at the PS wall also allow

`HRAc_L H HLFc_R` and `HRFc_L H HLAc_R`.

The fixed-order PS superpotential therefore has 19 coefficients: nine local
`Q_i H Qc_j`, six one-bulk current vertices, `LF H RA`, `LA H RF`, and the two
complementary-trace cubics.  Its Kähler action contains arbitrary positive
Hermitian 4x4 matrices for `(Q_i,LF)` and `(Qc_i,RA)`, explicitly including
`Q_i^dagger LF` and `Qc_i^dagger RA`.  The four complementary even traces
`HLFc_R`, `HLAc_R`, `HRAc_L`, and `HRFc_L` each have an independent positive
boundary metric.  Constant PS gauge kinetic terms, the PS-wall U1F FI datum
and the allowed broken-generator `Tr Zhat^2` term are declared as independent
matching coefficients.

## Exact cross-wall Wilson matching

For the full four-spinor V47 matrix, introduce both allowed initial data

`f(0)=Ea-Ob`, `g(0)=Oa+Eb`,

so that `f(L)=Ra+Pb`, `g(L)=Qa+Tb`.  The undivided resolved-wall matrices are

`K_reg=CR+DQ`, `N_reg=CP+DT`.

The source wall has no independent operator linear in one bulk spinor, so a
formal source current is not the actual matching problem.  Instead the PS wall
sets

`b=J_0+V_0(H)a`,

where `J_A=H sum_j Y_4j Qc_j`, `J_C=H sum_i Y_i4 Q_i`, and `V_0`
contains all four two-bulk Higgs vertices, including the complementary traces.
The exact physical host kernel is

`G_00=(K_reg+N_reg V_0)^-1 N_reg`,

and

`W_eff=-1/2 J_0^T G_00 J_0`.

For a source fluctuation `X` entering the four Theta/Sigma projectors, the
matched coefficient is

`delta_X W_eff=-1/2 J_0^T (partial_X G_00) J_0`.

The executable eight-coordinate left/right representative includes
`(A_L,B_L,Cc_L,Dc_L | Ac_R,Bc_R,C_R,D_R)`, all four Higgs vertices and all
four source projectors.  The other seven internal pairs follow by the stated
PS Clebsch contractions; the `H=0` V47 characteristic is unchanged.

For reference, the inner thin-wall characteristic is

`K(m)=(-mS+B F)E+(G+m B S)O`,

but every resolved result uses `K_reg`, not a divided `B_epsilon`.  Because
`K_reg^-1=adj(K_reg)/det(K_reg)`, every Wilson pole is a root of the complete
resolved signed KK characteristic; the matching introduces no spurious pole.

For Euclidean `m=ip`, the executable witness verifies exponential suppression
with momentum and wall separation.  It also verifies fixed-off-shell
decoupling as an invertible boundary matrix is scaled large.  That limit is
not uniform at a physical pole or at the distinct infinite-boundary spectral
flow endpoint.

## G2 decision

The fixed-order source/portal EFT subgate is **closed in the declared collar
scheme**: field content, operator coefficients, regulator, induced response
and the actual source-dependent PS-to-PS tree kernel are explicit and
replayable.  Unqualified G2 is left fail-closed until the integration audit
freezes that scoped Wilsonian definition.  If G2 instead demands a UV
prediction of the infinite neutral-dressing tower or a regulator-independent
distributional dimension-five basis, it remains open.  No claim about G3--G8
is promoted by this calculation.

Primary formal anchors are
[Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Nath--Syed](https://arxiv.org/abs/hep-th/0109116),
[Chen--Zhang--Bai](https://arxiv.org/abs/1707.00580),
[del Aguila--Perez-Victoria--Santiago](https://arxiv.org/abs/hep-th/0302023),
and [Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V48 source/operator/Wilson JSON missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V48 source/operator/Wilson Markdown missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V48_SOURCE_OPERATOR_WILSON_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
