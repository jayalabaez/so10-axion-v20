#!/usr/bin/env python3
"""Route C negative certificate for G8: the SM Pati-Salam G3 witness branch has no viable flavour sector (v20).

The certified G3 witness (g3_sm_pati_salam_candidate_v20, 27-parameter benchmark of the 51-parameter exact-X
potential, vacuum q0 = (p, 0, r0 sigma_std, r0, x0), exact Hessian in g3_sm_pati_salam_exact_hessian_v20) is a
scalar-vacuum certificate.  This module asks whether the SAME branch can carry the observed charged-fermion and
neutrino flavour sector at renormalizable tree level.  It cannot.  The argument is exact where it is structural and
float only where it meets data.

(1) Light doublet = pure 10_H (exact).  From the census orbit keys of the 44 live directions, exactly five
    directions (O15, O28, O38, O45_B01, O45_B02; ten re/im parameters) are linear in (H, H^dag).  At H = 0 only those
    can couple H to Phi or Sigma in the Hessian, and all ten vanish in the benchmark map for every r0, x0 (sympy).  The
    exact Hessian (binding units of g3_sm_pati_salam_exact_hessian_v20, Fraction arithmetic) at r0 = 1/5, 1/20, 1/100
    and the physical anchor r0 has H-block rows that vanish outside the H block, with the H block exactly
    diag(Re triplet 2, Im triplet 2 + 2 r0^2, Re doublet 0, Im doublet 2 r0^2) in u = (Re, Im) coordinates, and a zero
    gradient.  So the light doublet is exactly span{Re H_6..9}: no 126bar (15,2,2) and no 210 admixture.  The census
    has no H-degree-3 direction (H-degrees {0, 1, 2, 4}), so with the H-linear parameters zero V is even in H; the
    SU(2)_L centre element -1 composed with H -> -H fixes q0 + h for every light-doublet value h and acts as -1 on
    every heavy doublet, so no heavy doublet (126bar (15,2,2), 210 doublets) gets an induced vev at any order in v at
    tree level (the (10,3,1) part rests on O31/O35 = 0, checked).

(2) Clebsches and flavour relations (exact).  An exact Gaussian-integer Clifford algebra of so(10) (32 x 32, entries
    0, +-1, +-i) with charge conjugation C gives: the chirality whose repository hypercharge spectrum is one
    left-handed family (the 16); 16x16 = 10 + 120 + 126 and 16x16bar = 1 + 45 + 210 (exact ranks over GF(p) plus
    exact duality pairing); the 16.16.10 bilinear at any real neutral vev a e8 + b e9 (Re H_8, Re H_9; Q_em = 0 on
    that plane with the repository's integer Q_em) has only the eight Dirac pairs, with |c_u|^2 = |c_d|^2 = |c_e|^2 =
    |c_nu|^2 = a^2 + b^2, c_nu/c_u and c_e/c_d constant phases; the repository's sigma_std couples only nu^c nu^c; the
    (15,2,2) forms carry the relative lepton/quark Clebsch -3 exactly.  The SARAH model file is parsed and every
    renormalizable fermion bilinear allowed by SO(10) x U(1)_X (Z17 consistent) is enumerated: no 16.16.10_H^* coupling
    exists, H10/126bar Yukawas live only on the X = 1 16s (F, P, R), every 16.16bar mass is an SO(10) singlet vev, no
    120_H exists, and the allowed 16bar x 16 coupling pattern has generic rank 8 (exact rank at deterministic integer
    couplings), i.e. exactly three light families for generic couplings (assumed at the physical point).  Hence at dimension four the light-family mass matrices are M_u = c_u Y, M_d = c_d Y, M_e = c_e Y,
    M_D = c_nu Y with one symmetric Y (sympy): CKM = 1, m_u/m_d = m_c/m_s = m_t/m_b = 1 (tan beta = 1), m_e = m_d,
    m_mu = m_s, m_tau = m_b, M_D = M_u; the 126bar enters only M_R = Y_126 v_R.  SM running preserves the alignment.
    Data (PDG 2024, FLAG 2021, Xing-Zhang-Zhou 2008 running masses, one-loop SM running; float) exclude these
    relations by many sigma, with the tan-beta-independent, scale-robust tests load-bearing.

(3) The O28 portal alone (exact / parametric; the other portals zero).  O28 is the largest direct 10_H-(15,2,2)
    portal.  Its H-Sigma block is bound to the integer lattice (+-192 r0^2 in u coordinates) and the first-order
    (15,2,2) admixture of the witness light doublet Re H_6..9 is computed exactly: theta^2 = c^2 r0^4 R(r0), R(r) =
    7962624 (13 r^2 + 6)^2 / (13 r^4 + 12 r^2 + 36)^2, R(0) = 221184 = 6 * 192^2, i.e. theta -> 192 sqrt(6) c r0^2 ~
    470.3 c r0^2 (the scratch value 666 used the full block norm 192 sqrt(3) with M^2 = 1/2 instead of the light-doublet
    row).  For a light doublet with t = |5|/|5bar| the admixture is sqrt(2 t^2/(1 + t^2)) theta (<= sqrt(2) theta; exact
    Gram structure of (3b)), and it is purely up-type (exact selection rule of (3b)): O28 cannot split b from tau at
    all.  With O28 on, the doublet Schur complement is O(c^2) and mixes Re H and Im H, so tan beta leaves 1 (float:
    <= 1.19 inside the colour-stable range); restricted to that range (|c| <= min(4 pi, rho_O28(r0)), rho_O28 ~ 1/r0,
    4.54 at the 2HDM-content r0) Mirsky's singular-value inequality needs ||Y_F|| >= ~6e3 for the t-b split at every
    repository r0, with Y_F the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2).  For every c != 0 the
    doublet Schur complement at q0 is negative, so q0 is a saddle of V + c O28: portal = 0 is load-bearing for SOS27.

(3b) All five H-linear portals (O15, O28, O38, O45_B01, O45_B02) on the full H block.  All twenty H columns (colour
    triplets Re/Im H_0..5 and doublets Re/Im H_6..9) of every portal's Hessian at q0 are bound to the (1/6) Z lattice
    with pinned blocks and r0 powers (doublets: O28 Sigma r0^2; O15, O45_B02 Phi r0; O38 Phi r0^2; O45_B01 none;
    triplets: O15 Sigma r0^0 (the 126bar (6,1,1) through <Phi> = p) and Phi r0, O38 Sigma r0 and Phi r0^2, O28 Sigma
    r0^2, O45_B01/B02 Phi r0).  The Hessian of V + sum c_k O_k at q0 is exactly [[H_HH, B(c)^T], [B(c), A]], so the
    Schur complement on the H block is O(c^2) (exactly quadratic in c) and decides second-order stability (Haynsworth);
    its triplet and doublet blocks decouple and are phase independent (exact).  Colour-stable region: |c_O15| <= 0.7906
    at every repository r0 (beyond it q0 has GUT-scale (3,1)_|Y|=1/3 tachyons), |c_O28| <= rho_O28(r0) (14.1, 17.0,
    4.54, 230 at the four repository r0), O38 and O45 colour-stable in the 4 pi box; exact inertia brackets per radius,
    inner (sum |c_d|/rho_d <= 1) and outer (Cauchy-Schwarz) certificates for combinations.  Raising O06 cures only the
    doublet saddle (it lifts triplets and doublets alike; the doublet must stay light).  Inside the colour-stable region
    O45_B02 still moves tan beta past m_t/m_b (O15 only beyond its colour radius), so the t-b bound of (3) does NOT
    extend to the portal set.  But O15, O28, O45_B02 act only on the Y = +1/2 doublet component and O38 only on
    Y = -1/2, and every portal-induced 126bar vev couples only Q u^c and L nu^c (exact 16.16 bilinears at every
    repository r0): M_e = phase x M_d^T survives every portal combination at any coefficient, and the portal-immune
    tests (m_s/m_d)/(m_mu/m_e) and (m_b/m_s)/(m_tau/m_mu) (>= 10 sigma with a 10% theory term) exclude the portal fix at
    every repository r0.  Every doublet-coupled portal c != 0 makes q0 a saddle (SOS27 needs portal = 0).

(4) Seesaw (float, not load-bearing).  With M_D = M_u(data) (the generic SO(10) premise, not a prediction of the
    witness) at v_R = M_I the generic requirement is Y_R ~ m_t(M_I)^2/(sqrt(dm31^2) v_R) = O(10^2 - 10^4); a textured
    Y_126 with (m_nu^-1)_tautau ~ 0 lowers it and is reported honestly (it can reach perturbative values at the upper
    end of the v_R band).  On the witness itself M_D has the singular values of M_e = M_d (tan beta = 1), for which
    the generic Y_R ~ m_tau^2/(sqrt(dm31^2) v_R) ~ 0.06 at 1e12 GeV.

(5) Scope.  This does not falsify the G3-G5 scalar-vacuum certificates or the SO(10) contract; it records that THIS
    witness branch (renormalizable 27-parameter SM Pati-Salam benchmark family, H-linear portals zero) cannot close
    G8, and that no H-linear portal repair survives at q0.  Routes: A (new in-contract G3 branch away from q0 with a
    down-type (15,2,2) mixing channel), B (extension beyond the contract: 120_H or a second 10_H), C (record this
    no-go, G8 OPEN).  G8 stays OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import time
from collections import Counter, deque
from collections.abc import Mapping, Sequence
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import sympy
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
from sympy.polys.matrices import DomainMatrix

import g1_exact_declared_symmetry_character_census_v20 as census
import g3_candidate_physical_target_audit_v20 as target
import g3_sigma_hypercharge_audit_v20 as hypercharge
import g3_sm_pati_salam_candidate_v20 as candidate
import g3_sm_pati_salam_exact_hessian_v20 as exact_hessian
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.json"
OUT_MD = ROOT / "G8_SM_PATI_SALAM_FLAVOUR_NOGO_V20.md"
MODEL_FILE = ROOT / "models" / "SO10Z17AxionV20.m"
CANDIDATE_JSON = candidate.OUT_JSON
EXACT_HESSIAN_JSON = exact_hessian.OUT_JSON

MODEL_CONTRACT_ID = candidate.MODEL_CONTRACT_ID
STATUS_RECORDED = "G8_SM_PATI_SALAM_WITNESS_FLAVOUR_NOGO__ROUTE_C_RECORDED__G8_OPEN"
STATUS_INCOMPLETE = "G8_SM_PATI_SALAM_FLAVOUR_NOGO_INCOMPLETE__G8_OPEN"
OVERALL_STATE_RECORDED = "WITNESS_BRANCH_FLAVOUR_EXCLUDED_AT_RENORMALIZABLE_TREE_LEVEL"
OVERALL_STATE_OPEN = "G8_FLAVOUR_NOGO_NOT_ESTABLISHED"
CANDIDATE_STATUS = "SM_PATI_SALAM_G3_CANDIDATE__EXACT_GLOBAL_MINIMUM_OF_BENCHMARK_POTENTIAL__SM_UNBROKEN__G3_OPEN"
EXACT_HESSIAN_STATUS = exact_hessian.STATUS_CERTIFIED
DIGITS = 12

R0 = candidate.R0
X0 = candidate.X0
H_SLICE = chart.H_SLICE
SIGMA_SLICE = chart.SIGMA_SLICE
PHI_SLICE = chart.PHI_SLICE
TOTAL_DIM = chart.TOTAL_DIM
DOUBLET_REAL_X = tuple(candidate.DOUBLET_REAL_X)  # Re H_6..9 (chart = u indices)
DOUBLET_IMAG_X = tuple(index + 1 for index in DOUBLET_REAL_X)
EXACT_R0_VALUES = (Fraction(1, 5), Fraction(1, 20), Fraction(1, 100))
O28_DIRECTION = "O28_B01_unique_Hdag_Sigma2_Sigmadag"
O28_IDS = (f"re::{O28_DIRECTION}", f"im::{O28_DIRECTION}")
EXPECTED_H_LINEAR_DIRECTIONS = (
    "O15_B01_Phi_Hdag_Sigma",
    "O28_B01_unique_Hdag_Sigma2_Sigmadag",
    "O38_B01_Phi_Hdag_Sigmadag",
    "O45_B01_Phi2_Hdag_Sigma_210_1050",
    "O45_B02_Phi2_Hdag_Sigma_210_1050",
)
EXPECTED_NONZERO_H_QUADRATIC = (
    "lambda::O06_B01_Hdag_H_norm",
    "lambda::O46_B01_Phi2_HdagH_channels",
    "lambda::O46_B03_Phi2_HdagH_channels",
    "re::O12_B01_Hdag_Hdag_pair",
)
# H-degree-2 operators that also contain Sigma: O31 (H^dag^2 Sigma^2: a Sigma-induced 5/5bar split, i.e. tan beta) and
# O35 (H H^dag Sigma Sigma^dag: the 54 channel carries the type-II Delta_L Delta_R^* h h^dag term).
H_SIGMA_QUADRATIC_DIRECTIONS = ("O31_B01_unique_Hdag2_Sigma2", "O35_B01_H_Sigma_hermitian", "O35_B02_H_Sigma_hermitian")

# O28 closed forms (derived in o28_section by exact interpolation + exact linear solve; pinned here for fail-closed).
O28_LATTICE_ENTRY = 192
O28_R_NUMERATOR = "7962624*(13*r**2 + 6)**2"
O28_R_DENOMINATOR = "(13*r**4 + 12*r**2 + 36)**2"
O28_R_AT_ZERO = Fraction(221184)
PERTURBATIVE_LIMIT = math.sqrt(4.0 * math.pi)  # |Y| <= sqrt(4 pi): the usual Yukawa perturbativity bound
PORTAL_BOX = 4.0 * math.pi  # the repository's |coefficient| < 4 pi box for scalar couplings
NOGO_PULL_THRESHOLD = 5.0  # "excluded by many sigma": every load-bearing test >= 5 sigma with inflated uncertainties
# All five H-linear directions: the chart block to which their Hessian at q0 couples the light-doublet columns
# (Re/Im H_6..9) and the power of r0 of that coupling (the vev factors left after d_H and one other derivative at
# H = 0, x0 = 1).  Pinned (fail closed); the lattice binding re-derives both from the compiler at r0 = 1 and 1/5.
PORTAL_DOUBLET_COUPLING: dict[str, tuple[str | None, int]] = {
    "O15_B01_Phi_Hdag_Sigma": ("Phi210", 1),  # Phi H^dag Sigma: d_H d_Phi ~ <Sigma> = r0 sigma_std
    "O28_B01_unique_Hdag_Sigma2_Sigmadag": ("Sigma126bar", 2),  # H^dag Sigma^2 Sigma^dag: d_H d_Sigma ~ <Sigma>^2
    "O38_B01_Phi_Hdag_Sigmadag": ("Phi210", 2),  # Phi H^dag Sigma^dag S^dag: d_H d_Phi ~ <Sigma^dag> <S^dag>
    "O45_B01_Phi2_Hdag_Sigma_210_1050": (None, 0),  # no light-doublet coupling at q0
    "O45_B02_Phi2_Hdag_Sigma_210_1050": ("Phi210", 1),  # Phi^2 H^dag Sigma: d_H d_Phi ~ <Phi> <Sigma>
}
PORTAL_BLOCK_SLICES = {
    "Phi210": PHI_SLICE,
    "H10": H_SLICE,
    "Sigma126bar": SIGMA_SLICE,
    "S": chart.S_SLICE,
    "Phi17": chart.X_SLICE,
}
# The colour-triplet columns (Re/Im H_0..5) of every H-linear direction's Hessian at q0: the chart blocks they couple
# to and the power of r0 of each coupling (pinned, fail closed; the lattice binding re-derives them).  O15 reaches the
# 126bar (6,1,1) through the PS-singlet <Phi> = p at O(1), O38 through <Phi><S^dag> ~ r0.
PORTAL_TRIPLET_COUPLING: dict[str, tuple[tuple[str, int], ...]] = {
    "O15_B01_Phi_Hdag_Sigma": (("Phi210", 1), ("Sigma126bar", 0)),
    "O28_B01_unique_Hdag_Sigma2_Sigmadag": (("Sigma126bar", 2),),
    "O38_B01_Phi_Hdag_Sigmadag": (("Phi210", 2), ("Sigma126bar", 1)),
    "O45_B01_Phi2_Hdag_Sigma_210_1050": (("Phi210", 1),),
    "O45_B02_Phi2_Hdag_Sigma_210_1050": (("Phi210", 1),),
}
# The hypercharge component of the 10_H doublets on which each direction's doublet columns act at q0 (the other one is
# annihilated exactly on the integer lattice): "+" = Y = +1/2 (the "5": z4 = e6 + i e7, z5 = e8 + i e9, whose vev gives
# the up-type 10_H Yukawa), "-" = Y = -1/2 (the "5bar", their conjugates).  Pinned, fail closed.
PORTAL_DOUBLET_SOURCE: dict[str, str | None] = {
    "O15_B01_Phi_Hdag_Sigma": "+",
    "O28_B01_unique_Hdag_Sigma2_Sigmadag": "+",
    "O38_B01_Phi_Hdag_Sigmadag": "-",
    "O45_B01_Phi2_Hdag_Sigma_210_1050": None,
    "O45_B02_Phi2_Hdag_Sigma_210_1050": "+",
}
# Real u-vectors (H index, Re/Im, coefficient) spanning the two hypercharge components of the doublets: z, i z for
# z = z4, z5 (Y = +1/2) and for their conjugates (Y = -1/2).
DOUBLET_SUBSPACES: dict[str, tuple[tuple[tuple[int, str, int], ...], ...]] = {
    "+": (((6, "Re", 1), (7, "Im", 1)), ((6, "Im", 1), (7, "Re", -1)), ((8, "Re", 1), (9, "Im", 1)), ((8, "Im", 1), (9, "Re", -1))),
    "-": (((6, "Re", 1), (7, "Im", -1)), ((6, "Im", 1), (7, "Re", 1)), ((8, "Re", 1), (9, "Im", -1)), ((8, "Im", 1), (9, "Re", 1))),
}
TRIPLET_REAL_X = tuple(H_SLICE.start + 2 * index for index in range(6))  # Re H_0..5 (chart = u indices)
TRIPLET_IMAG_X = tuple(index + 1 for index in TRIPLET_REAL_X)
TRIPLET_COLUMNS = TRIPLET_REAL_X + TRIPLET_IMAG_X
DOUBLET_COLUMNS = DOUBLET_REAL_X + DOUBLET_IMAG_X
PORTAL_PARAMETERS = tuple(f"{part}::{direction}" for direction in EXPECTED_H_LINEAR_DIRECTIONS for part in ("re", "im"))
PORTAL_LATTICE_DENOMINATOR = 6  # every H-column entry of the five directions' u-Hessian at r0 = 1 lies in (1/6) Z
COLOUR_BRACKET_RELATIVE = 1.0e-6  # exact inertia bracket of each colour radius: stable at (1 - 1e-6) rho^2, not at (1 + 1e-6)
# 16.16 bilinear entries of the up-type Yukawa structures Q u^c (u u^c for the neutral, d u^c for the charged doublet
# component) and L nu^c (nu nu^c, e nu^c); the down-type structures Q d^c and L e^c would appear as d-dc, dc-u, e-ec, ec-nu.
QUARK_UP_TYPE_PAIRS = ("d-uc", "u-uc")
LEPTON_UP_TYPE_PAIRS = ("e-nuc", "nu-nuc")
UP_TYPE_PAIRS = QUARK_UP_TYPE_PAIRS + LEPTON_UP_TYPE_PAIRS
OUTER_CERTIFICATE_TEXT = (
    "if H_HH(eps) - Q(c) >= 0 then for every triplet vector v and heavy vector z, (z^T B(c) v)^2 <= (z^T A z)(v^T H_HH v); "
    "with z = A^-1 B_d(phi_d) v (the response of direction d at the phase of c_d) this gives |c_d| m <= sqrt(m h) + "
    "4 pi sum_{d' != d} X_d', m = v^T G_d v, X_d' = sqrt(sum_{a, b in re, im} (v^T G[(d, a), (d', b)] v)^2), h = v^T "
    "H_HH(eps_max) v, v the top generalised eigenvector of (G_d, H_TT) and eps_max the largest O06 compensation that keeps "
    "the doublet light anywhere in the box (Minkowski bound over the directions); valid for any combination with the "
    "other directions in the |c| <= 4 pi box"
)
PORTAL_THETA_THRESHOLD = 1.0e-3
TAN_BETA_MODULI = 48  # |c| grid (0, 4 pi] of the float tan beta scan
TAN_BETA_PHASES = 72
# The candidate's committed one-loop RG solutions that fix the repository r0 = M_I/M_GUT values (fail closed).
EXPECTED_REPOSITORY_SCALES = (
    "anchor_content_local_chain",
    "candidate_PS_content_with_1HDM_below_M_I",
    "candidate_PS_content_with_2HDM_below_M_I",
    "candidate_content_with_1HDM_and_sub_M_I_remnants",
)
ANCHOR_SCALE_KEY = "anchor_content_local_chain"
EXPECTED_VECTORLIKE_RANK = 8

# ---------------------------------------------------------------------------
# Data inputs (float; transcribed, cited).  Every load-bearing test has a margin far above any last-digit revision.
# ---------------------------------------------------------------------------

DATA: dict[str, Any] = {
    "ckm_moduli": {
        "V_us": {"value": 0.2243, "sigma": 0.0008},
        "V_cb": {"value": 0.0411, "sigma": 0.0012},
        "V_ub": {"value": 0.00382, "sigma": 0.00020},
        "source": "PDG 2024 (S. Navas et al., Phys. Rev. D 110, 030001), CKM review, direct determinations",
    },
    "lattice_quark_mass_ratios": {
        "mc_over_ms": {"value": 11.768, "sigma": 0.034},
        "ms_over_mud": {"value": 27.23, "sigma": 0.10},
        "mu_over_md": {"value": 0.465, "sigma": 0.024},
        "mb_over_ms": {"value": 53.94, "sigma": 0.12},
        "source": "FLAG Review 2021 (Y. Aoki et al., Eur. Phys. J. C 82, 869 (2022), arXiv:2111.09849), N_f = 2+1+1 "
        "averages; QCD-scale-independent ratios",
    },
    "lepton_pole_masses_MeV": {
        "e": {"value": 0.51099895, "sigma": 1.5e-10},
        "mu": {"value": 105.6583755, "sigma": 2.3e-6},
        "tau": {"value": 1776.93, "sigma": 0.09},
        "source": "PDG 2024",
    },
    "running_masses_at_MZ_GeV": {
        "u": {"value": 1.27e-3, "sigma": 0.50e-3},
        "c": {"value": 0.619, "sigma": 0.084},
        "t": {"value": 171.7, "sigma": 3.0},
        "d": {"value": 2.90e-3, "sigma": 1.24e-3},
        "s": {"value": 0.055, "sigma": 0.016},
        "b": {"value": 2.89, "sigma": 0.09},
        "e": {"value": 0.486570161e-3, "sigma": 4.2e-14},
        "mu": {"value": 0.1027181359, "sigma": 9.2e-12},
        "tau": {"value": 1.74624, "sigma": 0.00020},
        "source": "Z.-z. Xing, H. Zhang, S. Zhou, Phys. Rev. D 77, 113016 (2008), MS-bar running masses at M_Z "
        "(asymmetric errors symmetrised to the larger side)",
    },
    "gauge_at_MZ": {
        "M_Z_GeV": 91.1876,
        "alpha_s": 0.1180,
        "alpha_em_inverse": 127.951,
        "sin2_theta_w": 0.23122,
        "source": "PDG 2024 (MS-bar at M_Z)",
    },
    "higgs_vev_GeV": 246.21965,
    "neutrino_oscillation": {
        "normal": {"s12sq": 0.303, "s23sq": 0.572, "s13sq": 0.02203, "delta_deg": 197.0, "dm21sq_eV2": 7.41e-5,
                   "dm3l_sq_eV2": 2.511e-3},
        "inverted": {"s12sq": 0.303, "s23sq": 0.578, "s13sq": 0.02219, "delta_deg": 286.0, "dm21sq_eV2": 7.41e-5,
                     "dm3l_sq_eV2": -2.498e-3},
        "sum_mnu_max_eV": 0.12,
        "source": "NuFIT 5.2 (2022) best fits without SK atmospheric data; sum m_nu < 0.12 eV (Planck 2018 + BAO)",
    },
    "conservative_theory_fraction": 0.10,
    "conservative_theory_note": (
        "every observable also gets a deliberately inflated 10% (relative, or in the log for ratios) uncertainty for "
        "running between M_Z and M_I, thresholds, scheme and transcription; the raw pulls use experimental errors only"
    ),
}
SCALE_BAND_DECADES_GEV = (1.0e9, 1.0e10, 1.0e11, 1.0e12, 1.0e13, 2.0e16)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
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


def _dig(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping) or key not in value:
            return None
        value = value[key]
    return value


# ---------------------------------------------------------------------------
# (A) The contract's fermion couplings, parsed from the SARAH model file, and the complete allowed set.
# ---------------------------------------------------------------------------

FIELD_RE = re.compile(r"(Scalar|Fermion)Fields\[\[(\d+)\]\]\s*=\s*\{([^{}]*)\};")
PHASE_RE = re.compile(r"Exp\[2\*Pi\*I\*(\d+)/(\d+)\]")
REAL_RE = re.compile(r"RealScalars\s*=\s*\{([^{}]*)\};")
CONJ_RE = re.compile(r"conj\[(\w+)\]")
SO10_CONJUGATE = {"1": "1", "10": "10", "45": "45", "120": "120", "210": "210", "126": "-126", "-126": "126",
                  "16": "-16", "-16": "16"}
# Bilinear content, machine-checked in the spinor section (tensor_product_certificate): 16x16 = 10 + 120 + 126,
# 16x16bar = 1 + 45 + 210, 16bar x 16bar = 10 + 120 + 126bar ("-126").
BILINEAR_CONTENT = {
    ("16", "16"): ("10", "120", "126"),
    ("-16", "16"): ("1", "45", "210"),
    ("-16", "-16"): ("10", "120", "-126"),
}
SINGLET_SCALARS = ("S", "Phi17")


def parse_model(text: str) -> dict[str, Any]:
    fields: dict[str, dict[str, Any]] = {}
    for kind, _index, body in FIELD_RE.findall(text):
        parts = [part.strip() for part in body.split(",")]
        if len(parts) != 6:
            raise ValueError(f"unexpected field row {body!r}")
        name, generations, component, rep, xcharge, phase = parts
        if phase == "1":
            z17 = 0
        else:
            match = PHASE_RE.fullmatch(phase)
            if match is None or int(match.group(2)) != 17:
                raise ValueError(f"unexpected Z17 phase {phase!r}")
            z17 = int(match.group(1))
        fields[name] = {
            "kind": kind.lower(),
            "generations": int(generations),
            "component": component,
            "so10": rep,
            "X": int(xcharge),
            "Z17": z17,
        }
    real_match = REAL_RE.search(text)
    real_components = {item.strip() for item in real_match.group(1).split(",")} if real_match else set()
    for row in fields.values():
        row["real"] = row["component"] in real_components

    def block(name: str) -> list[dict[str, Any]]:
        match = re.search(name + r"\s*=\s*-\((.*?)\);", text, re.S)
        if match is None:
            raise ValueError(f"{name} block not found")
        terms = []
        for line in match.group(1).splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            stripped = stripped.lstrip("+").strip()
            coefficient, product = stripped.split(None, 1)
            factors = []
            for factor in product.strip().split("."):
                conj = CONJ_RE.fullmatch(factor)
                factors.append({"field": conj.group(1) if conj else factor, "conjugate": bool(conj)})
            terms.append({"coefficient": coefficient, "text": product.strip(), "factors": factors})
        return terms

    return {"fields": fields, "LagHC": block("LagHC"), "LagNoHC": block("LagNoHC")}


def _factor_rep(fields: Mapping[str, Any], factor: Mapping[str, Any]) -> str:
    rep = str(fields[factor["field"]]["so10"])
    return SO10_CONJUGATE[rep] if factor["conjugate"] else rep


def _factor_charge(fields: Mapping[str, Any], factor: Mapping[str, Any], key: str) -> int:
    value = int(fields[factor["field"]][key])
    return -value if factor["conjugate"] else value


def _yukawa_so10_singlet(rep_a: str, rep_b: str, rep_s: str) -> bool | None:
    key = tuple(sorted((rep_a, rep_b)))
    content = BILINEAR_CONTENT.get(key)  # type: ignore[arg-type]
    if content is None:
        return None
    return SO10_CONJUGATE[rep_s] in content


def _label(factors: Sequence[Mapping[str, Any]]) -> str:
    return ".".join(f"conj[{item['field']}]" if item["conjugate"] else item["field"] for item in factors)


def _pattern_integers(seed: int = 20260925) -> Any:
    """Deterministic pseudo-random nonzero integers in [1, 997] (a fixed linear congruential sequence)."""
    state = seed
    while True:
        state = (1103515245 * state + 12345) % 2**31
        yield 1 + state % 997


def vectorlike_rank_certificate(fields: Mapping[str, Mapping[str, Any]], vectorlike: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Exact rank of the allowed 16bar x 16 mass pattern (one row per 16bar generation, one column per 16 generation)
    at deterministic integer couplings.  The rank at any point is a lower bound on the generic rank and the rank is at
    most the number of 16bar rows, so rank = n16bar certifies generic rank n16bar: every 16bar is massive and the light
    families are the (n16 - n16bar)-dimensional kernel for generic couplings."""
    bars = [name for name, row in fields.items() if row["kind"] == "fermion" and row["so10"] == "-16"]
    sixteens = [name for name, row in fields.items() if row["kind"] == "fermion" and row["so10"] == "16"]
    rows = [(name, index) for name in bars for index in range(int(fields[name]["generations"]))]
    columns = [(name, index) for name in sixteens for index in range(int(fields[name]["generations"]))]
    row_position = {label: position for position, label in enumerate(rows)}
    column_position = {label: position for position, label in enumerate(columns)}
    matrix = [[0] * len(columns) for _ in rows]
    integers = _pattern_integers()
    pairs = set()
    for coupling in vectorlike:
        first, second = coupling["fermions"]
        bar, sixteen = (first, second) if fields[first]["so10"] == "-16" else (second, first)
        pairs.add((bar, sixteen))
        for i in range(int(fields[bar]["generations"])):
            for j in range(int(fields[sixteen]["generations"])):
                matrix[row_position[(bar, i)]][column_position[(sixteen, j)]] += next(integers)
    exact = sympy.Matrix(matrix)
    rank = int(exact.rank())
    kernel = exact.nullspace()
    support = sorted({columns[index][0] for vector in kernel for index in range(len(columns)) if vector[index] != 0})
    return {
        "rows_16bar": [f"{name}[{index}]" for name, index in rows],
        "columns_16": [f"{name}[{index}]" for name, index in columns],
        "coupled_pairs": sorted(f"{bar}-{sixteen}" for bar, sixteen in pairs),
        "rank_at_integer_couplings": rank,
        "kernel_dimension": len(kernel),
        "kernel_support_fields": support,
        "statement": (
            "rank of the allowed 16bar x 16 pattern at deterministic integer couplings (exact, sympy); rank = number "
            "of 16bar rows certifies that generic rank, hence exactly n16 - n16bar light families for generic "
            "couplings; the rank at the physical couplings is assumed"
        ),
    }


