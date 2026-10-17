#!/usr/bin/env python3
"""Axion quality from the declared operator Phi17^4 S^dag^17 / M_Pl,red^17, the axion mass band, ADMX overlap, and the
perturbative-unitarity (a0 <= 1/2) assumptions for the thresholds used in K1."""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
M_PL = 2.435e18
CHI = 0.0755**4           # QCD topological susceptibility (GeV^4), chi^(1/4) = 75.5 MeV (repo convention)
PHI17 = 1.0e17            # <Phi17> (GeV), taken as the field modulus in the operator (convention A)
THETA_MAX = 1.0e-10
M_A_REF = 5.70e-6 * 1.0e12  # m_a [eV] = 5.70(7) ueV x (1e12 GeV / f_a) (LIT-abstract: Gorghetto-Villadoro arXiv:1812.01008, chi^(1/4) = 75.5 MeV)
N_PQ_ABS = 34             # |N| (FINAL J1a, EXACT); f_a = v_S/17 = sqrt2 <S>/17 (repo: v_a = F_PQ/68 -> v_S/17 for v_Phi >> v_S)

out = {}


def s_max(pref: float, phi17: float) -> float:
    """<S>_max from dtheta = pref * phi17^4 <S>^17 / (M_Pl^17 chi) <= THETA_MAX."""
    ln_rhs = math.log(THETA_MAX) + math.log(CHI) + 17 * math.log(M_PL) - math.log(pref) - 4 * math.log(phi17)
    return math.exp(ln_rhs / 17.0)


# Conventions: (A) dtheta = 17 x |DeltaV|/chi with |DeltaV| = <Phi17>^4 <S>^17/M_Pl^17 (unit coefficient, field moduli);
# (B) same without the factor 17; (C) with the canonical v/sqrt2 moduli: <Phi17> = 1e17/sqrt2, <S> = v_S/sqrt2 (reported as v_S).
conv = {}
for name, pref, phi in (("A_17x_moduli", 17.0, PHI17), ("B_1x_moduli", 1.0, PHI17), ("A_17x_phi_over_sqrt2", 17.0, PHI17 / math.sqrt(2))):
    sm = s_max(pref, phi)
    conv[name] = {"prefactor": pref, "phi17_used": phi, "S_max_GeV": sm, "v_S_max_GeV": math.sqrt(2) * sm,
                  "f_a_min_GeV": math.sqrt(2) * sm / 17, "m_a_min_ueV": M_A_REF / (math.sqrt(2) * sm / 17) * 1e6}
out["quality_conventions"] = conv
out["quality_note"] = ("dtheta ~ n Lambda_PQ^4 sin(delta)/chi with Lambda_PQ^4 = <Phi17>^4 <S>^17/M_Pl,red^17 and n = 17 (the S-phase "
                       "winding of the operator) is convention A; the FINAL used <S>_max = 3.3e13 (convention B-like).  "
                       "The bound depends on the unknown O(1) Wilson coefficient and on the sin(delta) phase: a coefficient "
                       "c_21 = 0.1 raises <S>_max by 10^(1/17) = 1.145.")

S_MAX = conv["A_17x_moduli"]["S_max_GeV"]
S_MAX_B = conv["B_1x_moduli"]["S_max_GeV"]
out["S_max_used_in_K1"] = S_MAX

# y_s window per M_s.  Unitarity (EST): a0 = N y^2/(16 pi) in the singlet channel of psi psi -> psi psi with N = 16
# (dimension of the 16) -> y <= sqrt(8 pi / 16) = 1.2533; for the 10-pair N = 10 -> 1.585.  Also quoted: y <= sqrt(4 pi).
Y_UNIT_16 = math.sqrt(8 * math.pi / 16)
Y_UNIT_10 = math.sqrt(8 * math.pi / 10)
out["unitarity_EST"] = {"y_max_16pair_a0_half": Y_UNIT_16, "y_max_10pair_a0_half": Y_UNIT_10, "sqrt_4pi": math.sqrt(4 * math.pi),
                        "assumption": "tree-level s-wave amplitude of the Yukawa in the SO(10)-singlet channel, a0 = N y^2/(16 pi), "
                                      "N = multiplicity of the fermion pair; this is the K3-style normalisation a0 <= 1/2 (EST, not computed "
                                      "with the repo's exact partial-wave machinery)"}
rows = []
for M_s in (3e12, 5e12, 7e12, 1e13, 2e13, 3.6e13):
    y_min = M_s / S_MAX
    y_min_B = M_s / S_MAX_B
    row = {"M_s": M_s, "y_s_min_convA": y_min, "y_s_min_convB": y_min_B, "y_s_max_unitarity_16": Y_UNIT_16,
           "window_open_convA": y_min <= Y_UNIT_16, "S_at_y_min": S_MAX, "S_at_y_max": M_s / Y_UNIT_16}
    # axion mass band: m_a = M_A_REF / f_a, f_a = sqrt2 <S>/17
    for lab, S in (("at_quality_max_S", S_MAX), ("at_unitarity_min_S", M_s / Y_UNIT_16)):
        f_a = math.sqrt(2) * S / 17
        row[f"f_a_{lab}_GeV"] = f_a
        row[f"m_a_{lab}_ueV"] = M_A_REF / f_a * 1e6
    rows.append(row)
