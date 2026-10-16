#!/usr/bin/env python3
"""G8 structural-obstruction record: the degree-2-SOS-certified witness family is flavour-dead (v20; evidence only).

Status-neutral companion of g8_sm_pati_salam_flavour_nogo_v20 (G8 v2).  User decision of 2026-09-27 (U1: accept the
rescue study's no-go and record it; the re-scope and verdict wiring come in a later PR).  No gate status changes, the
module is not wired into the gate ledger and it does not close G8.  Labels: EXACT (Gaussian-integer / Fraction / sympy
arithmetic, or an integer lattice binding with a stated margin), NUM (float, recomputed here), RESEARCH_RECORD (scratch
outputs of the 2026-09-27 rescue study, not re-derived here; sha256 recorded for audit only).  Repository conventions
throughout: vector indices 0-5 are SO(6) (SU(4)), 6-9 are SO(4); Cartan planes (0,1), ..., (8,9); the witness 210 vev
is p = e6789; sigma_std = z1^z2^z3^z4^z5; the light doublet is Re H_6..9 (G8 v2).

(A) Weyl-element lemmas [EXACT].  g_de = pi-rotation in the plane (3,5) with spinor lift S_de = Gamma_3 Gamma_5 and
    g_cust = pi-rotation in the plane (7,9) with S_cust = Gamma_7 Gamma_9 (Gaussian-integer 32 x 32 matrices of G8 v2's
    Clifford algebra).  Exact covariance S Gamma_a = R_aa Gamma_a S; both lifts are monomial on the 32 spinor states.
    S_de flips the colour weights w1, w2 (d[+--] <-> e[+++], dc[-++] <-> ec[---]) and maps the Q = -1/3 colour-(+--)
    sector onto the Q = -1 sector in both chiralities; it fixes the full 32 x 32 bilinears C Gamma_w of every
    charged-sector vev (the singlets, p, e6..e9), while sigma_std couples only nu^c nu^c (entry 32i; its 16bar.16
    bilinear is 0).  L1: for any content of 16/16bar Weyl fermions coupled only to the witness vevs, spec(M_d) =
    spec(M_e) exactly, light and heavy, colour by colour.  S_cust flips w3, w4 (u <-> d, uc <-> dc, e <-> nu, ec <->
    nuc), acts on every SU(2)_L doublet state as the partner map and fixes the bilinears of the singlets, p and e8; a
    real neutral doublet a e8 + b e9 is rotated to sqrt(a^2 + b^2) e8 by a torus element of the (8,9) plane that fixes
    p (sympy).  L2: at tan beta = 1 (real doublet) spec(M_u) = spec(M_d) exactly and CKM = 1 exactly at the level
    of the light (dimension-4) Yukawa matrices; with 16bar content the charged-current matrix of full mass eigenstates
    is (phases)(1 - K), K = U_d^dag P_{16bar SU(2)_L-singlet} U_d = O(v^2/M_V^2) (dimension-6 non-unitarity: the W_L
    current does not act on the 16bar SU(2)_L-singlet components; exactly 0 without 16bar states).
(B) Corollaries [EXACT].  The contract's 26 field-level (74 generation-expanded) renormalizable fermion-scalar couplings,
    re-derived from models/SO10Z17AxionV20.m through G8 v2's parser, use only H10, 126bar and SO(10)-singlet vevs; no
    X-neutral 16bar.16 pair exists (Z17 = X mod 17 for every field, so the X census is complete).  Hence P/Q/R promotion
    and any vectorlike 16 + 16bar pair coupled only to contract scalars (whose new couplings include 16bar_V.16.Phi210 at
    p) stay under L1 and L2.  The float spectra of the study (74 random couplings) are research-recorded.
(C) X-parity for an added 120_H (T, X = -2, Z17 phase 15) [EXACT, integer enumeration].  Among X-neutral monomials
    exactly bilinear in {H, T, H*, T*} with Sigma, S, Phi17, Phi and conjugates, the Sigma number is even through total
    degree 11 ({0, 2} at degree <= 5, {0, 2, 4} at 6-7, {0, 2, 4, 6} at 8) and the first odd-Sigma monomial has degree 12,
    so every PS-breaking H/T bilinear entry at the witness is O(r0^2) through dimension 11.  The p-only operators have
    zero (1,2,2) <-> (15,2,2) matrix elements (exact contractions), the 120 has no SM-Cartan-neutral vector (hence no SM
    or PS singlet) and the T-linear covariants of the vevs vanish exactly, so 120 squares vanishing at q0 keep q0 an
    exact SOS minimum (research construction sos120 E3).  The (v_R/M15)^2 admixture slope is research-recorded (NUM).
(D) s-structure and conjugate mixing [EXACT, sympy].  s - 1 = -e (|alpha|^2 - |beta|^2)/(alpha (d conj(beta) + e
    conj(alpha))) for a G3221 composition, so s = 1 iff e = 0 or tan beta = 1; the commutant of so(4) on the real (2,2)
    is one-dimensional (exact integer linear algebra), invariant forms on copies are A (x) I_4 and a real (2,2) vector has
    equal Y = +-1/2 projections: one tuning of a G3221-invariant mass form gives tan beta = 1, s = 1 and CKM = 1.
(E) Off-q0 selection polynomials [EXACT by lattice binding].  The H-doublet -> Sigma blocks of O15, O38, O45_B01/B02 at
    Phi = p P + a A + w W (integer-normalised forms) are evaluated with the live compiler's own adapter functions, bound
    exactly to target.parameter_rows at a generic point, lattice-bound at integer points, interpolated exactly and verified
    at integer and rational points.  Every doublet -> Sigma response vanishes at a = w = 0; each doublet source feeds a
    single Yukawa type; a down-type source needs a (15,1,1) or (15,1,3) vev (a != 0 or w != 0): it leaves the certified
    orientation.  O28 is Phi-independent and up-type only.
(F) m^2((15,2,2) of 126bar) = p^2/2 + O(r0^2) [EXACT], bound to the committed G6 tree spectrum; r_S enters only the
    O12, O04, O23 units (H and S blocks) and the O36 units are empty at H = 0, so the Phi/Sigma/Phi17 Hessian blocks are
    identical across the r_S family and the O36 lambda_H member.
(G) Headline [EXACT, composed from A-F and G8 v2]: every vacuum in the degree-2-SOS-certified witness family (the
    committed witness, the r_S family and the O36 lambda_H member, whose certificate is
    g3_sm_pati_salam_higgs_quartic_member_v20) is flavour-dead: M_e = phase x M_d^T and CKM = 1 at the level of the
    light (dimension-4) Yukawa matrices, for any H-linear portal (L1 keeps d = e at any coefficient; every
    doublet-coupled portal (O15, O28, O38, O45_B02) makes q0 a saddle, O45_B01 has no doublet coupling (flavour-inert),
    and any portal != 0 is outside the SOS27 certificate), vectorlike 16s on contract scalars, P/Q/R promotion, or a
    120 added as SOS squares with a GUT-scale (15,2,2)_120 (M15 ~ M_GUT: the d/e split enters only through a
    (15,2,2)_120 admixture of O((v_R/M15)^2) = O(r0^2); X-parity bounds the PS-breaking H/T entries at O(r0^2)).  A
    tuned-light (15,2,2)_120, which SOS squares allow, gives O(1) splitting (research selection120 C4_tuned_15) and is
    excluded only numerically (no perturbative two-loop root, research).  With 16bar content the full charged current
    is non-unitary at O(v^2/M_V^2) (dimension 6).
(H) Research record: the rescue study's off-orientation splitters (the 45 scalar portal, vectorlike matter with a
    reoriented 210, the off-witness ERT channel) ALSO split d from e but sit off the certified orientation; a second
    126bar is Landau-excluded at BM-DA1; pure 10 + 120 fits; the one-vectorlike-family c/s inequality; the portal CKM
    caveat.  Not re-derived here.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from fractions import Fraction
from functools import lru_cache, reduce
from pathlib import Path
from typing import Any

import numpy as np
import sympy

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phi2_h_126dag_210_1050_channels_v20 as hsig
import g3_candidate_physical_target_audit_v20 as target
import g3_sigma_hypercharge_audit_v20 as hypercharge
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_exact_hessian_v20 as exact_hessian
import g8_sm_pati_salam_flavour_nogo_v20 as g8
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_final_mixed_quartic_derivatives_v20 as mixed
import live_g2_exact_portal_family_derivatives_v20 as portal

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_V20.json"
OUT_MD = ROOT / "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_V20.md"
G8_JSON = ROOT / "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json"
G6_TREE_JSON = ROOT / "G6_SM_PATI_SALAM_TREE_SPECTRUM_V20.json"
FAMILY_JSON = ROOT / "G3_SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_V20.json"
QUARTIC_MEMBER_JSON = ROOT / "G3_SM_PATI_SALAM_HIGGS_QUARTIC_MEMBER_V20.json"
QUARTIC_MEMBER_MODULE = "g3_sm_pati_salam_higgs_quartic_member_v20"
QUARTIC_MEMBER_STATUS = "SM_PATI_SALAM_HIGGS_QUARTIC_MEMBER_EXACT__TREE_LEVEL__STATUS_NEUTRAL"
MODEL_FILE = ROOT / "models" / "SO10Z17AxionV20.m"

MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
MODULE_NAME = "g8_sm_pati_salam_structural_obstruction_v20"
STATUS_RECORDED = "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION__SOS_CERTIFIED_FAMILY_FLAVOUR_DEAD__RECORDED__NO_GATE_CHANGE"
STATUS_INCOMPLETE = "G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION_INCOMPLETE__NO_GATE_CHANGE"
OVERALL_STATE_RECORDED = "CERTIFIED_WITNESS_FAMILY_FLAVOUR_DEAD_EXACT__OFF_ORIENTATION_SPLITTERS_RESEARCH_RECORDED"
OVERALL_STATE_OPEN = "G8_STRUCTURAL_OBSTRUCTION_NOT_ESTABLISHED"
G8_STATUS_REQUIRED = "G8_SM_PATI_SALAM_WITNESS_FLAVOUR_NOGO__ROUTE_C_RECORDED__G8_OPEN"
G8_EXPECTED_N_CHECKS = 157
G6_TREE_STATUS = "G6_SM_PATI_SALAM_TREE_SPECTRUM_EXACT__TREE_LEVEL_ONLY__NOT_WIRED"
FAMILY_STATUS = "SM_PATI_SALAM_DECOUPLED_SINGLET_FAMILY_EXACT__STATUS_NEUTRAL"
FAMILY_EXPECTED_N_CHECKS = 77
DIGITS = 12

EXPECTED_SECTION_COUNTS = {
    "weyl_lemmas": 24,
    "corollaries": 7,
    "xparity_120": 12,
    "s_structure": 7,
    "offq0_selection": 9,
    "fifteen_two_two_mass": 8,
    "headline": 7,
    "research_record": 3,
    "scope": 1,
}
EXPECTED_N_CHECKS = sum(EXPECTED_SECTION_COUNTS.values())

NEVER_TRUE_FLAGS = (
    "G8_closed",
    "gate_status_changed",
    "wired_into_gate_ledger",
    "report_closes_G8_by_itself",
    "falsifies_so10_contract",
    "falsifies_G3_G5_certificates",
    "route_B_reduced_to_120H_among_all_extensions",
    "loop_level_flavour_analysed",
    "off_orientation_splitters_rederived_here",
)

GaussianInteger = tuple[int, int]
LemmaForm = dict[tuple[int, ...], GaussianInteger]
GMatrix = tuple[np.ndarray, np.ndarray]


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        items = sorted(value, key=str) if isinstance(value, (set, frozenset)) else value
        return [_jsonable(item) for item in items]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sympy.Basic):
        return str(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, float):
        if not math.isfinite(value):
            return value
        return float(f"{value:.{DIGITS}g}") + 0.0
    return value


def json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(_jsonable(value), sort_keys=True))


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _dig(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping) or key not in value:
            return None
        value = value[key]
    return value


# ---------------------------------------------------------------------------------------------------------------------
# (A) Weyl-element lemmas (exact Gaussian-integer Clifford algebra of G8 v2).
# ---------------------------------------------------------------------------------------------------------------------

WEYL_PLANES = {"g_de": (3, 5), "g_cust": (7, 9)}
FIXED, ODD, MOVED = "+1 (fixed)", "-1 (odd)", "moved"
PHI_P: LemmaForm = {(6, 7, 8, 9): (1, 0)}
PHI_A: LemmaForm = {(0, 1, 2, 3): (1, 0), (0, 1, 4, 5): (1, 0), (2, 3, 4, 5): (1, 0)}
PHI_W: LemmaForm = {
    (0, 1, 6, 7): (1, 0), (0, 1, 8, 9): (1, 0), (2, 3, 6, 7): (1, 0),
    (2, 3, 8, 9): (1, 0), (4, 5, 6, 7): (1, 0), (4, 5, 8, 9): (1, 0),
}
FORTY_FIVE_BL: LemmaForm = {(0, 1): (1, 0), (2, 3): (1, 0), (4, 5): (1, 0)}
FORTY_FIVE_T3R: LemmaForm = {(6, 7): (1, 0), (8, 9): (1, 0)}
FORTY_FIVE_T3L: LemmaForm = {(6, 7): (1, 0), (8, 9): (-1, 0)}
SINGLET_FORM: LemmaForm = {(): (1, 0)}


def _vev_table_forms() -> dict[str, LemmaForm]:
    """The ten vev directions of the research table (c2 vev_transformation), in repository forms."""
    return {
        "210_PS_singlet_p": dict(g8.ps_singlet_form()),
        "210_(15,1,1)_B-L": dict(PHI_A),
        "45_B-L": dict(FORTY_FIVE_BL),
        "45_T3R": dict(FORTY_FIVE_T3R),
        "45_T3L": dict(FORTY_FIVE_T3L),
        "10_doublet_e8": {(8,): (1, 0)},
        "10_doublet_e9": {(9,): (1, 0)},
        "10_doublet_e6": {(6,): (1, 0)},
        "10_doublet_e7": {(7,): (1, 0)},
        "126bar_sigma_std": dict(candidate.sigma_std_exact_form()),
    }


# The research table (C/c2_weyl_lemmas.json vev_transformation), re-derived exactly here and pinned.
EXPECTED_VEV_TABLE = {
    "g_de": {
        "210_PS_singlet_p": FIXED, "210_(15,1,1)_B-L": MOVED, "45_B-L": MOVED, "45_T3R": FIXED, "45_T3L": FIXED,
        "10_doublet_e8": FIXED, "10_doublet_e9": FIXED, "10_doublet_e6": FIXED, "10_doublet_e7": FIXED,
        "126bar_sigma_std": MOVED,
    },
    "g_cust": {
        "210_PS_singlet_p": FIXED, "210_(15,1,1)_B-L": FIXED, "45_B-L": FIXED, "45_T3R": ODD, "45_T3L": ODD,
        "10_doublet_e8": FIXED, "10_doublet_e9": ODD, "10_doublet_e6": FIXED, "10_doublet_e7": ODD,
        "126bar_sigma_std": MOVED,
    },
}


def default_charged_sector_vevs() -> dict[str, LemmaForm]:
    """Every vev that can enter a charged-fermion (Q != 0) mass block at the witness: the SO(10) singlets (S, Phi17 and
    bare masses: the k = 0 bilinear C), the 210 PS singlet p and the 10_H directions e6..e9 (complex combinations by
    linearity; the light doublet is Re H_6..9).  sigma_std is not in this set: it couples only neutral states."""
    return {
        "singlets_S_Phi17_bare": dict(SINGLET_FORM),
        "210_PS_singlet_p": dict(g8.ps_singlet_form()),
        "10_H_e6": {(6,): (1, 0)},
        "10_H_e7": {(7,): (1, 0)},
        "10_H_e8": {(8,): (1, 0)},
        "10_H_e9": {(9,): (1, 0)},
    }


L2_VEV_NAMES = ("singlets_S_Phi17_bare", "210_PS_singlet_p", "10_H_e8")


def form_matrix(form: Mapping[tuple[int, ...], GaussianInteger]) -> GMatrix:
    """The full 32 x 32 bilinear C Gamma_form (16.16, 16.16bar and 16bar.16bar blocks at once)."""
    conj = g8.charge_conjugation()
    total = g8._g_zero()
    for indices, value in form.items():
        ordered = tuple(sorted(indices))
        sign = g8._perm_sign(tuple(indices), ordered)
        term = g8._g_mul(conj, g8.gamma_product(ordered))
        total = g8._g_add(total, g8._g_scale(term, (sign * int(value[0]), sign * int(value[1]))))
    return total


def _reflection_signs(plane: tuple[int, int]) -> tuple[int, ...]:
    signs = [1] * 10
    for index in plane:
        signs[index] = -1
    return tuple(signs)


def _classify_under_reflection(form: Mapping[tuple[int, ...], GaussianInteger], signs: Sequence[int]) -> str:
    factors = {math.prod(signs[i] for i in indices) for indices, value in form.items() if tuple(value) != (0, 0)}
    if factors == {1}:
        return FIXED
    if factors == {-1}:
        return ODD
    return MOVED


def _slot(index: int) -> int:
    return index // 2


def _state_map(lift: GMatrix) -> dict[int, tuple[int, GaussianInteger]] | None:
    """{source state: (target state, phase)} if the lift is monomial with Gaussian-unit entries, else None."""
    output: dict[int, tuple[int, GaussianInteger]] = {}
    for column in range(32):
        rows = [row for row in range(32) if lift[0][row, column] or lift[1][row, column]]
        if len(rows) != 1:
            return None
        value = (int(lift[0][rows[0], column]), int(lift[1][rows[0], column]))
        if value not in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            return None
        output[column] = (rows[0], value)
    return output


def _colour(state: int) -> tuple[int, int, int]:
    weights = g8.spinor_weights(state)
    return tuple(1 if weight > 0 else -1 for weight in weights[:3])  # type: ignore[return-value]


def _state_q(state: int) -> Fraction:
    return Fraction(g8.spinor_states()["states"][state]["Q"])


def _sector(q: Fraction, colour: tuple[int, int, int] | None) -> set[int]:
    return {s for s in range(32) if _state_q(s) == q and (colour is None or _colour(s) == colour)}


TRIPLET_COLOURS = ((1, -1, -1), (-1, 1, -1), (-1, -1, 1))


def _neutral_only(matrix: GMatrix) -> bool:
    rows, columns = np.nonzero((matrix[0] != 0) | (matrix[1] != 0))
    return bool(len(rows)) and all(_state_q(int(i)) == 0 and _state_q(int(j)) == 0 for i, j in zip(rows, columns))


def torus_reduction() -> dict[str, Any]:
    """sympy: the rotation of the (8,9) plane with cos = a/r, sin = b/r (r = sqrt(a^2 + b^2)) maps the real neutral doublet
    a e8 + b e9 to r e8, is orthogonal with determinant 1 on the plane (so it fixes p = e6789 and every form without
    indices 8, 9, and the singlets), and multiplies z5 = e8 + i e9 (hence sigma_std) by a unit phase."""
    a, b = sympy.symbols("a b", positive=True)
    r = sympy.sqrt(a**2 + b**2)
    c, s = a / r, b / r
    image_e8 = (c, -s)  # R e8 = c e8 - s e9
    image_e9 = (s, c)  # R e9 = s e8 + c e9
    doublet = tuple(sympy.simplify(a * x + b * y) for x, y in zip(image_e8, image_e9))
    orthogonal = sympy.simplify(c * c + s * s - 1) == 0 and sympy.simplify(c * s - s * c) == 0
    determinant = sympy.simplify(image_e8[0] * image_e9[1] - image_e8[1] * image_e9[0])
    z5_image = tuple(sympy.simplify(x + sympy.I * y) for x, y in zip(image_e8, image_e9))
    phase = sympy.simplify(c + sympy.I * s)
    z5_phase = all(sympy.simplify(z5_image[k] - phase * (1, sympy.I)[k]) == 0 for k in range(2))
    unit_phase = sympy.simplify(sympy.expand(phase * sympy.conjugate(phase)) - 1) == 0
    return {
        "doublet_image": [str(value) for value in doublet],
        "determinant": str(determinant),
        "z5_phase": str(phase),
        "reduces_real_doublet_to_e8": sympy.simplify(doublet[0] - r) == 0 and doublet[1] == 0,
        "fixes_p": bool(orthogonal) and sympy.simplify(determinant - 1) == 0,
        "sigma_std_phase_unit": bool(z5_phase and unit_phase),
    }


def weyl_section(charged_vevs: Mapping[str, LemmaForm] | None = None) -> dict[str, Any]:
    """(A).  ``charged_vevs`` replaces the charged-sector vev set for the fail-closed mutation test only."""
    vevs = default_charged_sector_vevs() if charged_vevs is None else {k: dict(v) for k, v in charged_vevs.items()}
    gammas = g8.gamma_matrices()
    identity = g8._identity()
    info = g8.spinor_states()
    names = info["names"]
    sigma = dict(candidate.sigma_std_exact_form())
    sigma_conj = {key: (value[0], -value[1]) for key, value in sigma.items()}
    sigma_matrix = form_matrix(sigma)
    sigma_conj_matrix = form_matrix(sigma_conj)
    sixteen, sixteen_bar = info["sixteen"], info["sixteen_bar"]
    table_forms = _vev_table_forms()
    elements: dict[str, dict[str, Any]] = {}
    for label, plane in WEYL_PLANES.items():
        lift = g8.gamma_product(plane)
        signs = _reflection_signs(plane)
        covariant = all(
            g8._g_equal(g8._g_mul(lift, gammas[a]), g8._g_scale(g8._g_mul(gammas[a], lift), (signs[a], 0)))
            for a in range(10)
        )
        squares_to_minus_one = g8._g_equal(g8._g_mul(lift, lift), g8._g_scale(identity, (-1, 0)))
        mapping = _state_map(lift)
        flipped_slots = {_slot(index) for index in plane}
        flips_only = mapping is not None and all(
            [w if k not in flipped_slots else -w for k, w in enumerate(g8.spinor_weights(source))]
            == list(g8.spinor_weights(target_state))
            for source, (target_state, _phase) in mapping.items()
        )
        chirality = mapping is not None and all(
            (source in sixteen) == (target_state in sixteen) for source, (target_state, _phase) in mapping.items()
        )
        name_map = (
            {names[source]: names[target_state] for source, (target_state, _phase) in mapping.items() if source in sixteen}
            if mapping
            else {}
        )
        def invariant(
            form: Mapping[tuple[int, ...], GaussianInteger], lift: GMatrix = lift, transpose: GMatrix = g8._g_transpose(lift)
        ) -> bool:
            """S^T (C Gamma_form) S == C Gamma_form on the full 32 x 32 (all chirality blocks)."""
            matrix = form_matrix(form)
            return g8._g_equal(g8._g_mul(transpose, g8._g_mul(matrix, lift)), matrix)

        table = {name: _classify_under_reflection(form, signs) for name, form in table_forms.items()}
        elements[label] = {
            "plane": plane,
            "lift": f"Gamma_{plane[0]} Gamma_{plane[1]}",
            "covariant": bool(covariant),
            "squares_to_minus_one": bool(squares_to_minus_one),
            "monomial": mapping is not None,
            "flips_only_slots": sorted(flipped_slots),
            "flips_only_those_weights": bool(flips_only),
            "preserves_chirality": bool(chirality),
            "state_map_16": dict(sorted(name_map.items())),
            "vev_table": table,
            "invariant": invariant,
            "mapping": mapping,
        }
    de, cust = elements["g_de"], elements["g_cust"]
    de_map, cust_map = de["mapping"] or {}, cust["mapping"] or {}

    def image(mapping: Mapping[int, tuple[int, GaussianInteger]], states: set[int]) -> set[int]:
        return {mapping[s][0] for s in states if s in mapping}

    down, lepton = _sector(Fraction(-1, 3), (1, -1, -1)), _sector(Fraction(-1), None)
    down_bar, lepton_bar = _sector(Fraction(1, 3), (-1, 1, 1)), _sector(Fraction(1), None)
    de_sector_map = (
        len(down) == len(lepton) == 2
        and len(down_bar) == len(lepton_bar) == 2
        and image(de_map, down) == lepton
        and image(de_map, down_bar) == lepton_bar
        and bool(down & set(sixteen))
        and bool(down & set(sixteen_bar))
    )
    cust_sector_map = bool(cust_map) and all(
        image(cust_map, _sector(Fraction(2, 3), colour)) == _sector(Fraction(-1, 3), colour)
        and image(cust_map, _sector(Fraction(-1, 3), colour)) == _sector(Fraction(2, 3), colour)
        and image(cust_map, _sector(Fraction(-2, 3), tuple(-c for c in colour))) == _sector(Fraction(1, 3), tuple(-c for c in colour))
        and len(_sector(Fraction(2, 3), colour)) == 2
        for colour in TRIPLET_COLOURS
    )
    states = info["states"]
    partner_map = bool(cust_map) and all(
        states[cust_map[s][0]]["T3L"] == -states[s]["T3L"]
        and _colour(cust_map[s][0]) == _colour(s)
        and states[cust_map[s][0]]["B_minus_L"] == states[s]["B_minus_L"]
        for s in range(32)
        if states[s]["T3L"] != 0
    )
    expected_de_names = {"d[+--]": "e[+++]", "e[+++]": "d[+--]", "dc[-++]": "ec[---]", "ec[---]": "dc[-++]",
                         "u[+--]": "nu[+++]", "nu[+++]": "u[+--]", "uc[-++]": "nuc[---]", "nuc[---]": "uc[-++]"}
    expected_cust_bases = {"u": "d", "d": "u", "uc": "dc", "dc": "uc", "e": "nu", "nu": "e", "ec": "nuc", "nuc": "ec"}
    de_names_ok = all(de["state_map_16"].get(k) == v for k, v in expected_de_names.items())
    cust_names_ok = bool(cust["state_map_16"]) and all(
        target_name.split("[")[0] == expected_cust_bases[source.split("[")[0]] and target_name.split("[")[1] == source.split("[")[1]
        for source, target_name in cust["state_map_16"].items()
    )
    de_fixed = {name: de["invariant"](form) for name, form in vevs.items()}
    cust_fixed = {name: cust["invariant"](form) for name, form in vevs.items() if name in L2_VEV_NAMES}
    so6_generators = [(i, j) for i, j in itertools.combinations(range(6), 2)]
    so6_invariant = all(
        not g2_audit._exact_generator_action(dict(form), i, j) for form in vevs.values() if () not in form for i, j in so6_generators
    )
    controls_moved = not de["invariant"](FORTY_FIVE_BL) and not de["invariant"](PHI_A)
    cust_controls = not cust["invariant"]({(9,): (1, 0)}) and not cust["invariant"](FORTY_FIVE_T3R)
    sigma_entries = g8._entries(g8._form_bilinear(sigma))
    sigma_16_16bar = g8._g_restrict(sigma_matrix, sixteen, sixteen_bar)
    torus = torus_reduction()
    table_ok = de["vev_table"] == EXPECTED_VEV_TABLE["g_de"] and cust["vev_table"] == EXPECTED_VEV_TABLE["g_cust"]
    checks = {
        "g_de_spinor_lift_covariant_exact": de["covariant"],
        "g_de_lift_squares_to_minus_one": de["squares_to_minus_one"],
        "g_de_lift_monomial_with_unit_phases_on_32_states": de["monomial"] and de["preserves_chirality"],
        "g_de_flips_only_colour_weights_w1_w2": de["flips_only_those_weights"] and de["flips_only_slots"] == [1, 2],
        "g_de_maps_d_to_e_dc_to_ec_u_to_nu_uc_to_nuc": bool(de_names_ok),
        "g_de_maps_down_sector_onto_charged_lepton_sector_both_chiralities": bool(de_sector_map),
        "g_de_fixes_every_charged_sector_vev_bilinear_exactly": bool(de_fixed) and all(de_fixed.values()),
        "charged_sector_vevs_so6_invariant_colour_by_colour": bool(so6_invariant),
        "g_de_moves_45_BL_and_210_15_1_1_controls": bool(controls_moved),
        "g_cust_spinor_lift_covariant_exact": cust["covariant"],
        "g_cust_lift_squares_to_minus_one": cust["squares_to_minus_one"],
        "g_cust_lift_monomial_flips_only_w3_w4": cust["monomial"] and cust["preserves_chirality"]
        and cust["flips_only_those_weights"] and cust["flips_only_slots"] == [3, 4],
        "g_cust_maps_u_d_uc_dc_e_nu_ec_nuc_colour_preserved": bool(cust_names_ok),
        "g_cust_maps_up_quark_sectors_onto_down_quark_sectors": bool(cust_sector_map),
        "g_cust_is_the_su2L_partner_map_on_every_doublet_state": bool(partner_map),
        "g_cust_fixes_singlet_p_e8_bilinears_exactly": len(cust_fixed) == len(L2_VEV_NAMES) and all(cust_fixed.values()),
        "g_cust_moves_e9_and_45_T3R_controls": bool(cust_controls),
        "vev_table_matches_research_c2_exactly": bool(table_ok),
        "sigma_std_16x16_bilinear_is_nuc_nuc_32i_only": sigma_entries == [("nuc[---]", "nuc[---]", (0, 32))],
        "sigma_std_16x16bar_bilinear_zero": g8._g_is_zero(sigma_16_16bar),
        "sigma_and_conjugate_bilinears_touch_only_neutral_states": _neutral_only(sigma_matrix) and _neutral_only(sigma_conj_matrix),
        "torus_element_reduces_real_doublet_to_e8_fixing_p": bool(
            torus["reduces_real_doublet_to_e8"] and torus["fixes_p"] and torus["sigma_std_phase_unit"]
        ),
    }
    l1_keys = (
        "g_de_spinor_lift_covariant_exact", "g_de_lift_squares_to_minus_one", "g_de_lift_monomial_with_unit_phases_on_32_states",
        "g_de_flips_only_colour_weights_w1_w2", "g_de_maps_d_to_e_dc_to_ec_u_to_nu_uc_to_nuc",
        "g_de_maps_down_sector_onto_charged_lepton_sector_both_chiralities", "g_de_fixes_every_charged_sector_vev_bilinear_exactly",
        "charged_sector_vevs_so6_invariant_colour_by_colour", "sigma_std_16x16_bilinear_is_nuc_nuc_32i_only",
        "sigma_std_16x16bar_bilinear_zero", "sigma_and_conjugate_bilinears_touch_only_neutral_states",
    )
    l2_keys = (
        "g_cust_spinor_lift_covariant_exact", "g_cust_lift_squares_to_minus_one", "g_cust_lift_monomial_flips_only_w3_w4",
        "g_cust_maps_u_d_uc_dc_e_nu_ec_nuc_colour_preserved", "g_cust_maps_up_quark_sectors_onto_down_quark_sectors",
        "g_cust_is_the_su2L_partner_map_on_every_doublet_state", "g_cust_fixes_singlet_p_e8_bilinears_exactly",
        "sigma_and_conjugate_bilinears_touch_only_neutral_states", "torus_element_reduces_real_doublet_to_e8_fixing_p",
    )
    checks["L1_composed_spec_Md_equals_spec_Me"] = all(checks[key] for key in l1_keys)
    checks["L2_composed_tan_beta_one_spec_Mu_equals_spec_Md_and_dim4_CKM_one"] = all(checks[key] for key in l2_keys)
    public = {
        label: {key: value for key, value in row.items() if key not in ("invariant", "mapping")} for label, row in elements.items()
    }
    return {
        "elements": public,
        "charged_sector_vevs": sorted(vevs),
        "g_de_fixes": de_fixed,
        "g_cust_fixes": cust_fixed,
        "sectors": {
            "L1_down_colour_+--": sorted(names.get(s, f"16bar:{s}") for s in down),
            "L1_charged_lepton": sorted(names.get(s, f"16bar:{s}") for s in lepton),
        },
        "sigma_std_16x16_entries": [[a, b, list(v)] for a, b, v in sigma_entries],
        "torus_reduction": torus,
        "lemma_L1": (
            "For any content of 16/16bar Weyl fermions coupled only to the witness vevs (singlets S, Phi17 and bare masses, "
            "p, H in span(e6..e9), sigma_std): the charged blocks (Q = -1/3, -1) see no sigma_std (it couples only neutral "
            "states), every other vev bilinear is exactly S_de-invariant, and S_de maps the colour-(+--) Q = -1/3 sector "
            "onto the Q = -1 sector in both chiralities; so M_e = S_de^T M_d S_de up to unit phases and spec(M_d) = "
            "spec(M_e), light and heavy, colour by colour (the charged-sector vevs are SO(6)-invariant)"
        ),
        "lemma_L2": (
            "At tan beta = 1 (a real neutral doublet, reduced to e8 by the (8,9) torus element): S_cust fixes the "
            "bilinears of the singlets, p and e8 exactly, sigma_std stays in the neutral sector, and S_cust maps every "
            "up-quark sector onto the down-quark sector of the same colour and acts on every SU(2)_L doublet state as "
            "the W_L partner map: spec(M_u) = spec(M_d) exactly and U_u = S U_d, so CKM = 1 exactly at the level of the "
            "light (dimension-4) Yukawa matrices (and for purely chiral 16 content); with 16bar content the W_L current "
            "does not act on the 16bar SU(2)_L-singlet components, so the charged-current matrix of full mass "
            "eigenstates is (phases)(1 - K), K = U_d^dag P_{16bar SU(2)_L-singlet} U_d = O(v^2/M_V^2) (dimension-6 "
            "non-unitarity; exactly 0 without 16bar states)"
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (B) Corollaries: the contract census (G8 v2 parser), P/Q/R promotion and vectorlike pairs.
# ---------------------------------------------------------------------------------------------------------------------

CONTRACT_SCALARS = ("H10", "conj[H10]", "Delta126bar", "conj[Delta126bar]", "S", "conj[S]", "Phi17", "conj[Phi17]")
EXPECTED_FIELD_LEVEL_COUPLINGS = 26
EXPECTED_GENERATION_EXPANDED_COUPLINGS = 74
VECTORLIKE_FIELD_LINES = (
    "FermionFields[[10]] = {Vv,     1, v16,      16,   1, Exp[2*Pi*I*1/17]};",
    "FermionFields[[11]] = {Vvbar,  1, vbar16,  -16,  -1, Exp[2*Pi*I*16/17]};",
)


def _coupling_parts(label: str) -> tuple[str, str, str]:
    scalar, first, second = label.split(".")
    return scalar, first, second


def _generation_expanded(contract: Mapping[str, Any]) -> int:
    fields = contract["fields"]
    total = 0
    for row in contract["allowed_renormalizable_fermion_couplings"]:
        _scalar, first, second = _coupling_parts(row["coupling"])
        g1, g2 = int(fields[first]["generations"]), int(fields[second]["generations"])
        total += g1 * (g1 + 1) // 2 if first == second else g1 * g2
    return total


def corollary_section(model_text: str | None = None) -> dict[str, Any]:
    text = MODEL_FILE.read_text(encoding="utf-8") if model_text is None else model_text
    contract = g8.contract_section(text)
    fields = contract["fields"]
    sixteens = [n for n, row in fields.items() if row["kind"] == "fermion" and str(row["so10"]) == "16"]
    bars = [n for n, row in fields.items() if row["kind"] == "fermion" and str(row["so10"]) == "-16"]
    x_neutral_pairs = sorted(f"{a}.{b}" for a in sixteens for b in bars if int(fields[a]["X"]) + int(fields[b]["X"]) == 0)
    z17_is_x = all((int(row["Z17"]) - int(row["X"])) % 17 == 0 for row in fields.values())
    labels = [row["coupling"] for row in contract["allowed_renormalizable_fermion_couplings"]]
    scalars = sorted({_coupling_parts(label)[0] for label in labels})
    expanded = _generation_expanded(contract)
    pqr = ("P", "Q", "R", "Pbar", "Qbar", "Rbar")
    pqr_scalars = sorted({_coupling_parts(label)[0] for label in labels if set(_coupling_parts(label)[1:]) & set(pqr)})
    extended = g8.contract_section(text.rstrip() + "\n" + "\n".join(VECTORLIKE_FIELD_LINES) + "\n")
    new_labels = sorted({row["coupling"] for row in extended["allowed_renormalizable_fermion_couplings"]} - set(labels))
    new_scalars = sorted({_coupling_parts(label)[0] for label in new_labels})
    checks = {
        "contract_couplings_26_field_level_74_generation_expanded": len(labels) == EXPECTED_FIELD_LEVEL_COUPLINGS
        and contract["allowed_count"] == EXPECTED_FIELD_LEVEL_COUPLINGS and expanded == EXPECTED_GENERATION_EXPANDED_COUPLINGS,
        "no_X_neutral_16bar_16_pair_in_contract": not x_neutral_pairs and bool(sixteens) and bool(bars),
        "Z17_equals_X_mod_17_for_every_field": bool(z17_is_x),
        "contract_couplings_use_only_H10_126bar_and_singlet_vevs": set(scalars) <= set(CONTRACT_SCALARS)
        and "Phi210" not in scalars and bool(contract["checks"]["vectorlike_masses_only_SO10_singlet_vevs"])
        and bool(contract["checks"]["no_16_16bar_210_coupling"]),
        "PQR_present_and_coupled_only_through_contract_scalars": all(name in fields for name in pqr)
        and bool(pqr_scalars) and set(pqr_scalars) <= set(CONTRACT_SCALARS),
        "vectorlike_pair_adds_only_contract_scalar_p_and_bare_couplings": bool(new_labels)
        and set(new_scalars) <= set(CONTRACT_SCALARS) | {"Phi210"} and "Phi210" in new_scalars
        and extended["checks"]["no_bare_vectorlike_mass"] is False,
        "corollaries_follow_from_L1_and_L2": True,  # composed in assemble_report with the weyl section
    }
    return {
        "model_file": "models/SO10Z17AxionV20.m",
        "field_level_couplings": labels,
        "generation_expanded_count": expanded,
        "scalars_used": scalars,
        "X_neutral_16bar_16_pairs": x_neutral_pairs,
        "PQR_coupling_scalars": pqr_scalars,
        "vectorlike_pair": {
            "fields": "16_V (X = +1, Z17 phase 1) + 16bar_V (X = -1, Z17 phase 16), appended to the parsed model text only",
            "new_couplings": new_labels,
            "new_scalars": new_scalars,
            "bare_mass_allowed": extended["checks"]["no_bare_vectorlike_mass"] is False,
        },
        "statement": (
            "Every renormalizable fermion-scalar coupling of the contract (26 field-level, 74 generation-expanded) uses a "
            "10_H, a 126bar or an SO(10)-singlet vev; no 16bar.16 pair is X-neutral (Z17 = X mod 17 for every field, so the "
            "X census is complete), so no 210 or bare 16bar.16 mass exists.  Promoting P, Q, R changes no vev bilinear, and "
            "a vectorlike 16 + 16bar pair coupled to contract scalars adds only 16bar_V.16.Phi210 at p, bare masses and "
            "10_H / 126bar / singlet couplings: all their bilinears are the L1/L2-invariant ones (or neutral-only for "
            "sigma_std), so L1 and L2 hold for any such content"
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (C) X-parity for an added 120_H; the 120 has no SM-Cartan-neutral vector; T-linear covariants; p-only operators.
# ---------------------------------------------------------------------------------------------------------------------

H_X_CHARGE = -2
T_X_CHARGE = -2
T_Z17_PHASE = 15
F_X_CHARGE, F_Z17_PHASE = 1, 1
OTHER_X_CHARGES = {"Sigma": -2, "S": 4, "Phi17": 17}  # Phi (X = 0) only pads the degree
EXPECTED_SIGMA_NUMBERS = {4: (0, 2), 5: (0, 2), 6: (0, 2, 4), 7: (0, 2, 4), 8: (0, 2, 4, 6)}
EXPECTED_MIN_ODD_SIGMA_DEGREE = 12
XPARITY_MAX_DEGREE = 13


def xparity_census(t_charge: int = T_X_CHARGE, max_degree: int = XPARITY_MAX_DEGREE) -> dict[str, Any]:
    """Monomials exactly bilinear in {H, T, H*, T*} times n factors from {Sigma, Sigma*, S, S*, Phi17, Phi17*} (Phi pads),
    X-neutral.  Returns the Sigma numbers per exact number n of non-Phi factors (degree 2 + n)."""
    bilinear_charges = {"H": H_X_CHARGE, "T": t_charge, "H*": -H_X_CHARGE, "T*": -t_charge}
    bilinears = list(itertools.combinations_with_replacement(sorted(bilinear_charges), 2))
    per_n: dict[int, set[int]] = {}
    odd_examples: dict[int, list[str]] = {}
    for n in range(0, max_degree - 1):
        found: set[int] = set()
        for counts in g8._bounded_compositions(6, n):
            if sum(counts) != n:
                continue
            ns, nsb, s, sb, p, pb = counts
            x_rest = -2 * ns + 2 * nsb + 4 * s - 4 * sb + 17 * p - 17 * pb
            for pair in bilinears:
                if sum(bilinear_charges[name] for name in pair) + x_rest == 0:
                    found.add(ns + nsb)
                    if (ns + nsb) % 2 and len(odd_examples.setdefault(n + 2, [])) < 4:
                        factors = [*pair]
                        for label, count in zip(("Sigma", "Sigma*", "S", "S*", "Phi17", "Phi17*"), counts, strict=True):
                            if count:
                                factors.append(label if count == 1 else f"{label}^{count}")
                        odd_examples[n + 2].append(" ".join(factors))
        per_n[n] = found
    cumulative = {}
    for degree in range(2, max_degree + 1):
        values: set[int] = set()
        for n in range(0, degree - 1):
            values |= per_n.get(n, set())
        cumulative[degree] = sorted(values)
    odd_degrees = [n + 2 for n, values in sorted(per_n.items()) if any(v % 2 for v in values)]
    return {
        "sigma_numbers_up_to_degree": cumulative,
        "min_odd_sigma_degree": odd_degrees[0] if odd_degrees else None,
        "odd_examples_at_min_degree": odd_examples.get(odd_degrees[0], []) if odd_degrees else [],
    }


def _three_form_basis() -> list[tuple[int, int, int]]:
    return list(itertools.combinations(range(10), 3))


def _generator_on_form(form: LemmaForm, generator: Sequence[int]) -> LemmaForm:
    total: LemmaForm = {}
    for coefficient, (first, second) in zip(generator, hypercharge.GENERATORS, strict=True):
        if coefficient:
            piece = g2_audit._exact_generator_action(dict(form), first, second)
            total = hypercharge._form_add(total, g2_audit._exact_form_scale(piece, int(coefficient)))
    return total


SM_CARTAN_GENERATORS = {
    "colour_Cartan_1": hypercharge._generator_vector({(0, 1): 1, (2, 3): -1}),
    "colour_Cartan_2": hypercharge._generator_vector({(2, 3): 1, (4, 5): -1}),
    "T3L": tuple(hypercharge.T3L_INTEGER),
    "Y": tuple(hypercharge.Y_STANDARD_INTEGER),
}


def sm_cartan_kernel_on_three_forms() -> dict[str, Any]:
    """Exact rank of the stacked SM-Cartan action on Lambda^3 R^10 (the real 120): rank 120 over GF(p) (a lower bound for
    the rank over Q, hence exact) means no nonzero 3-form is annihilated by the SM Cartan subalgebra: the 120 has no SM
    singlet and no PS singlet.  Control: p, the (15,1,1) form A and the (15,1,3) form W are annihilated (SM singlets)."""
    basis = _three_form_basis()
    position = {key: k for k, key in enumerate(basis)}
    vectors = []
    for key in basis:
        image = np.zeros(len(SM_CARTAN_GENERATORS) * len(basis), dtype=np.int64)
        for g_index, generator in enumerate(SM_CARTAN_GENERATORS.values()):
            for out_key, value in _generator_on_form({key: (1, 0)}, generator).items():
                image[g_index * len(basis) + position[out_key]] += int(value[0])
        vectors.append((image, np.zeros_like(image)))
    rank = g8._gf_rank(vectors)
    controls = all(
        not _generator_on_form(form, generator) for form in (PHI_P, PHI_A, PHI_W) for generator in SM_CARTAN_GENERATORS.values()
    )
    return {"dimension": len(basis), "rank_GFp": int(rank), "kernel_zero": rank == len(basis), "controls_annihilated": bool(controls)}


# Sparse Gaussian-integer tensor contractions (full antisymmetric component tensors).


def _gmul(x: GaussianInteger, y: GaussianInteger) -> GaussianInteger:
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def _permutation_sign(permutation: Sequence[int]) -> int:
    sign = 1
    items = list(permutation)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] > items[j]:
                sign = -sign
    return sign


def full_tensor(form: Mapping[tuple[int, ...], GaussianInteger]) -> dict[tuple[int, ...], GaussianInteger]:
    output: dict[tuple[int, ...], GaussianInteger] = {}
    for indices, value in form.items():
        for permutation in itertools.permutations(range(len(indices))):
            sign = _permutation_sign(permutation)
            key = tuple(indices[i] for i in permutation)
            output[key] = (sign * int(value[0]), sign * int(value[1]))
    return output


def sparse_einsum(spec: str, *tensors: Mapping[tuple[int, ...], GaussianInteger]) -> dict[tuple[int, ...], GaussianInteger]:
    """Exact pairwise contraction (left to right) of sparse Gaussian-integer tensors; each letter appears at most once per
    operand, and a letter shared by two operands is summed unless it appears later or in the output."""
    inputs, output_letters = spec.split("->")
    letters = inputs.split(",")
    current, current_letters = dict(tensors[0]), letters[0]
    for k in range(1, len(tensors)):
        other, other_letters = tensors[k], letters[k]
        later = set("".join(letters[k + 1 :])) | set(output_letters)
        shared = [ch for ch in current_letters if ch in other_letters]
        if any(ch in later for ch in shared):
            raise ValueError("a shared letter that is kept is not supported")
        keep = [ch for ch in dict.fromkeys(current_letters + other_letters) if ch in later]
        position_current = {ch: i for i, ch in enumerate(current_letters)}
        position_other = {ch: i for i, ch in enumerate(other_letters)}
        buckets: dict[tuple[int, ...], list[tuple[tuple[int, ...], GaussianInteger]]] = defaultdict(list)
        for index, value in other.items():
            buckets[tuple(index[position_other[ch]] for ch in shared)].append((index, value))
        result: dict[tuple[int, ...], GaussianInteger] = {}
        for index, value in current.items():
            for other_index, other_value in buckets.get(tuple(index[position_current[ch]] for ch in shared), ()):
                key = tuple(index[position_current[ch]] if ch in position_current else other_index[position_other[ch]] for ch in keep)
                product = _gmul(value, other_value)
                old = result.get(key, (0, 0))
                result[key] = (old[0] + product[0], old[1] + product[1])
        current = {key: value for key, value in result.items() if value != (0, 0)}
        current_letters = "".join(keep)
    order = [current_letters.index(ch) for ch in output_letters]
    return {tuple(index[i] for i in order): value for index, value in current.items()}


def antisymmetric_part(tensor: Mapping[tuple[int, ...], GaussianInteger]) -> LemmaForm:
    output: dict[tuple[int, ...], list[int]] = defaultdict(lambda: [0, 0])
    for index, value in tensor.items():
        if len(set(index)) < len(index):
            continue
        ordered = tuple(sorted(index))
        order = [ordered.index(i) for i in index]
        sign = _permutation_sign(order)
        output[ordered][0] += sign * value[0]
        output[ordered][1] += sign * value[1]
    return {key: (v[0], v[1]) for key, v in output.items() if v != [0, 0]}


def t_linear_covariants() -> dict[str, int]:
    """The T-linear covariants of the witness vevs (sos120 E2, exact): number of nonzero 3-form components."""
    p = full_tensor(PHI_P)
    sigma = full_tensor(candidate.sigma_std_exact_form())
    sigma_bar = {key: (value[0], -value[1]) for key, value in sigma.items()}
    return {
        "(Sigma0.p)_3": len(antisymmetric_part(sparse_einsum("abcde,cdeg->abg", sigma, p))),
        "(Sigma0*.p)_3": len(antisymmetric_part(sparse_einsum("abcde,cdeg->abg", sigma_bar, p))),
        "(Sigma0 Sigma0* Sigma0*)_3": len(antisymmetric_part(sparse_einsum("axyzw,bxyuv,czwuv->abc", sigma, sigma_bar, sigma_bar))),
        "(Sigma0* Sigma0 Sigma0)_3": len(antisymmetric_part(sparse_einsum("axyzw,bxyuv,czwuv->abc", sigma_bar, sigma, sigma))),
        "(Sigma0* p p)_3": len(antisymmetric_part(sparse_einsum("abxyz,xyuv,zuvc->abc", sigma_bar, p, p))),
        "(Sigma0 p p)_3": len(antisymmetric_part(sparse_einsum("abxyz,xyuv,zuvc->abc", sigma, p, p))),
    }


def _dense_real(form: Mapping[tuple[int, ...], GaussianInteger], rank: int) -> np.ndarray:
    output = np.zeros((10,) * rank, dtype=np.int64)
    for key, value in full_tensor(form).items():
        if value[1]:
            raise ValueError("real forms only")
        output[key] = value[0]
    return output


def p_only_operator_section() -> dict[str, Any]:
    """Exact matrix elements of the p-only (PS-invariant) operators between the (1,2,2) states (10: e_a; 120: iota_{e_a}
    p) and the 60 real (15,2,2)_120 states e_i ^ e_j ^ e_b (i < j < 6 <= b), with the contraction patterns of the research
    selection120 C1 (all real bases: sesquilinear operators vanish on complex combinations too)."""
    p = _dense_real(PHI_P, 4)
    pp = np.einsum("cefg,defg->cd", p, p)
    xpp = np.einsum("abde,cfde->abcf", p, p)
    ten = {a: _dense_real({(a,): (1, 0)}, 1) for a in g8.WEAK_INDICES}
    one22 = {a: _dense_real(g8._ps_singlet_dressing({a: (1, 0)}), 3) for a in g8.WEAK_INDICES}
    fifteen = {
        (i, j, b): _dense_real({(i, j, b): (1, 0)}, 3) for i, j in itertools.combinations(range(6), 2) for b in g8.WEAK_INDICES
    }
    t15 = {a: _dense_real(g8._hypothetical_120_fifteen({a: (1, 0)}), 3) for a in g8.WEAK_INDICES}

    def h_t(h: np.ndarray, t: np.ndarray) -> dict[str, int]:
        return {
            "H^dag T Phi": int(np.einsum("a,abcd,bcd->", h, p, t)),
            "H^dag T Phi Phi": int(np.einsum("a,abcf,bcf->", h, xpp, t)),
        }

    def t_t(t1: np.ndarray, t2: np.ndarray) -> dict[str, int]:
        x2 = np.einsum("abc,abde->cde", t1, p)
        y2 = np.einsum("fgh,fgde->hde", t2, p)
        x3 = np.einsum("abc,bcde->ade", t1, p)
        y3 = np.einsum("afg,fgde->ade", t2, p)
        return {
            "T^dag T Phi": int(np.einsum("abe,abcd,cde->", t1, p, t2)),
            "T^dag T Phi Phi ch1": int(np.einsum("abc,abd,cd->", t1, t2, pp)),
            "T^dag T Phi Phi ch2": int(np.einsum("cde,cde->", x2, y2)),
            "T^dag T Phi Phi ch3": int(np.einsum("ade,ade->", x3, y3)),
        }

    mixed_values: list[int] = []
    for state in fifteen.values():
        for a in g8.WEAK_INDICES:
            mixed_values += list(h_t(ten[a], state).values())
            mixed_values += list(t_t(one22[a], state).values()) + list(t_t(state, one22[a]).values())
    control_h = max(abs(v) for a in g8.WEAK_INDICES for v in h_t(ten[a], one22[a]).values())
    control_t = max(abs(t_t(state, state)["T^dag T Phi Phi ch1"]) for state in fifteen.values())
    t15_in_span = all(set(g8._hypothetical_120_fifteen({a: (1, 0)})) <= set(fifteen) for a in g8.WEAK_INDICES)
    t15_mixed = [v for a in g8.WEAK_INDICES for b in g8.WEAK_INDICES for v in (*h_t(ten[b], t15[a]).values(), *t_t(one22[b], t15[a]).values())]
    o15_at_p_zero = all(not g2_audit._exact_wedge(g8._one_form({a: (1, 0)}), dict(PHI_P)) for a in g8.WEAK_INDICES)
    iota15_nonzero = all(bool(g8._iota15({a: (1, 0)})) for a in g8.WEAK_INDICES)
    return {
        "operators": ["H^dag T Phi", "H^dag T Phi Phi", "T^dag T Phi", "T^dag T Phi Phi (3 channels)"],
        "n_122_to_1522_matrix_elements": len(mixed_values) + len(t15_mixed),
        "max_abs_122_to_1522": max(abs(v) for v in mixed_values + t15_mixed),
        "control_max_H_to_122_120": control_h,
        "control_max_1522_diagonal_ch1": control_t,
        "t15_direction_in_1522_span": bool(t15_in_span),
        "p_only_O15_map_v_wedge_p_zero_on_doublets": bool(o15_at_p_zero),
        "iota15_126bar_fifteen_nonzero": bool(iota15_nonzero),
    }


def xparity_section(t_charge: int = T_X_CHARGE) -> dict[str, Any]:
    """(C).  ``t_charge`` replaces the 120_H X charge for the fail-closed mutation test only."""
    census = xparity_census(t_charge)
    sm = sm_cartan_kernel_on_three_forms()
    covariants = t_linear_covariants()
    operators = p_only_operator_section()
    sets = census["sigma_numbers_up_to_degree"]
    research = RESEARCH_RECORD["xparity_sets"]["value"]
    checks = {
        "F_F_120_allowed_only_for_X_minus_2_Z17_15": 2 * F_X_CHARGE + t_charge == 0 and (2 * F_Z17_PHASE + T_Z17_PHASE) % 17 == 0,
        "Z17_equals_X_mod_17_for_T": (T_Z17_PHASE - t_charge) % 17 == 0,
        "sigma_numbers_pinned_degrees_4_to_8": all(tuple(sets[d]) == EXPECTED_SIGMA_NUMBERS[d] for d in EXPECTED_SIGMA_NUMBERS),
        "sigma_number_even_through_degree_11": all(v % 2 == 0 for v in sets[11]),
        "minimal_odd_sigma_degree_is_12": census["min_odd_sigma_degree"] == EXPECTED_MIN_ODD_SIGMA_DEGREE,
        "research_xparity_sets_reproduced": all(sorted(research[str(d)]) == sets[d] for d in (4, 5, 6, 7, 8)),
        "three_forms_have_no_SM_Cartan_neutral_vector": bool(sm["kernel_zero"]),
        "sm_cartan_control_p_A_W_annihilated": bool(sm["controls_annihilated"]),
        "T_linear_covariants_of_the_vevs_vanish_exactly": all(value == 0 for value in covariants.values()),
        "p_only_operators_zero_122_to_1522_matrix_elements": operators["max_abs_122_to_1522"] == 0
        and operators["t15_direction_in_1522_span"],
        "p_only_operator_controls_nonzero": operators["control_max_H_to_122_120"] != 0 and operators["control_max_1522_diagonal_ch1"] != 0,
        "p_only_O15_map_vanishes_on_10_doublets_iota15_nonzero": operators["p_only_O15_map_v_wedge_p_zero_on_doublets"]
        and operators["iota15_126bar_fifteen_nonzero"],
    }
    return {
        "fields": {"H": H_X_CHARGE, "T (120_H)": t_charge, "T_Z17_phase": T_Z17_PHASE, **OTHER_X_CHARGES, "Phi": 0},
        "census": census,
        "sm_cartan_kernel_on_120": sm,
        "t_linear_covariants_nonzero_components": covariants,
        "p_only_operators": operators,
        "consequence": (
            "At the witness the only PS-breaking vev is Sigma = r0 sigma_std; p, S and Phi17 are PS singlets.  Every X-neutral "
            "H/T bilinear operator through total degree 11 carries an even Sigma number, and its p-only (PS-invariant) part has "
            "zero (1,2,2) <-> (15,2,2) matrix elements, so every PS-breaking H/T bilinear entry is O(r0^2) (two Sigma "
            "insertions).  The 120 has no SM-Cartan-neutral vector, so every T-linear term vanishes at q0 (checked explicitly "
            "for six covariants) and 120 squares that vanish at q0 keep q0 an exact SOS minimum (research construction "
            "sos120 E3).  Z17 = X mod 17 for every field, so Z17 removes nothing further"
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (D) s-structure, conjugate mixing and the real-type lemma (sympy, exact).
# ---------------------------------------------------------------------------------------------------------------------

# (alpha, beta, d, e) as Gaussian rationals (re, im); the claimed set: e = 0 or |alpha| = |beta|.
DEFAULT_S_POINTS: tuple[tuple[tuple[int, int], ...], ...] = (
    ((1, 0), (1, 0), (1, 0), (1, 0)),
    ((3, 4), (5, 0), (2, 1), (7, -3)),
    ((0, 2), (2, 0), (1, -1), (3, 5)),
    ((2, 0), (1, 0), (1, 0), (0, 0)),
    ((5, 1), (1, 3), (4, 0), (0, 0)),
)
CONTROL_S_POINT = ((2, 0), (1, 0), (1, 0), (1, 0))  # conjugate mixing with tan beta = 2: s = 1/2


def _gauss_sym(value: tuple[int, int]) -> sympy.Expr:
    return sympy.Integer(value[0]) + sympy.I * sympy.Integer(value[1])


def s_structure_section(points: Sequence[Sequence[tuple[int, int]]] | None = None) -> dict[str, Any]:
    """(D).  ``points`` replaces the claimed point set for the fail-closed mutation test only."""
    al, be, alb, beb, du, dd, eu, ed, c, d, e = sympy.symbols("alpha beta alphabar betabar d_u d_d e_u e_d c d e")
    s_general = ((du * al + eu * be) / (c * al)) / ((dd * beb + ed * alb) / (c * beb))
    s3221 = s_general.subs({du: d, dd: d, eu: e, ed: e})
    closed = -e * (al * alb - be * beb) / (al * (d * beb + e * alb))
    residual = sympy.simplify(sympy.together(s3221 - 1 - closed))
    numerator, _denominator = sympy.fraction(sympy.together(s3221 - 1))
    tan_beta_one = sympy.simplify(numerator.subs(beb, al * alb / be)) == 0
    no_conjugate = sympy.simplify(numerator.subs(e, 0)) == 0

    def s_value(point: Sequence[tuple[int, int]]) -> sympy.Expr:
        alpha, beta, dv, ev = (_gauss_sym(value) for value in point)
        return sympy.nsimplify(sympy.simplify(s3221.subs({al: alpha, be: beta, alb: sympy.conjugate(alpha),
                                                            beb: sympy.conjugate(beta), d: dv, e: ev, c: 1})))

    claimed = list(DEFAULT_S_POINTS if points is None else points)
    values = [s_value(point) for point in claimed]
    control = s_value(CONTROL_S_POINT)
    # Real-type lemma: the commutant of so(4) on R^4 (indices 6..9).
    generators = []
    for i, j in itertools.combinations(range(4), 2):
        matrix = sympy.zeros(4, 4)
        matrix[i, j], matrix[j, i] = 1, -1
        generators.append(matrix)
    x = sympy.Matrix(4, 4, sympy.symbols("x0:16"))
    equations = []
    for generator in generators:
        equations += list(x * generator - generator * x)
    system = sympy.Matrix([[sympy.diff(eq, symbol) for symbol in x] for eq in equations])
    commutant_dimension = 16 - system.rank()
    identity_in_commutant = all(sympy.simplify(eq.subs(dict(zip(x, sympy.eye(4))))) == 0 for eq in equations)
    # Invariant symmetric forms on two copies: B = A (x) I_4 (dimension 3 = dim Sym(2 x 2)).
    b = sympy.Matrix(8, 8, sympy.symbols("b0:64"))
    two_copy = [sympy.kronecker_product(sympy.eye(2), generator) for generator in generators]
    form_equations = [entry for generator in two_copy for entry in (b * generator - generator * b)]
    form_equations += [b[i, j] - b[j, i] for i in range(8) for j in range(i + 1, 8)]
    form_system = sympy.Matrix([[sympy.diff(eq, symbol) for symbol in b] for eq in form_equations])
    nullspace = form_system.nullspace()
    tensor_form = len(nullspace) == 3 and all(
        sympy.Matrix(8, 8, list(vector)) == sympy.kronecker_product(
            sympy.Matrix(2, 2, lambda r_, c_: sympy.Matrix(8, 8, list(vector))[4 * r_, 4 * c_]), sympy.eye(4)
        )
        for vector in nullspace
    )
    half = sympy.Rational(1, 2)
    p_plus = half * sympy.Matrix([[1, -sympy.I, 0, 0], [sympy.I, 1, 0, 0], [0, 0, 1, -sympy.I], [0, 0, sympy.I, 1]])
    p_minus = p_plus.conjugate()
    z4 = sympy.Matrix([1, sympy.I, 0, 0])
    z5 = sympy.Matrix([0, 0, 1, sympy.I])
    projector_ok = (
        sympy.simplify(p_plus * p_plus - p_plus) == sympy.zeros(4, 4)
        and sympy.simplify(p_plus.H - p_plus) == sympy.zeros(4, 4)
        and sympy.simplify(p_plus + p_minus - sympy.eye(4)) == sympy.zeros(4, 4)
        and sympy.simplify(p_plus * p_minus) == sympy.zeros(4, 4)
        and sympy.simplify(p_plus * z4 - z4) == sympy.zeros(4, 1)
        and sympy.simplify(p_plus * z5 - z5) == sympy.zeros(4, 1)
    )
    v = sympy.Matrix(sympy.symbols("v6:10", real=True))
    equal_norms = sympy.expand(((p_plus * v).H * (p_plus * v))[0] - ((p_minus * v).H * (p_minus * v))[0]) == 0
    checks = {
        "s_minus_1_closed_form_G3221_exact": residual == 0,
        "s_equals_one_iff_e_zero_or_tan_beta_one_symbolic": bool(tan_beta_one and no_conjugate),
        "s_equals_one_on_the_claimed_point_set": bool(values) and all(sympy.simplify(value - 1) == 0 for value in values),
        "conjugate_mixing_with_tan_beta_2_gives_s_one_half": sympy.simplify(control - sympy.Rational(1, 2)) == 0,
        "so4_commutant_on_real_22_is_one_dimensional": commutant_dimension == 1 and identity_in_commutant,
        "invariant_forms_on_two_copies_are_A_tensor_I4": bool(tensor_form),
        "real_22_vector_has_equal_Y_projections_tan_beta_one": bool(projector_ok and equal_norms),
    }
    return {
        "definition": "s = (v_u^126/v_u^10)/(v_d^126/v_d^10), v_u^126 = d_u alpha + e_u beta, v_d^126 = d_d conj(beta) + e_d conj(alpha)",
        "s_general": str(s_general),
        "s_minus_1_G3221": str(closed),
        "claimed_points": [[list(value) for value in point] for point in claimed],
        "s_at_claimed_points": [str(value) for value in values],
        "s_at_control_point": str(control),
        "commutant_dimension": int(commutant_dimension),
        "invariant_two_copy_form_dimension": len(nullspace),
        "lemma": (
            "For a G3221 composition (d_u = d_d, e_u = e_d) s - 1 = -e (|alpha|^2 - |beta|^2)/(alpha (d conj(beta) + e "
            "conj(alpha))): s = 1 iff e = 0 (no conjugate mixing) or tan beta = 1.  The so(4) commutant on the real (2,2) is "
            "R, so every G3221-invariant real quadratic form on m copies is A (x) I_4, its eigenvectors are a (x) v with v a "
            "real (2,2) vector, and ||P_+ v|| = ||P_- v|| (P_- = conj(P_+)): one tuning of a G3221-invariant mass form gives "
            "tan beta = 1 for the 10 and |v_u^126| = |v_d^126|, hence s = 1 and CKM = 1 (G8 v2 lemma_s1_g3221)"
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (E) Off-q0 selection polynomials (live-compiler adapter functions, exact by lattice binding).
# ---------------------------------------------------------------------------------------------------------------------

O15 = "O15_B01_Phi_Hdag_Sigma"
O28 = "O28_B01_unique_Hdag_Sigma2_Sigmadag"
O38 = "O38_B01_Phi_Hdag_Sigmadag"
O45_B01 = "O45_B01_Phi2_Hdag_Sigma_210_1050"
O45_B02 = "O45_B02_Phi2_Hdag_Sigma_210_1050"
POLY_DIRECTIONS = (O15, O38, O45_B01, O45_B02)
PHI_DEGREE = {O15: 1, O38: 1, O45_B01: 2, O45_B02: 2, O28: 0}
SHORT = {O15: "O15", O38: "O38", O45_B01: "O45_B01", O45_B02: "O45_B02", O28: "O28"}
MONOMIALS = {1: ("p", "a", "w"), 2: ("p^2", "a^2", "w^2", "p a", "p w", "a w")}
INTERPOLATION_POINTS = {1: ((1, 0, 0), (0, 1, 0), (0, 0, 1)), 2: ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1))}
INTEGER_POINTS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1), (1, 2, -1), (2, -1, 1))
RATIONAL_POINTS = (
    (Fraction(1, 2), Fraction(1, 3), Fraction(-2, 5)),
    (Fraction(2, 3), Fraction(-1, 4), Fraction(3, 2)),
    (Fraction(-3, 2), Fraction(5, 7), Fraction(1, 3)),
)
BINDING_POINT = ((3, 1, 2), Fraction(1), Fraction(1, 2))  # ((p, a, w), r0, rS): generic, rS != 1 tests O38's S^dag
LATTICE_CANDIDATES = (1, 2, 3, 4, 6, 8, 9, 12, 18, 24, 36, 48, 72)
LATTICE_MARGIN_REQUIRED = 0.49
FLOAT_BINDING_TOLERANCE = 1.0e-12
UP_TYPE = {"d-uc", "u-uc", "e-nuc", "nu-nuc"}
DOWN_TYPE = {"d-dc", "dc-u", "e-ec", "ec-nu"}
EXPECTED_SOURCE_TYPE = {
    (O15, "+"): "up", (O15, "-"): "down", (O38, "+"): "down", (O38, "-"): "up",
    (O45_B01, "+"): "up", (O45_B01, "-"): "down", (O45_B02, "+"): "up", (O45_B02, "-"): "down",
}
EXPECTED_LINEAR_FACTORS = {(O15, "+"): "a + w", (O15, "-"): "a - w", (O38, "+"): "a - w", (O38, "-"): "a + w"}
PARAMETERS = tuple(f"{part}::{direction}" for direction in POLY_DIRECTIONS for part in ("re", "im"))


def _phi_form(p: Any, a: Any, w: Any) -> dict[tuple[int, ...], complex]:
    return direct.add_forms(
        direct.scale_form({key: complex(v[0]) for key, v in PHI_P.items()}, float(p)),
        direct.scale_form({key: complex(v[0]) for key, v in PHI_A.items()}, float(a)),
        direct.scale_form({key: complex(v[0]) for key, v in PHI_W.items()}, float(w)),
    )


def _state(point: Sequence[Any], r0: Any, rs: Any) -> Any:
    return potential.FieldState(
        phi=_phi_form(*point),
        h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex),
        sigma=chart.sigma_from_coordinates(float(r0) * candidate.sigma_std_unit_coordinates()),
        s=complex(float(rs)),
        x=complex(1.0),
    ).validated()


def direct_u_blocks(point: Sequence[Any], r0: Any = 1, rs: Any = 1) -> dict[str, np.ndarray]:
    """u-coordinate H x Sigma blocks (20 x 252) of the re::/im:: parameters of O15, O38, O45_B01/B02 at Phi = p P + a A +
    w W, H = 0, Sigma = r0 sigma_std, S = rs, from the live compiler's adapter functions: O15/O38 via
    portal.base_derivative (times the S^dag dressing conj(S) for O38), O45 via the exact phi2_bilinear source with the
    210/1050 chiral projectors (the mixed-quartic adapter's H-Sigma block).  re:: = 2 Re, im:: = -2 Im of the complex
    direction block; u = 2 x chart on the H x Sigma block."""
    state = _state(point, r0, rs)
    q = chart.pack(state)
    blocks: dict[str, np.ndarray] = {}
    h15 = portal.base_derivative(q, "Phi_Hdag_Sigma")[2][chart.H_SLICE, chart.SIGMA_SLICE]
    h38 = portal.base_derivative(q, "Phi_Hdag_Sigmadag")[2][chart.H_SLICE, chart.SIGMA_SLICE] * np.conjugate(state.s)
    x = np.asarray(q, dtype=float)[chart.PHI_SLICE]
    phi_form = {indices: complex(x[index]) for index, indices in enumerate(hsig.C4) if abs(x[index]) > 1.0e-15}
    base = hsig.phi2_bilinear(phi_form, phi_form, +1)
    hbar = np.conjugate(mixed.h_real_map())
    sigma_real = mixed.sigma_full_real_map()
    complex_blocks = {
        O15: h15,
        O38: h38,
        O45_B01: hbar.T @ hsig.project_210(base, +1) @ sigma_real,
        O45_B02: hbar.T @ hsig.project_1050(base, +1) @ sigma_real,
    }
    for direction, block in complex_blocks.items():
        blocks[f"re::{direction}"] = 2.0 * (2.0 * block.real)
        blocks[f"im::{direction}"] = 2.0 * (-2.0 * block.imag)
    return blocks


@lru_cache(maxsize=1)
def compiler_binding() -> dict[str, Any]:
    """One live compiler pass (target.parameter_rows) at the generic BINDING_POINT: the direct blocks must equal the
    compiler's u-Hessian H x Sigma blocks for all eight parameters; O28's doublet columns are lattice-bound (1/6 Z)."""
    point, r0, rs = BINDING_POINT
    rows = target.parameter_rows(_state(point, r0, rs), include=lambda d: d.direction_id in set(g8.EXPECTED_H_LINEAR_DIRECTIONS))
    direct_blocks = direct_u_blocks(point, r0, rs)
    deviation = {}
    for parameter, block in direct_blocks.items():
        hessian = np.asarray(rows[parameter].hessian, dtype=float)
        u = exact_hessian.chart_to_u_hessian(0.5 * (hessian + hessian.T))
        deviation[parameter] = float(np.max(np.abs(u[chart.H_SLICE, chart.SIGMA_SLICE] - block)))
    o28 = {}
    for part in ("re", "im"):
        hessian = np.asarray(rows[f"{part}::{O28}"].hessian, dtype=float)
        u = exact_hessian.chart_to_u_hessian(0.5 * (hessian + hessian.T))
        block = 6.0 * u[chart.H_SLICE, chart.SIGMA_SLICE]
        integer = np.rint(block).astype(np.int64)
        o28[part] = {"integer_times_6": integer, "residual": float(np.max(np.abs(block - integer)))}
    return {"deviation": deviation, "o28": o28, "point": point, "r0": r0, "rS": rs}


def _lattice_bind(block: np.ndarray) -> tuple[int, float] | None:
    for lattice in LATTICE_CANDIDATES:
        scaled = block * lattice
        residual = float(np.max(np.abs(scaled - np.rint(scaled))))
        if residual <= 1.0e-9:
            return lattice, 0.5 - residual
    return None


def _responses(integer_block: np.ndarray, sign: str) -> list[np.ndarray]:
    """Sigma responses (integer, 252) of the H-doublet subspace vectors of one hypercharge sign (G8 v2 subspaces)."""
    output = []
    for vector in g8._doublet_subspace_vectors(sign):
        column = np.zeros(integer_block.shape[1], dtype=object)
        for index, coefficient in vector.items():
            column = column + int(coefficient) * integer_block[index - chart.H_SLICE.start, :].astype(object)
        output.append(column)
    return output


def _pair_types(response: np.ndarray) -> set[str]:
    """Nonzero 16.16 pair types of the bilinear of an integer Sigma u-response (exact integer arithmetic)."""
    bilinears = g8.sigma_basis_bilinears()
    info = g8.spinor_states()
    names = [info["names"][state].split("[")[0] for state in info["sixteen"]]
    entries: dict[tuple[int, int], list[int]] = {}
    for k in range(chart.SIGMA_COMPLEX_DIM):
        re_part, im_part = int(response[2 * k]), int(response[2 * k + 1])
        if not re_part and not im_part:
            continue
        for i, j, a, b in bilinears[k]:
            slot = entries.setdefault((i, j), [0, 0])
            slot[0] += re_part * a - im_part * b
            slot[1] += re_part * b + im_part * a
    return {"-".join(sorted((names[i], names[j]))) for (i, j), value in entries.items() if value != [0, 0]}


def _monomial_values(point: Sequence[Any], degree: int) -> list[Any]:
    p, a, w = point
    return [p, a, w] if degree == 1 else [p * p, a * a, w * w, p * a, p * w, a * w]


def _coefficients(values: Mapping[tuple[int, int, int], np.ndarray], degree: int) -> list[np.ndarray]:
    if degree == 1:
        return [values[(1, 0, 0)], values[(0, 1, 0)], values[(0, 0, 1)]]
    pp, aa, ww = values[(1, 0, 0)], values[(0, 1, 0)], values[(0, 0, 1)]
    return [pp, aa, ww, values[(1, 1, 0)] - pp - aa, values[(1, 0, 1)] - pp - ww, values[(0, 1, 1)] - aa - ww]


def _rank_one_factor(vectors: Sequence[np.ndarray], degree: int) -> str | None:
    """If every monomial coefficient response is a rational multiple of one integer vector R, return the primitive
    polynomial f with response = f(p, a, w) R (sympy string, content removed, leading coefficient positive)."""
    p, a, w = sympy.symbols("p a w")
    monomials = [p, a, w] if degree == 1 else [p * p, a * a, w * w, p * a, p * w, a * w]
    reference = next((vector for vector in vectors if any(int(v) for v in vector)), None)
    if reference is None:
        return None
    pivot = next(k for k, v in enumerate(reference) if int(v))
    factor = sympy.Integer(0)
    for monomial, vector in zip(monomials, vectors, strict=True):
        ratio = Fraction(int(vector[pivot]), int(reference[pivot]))
        if any(Fraction(int(x)) != ratio * int(y) for x, y in zip(vector, reference)):
            return None
        factor += sympy.Rational(ratio.numerator, ratio.denominator) * monomial
    if factor == 0:
        return None
    _content, primitive = sympy.Poly(factor, p, a, w).primitive()
    expression = primitive.as_expr()
    if sympy.Poly(expression, p, a, w).LC() < 0:
        expression = -expression
    return str(sympy.expand(expression))


def _research_ratio_consistency(factors: Mapping[tuple[str, str], str]) -> dict[str, Any]:
    """NUM: the unit-form coefficients of the research a3 fit, converted to integer forms (a_int = a/sqrt3, w_int =
    w/sqrt6), are proportional to the exact factors f (relative 1e-5; the research values carry 6 decimals)."""
    p, a, w = sympy.symbols("p a w")
    to_unit = {"p": 1.0, "a": 1.0 / math.sqrt(3.0), "w": 1.0 / math.sqrt(6.0)}
    record = RESEARCH_RECORD["a3_polynomials"]["value"]
    worst = 0.0
    compared = 0
    for (direction, sign), factor in factors.items():
        entry = record.get(f"{SHORT[direction]}|H{sign}")
        if entry is None or factor is None:
            continue
        poly = sympy.Poly(sympy.sympify(factor), p, a, w)
        exact_unit: dict[str, float] = {}
        for monom, coefficient in poly.terms():
            label = " ".join(f"{name}" if power == 1 else f"{name}^{power}" for name, power in zip("paw", monom) if power)
            scale = math.prod(to_unit[name] ** power for name, power in zip("paw", monom))
            exact_unit[label] = float(coefficient) * scale
        research = {key: float(value) for key, value in entry.items()}
        if set(research) != set(exact_unit):
            return {"consistent": False, "compared": compared, "max_relative_deviation": None}
        key0 = sorted(research)[0]
        for key in research:
            ratio_research = research[key] / research[key0]
            ratio_exact = exact_unit[key] / exact_unit[key0]
            worst = max(worst, abs(ratio_research - ratio_exact) / max(1.0, abs(ratio_exact)))
        compared += 1
    return {"consistent": compared == len(record) and worst <= 1.0e-5, "compared": compared, "max_relative_deviation": worst}


def offq0_section(lattice_perturbation: tuple[str, int] | None = None, g8_report: Any = None) -> dict[str, Any]:
    """(E).  ``lattice_perturbation`` = (parameter, integer-point index) adds 1/L to one lattice-bound entry (mutation
    test only)."""
    g8_json = _load_json(G8_JSON) if g8_report is None else g8_report
    table = {row.get("direction_id"): row.get("representative", "") for row in (_dig(g8_json, "light_doublet", "H_degree_table") or [])}

    def phi_degree(representative: str) -> int:
        match = re.search(r"210_H(\^(\d+))?", representative)
        return 0 if match is None else int(match.group(2) or 1)

    degrees_ok = all(phi_degree(table.get(direction, "missing")) == degree for direction, degree in PHI_DEGREE.items()) and (
        "S^dag" in table.get(O38, "")
    )
    binding = compiler_binding()
    binding_ok = bool(binding["deviation"]) and max(binding["deviation"].values()) <= FLOAT_BINDING_TOLERANCE
    lattice_rows: dict[str, dict[str, Any]] = {}
    lattice_ok = True
    identity_ok = True
    zero_at_p = True
    single_type = True
    factors: dict[tuple[str, str], str | None] = {}
    source_types: dict[str, str] = {}
    rational_residual = 0.0
    integer_blocks_cache = {point: direct_u_blocks(point) for point in INTEGER_POINTS}
    rational_blocks = {point: direct_u_blocks(point) for point in RATIONAL_POINTS}
    for parameter in PARAMETERS:
        direction = parameter.split("::", 1)[1]
        degree = PHI_DEGREE[direction]
        bound: dict[tuple[int, int, int], tuple[np.ndarray, int]] = {}
        margins = []
        lattices = []
        for point in INTEGER_POINTS:
            block = integer_blocks_cache[point][parameter]
            result = _lattice_bind(block)
            if result is None:
                lattice_ok = False
                continue
            lattice, margin = result
            margins.append(margin)
            lattices.append(lattice)
            bound[point] = (np.rint(block * lattice).astype(np.int64), lattice)
        if len(bound) != len(INTEGER_POINTS):
            lattice_ok = False
            continue
        common = reduce(lambda x, y: x * y // math.gcd(x, y), lattices)
        values = {point: integer * (common // lattice) for point, (integer, lattice) in bound.items()}
        if lattice_perturbation is not None and lattice_perturbation[0] == parameter:
            point = INTEGER_POINTS[lattice_perturbation[1]]
            perturbed = values[point].copy()
            nonzero = np.argwhere(perturbed != 0)
            row, column = (tuple(nonzero[0]) if len(nonzero) else (0, 0))
            perturbed[row, column] += 1
            values[point] = perturbed
        coefficients = _coefficients(values, degree)
        for point in INTEGER_POINTS:
            predicted = sum(c * m for c, m in zip(coefficients, _monomial_values(point, degree), strict=True))
            identity_ok &= bool(np.array_equal(predicted, values[point]))
        for point in RATIONAL_POINTS:
            predicted = sum(c.astype(float) * float(m) for c, m in zip(coefficients, _monomial_values(point, degree), strict=True)) / common
            actual = rational_blocks[point][parameter]
            residual = float(np.max(np.abs(predicted - actual))) / max(1.0, float(np.max(np.abs(actual))))
            rational_residual = max(rational_residual, residual)
        # a = w = 0: the pure-p monomial (p or p^2) must give no doublet -> Sigma response.
        types_by_sign: dict[str, set[str]] = {}
        for sign in ("+", "-"):
            per_monomial = [_responses(c, sign) for c in coefficients]
            zero_at_p &= all(not any(int(v) for v in response) for response in per_monomial[0])
            types = set()
            for responses in per_monomial:
                for response in responses:
                    types |= _pair_types(response)
            types_by_sign[sign] = types
            kind = "up" if types and types <= UP_TYPE else ("down" if types and types <= DOWN_TYPE else "mixed")
            single_type &= kind == EXPECTED_SOURCE_TYPE[(direction, sign)]
            source_types[f"{parameter}|H{sign}"] = kind
            vector_factors = [_rank_one_factor([responses[k] for responses in per_monomial], degree) for k in range(4)]
            if parameter.startswith("re::"):
                factors[(direction, sign)] = vector_factors[0] if len(set(vector_factors)) == 1 else None
        lattice_rows[parameter] = {
            "phi_degree": degree,
            "lattice_denominators": sorted(set(lattices)),
            "common_lattice": common,
            "min_margin": min(margins) if margins else None,
            "pair_types": {sign: sorted(types) for sign, types in types_by_sign.items()},
        }
        lattice_ok &= bool(margins) and min(margins) >= LATTICE_MARGIN_REQUIRED
    factors_ok = all(value is not None for value in factors.values()) and all(
        factors.get(key) == expected for key, expected in EXPECTED_LINEAR_FACTORS.items()
    )
    no_p_squared = all("p**2" not in (factors.get((direction, sign)) or "p**2") for direction in (O45_B01, O45_B02) for sign in "+-")
    o28 = binding["o28"]
    o28_types = {}
    o28_ok = True
    for part, row in o28.items():
        o28_ok &= row["residual"] <= 1.0e-9
        plus = [_pair_types(response) for response in _responses(row["integer_times_6"], "+")]
        minus = [_pair_types(response) for response in _responses(row["integer_times_6"], "-")]
        o28_types[part] = {"+": sorted(set().union(*plus)), "-": sorted(set().union(*minus))}
        doublet_rows = [index - chart.H_SLICE.start for index in g8.DOUBLET_COLUMNS]
        entries = sorted({int(v) for v in row["integer_times_6"][doublet_rows, :].flat if v})
        o28_ok &= all(types and types <= UP_TYPE for types in plus) and all(not types for types in minus)
        o28_ok &= [Fraction(v, 6) for v in entries] == [Fraction(-192), Fraction(192)]
    o28_ok &= _dig(g8_json, "H_linear_portals", "lattice_binding", "patterns", f"re::{O28}", "doublet_column_entries") == ["-192", "192"]
    research = _research_ratio_consistency(factors)
    checks = {
        "portal_phi_degrees_from_committed_census_representatives": bool(degrees_ok),
        "direct_blocks_equal_live_compiler_rows_at_generic_point": bool(binding_ok),
        "lattice_bound_at_every_integer_point_margin_0_49": bool(lattice_ok),
        "polynomial_identity_verified_at_extra_points": bool(identity_ok) and rational_residual <= FLOAT_BINDING_TOLERANCE,
        "doublet_to_sigma_response_vanishes_at_a_w_zero": bool(zero_at_p),
        "each_doublet_source_feeds_one_pinned_yukawa_type": bool(single_type),
        "responses_rank_one_with_pinned_O15_O38_factors_no_p2_in_O45": bool(factors_ok and no_p_squared),
        "O28_phi_independent_and_up_type_only_at_generic_point": bool(o28_ok),
        "research_a3_coefficients_consistent_NUM": bool(research["consistent"]),
    }
    return {
        "forms": {
            "P": "e6789 (unit)", "A": "e0123 + e0145 + e2345 = sqrt3 x unit a", "W": "(e01 + e23 + e45)^(e67 + e89) = sqrt6 x unit omega",
            "unit_conversion": "a_int = a_unit/sqrt3, w_int = w_unit/sqrt6 (so (a_int + w_int) is proportional to sqrt2 a_unit + w_unit)",
        },
        "evaluation": (
            "live compiler adapter functions (portal.base_derivative for O15 and O38 with the S^dag dressing, the exact "
            "phi2_bilinear source with the 210/1050 chiral projectors for O45); H x Sigma block at H = 0, Sigma = r0 sigma_std; "
            "O15 and O45 blocks do not depend on (r0, rS), O38's is linear in rS (census S^dag degree 1): evaluated at r0 = rS = 1"
        ),
        "compiler_binding": {
            "point_p_a_w": list(binding["point"]),
            "r0": binding["r0"],
            "rS": binding["rS"],
            "max_abs_deviation": max(binding["deviation"].values()) if binding["deviation"] else None,
        },
        "integer_points": [list(point) for point in INTEGER_POINTS],
        "rational_points": [[str(x) for x in point] for point in RATIONAL_POINTS],
        "rational_max_relative_residual": rational_residual,
        "parameters": lattice_rows,
        "source_types": source_types,
        "factors_f": {f"{SHORT[d]}|H{s}": f for (d, s), f in factors.items()},
        "O28_pair_types": o28_types,
        "research_a3_consistency": research,
        "statement": (
            "Every H-linear portal's doublet -> Sigma response is a polynomial f(p, a, w) times a fixed Sigma vector (rank "
            "one per doublet vector), with no pure-p term: at a = w = 0 (the certified orientation) it vanishes, so no "
            "down-type 126bar source exists there (O28, Phi-independent, is up-type only).  O15 and O45 feed up-type from "
            "the Y = +1/2 doublet and down-type from Y = -1/2 (O15: a + w and a - w); O38 is conjugate (Y = +1/2 -> "
            "down-type with a - w, Y = -1/2 -> up-type with a + w).  A down-type source needs a != 0 or w != 0, i.e. a "
            "(15,1,1) or (15,1,3) Phi vev, which leaves the certified orientation"
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (F) m^2((15,2,2) of 126bar) = p^2/2 + O(r0^2) across the family.
# ---------------------------------------------------------------------------------------------------------------------

EXPECTED_1522_FACTORS = (
    ("lam - (1/2)", {"(3,2)_|Y|=1/6": 12}),
    ("lam - (1/2 + 1/96*r0^2)", {"(3,2)_|Y|=7/6": 12, "(8,2)_|Y|=1/2": 32}),
    ("lam - (1/2 + 37/576*r0^2)", {"(1,2)_|Y|=1/2": 4, "(3,2)_|Y|=7/6": 12, "(8,2)_|Y|=1/2": 32}),
    ("lam - (1/2 + 353/3360*r0^2)", {"(3,2)_|Y|=1/6": 12}),
    ("lam^2 - (2 + 10/3*r0^2)*lam + (3/4 + 1/4*r0^2 + 13/48*r0^4)", {"(1,2)_|Y|=1/2": 4}),
)
RS_DEPENDENT_UNITS = ("re::O12 2 Re[conj(H.H) conj(S)]", "O04 |S|^2", "O23 |S|^4")
FAMILY_POINT = (Fraction(1, 5), Fraction(1), Fraction(-1, 100), Fraction(1))  # (r0, x0, kappa, rS): the KEEPS_H_BLOCK point
WITNESS_POINT = (candidate.R0, candidate.X0, -candidate.R0 / 4, None)


def _parse_polynomial(text: str) -> sympy.Expr:
    lam, r0, eps, x0 = sympy.symbols("lam r0 eps x0")
    return sympy.sympify(text.replace("^", "**"), locals={"lam": lam, "r0": r0, "eps": eps, "x0": x0})


def _assemble_hu(point: Sequence[Any]) -> tuple[np.ndarray, int, bool]:
    r0, x0, kappa, rs = point
    units = exact_hessian.exact_unit_matrices(r0, x0) if rs is None else exact_hessian.exact_unit_matrices(r0, x0, rs=rs)
    coefficients = {key: Fraction(value) for key, value in candidate.candidate_coefficients(r0, x0, kappa, rs=rs).items()}
    coverage = exact_hessian.unit_coefficients(units, coefficients)
    terms = [(coverage["unit_coefficients"][unit["name"]] / unit["hessian"][1], unit["hessian"][0]) for unit in units]
    numerator, denominator = exact_hessian.combine(terms, (chart.TOTAL_DIM, chart.TOTAL_DIM))
    complete = bool(coverage["coefficients_proportional_to_unit_weights"] and coverage["every_nonzero_parameter_covered"])
    return numerator, int(denominator), complete


def mass_section(g6_report: Any = None) -> dict[str, Any]:
    """(F).  ``g6_report`` replaces the committed G6 tree spectrum for the fail-closed mutation test only."""
    g6 = _load_json(G6_TREE_JSON) if g6_report is None else g6_report
    lam, r0 = sympy.symbols("lam r0")
    factors = [row for row in (_dig(g6, "parametric_spectrum", "factors") or []) if isinstance(row, Mapping)]
    parsed = [(_parse_polynomial(str(row.get("polynomial", "0"))), row) for row in factors]
    found = []
    limits_ok = True
    for text, content in EXPECTED_1522_FACTORS:
        expected = _parse_polynomial(text)
        match = next(
            (row for polynomial, row in parsed if sympy.expand(polynomial - expected) == 0 and row.get("sm_content_per_root_real") == content),
            None,
        )
        if match is None:
            found.append(None)
            limits_ok = False
            continue
        roots_at_zero = sorted(sympy.solve(expected.subs(r0, 0), lam))
        limits_ok &= sympy.Rational(1, 2) in roots_at_zero
        per_root = sum(content.values())
        found.append({"polynomial": text, "multiplicity": int(match["multiplicity"]), "roots_at_r0_0": [str(v) for v in roots_at_zero],
                      "real_dimension_on_the_one_half_branch": per_root})
    total = sum(row["real_dimension_on_the_one_half_branch"] for row in found if row) if all(found) else 0
    # The scalar content has exactly one (15,2,2) (the 126bar's; the 210 has none), and every (8,2)_|Y|=1/2 state of
    # the committed spectrum lies on the bound 1/2-branch factors (64 real = the (8,2) + (8bar,2) of the complex (15,2,2)).
    octet_rows = [row for row in factors if "(8,2)_|Y|=1/2" in (row.get("sm_content_per_root_real") or {})]
    octet_states = sum(int(row["sm_content_per_root_real"]["(8,2)_|Y|=1/2"]) for row in octet_rows)
    octet_on_branch = bool(octet_rows) and all(
        any(sympy.expand(_parse_polynomial(str(row.get("polynomial", "0"))) - _parse_polynomial(text)) == 0 for text, _ in EXPECTED_1522_FACTORS)
        for row in octet_rows
    )
    units_a = {unit["name"]: unit for unit in exact_hessian.exact_unit_matrices(candidate.R0, candidate.X0)}
    units_b = {unit["name"]: unit for unit in exact_hessian.exact_unit_matrices(candidate.R0, candidate.X0, rs=Fraction(1))}
    differing = sorted(
        name for name in units_a
        if not (units_a[name]["hessian"][1] == units_b[name]["hessian"][1]
                and np.array_equal(units_a[name]["hessian"][0], units_b[name]["hessian"][0])
                and units_a[name]["gradient"][1] == units_b[name]["gradient"][1]
                and np.array_equal(units_a[name]["gradient"][0], units_b[name]["gradient"][0]))
    )
    hs = np.zeros(chart.TOTAL_DIM, dtype=bool)
    hs[chart.H_SLICE] = True
    hs[chart.S_SLICE] = True
    in_hs_blocks = True
    for name in differing:
        for units in (units_a, units_b):
            rows, columns = np.nonzero(units[name]["hessian"][0])
            in_hs_blocks &= all(
                (chart.H_SLICE.start <= i < chart.H_SLICE.stop and chart.H_SLICE.start <= j < chart.H_SLICE.stop)
                or (chart.S_SLICE.start <= i < chart.S_SLICE.stop and chart.S_SLICE.start <= j < chart.S_SLICE.stop)
                for i, j in zip(rows.tolist(), columns.tolist())
            )
    witness_num, witness_den, witness_complete = _assemble_hu(WITNESS_POINT)
    family_num, family_den, family_complete = _assemble_hu(FAMILY_POINT)
    rest = ~hs
    same_rest = bool(
        np.array_equal(
            np.asarray(witness_num[np.ix_(rest, rest)], dtype=object) * family_den,
            np.asarray(family_num[np.ix_(rest, rest)], dtype=object) * witness_den,
        )
    )
    decoupled = all(not np.any(num[np.ix_(hs, rest)]) for num in (witness_num, family_num))
    o36 = [unit for name, unit in units_a.items() if name.startswith("O36")]
    o36_empty = len(o36) == 2 and all(not np.any(unit["hessian"][0]) and not np.any(unit["gradient"][0]) for unit in o36)
    units_text = str(_dig(g6, "witness", "units") or "")
    checks = {
        "g6_tree_spectrum_committed_status": _dig(g6, "status") == G6_TREE_STATUS and _dig(g6, "n_failed") == 0,
        "fifteen_two_two_levels_bound_to_committed_g6_factors": all(row is not None for row in found),
        "fifteen_two_two_levels_tend_to_one_half_as_r0_to_0": bool(limits_ok),
        "fifteen_two_two_real_dimension_120_on_the_one_half_branch": total == 120 and octet_states == 64 and octet_on_branch,
        "chart_units_p_squared_one": "chart unit |Phi| = 1" in units_text,
        "rS_dependence_confined_to_O12_O04_O23_units_in_H_S_blocks": tuple(differing) == tuple(sorted(RS_DEPENDENT_UNITS)) and bool(in_hs_blocks),
        "phi_sigma_phi17_hessian_blocks_identical_at_witness_and_rS_1_member": bool(
            same_rest and decoupled and witness_complete and family_complete
        ),
        "O36_units_empty_at_H_zero_lambda_H_independent": bool(o36_empty),
    }
    return {
        "factors": found,
        "one_half_branch_real_dimension": total,
        "octet_doublet_states_in_spectrum": octet_states,
        "identification": (
            "the scalar content (10_H, 126bar, 210, singlets) has exactly one (15,2,2), the 126bar's (the 210 is (1,1,1) + "
            "(15,1,1) + (15,3,1) + (15,1,3) + (6,2,2) + (10,2,2) + (10bar,2,2)); all 64 (8,2)_|Y|=1/2 states of the committed "
            "spectrum lie on the bound 1/2-branch factors"
        ),
        "rS_dependent_units": differing,
        "compared_points": {"witness": "(r0, x0, kappa, rS) = (1/5, 1, -1/20, r0)", "family": "(1/5, 1, -1/100, 1)"},
        "statement": (
            "The 126bar (15,2,2) levels of the committed G6 tree spectrum are 1/2, 1/2 + r0^2/96, 1/2 + 37 r0^2/576, 1/2 + 353 "
            "r0^2/3360 and the 1/2-branch of lam^2 - (2 + 10 r0^2/3) lam + (3/4 + r0^2/4 + 13 r0^4/48): 120 real states with "
            "m^2 = p^2/2 + O(r0^2) (M_GUT^2, |p| = 1 chart unit).  r_S enters only the O12, O04 and O23 units (H and S "
            "blocks), and the O36 units are empty at H = 0, so the Phi/Sigma/Phi17 blocks (hence these levels) are the same "
            "for the r_S family and the O36 lambda_H member"
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# (H) Research record (not re-derived; sha256 provenance) and the headline composition.
# ---------------------------------------------------------------------------------------------------------------------

RESEARCH_PROVENANCE_NOTE = (
    "scratch research outputs of 2026-09-27 (wfRESCUE rescue study); not in the repository; hashes recorded for audit only; "
    "the source files are not in the repository and were hashed at generation time (the session scratch area that held "
    "them was wiped afterwards), so the sha256 values are a record of the inputs and are not re-verified at runtime"
)
RESEARCH_LABELS = ("RESEARCH_RECORD",)
RESEARCH_FILES = {
    "C/c1_spinor.py": ("C/c1_spinor.py (script)", "5fd049bbdcafb843dfd870bf28eac6328ed5b10d6a18ff0ae1ffe11c58919b9d"),
    "C/c2_weyl_lemmas.py": ("C/c2_weyl_lemmas.py (script)", "3c2f838e6ee4513027bbef97e56ef25fba7f53818e0bfa461188e39c9b7c1473"),
    "C/c2_weyl_lemmas.json": ("C/c2_weyl_lemmas.py", "0004d434d35daddfbcfd8e09b1a0e01bc2a86011afc4305fe9bacfaa2857d3a0"),
    "C/verify-feasibility/v3_45_scalar_portal.json": ("C/verify-feasibility/v3_45_scalar_portal.py", "f19529928b77c65194f648efd8646731a5d0bddcece16602dfc90b64a54024f8"),
    "C/verify-physics/v1_spinor_indep.json": ("C/verify-physics/v1_spinor_indep.py", "9316dc7d66d37f01d7a11eca7645cf0f19930d85bfa07c2b14cf384b95e3d0bb"),
    "C/c6_landau_cost.json": ("C/c6_landau_cost.py", "78cc4eb01879dae36a6aeeee96339ec1772c7409621ba237479fa4464afbb1a4"),
    "C/c8_second126_portals.json": ("C/c8_second126_portals.py", "294d5c0552ee5fae3f5b5f1efa8ac1938a23d2374d0566cac8cdc11dd0a24a1f"),
    "B/verify-feasibility/xparity.json": ("B/verify-feasibility/xparity.py", "aa4b4c4cd5dfbc9f520a3027db955d6b2aa6d70e9be180fa00fcfddb7d1e48fd"),
    "B/selection120.json": ("B/selection120.py", "3362628b29e5078a716221bebe6413e7cf935bd12624d58c3a74e81b6787621c"),
    "critic/c1_f17_light1522_scan.json": (
        "critic/c1_f17_light1522_scan.py (Route-B engine)", "4481ba5df0ee232dec1a04c39439fcfda59a423312d9b84239bb52488b139d3d"
    ),
    "B/sos120.json": ("B/sos120.py", "526d4551a529c3e7ceb3de61411374de9d89f749092ec44847fe81f7839378f9"),
    "B/fitB_pure10_120_1.27e+09_21.json": ("B/fitB.py", "c3def7c804fcaa8a2240bef012869af916d902ae6022a9ef5e7f1c7425a60a15"),
    "B/fitB_pure10_120_1e+13_22.json": ("B/fitB.py", "868b822b0497782c1a3bce914accee6d45ea37d9fb58ffe3fd4a5fd832ccea85"),
    "A/a1_selection_offq0.json": ("A/a1_selection_offq0.py", "236d57400052c7420995b76a0303241cf2a9c70ed72026a40a5ed606b57b967c"),
    "A/a2_s_structure.json": ("A/a2_s_structure.py", "138cde03a608ad8d48e2dd90d9b5e176678f77d14b29f019a6b0c874f66bf1c3"),
    "A/a3_portal_polynomials.json": ("A/a3_portal_polynomials.py", "78300c431e63d976a3bc6f7a1c5a7f3dbfd8d0cf637bebdcf0f9e20ab71cc359"),
    "routes_and_verdicts.json": ("wfRESCUE route and verifier records", "c20dff1098e95288b4b66a7060e3571dce3ed4f5eb56fd62c7cb938fe22f6434"),
}
RESEARCH_FILES_DIGEST = "3420414ab2c526a05898eb92f84eb60d9787a3d5c1a6b83f12f485b6fa51b1aa"  # sha256 of the sorted name:script:sha lines


def research_files_digest(files: Mapping[str, tuple[str, str]]) -> str:
    lines = "\n".join(f"{name}:{script}:{sha}" for name, (script, sha) in sorted(files.items()))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def _record(label: str, value: Any, meaning: str, source_json: str, key: str) -> dict[str, Any]:
    script, sha = RESEARCH_FILES[source_json]
    return {
        "label": label,
        "value": value,
        "meaning": meaning,
        "source_script": script,
        "source_json": source_json,
        "key": key,
        "source_json_sha256": sha,
        "reproducible_from_repository": False,
    }


_REC = "RESEARCH_RECORD"
RESEARCH_RECORD: dict[str, dict[str, Any]] = {
    "c2_spectral_cases": _record(
        _REC,
        {
            "contract_74_couplings_tan_beta_1": {"max_rel_spec_d_vs_e": 1.0595957387910222e-15, "CKM_max_offdiag": 4.5927327814888583e-07},
            "contract_74_couplings_generic_H": {"max_rel_spec_d_vs_e": 7.391718719670131e-16},
            "contract_plus_VL16_210PS_tan_beta_1": {"max_rel_spec_d_vs_e": 8.113039371598708e-16, "n_couplings": 104},
            "control_45_BL_vev": {"light_m_e_over_m_d": [2.493838971246228, 2.264798487049985, 1.0442383991983346]},
            "control_45_BL_plus_T3R_vev": {"CKM_max_offdiag": 0.6610669691685491},
        },
        "NUM float corroboration of L1/L2: full Weyl mass matrices with random couplings (seed 20260926); CKM ~ 1e-7 is "
        "O(v^2/M_V^2) light-heavy mixing with the 16bar SU(2)_L-singlet components (dimension-6 non-unitarity of the "
        "charged current, not a dimension-4 CKM); controls: a 45 B-L vev splits d from e, B-L + T3R gives CKM != 1",
        "C/c2_weyl_lemmas.json",
        "spectral_cases",
    ),
    "c2_sigma_entry": _record(_REC, "32j", "research value of sigma_std's only 16.16 entry (nu^c nu^c)", "C/c2_weyl_lemmas.json", "Sigma_16x16_entries"),
    "v1_independent_spinor": _record(
        _REC,
        {
            "L1_with_up_type_1522_portal_vev_tan_beta_1": {"rel_spec_d_vs_e": 8.207061487281008e-16, "CKM_max_offdiag": 0.2337713462254801},
            "L1_with_up_type_1522_portal_vev_generic_H": {"rel_spec_d_vs_e": 1.2478124017272904e-15, "CKM_max_offdiag": 0.3028018114634229},
            "c_prime_VL_plus_210_PS_0p4_15_1_1_0p5_15_1_3_tan_beta_1": {"rel_spec_d_vs_e": 0.2578586375229353,
                                                                        "rel_spec_u_vs_d": 0.20883032173625346,
                                                                        "CKM_max_offdiag": 0.9446100152897954},
            "control_down_type_1522_vev": {"rel_spec_d_vs_e": 0.0003414739726568752},
        },
        "NUM independent verifier (oscillator spinor code): L1 is portal-robust; the up-type (15,2,2) portal vev can give "
        "CKM != 1 in the toy (at unphysical portal size); (c') a vectorlike pair with the contract's own 210 reoriented "
        "((15,1,1)/(15,1,3) vevs) splits d/e and u/d with CKM != 1 at tan beta = 1",
        "C/verify-physics/v1_spinor_indep.json",
        "spectral_cases",
    ),
    "forty_five_scalar_portal": _record(
        _REC,
        {
            "A=BL,H=e8(tanb=1)": {"nu-nuc": 6.0, "e-ec": 6.0, "d-dc": 2.0, "u-uc": 2.0},
            "A=BL+0.7T3R,H=e8(tanb=1)": {"nu-nuc": 10.2, "e-ec": 1.8, "d-dc": 0.6, "u-uc": 3.4},
            "A=T3R": "no 5-form term (T3R^T3R is the PS singlet 4-form)",
        },
        "exact spinor computation of the verifier: the 45 scalar portal H^*.126bar.45.45 (X, Z17, PQ neutral) with the "
        "45.45.210 cubic induces a 126bar vev along H^(A^A) that couples Q d^c and L e^c with |lepton/quark| = 3 "
        "(off the certified orientation: it needs a GUT-scale 45 vev, a G3211 chain and a new G3 certificate)",
        "C/verify-feasibility/v3_45_scalar_portal.json",
        "A=BL / A=BL+0.7T3R / A=T3R",
    ),
    "vectorlike_reoriented_210_landau": _record(
        _REC,
        {"one_VL_pair_at_mu_G_two_loop_alpha_eq_1_GeV": 2.6935e18, "M_Pl_red_GeV": 2.435e18},
        "(c') one vectorlike 16 + 16bar (X = +-1) plus the contract's own 210 with (15,1,1)/(15,1,3) vevs: two-loop "
        "SO(10) alpha = 1 at BM-DA1 (passes at two loops); it abandons the PS witness orientation (G1-G5 restart)",
        "routes_and_verdicts.json",
        "[19].issues[1], [19].reproduced[4]",
    ),
    "off_witness_ERT_channel": _record(
        _REC,
        {"portal": "H.126bar^*.Phi210 (X, Z17 neutral)", "tadpole_ratio_J(p):J(a):J(omega)": "1:3:6",
         "induced": "a - omega proportional to mu eta v_R^2 (1/M_a^2 - 1/M_omega^2)"},
        "the contract's renormalizable H.126bar^*.210 portal feeds the down-type (15,2,2) whenever the 210 vev has a != "
        "omega (up-type only on a = omega, down-type only for a = -omega); it sits off the SOS witness (portals 0, a = "
        "omega = 0) and needs (15,2,2) doublets near v_R or an uncertified branch",
        "routes_and_verdicts.json",
        "[5].issues[0]",
    ),
    "second_126bar_landau": _record(
        _REC,
        {"two_loop_alpha_eq_1_GeV": 8.124031146123272e17, "b1_below_PQR": "21", "b2_below_PQR": "11301/2"},
        "a second complex 126bar_H at mu_G: two-loop SO(10) alpha = 1 at BM-DA1, below M_Pl,red = 2.435e18 GeV (Landau-"
        "excluded)",
        "C/c6_landau_cost.json",
        "(b) + second complex 126bar_H",
    ),
    "second_126bar_portal_census": _record(
        _REC,
        {
            "X(D2)=-2": {"FF_Yukawa_allowed": True, "X_neutral_single_step_portals": 16, "any_mixed_Phi_Sigma": False},
            "X(D2)=2": {"FF_Yukawa_allowed": False, "X_neutral_single_step_portals": 16, "any_mixed_Phi_Sigma": False},
            "X(D2)=15": {"FF_Yukawa_allowed": False, "X_neutral_single_step_portals": 6, "any_mixed_Phi_Sigma": False},
            "X(D2)=-19": {"FF_Yukawa_allowed": False, "X_neutral_single_step_portals": 6, "any_mixed_Phi_Sigma": False},
        },
        "X-charge census of the renormalizable (cubic/quartic) single-step portals linear in {H, H*} and in a second "
        "126bar D2: none uses both a Phi and a Sigma vev, so each is PS-equivariant (no (1,2,2) -> (15,2,2) map, Schur) or "
        "SU(5)-equivariant (no 10_H -> down-type 126bar doublet map); no first-order d/e split at the quartic level",
        "C/c8_second126_portals.json",
        "X(D2)=-2 / 2 / 15 / -19",
    ),
    "pure_10_120_fit_vR_1p27e9": _record(
        _REC, {"chi2": 38.53685442291748, "v_R_GeV": 1.27e9},
        "best pure 10 + 120 fit (24 starts): no chi2 < 1", "B/fitB_pure10_120_1.27e+09_21.json", "best.chi2",
    ),
    "pure_10_120_fit_vR_1e13": _record(
        _REC, {"chi2": 43.33632992490345, "v_R_GeV": 1.0e13},
        "best pure 10 + 120 fit (16 starts): no chi2 < 1", "B/fitB_pure10_120_1e+13_22.json", "best.chi2",
    ),
    "one_vectorlike_family_cs_inequality": _record(
        _REC, {"violation_factor_at_1e9_GeV": 3.647, "minimal_tan_beta": 3.41},
        "the exact one-vectorlike-family c/s inequality at tan beta = 1 is violated by the data (tan beta >= 3.4 needed; "
        "tan beta != 1 needs an extra doublet-sector tuning off the witness)",
        "routes_and_verdicts.json",
        "[9].gate_assessment.G8, [19].reproduced[5]",
    ),
    "portal_ckm_caveat": _record(
        _REC,
        {
            "CKM_max_offdiag": {
                "B' tan b=1 + up-type (15,2,2)": 0.2337713462254801,
                "A' witness generic H + up-type (15,2,2)": 0.3028018114634229,
                "VL witness tan b=1 + up-type (15,2,2)": 0.24607852429576857,
            },
            "G8_v2_theta_bound": 1.0e-3,
        },
        "with the up-type portal switched on, CKM != 1 is possible in a toy at unphysical portal size (maximum 0.3028 in "
        "v1_spinor_indep.json; the routes_and_verdicts [19].issues[4] summary quotes 0.23-0.38, and 0.38 does not appear in "
        "v1); G8 v2 bounds theta < 1e-3 at every repository r0 and a portal != 0 leaves the certified family; L1 (d = e) is "
        "portal-robust",
        "C/verify-physics/v1_spinor_indep.json",
        "spectral_cases.{B' tan b=1 + up-type (15,2,2), A' witness generic H + up-type (15,2,2), VL witness tan b=1 + "
        "up-type (15,2,2)}.CKM_max_offdiag",
    ),
    "selection120_admixture_slope": _record(
        _REC, 2.0000000429673563,
        "NUM: d log(amplitude)/d log(r0) of the (15,2,2)_120 d/e splitting amplitude (random O(1) couplings): amplitude ~ "
        "r0^2 ~ (v_R/M15)^2", "B/selection120.json", "C4_amplitude_slope_dlog_amp_dlog_r0",
    ),
    "selection120_tuned_light_1522": _record(
        _REC,
        {
            "r0": 8.3e-09,
            "M15_over_vR_and_median_amplitude": [
                [12048192.771084338, 7.884601874776446e-15],
                [120481.92771084337, 7.884601874468468e-11],
                [1204.8192771084339, 7.884598221095975e-07],
                [38.099730845402156, 0.0007881340969002458],
                [12.048192771084336, 0.007828701506677216],
                [3.809973084540216, 0.07885136228289637],
                [1.2048192771084338, 0.6543360819899953],
            ],
        },
        "NUM (random O(1) couplings): median d/e splitting amplitude of the light doublet with the (15,2,2)_120 mass M15 "
        "tuned below M_GUT at fixed r0 = 8.3e-9: amplitude ~ (v_R/M15)^2, 0.079 at M15 = 3.8 v_R and 0.65 at M15 = 1.2 v_R "
        "(O(1)); SOS squares allow such a light (15,2,2)_120 (sos120 E4: 44 massless (15,2,2)_120 components, W1 mass free)",
        "B/selection120.json",
        "C4_tuned_15",
    ),
    "light_1522_no_perturbative_two_loop_root": _record(
        _REC,
        {
            "v20_rho1e3_with_120H_one_complex_1522_at_10vR": {"n_roots": 0, "max_dRL_on_grid_log10vR_value": [11.0, -7.2079122868114816]},
            "v20_rho1e3_with_120H_no_light_1522": {"n_roots": 1},
        },
        "NUM (Route-B engine): on the v20 witness chain at rho = 1e3 with a 120_H at mu_G, one complex (15,2,2) at 10 v_R "
        "leaves no two-loop unification root (a_R - a_L stays negative on the grid); a tuned-light (15,2,2)_120 is "
        "therefore excluded only numerically",
        "critic/c1_f17_light1522_scan.json",
        "rows[design = v20, rho = 1000, with120 = true, n15 = 0 / 1, k15 = None / 10]",
    ),
    "light_1522_root_lost_to_strong_coupling": _record(
        _REC,
        {"variants_without_root": 12, "a_R_minus_a_L_range": [-17, -3], "one_loop_roots_exist": True,
         "homotopy_alpha_U_inv_at_loss": 7},
        "research verifiers: a light (15,2,2) near v_R with the anomaly-mandated spectators gives no two-loop root in 12 "
        "variants; one-loop roots exist and are lost to strong coupling along a b -> s b homotopy (alpha_U^-1 ~ 7), so the "
        "statement is 'no perturbative two-loop root'",
        "routes_and_verdicts.json",
        "[4].issues[0], [5].reproduced[5]",
    ),
    "sos120_construction": _record(
        _REC, {"E1_120_has_SM_singlet": False, "E2_pass": True, "E4_massless_1522_120_components_left_by_Sigma_squares": 44},
        "E1-E3: no T tadpole; W1 = |M T + c (h.Phi) + d (Sigma.Phi) + e (T.Phi)_2|^2 and W2 = |a (T.Sigma^*)_2 + b "
        "(h.Sigma^*)|^2 vanish at q0, so V_SOS + W1 + W2 >= V0 with the old equality set; E4 records that a light "
        "(15,2,2)_120 needs further lifting squares", "B/sos120.json", "E1_120_has_SM_singlet, E2_pass, E4_...",
    ),
    "xparity_sets": _record(
        _REC, {"4": [0, 2], "5": [0, 2], "6": [0, 2, 4], "7": [0, 2, 4], "8": [0, 2, 4, 6]},
        "independent X-charge-only enumeration of the Sigma numbers per total degree", "B/verify-feasibility/xparity.json", "4..8",
    ),
    "a1_witness_down_type": _record(
        _REC, {"max_Sig_down_at_p_witness": 0.0, "O28_Sig_up_at_r0_0p2": 300.9933},
        "NUM live-compiler scan: at the witness orientation p every down-type Sigma weight is 0", "A/a1_selection_offq0.json",
        "points['p(witness)|r0=0.2|rS=0.3'].summary",
    ),
    "a2_s_structure": _record(
        _REC, {"s_minus_1_numerator": "-e*(alpha*conjugate(alpha) - beta*conjugate(beta))", "part2_trials": 200,
               "part2_max_tan_beta_deviation": 2.220446049250313e-15},
        "sympy closed form and 200 float trials (replaced here by the exact real-type lemma)", "A/a2_s_structure.json", "part1, part2",
    ),
    "a3_polynomials": _record(
        _REC,
        {
            "O15|H+": {"a": 2.828427, "w": 2.0},
            "O15|H-": {"a": 2.828427, "w": -2.0},
            "O38|H+": {"a": 0.848528, "w": -0.6},
            "O38|H-": {"a": 0.848528, "w": 0.6},
            "O45_B01|H+": {"a^2": -2.177324, "w^2": -2.177324, "p w": -2.666667, "a w": -3.079201},
            "O45_B01|H-": {"a^2": -2.177324, "w^2": -2.177324, "p w": 2.666667, "a w": 3.079201},
            "O45_B02|H+": {"a^2": 2.177324, "w^2": -1.088662, "p w": -5.333333, "a w": 3.079201},
            "O45_B02|H-": {"a^2": 2.177324, "w^2": -1.088662, "p w": 5.333333, "a w": -3.079201},
        },
        "NUM least-squares fit (unit-normalised forms, r0 = 0.2, rS = 0.3) of the overlaps with reference vectors",
        "A/a3_portal_polynomials.json",
        "<direction>|H<sign>.to_w_u / to_w_d.coeffs (real parts)",
    ),
}


def research_section(research_files: Mapping[str, tuple[str, str]] | None = None, record: Mapping[str, Any] | None = None) -> dict[str, Any]:
    files = RESEARCH_FILES if research_files is None else research_files
    entries = RESEARCH_RECORD if record is None else record
    schema = ("label", "value", "meaning", "source_script", "source_json", "key", "source_json_sha256", "reproducible_from_repository")
    problems = []
    for name, entry in entries.items():
        if not isinstance(entry, Mapping) or set(entry) != set(schema):
            problems.append(f"{name}: schema")
            continue
        if entry["label"] not in RESEARCH_LABELS:
            problems.append(f"{name}: label")
        source = files.get(entry["source_json"])
        if source is None or source[1] != entry["source_json_sha256"] or not re.fullmatch(r"[0-9a-f]{64}", str(entry["source_json_sha256"])):
            problems.append(f"{name}: sha256")
        if entry["reproducible_from_repository"] is not False:
            problems.append(f"{name}: reproducible_from_repository")
    digest = research_files_digest(files)
    checks = {
        "research_entries_labelled_with_provenance": bool(entries) and not problems,
        "research_files_digest_pinned": digest == RESEARCH_FILES_DIGEST,
        "research_off_orientation_splitters_recorded_with_sources": all(
            name in entries for name in ("forty_five_scalar_portal", "v1_independent_spinor", "off_witness_ERT_channel", "second_126bar_landau")
        ),
    }
    return {
        "kind": "RESEARCH_RECORD",
        "provenance_note": RESEARCH_PROVENANCE_NOTE,
        "files": {name: {"script": script, "sha256": sha} for name, (script, sha) in sorted(files.items())},
        "files_digest": digest,
        "entries": dict(entries),
        "problems": problems,
        "off_orientation_splitters": [
            "the 45 scalar portal H^*.126bar.45.45 (X, Z17, PQ neutral) with the 45.45.210 cubic: a 126bar vev along H^(A^A) "
            "couples Q d^c and L e^c with |lepton/quark| = 3 (forty_five_scalar_portal)",
            "one vectorlike 16 + 16bar (X = +-1) plus the contract's own 210 with (15,1,1)/(15,1,3) vevs ((c')): splits d/e and "
            "u/d, CKM != 1 at tan beta = 1; two-loop Landau at BM-DA1 with 1 VL at mu_G 2.694e18 GeV (v1_independent_spinor, "
            "vectorlike_reoriented_210_landau)",
            "the off-witness ERT channel H.126bar^*.Phi210 at a != omega, a - omega ~ mu eta v_R^2 (1/M_a^2 - 1/M_omega^2) "
            "(off_witness_ERT_channel)",
        ],
        "also_recorded": [
            "a second 126bar_H: Landau-excluded at BM-DA1, two-loop alpha = 1 at 8.1e17 GeV (second_126bar_landau); no "
            "mixed Phi-Sigma single-step portal, so no first-order d/e split at the quartic level (second_126bar_portal_census)",
            "pure 10 + 120 fits: chi2 = 38.5 at v_R = 1.27e9 GeV and 43.3 at 1e13 GeV (pure_10_120_fit_*)",
            "the one-vectorlike-family c/s inequality at tan beta = 1: violated by a factor 3.65 (one_vectorlike_family_cs_inequality)",
            "a tuned-light (15,2,2)_120 (allowed by SOS squares) gives O(1) d/e splitting, 0.65 at M15 = 1.2 v_R "
            "(selection120_tuned_light_1522), and is excluded only numerically: no perturbative two-loop root "
            "(light_1522_no_perturbative_two_loop_root, light_1522_root_lost_to_strong_coupling)",
        ],
        "checks": checks,
    }


# ---------------------------------------------------------------------------------------------------------------------
# Report assembly.
# ---------------------------------------------------------------------------------------------------------------------

SCOPE = {
    "proved_exactly": [
        "(A) Weyl-element lemmas L1 (d <-> e) and L2 (u <-> d: spec(M_u) = spec(M_d) and CKM = 1 at the level of the light "
        "(dimension-4) Yukawa matrices at tan beta = 1) in G8 v2's exact Clifford algebra",
        "(B) contract census (26 field-level / 74 generation-expanded couplings, no X-neutral 16bar.16 pair, Z17 = X mod 17) and the P/Q/R and vectorlike corollaries",
        "(C) X-parity census of an added 120_H (Sigma number even through degree 11, first odd at 12), no SM-Cartan-neutral vector in the 120, T-linear covariants zero, p-only operators with zero (1,2,2) <-> (15,2,2) matrix elements",
        "(D) s-structure closed form, s = 1 iff e = 0 or tan beta = 1, so(4) commutant dimension 1, A (x) I_4 forms, equal Y projections of a real (2,2) vector",
        "(E) off-q0 H-doublet -> Sigma selection polynomials of O15, O38, O45 (exact by lattice binding; bound to the live compiler at a generic point), O28 Phi-independent and up-type only",
        "(F) m^2((15,2,2) of 126bar) = p^2/2 + O(r0^2) bound to the committed G6 tree spectrum; r_S and lambda_H independence of the Phi/Sigma/Phi17 blocks",
        "(G) the headline composition with G8 v2 (committed, 157 checks), the committed r_S family and the committed O36 "
        "lambda_H member (g3_sm_pati_salam_higgs_quartic_member_v20, read fail-closed)",
    ],
    "float_or_research": [
        "(E) the rational-point verification compares float evaluations with the exact polynomials (<= 1e-12 relative)",
        "(E) the research a3 least-squares coefficients are compared (NUM, relative 1e-5) with the exact factors",
        "(H) every research record: float spectra of the Weyl lemmas, the off-orientation splitters, Landau numbers, fits, the admixture slope",
    ],
    "not_claimed": [
        "no statement off the certified orientation beyond the research record: the 45 scalar portal, vectorlike matter with a "
        "reoriented 210 and the off-witness ERT channel are research-recorded, not re-derived here",
        "no loop-level flavour (threshold corrections, radiative PS breaking)",
        "the Phi-sector-only degree-2 SOS no-go for G3221/G3211 orientations is a research NUM statement, not proved here",
        "no exclusion of the SO(10) contract and no statement about the G3-G5 scalar-vacuum certificates (they stand)",
        "the 120 statement holds for a GUT-scale (15,2,2)_120 (M15 ~ M_GUT): the d/e split enters only through a "
        "(15,2,2)_120 admixture of O((v_R/M15)^2) = O(r0^2); a tuned-light (15,2,2)_120, which SOS squares allow (sos120 "
        "E4 leaves 44 massless (15,2,2)_120 components and the W1 mass M is free), gives O(1) splitting (research "
        "selection120 C4_tuned_15) and is excluded only numerically (no perturbative two-loop root, research); it is not "
        "analysed exactly here",
        "CKM = 1 is exact only at the level of the light (dimension-4) Yukawa matrices (or for purely chiral 16 content); "
        "with 16bar content the charged current of full mass eigenstates is (phases)(1 - K), K = O(v^2/M_V^2) "
        "(dimension-6 non-unitarity), not computed here",
        "with a portal switched on, CKM != 1 is not excluded (research toy caveat); such a point is outside the certified family",
        "G8 is not closed and no gate status changes; the module is not wired into the gate ledger",
    ],
}


def _collect_checks(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    output = {}
    for prefix, section in sections.items():
        for key, value in section.get("checks", {}).items():
            output[f"{prefix}.{key}"] = bool(value)
    return output


G8_NEW_ROUTE_B_PHRASES = ("on the certified witness orientation", "also split d from e", "off the certified orientation", MODULE_NAME)
G8_OLD_PHRASE = "vectorlike matter were not analysed"


def headline_section(
    sections: Mapping[str, Mapping[str, Any]], g8_report: Any = None, family_report: Any = None, quartic_report: Any = None
) -> dict[str, Any]:
    g8_json = _load_json(G8_JSON) if g8_report is None else g8_report
    family = _load_json(FAMILY_JSON) if family_report is None else family_report
    quartic = _load_json(QUARTIC_MEMBER_JSON) if quartic_report is None else quartic_report
    flags = _dig(g8_json, "flags") or {}
    route_b = str(_dig(g8_json, "routes", "B") or "")
    verdict = str(_dig(g8_json, "verdict") or "")
    not_claimed = " ".join(_dig(g8_json, "scope", "not_claimed") or [])

    def passed(name: str) -> bool:
        checks = sections.get(name, {}).get("checks", {})
        return bool(checks) and all(bool(v) for v in checks.values())

    weyl = sections.get("weyl_lemmas", {}).get("checks", {})
    l1 = bool(weyl.get("L1_composed_spec_Md_equals_spec_Me"))
    l2 = bool(weyl.get("L2_composed_tan_beta_one_spec_Mu_equals_spec_Md_and_dim4_CKM_one"))
    checks = {
        "g8_v2_committed_status_157_checks_0_failed": _dig(g8_json, "status") == G8_STATUS_REQUIRED
        and _dig(g8_json, "n_checks") == G8_EXPECTED_N_CHECKS and _dig(g8_json, "n_failed") == 0 and _dig(g8_json, "G8_status") == "OPEN",
        "g8_v2_portal_rules_and_S_independence_exact": all(
            flags.get(name) is True
            for name in (
                "M_e_equals_phase_M_d_transpose_for_every_portal_combination",
                "portal_induced_126bar_vev_up_type_only_exact",
                "every_doublet_coupled_portal_breaks_SOS27_certificate",
                "light_doublet_pure_10H_exact",
                "light_doublet_pure_10H_and_tan_beta_one_for_every_S_modulus_exact",
            )
        )
        and _dig(g8_json, "checks", "H_linear_portals.only_O45_B01_lacks_a_doublet_coupling") is True,
        "g8_v2_route_b_text_corrected": all(phrase in route_b for phrase in G8_NEW_ROUTE_B_PHRASES)
        and all(G8_OLD_PHRASE not in text for text in (route_b, verdict, not_claimed))
        and "also split d from e" in verdict and "off the certified orientation" in not_claimed,
        "family_committed_status_77_checks_0_failed": _dig(family, "status") == FAMILY_STATUS
        and _dig(family, "n_checks") == FAMILY_EXPECTED_N_CHECKS and _dig(family, "n_failed") == 0,
        "o36_quartic_member_committed_certified_0_failed": _dig(quartic, "status") == QUARTIC_MEMBER_STATUS
        and _dig(quartic, "module") == QUARTIC_MEMBER_MODULE and _dig(quartic, "n_failed") == 0
        and isinstance(_dig(quartic, "n_checks"), int) and _dig(quartic, "n_checks") == _dig(quartic, "expected_n_checks")
        and _dig(quartic, "flags", "member_theorem_claimed") is True,
        "headline_certified_family_flavour_dead": l1 and l2 and passed("corollaries") and passed("xparity_120")
        and passed("fifteen_two_two_mass") and flags.get("M_e_equals_phase_M_d_transpose_for_every_portal_combination") is True
        and flags.get("every_doublet_coupled_portal_breaks_SOS27_certificate") is True,
        "flavour_capable_sources_require_leaving_the_certified_orientation": passed("offq0_selection") and passed("s_structure"),
    }
    return {
        "theorem": (
            "Every vacuum in the degree-2-SOS-certified witness family (the committed witness, the r_S family and the O36 "
            "lambda_H member, whose certificate is g3_sm_pati_salam_higgs_quartic_member_v20; they share the "
            "Phi/Sigma/Phi17 blocks and the charged-sector vev set) is flavour-dead: M_e = phase x M_d^T and CKM = 1 "
            "(tan beta = 1) at the level of the light (dimension-4) Yukawa matrices, for (i) any H-linear portal (L1 keeps "
            "M_e = phase x M_d^T at any coefficient; every doublet-coupled portal (O15, O28, O38, O45_B02) makes q0 a "
            "saddle, O45_B01 has no doublet coupling (flavour-inert), and any portal != 0 is outside the SOS27 "
            "certificate, G8 v2), (ii) vectorlike 16s on contract scalars, (iii) P/Q/R promotion and (iv) a 120 added as "
            "SOS squares with a GUT-scale (15,2,2)_120 (M15 ~ M_GUT), up to an O(r0^2) = O((v_R/M15)^2) (15,2,2)_120 "
            "admixture.  With 16bar content ((ii), (iii) and the contract's own Pbar, Qbar, Rbar) the charged current of "
            "full mass eigenstates is non-unitary at O(v^2/M_V^2) (dimension 6); a tuned-light (15,2,2)_120 is outside "
            "(iv) (O(1) splitting, research selection120 C4_tuned_15; excluded only numerically, no perturbative two-loop "
            "root, research)"
        ),
        "caveat": (
            "RESEARCH_RECORD (portal_ckm_caveat): with the up-type portal on, CKM != 1 is possible in a toy at unphysical "
            "portal size; G8 v2 bounds theta < 1e-3 and a portal != 0 is outside the certified family; L1 (d = e) is portal-robust"
        ),
        "checks": checks,
    }


def scope_section(flags: Mapping[str, bool]) -> dict[str, Any]:
    return {"checks": {"status_neutral_never_true_flags_false": all(flags.get(name) is False for name in NEVER_TRUE_FLAGS)}}


def compute_sections(
    *,
    charged_vevs: Mapping[str, LemmaForm] | None = None,
    model_text: str | None = None,
    t_charge: int = T_X_CHARGE,
    s_points: Sequence[Sequence[tuple[int, int]]] | None = None,
    lattice_perturbation: tuple[str, int] | None = None,
    g6_report: Any = None,
    research_files: Mapping[str, tuple[str, str]] | None = None,
) -> dict[str, dict[str, Any]]:
    """The six computed sections (A)-(F) and the research record; None / default = the committed inputs, every other
    value is a fail-closed mutation."""
    return {
        "weyl_lemmas": weyl_section(charged_vevs),
        "corollaries": corollary_section(model_text),
        "xparity_120": xparity_section(t_charge),
        "s_structure": s_structure_section(s_points),
        "offq0_selection": offq0_section(lattice_perturbation),
        "fifteen_two_two_mass": mass_section(g6_report),
        "research_record": research_section(research_files),
    }


def _derive_flags(checks: Mapping[str, bool], headline: Mapping[str, Any]) -> dict[str, bool]:
    passed = bool(checks) and all(checks.values()) and len(checks) == EXPECTED_N_CHECKS
    head = headline.get("checks", {})
    flags = {
        "certified_family_flavour_dead_exact": bool(passed and head.get("headline_certified_family_flavour_dead")),
        "L1_portal_robust": bool(passed and checks.get("weyl_lemmas.L1_composed_spec_Md_equals_spec_Me")
                                 and head.get("g8_v2_portal_rules_and_S_independence_exact")),
        "off_orientation_splitters_research_recorded": bool(passed and checks.get("research_record.research_off_orientation_splitters_recorded_with_sources")),
        "evidence_only": True,
    }
    for name in NEVER_TRUE_FLAGS:
        flags[name] = False
    return flags


def assemble_report(
    sections: Mapping[str, Mapping[str, Any]],
    *,
    started: float | None = None,
    g8_report: Any = None,
    family_report: Any = None,
    quartic_report: Any = None,
) -> dict[str, Any]:
    started = time.time() if started is None else started
    ordered = {name: sections[name] for name in ("weyl_lemmas", "corollaries", "xparity_120", "s_structure", "offq0_selection", "fifteen_two_two_mass")}
    corollaries = dict(ordered["corollaries"])
    corollary_checks = dict(corollaries.get("checks", {}))
    corollary_checks["corollaries_follow_from_L1_and_L2"] = bool(
        sections["weyl_lemmas"]["checks"].get("L1_composed_spec_Md_equals_spec_Me")
        and sections["weyl_lemmas"]["checks"].get("L2_composed_tan_beta_one_spec_Mu_equals_spec_Md_and_dim4_CKM_one")
        and all(v for k, v in corollary_checks.items() if k != "corollaries_follow_from_L1_and_L2")
    )
    corollaries["checks"] = corollary_checks
    ordered["corollaries"] = corollaries
    headline = headline_section(ordered, g8_report, family_report, quartic_report)
    ordered["headline"] = headline
    ordered["research_record"] = sections["research_record"]
    checks = _collect_checks(ordered)
    flags = _derive_flags({**checks, "scope.status_neutral_never_true_flags_false": True}, headline)
    ordered["scope"] = scope_section(flags)
    checks = _collect_checks(ordered)
    flags = _derive_flags(checks, headline)
    failures = sorted(name for name, value in checks.items() if not value)
    count_ok = len(checks) == EXPECTED_N_CHECKS
    if not count_ok:
        failures.append(f"check_count_{len(checks)}_expected_{EXPECTED_N_CHECKS}")
    passed = not failures
    report = {
        "module": MODULE_NAME,
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": STATUS_RECORDED if passed else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_RECORDED if passed else OVERALL_STATE_OPEN,
        "gate": "G8",
        "n_checks": len(checks),
        "expected_n_checks": EXPECTED_N_CHECKS,
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "scope": {"claimed": SCOPE["proved_exactly"], "float_or_research": SCOPE["float_or_research"], "not_claimed": SCOPE["not_claimed"]},
        **{name: section for name, section in ordered.items() if name != "scope"},
        "provenance": {
            "research_note": RESEARCH_PROVENANCE_NOTE,
            "research_files": {name: {"script": script, "sha256": sha} for name, (script, sha) in sorted(RESEARCH_FILES.items())},
            "repository_inputs": [
                "g8_sm_pati_salam_flavour_nogo_v20 (Clifford algebra, spinor states, contract parser, sigma-basis bilinears, doublet subspaces)",
                "live compiler adapters: live_g2_exact_portal_family_derivatives_v20, live_g2_exact_final_mixed_quartic_derivatives_v20, "
                "exact_phi2_h_126dag_210_1050_channels_v20; g3_candidate_physical_target_audit_v20.parameter_rows (binding)",
                "g3_sm_pati_salam_exact_hessian_v20 (exact unit matrices), g3_sm_pati_salam_candidate_v20 (coefficient map, sigma_std)",
                G8_JSON.name + ", " + G6_TREE_JSON.name + ", " + FAMILY_JSON.name + ", " + QUARTIC_MEMBER_JSON.name
                + " (read-only, fail closed)",
            ],
        },
        "verdict": "",
        "runtime_seconds": 0.0,
    }
    if any(flags[name] for name in NEVER_TRUE_FLAGS):
        raise AssertionError("the structural-obstruction record is status-neutral")
    report["verdict"] = _verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


def build_report(**mutations: Any) -> dict[str, Any]:
    started = time.time()
    return assemble_report(compute_sections(**mutations), started=started)


def report_passes(report: Mapping[str, Any]) -> bool:
    try:
        return bool(
            report["status"] == STATUS_RECORDED
            and report["n_failed"] == 0
            and report["n_checks"] == EXPECTED_N_CHECKS
            and len(report["checks"]) == EXPECTED_N_CHECKS
            and all(report["checks"].values())
            and report["flags"]["certified_family_flavour_dead_exact"] is True
            and all(report["flags"][name] is False for name in NEVER_TRUE_FLAGS)
        )
    except (KeyError, TypeError):
        return False


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "FAIL-CLOSED: the G8 structural-obstruction record is NOT established (failed: " + ", ".join(report["failures"])
            + ").  No statement about the certified family's flavour sector is recorded; no gate status changes."
        )
    census = report["xparity_120"]["census"]
    return (
        "EXACT: every vacuum in the degree-2-SOS-certified witness family (the committed witness, the r_S family and the O36 "
        "lambda_H member, certified by g3_sm_pati_salam_higgs_quartic_member_v20) is flavour-dead: M_e = phase x M_d^T and "
        "CKM = 1 (tan beta = 1) at the level of the light (dimension-4) Yukawa matrices.  The Weyl element g_de (pi-rotation "
        "in the (3,5) plane, lift Gamma_3 Gamma_5) fixes every charged-sector vev bilinear and maps d[+--] to e[+++]; sigma_std "
        "couples only nu^c nu^c; so spec(M_d) = spec(M_e) for any 16/16bar content (L1).  g_cust (the (7,9) plane) gives "
        "spec(M_u) = spec(M_d) exactly and CKM = 1 at the dimension-4 level at tan beta = 1 (L2); with 16bar content the "
        "charged current of full mass eigenstates is (phases)(1 - K), K = U_d^dag P_{16bar SU(2)_L-singlet} U_d = "
        "O(v^2/M_V^2) (dimension-6 non-unitarity; exactly 0 without 16bar states).  This holds for any H-linear portal (L1 "
        "is portal-robust; every doublet-coupled portal (O15, O28, O38, O45_B02) makes q0 a saddle, O45_B01 has no doublet "
        "coupling (flavour-inert), and any portal != 0 is outside the SOS27 certificate), for vectorlike 16s on contract "
        "scalars and P/Q/R promotion (the contract's 74 couplings have no X-neutral 16bar.16 pair), and for a 120_H added as "
        "SOS squares with a GUT-scale (15,2,2)_120 (M15 ~ M_GUT): the d/e split then enters only through a (15,2,2)_120 "
        "admixture of O((v_R/M15)^2) = O(r0^2) (X-parity bounds the PS-breaking H/T entries at O(r0^2): Sigma number even "
        f"through degree 11, the first odd-Sigma monomial at degree {census['min_odd_sigma_degree']}); a tuned-light "
        "(15,2,2)_120, which SOS squares allow, gives O(1) splitting (research selection120 C4_tuned_15) and is excluded "
        "only numerically (no perturbative two-loop root, research).  The 126bar's (15,2,2) (not the 120's) has m^2 = p^2/2 "
        "+ O(r0^2) across the family.  Off q0 every H-linear portal's down-type 126bar source needs a "
        "(15,1,1) or (15,1,3) Phi vev, i.e. it leaves the certified orientation.  RESEARCH_RECORD (not re-derived): the 45 "
        "scalar portal, vectorlike matter with a reoriented 210 and the off-witness ERT channel also split d from e, but all "
        "sit off the certified orientation; a second 126bar is Landau-excluded at BM-DA1 (8.1e17 GeV, two loops).  G8 is not "
        "closed, the contract and the G3-G5 certificates are not falsified, and no gate status changes."
    )


def _markdown(report: Mapping[str, Any]) -> str:
    weyl = report["weyl_lemmas"]
    lines = [
        "# G8 structural obstruction: the SOS-certified witness family is flavour-dead (v20, evidence only)",
        "",
        f"- Status: `{report['status']}`",
        f"- Overall state: `{report['overall_state']}`",
        f"- Checks: {report['n_checks'] - report['n_failed']}/{report['n_checks']} pass (expected {report['expected_n_checks']})",
        "- No gate status changes; not wired into the gate ledger.",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
        "## (A) Weyl-element lemmas [EXACT]",
        "",
        "| element | lift | covariant | monomial | flipped weight slots |",
        "|---|---|---|---|---|",
    ]
    for label, row in weyl["elements"].items():
        lines.append(f"| {label} | {row['lift']} | {row['covariant']} | {row['monomial']} | {row['flips_only_slots']} |")
    lines += ["", "| vev | g_de | g_cust |", "|---|---|---|"]
    for name in weyl["elements"]["g_de"]["vev_table"]:
        lines.append(f"| {name} | {weyl['elements']['g_de']['vev_table'][name]} | {weyl['elements']['g_cust']['vev_table'][name]} |")
    lines += [
        "",
        "State maps on the 16: g_de " + ", ".join(f"{k} -> {v}" for k, v in weyl["elements"]["g_de"]["state_map_16"].items()) + ".",
        "",
        "g_cust " + ", ".join(f"{k} -> {v}" for k, v in weyl["elements"]["g_cust"]["state_map_16"].items()) + ".",
        "",
        f"- sigma_std 16.16 entries: {weyl['sigma_std_16x16_entries']}.",
        f"- Torus reduction: {weyl['torus_reduction']}.",
        f"- L1: {weyl['lemma_L1']}.",
        f"- L2: {weyl['lemma_L2']}.",
        "",
        "## (B) Corollaries [EXACT]",
        "",
        f"- {report['corollaries']['statement']}.",
        f"- Scalars used: {', '.join(report['corollaries']['scalars_used'])}; generation-expanded couplings: "
        f"{report['corollaries']['generation_expanded_count']}.",
        f"- Vectorlike pair: new couplings {', '.join(report['corollaries']['vectorlike_pair']['new_couplings'])}.",
        "",
        "## (C) X-parity of an added 120_H [EXACT]",
        "",
        "| total degree <= D | Sigma numbers |",
        "|---|---|",
    ]
    for degree, values in sorted(report["xparity_120"]["census"]["sigma_numbers_up_to_degree"].items(), key=lambda item: int(item[0])):
        lines.append(f"| {degree} | {values} |")
    ops = report["xparity_120"]["p_only_operators"]
    lines += [
        "",
        f"- Minimal odd-Sigma degree: {report['xparity_120']['census']['min_odd_sigma_degree']}; examples: "
        f"{'; '.join(report['xparity_120']['census']['odd_examples_at_min_degree'])}.",
        f"- SM-Cartan kernel on the 120: {report['xparity_120']['sm_cartan_kernel_on_120']}.",
        f"- T-linear covariants (nonzero components): {report['xparity_120']['t_linear_covariants_nonzero_components']}.",
        f"- p-only operators: {ops['n_122_to_1522_matrix_elements']} (1,2,2) <-> (15,2,2) matrix elements, max |value| "
        f"{ops['max_abs_122_to_1522']}; controls {ops['control_max_H_to_122_120']}, {ops['control_max_1522_diagonal_ch1']}.",
        f"- {report['xparity_120']['consequence']}.",
        "",
        "## (D) s-structure and the real-type lemma [EXACT]",
        "",
        f"- s(G3221) - 1 = {report['s_structure']['s_minus_1_G3221']}.",
        f"- s at the claimed points: {report['s_structure']['s_at_claimed_points']}; control (tan beta = 2, e != 0): "
        f"{report['s_structure']['s_at_control_point']}.",
        f"- so(4) commutant dimension {report['s_structure']['commutant_dimension']}; invariant two-copy forms "
        f"{report['s_structure']['invariant_two_copy_form_dimension']}.",
        f"- {report['s_structure']['lemma']}.",
        "",
        "## (E) Off-q0 selection polynomials [EXACT by lattice binding]",
        "",
        f"- {report['offq0_selection']['evaluation']}.",
        f"- Compiler binding: {report['offq0_selection']['compiler_binding']}.",
        "",
        "| source | Yukawa type | f(p, a, w) (integer forms) |",
        "|---|---|---|",
    ]
    for key, value in report["offq0_selection"]["factors_f"].items():
        direction = {v: k for k, v in SHORT.items()}[key.split("|")[0]]
        sign = key.split("|H")[1]
        label = key.replace("|", " ")
        lines.append(f"| {label} | {report['offq0_selection']['source_types'].get(f're::{direction}|H{sign}')} | `{value}` |")
    lines += [
        "",
        f"- O28 pair types at the generic point: {report['offq0_selection']['O28_pair_types']}.",
        f"- Research a3 consistency (NUM): {report['offq0_selection']['research_a3_consistency']}.",
        f"- {report['offq0_selection']['statement']}.",
        "",
        "## (F) m^2((15,2,2) of 126bar) [EXACT]",
        "",
        "| G6 factor | multiplicity | roots at r0 = 0 |",
        "|---|---|---|",
    ]
    for row in report["fifteen_two_two_mass"]["factors"]:
        if row:
            lines.append(f"| {row['polynomial']} | {row['multiplicity']} | {row['roots_at_r0_0']} |")
    lines += [
        "",
        f"- {report['fifteen_two_two_mass']['statement']}.",
        "",
        "## (G) Headline [EXACT, composed]",
        "",
        f"- {report['headline']['theorem']}.",
        f"- Caveat: {report['headline']['caveat']}.",
        "",
        "## (H) Research record (not re-derived)",
        "",
        f"- {report['research_record']['provenance_note']}.",
    ]
    lines += [f"- {item}." for item in report["research_record"]["off_orientation_splitters"]]
    lines += [f"- {item}." for item in report["research_record"]["also_recorded"]]
    lines += ["", "| file | sha256 |", "|---|---|"]
    for name, row in report["research_record"]["files"].items():
        lines.append(f"| {name} | `{row['sha256']}` |")
    lines += ["", "## Scope", ""]
    for key, items in report["scope"].items():
        lines.append(f"**{key}**")
        lines += [f"- {item}" for item in items]
        lines.append("")
    lines += ["## Flags", ""]
    lines += [f"- `{key}`: {value}" for key, value in report["flags"].items()]
    lines += ["", "## Checks", ""]
    lines += [f"- {'PASS' if value else 'FAIL'} `{key}`" for key, value in report["checks"].items()]
    return "\n".join(lines) + "\n"


def write_report(report: Mapping[str, Any]) -> bool:
    """Write the JSON and Markdown only for a passing report (fail closed); returns whether they were written."""
    if not report_passes(report):
        return False
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(json_roundtrip(report)), encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts (only if every check passes)")
    args = parser.parse_args(argv)
    report = build_report()
    written = write_report(report) if args.write else False
    summary = {key: report[key] for key in ("status", "overall_state", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    summary["written"] = written
    print(json.dumps(_jsonable(summary), indent=2))
    if not report_passes(report):
        return 1
    if args.write and not written:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