def contract_section(model_text: str | None = None) -> dict[str, Any]:
    text = MODEL_FILE.read_text(encoding="utf-8") if model_text is None else model_text
    parsed = parse_model(text)
    fields = parsed["fields"]
    fermions = [name for name, row in fields.items() if row["kind"] == "fermion"]
    scalars = [name for name, row in fields.items() if row["kind"] == "scalar"]
    declared = []
    for term in parsed["LagHC"]:
        factors = term["factors"]
        x_sum = sum(_factor_charge(fields, item, "X") for item in factors)
        z_sum = sum(_factor_charge(fields, item, "Z17") for item in factors) % 17
        kinds = [fields[item["field"]]["kind"] for item in factors]
        row = {
            "term": f"{term['coefficient']} {term['text']}",
            "X_sum": x_sum,
            "Z17_sum_mod_17": z_sum,
            "fermions": kinds.count("fermion"),
            "scalars": kinds.count("scalar"),
        }
        if kinds.count("fermion") == 2 and kinds.count("scalar") == 1:
            fs = [item for item in factors if fields[item["field"]]["kind"] == "fermion"]
            ss = [item for item in factors if fields[item["field"]]["kind"] == "scalar"]
            row["so10_singlet"] = _yukawa_so10_singlet(_factor_rep(fields, fs[0]), _factor_rep(fields, fs[1]),
                                                       _factor_rep(fields, ss[0]))
        declared.append(row)

    # Every renormalizable fermion-fermion-(scalar) coupling allowed by SO(10) x U(1)_X (Z17 checked for consistency).
    scalar_options = []
    for name in scalars:
        scalar_options.append({"field": name, "conjugate": False})
        if not fields[name]["real"]:
            scalar_options.append({"field": name, "conjugate": True})
    allowed = []
    z17_consistent = True
    bare_masses = []
    for first, second in itertools.combinations_with_replacement(fermions, 2):
        fa = {"field": first, "conjugate": False}
        fb = {"field": second, "conjugate": False}
        if fields[first]["X"] + fields[second]["X"] == 0 and _yukawa_so10_singlet(
            fields[first]["so10"], fields[second]["so10"], "1"
        ):
            bare_masses.append(f"{first}.{second}")
        for option in scalar_options:
            singlet = _yukawa_so10_singlet(fields[first]["so10"], fields[second]["so10"], _factor_rep(fields, option))
            x_sum = fields[first]["X"] + fields[second]["X"] + _factor_charge(fields, option, "X")
            if not singlet or x_sum != 0:
                continue
            z_sum = (fields[first]["Z17"] + fields[second]["Z17"] + _factor_charge(fields, option, "Z17")) % 17
            z17_consistent &= z_sum == 0
            allowed.append(
                {
                    "coupling": _label([option, fa, fb]),
                    "fermions": [first, second],
                    "fermion_reps": [fields[first]["so10"], fields[second]["so10"]],
                    "scalar": _label([option]),
                    "scalar_rep": _factor_rep(fields, option),
                }
            )
    declared_labels = set()
    declared_yukawa_labels = set()
    for term in parsed["LagHC"]:
        names = tuple(sorted(_label([item]) for item in term["factors"]))
        declared_labels.add(names)
        kinds = [fields[item["field"]]["kind"] for item in term["factors"]]
        if kinds.count("fermion") == 2 and kinds.count("scalar") == 1:
            declared_yukawa_labels.add(names)
    allowed_labels = set()
    for row in allowed:
        label = tuple(sorted([row["scalar"], *row["fermions"]]))
        allowed_labels.add(label)
        row["declared"] = label in declared_labels

    def couplings(rep_pair: tuple[str, str], scalar: str | None = None) -> list[dict[str, Any]]:
        return [
            row
            for row in allowed
            if tuple(sorted(row["fermion_reps"])) == tuple(sorted(rep_pair)) and (scalar is None or row["scalar"] == scalar)
        ]

    x_one = sorted(name for name in fermions if fields[name]["so10"] == "16" and fields[name]["X"] == 1)
    h_yukawa = couplings(("16", "16"), "H10")
    hconj_yukawa = couplings(("16", "16"), "conj[H10]")
    delta_yukawa = couplings(("16", "16"), "Delta126bar")
    ff_all = couplings(("16", "16"))
    vectorlike = couplings(("16", "-16"))
    bar_bar = couplings(("-16", "-16"))
    n16 = sum(fields[name]["generations"] for name in fermions if fields[name]["so10"] == "16")
    n16bar = sum(fields[name]["generations"] for name in fermions if fields[name]["so10"] == "-16")
    sixteenbars = [name for name in fermions if fields[name]["so10"] == "-16"]
    rank_certificate = vectorlike_rank_certificate(fields, vectorlike)
    checks = {
        "model_fields_parsed": set(fermions) == {"F", "P", "R", "SpecS", "SpecB", "Q", "Pbar", "Qbar", "Rbar"}
        and set(scalars) == {"Phi210", "Delta126bar", "H10", "S", "Phi17"},
        "declared_terms_parsed": len(declared) == 11,
        "declared_terms_U1X_neutral": all(row["X_sum"] == 0 for row in declared),
        "declared_terms_Z17_neutral": all(row["Z17_sum_mod_17"] == 0 for row in declared),
        "declared_yukawas_SO10_singlets": all(row.get("so10_singlet", True) is True for row in declared),
        "declared_yukawas_subset_of_allowed": len(declared_yukawa_labels) == 10
        and declared_yukawa_labels <= allowed_labels,
        "allowed_set_Z17_consistent": bool(z17_consistent),
        "no_bare_vectorlike_mass": not bare_masses,
        "no_16_16_10H_conjugate_coupling": not hconj_yukawa,
        "H10_yukawas_only_on_X1_sixteens": bool(h_yukawa) and all(set(row["fermions"]) <= set(x_one) for row in h_yukawa),
        "Delta126bar_yukawas_only_on_X1_sixteens": bool(delta_yukawa)
        and all(set(row["fermions"]) <= set(x_one) for row in delta_yukawa),
        "sixteen_sixteen_scalars_only_H10_and_Delta126bar": {row["scalar"] for row in ff_all} == {"H10", "Delta126bar"},
        "no_120_scalar_in_contract": all(fields[name]["so10"] not in ("120", "-120") for name in scalars),
        "vectorlike_masses_only_SO10_singlet_vevs": bool(vectorlike)
        and all(row["scalar"].replace("conj[", "").rstrip("]") in SINGLET_SCALARS for row in vectorlike),
        "no_16_16bar_210_coupling": all("Phi210" not in row["scalar"] for row in vectorlike),
        "every_16bar_has_a_singlet_mass_partner": all(
            any(name in row["fermions"] for row in vectorlike) for name in sixteenbars
        ),
        "net_chirality_three_families": n16 - n16bar == 3,
        "Q_and_spectators_have_no_16_16_scalar_coupling": all(
            name not in row["fermions"] for row in ff_all for name in ("Q", "SpecS")
        ),
        "sixteenbar_pair_couplings_involve_only_16bars": all(
            all(fields[name]["so10"] == "-16" for name in row["fermions"]) for row in bar_bar
        ),
        "vectorlike_pattern_generic_rank_8": rank_certificate["rank_at_integer_couplings"] == EXPECTED_VECTORLIKE_RANK
        == n16bar
        and rank_certificate["kernel_dimension"] == n16 - n16bar == 3,
    }
    return {
        "model_file": "models/SO10Z17AxionV20.m",
        "model_text_sha256": hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "fields": fields,
        "declared_LagHC_terms": declared,
        "allowed_renormalizable_fermion_couplings": [
            {key: row[key] for key in ("coupling", "scalar_rep", "declared")} for row in allowed
        ],
        "allowed_count": len(allowed),
        "allowed_but_undeclared": sorted(row["coupling"] for row in allowed if not row["declared"]),
        "X1_sixteens": x_one,
        "H10_yukawas": sorted(row["coupling"] for row in h_yukawa),
        "Delta126bar_yukawas": sorted(row["coupling"] for row in delta_yukawa),
        "conj_H10_yukawas": sorted(row["coupling"] for row in hconj_yukawa),
        "vectorlike_mass_couplings": sorted(row["coupling"] for row in vectorlike),
        "sixteenbar_pair_couplings": sorted(row["coupling"] for row in bar_bar),
        "chirality": {"n16": n16, "n16bar": n16bar, "net": n16 - n16bar},
        "vectorlike_rank_certificate": rank_certificate,
        "light_state_lemma": (
            "All 16.16bar masses come from SO(10)-singlet vevs (Phi17, S), so the 3 light families are a 3-dimensional "
            "kernel U of the 16bar x 16 mass matrix (rank 8 for generic couplings, certified by the exact rank of the "
            "allowed pattern at deterministic integer couplings; assumed at the physical point: every 16bar massive, "
            "exactly three families), the same for every SM component of the 16.  16bar components are purely heavy, so 16bar.16bar couplings "
            "(e.g. Pbar.Rbar.conj[H10]) reach the light block only at O(v^3/M_V^2) (block elimination).  At dimension "
            "four the light Yukawa matrix to any 10_H component is Y = U^T Yhat U with Yhat the symmetric 16.16.10_H "
            "coupling on the X = 1 sixteens; no 16.16.conj[H10] coupling exists at all"
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# (B) The light doublet is pure 10_H: census H-degree classification and exact Hessian decoupling.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def census_rows() -> tuple[dict[str, Any], ...]:
    live = set(g2_audit.contract_selection()["direction_ids"])
    rows = []
    for orbit_index, orbit in enumerate(census.orbits(census.census(False))):
        counts = dict(zip(census.FIELD_ORDER, (int(value) for value in orbit["orbit_key"]), strict=True))
        base_key = tuple(counts[name] for name in ("P", "H", "Hb", "D", "Db"))
        base = ledger.BASE_FAMILIES[base_key]
        for basis_index, _label_ in enumerate(base["basis"]):
            direction_id = f"O{orbit_index + 1:02d}_B{basis_index + 1:02d}_{base['id']}"
            if direction_id not in live:
                continue
            self_conjugate = bool(orbit["self_conjugate"])
            rows.append(
                {
                    "direction_id": direction_id,
                    "representative": str(orbit["representative"]),
                    "counts": {key: value for key, value in counts.items() if value},
                    "H_degree": counts["H"] + counts["Hb"],
                    "Sigma_degree": counts["D"] + counts["Db"],
                    "parameters": [f"lambda::{direction_id}"] if self_conjugate else [f"re::{direction_id}", f"im::{direction_id}"],
                }
            )
    return tuple(rows)


def exact_hessian_at(r0: Fraction, overrides: Mapping[str, Fraction] | None = None) -> dict[str, Any]:
    """Exact H_u and grad_u at the witness for rational r0 (x0 = 1, kappa = -r0/4) from the binding units."""
    r0 = Fraction(r0)
    units = exact_hessian.exact_unit_matrices(r0, X0)
    coefficients = {key: Fraction(value) for key, value in candidate.candidate_coefficients(r0, X0, -r0 / 4).items()}
    for key, value in (overrides or {}).items():
        coefficients[key] = Fraction(value)
    coverage = exact_hessian.unit_coefficients(units, coefficients)
    hessian_terms = []
    gradient_terms = []
    for unit in units:
        scalar = coverage["unit_coefficients"][unit["name"]]
        numerator, denominator = unit["hessian"]
        hessian_terms.append((scalar / denominator, numerator))
        numerator, denominator = unit["gradient"]
        gradient_terms.append((scalar / denominator, numerator))
    hessian = exact_hessian.combine(hessian_terms, (TOTAL_DIM, TOTAL_DIM))
    gradient = exact_hessian.combine(gradient_terms, (TOTAL_DIM,))
    return {"hessian": hessian, "gradient": gradient, "coverage": coverage, "coefficients": coefficients}


def _expected_h_block(r0: Fraction) -> list[Fraction]:
    """u-coordinate H block diagonal: triplets (Re 2, Im 2 + 2 r0^2), doublets (Re 0, Im 2 r0^2)."""
    output = []
    for index in range(10):
        if index < 6:
            output += [Fraction(2), 2 + 2 * r0 * r0]
        else:
            output += [Fraction(0), 2 * r0 * r0]
    return output


def h_block_audit(r0: Fraction, overrides: Mapping[str, Fraction] | None = None) -> dict[str, Any]:
    data = exact_hessian_at(r0, overrides)
    numerator, denominator = data["hessian"]
    gnum, _gden = data["gradient"]
    rows = numerator[H_SLICE]
    outside = np.ones(TOTAL_DIM, dtype=bool)
    outside[H_SLICE] = False
    off_block_zero = not any(int(value) != 0 for value in rows[:, outside].flat)
    block = numerator[H_SLICE, H_SLICE]
    diagonal = [Fraction(int(block[i, i]), denominator) for i in range(block.shape[0])]
    off_diagonal_zero = all(int(block[i, j]) == 0 for i in range(block.shape[0]) for j in range(block.shape[1]) if i != j)
    coverage = data["coverage"]
    return {
        "r0": Fraction(r0),
        "coverage_complete": bool(coverage["coefficients_proportional_to_unit_weights"] and coverage["every_nonzero_parameter_covered"]),
        "gradient_zero": not any(int(value) != 0 for value in gnum.flat),
        "H_rows_vanish_outside_H_block": off_block_zero,
        "H_block_diagonal": off_diagonal_zero,
        "H_block_diagonal_u": diagonal,
        "H_block_matches_exact_formula": off_diagonal_zero and diagonal == _expected_h_block(Fraction(r0)),
        "Re_H_6_9_exact_null_vectors": all(
            not any(int(value) != 0 for value in numerator[:, index]) for index in DOUBLET_REAL_X
        ),
        "Im_H_6_9_mass_squared_chart": Fraction(r0) ** 2,
    }


def portal_section(
    coefficient_overrides: Mapping[str, Fraction] | None = None,
    r0_values: Sequence[Fraction] | None = None,
) -> dict[str, Any]:
    rows = census_rows()
    h_linear = sorted(row["direction_id"] for row in rows if row["H_degree"] == 1)
    h_linear_parameters = sorted(parameter for row in rows if row["H_degree"] == 1 for parameter in row["parameters"])
    h_quadratic_parameters = sorted(parameter for row in rows if row["H_degree"] == 2 for parameter in row["parameters"])
    benchmark = {key: Fraction(value) for key, value in candidate.candidate_coefficients().items()}
    for key, value in (coefficient_overrides or {}).items():
        benchmark[key] = Fraction(value)
    benchmark = {key: value for key, value in benchmark.items() if value != 0}
    r_symbol, x_symbol = sympy.symbols("r0 x0", positive=True)
    symbolic = candidate.candidate_coefficients(r_symbol, x_symbol, -r_symbol / 4)
    symbolic = {key: value for key, value in symbolic.items() if sympy.simplify(value) != 0}
    for key, value in (coefficient_overrides or {}).items():
        if value != 0:
            symbolic[key] = sympy.Rational(Fraction(value).numerator, Fraction(value).denominator)
    nonzero_h_quadratic = sorted(parameter for parameter in h_quadratic_parameters if parameter in benchmark)
    h_sigma_quadratic_zero = all(
        parameter not in benchmark
        for row in rows
        if row["direction_id"] in H_SIGMA_QUADRATIC_DIRECTIONS
        for parameter in row["parameters"]
    )
    r0_list = list(r0_values) if r0_values is not None else [*EXACT_R0_VALUES, physical_r0()]
    audits = [h_block_audit(r0, coefficient_overrides) for r0 in r0_list]
    benchmark_exact = exact_hessian.exact_hessian("benchmark")
    b_num, b_den = benchmark_exact["hessian"]
    mine = exact_hessian_at(R0, coefficient_overrides)
    m_num, m_den = mine["hessian"]
    reproduces_benchmark = (b_den == m_den) and all(
        int(a) == int(b) for a, b in zip(b_num.flat, m_num.flat)
    )
    h_degrees = Counter(int(row["H_degree"]) for row in rows)
    no_degree_three = set(h_degrees) <= {0, 1, 2, 4}
    linear_zero = not (set(h_linear_parameters) & set(benchmark)) and not (set(h_linear_parameters) & set(symbolic))
    checks = {
        "census_has_44_live_directions": len(rows) == 44,
        "H_linear_directions_are_exactly_O15_O28_O38_O45": tuple(h_linear) == EXPECTED_H_LINEAR_DIRECTIONS,
        "H_linear_parameters_are_the_candidate_portal_list_plus_im": set(h_linear_parameters)
        == set(candidate.H_LINEAR_PORTAL_IDS) | {key.replace("re::", "im::") for key in candidate.H_LINEAR_PORTAL_IDS},
        "H_linear_parameters_zero_in_benchmark": not (set(h_linear_parameters) & set(benchmark)),
        "H_linear_parameters_zero_for_all_r0_x0_symbolic": not (set(h_linear_parameters) & set(symbolic)),
        "no_H_degree_3_live_direction": bool(no_degree_three),
        "potential_even_in_H_on_the_witness": bool(no_degree_three and linear_zero),
        "nonzero_H_quadratic_parameters_are_O06_O12_O46": tuple(nonzero_h_quadratic) == EXPECTED_NONZERO_H_QUADRATIC,
        "H_Sigma_quadratic_O31_O35_zero_in_benchmark": h_sigma_quadratic_zero,
        "my_exact_hessian_reproduces_certified_benchmark_hessian": bool(reproduces_benchmark),
        "exact_gradient_zero_at_every_r0": all(audit["gradient_zero"] for audit in audits),
        "H_block_decoupled_at_every_r0": all(audit["H_rows_vanish_outside_H_block"] for audit in audits),
        "H_block_equals_exact_formula_at_every_r0": all(audit["H_block_matches_exact_formula"] for audit in audits),
        "Re_H_6_9_exact_null_vectors_at_every_r0": all(audit["Re_H_6_9_exact_null_vectors"] for audit in audits),
        "binding_unit_coverage_complete_at_every_r0": all(audit["coverage_complete"] for audit in audits),
    }
    return {
        "H_linear_directions": h_linear,
        "H_linear_parameters": h_linear_parameters,
        "nonzero_H_quadratic_parameters": nonzero_h_quadratic,
        "H_degree_table": [
            {key: row[key] for key in ("direction_id", "representative", "H_degree", "Sigma_degree")} for row in rows
        ],
        "H_degree_histogram": {str(key): value for key, value in sorted(h_degrees.items())},
        "lemma": (
            "At H = 0 a direction of H-degree d contributes to the H-(non-H) block of the Hessian only if d = 1 (d >= 2 "
            "leaves a factor of H after one H-derivative; d = 0 has no H-derivative).  The d = 1 directions are exactly "
            "O15, O28, O38, O45_B01, O45_B02 and all ten re/im parameters vanish in the benchmark map for every r0, x0; "
            "hence the H block decouples and the light doublet is span{Re H_6..9} with zero 126bar (15,2,2) and zero "
            "210 admixture."
        ),
        "induced_doublet_vev_lemma": (
            "The live H-degrees are {0, 1, 2, 4} (no H-degree 3) and the H-degree-1 parameters vanish, so V is even in H "
            "on the witness.  For any light-doublet value h, the SU(2)_L centre element z = -1 (unbroken at q0: it fixes "
            "p, sigma_std, S and Phi17) composed with P: H -> -H fixes q0 + h, since z acts as -1 on the (1,2,2) of the "
            "10_H and P undoes it.  The gradient at a fixed point of a linear symmetry lies in its fixed subspace, and "
            "P z acts as -1 on every heavy SU(2)_L doublet (126bar (15,2,2), 210 doublets) and on the H triplets.  So no "
            "heavy doublet gets an induced vev at any order in v at tree level; integer-isospin fields (e.g. the "
            "(10,3,1) Delta_L) are not covered by this argument and rest on O31/O35 = 0 (checked)."
        ),
        "exact_hessian_audits": audits,
        "r0_values": r0_list,
        "checks": checks,
    }


@lru_cache(maxsize=1)
def physical_r0() -> Fraction:
    return Fraction(candidate.hierarchy_anchor()["r0_physical"])


# ---------------------------------------------------------------------------
# (C) Exact spinor algebra: Clebsches of 16.16.10_H, 16.16.126bar and the (15,2,2).
# ---------------------------------------------------------------------------

GMatrix = tuple[np.ndarray, np.ndarray]
_SIGMA = {
    "1": (np.eye(2, dtype=np.int64), np.zeros((2, 2), dtype=np.int64)),
    "x": (np.array([[0, 1], [1, 0]], dtype=np.int64), np.zeros((2, 2), dtype=np.int64)),
    "y": (np.zeros((2, 2), dtype=np.int64), np.array([[0, -1], [1, 0]], dtype=np.int64)),
    "z": (np.array([[1, 0], [0, -1]], dtype=np.int64), np.zeros((2, 2), dtype=np.int64)),
}


def _g_kron(a: GMatrix, b: GMatrix) -> GMatrix:
    return (np.kron(a[0], b[0]) - np.kron(a[1], b[1]), np.kron(a[0], b[1]) + np.kron(a[1], b[0]))


def _g_mul(a: GMatrix, b: GMatrix) -> GMatrix:
    return (a[0] @ b[0] - a[1] @ b[1], a[0] @ b[1] + a[1] @ b[0])


def _g_add(a: GMatrix, b: GMatrix) -> GMatrix:
    return (a[0] + b[0], a[1] + b[1])


def _g_scale(a: GMatrix, coefficient: tuple[int, int]) -> GMatrix:
    re, im = coefficient
    return (re * a[0] - im * a[1], re * a[1] + im * a[0])


def _g_transpose(a: GMatrix) -> GMatrix:
    return (a[0].T.copy(), a[1].T.copy())


def _g_equal(a: GMatrix, b: GMatrix) -> bool:
    return bool(np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]))


def _g_zero(size: int = 32) -> GMatrix:
    return (np.zeros((size, size), dtype=np.int64), np.zeros((size, size), dtype=np.int64))


def _g_is_zero(a: GMatrix) -> bool:
    return not (np.any(a[0]) or np.any(a[1]))


def _g_restrict(a: GMatrix, rows: Sequence[int], columns: Sequence[int]) -> GMatrix:
    return (a[0][np.ix_(rows, columns)], a[1][np.ix_(rows, columns)])