out["y_s_windows"] = rows

# ADMX / haloscope DFSZ exclusions (LIT-abstract, 100% axion DM assumed): mass bands in ueV.
ADMX_DFSZ = [(2.66, 2.81, "ADMX arXiv:1804.05750 (DFSZ sensitivity)"), (2.81, 3.31, "ADMX arXiv:1910.08638 (full benchmark range excluded)"),
             (3.27, 3.34, "ADMX arXiv:2408.15227, PRL 134, 111002 (2025) DFSZ 90% CL"),
             (3.9, 4.1, "ADMX arXiv:2110.06096 run 1C: DFSZ only in 3.9-4.1 (KSVZ over 3.3-4.2); DFSZ sub-band from the APS talk abstract, LIT-weak"),
             (4.51, 4.59, "CAPP arXiv:2210.10961 (DFSZ sensitivity)")]
out["dfsz_excluded_bands_ueV_LIT"] = ADMX_DFSZ


def m_a_of_S(S):
    return M_A_REF / (math.sqrt(2) * S / 17) * 1e6


def S_of_m_a(m):
    return M_A_REF / (m * 1e-6) * 17 / math.sqrt(2)


# allowed y_s sub-windows per M_s avoiding the DFSZ-excluded bands (convention A)
allowed = []
for M_s in (3e12, 5e12, 7e12, 1e13):
    y_lo, y_hi = M_s / S_MAX, Y_UNIT_16
    m_lo, m_hi = m_a_of_S(S_MAX), m_a_of_S(M_s / Y_UNIT_16)  # m_a increases with y_s
    segs = [(m_lo, m_hi)]
    for a, b, _ in ADMX_DFSZ:
        new = []
        for (x, y) in segs:
            if b <= x or a >= y:
                new.append((x, y))
            else:
                if x < a:
                    new.append((x, a))
                if b < y:
                    new.append((b, y))
        segs = new
    allowed.append({"M_s": M_s, "m_a_range_ueV": [m_lo, m_hi], "y_s_range": [y_lo, y_hi],
                    "allowed_m_a_segments_ueV": segs,
                    "allowed_y_s_segments": [[M_s / S_of_m_a(x), M_s / S_of_m_a(y)] for (x, y) in segs]})
out["axion_windows_avoiding_DFSZ_bands"] = allowed
out["three_loop_point_axion"] = {"M_s": 1e13, "y_s": 1e13 / S_MAX, "S": S_MAX, "f_a_GeV": math.sqrt(2) * S_MAX / 17,
                                 "m_a_ueV": m_a_of_S(S_MAX), "E_over_N": "8/3 (EXACT, FINAL J1a)", "coupling": "DFSZ-I-like",
                                 "g_agg_GeV^-1_EST": 1.92e-16 * (m_a_of_S(S_MAX)) * abs(8 / 3 - 1.92) / 1.0}

# GUT-scalar unitarity (EST): the singlet channel of lambda |Phi|^4 on an n-component multiplet has a0 ~ lambda (n+2)/(16 pi)
# (calibration: complex doublet n = 4 gives 3 lambda/(8 pi) -> 6 lambda/(16 pi) = lambda (n+2)/(16 pi) with n = 4).
# a0 <= 1/2 -> lambda <= 8 pi/(n+2); mass^2 ~ lambda rho^2 with rho = M_U/(g sqrt(cos^2 th/2 + sin^2 th)).
gut = {}
for n, lab in ((210, "210 self-quartic"), (252, "126bar self-quartic"), (20, "10_H self-quartic")):
    lam = 8 * math.pi / (n + 2)
    for th in (30, 45, 60, 90):
        g = math.sqrt(4 * math.pi / 26.5)
        ratio = math.sqrt(lam) / (g * math.sqrt(math.cos(math.radians(th)) ** 2 / 2 + math.sin(math.radians(th)) ** 2))
        gut[f"{lab} theta={th}"] = {"lambda_max": lam, "M_scalar_over_M_U_max_if_self_quartic_dominated": ratio}
out["gut_scalar_unitarity_EST"] = gut
out["gut_scalar_unitarity_note"] = ("EST: with a0 <= 1/2 on the dominant self-quartic channel the 210 and 126bar masses generated by their own "
                                    "quartics are <= ~0.5-1.0 M_U, i.e. the x1/2..x1 half of the GUT threshold window (the S2u Monte Carlo); "
                                    "cross-quartics and the unknown vacuum (G3 blocked) can move individual states, so x1/2..x2 is kept as the "
                                    "declared window.")

with open(os.path.join(HERE, "k1_axion_quality.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out, indent=1))