@lru_cache(maxsize=1)
def gamma_matrices() -> tuple[GMatrix, ...]:
    """Gamma_{2k} = sz^(k) x sx x 1, Gamma_{2k+1} = sz^(k) x sy x 1 (slot k <-> Cartan plane (2k, 2k+1))."""
    output = []
    for slot in range(5):
        for kind in ("x", "y"):
            matrix: GMatrix = (np.ones((1, 1), dtype=np.int64), np.zeros((1, 1), dtype=np.int64))
            for position in range(5):
                factor = "z" if position < slot else (kind if position == slot else "1")
                matrix = _g_kron(matrix, _SIGMA[factor])
            output.append(matrix)
    return tuple(output)


def _identity() -> GMatrix:
    return (np.eye(32, dtype=np.int64), np.zeros((32, 32), dtype=np.int64))


def gamma_product(indices: Sequence[int]) -> GMatrix:
    matrix = _identity()
    gammas = gamma_matrices()
    for index in indices:
        matrix = _g_mul(matrix, gammas[index])
    return matrix


@lru_cache(maxsize=1)
def charge_conjugation() -> GMatrix:
    """C = Gamma_1 Gamma_3 Gamma_5 Gamma_7 Gamma_9 (the five sigma_y gammas)."""
    return gamma_product((1, 3, 5, 7, 9))


def spinor_weights(state: int) -> tuple[Fraction, ...]:
    bits = [(state >> (4 - slot)) & 1 for slot in range(5)]
    return tuple(Fraction(1, 2) if bit == 0 else Fraction(-1, 2) for bit in bits)


def _cartan_charge(state: int, generator: Sequence[int], factor: Fraction) -> Fraction:
    weights = spinor_weights(state)
    total = Fraction(0)
    for (first, second), coefficient in zip(hypercharge.GENERATORS, generator, strict=True):
        if not coefficient:
            continue
        if (first, second) not in hypercharge.CARTAN_PLANES:
            raise ValueError("charge generator is not in the Cartan subalgebra")
        total += coefficient * weights[hypercharge.CARTAN_PLANES.index((first, second))]
    return factor * total


FAMILY_Y_SPECTRUM = {
    Fraction(1, 6): 6,
    Fraction(-2, 3): 3,
    Fraction(1, 3): 3,
    Fraction(-1, 2): 2,
    Fraction(1): 1,
    Fraction(0): 1,
}
Y_TO_FIELD = {
    Fraction(1, 6): "Q",
    Fraction(-2, 3): "uc",
    Fraction(1, 3): "dc",
    Fraction(-1, 2): "L",
    Fraction(1): "ec",
    Fraction(0): "nuc",
}
DIRAC_PAIRS = (("u", "uc"), ("d", "dc"), ("e", "ec"), ("nu", "nuc"))


@lru_cache(maxsize=1)
def spinor_states() -> dict[str, Any]:
    states = {}
    for state in range(32):
        y = _cartan_charge(state, hypercharge.Y_STANDARD_INTEGER, Fraction(1, 6))
        t3l = _cartan_charge(state, hypercharge.T3L_INTEGER, Fraction(1, 2))
        q = _cartan_charge(state, hypercharge.Q_EM_STANDARD_INTEGER, Fraction(1, 3))
        bl = _cartan_charge(state, hypercharge.BL_INTEGER, Fraction(-2, 3))
        states[state] = {"weights": spinor_weights(state), "Y": y, "T3L": t3l, "Q": q, "B_minus_L": bl}
    odd = [state for state in range(32) if sum(1 for w in spinor_weights(state) if w < 0) % 2 == 1]
    even = [state for state in range(32) if state not in odd]
    spectrum_odd = Counter(states[state]["Y"] for state in odd)
    spectrum_even = Counter(states[state]["Y"] for state in even)
    names = {}
    for state in odd:
        row = states[state]
        base = Y_TO_FIELD.get(row["Y"], "?")
        if base == "Q":
            base = "u" if row["T3L"] > 0 else "d"
        elif base == "L":
            base = "nu" if row["T3L"] > 0 else "e"
        colour = "".join("+" if w > 0 else "-" for w in row["weights"][:3])
        names[state] = f"{base}[{colour}]"
    return {
        "states": states,
        "sixteen": odd,
        "sixteen_bar": even,
        "sixteen_is_family": dict(spectrum_odd) == FAMILY_Y_SPECTRUM,
        "sixteen_bar_is_conjugate_family": dict(spectrum_even) == {-key: value for key, value in FAMILY_Y_SPECTRUM.items()},
        "names": names,
        "Q_em_consistent": all(states[s]["Q"] == states[s]["T3L"] + states[s]["Y"] for s in range(32)),
    }


def _bilinear_16(matrix: GMatrix) -> GMatrix:
    sixteen = spinor_states()["sixteen"]
    return _g_restrict(matrix, sixteen, sixteen)


def _entries(matrix: GMatrix) -> list[tuple[str, str, tuple[int, int]]]:
    """Upper-triangular nonzero entries of a 16 x 16 Gaussian-integer bilinear, labelled by SM state names."""
    info = spinor_states()
    sixteen = info["sixteen"]
    rows, columns = np.nonzero((matrix[0] != 0) | (matrix[1] != 0))
    output = []
    for i, j in zip(rows.tolist(), columns.tolist()):
        if i <= j:
            output.append((info["names"][sixteen[i]], info["names"][sixteen[j]], (int(matrix[0][i, j]), int(matrix[1][i, j]))))
    return output


def _pair_table(matrix: GMatrix) -> dict[str, tuple[int, int]] | None:
    """{'u[--+]': value, ...} keyed by the particle of each Dirac pair; None if any entry is not a Dirac pair."""
    table: dict[str, tuple[int, int]] = {}
    for first, second, value in _entries(matrix):
        base_first, colour_first = first.split("[")[0], first[first.index("[") + 1 : -1]
        base_second, colour_second = second.split("[")[0], second[second.index("[") + 1 : -1]
        pair = None
        for particle, antiparticle in DIRAC_PAIRS:
            if {base_first, base_second} == {particle, antiparticle}:
                pair = particle
        if pair is None:
            return None
        particle_colour = colour_first if base_first == pair else colour_second
        other_colour = colour_second if base_first == pair else colour_first
        flipped = "".join("-" if c == "+" else "+" for c in particle_colour)
        if other_colour != flipped or f"{pair}[{particle_colour}]" in table:
            return None
        table[f"{pair}[{particle_colour}]"] = value
    return table


def _form_bilinear(form: Mapping[tuple[int, ...], tuple[int, int]]) -> GMatrix:
    conj = charge_conjugation()
    total = _g_zero()
    for indices, coefficient in form.items():
        ordered = tuple(sorted(indices))
        sign = _perm_sign(indices, ordered)
        total = _g_add(total, _g_scale(_g_mul(conj, gamma_product(ordered)), (sign * coefficient[0], sign * coefficient[1])))
    return _bilinear_16(total)


def _perm_sign(indices: Sequence[int], ordered: Sequence[int]) -> int:
    position = {value: index for index, value in enumerate(ordered)}
    permutation = [position[value] for value in indices]
    sign = 1
    for i in range(len(permutation)):
        for j in range(i + 1, len(permutation)):
            if permutation[i] > permutation[j]:
                sign = -sign
    return sign


GF_PRIME = 998244353  # = 119 * 2^23 + 1, prime, = 1 mod 4


def _gf_rank(vectors: Sequence[tuple[np.ndarray, np.ndarray]]) -> int:
    """Rank over GF(p) (i -> a square root of -1): a lower bound for the rank over Q(i)."""
    if not vectors:
        return 0
    p = GF_PRIME
    root = pow(3, (p - 1) // 4, p)
    if root * root % p != p - 1:
        raise ArithmeticError("no square root of -1 found")
    matrix = np.stack([(re.reshape(-1) % p + (im.reshape(-1) % p) * root) % p for re, im in vectors]).astype(np.int64)
    rank = 0
    rows, columns = matrix.shape
    for column in range(columns):
        pivot = None
        for row in range(rank, rows):
            if matrix[row, column] % p:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[[rank, pivot]] = matrix[[pivot, rank]]
        inverse = pow(int(matrix[rank, column]), p - 2, p)
        matrix[rank] = (matrix[rank] * inverse) % p
        factors = matrix[:, column].copy()
        factors[rank] = 0
        nonzero = np.nonzero(factors)[0]
        if nonzero.size:
            matrix[nonzero] = (matrix[nonzero] - (factors[nonzero, None] * matrix[rank][None, :]) % p) % p
        rank += 1
        if rank == rows:
            break
    return rank


@lru_cache(maxsize=1)
def tensor_product_certificate() -> dict[str, Any]:
    info = spinor_states()
    blocks = {
        "16x16": (info["sixteen"], info["sixteen"]),
        "16barx16bar": (info["sixteen_bar"], info["sixteen_bar"]),
        "16x16bar": (info["sixteen"], info["sixteen_bar"]),
    }
    conj = charge_conjugation()
    output: dict[str, Any] = {}
    all_ok = True
    for name, (rows, columns) in blocks.items():
        per_k = {}
        union = []
        for k in range(6):
            mats = [_g_restrict(_g_mul(conj, gamma_product(indices)), rows, columns) for indices in itertools.combinations(range(10), k)]
            nonzero = [m for m in mats if not _g_is_zero(m)]
            symmetric = all(_g_equal(_g_transpose(m), m) for m in nonzero) if name != "16x16bar" else None
            antisymmetric = all(_g_equal(_g_transpose(m), _g_scale(m, (-1, 0))) for m in nonzero) if name != "16x16bar" else None
            rank = _gf_rank(nonzero)
            per_k[k] = {"nonzero": len(nonzero), "rank_lower_bound_GFp": rank, "symmetric": symmetric, "antisymmetric": antisymmetric}
            union += nonzero
        per_k["union_rank_lower_bound_GFp"] = _gf_rank(union)
        output[name] = per_k
    # 5-form duality pairing on 16x16: C Gamma_I = lambda C Gamma_{I^c} with |lambda| = 1 (upper bound 126).
    sixteen = info["sixteen"]
    pairing_ok = True
    for indices in itertools.combinations(range(10), 5):
        if 0 not in indices:
            continue
        complement = tuple(sorted(set(range(10)) - set(indices)))
        left = _g_restrict(_g_mul(conj, gamma_product(indices)), sixteen, sixteen)
        right = _g_restrict(_g_mul(conj, gamma_product(complement)), sixteen, sixteen)
        if not any(_g_equal(left, _g_scale(right, unit)) for unit in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            pairing_ok = False
    ff = output["16x16"]
    fb = output["16x16bar"]
    all_ok = (
        [ff[k]["rank_lower_bound_GFp"] for k in range(6)] == [0, 10, 0, 120, 0, 126]
        and ff[1]["symmetric"] and ff[3]["antisymmetric"] and ff[5]["symmetric"]
        and ff["union_rank_lower_bound_GFp"] == 256
        and [fb[k]["rank_lower_bound_GFp"] for k in range(6)] == [1, 0, 45, 0, 210, 0]
        and fb["union_rank_lower_bound_GFp"] == 256
        and [output["16barx16bar"][k]["rank_lower_bound_GFp"] for k in range(6)] == [0, 10, 0, 120, 0, 126]
        and pairing_ok
    )
    return {
        "blocks": output,
        "five_form_duality_pairing_on_16": pairing_ok,
        "decomposition_proved": bool(all_ok),
        "statement": (
            "on the 16 x 16 block the k-form bilinears C Gamma_I vanish for even k and have ranks 10 (k=1, symmetric), "
            "120 (k=3, antisymmetric), 126 (k=5, symmetric; <= 126 by the exact duality pairing I <-> I^c, >= 126 over "
            "GF(p)) spanning all 256 = 16^2 matrices: 16x16 = 10_s + 120_a + 126_s; on 16 x 16bar the ranks are 1, 45, "
            "210 (k = 0, 2, 4), total 256: 16x16bar = 1 + 45 + 210.  GF(p) ranks are lower bounds for ranks over Q(i) "
            "and meet the trivial upper bounds C(10,k), so they are exact."
        ),
    }


def _complex_to_sympy(value: tuple[int, int]) -> sympy.Expr:
    return sympy.Integer(value[0]) + sympy.I * sympy.Integer(value[1])


A_SYMBOL, B_SYMBOL = sympy.symbols("a b", real=True)
DEFAULT_DOUBLET_VEV = {8: A_SYMBOL, 9: B_SYMBOL}  # v = a e8 + b e9 (Re H_8, Re H_9), a, b real


def spinor_section(doublet_vev: Mapping[int, sympy.Expr] | None = None) -> dict[str, Any]:
    vev = dict(DEFAULT_DOUBLET_VEV if doublet_vev is None else doublet_vev)
    gammas = gamma_matrices()
    identity = _identity()
    clifford = all(
        _g_equal(_g_add(_g_mul(gammas[a], gammas[b]), _g_mul(gammas[b], gammas[a])), _g_scale(identity, (2, 0)) if a == b else _g_zero())
        for a in range(10)
        for b in range(10)
    )
    cartan_diagonal = True
    for slot in range(5):
        twice_j = _g_scale(_g_mul(gammas[2 * slot], gammas[2 * slot + 1]), (0, -1))  # 2 J = -i Gamma Gamma
        if np.any(twice_j[1]) or np.count_nonzero(twice_j[0] - np.diag(np.diag(twice_j[0]))):
            cartan_diagonal = False
            continue
        if any(Fraction(int(twice_j[0][s, s]), 2) != spinor_weights(s)[slot] for s in range(32)):
            cartan_diagonal = False
    conj = charge_conjugation()
    invariant = all(
        _g_equal(_g_mul(conj, _g_mul(gammas[a], gammas[b])), _g_scale(_g_mul(_g_transpose(_g_mul(gammas[a], gammas[b])), conj), (-1, 0)))
        for a, b in itertools.combinations(range(10), 2)
    )
    info = spinor_states()
    tensor = tensor_product_certificate()
    ten = {a: _bilinear_16(_g_mul(conj, gammas[a])) for a in range(10)}
    ten_symmetric = all(_g_equal(_g_transpose(m), m) for m in ten.values())
    tables = {a: _pair_table(ten[a]) for a in (8, 9)}
    tables_ok = all(table is not None and len(table) == 8 for table in tables.values())
    clebsch: dict[str, sympy.Expr] = {}
    if tables_ok:
        for key in tables[8]:
            clebsch[key] = sympy.expand(
                sum(_complex_to_sympy(tables[a].get(key, (0, 0))) * vev.get(a, 0) for a in (8, 9))
            )
    moduli = {key: sympy.expand(value * sympy.conjugate(value)) for key, value in clebsch.items()}
    norm = sympy.expand(A_SYMBOL**2 + B_SYMBOL**2)

    def by_type(prefix: str) -> list[str]:
        return sorted(key for key in clebsch if key.split("[")[0] == prefix)

    ups, downs, electrons, neutrinos = by_type("u"), by_type("d"), by_type("e"), by_type("nu")
    all_moduli_equal = bool(clebsch) and all(sympy.simplify(value - moduli[ups[0]]) == 0 for value in moduli.values())
    moduli_are_norm = bool(clebsch) and all(sympy.simplify(value - norm) == 0 for value in moduli.values())

    def constant_ratio(first: str, second: str) -> sympy.Expr | None:
        numerator, denominator = clebsch[first], clebsch[second]
        if denominator == 0:
            return None
        ratio = sympy.simplify(numerator / denominator)
        if ratio.free_symbols:
            return None
        return ratio

    nu_over_u = [constant_ratio(u, neutrinos[0]) for u in ups] if clebsch else []
    e_over_d = [constant_ratio(electrons[0], d) for d in downs] if clebsch else []
    unimodular = all(r is not None and sympy.simplify(r * sympy.conjugate(r) - 1) == 0 for r in nu_over_u + e_over_d)
    # Hypercharge of the two neutral vector components: z5 = e8 + i e9 and its conjugate.
    y_matrix = hypercharge._matrix(hypercharge.Y_STANDARD_INTEGER)
    q_matrix = hypercharge._matrix(hypercharge.Q_EM_STANDARD_INTEGER)
    z5 = (np.eye(10, dtype=np.int64)[8], np.eye(10, dtype=np.int64)[9])  # (re, im) of e8 + i e9
    # Y = (1/6)(-i) Y_int: (-i)(Y_int z) = Y_int z_im - i Y_int z_re
    y_z5 = (y_matrix @ z5[1], -(y_matrix @ z5[0]))
    z5_hypercharge_plus_half = bool(np.array_equal(y_z5[0], 3 * z5[0]) and np.array_equal(y_z5[1], 3 * z5[1]))
    neutral_plane = bool(not np.any(q_matrix[:, 8]) and not np.any(q_matrix[:, 9]) and np.any(q_matrix[:, 6]) and np.any(q_matrix[:, 7]))
    v_up = sympy.expand((vev.get(8, 0) - sympy.I * vev.get(9, 0)) / 2)  # coefficient of z5 (Y = +1/2)
    v_down = sympy.expand((vev.get(8, 0) + sympy.I * vev.get(9, 0)) / 2)  # coefficient of conj(z5) (Y = -1/2)
    tan_beta_one = sympy.simplify(sympy.expand(v_up * sympy.conjugate(v_up) - v_down * sympy.conjugate(v_down))) == 0
    # 126bar vev: the repository's exact sigma_std form couples only nu^c nu^c; its conjugate not at all.
    sigma_form = candidate.sigma_std_exact_form()
    sigma_bilinear = _form_bilinear(sigma_form)
    sigma_entries = _entries(sigma_bilinear)
    sigma_conj_bilinear = _form_bilinear({key: (value[0], -value[1]) for key, value in sigma_form.items()})
    sigma_only_nuc = len(sigma_entries) == 1 and sigma_entries[0][0] == sigma_entries[0][1] and sigma_entries[0][0].startswith("nuc")
    # (15,2,2): omega6 ^ e_{679} (Hodge-dual to e8 in SO(4)) and omega6 ^ e_{678} (dual to e9), omega6 = e01+e23+e45.
    fifteen = {}
    fifteen_ok = True
    for vector_index, triple in ((8, (6, 7, 9)), (9, (6, 7, 8))):
        form = {pair + triple: (1, 0) for pair in ((0, 1), (2, 3), (4, 5))}
        table = _pair_table(_form_bilinear(form))
        ten_table = tables[vector_index] if tables_ok else None
        if table is None or ten_table is None or len(table) != 8:
            fifteen_ok = False
            continue
        ratios = {}
        for key, value in table.items():
            ratios[key] = sympy.simplify(_complex_to_sympy(value) / _complex_to_sympy(ten_table[key]))
        quark = {ratios[key] for key in ratios if key.split("[")[0] in ("u", "d")}
        lepton = {ratios[key] for key in ratios if key.split("[")[0] in ("e", "nu")}
        relative = sympy.simplify(next(iter(lepton)) / next(iter(quark))) if len(quark) == 1 and len(lepton) == 1 else None
        fifteen[f"dual_to_e{vector_index}"] = {
            "126_over_10_quarks": sorted(str(value) for value in quark),
            "126_over_10_leptons": sorted(str(value) for value in lepton),
            "lepton_over_quark_relative_clebsch": str(relative),
        }
        fifteen_ok &= relative == -3
    checks = {
        "clifford_relations_exact": bool(clifford),
        "cartan_generators_diagonal_with_spinor_weights": bool(cartan_diagonal),
        "charge_conjugation_intertwines_so10": bool(invariant),
        "sixteen_has_one_family_hypercharge_spectrum": bool(info["sixteen_is_family"]),
        "sixteen_bar_has_conjugate_spectrum": bool(info["sixteen_bar_is_conjugate_family"]),
        "Q_em_equals_T3L_plus_Y_on_spinor": bool(info["Q_em_consistent"]),
        "tensor_products_16x16_and_16x16bar_proved": bool(tensor["decomposition_proved"]),
        "ten_bilinear_symmetric_on_16": bool(ten_symmetric),
        "ten_bilinear_at_e8_e9_only_dirac_pairs": bool(tables_ok),
        "neutral_vev_plane_is_e8_e9": neutral_plane,
        "z5_has_hypercharge_plus_half": z5_hypercharge_plus_half,
        "equal_5_5bar_components_tan_beta_one": bool(tan_beta_one),
        "all_charged_and_dirac_clebsch_moduli_equal": bool(all_moduli_equal),
        "clebsch_moduli_equal_a2_plus_b2": bool(moduli_are_norm),
        "nu_over_u_and_e_over_d_constant_unimodular": bool(unimodular) and bool(nu_over_u) and bool(e_over_d),
        "sigma_std_couples_only_nuc_nuc": bool(sigma_only_nuc),
        "conjugate_sigma_std_decouples_from_16x16": _g_is_zero(sigma_conj_bilinear),
        "fifteen_two_two_relative_lepton_clebsch_minus_3": bool(fifteen_ok),
    }
    return {
        "convention": (
            "Gamma_{2k} = sz^(k) x sx x 1, Gamma_{2k+1} = sz^(k) x sy x 1; S_ab = (1/2) Gamma_a Gamma_b represents the "
            "repository generator L_ab (L_ab e_b = e_a); charges are (-i) x the repository integer generators; "
            "C = Gamma_1 Gamma_3 Gamma_5 Gamma_7 Gamma_9 satisfies C S_ab = -S_ab^T C; the 16 is the chirality with an "
            "odd number of weights -1/2"
        ),
        "vev": {str(key): str(value) for key, value in vev.items()},
        "vev_meaning": "v = a e8 + b e9 with a, b real: the chart's Re H_8, Re H_9 (H_k = (x_k + i y_k)/sqrt 2, y = 0)",
        "ten_clebsch_tables": {f"e{a}": {key: list(value) for key, value in (tables[a] or {}).items()} for a in (8, 9)},
        "clebsch_at_vev": {key: str(value) for key, value in clebsch.items()},
        "clebsch_moduli": {key: str(value) for key, value in moduli.items()},
        "v_up_coefficient_of_z5": str(v_up),
        "v_down_coefficient_of_conj_z5": str(v_down),
        "nu_over_u_ratios": [str(r) for r in nu_over_u],
        "e_over_d_ratios": [str(r) for r in e_over_d],
        "sigma_std_bilinear_entries": [[a, b, list(v)] for a, b, v in sigma_entries],
        "fifteen_two_two": fifteen,
        "tensor_products": tensor,
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# (D) The flavour structure theorem (exact, sympy) and its consequences.
# ---------------------------------------------------------------------------


def flavour_structure_section(spinor: Mapping[str, Any]) -> dict[str, Any]:
    symbols = {"a": A_SYMBOL, "b": B_SYMBOL}  # the real symbols of the vev (sympify would drop real=True)
    clebsch = {key: sympy.sympify(value, locals=symbols) for key, value in spinor["clebsch_at_vev"].items()}
    if not clebsch:
        return {"checks": {"clebsch_available": False}}
    pick = {prefix: sorted(key for key in clebsch if key.split("[")[0] == prefix)[0] for prefix in ("u", "d", "e", "nu")}
    c = {prefix: clebsch[key] for prefix, key in pick.items()}
    entries = {}
    y = sympy.zeros(3, 3)
    for i in range(3):
        for j in range(i, 3):
            re_part, im_part = sympy.symbols(f"p{i}{j} q{i}{j}", real=True)
            entries[(i, j)] = re_part + sympy.I * im_part
            y[i, j] = entries[(i, j)]
            y[j, i] = entries[(i, j)]

    def dagger(matrix: sympy.Matrix) -> sympy.Matrix:
        return matrix.T.applyfunc(sympy.conjugate)

    m_u, m_d, m_e, m_nu = (c[p] * y for p in ("u", "d", "e", "nu"))
    difference = (m_u * dagger(m_u) - m_d * dagger(m_d)).applyfunc(lambda value: sympy.simplify(sympy.expand(value)))
    commutator = (m_u * dagger(m_u) * m_d * dagger(m_d) - m_d * dagger(m_d) * m_u * dagger(m_u)).applyfunc(
        lambda value: sympy.expand(value)
    )
    ratio_e_d = sympy.simplify(c["e"] / c["d"])
    ratio_nu_u = sympy.simplify(c["nu"] / c["u"])
    me_vs_md = (m_e - ratio_e_d * m_d.T).applyfunc(lambda value: sympy.simplify(sympy.expand(value)))
    mnu_vs_mu = (m_nu - ratio_nu_u * m_u.T).applyfunc(lambda value: sympy.simplify(sympy.expand(value)))
    checks = {
        "clebsch_available": True,
        "MuMu_dagger_equals_MdMd_dagger": all(value == 0 for value in difference),
        "MuMu_dagger_commutes_with_MdMd_dagger": all(value == 0 for value in commutator),
        "Me_equals_constant_phase_times_Md_transpose": not ratio_e_d.free_symbols and all(value == 0 for value in me_vs_md),
        "MD_equals_constant_phase_times_Mu_transpose": not ratio_nu_u.free_symbols and all(value == 0 for value in mnu_vs_mu),
    }
    return {
        "setup": (
            "Y = U^T Yhat U is a generic complex symmetric 3 x 3 matrix (6 complex symbols); M_f = c_f(a, b) Y with the "
            "exact Clebsches of the spinor section at v = a e8 + b e9"
        ),
        "theorem": (
            "At renormalizable tree level (dimension four in the light-family EFT) on the witness branch: M_u M_u^dag = "
            "M_d M_d^dag identically, so the left rotations coincide and V_CKM is a diagonal phase matrix (= 1 after "
            "rephasing; the mass orderings coincide because the singular values are equal); m_u = m_d, m_c = m_s, "
            "m_t = m_b (tan beta = 1; for any tan beta the ratios m_t/m_b = m_c/m_s = m_u/m_d would still be equal); "
            "M_e = phase x M_d^T gives m_e = m_d, m_mu = m_s, m_tau = m_b; M_D = phase x M_u^T.  The 126bar enters "
            "only M_R = Y_126 v_R (nu^c nu^c).  SM running preserves the alignment: with Y_u = L D_u R^dag and Y_d = "
            "L D_d R^dag the one-loop betas are Y_f g_f(Y^dag Y) and keep a common L (to all orders the aligned SM has "
            "an exact U(1)^3 quark-family symmetry), so V_CKM = 1 at every scale below M_I."
        ),
        "ratio_e_over_d": str(ratio_e_d),
        "ratio_nu_over_u": str(ratio_nu_u),
        "predictions": {
            "V_CKM": "1 (diagonal phases)",
            "m_u/m_d = m_c/m_s = m_t/m_b": "1",
            "m_d/m_e = m_s/m_mu = m_b/m_tau": "1",
            "(m_c/m_u)/(m_s/m_d)": "1",
            "(m_t/m_c)/(m_b/m_s)": "1",
            "(m_s/m_d)/(m_mu/m_e)": "1",
            "(m_b/m_s)/(m_tau/m_mu)": "1",
            "M_D": "M_u (up to rephasing)",
            "M_R": "Y_126 v_R",
        },
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# (E) Data comparison (float diagnostics): one-loop SM running and pulls.
# ---------------------------------------------------------------------------

SIXTEEN_PI2 = 16.0 * math.pi**2


def _sm_one_loop(_t: float, y: np.ndarray) -> np.ndarray:
    g1, g2, g3 = y[0], y[1], y[2]
    yu, yd, ye = y[3:6], y[6:9], y[9:12]
    trace = 3.0 * float(np.sum(yu**2)) + 3.0 * float(np.sum(yd**2)) + float(np.sum(ye**2))
    gu = 17.0 / 20.0 * g1**2 + 9.0 / 4.0 * g2**2 + 8.0 * g3**2
    gd = 1.0 / 4.0 * g1**2 + 9.0 / 4.0 * g2**2 + 8.0 * g3**2
    ge = 9.0 / 4.0 * g1**2 + 9.0 / 4.0 * g2**2
    out = np.empty(12)
    out[0] = 41.0 / 10.0 * g1**3
    out[1] = -19.0 / 6.0 * g2**3
    out[2] = -7.0 * g3**3
    out[3:6] = yu * (1.5 * (yu**2 - yd**2) + trace - gu)
    out[6:9] = yd * (1.5 * (yd**2 - yu**2) + trace - gd)
    out[9:12] = ye * (1.5 * ye**2 + trace - ge)
    return out / SIXTEEN_PI2


def run_sm_masses(scales: Sequence[float], data: Mapping[str, Any] = DATA) -> dict[float, dict[str, float]]:
    """One-loop SM running from M_Z to every scale; an empty scale list returns {} (the callers' pinned-scale checks
    then fail closed instead of this function raising)."""
    if not scales:
        return {}
    gauge = data["gauge_at_MZ"]
    mz = gauge["M_Z_GeV"]
    e = math.sqrt(4.0 * math.pi / gauge["alpha_em_inverse"])
    sw = math.sqrt(gauge["sin2_theta_w"])
    cw = math.sqrt(1.0 - gauge["sin2_theta_w"])
    g1 = math.sqrt(5.0 / 3.0) * e / cw
    g2 = e / sw
    g3 = math.sqrt(4.0 * math.pi * gauge["alpha_s"])
    v = data["higgs_vev_GeV"]
    masses = data["running_masses_at_MZ_GeV"]
    order = ("u", "c", "t", "d", "s", "b", "e", "mu", "tau")
    y0 = np.array([g1, g2, g3] + [math.sqrt(2.0) * masses[name]["value"] / v for name in order])
    t_values = sorted({math.log(scale) for scale in scales})
    solution = solve_ivp(_sm_one_loop, (math.log(mz), t_values[-1]), y0, method="DOP853", rtol=1.0e-11, atol=1.0e-14,
                         dense_output=True)
    output = {}
    for scale in scales:
        state = solution.sol(math.log(scale))
        output[scale] = {name: float(state[3 + index]) * v / math.sqrt(2.0) for index, name in enumerate(order)}
        output[scale]["g1"], output[scale]["g2"], output[scale]["g3"] = (float(state[0]), float(state[1]), float(state[2]))
    return output


def _rel(entry: Mapping[str, float]) -> float:
    return float(entry["sigma"]) / float(entry["value"])


def _pulls_zero(value: float, sigma: float, theory: float) -> tuple[float, float]:
    return value / sigma, value / math.hypot(sigma, theory * value)


def _pulls_ratio(value: float, sigma_ln: float, theory: float) -> tuple[float, float]:
    return abs(math.log(value)) / sigma_ln, abs(math.log(value)) / math.hypot(sigma_ln, theory)


def repository_scales(report: Mapping[str, Any] | None = None) -> dict[str, dict[str, float]]:
    """(M_I, M_GUT) of the candidate's committed one-loop RG solutions, duplicates (same pair) dropped.  Every key of
    EXPECTED_REPOSITORY_SCALES must be present (checked by the callers: O28_fix.repository_scales_present,
    data.repository_M_I_rows_present); ``report`` replaces the committed candidate JSON for mutation tests only."""
    if report is None:
        report = json.loads(CANDIDATE_JSON.read_text(encoding="utf-8"))
    solutions = _dig(report, "rg_anchor_consistency", "one_loop_solutions") or {}
    if not isinstance(solutions, Mapping):
        return {}
    output: dict[str, dict[str, float]] = {}
    seen = set()
    for key, row in sorted(solutions.items()):
        if isinstance(row, Mapping) and "M_I_GeV" in row and "M_GUT_GeV" in row:
            pair = (float(row["M_I_GeV"]), float(row["M_GUT_GeV"]))
            if pair in seen:
                continue
            seen.add(pair)
            output[key] = {"M_I_GeV": pair[0], "M_GUT_GeV": pair[1]}
    return output


def scale_band(decades: Sequence[float], scales: Mapping[str, Mapping[str, float]] | None = None) -> dict[str, float]:
    band = {f"{scale:.0e} GeV": float(scale) for scale in decades}
    for key, row in (repository_scales() if scales is None else scales).items():
        band[f"M_I[{key}]"] = row["M_I_GeV"]
    return dict(sorted(band.items(), key=lambda item: item[1]))


def repository_scales_complete(scales: Mapping[str, Any]) -> bool:
    return set(scales) == set(EXPECTED_REPOSITORY_SCALES)


def data_section(data: Mapping[str, Any] = DATA, scales: Mapping[str, Mapping[str, float]] | None = None) -> dict[str, Any]:
    """``scales`` replaces the repository (M_I, M_GUT) rows for mutation tests only."""
    scales = repository_scales() if scales is None else scales
    theory = float(data["conservative_theory_fraction"])
    ckm = data["ckm_moduli"]
    lat = data["lattice_quark_mass_ratios"]
    lep = data["lepton_pole_masses_MeV"]
    tests = []

    def add(name: str, prediction: str, value: float, raw: float, conservative: float, load_bearing: bool, scale: str,
            inputs: str) -> None:
        tests.append({"test": name, "prediction": prediction, "data_value": value, "pull_raw_sigma": raw,
                      "pull_conservative_sigma": conservative, "load_bearing": load_bearing, "scale": scale, "inputs": inputs})

    for key in ("V_us", "V_cb", "V_ub"):
        raw, cons = _pulls_zero(ckm[key]["value"], ckm[key]["sigma"], theory)
        add(f"|{key}|", "0 (V_CKM = 1, preserved by SM running)", ckm[key]["value"], raw, cons, True, "any", "PDG 2024")
    r = lat["mu_over_md"]["value"]
    r12 = lat["mc_over_ms"]["value"] / r
    sigma12 = math.hypot(_rel(lat["mc_over_ms"]), _rel(lat["mu_over_md"]))
    raw, cons = _pulls_ratio(r12, sigma12, theory)
    add("(m_c/m_u)/(m_s/m_d) = (m_c/m_s)(m_d/m_u)", "1", r12, raw, cons, True, "RG-invariant (same-type ratios)", "FLAG 2021")
    ms_md = lat["ms_over_mud"]["value"] * (1.0 + r) / 2.0
    sigma_msmd = math.hypot(_rel(lat["ms_over_mud"]), lat["mu_over_md"]["sigma"] / (1.0 + r))
    mmu_me = lep["mu"]["value"] / lep["e"]["value"]
    gj12 = ms_md / mmu_me
    sigma_gj12 = math.hypot(sigma_msmd, 0.03)  # 3%: pole vs running lepton ratio (QED), declared
    raw, cons = _pulls_ratio(gj12, sigma_gj12, theory)
    add("(m_s/m_d)/(m_mu/m_e)", "1", gj12, raw, cons, True, "RG-invariant (same-type ratios)",
        "FLAG 2021 + PDG 2024 (3% pole-vs-running allowance)")

    band = scale_band(SCALE_BAND_DECADES_GEV, scales)
    running = run_sm_masses(sorted(set(band.values())), data)
    mz_masses = data["running_masses_at_MZ_GeV"]
    per_scale = {}
    for label, scale in sorted(band.items(), key=lambda item: item[1]):
        m = running[scale]
        f_bs = (m["b"] / m["s"]) / (mz_masses["b"]["value"] / mz_masses["s"]["value"])
        mb_ms = lat["mb_over_ms"]["value"] * f_bs
        tc = m["t"] / m["c"]
        r23 = tc / mb_ms
        sigma23 = math.hypot(_rel(mz_masses["t"]), _rel(mz_masses["c"]), _rel(lat["mb_over_ms"]))
        raw23, cons23 = _pulls_ratio(r23, sigma23, theory)
        gj23 = mb_ms / (m["tau"] / m["mu"])
        sigma_gj23 = math.hypot(_rel(lat["mb_over_ms"]), 0.03)
        raw_gj23, cons_gj23 = _pulls_ratio(gj23, sigma_gj23, theory)
        tb = m["t"] / m["b"]
        sigma_tb = math.hypot(_rel(mz_masses["t"]), _rel(mz_masses["b"]))
        raw_tb, cons_tb = _pulls_ratio(tb, sigma_tb, theory)
        btau = m["b"] / m["tau"]
        raw_bt, cons_bt = _pulls_ratio(btau, _rel(mz_masses["b"]), theory)
        per_scale[label] = {
            "mu_GeV": scale,
            "running_masses_GeV": {key: m[key] for key in ("u", "c", "t", "d", "s", "b", "e", "mu", "tau")},
            "(m_t/m_c)/(m_b/m_s)": {"value": r23, "pull_raw_sigma": raw23, "pull_conservative_sigma": cons23, "load_bearing": True},
            "(m_b/m_s)/(m_tau/m_mu)": {"value": gj23, "pull_raw_sigma": raw_gj23, "pull_conservative_sigma": cons_gj23, "load_bearing": True},
            "m_t/m_b (tan beta = 1)": {"value": tb, "pull_raw_sigma": raw_tb, "pull_conservative_sigma": cons_tb, "load_bearing": False},
            "m_b/m_tau": {"value": btau, "pull_raw_sigma": raw_bt, "pull_conservative_sigma": cons_bt, "load_bearing": False},
        }
    load_raw = [row["pull_raw_sigma"] for row in tests if row["load_bearing"]]
    load_cons = [row["pull_conservative_sigma"] for row in tests if row["load_bearing"]]
    for row in per_scale.values():
        for key, value in row.items():
            if isinstance(value, Mapping) and value.get("load_bearing"):
                load_raw.append(value["pull_raw_sigma"])
                load_cons.append(value["pull_conservative_sigma"])
    tb_min = min(row["m_t/m_b (tan beta = 1)"]["value"] for row in per_scale.values())
    checks = {
        "every_load_bearing_test_excluded_raw_at_threshold": min(load_raw) >= NOGO_PULL_THRESHOLD,
        "every_load_bearing_test_excluded_conservative_at_threshold": min(load_cons) >= NOGO_PULL_THRESHOLD,
        "m_t_over_m_b_far_from_one_across_band": tb_min > 30.0,
        "running_reproduces_published_high_scale_top_mass_roughly": 60.0 < running[2.0e16]["t"] < 90.0,
        "repository_M_I_rows_present": repository_scales_complete(scales)
        and {f"M_I[{key}]" for key in EXPECTED_REPOSITORY_SCALES} <= set(band),
    }
    return {
        "inputs": data,
        "method": (
            "Load-bearing tests are tan-beta-independent: CKM moduli (prediction 0 at every scale), the RG-invariant "
            "same-type light ratios, and (m_t/m_c)/(m_b/m_s), (m_b/m_s)/(m_tau/m_mu) evaluated with one-loop SM running "
            "(GUT-normalised g1, diagonal Yukawas, no CKM in the betas) from M_Z to each scale of the band; the lattice "
            "m_b/m_s is carried with the running factor of y_b/y_s.  Pulls: |ln R|/sigma_ln for ratios predicted to be 1, "
            "x/sigma for moduli predicted to be 0; 'conservative' adds the declared 10% theory term.  Float diagnostics."
        ),
        "scale_band": band,
        "tests_scale_free": tests,
        "tests_per_scale": per_scale,
        "minimum_load_bearing_pull_raw_sigma": min(load_raw),
        "minimum_load_bearing_pull_conservative_sigma": min(load_cons),
        "threshold_sigma": NOGO_PULL_THRESHOLD,
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# (F) O28 alone: the largest direct 10_H-(15,2,2) portal (exact lattice binding, exact first-order admixture, saddle).
# ---------------------------------------------------------------------------


@lru_cache(maxsize=2)
def portal_compiler_rows(r0: Fraction) -> dict[str, np.ndarray]:
    """The live compiler's Hessian (u coordinates) and gradient of every re::/im:: parameter of the five H-linear
    directions at the witness state for this r0 (float64; one compiler pass for all five directions)."""
    state = candidate.candidate_state(r0)
    directions = set(EXPECTED_H_LINEAR_DIRECTIONS)
    rows = target.parameter_rows(state, include=lambda direction: direction.direction_id in directions)
    output = {}
    for direction in EXPECTED_H_LINEAR_DIRECTIONS:
        for parameter in (f"re::{direction}", f"im::{direction}"):
            hessian = np.asarray(rows[parameter].hessian, dtype=float)
            output[parameter] = exact_hessian.chart_to_u_hessian(0.5 * (hessian + hessian.T))
            output[parameter + "::gradient"] = np.asarray(rows[parameter].gradient, dtype=float)
    return output


def o28_compiler_rows(r0: Fraction) -> dict[str, np.ndarray]:
    rows = portal_compiler_rows(r0)
    return {key: rows[key] for parameter in O28_IDS for key in (parameter, parameter + "::gradient")}


def o28_lattice_binding() -> dict[str, Any]:
    """Round the compiler's O28 u-Hessian at r0 = 1 to integers (half-lattice margin) and re-check at r0 = 1/5."""
    base = o28_compiler_rows(Fraction(1))
    fifth = o28_compiler_rows(Fraction(1, 5))
    output: dict[str, Any] = {"patterns": {}}
    ok = True
    for parameter in O28_IDS:
        rounded = np.rint(base[parameter]).astype(np.int64)
        residual = float(np.max(np.abs(base[parameter] - rounded)))
        scaled = fifth[parameter] * 25.0
        residual_fifth = float(np.max(np.abs(scaled - rounded)))
        support = rounded[H_SLICE][:, SIGMA_SLICE]
        outside = rounded.copy()
        outside[H_SLICE, SIGMA_SLICE] = 0
        outside[SIGMA_SLICE, H_SLICE] = 0
        entries = sorted({int(value) for value in support.flat if value})
        row = {
            "max_rounding_residual_r0_1": residual,
            "max_residual_r0_one_fifth_times_25": residual_fifth,
            "nonzero_only_in_H_Sigma_block": not np.any(outside),
            "H_Sigma_nonzero_entries": entries,
            "H_Sigma_nonzero_count": int(np.count_nonzero(support)),
            "gradient_max_abs_r0_1": float(np.max(np.abs(base[parameter + "::gradient"]))),
            "gradient_max_abs_r0_one_fifth": float(np.max(np.abs(fifth[parameter + "::gradient"]))),
        }
        ok &= residual < 1.0e-9 and residual_fifth < 1.0e-9 and row["nonzero_only_in_H_Sigma_block"]
        ok &= entries == [-O28_LATTICE_ENTRY, O28_LATTICE_ENTRY]
        ok &= row["gradient_max_abs_r0_1"] == 0.0 and row["gradient_max_abs_r0_one_fifth"] == 0.0
        output["patterns"][parameter] = row
        output.setdefault("_integer", {})[parameter] = rounded
    output["bound"] = bool(ok)
    output["homogeneity"] = (
        "O28 = H^dag Sigma^2 Sigma^dag is linear in H^dag and cubic in Sigma, so at H = 0, Sigma = r0 sigma_std its "
        "Hessian is the H-Sigma block only and scales exactly as r0^2 (two vev factors); its H-gradient is the 10 "
        "component of the SM singlet Sigma^2 Sigma^dag, which vanishes (the 10 has no SM singlet)"
    )
    return output


def _component(numerator: np.ndarray, seeds: Sequence[int]) -> list[int]:
    adjacency: list[set[int]] = [set() for _ in range(TOTAL_DIM)]
    rows, columns = np.nonzero(numerator != 0)
    for row, column in zip(rows.tolist(), columns.tolist()):
        if row != column:
            adjacency[row].add(column)
    seen = set(seeds)
    queue = deque(seeds)
    while queue:
        current = queue.popleft()
        for neighbour in adjacency[current]:
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return sorted(seen)


def _solve(matrix: list[list[Fraction]], vector: list[Fraction]) -> tuple[list[Fraction], int]:
    size = len(matrix)
    work = [row[:] + [vector[index]] for index, row in enumerate(matrix)]
    pivots = []
    rank = 0
    for column in range(size):
        pivot = next((row for row in range(rank, size) if work[row][column] != 0), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = 1 / work[rank][column]
        work[rank] = [value * inverse for value in work[rank]]
        for row in range(size):
            if row != rank and work[row][column] != 0:
                factor = work[row][column]
                work[row] = [a - factor * b for a, b in zip(work[row], work[rank])]
        pivots.append(column)
        rank += 1
    solution = [Fraction(0)] * size
    for row, column in enumerate(pivots):
        solution[column] = work[row][size]
    return solution, rank


@lru_cache(maxsize=16)
def base_hessian(r0: Fraction) -> tuple[np.ndarray, int]:
    """The exact witness Hessian (u coordinates) at r0, x0 = 1, kappa = -r0/4 (cached; shared by sections F and F')."""
    return exact_hessian_at(Fraction(r0))["hessian"]


@lru_cache(maxsize=16)
def base_adjacency(r0: Fraction) -> tuple[tuple[int, ...], ...]:
    numerator, _ = base_hessian(r0)
    adjacency: list[set[int]] = [set() for _ in range(TOTAL_DIM)]
    rows, columns = np.nonzero(numerator != 0)
    for row, column in zip(rows.tolist(), columns.tolist()):
        if row != column:
            adjacency[row].add(column)
    return tuple(tuple(sorted(neighbours)) for neighbours in adjacency)


def _component_from(adjacency: Sequence[Sequence[int]], seeds: Sequence[int]) -> list[int]:
    seen = set(seeds)
    queue = deque(seeds)
    while queue:
        current = queue.popleft()
        for neighbour in adjacency[current]:
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append(neighbour)
    return sorted(seen)


def o28_first_order(r0: Fraction, lattice: Mapping[str, np.ndarray]) -> dict[str, Any]:
    """Exact first-order (15,2,2) and 210 admixture of the light doublet Re H_k under c * O28 (per unit c)."""
    r0 = Fraction(r0)
    numerator, denominator = base_hessian(r0)
    squared = exact_hessian.congruence_scale_squared()
    per_parameter = {}
    ys: dict[str, dict[int, list[Fraction]]] = {}
    components: dict[tuple[str, int], list[int]] = {}
    positive_definite = True
    solvable = True
    for parameter in O28_IDS:
        pattern = lattice[parameter]
        values = []
        ys[parameter] = {}
        for column_index in DOUBLET_REAL_X + DOUBLET_IMAG_X:
            w_full = [Fraction(int(value)) * r0 * r0 for value in pattern[column_index]]
            support = [index for index in range(TOTAL_DIM) if w_full[index] != 0]
            component = _component_from(base_adjacency(r0), support)
            components[(parameter, column_index)] = component
            block = [[Fraction(int(numerator[a, b]), denominator) for b in component] for a in component]
            inertia = exact_hessian.exact_inertia(block, component)
            positive_definite &= inertia["positive"] == len(component) and inertia["negative"] == 0 and inertia["zero"] == 0
            w = [w_full[a] for a in component]
            y, rank = _solve(block, w)
            solvable &= rank == len(component)
            ys[parameter][column_index] = [Fraction(0)] * TOTAL_DIM
            for position, index in enumerate(component):
                ys[parameter][column_index][index] = y[position]
            if column_index in DOUBLET_REAL_X:
                theta_sigma2 = sum(squared[a] * y[p] ** 2 for p, a in enumerate(component) if SIGMA_SLICE.start <= a < SIGMA_SLICE.stop) / 2
                theta_phi2 = sum(squared[a] * y[p] ** 2 for p, a in enumerate(component) if PHI_SLICE.start <= a < PHI_SLICE.stop) / 2
                other = sum(1 for a in component if not (SIGMA_SLICE.start <= a < SIGMA_SLICE.stop or PHI_SLICE.start <= a < PHI_SLICE.stop))
                shift = -sum(w[p] * y[p] for p in range(len(component))) / 2
                values.append({"theta_sigma2": theta_sigma2, "theta_phi2": theta_phi2, "shift": shift, "other": other,
                               "component_size": len(component)})
        per_parameter[parameter] = values
    # Exact Schur complement of the heavy block on the 8 H-doublet u coordinates (Re H_6..9, Im H_6..9), for the
    # coupling c_re re::O28 + c_im im::O28: Hess_eff = M0 - (c_re, c_im) G (c_re, c_im) with the 16 x 16 Gram matrix
    # G[(p, i), (q, j)] = w_{p,i} . A^-1 w_{q,j} (exact), M0 = diag(0^4, (2 r0^2)^4).
    indices = DOUBLET_REAL_X + DOUBLET_IMAG_X
    labels = [(parameter, index) for parameter in O28_IDS for index in indices]
    sparse_w = {
        (parameter, index): [(k, Fraction(int(lattice[parameter][index][k])) * r0 * r0) for k in np.nonzero(lattice[parameter][index])[0].tolist()]
        for parameter, index in labels
    }
    gram = [[sum(value * ys[q][j][k] for k, value in sparse_w[(p, i)]) for (q, j) in labels] for (p, i) in labels]
    gram_symmetric = all(gram[a][b] == gram[b][a] for a in range(16) for b in range(16))
    second_order = {}
    for offset, parameter in enumerate(O28_IDS):
        block = [row[8 * offset : 8 * offset + 8] for row in gram[8 * offset : 8 * offset + 8]]
        second_order[parameter] = {
            "Re_Re_diagonal_over_r0_4": [block[a][a] / r0**4 for a in range(4)],
            "Re_Im_block_zero": all(block[a][b] == 0 for a in range(4) for b in range(4, 8)),
            "Re_Re_offdiagonal_zero": all(block[a][b] == 0 for a in range(4) for b in range(4) if a != b),
        }
    cross = []
    for index, column_index in enumerate(DOUBLET_REAL_X):
        y_re = ys[O28_IDS[0]][column_index]
        y_im = ys[O28_IDS[1]][column_index]
        cross.append(sum(squared[k] * y_re[k] * y_im[k] for k in range(TOTAL_DIM)) / 2)
    first = per_parameter[O28_IDS[0]][0]
    uniform = all(
        row["theta_sigma2"] == first["theta_sigma2"] and row["theta_phi2"] == first["theta_phi2"] and row["shift"] == first["shift"]
        for rows in per_parameter.values()
        for row in rows
    )
    return {
        "r0": r0,
        "heavy_components_positive_definite": bool(positive_definite),
        "heavy_systems_nonsingular": bool(solvable),
        "same_for_Re_H_6_9_and_re_im": bool(uniform),
        "re_im_cross_term_zero": all(value == 0 for value in cross),
        "theta_sigma_squared_over_c2_r0_4": first["theta_sigma2"] / r0**4,
        "theta_phi_squared_over_c2_r0_4": first["theta_phi2"] / r0**4,
        "light_mass_shift_over_c2_r0_4": first["shift"] / r0**4,
        "only_sigma_and_phi_in_heavy_component": first["other"] == 0,
        "component_size": first["component_size"],
        "second_order_H_doublet_block": second_order,
        "second_order_gram_symmetric": gram_symmetric,
        "_gram_over_r0_4": np.array([[float(value / r0**4) for value in row] for row in gram]),
        "_ys": ys,
        "_components": components,
    }


def tan_beta_under_o28(r0: Fraction, gram_over_r0_4: np.ndarray, modulus: float, n_phases: int = 72) -> dict[str, Any]:
    """Float: tan beta = |5 part|/|5bar part| of the lightest H-doublet eigenvector of M0 - |c|^2 S(phi) (retuned
    O06 shifts all H eigenvalues equally and does not move eigenvectors), maximised over the phase of c."""
    r0f = float(r0)
    m0 = np.diag([0.0] * 4 + [2.0 * r0f**2] * 4)
    s_rr, s_ii = gram_over_r0_4[:8, :8], gram_over_r0_4[8:, 8:]
    s_ri = gram_over_r0_4[:8, 8:] + gram_over_r0_4[8:, :8]
    worst = 1.0
    for phase in np.linspace(0.0, math.pi, n_phases, endpoint=False):
        s = math.cos(phase) ** 2 * s_rr + math.sin(phase) ** 2 * s_ii + math.sin(phase) * math.cos(phase) * s_ri
        values, vectors = np.linalg.eigh(m0 - modulus**2 * r0f**4 * s)
        for column in range(4):
            vector = vectors[:, column]
            h = vector[:4] + 1j * vector[4:]  # H_6..9 = Re + i Im (u coordinates)
            five = abs(h[0] - 1j * h[1]) ** 2 + abs(h[2] - 1j * h[3]) ** 2  # <z4, h>, <z5, h>: Y = +1/2
            five_bar = abs(h[0] + 1j * h[1]) ** 2 + abs(h[2] + 1j * h[3]) ** 2
            ratio = math.sqrt(five / five_bar)
            worst = max(worst, ratio, 1.0 / ratio)
    return {"tan_beta_max_over_phase": worst, "phases_scanned": n_phases, "modulus_c": modulus}


def o28_closed_form(lattice: Mapping[str, np.ndarray]) -> dict[str, Any]:
    """R(r) = theta^2/(c^2 r^4) as an exact rational function: entries of the heavy block are polynomials of degree
    <= 2 in r0 (binding-unit scalars rho^2, rho, 1 with rho = r0/4 and couplings of degree <= 2), fixed by three
    exact points and re-checked at two more; then an exact solve over QQ(r)."""
    r = sympy.symbols("r", positive=True)
    points = (Fraction(1, 5), Fraction(1, 20), Fraction(1, 100), Fraction(1, 7), Fraction(3, 11))
    matrices = {point: base_hessian(point) for point in points}
    pattern = lattice[O28_IDS[0]]
    column_index = DOUBLET_REAL_X[2]
    support = [index for index in range(TOTAL_DIM) if pattern[column_index][index] != 0]
    component = _component(matrices[points[0]][0], support)
    consistent = all(_component(matrices[point][0], support) == component for point in points)
    size = len(component)
    rows = []
    interpolation_ok = True
    for a in component:
        row = []
        for b in component:
            samples = [(sympy.Rational(p.numerator, p.denominator),
                        sympy.Rational(int(matrices[p][0][a, b]), int(matrices[p][1]))) for p in points[:3]]
            poly = sympy.expand(sympy.interpolate(samples, r)) if any(value != 0 for _, value in samples) else sympy.Integer(0)
            for p in points[3:]:
                expected = sympy.Rational(int(matrices[p][0][a, b]), int(matrices[p][1]))
                if poly.subs(r, sympy.Rational(p.numerator, p.denominator)) != expected:
                    interpolation_ok = False
            row.append(poly)
        rows.append(row)
    field = sympy.QQ.frac_field(r)
    matrix = DomainMatrix([[field.from_sympy(value) for value in row] for row in rows], (size, size), field)
    rhs = DomainMatrix([[field.from_sympy(int(pattern[column_index][a]) * r**2)] for a in component], (size, 1), field)
    solution = matrix.lu_solve(rhs)
    y = [field.to_sympy(solution[index, 0].element) for index in range(size)]
    squared = exact_hessian.congruence_scale_squared()
    theta2 = sum(squared[a] * y[p] ** 2 for p, a in enumerate(component) if SIGMA_SLICE.start <= a < SIGMA_SLICE.stop) / 2
    phi2 = sum(squared[a] * y[p] ** 2 for p, a in enumerate(component) if PHI_SLICE.start <= a < PHI_SLICE.stop) / 2
    shift = -sum(int(pattern[column_index][a]) * r**2 * y[p] for p, a in enumerate(component)) / 2
    big_r = sympy.factor(sympy.cancel(sympy.together(theta2 / r**4)))
    phi_r = sympy.factor(sympy.cancel(sympy.together(phi2 / r**4)))
    shift_r = sympy.factor(sympy.cancel(sympy.together(shift / r**4)))
    pinned = sympy.sympify(O28_R_NUMERATOR, locals={"r": r}) / sympy.sympify(O28_R_DENOMINATOR, locals={"r": r})
    return {
        "variable": "r = r0",
        "heavy_component_size": size,
        "component_same_at_all_points": bool(consistent),
        "degree_two_interpolation_rechecked": bool(interpolation_ok),
        "R_theta_sigma_squared_over_c2_r4": str(big_r),
        "theta_phi_squared_over_c2_r4": str(phi_r),
        "light_mass_shift_over_c2_r4": str(shift_r),
        "R_at_zero": str(sympy.cancel(big_r).subs(r, 0)),
        "matches_pinned_closed_form": sympy.cancel(big_r - pinned) == 0,
        "_R": big_r,
        "_shift": shift_r,
        "_r": r,
    }


def _t_b_requirement(theta_re: float, masses: Mapping[str, float], v_doublet: float, tan_beta: float) -> float:
    """||Y_F|| lower bound for the t-b split from an up-type (15,2,2) admixture (alpha_d = 0 exactly, section
    H_linear_portals.selection_rule), Y_F the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2) (not the
    contract's declared Y126, not the seesaw Y_R: they differ by unfixed Clebsch normalisations).  The admixture of the
    light doublet is theta(t) = sqrt(2 t^2/(1 + t^2)) theta_re (t = |5|/|5bar|; theta_re the witness-column value at
    this |c|), M_u - t e^{i phi} M_d = sin(theta(t)) Y_F v with t = |c_u/c_d| of the 10_H part, so Mirsky gives
    |m_t - t m_b| <= theta(t) ||Y_F|| v; the bound decreases in t for 1 <= t < m_t/m_b (evaluated at t_max) and
    vanishes once t reaches m_t/m_b."""
    theta = theta_re * math.sqrt(2.0 * tan_beta**2 / (1.0 + tan_beta**2))
    return abs(masses["t"] - tan_beta * masses["b"]) / (theta * v_doublet)


def o28_section(data: Mapping[str, Any] = DATA, scales: Mapping[str, Mapping[str, float]] | None = None) -> dict[str, Any]:
    """The O28 portal alone (the other H-linear portals zero).  ``scales`` replaces the repository (M_I, M_GUT) rows
    for mutation tests only.  The colour radius and the Yukawa selection rule at each repository r0 come from the
    full-H-block Schur data of section H_linear_portals (portal_schur, shared cache)."""
    lattice_report = o28_lattice_binding()
    lattice = lattice_report.pop("_integer")
    closed = o28_closed_form(lattice)
    big_r, shift_r, r = closed.pop("_R"), closed.pop("_shift"), closed.pop("_r")
    scales = repository_scales() if scales is None else scales
    repository_r0 = {
        key: Fraction(row["M_I_GeV"] / row["M_GUT_GeV"]).limit_denominator(10**12) for key, row in scales.items()
    }
    r0_values = [*EXACT_R0_VALUES, physical_r0()]
    r0_values += [value for value in repository_r0.values() if value not in r0_values]
    exact_rows = []
    grams = {}
    for value in r0_values:
        row = o28_first_order(value, lattice)
        row.pop("_ys")
        row.pop("_components")
        grams[value] = row.pop("_gram_over_r0_4")
        rational = sympy.Rational(value.numerator, value.denominator)
        row["closed_form_matches"] = (
            sympy.Rational(row["theta_sigma_squared_over_c2_r0_4"].numerator, row["theta_sigma_squared_over_c2_r0_4"].denominator)
            == big_r.subs(r, rational)
            and sympy.Rational(row["light_mass_shift_over_c2_r0_4"].numerator, row["light_mass_shift_over_c2_r0_4"].denominator)
            == shift_r.subs(r, rational)
        )
        row["theta_over_c_r0_2_float"] = math.sqrt(float(row["theta_sigma_squared_over_c2_r0_4"]))
        row["saddle_for_every_c_nonzero"] = row["light_mass_shift_over_c2_r0_4"] < 0 and row["heavy_components_positive_definite"]
        exact_rows.append(row)
    portal_lattice = portal_lattice_binding()["_lattice"]
    v_doublet = data["higgs_vev_GeV"] / math.sqrt(2.0)
    bounds = {}
    masses_at = run_sm_masses(sorted({row["M_I_GeV"] for row in scales.values()}), data)
    for key, row in scales.items():
        r0_value = repository_r0[key]
        o28_row = portal_schur(r0_value, portal_lattice)["rows"][O28_DIRECTION]
        radius = o28_row["colour_radius"]
        c_max = min(PORTAL_BOX, radius) if radius is not None else PORTAL_BOX
        rational = sympy.Rational(r0_value.numerator, r0_value.denominator)
        ratio = float(big_r.subs(r, rational))
        theta_unit = math.sqrt(ratio) * float(r0_value) ** 2
        tan_beta = tan_beta_under_o28(r0_value, grams[r0_value], c_max)
        # Minimum over |c| in {1/4, 1/2, 3/4, 1} x the colour-stable maximum (theta and t both grow with |c|).
        requirement = math.inf
        for fraction in (0.25, 0.5, 0.75, 1.0):
            modulus = fraction * c_max
            t_c = tan_beta_under_o28(r0_value, grams[r0_value], modulus)["tan_beta_max_over_phase"]
            requirement = min(requirement, _t_b_requirement(modulus * theta_unit, masses_at[row["M_I_GeV"]], v_doublet, t_c))
        bounds[key] = {
            "r0": r0_value,
            "r0_float": float(r0_value),
            "M_I_GeV": row["M_I_GeV"],
            "theta_over_c_r0_2": math.sqrt(ratio),
            "theta_max_at_abs_c_4pi": PORTAL_BOX * theta_unit,
            "colour_radius": radius,
            "abs_c_max_colour_stable": c_max,
            "theta_max_colour_stable_any_tan_beta": math.sqrt(2.0) * c_max * theta_unit,
            **tan_beta,
            "t_b_split_requires_Y_F_at_least": requirement,
            "t_b_requirement_exceeds_4pi": requirement > PORTAL_BOX,
            "t_b_requirement_over_4pi": requirement / PORTAL_BOX,
            "induced_126bar_vev_up_type_only": bool(o28_row["induced_126bar_vev_up_type_only"]),
        }
    anchor = physical_r0()
    anchor_ratio = float(big_r.subs(r, sympy.Rational(anchor.numerator, anchor.denominator)))
    theta_anchor_max = PORTAL_BOX * math.sqrt(anchor_ratio) * float(anchor) ** 2
    checks = {
        "O28_lattice_bound_to_plus_minus_192": bool(lattice_report["bound"]),
        "closed_form_derived_and_matches_pinned": bool(closed["matches_pinned_closed_form"])
        and bool(closed["degree_two_interpolation_rechecked"])
        and bool(closed["component_same_at_all_points"]),
        "R_at_zero_is_221184": closed["R_at_zero"] == str(O28_R_AT_ZERO),
        "exact_rows_match_closed_form": all(row["closed_form_matches"] for row in exact_rows),
        "admixture_uniform_over_doublet_and_re_im": all(row["same_for_Re_H_6_9_and_re_im"] for row in exact_rows),
        "re_im_admixtures_orthogonal": all(row["re_im_cross_term_zero"] for row in exact_rows),
        "heavy_blocks_positive_definite": all(row["heavy_components_positive_definite"] for row in exact_rows),
        "saddle_for_every_nonzero_c_at_every_r0": all(row["saddle_for_every_c_nonzero"] for row in exact_rows),
        "second_order_gram_symmetric": all(row["second_order_gram_symmetric"] for row in exact_rows),
        "repository_scales_present": repository_scales_complete(scales) and set(bounds) == set(EXPECTED_REPOSITORY_SCALES),
        "theta_max_small_at_every_repository_r0": bool(bounds)
        and all(math.sqrt(2.0) * row["theta_max_at_abs_c_4pi"] < PORTAL_THETA_THRESHOLD for row in bounds.values()),
        "admixture_up_type_only_at_every_repository_r0": bool(bounds)
        and all(row["induced_126bar_vev_up_type_only"] for row in bounds.values()),
        "t_b_repair_nonperturbative_at_every_repository_r0": bool(bounds)
        and all(row["t_b_requirement_exceeds_4pi"] for row in bounds.values()),
    }
    findings = {
        "second_order_Re_Im_H_mixing_present": not all(
            block["Re_Im_block_zero"] for row in exact_rows for block in row["second_order_H_doublet_block"].values()
        ),
        "b_tau_repairable_by_O28": not checks["admixture_up_type_only_at_every_repository_r0"],
        "colour_radius_below_4pi_at": sorted(
            key for key, row in bounds.items() if row["colour_radius"] is not None and row["colour_radius"] < PORTAL_BOX
        ),
    }
    return {
        "lattice_binding": lattice_report,
        "closed_form": closed,
        "exact_rows": exact_rows,
        "scope_note": (
            "O28 alone (the other H-linear portals zero): O28 is the largest direct 10_H-(15,2,2) portal.  The "
            "portal-set analysis (all five directions on the full H block, the colour-stable region and the tan beta "
            "freedom from O45_B02) is section H_linear_portals"
        ),
        "theta_formula": "theta = |c| r0^2 sqrt(R(r0)), R(r) = 7962624 (13 r^2 + 6)^2/(13 r^4 + 12 r^2 + 36)^2, "
        "theta -> 192 sqrt(6) |c| r0^2 = 470.30 |c| r0^2 (r0 -> 0) for the witness light doublet Re H_6..9 (tan beta = 1); "
        "for a light doublet with t = |5|/|5bar| the admixture is sqrt(2 t^2/(1 + t^2)) times this (<= sqrt(2) times, "
        "exact Gram structure of section H_linear_portals); c = the compiler's re:: or im:: O28 coefficient (complex c: "
        "theta^2 = |c|^2 r0^4 R, the re/im admixtures are orthogonal)",
        "coefficient_box_note": (
            "|c| <= 4 pi is applied to the compiler coefficient, whose operator has lattice entry 192 in the H-Sigma "
            "block: this is generous and overestimates theta, which is conservative for the no-go.  The colour-stable "
            "range is smaller where the colour radius rho_O28(r0) (~ 1/r0) is below 4 pi"
        ),
        "anchor_r0": anchor,
        "theta_max_at_anchor_abs_c_4pi": theta_anchor_max,
        "theta_max_at_anchor_abs_c_4pi_any_tan_beta": math.sqrt(2.0) * theta_anchor_max,
        "repository_r0_bounds": bounds,
        "mirsky_argument": (
            "Y_F denotes the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2); it differs from the "
            "contract's declared Y126 and from the seesaw Y_R by unfixed Clebsch normalisations (the t-b bound is far "
            "above 4 pi, so the O(1) normalisation does not matter).  The O28 admixture of the light doublet is purely "
            "up-type (exact selection rule of section H_linear_portals: O28 acts only on the Y = +1/2 doublet component and "
            "its induced 126bar vev couples only Q u^c and L nu^c), so alpha_d = 0: M_d and M_e keep only their 10_H parts, "
            "M_e = phase x M_d^T, and the b-tau split is not generated at any ||Y_F|| (the earlier alpha_d-free b-tau "
            "estimate is withdrawn).  M_u - t e^{i phi} M_d = sin(theta(t)) Y_F v with t = |c_u/c_d| of the 10_H part and "
            "theta(t) = sqrt(2 t^2/(1 + t^2)) theta_Re.  With O28 on, the doublet Schur complement M0 - |c|^2 S (O(c^2)) "
            "mixes Re H and Im H, so t is computed from its lightest eigenvector (float, maximised over the phase of c), "
            "and |c| is restricted to the colour-stable range min(4 pi, rho_O28(r0)).  Mirsky: max_i |sigma_i(A) - "
            "sigma_i(B)| <= ||A - B||_2, so ||Y_F|| >= |m_t - t m_b|/(theta(t) v) at M_I (v = 174.1 GeV; running masses "
            "from section E)."
        ),
        "findings": findings,
        "sos27_statement": (
            "q0 stays stationary with V_c(q0) = V0 (O28 vanishes at H = 0, its gradient is zero), but for every c != 0 "
            "the doublet Schur complement of the positive-definite heavy block is O(c^2), exactly "
            "-c^2 r0^4 663552 (13 r0^2 + 6)/(13 r0^4 + 12 r0^2 + 36) < 0 on the light doublet: q0 is a saddle and "
            "V + c O28 < V0 nearby, so the SOS27 lower bound V >= V0 fails at the certified member.  Raising O06 by that "
            "shift restores the doublet sector, but for |c| > rho_O28(r0) O28 also drives the (3,1)_|Y|=1/3 sector "
            "tachyonic, which O06 cannot cure (it lifts the H triplets and doublets together and the doublet must stay "
            "light); and the certified SOS27 identity does not contain the H-odd O28 term, so a light doublet with the "
            "O28 portal on needs a new G3 certificate (Route A).  Portal = 0 is load-bearing."
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# (F') All five H-linear portals on the full H block (colour triplets and doublets): exact Schur complements, the
#      colour-stable region, the Yukawa selection rule of the induced 126bar vev, float tan beta scans.
# ---------------------------------------------------------------------------


def _doublet_subspace_vectors(sign: str) -> tuple[dict[int, int], ...]:
    """The real u-vectors spanning one hypercharge component of the 10_H doublets (chart columns Re/Im H_6..9)."""
    return tuple({H_SLICE.start + 2 * k + (0 if part == "Re" else 1): coefficient for k, part, coefficient in vector}
                 for vector in DOUBLET_SUBSPACES[sign])


def _column_combination(integer: np.ndarray, columns: Sequence[int], vector: Mapping[int, int]) -> np.ndarray:
    position = {column: index for index, column in enumerate(columns)}
    total = np.zeros(integer.shape[0], dtype=np.int64)
    for column, coefficient in vector.items():
        total += coefficient * integer[:, position[column]]
    return total


def portal_lattice_binding() -> dict[str, Any]:
    """Bind all twenty H columns (colour triplets Re/Im H_0..5 and doublets Re/Im H_6..9) of every H-linear
    parameter's compiler u-Hessian to the (1/6) Z lattice at r0 = 1 (float residual < 1e-9), re-check every (column
    group, chart block) at r0 = 1/5 with its pinned r0 power (PORTAL_DOUBLET_COUPLING, PORTAL_TRIPLET_COUPLING),
    require the H x H and non-H x non-H blocks and the gradient to vanish at both r0 (compiler float64 evidence), and
    read off exactly (integer lattice) which hypercharge component of the doublets each direction acts on
    (PORTAL_DOUBLET_SOURCE)."""
    base = portal_compiler_rows(Fraction(1))
    fifth = portal_compiler_rows(Fraction(1, 5))
    columns = list(TRIPLET_COLUMNS + DOUBLET_COLUMNS)
    non_h = np.ones(TOTAL_DIM, dtype=bool)
    non_h[H_SLICE] = False
    patterns: dict[str, Any] = {}
    lattice: dict[str, dict[int, tuple[tuple[int, Fraction, int], ...]]] = {}
    bound = True
    for direction in EXPECTED_H_LINEAR_DIRECTIONS:
        expected_block, degree = PORTAL_DOUBLET_COUPLING[direction]
        expected = {
            "triplet": dict(PORTAL_TRIPLET_COUPLING[direction]),
            "doublet": {expected_block: degree} if expected_block else {},
        }
        for parameter in (f"re::{direction}", f"im::{direction}"):
            scaled = PORTAL_LATTICE_DENOMINATOR * base[parameter][:, columns]
            integer = np.rint(scaled).astype(np.int64)
            residual = float(np.max(np.abs(scaled - integer)))
            h_by_h_zero = not np.any(integer[H_SLICE])
            off_h_zero = all(
                float(np.max(np.abs(rows[parameter][np.ix_(non_h, non_h)]))) == 0.0 for rows in (base, fifth)
            )
            gradient = max(
                float(np.max(np.abs(base[parameter + "::gradient"]))), float(np.max(np.abs(fifth[parameter + "::gradient"])))
            )
            found: dict[str, dict[str, int | None]] = {"triplet": {}, "doublet": {}}
            residual_fifth = 0.0
            entries: dict[str, dict[str, list[Fraction]]] = {"triplet": {}, "doublet": {}}
            ok = residual < 1.0e-9 and h_by_h_zero and off_h_zero and gradient == 0.0
            column_power: dict[tuple[str, str], int] = {}
            for group, group_columns in (("triplet", TRIPLET_COLUMNS), ("doublet", DOUBLET_COLUMNS)):
                positions = [columns.index(column) for column in group_columns]
                for name, window in PORTAL_BLOCK_SLICES.items():
                    block = integer[window][:, positions]
                    if not np.any(block):
                        continue
                    power = expected[group].get(name)
                    found[group][name] = power
                    entries[group][name] = sorted({Fraction(int(value), PORTAL_LATTICE_DENOMINATOR) for value in block.flat if value})
                    if power is None:
                        ok = False
                        continue
                    column_power[(group, name)] = power
                    check = PORTAL_LATTICE_DENOMINATOR * fifth[parameter][window][:, list(group_columns)] * 5.0**power
                    difference = float(np.max(np.abs(check - block)))
                    residual_fifth = max(residual_fifth, difference)
                    ok &= difference < 1.0e-9
                ok &= set(found[group]) == set(expected[group])
            annihilated = {
                sign: all(not np.any(_column_combination(integer, columns, vector)) for vector in _doublet_subspace_vectors(sign))
                for sign in ("+", "-")
            }
            if annihilated["+"] and annihilated["-"]:
                source = None
            elif annihilated["+"] or annihilated["-"]:
                source = "-" if annihilated["+"] else "+"
            else:
                source = "both"
            ok &= source == PORTAL_DOUBLET_SOURCE[direction]
            bound &= ok
            doublet_blocks = sorted(found["doublet"])
            patterns[parameter] = {
                "doublet_column_block": doublet_blocks[0] if len(doublet_blocks) == 1 else doublet_blocks,
                "expected_block": expected_block,
                "r0_power": degree,
                "doublet_column_entries": entries["doublet"].get(expected_block, []) if expected_block else
                sorted({value for values in entries["doublet"].values() for value in values}),
                "doublet_column_nonzero_count": int(np.count_nonzero(integer[:, [columns.index(c) for c in DOUBLET_COLUMNS]])),
                "triplet_column_blocks": {name: {"r0_power": found["triplet"][name], "entries": entries["triplet"][name]}
                                          for name in sorted(found["triplet"])},
                "expected_triplet_blocks": {name: power for name, power in PORTAL_TRIPLET_COUPLING[direction]},
                "doublet_source_hypercharge": source,
                "expected_doublet_source_hypercharge": PORTAL_DOUBLET_SOURCE[direction],
                "H_by_H_and_nonH_by_nonH_blocks_zero": bool(h_by_h_zero and off_h_zero),
                "max_rounding_residual_r0_1": residual,
                "max_residual_r0_one_fifth_rescaled": residual_fifth,
                "gradient_max_abs": gradient,
                "bound": bool(ok),
            }
            output: dict[int, tuple[tuple[int, Fraction, int], ...]] = {}
            for position, column in enumerate(columns):
                group = "triplet" if column in TRIPLET_COLUMNS else "doublet"
                items = []
                for index in np.nonzero(integer[:, position])[0].tolist():
                    name = next(key for key, window in PORTAL_BLOCK_SLICES.items() if window.start <= index < window.stop)
                    power = column_power.get((group, name))
                    if power is None:
                        continue
                    items.append((int(index), Fraction(int(integer[index, position]), PORTAL_LATTICE_DENOMINATOR), power))
                output[column] = tuple(items)
            lattice[parameter] = output
    return {
        "patterns": patterns,
        "bound": bool(bound),
        "lattice_denominator": PORTAL_LATTICE_DENOMINATOR,
        "homogeneity": (
            "each H-linear operator is linear in (H, H^dag), so at H = 0 its Hessian has only H x (non-H) blocks (checked: "
            "the H x H and non-H x non-H blocks vanish).  Doublet columns: O28 (H^dag Sigma^2 Sigma^dag) to Sigma with "
            "<Sigma>^2 ~ r0^2; O15 (Phi H^dag Sigma) and O45_B02 (Phi^2 H^dag Sigma) to Phi with <Sigma> ~ r0 (times <Phi> "
            "for O45); O38 (Phi H^dag Sigma^dag S^dag) to Phi with <Sigma^dag><S^dag> ~ r0^2; O45_B01 none (the PS-singlet "
            "p cannot connect (1,2,2)_10 to (15,2,2)_126bar).  Colour-triplet columns: O15 to Sigma with <Phi> = p ~ 1 (the "
            "126bar (6,1,1)) and to Phi with ~ r0; O38 to Sigma with <Phi><S^dag> ~ r0 and to Phi with ~ r0^2; O28 to Sigma "
            "with ~ r0^2; O45_B01 and O45_B02 to Phi with ~ r0.  O15, O28 and O45_B02 act on the Y = +1/2 ('5') component "
            "of the doublets and annihilate the Y = -1/2 ('5bar') one; O38 acts on the Y = -1/2 component only"
        ),
        "_lattice": lattice,
    }


def _d2_inner(first: Mapping[int, Fraction], second: Mapping[int, Fraction], window: slice | None, squared: Sequence[Any]) -> Fraction:
    """(1/2) sum_a D_a^2 x_a y_a over a chart block (None: all coordinates); the light-doublet norm is D^2 = 2."""
    total = Fraction(0)
    for index, value in first.items():
        if window is not None and not (window.start <= index < window.stop):
            continue
        other = second.get(index)
        if other:
            total += Fraction(squared[index]) * value * other
    return total / 2


@lru_cache(maxsize=1)
def sigma_basis_bilinears() -> tuple[tuple[tuple[int, int, int, int], ...], ...]:
    """Per chart Sigma basis state k (the exact Z[i] basis e_first + i sign e_second, identical to the compiler chart
    basis: g2_audit.exact_sigma_chart_convention_certificate): the nonzero upper-triangular entries (i, j, re, im) of its
    16.16 bilinear C Gamma_first + i sign C Gamma_second (the same contraction that couples sigma_std only to nu^c nu^c)."""
    conj = charge_conjugation()
    output = []
    for first, second, sign in g2_audit._exact_sigma_basis_rows():
        total = _g_add(_g_mul(conj, gamma_product(first)), _g_scale(_g_mul(conj, gamma_product(second)), (0, sign)))
        block = _bilinear_16(total)
        rows, columns = np.nonzero((block[0] != 0) | (block[1] != 0))
        output.append(
            tuple(
                (int(i), int(j), int(block[0][i, j]), int(block[1][i, j]))
                for i, j in zip(rows.tolist(), columns.tolist(), strict=True)
                if i <= j
            )
        )
    return tuple(output)


def induced_yukawa_content(response: Mapping[int, Any]) -> dict[str, Any]:
    """Exact 16.16 Yukawa content of the Sigma part of a u-coordinate vector (Sigma coefficient k = u[2k] + i u[2k+1]):
    the bilinear sum_k sigma_k (C Gamma_first + i sign C Gamma_second) on the 16, entries labelled by the spinor section's
    SM names.  Returns the nonzero pair types ('u-uc', 'd-uc', 'nu-nuc', 'e-nuc' for the up-type structures Q u^c and
    L nu^c; 'd-dc', 'dc-u', 'e-ec', 'ec-nu' for the down-type ones; others such as 'nuc-nuc'), whether only up-type
    structures occur, and whether every lepton entry has 3 times the modulus of every quark entry (the (15,2,2) Clebsch)."""
    bilinears = sigma_basis_bilinears()
    info = spinor_states()
    names = [info["names"][state].split("[")[0] for state in info["sixteen"]]
    entries: dict[tuple[int, int], list[Fraction]] = {}
    for k in range(chart.SIGMA_COMPLEX_DIM):
        re_part = Fraction(response.get(SIGMA_SLICE.start + 2 * k, 0))
        im_part = Fraction(response.get(SIGMA_SLICE.start + 2 * k + 1, 0))
        if not re_part and not im_part:
            continue
        for i, j, a, b in bilinears[k]:
            slot = entries.setdefault((i, j), [Fraction(0), Fraction(0)])
            slot[0] += re_part * a - im_part * b
            slot[1] += re_part * b + im_part * a
    moduli: dict[str, set[Fraction]] = {}
    for (i, j), (re_part, im_part) in entries.items():
        if re_part or im_part:
            pair = "-".join(sorted((names[i], names[j])))
            moduli.setdefault(pair, set()).add(re_part * re_part + im_part * im_part)
    pairs = sorted(moduli)
    quark = set().union(*(moduli.get(pair, set()) for pair in QUARK_UP_TYPE_PAIRS))
    lepton = set().union(*(moduli.get(pair, set()) for pair in LEPTON_UP_TYPE_PAIRS))
    return {
        "pairs": pairs,
        "up_type_only": bool(pairs) and set(pairs) <= set(UP_TYPE_PAIRS),
        "lepton_over_quark_modulus_3": len(quark) == 1 and lepton == {9 * next(iter(quark))},
    }


def colour_radius(gram: Sequence[Sequence[Fraction]], h_diagonal: Sequence[Fraction]) -> dict[str, Any]:
    """rho = 1/sqrt(lambda_max(H^-1/2 G H^-1/2)) for the colour-triplet Schur complement H - |c|^2 G (float of the exact
    matrices), with an exact inertia bracket: H - t G has no negative eigenvalue at t = (1 - 1e-6) rho^2 and at least
    one at t = (1 + 1e-6) rho^2 (Fraction arithmetic).  radius None when G = 0 (no colour coupling)."""
    size = len(h_diagonal)
    matrix = np.array([[float(value) for value in row] for row in gram])
    if not np.any(matrix):
        return {"radius": None, "exact_bracket": True, "negative_modes_just_beyond": 0}
    scale = 1.0 / np.sqrt(np.array([float(value) for value in h_diagonal]))
    largest = float(np.max(np.linalg.eigvalsh(matrix * scale[:, None] * scale[None, :])))
    squared = 1.0 / largest

    def negatives(t: Fraction) -> int:
        shifted = [[(h_diagonal[a] if a == b else Fraction(0)) - t * gram[a][b] for b in range(size)] for a in range(size)]
        return int(exact_hessian.exact_inertia(shifted)["negative"])

    below = negatives(Fraction(squared * (1.0 - COLOUR_BRACKET_RELATIVE)))
    beyond = negatives(Fraction(squared * (1.0 + COLOUR_BRACKET_RELATIVE)))
    return {"radius": math.sqrt(squared), "exact_bracket": below == 0 and beyond > 0, "negative_modes_just_beyond": beyond}


def doublet_compensation(gram_rr: np.ndarray, r0: Fraction, modulus: float) -> float:
    """The O06 raise eps (chart units, M_GUT^2) that brings the lowest H-doublet level of M0 + 2 eps - |c|^2 S back to 0
    (S the doublet Schur Gram, phase independent): eps = max(0, lambda_max(|c|^2 S - M0))/2."""
    r0f = float(r0)
    m0 = np.diag([0.0] * 4 + [2.0 * r0f**2] * 4)
    return max(0.0, float(np.max(np.linalg.eigvalsh(modulus**2 * gram_rr - m0)))) / 2.0


def _triplet_h_diagonal(r0: Fraction) -> list[Fraction]:
    """u-coordinate H triplet block at q0 (eps = 0) in TRIPLET_COLUMNS order: Re H_0..5 -> 2, Im H_0..5 -> 2 + 2 r0^2."""
    return [Fraction(2)] * 6 + [2 + 2 * Fraction(r0) ** 2] * 6


def _lattice_digest(lattice: Mapping[str, Mapping[int, Sequence[tuple[int, Fraction, int]]]]) -> str:
    items = [(parameter, column, tuple(lattice[parameter][column])) for parameter in sorted(lattice) for column in sorted(lattice[parameter])]
    return hashlib.sha256(repr(items).encode("utf-8")).hexdigest()


_PORTAL_SCHUR_CACHE: dict[tuple[Fraction, str], dict[str, Any]] = {}


def portal_schur(r0: Fraction, lattice: Mapping[str, Mapping[int, Sequence[tuple[int, Fraction, int]]]]) -> dict[str, Any]:
    """Exact Schur data of the five H-linear directions at q0 for this r0 (cached per r0 and lattice digest).

    The Hessian of V + sum_k c_k O_k at q0 is exactly [[H_HH, B(c)^T], [B(c), A]] with B(c) = sum_k c_k B_k (the portal
    Hessians have only H x non-H blocks and A, the witness Hessian off H, does not depend on c).  For every parameter
    k and H column j the heavy response y = A^-1 w (w = B_k e_j) is solved exactly on the positive-definite heavy
    component connected to its support; Gram entries w_{k,j} . y_{l,i} give the Schur complement
    H_HH - sum c_k c_l G[k, l] exactly, which by Haynsworth inertia additivity decides the second-order stability of q0."""
    r0 = Fraction(r0)
    key = (r0, _lattice_digest(lattice))
    if key in _PORTAL_SCHUR_CACHE:
        return _PORTAL_SCHUR_CACHE[key]
    numerator, denominator = base_hessian(r0)
    adjacency = base_adjacency(r0)
    squared = exact_hessian.congruence_scale_squared()
    ws: dict[tuple[str, int], dict[int, Fraction]] = {}
    ys: dict[tuple[str, int], dict[int, Fraction]] = {}
    blocks: dict[tuple[int, ...], list[list[Fraction]]] = {}
    positive_definite = True
    solvable = True
    avoid_h = True
    sizes: dict[tuple[str, str], set[int]] = {}
    only_sigma_phi: dict[str, bool] = {direction: True for direction in EXPECTED_H_LINEAR_DIRECTIONS}
    for parameter in PORTAL_PARAMETERS:
        direction = parameter.split("::", 1)[1]
        for column in TRIPLET_COLUMNS + DOUBLET_COLUMNS:
            w = {index: value * r0**power for index, value, power in lattice[parameter][column]}
            ws[(parameter, column)] = w
            if not w:
                ys[(parameter, column)] = {}
                continue
            component = tuple(_component_from(adjacency, sorted(w)))
            group = "triplet" if column in TRIPLET_COLUMNS else "doublet"
            sizes.setdefault((direction, group), set()).add(len(component))
            avoid_h &= not any(H_SLICE.start <= index < H_SLICE.stop for index in component)
            if group == "doublet":
                only_sigma_phi[direction] &= all(
                    SIGMA_SLICE.start <= index < SIGMA_SLICE.stop or PHI_SLICE.start <= index < PHI_SLICE.stop for index in component
                )
            if component not in blocks:
                block = [[Fraction(int(numerator[a, b]), denominator) for b in component] for a in component]
                inertia = exact_hessian.exact_inertia(block, component)
                positive_definite &= inertia["positive"] == len(component) and inertia["negative"] == 0 and inertia["zero"] == 0
                blocks[component] = block
            y, rank = _solve(blocks[component], [w.get(index, Fraction(0)) for index in component])
            solvable &= rank == len(component)
            ys[(parameter, column)] = {index: value for index, value in zip(component, y, strict=True) if value}

    def gram(first: tuple[str, int], second: tuple[str, int]) -> Fraction:
        y = ys[second]
        return sum((value * y[index] for index, value in ws[first].items() if index in y), Fraction(0))

    triplet_doublet_decoupled = all(
        gram((p, j), (q, i)) == 0 for p in PORTAL_PARAMETERS for q in PORTAL_PARAMETERS for j in TRIPLET_COLUMNS for i in DOUBLET_COLUMNS
    )
    triplet: dict[tuple[str, str], list[list[Fraction]]] = {
        (p, q): [[gram((p, j), (q, i)) for i in TRIPLET_COLUMNS] for j in TRIPLET_COLUMNS]
        for p in PORTAL_PARAMETERS
        for q in PORTAL_PARAMETERS
    }
    doublet: dict[tuple[str, str], list[list[Fraction]]] = {
        (p, q): [[gram((p, j), (q, i)) for i in DOUBLET_COLUMNS] for j in DOUBLET_COLUMNS]
        for direction in EXPECTED_H_LINEAR_DIRECTIONS
        for p in (f"re::{direction}", f"im::{direction}")
        for q in (f"re::{direction}", f"im::{direction}")
    }
    h_triplet = _triplet_h_diagonal(r0)
    projectors = {
        sign: [[sum((Fraction(v.get(a, 0) * v.get(b, 0)) for v in _doublet_subspace_vectors(sign)), Fraction(0)) / 2
                for b in DOUBLET_COLUMNS] for a in DOUBLET_COLUMNS]
        for sign in ("+", "-")
    }
    sigma_std_content = induced_yukawa_content(
        {SIGMA_SLICE.start + 2 * index + part: Fraction(int(value))
         for index, (re_value, im_value) in enumerate(zip(*candidate.sigma_std_raw_coordinates(), strict=True))
         for part, value in ((0, re_value), (1, im_value)) if value}
    )
    rows: dict[str, dict[str, Any]] = {}
    for direction in EXPECTED_H_LINEAR_DIRECTIONS:
        re_p, im_p = f"re::{direction}", f"im::{direction}"
        coupled = any(ws[(parameter, column)] for parameter in (re_p, im_p) for column in DOUBLET_COLUMNS)
        per_column = [
            (
                _d2_inner(ys[(parameter, column)], ys[(parameter, column)], SIGMA_SLICE, squared),
                _d2_inner(ys[(parameter, column)], ys[(parameter, column)], PHI_SLICE, squared),
                -doublet[(parameter, parameter)][DOUBLET_COLUMNS.index(column)][DOUBLET_COLUMNS.index(column)] / 2,
            )
            for parameter in (re_p, im_p)
            for column in DOUBLET_REAL_X
        ]
        first = per_column[0]
        cross = [_d2_inner(ys[(re_p, column)], ys[(im_p, column)], None, squared) for column in DOUBLET_REAL_X]
        rr, ii, ri = doublet[(re_p, re_p)], doublet[(im_p, im_p)], doublet[(re_p, im_p)]
        size = len(DOUBLET_COLUMNS)
        doublet_phase_free = rr == ii and all(ri[a][b] == -ri[b][a] for a in range(size) for b in range(size))
        trr, tii, tri = triplet[(re_p, re_p)], triplet[(im_p, im_p)], triplet[(re_p, im_p)]
        tsize = len(TRIPLET_COLUMNS)
        triplet_phase_free = trr == tii and all(tri[a][b] == -tri[b][a] for a in range(tsize) for b in range(tsize))
        source = PORTAL_DOUBLET_SOURCE[direction]
        theta_re2 = first[0]
        admixture_structure = True
        for parameter in (re_p, im_p):
            sigma_gram = [
                [_d2_inner(ys[(parameter, a)], ys[(parameter, b)], SIGMA_SLICE, squared) for b in DOUBLET_COLUMNS] for a in DOUBLET_COLUMNS
            ]
            if coupled:
                admixture_structure &= source in ("+", "-") and sigma_gram == [
                    [2 * theta_re2 * value for value in row] for row in projectors[source]
                ]
            else:
                admixture_structure &= all(value == 0 for row in sigma_gram for value in row)
        contents = [
            induced_yukawa_content(ys[(parameter, column)])
            for parameter in (re_p, im_p)
            for column in DOUBLET_COLUMNS
            if any(SIGMA_SLICE.start <= index < SIGMA_SLICE.stop for index in ys[(parameter, column)])
        ]
        radius = colour_radius(trr, h_triplet)
        gram_rr_float = np.array([[float(value) for value in row] for row in rr])
        eps_box = doublet_compensation(gram_rr_float, r0, PORTAL_BOX)
        rows[direction] = {
            "r0": r0,
            "direction": direction,
            "doublet_coupling": bool(coupled),
            "heavy_component_sizes": sorted(sizes.get((direction, "doublet"), set())),
            "triplet_heavy_component_sizes": sorted(sizes.get((direction, "triplet"), set())),
            "only_sigma_and_phi_in_heavy_components": bool(only_sigma_phi[direction]),
            "uniform_over_Re_H_6_9_and_re_im": all(row == first for row in per_column),
            "re_im_admixtures_orthogonal": all(value == 0 for value in cross),
            "gram_symmetric": all(rr[a][b] == rr[b][a] for a in range(size) for b in range(size)),
            "doublet_schur_phase_independent": bool(doublet_phase_free),
            "triplet_schur_phase_independent": bool(triplet_phase_free),
            "theta_sigma_squared_per_unit_c": first[0],
            "theta_phi_squared_per_unit_c": first[1],
            "light_mass_shift_per_unit_c2": first[2],
            "theta_sigma_per_unit_c_float": math.sqrt(float(first[0])),
            "theta_sigma_over_c_r0_2_float": math.sqrt(float(first[0])) / float(r0) ** 2,
            "theta_sigma_max_over_tan_beta_per_unit_c_float": math.sqrt(2.0 * float(first[0])),
            "theta_phi_per_unit_c_float": math.sqrt(float(first[1])),
            "light_mass_shift_over_c2_r0_2_float": float(first[2]) / float(r0) ** 2,
            "saddle_for_every_c_nonzero": bool(coupled and first[2] < 0 and positive_definite),
            "doublet_source_hypercharge": source,
            "sigma_admixture_gram_equals_2_theta2_times_source_projector": bool(admixture_structure),
            "induced_126bar_yukawa_pairs": sorted({pair for content in contents for pair in content["pairs"]}),
            "induced_126bar_vev_up_type_only": all(content["up_type_only"] for content in contents),
            "induced_lepton_over_quark_modulus_3": all(content["lepton_over_quark_modulus_3"] for content in contents),
            "colour_triplet_coupling": any(ws[(parameter, column)] for parameter in (re_p, im_p) for column in TRIPLET_COLUMNS),
            "colour_radius": radius["radius"],
            "colour_radius_exact_bracket": bool(radius["exact_bracket"]),
            "colour_negative_modes_just_beyond_radius": radius["negative_modes_just_beyond"],
            "doublet_compensation_eps_at_abs_c_4pi": eps_box,
            "colour_radius_with_O06_compensation_upper": (
                radius["radius"] * math.sqrt(1.0 + eps_box) if radius["radius"] is not None else None
            ),
            "_gram16": np.array(
                [[float(doublet[(p, q)][a][b]) for q in (re_p, im_p) for b in range(size)] for p in (re_p, im_p) for a in range(size)]
            ),
            "_gram_rr": gram_rr_float,
        }
    output = {
        "r0": r0,
        "rows": rows,
        "heavy_components_positive_definite": bool(positive_definite),
        "heavy_systems_nonsingular": bool(solvable),
        "heavy_components_avoid_H": bool(avoid_h),
        "triplet_doublet_schur_blocks_decoupled": bool(triplet_doublet_decoupled),
        "sigma_std_yukawa_pairs": sigma_std_content["pairs"],
        "_triplet_float": {pair: np.array([[float(value) for value in row] for row in matrix]) for pair, matrix in triplet.items()},
    }
    _PORTAL_SCHUR_CACHE[key] = output
    return output


def combination_outer_bounds(schur: Mapping[str, Any]) -> dict[str, Any]:
    """Necessary bounds on each |c_d| over the colour-stable region of ANY portal combination with the other directions in
    the |c| <= 4 pi box (float of exact Grams).  If H_HH(eps) - Q(c) >= 0 then for every triplet vector v and heavy z,
    (z^T B(c) v)^2 <= (z^T A z)(v^T H v); with z = A^-1 B_d(phi_d) v (the response of direction d at the phase of c_d)
    this gives |c_d| m <= sqrt(m h) + 4 pi sum_{d' != d} X_d', m = v^T G_d v, X_d' = sqrt(sum_{a, b in re, im}
    (v^T G[(d, a), (d', b)] v)^2), h = v^T H(eps_max) v, v the top generalised eigenvector of (G_d, H) and eps_max the
    largest O06 compensation that keeps the doublet light anywhere in the box (Minkowski bound over the directions)."""
    r0 = Fraction(schur["r0"])
    rows = schur["rows"]
    triplet = schur["_triplet_float"]
    root = sum(
        PORTAL_BOX * math.sqrt(max(0.0, float(np.max(np.linalg.eigvalsh(rows[direction]["_gram_rr"])))))
        for direction in EXPECTED_H_LINEAR_DIRECTIONS
    )
    eps_max = root**2 / 2.0
    h_zero = np.array([float(value) for value in _triplet_h_diagonal(r0)])
    h_eps = h_zero + 2.0 * eps_max
    bounds = {}
    for direction in EXPECTED_H_LINEAR_DIRECTIONS:
        re_p = f"re::{direction}"
        gram_d = triplet[(re_p, re_p)]
        if not np.any(gram_d):
            bounds[direction] = None
            continue
        scale = 1.0 / np.sqrt(h_zero)
        _values, vectors = np.linalg.eigh(gram_d * scale[:, None] * scale[None, :])
        v = scale * vectors[:, -1]
        m = float(v @ gram_d @ v)
        h = float(v @ (h_eps * v))
        others = 0.0
        for other in EXPECTED_H_LINEAR_DIRECTIONS:
            if other == direction:
                continue
            others += math.sqrt(sum(
                float(v @ triplet[(f"{a}::{direction}", f"{b}::{other}")] @ v) ** 2 for a in ("re", "im") for b in ("re", "im")
            ))
        bounds[direction] = math.sqrt(h / m) + PORTAL_BOX * others / m
    return {"outer_bound": bounds, "eps_max_O06_compensation_in_box": eps_max}


def tan_beta_scan(r0: Fraction, gram: np.ndarray, target_ratio: float, max_modulus: float = PORTAL_BOX,
                  n_moduli: int = TAN_BETA_MODULI, n_phases: int = TAN_BETA_PHASES) -> dict[str, Any]:
    """Float: tan beta (|5 part|/|5bar part|, symmetrised to >= 1) of the four lightest H-doublet eigenvectors of the
    doublet Schur complement M0 - |c|^2 S(phi) (u coordinates; S = gram, M0 = diag(0^4, (2 r0^2)^4)) over a grid of
    |c| in (0, max_modulus] and of the phase of c.  A retuned O06 shifts every H eigenvalue equally and moves no
    eigenvector.  Records the largest tan beta and the smallest grid |c| reaching target_ratio (m_t/m_b at M_I)."""
    r0f = float(r0)
    m0 = np.diag([0.0] * 4 + [2.0 * r0f**2] * 4)
    s_rr, s_ii = gram[:8, :8], gram[8:, 8:]
    s_ri = gram[:8, 8:] + gram[8:, :8]
    worst = 1.0
    first_reaching = None
    for modulus in np.linspace(max_modulus / n_moduli, max_modulus, n_moduli):
        worst_here = 1.0
        for phase in np.linspace(0.0, math.pi, n_phases, endpoint=False):
            s = math.cos(phase) ** 2 * s_rr + math.sin(phase) ** 2 * s_ii + math.sin(phase) * math.cos(phase) * s_ri
            _values, vectors = np.linalg.eigh(m0 - modulus**2 * s)
            for column in range(4):
                vector = vectors[:, column]
                h = vector[:4] + 1j * vector[4:]
                five = abs(h[0] - 1j * h[1]) ** 2 + abs(h[2] - 1j * h[3]) ** 2
                five_bar = abs(h[0] + 1j * h[1]) ** 2 + abs(h[2] + 1j * h[3]) ** 2
                if five == 0.0 or five_bar == 0.0:
                    worst_here = math.inf
                    continue
                ratio = math.sqrt(five / five_bar)
                worst_here = max(worst_here, ratio, 1.0 / ratio)
        worst = max(worst, worst_here)
        if first_reaching is None and worst_here >= target_ratio:
            first_reaching = float(modulus)
    return {
        "tan_beta_max_over_scan": worst,
        "max_abs_c_scanned": float(max_modulus),
        "reaches_m_t_over_m_b": worst >= target_ratio,
        "smallest_grid_abs_c_reaching_m_t_over_m_b": first_reaching,
        "moduli_scanned": n_moduli,
        "phases_scanned": n_phases,
    }


def _public_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def portals_section(data: Mapping[str, Any] = DATA, scales: Mapping[str, Mapping[str, float]] | None = None,
                    o28: Mapping[str, Any] | None = None, comparison: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """All five H-linear portals at q0 on the full H block: exact per-direction Schur data (colour triplets and
    doublets) at the physical member and the repository r0, the colour-stable region (per direction, and inner / outer
    bounds for any combination), the exact Yukawa selection rule of the induced 126bar vev, and float tan beta scans in
    the box and in the colour-stable region.  ``o28`` (the O28-alone section) cross-checks the general solver exactly;
    ``comparison`` is the data section (recomputed from ``data`` and ``scales`` when omitted)."""
    binding = portal_lattice_binding()
    lattice = binding.pop("_lattice")
    scales = repository_scales() if scales is None else scales
    comparison = data_section(data, scales) if comparison is None else comparison
    repository_r0 = {
        key: Fraction(row["M_I_GeV"] / row["M_GUT_GeV"]).limit_denominator(10**12) for key, row in scales.items()
    }
    anchor = physical_r0()
    r0_values = [anchor] + [value for value in repository_r0.values() if value != anchor]
    per_direction: dict[str, list[dict[str, Any]]] = {direction: [] for direction in EXPECTED_H_LINEAR_DIRECTIONS}
    schur_by_r0 = {value: portal_schur(value, lattice) for value in r0_values}
    outer_by_r0 = {value: combination_outer_bounds(schur) for value, schur in schur_by_r0.items()}
    for value in r0_values:
        for direction in EXPECTED_H_LINEAR_DIRECTIONS:
            row = _public_row(schur_by_r0[value]["rows"][direction])
            row["colour_radius_outer_bound_any_combination"] = outer_by_r0[value]["outer_bound"][direction]
            per_direction[direction].append(row)
    theta_unit = {
        (direction, value): math.sqrt(float(schur_by_r0[value]["rows"][direction]["theta_sigma_squared_per_unit_c"]))
        for direction in EXPECTED_H_LINEAR_DIRECTIONS
        for value in r0_values
    }
    scale_free = {row["test"]: row for row in comparison.get("tests_scale_free", [])}
    immune_scale_free = scale_free.get("(m_s/m_d)/(m_mu/m_e)")
    per_scale = comparison.get("tests_per_scale", {})
    masses_at = run_sm_masses(sorted({row["M_I_GeV"] for row in scales.values()}), data)
    bounds = {}
    for key, row in scales.items():
        value = repository_r0[key]
        schur = schur_by_r0[value]
        rows = schur["rows"]
        outer = outer_by_r0[value]["outer_bound"]
        masses = masses_at[row["M_I_GeV"]]
        target_ratio = masses["t"] / masses["b"]
        stable_max = {
            direction: min(PORTAL_BOX, outer[direction]) if outer[direction] is not None else PORTAL_BOX
            for direction in EXPECTED_H_LINEAR_DIRECTIONS
        }
        coupled = [direction for direction in EXPECTED_H_LINEAR_DIRECTIONS if rows[direction]["doublet_coupling"]]
        scans_box = {direction: tan_beta_scan(value, rows[direction]["_gram16"], target_ratio) for direction in coupled}
        scans_stable = {
            direction: tan_beta_scan(value, rows[direction]["_gram16"], target_ratio, max_modulus=min(PORTAL_BOX, rows[direction]["colour_radius"] or PORTAL_BOX))
            for direction in coupled
        }
        reaching_box = sorted(direction for direction, scan in scans_box.items() if scan["reaches_m_t_over_m_b"])
        reaching_stable = sorted(direction for direction, scan in scans_stable.items() if scan["reaches_m_t_over_m_b"])
        contributions_box = {direction: PORTAL_BOX * math.sqrt(2.0) * theta_unit[(direction, value)] for direction in EXPECTED_H_LINEAR_DIRECTIONS}
        contributions_stable = {
            direction: stable_max[direction] * math.sqrt(2.0) * theta_unit[(direction, value)] for direction in EXPECTED_H_LINEAR_DIRECTIONS
        }
        theta_box = sum(contributions_box.values())
        theta_stable = sum(contributions_stable.values())
        up_type_only = all(rows[direction]["induced_126bar_vev_up_type_only"] for direction in coupled)
        immune_row = (per_scale.get(f"M_I[{key}]") or {}).get("(m_b/m_s)/(m_tau/m_mu)")
        immune_pulls = [
            item[name]
            for item in (immune_scale_free, immune_row)
            if isinstance(item, Mapping)
            for name in ("pull_raw_sigma", "pull_conservative_sigma")
        ]
        immune_excluded = len(immune_pulls) == 4 and min(immune_pulls) >= NOGO_PULL_THRESHOLD
        bounds[key] = {
            "r0": value,
            "r0_float": float(value),
            "M_I_GeV": row["M_I_GeV"],
            "m_t_over_m_b_at_M_I": target_ratio,
            "colour_radius": {direction: rows[direction]["colour_radius"] for direction in EXPECTED_H_LINEAR_DIRECTIONS},
            "colour_radius_outer_bound_any_combination": outer,
            "colour_stable_abs_c_max_in_box": stable_max,
            "eps_max_O06_compensation_in_box": outer_by_r0[value]["eps_max_O06_compensation_in_box"],
            "theta_up_type_max_per_direction_box": contributions_box,
            "theta_up_type_max_box_triangle_bound": theta_box,
            "theta_up_type_max_colour_stable_triangle_bound": theta_stable,
            "O28_share_of_box_bound": contributions_box["O28_B01_unique_Hdag_Sigma2_Sigmadag"] / theta_box if theta_box else None,
            "induced_126bar_vev_up_type_only_every_direction": bool(up_type_only),
            "down_type_126bar_admixture": "0 (exact): M_e = phase x M_d^T for every portal combination",
            "portal_immune_tests_min_pull_raw_sigma": min(immune_pulls[0::2]) if immune_pulls else None,
            "portal_immune_tests_min_pull_conservative_sigma": min(immune_pulls[1::2]) if immune_pulls else None,
            "tan_beta_scan_box": scans_box,
            "tan_beta_scan_colour_stable": scans_stable,
            "tan_beta_reaches_m_t_over_m_b_in_box_with": reaching_box,
            "tan_beta_reaches_m_t_over_m_b_colour_stable_with": reaching_stable,
            "t_b_bound_survives_portal_set": not reaching_stable,
            "portal_fix_excluded": bool(up_type_only and immune_excluded),
        }
    anchor_rows = schur_by_r0[anchor]["rows"]
    anchor_theta = PORTAL_BOX * math.sqrt(2.0) * sum(theta_unit[(direction, anchor)] for direction in EXPECTED_H_LINEAR_DIRECTIONS)
    coupled_all = [direction for direction in EXPECTED_H_LINEAR_DIRECTIONS if anchor_rows[direction]["doublet_coupling"]]
    o28_consistent = False
    if o28 is not None:
        exact_by_r0 = {Fraction(row["r0"]): row for row in o28.get("exact_rows", [])}
        shared = [row for row in per_direction["O28_B01_unique_Hdag_Sigma2_Sigmadag"] if row["r0"] in exact_by_r0]
        o28_consistent = bool(shared) and all(
            row["theta_sigma_squared_per_unit_c"] == exact_by_r0[row["r0"]]["theta_sigma_squared_over_c2_r0_4"] * row["r0"] ** 4
            and row["light_mass_shift_per_unit_c2"] == exact_by_r0[row["r0"]]["light_mass_shift_over_c2_r0_4"] * row["r0"] ** 4
            for row in shared
        )
    all_rows = [row for rows in per_direction.values() for row in rows]
    schurs = list(schur_by_r0.values())
    checks = {
        "every_direction_lattice_bound_with_pinned_blocks_powers_and_hypercharge_source": bool(binding["bound"]),
        "general_solver_reproduces_O28_alone_exactly": o28_consistent,
        "heavy_blocks_positive_definite_every_direction": all(schur["heavy_components_positive_definite"] for schur in schurs),
        "heavy_systems_nonsingular_every_direction": all(schur["heavy_systems_nonsingular"] for schur in schurs),
        "heavy_components_avoid_the_H_block": all(schur["heavy_components_avoid_H"] for schur in schurs),
        "triplet_and_doublet_schur_blocks_decouple_exactly": all(schur["triplet_doublet_schur_blocks_decoupled"] for schur in schurs),
        "schur_complements_phase_independent_exactly": all(
            row["doublet_schur_phase_independent"] and row["triplet_schur_phase_independent"] for row in all_rows
        ),
        "admixture_uniform_over_doublet_and_re_im_every_direction": all(row["uniform_over_Re_H_6_9_and_re_im"] for row in all_rows),
        "re_im_admixtures_orthogonal_every_direction": all(row["re_im_admixtures_orthogonal"] for row in all_rows),
        "gram_symmetric_every_direction": all(row["gram_symmetric"] for row in all_rows),
        "sigma_admixture_gram_is_2_theta2_times_source_projector": all(
            row["sigma_admixture_gram_equals_2_theta2_times_source_projector"] for row in all_rows
        ),
        "only_O45_B01_lacks_a_doublet_coupling": {
            row["direction"] for row in all_rows if not row["doublet_coupling"]
        } == {"O45_B01_Phi2_Hdag_Sigma_210_1050"},
        "every_direction_couples_the_colour_triplets": all(row["colour_triplet_coupling"] for row in all_rows),
        "colour_radii_exactly_bracketed": all(row["colour_radius_exact_bracket"] for row in all_rows),
        "yukawa_machinery_reproduces_sigma_std_nuc_nuc": all(schur["sigma_std_yukawa_pairs"] == ["nuc-nuc"] for schur in schurs),
        "induced_126bar_vev_up_type_only_every_direction_every_r0": all(
            row["induced_126bar_vev_up_type_only"] and row["induced_lepton_over_quark_modulus_3"]
            for row in all_rows
            if row["direction"] in coupled_all
        ),
        "saddle_for_every_nonzero_c_every_doublet_coupled_direction": all(
            row["saddle_for_every_c_nonzero"] for row in all_rows if row["direction"] in coupled_all
        ),
        "repository_scales_present": repository_scales_complete(scales) and set(bounds) == set(EXPECTED_REPOSITORY_SCALES),
        "every_H_linear_portal_theta_below_1e-3_at_every_repository_r0": bool(bounds)
        and all(row["theta_up_type_max_box_triangle_bound"] < PORTAL_THETA_THRESHOLD for row in bounds.values()),
        "portal_immune_tests_excluded_at_every_repository_r0": bool(bounds)
        and all(
            row["portal_immune_tests_min_pull_conservative_sigma"] is not None
            and row["portal_immune_tests_min_pull_conservative_sigma"] >= NOGO_PULL_THRESHOLD
            for row in bounds.values()
        ),
    }
    anchor_row = bounds.get(ANCHOR_SCALE_KEY, {})
    o15 = "O15_B01_Phi_Hdag_Sigma"
    findings = {
        "portal_fix_excluded_at_anchor_chain_r0": bool(anchor_row.get("portal_fix_excluded", False)),
        "portal_fix_excluded_at_every_repository_r0": bool(bounds) and all(row["portal_fix_excluded"] for row in bounds.values()),
        "portal_fix_not_excluded_at": sorted(key for key, row in bounds.items() if not row["portal_fix_excluded"]),
        "down_type_and_charged_lepton_masses_untouched_by_every_portal_combination": bool(
            checks["induced_126bar_vev_up_type_only_every_direction_every_r0"]
        ),
        "t_b_bound_survives_portal_set_at_every_repository_r0": bool(bounds)
        and all(row["t_b_bound_survives_portal_set"] for row in bounds.values()),
        "tan_beta_reaches_m_t_over_m_b_colour_stable_with": {
            key: row["tan_beta_reaches_m_t_over_m_b_colour_stable_with"] for key, row in bounds.items()
        },
        "tan_beta_reaches_m_t_over_m_b_in_box_with": {key: row["tan_beta_reaches_m_t_over_m_b_in_box_with"] for key, row in bounds.items()},
        "O15_frees_tan_beta_only_beyond_its_colour_radius": bool(bounds)
        and all(o15 in row["tan_beta_reaches_m_t_over_m_b_in_box_with"] and o15 not in row["tan_beta_reaches_m_t_over_m_b_colour_stable_with"]
                for row in bounds.values()),
        "colour_radius_below_4pi": {
            key: sorted(direction for direction, radius in row["colour_radius"].items() if radius is not None and radius < PORTAL_BOX)
            for key, row in bounds.items()
        },
    }
    return {
        "scope_note": (
            "all five H-linear directions at the certified vacuum q0 on the full H block (colour triplets Re/Im H_0..5 and "
            "doublets Re/Im H_6..9) and every non-H block they couple to (Phi, Sigma; S and Phi17 are not reached).  The "
            "Hessian of V + sum c_k O_k at q0 is exactly [[H_HH, B(c)^T], [B(c), A]] (the portals have only H x non-H "
            "blocks there and A does not depend on c), so its Schur complement on the H block, H_HH - sum c_k c_l G[k, l], "
            "is O(c^2) (exactly quadratic in c) and decides the second-order stability of q0 by Haynsworth inertia "
            "additivity; the light eigenvalues and the heavy admixture agree with it to O(c^2) (first order in c for the "
            "admixture).  |c_d| <= 4 pi for the complex coefficient of each direction (|c_d|^2 = c_re^2 + c_im^2); the "
            "combined admixture obeys the triangle inequality theta <= sum_d |c_d| theta_d"
        ),
        "lattice_binding": binding,
        "r0_values": r0_values,
        "per_direction": per_direction,
        "theta_up_type_max_box_at_physical_r0": anchor_theta,
        "colour_stable_region": {
            "per_direction": (
                "the colour-triplet Schur block is H_TT - |c_d|^2 G_d (phase independent, exact); q0 has no colour-triplet "
                "negative mode iff |c_d| <= rho_d, rho_d = 1/sqrt(lambda_max(H_TT^-1/2 G_d H_TT^-1/2)), bracketed exactly "
                "by the inertia of H_TT - t G_d at t = (1 -+ 1e-6) rho_d^2"
            ),
            "inner_certificate_any_combination": (
                "sum_d |c_d|/rho_d <= 1 implies H_TT - Q_T(c) >= 0 (Minkowski: ||A^-1/2 B_T(c) v|| <= sum_d |c_d| "
                "||A^-1/2 B_T,d v|| <= (sum_d |c_d|/rho_d) sqrt(v^T H_TT v))"
            ),
            "outer_certificate_any_combination": OUTER_CERTIFICATE_TEXT,
            "compensation": (
                "raising O06 by eps shifts every H level (triplets and doublets) by eps.  eps = the doublet Schur shift "
                "(O(c^2 r0^2), at most eps_max_O06_compensation_in_box) restores the doublet sector and keeps the "
                "doublet light; it enlarges each colour radius by at most sqrt(1 + eps) (H_TT(eps) <= (1 + eps) H_TT(0)), "
                "so O06 cannot remove a colour tachyon: any larger eps makes the doublet GUT-heavy.  Beyond rho_d the "
                "H-triplet level (from O46, (3/5) I_1 - I_54, relative to the doublet) or the heavy (3,1)_1/3 levels must "
                "be raised by the factor (|c_d|/rho_d)^2, which changes the certified benchmark coefficient map.  Either "
                "way (and for every portal c != 0, which makes q0 a saddle of V + c O) the SOS27 identity no longer "
                "certifies the vacuum: a new G3 certificate is required (Route A)"
            ),
        },
        "selection_rule": (
            "exact at the physical member and at every repository r0: the doublet columns of O15, O28 and O45_B02 "
            "annihilate the Y = -1/2 (5bar) component of the 10_H doublets and those of O38 the Y = +1/2 (5) component "
            "(integer lattice); the Sigma admixture Gram is 2 theta_Re^2 times the projector onto the coupled component, so "
            "theta(tan beta) = sqrt(2 t^2/(1 + t^2)) theta_Re (O15, O28, O45_B02) or sqrt(2/(1 + t^2)) theta_Re (O38) with "
            "t = |5|/|5bar| (theta <= sqrt(2) theta_Re for every tan beta); and for every portal parameter and every doublet "
            "column the induced 126bar vev couples only the up-type structures Q u^c and L nu^c (entries u u^c, d u^c, "
            "nu nu^c, e nu^c; lepton/quark modulus 3), never Q d^c or L e^c (exact Gaussian-rational 16.16 bilinears; the "
            "same machinery couples sigma_std only to nu^c nu^c).  So M_d and M_e keep only their 10_H parts, M_e = phase "
            "x M_d^T, for every combination of the five portals at any coefficient (first order in v, tree level)"
        ),
        "repository_r0_bounds": bounds,
        "findings": findings,
        "reading": (
            "The full H block changes the picture of the doublet-only analysis in two ways.  (i) Colour: O15 couples the "
            "H triplets to the 126bar (6,1,1) through <Phi> = p at O(1), so q0 acquires GUT-scale (3,1)_|Y|=1/3 tachyons "
            "for |c_O15| > rho_O15 ~ 0.79 (r0-independent), well before O15 can move tan beta to m_t/m_b; O28 is "
            "colour-limited to |c| <= rho_O28 ~ 1/r0 (below 4 pi at the 2HDM-content r0); O38 and O45 are colour-stable "
            "in the box.  O45_B02 still moves tan beta past m_t/m_b inside the colour-stable region (the doublet saddle it "
            "creates is cured by O06), so the O28-alone t-b bound does not survive the portal set.  (ii) Flavour: every "
            "portal-induced 126bar (15,2,2) vev is purely up-type (exact selection rule), so M_e = phase x M_d^T survives "
            "every portal combination and the tan-beta-independent (m_s/m_d)/(m_mu/m_e) and (m_b/m_s)/(m_tau/m_mu) "
            "exclusions stand: no in-contract H-linear portal repair survives at any repository r0 at q0.  Any "
            "doublet-coupled portal makes q0 a saddle, so a flavour-repairing branch would need a new G3 certificate in "
            "any case (Route A)"
        ),
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# (G) Seesaw with M_D = M_u (float, not load-bearing).
# ---------------------------------------------------------------------------


def _pmns(s12sq: float, s23sq: float, s13sq: float, delta: float, alpha21: np.ndarray, alpha31: np.ndarray) -> np.ndarray:
    s12, s23, s13 = math.sqrt(s12sq), math.sqrt(s23sq), math.sqrt(s13sq)
    c12, c23, c13 = math.sqrt(1 - s12sq), math.sqrt(1 - s23sq), math.sqrt(1 - s13sq)
    delta = np.asarray(delta, dtype=float)
    e = np.exp(-1j * delta)
    shape = np.broadcast(delta, alpha21, alpha31).shape
    u = np.zeros(shape + (3, 3), dtype=complex)
    u[..., 0, 0] = c12 * c13
    u[..., 0, 1] = s12 * c13
    u[..., 0, 2] = s13 * e
    u[..., 1, 0] = -s12 * c23 - c12 * s23 * s13 / e
    u[..., 1, 1] = c12 * c23 - s12 * s23 * s13 / e
    u[..., 1, 2] = s23 * c13
    u[..., 2, 0] = s12 * s23 - c12 * c23 * s13 / e
    u[..., 2, 1] = -c12 * s23 - s12 * c23 * s13 / e
    u[..., 2, 2] = c23 * c13
    phases = np.stack(np.broadcast_arrays(np.ones(shape), np.exp(0.5j * np.asarray(alpha21)), np.exp(0.5j * np.asarray(alpha31))), axis=-1)
    return u * phases[..., None, :]


def _light_masses(ordering: str, lightest: np.ndarray, osc: Mapping[str, float]) -> np.ndarray:
    dm21 = osc["dm21sq_eV2"]
    dm3l = abs(osc["dm3l_sq_eV2"])
    lightest = np.asarray(lightest, dtype=float)
    if ordering == "normal":
        return np.stack([lightest, np.sqrt(lightest**2 + dm21), np.sqrt(lightest**2 + dm3l)], axis=-1)
    m2 = np.sqrt(lightest**2 + dm3l)
    return np.stack([np.sqrt(m2**2 - dm21), m2, lightest], axis=-1)


def _max_lightest(ordering: str, osc: Mapping[str, float], total: float) -> float:
    low, high = 0.0, total
    for _ in range(200):
        mid = 0.5 * (low + high)
        if float(np.sum(_light_masses(ordering, np.array(mid), osc))) > total:
            high = mid
        else:
            low = mid
    return low


def _largest_rh_mass(dirac: np.ndarray, ordering: str, osc: Mapping[str, float], lightest: np.ndarray, delta: np.ndarray,
                     alpha21: np.ndarray, alpha31: np.ndarray) -> np.ndarray:
    """sigma_max(M_R) in GeV for M_R = D m_nu^-1 D, m_nu^-1 = U diag(1/m) U^T (m in eV -> GeV)."""
    masses = _light_masses(ordering, lightest, osc) * 1.0e-9
    u = _pmns(osc["s12sq"], osc["s23sq"], osc["s13sq"], delta, alpha21, alpha31)
    inverse = np.einsum("...ik,...k,...jk->...ij", u, 1.0 / masses, u)
    mr = dirac[:, None] * inverse * dirac[None, :]
    return np.linalg.svd(mr, compute_uv=False)[..., 0]


def seesaw_section(data: Mapping[str, Any] = DATA, *, n_random: int = 4000, n_starts: int = 6, seed: int = 20260925) -> dict[str, Any]:
    osc_all = data["neutrino_oscillation"]
    scales = scale_band((1.0e10, 1.0e11, 1.0e12))
    running = run_sm_masses(sorted(set(scales.values())), data)
    rng = np.random.default_rng(seed)
    rows = {}
    for label, v_r in sorted(scales.items(), key=lambda item: item[1]):
        m = running[v_r]
        dirac = np.array([m["u"], m["c"], m["t"]])
        generic = m["t"] ** 2 / (math.sqrt(osc_all["normal"]["dm3l_sq_eV2"]) * 1.0e-9) / v_r
        generic_lepton = m["tau"] ** 2 / (math.sqrt(osc_all["normal"]["dm3l_sq_eV2"]) * 1.0e-9) / v_r
        per_order = {}
        for ordering in ("normal", "inverted"):
            osc = osc_all[ordering]
            m_max = _max_lightest(ordering, osc, osc_all["sum_mnu_max_eV"])
            lightest = 10.0 ** rng.uniform(-4.0, math.log10(m_max), n_random)
            delta = rng.uniform(0.0, 2.0 * math.pi, n_random)
            a21 = rng.uniform(0.0, 2.0 * math.pi, n_random)
            a31 = rng.uniform(0.0, 2.0 * math.pi, n_random)
            y = _largest_rh_mass(dirac, ordering, osc, lightest, delta, a21, a31) / v_r

            def objective(params: np.ndarray, osc: Mapping[str, float] = osc, ordering: str = ordering, m_max: float = m_max) -> float:
                lightest_value = m_max / (1.0 + math.exp(-params[0]))
                value = _largest_rh_mass(dirac, ordering, osc, np.array(max(lightest_value, 1.0e-7)), np.array(params[1]),
                                         np.array(params[2]), np.array(params[3]))
                return math.log(float(value))

            best = math.inf
            order = np.argsort(y)[:n_starts]
            for index in order:
                start = np.array([math.log(lightest[index] / max(m_max - lightest[index], 1.0e-12)), delta[index], a21[index], a31[index]])
                result = minimize(objective, start, method="Nelder-Mead", options={"xatol": 1.0e-7, "fatol": 1.0e-9, "maxiter": 2000})
                best = min(best, math.exp(result.fun) / v_r)
            per_order[ordering] = {
                "lightest_mass_max_eV": m_max,
                "median_Y_R": float(np.median(y)),
                "fraction_Y_R_below_sqrt_4pi": float(np.mean(y <= PERTURBATIVE_LIMIT)),
                "minimum_Y_R_found": min(best, float(np.min(y))),
            }
        rows[label] = {
            "v_R_GeV": v_r,
            "m_u_m_c_m_t_at_v_R_GeV": [m["u"], m["c"], m["t"]],
            "generic_Y_R": generic,
            "generic_Y_R_if_MD_has_charged_lepton_singular_values": generic_lepton,
            **per_order,
        }
    generic_nonperturbative = all(row["generic_Y_R"] > PORTAL_BOX for row in rows.values())
    escape = any(row[o]["minimum_Y_R_found"] <= PERTURBATIVE_LIMIT for row in rows.values() for o in ("normal", "inverted"))
    return {
        "assumptions": (
            "type-I only (the type-II-capable H-Sigma quartics O35 and the 5/5bar-splitting O31 vanish in the benchmark); "
            "v_R = M_I; M_D = M_u = diag(m_u, m_c, m_t)(v_R) in the common flavour basis (M_e, M_d, M_u, M_D aligned on "
            "the witness); only the nu^c of the three light families (nu^c-vectorlike mixing through the S and Phi17 vevs "
            "is neglected); m_nu = -M_D^T M_R^-1 M_D, so M_R = -M_D m_nu^-1 M_D^T; oscillation data NuFIT 5.2, "
            "sum m_nu < 0.12 eV; the RG running of m_nu below v_R (a factor ~1.2-1.4) is ignored; Y_R = sigma_max(M_R)/v_R.  "
            "M_D = M_u(data) is the generic SO(10) premise, not a prediction of the witness: on the witness M_D = phase "
            "M_u^T and M_u has the singular values of M_e = M_d (tan beta = 1), for which the generic Y_R ~ "
            "m_tau^2/(sqrt(dm31^2) v_R) ~ 0.06 at 1e12 GeV (column generic_Y_R_if_MD_has_charged_lepton_singular_values)"
        ),
        "generic_estimate": "Y_R ~ m_t(v_R)^2/(sqrt(dm31^2) v_R) if M_D = M_u(data); m_tau(v_R)^2/(sqrt(dm31^2) v_R) if "
        "M_D has the charged-lepton singular values",
        "rows": rows,
        "generic_requires_nonperturbative_Y_R_everywhere_if_MD_equals_Mu_data": generic_nonperturbative,
        "textured_escape_exists_somewhere_in_band": escape,
        "load_bearing": False,
        "reading": (
            "If M_D = M_u(data), a generic Y_126 needs Y_R = O(10^2 - 10^4) (non-perturbative) across the band; a "
            "textured Y_126 with (m_nu^-1)_tautau ~ 0 lowers the requirement, and where the scan finds perturbative "
            "minima the seesaw alone is not a no-go.  With the witness's own M_D (charged-lepton singular values) the "
            "generic Y_R is perturbative.  So 'the seesaw needs Y_126 ~ 10^2-10^3' is a statement about the M_D = M_u "
            "premise, not about the witness.  The no-go of this certificate rests on the charged sector (sections B-E), "
            "not on the seesaw."
        ),
    }


# ---------------------------------------------------------------------------
# (H) Upstream artifacts (fail closed) and the report.
# ---------------------------------------------------------------------------


def upstream_section(candidate_report: Mapping[str, Any] | None = None, hessian_report: Mapping[str, Any] | None = None) -> dict[str, Any]:
    cand = candidate_report if candidate_report is not None else json.loads(CANDIDATE_JSON.read_text(encoding="utf-8"))
    hess = hessian_report if hessian_report is not None else json.loads(EXACT_HESSIAN_JSON.read_text(encoding="utf-8"))
    checks = {
        "candidate_status_and_zero_failures": cand.get("status") == CANDIDATE_STATUS and cand.get("n_failed") == 0,
        "candidate_H_linear_portals_are_zero": _dig(cand, "checks", "H_linear_portals_are_zero") is True,
        "candidate_light_doublet_equal_5_5bar": _dig(cand, "checks", "light_doublet_is_equal_5_5bar_mixture") is True,
        "candidate_kernel_symmetry_plus_light_doublet_float": _dig(cand, "checks", "hessian_psd_with_kernel_symmetry_plus_light_doublet") is True,
        "exact_hessian_certified": hess.get("status") == EXACT_HESSIAN_STATUS and hess.get("n_failed") == 0,
        "exact_hessian_kernel_orbit_plus_doublet": _dig(hess, "flags", "kernel_equals_35_symmetry_tangents_plus_4_light_doublet") is True,
        "candidate_r0_physical_matches": _dig(cand, "hierarchy", "r0_physical") == str(physical_r0()),
    }
    return {
        "candidate_status": cand.get("status"),
        "exact_hessian_status": hess.get("status"),
        "checks": checks,
    }


ROUTES = {
    "A": (
        "New in-contract G3 branch: a vacuum in which a DOWN-type doublet from the 126bar (15,2,2) has a nonzero admixture "
        "theta_d in the light doublet, large enough that theta_d ||Y_F|| v reaches the required d-e / s-mu / b-tau "
        "splittings (theta_d ||Y_F|| ~ 1e-4 at M_I for s-mu; far below O(1) for perturbative Y_F).  At the certified q0 "
        "this is impossible at every repository r0 (sections F and F'): theta_d = 0 exactly, because every "
        "H-linear portal (O15, O28, O38, O45) feeds only the up-type (15,2,2) (exact Yukawa selection rule), so M_e = "
        "phase x M_d^T survives any portal combination; the portals are also colour-limited (|c_O15| <= ~0.79 at every "
        "r0, |c_O28| <= rho_O28(r0) ~ 1/r0, 4.5 at the 2HDM-content r0) and every doublet-coupled portal makes q0 a saddle "
        "(SOS27 needs portal = 0; O06 cures only the doublet saddle).  A Route A branch must therefore leave q0 (other "
        "vevs, or a (15,2,2) near M_I with a down-type mixing channel), keep the colour triplets non-tachyonic, and needs "
        "new exact G3/G4/G5 certificates; it may not exist and reopens the 2HDM proton-decay and high-v_R Higgs-matching "
        "risks."
    ),
    "B": (
        "Extension beyond the declared contract: a 120_H, a second 10_H, or a UV completion that generates "
        "F.F.H10^*.S^* (U(1)_X allows it at dimension five).  Changes models/SO10Z17AxionV20.m; G1-G5 restart."
    ),
    "C": "Record this no-go (this artifact) and leave G8 OPEN on the current witness branch.",
}


def _all_checks(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, bool]:
    output = {}
    for prefix, section in sections.items():
        for key, value in section.get("checks", {}).items():
            output[f"{prefix}.{key}"] = bool(value)
    return output


def build_report(
    *,
    model_text: str | None = None,
    coefficient_overrides: Mapping[str, Fraction] | None = None,
    doublet_vev: Mapping[int, sympy.Expr] | None = None,
    data: Mapping[str, Any] | None = None,
    candidate_report: Mapping[str, Any] | None = None,
    hessian_report: Mapping[str, Any] | None = None,
    seesaw_samples: int = 4000,
) -> dict[str, Any]:
    started = time.time()
    data = DATA if data is None else data
    contract = contract_section(model_text)
    portal = portal_section(coefficient_overrides)
    spinor = spinor_section(doublet_vev)
    structure = flavour_structure_section(spinor)
    comparison = data_section(data)
    o28 = o28_section(data)
    portals = portals_section(data, o28=o28, comparison=comparison)
    seesaw = seesaw_section(data, n_random=seesaw_samples)
    upstream = upstream_section(candidate_report, hessian_report)
    sections = {
        "contract": contract,
        "light_doublet": portal,
        "spinor": spinor,
        "flavour_structure": structure,
        "data": comparison,
        "O28_fix": o28,
        "H_linear_portals": portals,
        "upstream": upstream,
    }
    checks = _all_checks(sections)
    failures = sorted(key for key, value in checks.items() if not value)
    excluded = not failures
    portal_checks_pass = all(value for key, value in checks.items() if key.startswith("H_linear_portals."))
    findings = portals["findings"]
    stable_reach = findings["tan_beta_reaches_m_t_over_m_b_colour_stable_with"]
    flags = {
        "witness_branch_flavour_excluded_at_renormalizable_tree_level": excluded,
        "light_doublet_pure_10H_exact": all(value for key, value in checks.items() if key.startswith("light_doublet.")),
        "no_induced_heavy_doublet_vev_at_tree_level": bool(portal["checks"]["potential_even_in_H_on_the_witness"]),
        "flavour_relations_exact": all(value for key, value in checks.items() if key.startswith(("spinor.", "flavour_structure.", "contract."))),
        "data_exclusion_many_sigma": all(value for key, value in checks.items() if key.startswith("data.")),
        "O28_alone_fix_excluded": all(value for key, value in checks.items() if key.startswith("O28_fix.")),
        "O28_alone_b_tau_repairable": bool(o28["findings"]["b_tau_repairable_by_O28"]),
        "O28_portal_breaks_SOS27_certificate": bool(o28["checks"]["saddle_for_every_nonzero_c_at_every_r0"]),
        "every_doublet_coupled_portal_breaks_SOS27_certificate": bool(
            portals["checks"]["saddle_for_every_nonzero_c_every_doublet_coupled_direction"]
        ),
        "colour_stable_region_computed_on_full_H_block": bool(
            portals["checks"]["colour_radii_exactly_bracketed"]
            and portals["checks"]["triplet_and_doublet_schur_blocks_decouple_exactly"]
            and portals["checks"]["every_direction_couples_the_colour_triplets"]
        ),
        "O28_colour_radius_below_4pi_at_some_repository_r0": bool(o28["findings"]["colour_radius_below_4pi_at"]),
        "O15_frees_tan_beta_only_beyond_its_colour_radius": bool(findings["O15_frees_tan_beta_only_beyond_its_colour_radius"]),
        "O45_B02_frees_tan_beta_inside_colour_stable_region": bool(stable_reach)
        and all("O45_B02_Phi2_Hdag_Sigma_210_1050" in value for value in stable_reach.values()),
        "portal_induced_126bar_vev_up_type_only_exact": bool(
            portals["checks"]["induced_126bar_vev_up_type_only_every_direction_every_r0"]
        ),
        "M_e_equals_phase_M_d_transpose_for_every_portal_combination": bool(
            portal_checks_pass and findings["down_type_and_charged_lepton_masses_untouched_by_every_portal_combination"]
        ),
        "H_linear_portal_fix_excluded_at_anchor_chain_r0": bool(
            portal_checks_pass and findings["portal_fix_excluded_at_anchor_chain_r0"]
        ),
        "H_linear_portal_fix_excluded_at_every_repository_r0": bool(
            portal_checks_pass and findings["portal_fix_excluded_at_every_repository_r0"]
        ),
        "O28_alone_t_b_bound_survives_other_portals": bool(findings["t_b_bound_survives_portal_set_at_every_repository_r0"]),
        "seesaw_generic_nonperturbative_if_MD_equals_Mu_data": bool(
            seesaw["generic_requires_nonperturbative_Y_R_everywhere_if_MD_equals_Mu_data"]
        ),
        "seesaw_textured_escape_exists": bool(seesaw["textured_escape_exists_somewhere_in_band"]),
        "seesaw_load_bearing": False,
        "route_C_recorded": excluded,
        "G8_closed": False,
        "falsifies_G3_G5_scalar_vacuum_certificates": False,
        "falsifies_so10_contract": False,
    }
    report: dict[str, Any] = {
        "module": "g8_sm_pati_salam_flavour_nogo_v20",
        "model_contract_id": MODEL_CONTRACT_ID,
        "status": STATUS_RECORDED if excluded else STATUS_INCOMPLETE,
        "overall_state": OVERALL_STATE_RECORDED if excluded else OVERALL_STATE_OPEN,
        "G8_status": "OPEN",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "flags": flags,
        "witness": {
            "vacuum": "(Phi, H, Sigma, S, Phi17) = (p, 0, r0 sigma_std, r0, x0), kappa = -r0/4, O06 = 2|kappa| r0",
            "benchmark_r0": R0,
            "anchor_r0": physical_r0(),
            "source": "g3_sm_pati_salam_candidate_v20 / g3_sm_pati_salam_exact_hessian_v20",
        },
        "contract": contract,
        "light_doublet": portal,
        "spinor": spinor,
        "flavour_structure": structure,
        "data": comparison,
        "O28_fix": o28,
        "H_linear_portals": portals,
        "seesaw": seesaw,
        "upstream": upstream,
        "routes": ROUTES,
        "scope": {
            "proved_exactly": [
                "the H-linear directions of the 44-direction contract are exactly O15, O28, O38, O45_B01, O45_B02 (census "
                "orbit keys) and all ten re/im parameters vanish in the benchmark map for every r0, x0 (sympy)",
                "exact Hessian (Fraction binding units) at r0 = 1/5, 1/20, 1/100 and the anchor r0: zero gradient, H block "
                "decoupled and equal to diag(2, 2 + 2 r0^2 | 0, 2 r0^2) (u coords), Re H_6..9 exact null vectors: the light "
                "doublet is pure 10_H with zero 126bar (15,2,2) and zero 210 admixture",
                "V is even in H on the witness (live H-degrees {0, 1, 2, 4}, H-linear parameters zero), so no heavy "
                "doublet (126bar (15,2,2), 210 doublets) gets an induced vev at any order in v at tree level (the SU(2)_L "
                "centre -1 composed with H -> -H fixes q0 + h and acts as -1 on every heavy doublet)",
                "the allowed 16bar x 16 coupling pattern has generic rank 8 (exact rank at deterministic integer "
                "couplings; kernel of dimension 3 in span{F, P, Q, R}): exactly three light families for generic couplings",
                "Gaussian-integer Clifford algebra: 16x16 = 10 + 120 + 126, 16x16bar = 1 + 45 + 210; the 16.16.10 Clebsches "
                "at the real neutral vev a e8 + b e9 have |c_f|^2 = a^2 + b^2 for u, d, e, nu (tan beta = 1), constant "
                "phases nu/u and e/d; sigma_std couples only nu^c nu^c; the (15,2,2) lepton/quark Clebsch is -3",
                "contract enumeration from the SARAH model file: no 16.16.10_H^* coupling, H10/126bar Yukawas only on the "
                "X = 1 sixteens, 16.16bar masses only from SO(10) singlets, no 120_H",
                "flavour structure (sympy): M_u M_u^dag = M_d M_d^dag, M_e = phase M_d^T, M_D = phase M_u^T",
                "O28 alone: lattice-bound H-Sigma block (+-192 r0^2), exact first-order admixture theta^2 = c^2 r0^4 R(r0) "
                "with R = 7962624 (13 r^2+6)^2/(13 r^4+12 r^2+36)^2 (derived from 3 exact points, re-checked at 2, and "
                "matched exactly by the first-order solve at 8 r0 values including the anchor and the 4 repository r0), "
                "O(c^2) (exactly quadratic) negative doublet Schur complement (saddle) for every c != 0",
                "all five H-linear portals on the full H block (colour triplets and doublets): all twenty H columns bound "
                "to the (1/6) Z lattice with pinned blocks and r0 powers, exact heavy responses, exact Schur Grams (the "
                "triplet and doublet blocks decouple, both are phase independent) at the physical member and the 4 "
                "repository r0; every doublet-coupled portal makes q0 a saddle for c != 0; O45_B01 has no doublet coupling "
                "but, like every portal, couples the colour triplets",
                "colour-stable radii: H_TT - t G_d has no negative eigenvalue at t = (1 - 1e-6) rho_d^2 and one at "
                "(1 + 1e-6) rho_d^2 (exact inertia, per direction and r0)",
                "selection rule: O15, O28, O45_B02 act only on the Y = +1/2 doublet component, O38 only on Y = -1/2 "
                "(integer lattice); the Sigma admixture Gram is 2 theta_Re^2 times the coupled-component projector "
                "(theta(tan beta) exact up to the float t); and every portal-induced 126bar vev couples only Q u^c and "
                "L nu^c (exact 16.16 bilinears), so M_e = phase x M_d^T for every portal combination at any coefficient",
            ],
            "float_diagnostics": [
                "data comparison: PDG/FLAG/XZZ inputs, one-loop SM running, pulls (raw and with a 10% theory term)",
                "O28 bounds at the repository r0 values: theta at |c| = 4 pi and in the colour-stable range, tan beta of "
                "the lightest eigenvector of the O(c^2) doublet Schur complement (eigh, phase scan), and the Mirsky t-b "
                "requirement",
                "colour radii rho_d (eigvalsh of the exact triplet Grams; bracketed exactly), the O06-compensated upper "
                "radius, and the outer bound on each |c_d| for any combination (Cauchy-Schwarz with the others in the box)",
                "portal-set bounds: up-type theta_(15,2,2) <= sum_d |c_d| sqrt(2) theta_d (box and colour-stable), the "
                "portal-immune data pulls, and tan beta scans per direction over |c| in (0, 4 pi] and over the colour-stable "
                "range, and the phase of c",
                "seesaw: generic Y_R and a scan (random + Nelder-Mead) of textured Y_126",
                "the O28 and portal lattice bindings compare the compiler's float64 Hessian with the (1/6)-integer patterns",
            ],
            "cited_or_hand_argued": [
                "electroweak breaking proceeds along the light doublet Re H_6..9 (the only light scalar with doublet "
                "quantum numbers; the certified eps >= 0 family itself leaves SU(2)_L x U(1)_Y unbroken)",
                "the light-state lemma: 16bar components are heavy (generic rank 8 certified; rank 8 at the physical "
                "couplings assumed: exactly three light families), heavy-light corrections O(v^2/M_V^2) are dimension >= 6",
                "no induced (10,3,1) (Delta_L) vev from EW breaking at tree level: the heavy-doublet part is proved (V even "
                "in H), the integer-isospin (10,3,1) part rests on the vanishing H-Sigma quartics O31/O35 (checked)",
                "SM running preserves Yukawa alignment (one-loop form Y g(Y^dag Y); U(1)^3 family symmetry to all orders)",
                "Mirsky's singular-value inequality; Haynsworth inertia additivity (the Schur complement on the H block "
                "decides the second-order stability of q0); the Minkowski and Cauchy-Schwarz inequalities of the "
                "combination certificates",
                "with portals on, the induced heavy vevs are the first-order (in v) response -A^-1 B(c) h v of the light "
                "doublet h; O(v^3/M^2) corrections are dimension >= 6",
                "Y_F (the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2)), the contract's declared Y126 "
                "and the seesaw Y_R differ by unfixed Clebsch normalisations; the O28-alone t-b bound is far above 4 pi, so "
                "this O(1) ambiguity does not matter",
            ],
            "not_claimed": [
                "no statement about the G3-G5 scalar-vacuum certificates or the SO(10) contract: they stand",
                "no loop-level flavour analysis (threshold corrections from 126bar remnants below M_I are O(Y_126^2/16 pi^2))",
                "the seesaw section is not a no-go (textured Y_126 can lower the requirement), and its non-perturbative "
                "generic Y_R assumes M_D = M_u(data), not the witness's own M_D",
                "the colour-stable region is the second-order (Hessian) region at q0 with the certified couplings; global "
                "minimality with any portal on is not certified (a new G3 certificate would be needed); tan beta is freed "
                "inside it by O45_B02, so the O28-alone t-b bound is not a statement about the portal set",
                "no analysis away from q0 (a vacuum with a light or down-type-mixing (15,2,2) is Route A)",
                "G8 is not closed; Route A or B is required to reach it",
            ],
        },
        "runtime_seconds": 0.0,
        "verdict": "",
    }
    report["verdict"] = _verdict(report)
    report["runtime_seconds"] = time.time() - started
    return report


def _verdict(report: Mapping[str, Any]) -> str:
    if report["n_failed"]:
        return (
            "The Route C flavour no-go is NOT recorded: " + ", ".join(report["failures"]) + ".  G8 stays OPEN and no "
            "statement about the witness branch's flavour sector is made (fail closed)."
        )
    data = report["data"]
    o28 = report["O28_fix"]
    t_b_min = min(row["t_b_split_requires_Y_F_at_least"] for row in o28["repository_r0_bounds"].values())
    portals = report["H_linear_portals"]
    bounds = portals["repository_r0_bounds"]
    findings = portals["findings"]
    o15 = "O15_B01_Phi_Hdag_Sigma"
    o28_key = "O28_B01_unique_Hdag_Sigma2_Sigmadag"
    rho15 = min(row["colour_radius"][o15] for row in bounds.values())
    rho28 = {key: row["colour_radius"][o28_key] for key, row in bounds.items()}
    below = o28["findings"]["colour_radius_below_4pi_at"]
    rho28_text = ", ".join(f"{rho28[key]:.3g} at {key}" for key in sorted(rho28, key=lambda item: rho28[item]))
    immune = min(row["portal_immune_tests_min_pull_conservative_sigma"] for row in bounds.values())
    immune_raw = min(row["portal_immune_tests_min_pull_raw_sigma"] for row in bounds.values())
    stable_reach = sorted({direction for row in bounds.values() for direction in row["tan_beta_reaches_m_t_over_m_b_colour_stable_with"]})
    t_b_text = (
        "; inside it " + " and ".join(stable_reach) + " still moves tan beta past m_t/m_b (O15 only beyond its colour "
        "radius), so the O28-alone t-b bound does not survive the portal set"
        if stable_reach
        else "; no portal moves tan beta to m_t/m_b inside the colour-stable region"
    )
    excluded_text = (
        "no in-contract H-linear portal repair of the flavour sector survives at any repository r0"
        if findings["portal_fix_excluded_at_every_repository_r0"]
        else "the portal fix is NOT excluded at " + ", ".join(findings["portal_fix_not_excluded_at"])
    )
    seesaw = report["seesaw"]
    return (
        "On the SM Pati-Salam G3 witness branch (renormalizable 27-parameter benchmark family, H-linear portals zero) "
        "the light Higgs doublet is exactly the 10_H direction Re H_6..9 and, with the contract's renormalizable Yukawas, "
        "M_u = c_u Y, M_d = c_d Y, M_e = c_e Y^T, M_D = c_nu Y^T with |c_u| = |c_d|: CKM = 1, m_t = m_b, m_d = m_e, "
        "m_s = m_mu, M_D = M_u, and the 126bar enters only M_R.  The tan-beta-independent tests are excluded by at least "
        f"{data['minimum_load_bearing_pull_raw_sigma']:.1f} sigma (experimental errors) and "
        f"{data['minimum_load_bearing_pull_conservative_sigma']:.1f} sigma (with a 10% theory term) across 1e9-2e16 GeV.  "
        "The O28 portal alone (the largest direct 10_H-(15,2,2) portal, other portals zero) gives theta = |c| r0^2 "
        f"sqrt(R(r0)) <= {o28['theta_max_at_anchor_abs_c_4pi']:.2e} at the anchor r0 with |c| <= 4 pi for the witness "
        f"doublet (<= {o28['theta_max_at_anchor_abs_c_4pi_any_tan_beta']:.2e} for any tan beta); its admixture is purely "
        f"up-type, so it cannot split b from tau at all, and repairing the t-b split needs ||Y_F|| >= {t_b_min:.0f} at "
        "every repository r0 inside the colour-stable range (Mirsky; Y_F the Yukawa of the canonically normalised (1,2,2) "
        "inside the (15,2,2)).  With all five H-linear portals on at q0, the full H block (colour triplets included) "
        f"gives the second-order colour-stable region: |c_O15| <= {rho15:.3f} at every repository r0 (the H triplets "
        "couple to the 126bar (6,1,1) through <Phi> at O(1); beyond it q0 has GUT-scale (3,1)_|Y|=1/3 tachyons), "
        f"|c_O28| <= rho_O28(r0) ~ 1/r0 ({rho28_text}; below 4 pi at {', '.join(below) or 'no repository r0'}), O38 and "
        "O45 colour-stable in the box; raising O06 cures only the doublet saddle (it lifts triplets and doublets alike "
        f"and the doublet must stay light){t_b_text}.  But every portal-induced 126bar (15,2,2) vev is purely up-type "
        "(exact: the induced 16.16 couplings are only Q u^c and L nu^c at every repository r0), so M_e = phase x M_d^T "
        "survives every portal combination at any coefficient and the portal-immune tests (m_s/m_d)/(m_mu/m_e) and "
        f"(m_b/m_s)/(m_tau/m_mu) stay excluded by >= {immune_raw:.1f} sigma ({immune:.1f} sigma with the theory term): "
        f"{excluded_text}.  Every doublet-coupled portal c != 0 turns the certified witness into a saddle (SOS27 needs "
        "portal = 0), so any repair needs a new G3 certificate (Route A).  If M_D = M_u(data) (the generic SO(10) "
        "premise, not the witness's own M_D), the seesaw needs a non-perturbative Y_126 for generic textures ("
        + ("a tuned texture can evade this, so it is not load-bearing" if seesaw["textured_escape_exists_somewhere_in_band"] else "no texture found evades it")
        + ").  Route C is recorded; G8 stays OPEN; the G3-G5 certificates and the SO(10) contract are not falsified."
    )


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _radius_text(value: Any) -> str:
    return "none" if value is None else f"{value:.4g}"


PORTAL_SHORT_NAMES = {
    "O15_B01_Phi_Hdag_Sigma": "O15",
    "O28_B01_unique_Hdag_Sigma2_Sigmadag": "O28",
    "O38_B01_Phi_Hdag_Sigmadag": "O38",
    "O45_B01_Phi2_Hdag_Sigma_210_1050": "O45_B01",
    "O45_B02_Phi2_Hdag_Sigma_210_1050": "O45_B02",
}


def _markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# G8 flavour no-go on the SM Pati-Salam G3 witness branch (Route C, v20)",
        "",
        f"- Status: `{report['status']}`",
        f"- Overall state: `{report['overall_state']}`; G8: **{report['G8_status']}**",
        f"- Checks: {report['n_checks'] - report['n_failed']}/{report['n_checks']} pass",
        "",
        "## Verdict",
        "",
        report["verdict"],
        "",
        "## (1) The light doublet is pure 10_H (exact)",
        "",
        f"- H-linear directions: {', '.join(report['light_doublet']['H_linear_directions'])} (all re/im parameters zero).",
        f"- Nonzero H-quadratic parameters: {', '.join(report['light_doublet']['nonzero_H_quadratic_parameters'])}.",
        "",
        "| r0 | gradient 0 | H block decoupled | H block = exact formula | Re H_6..9 null |",
        "|---|---|---|---|---|",
    ]
    for audit in report["light_doublet"]["exact_hessian_audits"]:
        lines.append(
            f"| {audit['r0']} | {audit['gradient_zero']} | {audit['H_rows_vanish_outside_H_block']} | "
            f"{audit['H_block_matches_exact_formula']} | {audit['Re_H_6_9_exact_null_vectors']} |"
        )
    spinor = report["spinor"]
    lines += [
        "",
        "## (2) Clebsches, contract couplings and flavour relations (exact)",
        "",
        f"- Clebsches at v = a e8 + b e9: {', '.join(f'{k} = {v}' for k, v in sorted(spinor['clebsch_at_vev'].items()))}.",
        f"- Moduli: all equal to a^2 + b^2 (tan beta = 1). sigma_std bilinear: {spinor['sigma_std_bilinear_entries']}.",
        f"- (15,2,2) relative lepton/quark Clebsch: {', '.join(v['lepton_over_quark_relative_clebsch'] for v in spinor['fifteen_two_two'].values())}.",
        f"- H10 Yukawas allowed: {', '.join(report['contract']['H10_yukawas'])}; 126bar Yukawas: {', '.join(report['contract']['Delta126bar_yukawas'])}; "
        f"16.16.conj[H10]: {report['contract']['conj_H10_yukawas'] or 'none'}.",
        f"- Allowed but undeclared renormalizable couplings: {', '.join(report['contract']['allowed_but_undeclared'])}.",
        f"- Predictions: {json.dumps(report['flavour_structure'].get('predictions', {}))}",
        "",
        "## Data comparison (float)",
        "",
        "| test | prediction | data | pull (raw) | pull (10% theory) |",
        "|---|---|---|---|---|",
    ]
    for row in report["data"]["tests_scale_free"]:
        lines.append(
            f"| {row['test']} | {row['prediction']} | {_fmt(row['data_value'])} | {_fmt(row['pull_raw_sigma'])} | "
            f"{_fmt(row['pull_conservative_sigma'])} |"
        )
    lines += ["", "| scale | (m_t/m_c)/(m_b/m_s) | (m_b/m_s)/(m_tau/m_mu) | m_t/m_b | m_b/m_tau |", "|---|---|---|---|---|"]
    for label, row in report["data"]["tests_per_scale"].items():
        lines.append(
            f"| {label} | {_fmt(row['(m_t/m_c)/(m_b/m_s)']['value'])} ({_fmt(row['(m_t/m_c)/(m_b/m_s)']['pull_conservative_sigma'])} sigma) | "
            f"{_fmt(row['(m_b/m_s)/(m_tau/m_mu)']['value'])} ({_fmt(row['(m_b/m_s)/(m_tau/m_mu)']['pull_conservative_sigma'])} sigma) | "
            f"{_fmt(row['m_t/m_b (tan beta = 1)']['value'])} | {_fmt(row['m_b/m_tau']['value'])} |"
        )
    lines += [
        "",
        f"Minimum load-bearing pull: {report['data']['minimum_load_bearing_pull_raw_sigma']:.1f} sigma (raw), "
        f"{report['data']['minimum_load_bearing_pull_conservative_sigma']:.1f} sigma (10% theory).",
        "",
        "## (3) The O28 portal alone (exact / parametric)",
        "",
        f"- {report['O28_fix']['scope_note']}.",
        f"- {report['O28_fix']['theta_formula']}.",
        f"- {report['O28_fix']['coefficient_box_note']}.",
        f"- Closed form derived: R(r) = {report['O28_fix']['closed_form']['R_theta_sigma_squared_over_c2_r4']}; "
        f"light-doublet shift = c^2 r^4 x {report['O28_fix']['closed_form']['light_mass_shift_over_c2_r4']}.",
        "",
        "| r0 | theta/(c r0^2) | shift/(c^2 r0^4) | saddle for c != 0 |",
        "|---|---|---|---|",
    ]
    for row in report["O28_fix"]["exact_rows"]:
        lines.append(
            f"| {row['r0']} | {row['theta_over_c_r0_2_float']:.4f} | {float(Fraction(row['light_mass_shift_over_c2_r0_4'])):.6g} | "
            f"{row['saddle_for_every_c_nonzero']} |"
        )
    lines += [
        "",
        "| repository scale | r0 | colour radius | abs c max (colour-stable) | theta (abs c = 4 pi, tan beta = 1) | "
        "theta max (colour-stable, any tan beta) | tan beta max | Y_F needed (t-b) | admixture up-type only |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for key, row in report["O28_fix"]["repository_r0_bounds"].items():
        lines.append(
            f"| {key} | {row['r0_float']:.3e} | {_radius_text(row['colour_radius'])} | {row['abs_c_max_colour_stable']:.4g} | "
            f"{row['theta_max_at_abs_c_4pi']:.3e} | {row['theta_max_colour_stable_any_tan_beta']:.3e} | "
            f"{row['tan_beta_max_over_phase']:.3f} | {row['t_b_split_requires_Y_F_at_least']:.3g} | {row['induced_126bar_vev_up_type_only']} |"
        )
    lines += ["", f"Findings: {json.dumps(report['O28_fix']['findings'])}", "", report["O28_fix"]["mirsky_argument"]]
    lines += ["", report["O28_fix"]["sos27_statement"]]
    portals = report["H_linear_portals"]
    region = portals["colour_stable_region"]
    lines += [
        "",
        "## (3b) All five H-linear portals at q0 on the full H block",
        "",
        f"- {portals['scope_note']}.",
        f"- Lattice binding: {portals['lattice_binding']['homogeneity']}.",
        f"- Selection rule: {portals['selection_rule']}.",
        f"- Colour-stable region, per direction: {region['per_direction']}.",
        f"- Any combination (sufficient): {region['inner_certificate_any_combination']}.",
        f"- Any combination (necessary): {region['outer_certificate_any_combination']}.",
        f"- Compensation: {region['compensation']}.",
        "",
        "| direction | doublet block (r0 power) | triplet blocks (r0 power) | doublet source | theta_(15,2,2)/(c r0^2) (physical r0, tan beta = 1) | "
        "shift/(c^2 r0^2) | induced 16.16 pairs | colour radius (physical r0) | saddle for c != 0 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for direction, rows in portals["per_direction"].items():
        pattern = portals["lattice_binding"]["patterns"][f"re::{direction}"]
        row = rows[0]
        triplet_text = ", ".join(f"{name} ({value['r0_power']})" for name, value in pattern["triplet_column_blocks"].items()) or "none"
        doublet_text = f"{pattern['doublet_column_block']} ({pattern['r0_power']})" if pattern["expected_block"] else "none"
        lines.append(
            f"| {direction} | {doublet_text} | {triplet_text} | {pattern['doublet_source_hypercharge'] or 'none'} | "
            f"{row['theta_sigma_over_c_r0_2_float']:.4g} | {row['light_mass_shift_over_c2_r0_2_float']:.4g} | "
            f"{', '.join(row['induced_126bar_yukawa_pairs']) or 'none'} | {_radius_text(row['colour_radius'])} | "
            f"{row['saddle_for_every_c_nonzero']} |"
        )
    short = [PORTAL_SHORT_NAMES[direction] for direction in EXPECTED_H_LINEAR_DIRECTIONS]
    lines += [
        "",
        "| repository scale | r0 | colour radius: " + " / ".join(short) + " | outer bound O15 / O28 | theta up-type: box / colour-stable | "
        "portal-immune pull (raw / theory) | tan beta max colour-stable: O15 / O28 / O38 / O45_B02 | "
        "reaches m_t/m_b (box; smallest grid abs c, step 4 pi/48) | "
        "reaches m_t/m_b (colour-stable; smallest grid abs c, step 4 pi/48) | fix excluded |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for key, row in portals["repository_r0_bounds"].items():
        scans = row["tan_beta_scan_colour_stable"]
        tan_text = " / ".join(
            f"{scans[direction]['tan_beta_max_over_scan']:.3g}"
            for direction in EXPECTED_H_LINEAR_DIRECTIONS
            if direction in scans
        )

        def reach(names: Sequence[str], table: Mapping[str, Any]) -> str:
            return ", ".join(
                f"{PORTAL_SHORT_NAMES[name]} (abs c >= {table[name]['smallest_grid_abs_c_reaching_m_t_over_m_b']:.2f})" for name in names
            ) or "none"

        outer = row["colour_radius_outer_bound_any_combination"]
        lines.append(
            f"| {key} | {row['r0_float']:.3e} | "
            + " / ".join(_radius_text(row["colour_radius"][direction]) for direction in EXPECTED_H_LINEAR_DIRECTIONS)
            + f" | {_radius_text(outer['O15_B01_Phi_Hdag_Sigma'])} / {_radius_text(outer['O28_B01_unique_Hdag_Sigma2_Sigmadag'])} | "
            f"{row['theta_up_type_max_box_triangle_bound']:.3e} / {row['theta_up_type_max_colour_stable_triangle_bound']:.3e} | "
            f"{_fmt(row['portal_immune_tests_min_pull_raw_sigma'])} / {_fmt(row['portal_immune_tests_min_pull_conservative_sigma'])} | "
            f"{tan_text} | {reach(row['tan_beta_reaches_m_t_over_m_b_in_box_with'], row['tan_beta_scan_box'])} | "
            f"{reach(row['tan_beta_reaches_m_t_over_m_b_colour_stable_with'], scans)} | {row['portal_fix_excluded']} |"
        )
    lines += ["", f"Findings: {json.dumps(portals['findings'])}", "", portals["reading"] + "."]
    lines += ["", "## (4) Seesaw (float, not load-bearing)", "", report["seesaw"]["assumptions"], ""]
    lines += [
        "| v_R | generic Y_R (M_D = M_u data) | generic Y_R (M_D with charged-lepton values) | median Y_R (NO) | min Y_R found (NO) | min Y_R found (IO) |",
        "|---|---|---|---|---|---|",
    ]
    for label, row in report["seesaw"]["rows"].items():
        lines.append(
            f"| {label} | {row['generic_Y_R']:.3g} | {row['generic_Y_R_if_MD_has_charged_lepton_singular_values']:.3g} | "
            f"{row['normal']['median_Y_R']:.3g} | {row['normal']['minimum_Y_R_found']:.3g} | "
            f"{row['inverted']['minimum_Y_R_found']:.3g} |"
        )
    lines += ["", report["seesaw"]["reading"], "", "## (5) Scope and routes", ""]
    for key, value in report["scope"].items():
        lines.append(f"**{key}**")
        lines += [f"- {item}" for item in value]
        lines.append("")
    for key, value in report["routes"].items():
        lines.append(f"- Route {key}: {value}")
    lines += ["", "## Checks", ""]
    lines += [f"- {'PASS' if value else 'FAIL'} `{key}`" for key, value in report["checks"].items()]
    return "\n".join(lines) + "\n"


def write_report(report: Mapping[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(json_roundtrip(report)), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown artifacts")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    summary = {key: report[key] for key in ("status", "overall_state", "G8_status", "n_checks", "n_failed", "failures", "flags", "runtime_seconds")}
    print(json.dumps(_jsonable(summary), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
