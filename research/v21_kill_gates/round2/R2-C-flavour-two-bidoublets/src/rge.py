"""RG machinery for the K2 fit.

SM: two-loop gauge + two-loop matrix Yukawa RGEs (Machacek-Vaughn / Luo-Wang-Xiao hep-ph/0211440 form, GUT-normalised
g1), one-loop Higgs quartic (LX convention lambda_LX = 2 lambda_SM), one-loop Weinberg-operator running
(Antusch et al. hep-ph/0501272 form, kappa for m_nu = kappa v^2) below v_R.
G3221 (SU(3)xSU(2)_LxSU(2)_RxU(1)_{B-L}) between v_R and M_U: one-loop gauge with the T2/T3 light content and the
F17 vector-like states, one-loop Yukawa RGEs for the single light bidoublet (no tilde couplings, X-charge forbids
them): beta_Yf = Yf[(3/2)Yf^dag Yf + (1/2)Yf'^dag Yf' + T_Phi - G_f] (2HDM-type-II-like vertex structure, bidoublet
trace T_Phi = Tr(3Yu^dag Yu + 3Yd^dag Yd + Ye^dag Ye + Ynu^dag Ynu)), gauge Casimirs of G3221 (B-L charge q=(B-L)/2,
non-GUT-normalised g_BL).  Everything is run top-down from M_U to M_Z.  Convention: t = ln mu, dY/dt = beta/(16pi^2)
+ beta2/(16pi^2)^2.
"""
import math
import numpy as np
from scipy.integrate import solve_ivp

K1 = 1 / (16 * math.pi**2)
K2 = K1 * K1

def _H(m):
    return m.conj().T

# ----------------------------------------------------------------------------------------------------------------
# SM two-loop
# ----------------------------------------------------------------------------------------------------------------
def sm_rhs(t, y, with_kappa):
    g1, g2, g3, lam = y[0:4]
    Yu = y[4:22].view(complex).reshape(3, 3) if False else (y[4:13] + 1j * y[13:22]).reshape(3, 3)
    Yd = (y[22:31] + 1j * y[31:40]).reshape(3, 3)
    Ye = (y[40:49] + 1j * y[49:58]).reshape(3, 3)
    if with_kappa:
        kap = (y[58:67] + 1j * y[67:76]).reshape(3, 3)
    Uu, Dd, Ee = _H(Yu) @ Yu, _H(Yd) @ Yd, _H(Ye) @ Ye
    T = 3 * np.trace(Uu).real + 3 * np.trace(Dd).real + np.trace(Ee).real
    g1s, g2s, g3s = g1 * g1, g2 * g2, g3 * g3
    # gauge: one loop + two loop (incl. Yukawa)
    b = np.array([41 / 10, -19 / 6, -7])
    B = np.array([[199 / 50, 27 / 10, 44 / 5], [9 / 10, 35 / 6, 12], [11 / 10, 9 / 2, -26]])
    cu, cd, ce = np.array([17 / 10, 3 / 2, 2]), np.array([1 / 2, 3 / 2, 2]), np.array([3 / 2, 1 / 2, 0])
    g = np.array([g1, g2, g3]); gs = g * g
    tu, td, te = np.trace(Uu).real, np.trace(Dd).real, np.trace(Ee).real
    dg = K1 * b * g**3 + K2 * g**3 * (B @ gs - (cu * tu + cd * td + ce * te))
    # Yukawa one loop
    Gu = 17 / 20 * g1s + 9 / 4 * g2s + 8 * g3s
    Gd = 1 / 4 * g1s + 9 / 4 * g2s + 8 * g3s
    Ge = 9 / 4 * g1s + 9 / 4 * g2s
    I3 = np.eye(3)
    bu1 = Yu @ (1.5 * (Uu - Dd) + (T - Gu) * I3)
    bd1 = Yd @ (1.5 * (Dd - Uu) + (T - Gd) * I3)
    be1 = Ye @ (1.5 * Ee + (T - Ge) * I3)
    # Yukawa two loop (Luo-Wang-Xiao)
    chi4 = 9 / 4 * (3 * np.trace(Uu @ Uu) + 3 * np.trace(Dd @ Dd) + np.trace(Ee @ Ee) - 2 / 3 * np.trace(Uu @ Dd)).real
    Y4 = Gu * tu + Gd * td + (3 / 4 * g1s + 3 / 4 * g2s) * te
    bu2 = Yu @ (1.5 * Uu @ Uu - Uu @ Dd - 0.25 * Dd @ Uu + 11 / 4 * Dd @ Dd + T * (5 / 4 * Dd - 9 / 4 * Uu)
                + (-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 + 1187 / 600 * g1s**2 - 23 / 4 * g2s**2 - 108 * g3s**2
                   - 9 / 20 * g1s * g2s + 19 / 15 * g1s * g3s + 9 * g2s * g3s) * I3
                - 6 * lam * Uu + (223 / 80 * g1s + 135 / 16 * g2s + 16 * g3s) * Uu
                - (43 / 80 * g1s - 9 / 16 * g2s + 16 * g3s) * Dd)
    bd2 = Yd @ (1.5 * Dd @ Dd - Dd @ Uu - 0.25 * Uu @ Dd + 11 / 4 * Uu @ Uu + T * (5 / 4 * Uu - 9 / 4 * Dd)
                + (-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 - 127 / 600 * g1s**2 - 23 / 4 * g2s**2 - 108 * g3s**2
                   - 27 / 20 * g1s * g2s + 31 / 15 * g1s * g3s + 9 * g2s * g3s) * I3
                - 6 * lam * Dd + (187 / 80 * g1s + 135 / 16 * g2s + 16 * g3s) * Dd
                - (79 / 80 * g1s - 9 / 16 * g2s + 16 * g3s) * Uu)
    be2 = Ye @ (1.5 * Ee @ Ee - 9 / 4 * T * Ee
                + (-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 + 1371 / 200 * g1s**2 - 23 / 4 * g2s**2 + 27 / 20 * g1s * g2s) * I3
                - 6 * lam * Ee + (387 / 80 * g1s + 135 / 16 * g2s) * Ee)
    dYu = K1 * bu1 + K2 * bu2
    dYd = K1 * bd1 + K2 * bd2
    dYe = K1 * be1 + K2 * be2
    # quartic one loop (LX convention)
    H4 = 3 * np.trace(Uu @ Uu).real + 3 * np.trace(Dd @ Dd).real + np.trace(Ee @ Ee).real
    dlam = K1 * (12 * lam**2 - (9 / 5 * g1s + 9 * g2s) * lam + 9 / 4 * (3 / 25 * g1s**2 + 2 / 5 * g1s * g2s + g2s**2) + 4 * lam * T - 4 * H4)
    out = [dg[0], dg[1], dg[2], dlam]
    out += list(dYu.real.ravel()) + list(dYu.imag.ravel())
    out += list(dYd.real.ravel()) + list(dYd.imag.ravel())
    out += list(dYe.real.ravel()) + list(dYe.imag.ravel())
    if with_kappa:
        # one loop: 16pi^2 dkappa/dt = -3/2 [kappa (Ye^dag Ye) + (Ye^dag Ye)^T kappa] + (2T + lambda_LX - 3 g2^2) kappa
        dk = K1 * (-1.5 * (kap @ Ee + Ee.T @ kap) + (2 * T + lam - 3 * g2s) * kap)
        out += list(dk.real.ravel()) + list(dk.imag.ravel())
    return out

def pack_sm(g, lam, Yu, Yd, Ye, kap=None):
    y = [g[0], g[1], g[2], lam]
    for M in (Yu, Yd, Ye):
        y += list(M.real.ravel()) + list(M.imag.ravel())
    if kap is not None:
        y += list(kap.real.ravel()) + list(kap.imag.ravel())
    return np.array(y, dtype=float)

def unpack_sm(y, with_kappa):
    g = y[0:3]; lam = y[3]
    Yu = (y[4:13] + 1j * y[13:22]).reshape(3, 3)
    Yd = (y[22:31] + 1j * y[31:40]).reshape(3, 3)
    Ye = (y[40:49] + 1j * y[49:58]).reshape(3, 3)
    kap = (y[58:67] + 1j * y[67:76]).reshape(3, 3) if with_kappa else None
    return g, lam, Yu, Yd, Ye, kap

def run_sm(y0, mu0, mu1, with_kappa, rtol=1e-8):
    sol = solve_ivp(sm_rhs, (math.log(mu0), math.log(mu1)), y0, args=(with_kappa,), method="DOP853", rtol=rtol, atol=1e-12)
    return sol.y[:, -1]

# ----------------------------------------------------------------------------------------------------------------
# G3221 one loop
# ----------------------------------------------------------------------------------------------------------------
def g3221_b_coefficients(content="T2", f17=True, full_delta_r=False):
    """One-loop b_i for (SU3, SU2L, SU2R, U1_BL[q=(B-L)/2, non-normalised]).  Dynkin: fund SU(N) 1/2, adj N."""
    b3 = -11.0; bL = -22 / 3; bR = -22 / 3; bBL = 0.0
    # fermions (Weyl): per generation Q_L (3,2,1,1/6), Q_R (3,1,2,1/6), L_L (1,2,1,-1/2), L_R (1,1,2,-1/2)
    def ferm(gens):
        nonlocal b3, bL, bR, bBL
        b3 += (2 / 3) * gens * (2 * 0.5 + 2 * 0.5)          # Q_L: 2 Weyl (SU2L) * 1/2, Q_R same
        bL += (2 / 3) * gens * (3 * 0.5 + 1 * 0.5)          # Q_L colour 3, L_L
        bR += (2 / 3) * gens * (3 * 0.5 + 1 * 0.5)
        bBL += (2 / 3) * gens * (6 * (1 / 6)**2 + 6 * (1 / 6)**2 + 2 * 0.25 + 2 * 0.25)
    ferm(3)
    if f17:
        # F17 S-sector vector-like states (masses ~1e13, counted above v_R): 3 x (16+16bar) -> 3 generations' worth x2 (Dirac)
        ferm(6)
        # two 10_F (Dirac/Majorana of SO(10) vectors): 10 -> (3,1,1,-1/3)+(3bar,1,1,1/3)+(1,2,2,0): Weyl fermions
        for _ in range(2):
            b3 += (2 / 3) * (0.5 + 0.5)
            bL += (2 / 3) * (2 * 0.5)
            bR += (2 / 3) * (2 * 0.5)
            bBL += (2 / 3) * (3 * (1 / 3)**2 * 2)
        # singlets: nothing
    # scalars (complex): bidoublet (1,2,2,0); Delta_R (10bar,1,3): (1,1,3,+1)+(3bar,1,3,+1/3)+(6,1,3,-1/3) [q=(B-L)/2 = -1*(-1)...]
    def scal(c3, cL, cR, q, dim):
        nonlocal b3, bL, bR, bBL
        b3 += (1 / 3) * c3; bL += (1 / 3) * cL; bR += (1 / 3) * cR; bBL += (1 / 3) * dim * q * q
    scal(0, 2 * 0.5, 2 * 0.5, 0, 4)                            # bidoublet
    scal(0, 0, 2, 1.0, 3)                                      # (1,1,3,q=1): the Delta_R vev component only
    if full_delta_r:                                           # colour triplet/sextet partners of (10bar,1,3) (default: at M_U)
        scal(3 * 0.5, 0, 3 * 0.5, 1 / 3, 9)                    # (3bar,1,3,q=1/3)
        scal(3 * 2.5, 0, 6 * 0.5, 1 / 3, 18)                   # (6,1,3,q=1/3): Dynkin(6)=5/2
    scal(4 * 3, 8 * 0.5, 8 * 0.5, 0, 32)                       # (8,2,2,0)
    scal(3 * 3, 8 * 2, 0, 0, 24)                               # (8,3,1,0)
    scal(0, 2, 0, 0, 3)                                        # (1,3,1,0)
    if content == "T3":
        scal(0, 2 * 0.5, 2 * 0.5, 0, 4)                        # second colour-singlet bidoublet
        scal(3, 0, 0, 0, 8)                                    # (8,1,1,0)
    return np.array([b3, bL, bR, bBL])

def g3221_yuk_rhs(t, y, b):
    g3, gL, gR, gBL = y[0:4]
    Yu = (y[4:13] + 1j * y[13:22]).reshape(3, 3)
    Yd = (y[22:31] + 1j * y[31:40]).reshape(3, 3)
    Ye = (y[40:49] + 1j * y[49:58]).reshape(3, 3)
    Yn = (y[58:67] + 1j * y[67:76]).reshape(3, 3)
    Uu, Dd, Ee, Nn = _H(Yu) @ Yu, _H(Yd) @ Yd, _H(Ye) @ Ye, _H(Yn) @ Yn
    T = (3 * np.trace(Uu) + 3 * np.trace(Dd) + np.trace(Ee) + np.trace(Nn)).real
    Gq = 8 * g3**2 + 9 / 4 * gL**2 + 9 / 4 * gR**2 + (1 / 6) * gBL**2
    Gl = 9 / 4 * gL**2 + 9 / 4 * gR**2 + (3 / 2) * gBL**2
    I3 = np.eye(3)
    dYu = K1 * Yu @ (1.5 * Uu + 0.5 * Dd + (T - Gq) * I3)
    dYd = K1 * Yd @ (1.5 * Dd + 0.5 * Uu + (T - Gq) * I3)
    dYe = K1 * Ye @ (1.5 * Ee + 0.5 * Nn + (T - Gl) * I3)
    dYn = K1 * Yn @ (1.5 * Nn + 0.5 * Ee + (T - Gl) * I3)
    g = np.array([g3, gL, gR, gBL])
    dg = K1 * b * g**3
    out = list(dg)
    for M in (dYu, dYd, dYe, dYn):
        out += list(M.real.ravel()) + list(M.imag.ravel())
    return out

def pack_g3221(g, Yu, Yd, Ye, Yn):
    y = list(g)
    for M in (Yu, Yd, Ye, Yn):
        y += list(M.real.ravel()) + list(M.imag.ravel())
    return np.array(y, dtype=float)

def unpack_g3221(y):
    g = y[0:4]
    Yu = (y[4:13] + 1j * y[13:22]).reshape(3, 3)
    Yd = (y[22:31] + 1j * y[31:40]).reshape(3, 3)
    Ye = (y[40:49] + 1j * y[49:58]).reshape(3, 3)
    Yn = (y[58:67] + 1j * y[67:76]).reshape(3, 3)
    return g, Yu, Yd, Ye, Yn

def run_g3221(y0, mu0, mu1, b, rtol=1e-8):
    sol = solve_ivp(g3221_yuk_rhs, (math.log(mu0), math.log(mu1)), y0, args=(b,), method="DOP853", rtol=rtol, atol=1e-12)
    return sol.y[:, -1]

# ----------------------------------------------------------------------------------------------------------------
# gauge couplings: bottom-up SM, then G3221 with unification condition
# ----------------------------------------------------------------------------------------------------------------
def gauge_bottom_up(inputs, mu_top, vR, MU, content="T2"):
    """Return g_SM at MZ, SM gauge couplings at vR (two-loop, Yukawa-less approx with y_t only), G3221 couplings at vR
    satisfying g_R(MU) = g_L(MU) with the one-loop b's, and the gauge couplings at MU."""
    MZ = inputs["MZ"]
    a_em = 1 / inputs["gauge_MZ"]["alpha_em_inv"]; s2 = inputs["gauge_MZ"]["sin2_thw_MSbar"]; a_s = inputs["gauge_MZ"]["alpha_s"]
    g1 = math.sqrt(4 * math.pi * a_em / (1 - s2) * 5 / 3); g2 = math.sqrt(4 * math.pi * a_em / s2); g3 = math.sqrt(4 * math.pi * a_s)
    yt = inputs["masses_GeV_MZ"]["m_t"][0] / inputs["VEV"]
    yb = inputs["masses_GeV_MZ"]["m_b"][0] / inputs["VEV"]; ytau = inputs["masses_GeV_MZ"]["m_tau"][0] / inputs["VEV"]
    Yu = np.diag([0, 0, yt]).astype(complex); Yd = np.diag([0, 0, yb]).astype(complex); Ye = np.diag([0, 0, ytau]).astype(complex)
    y0 = pack_sm([g1, g2, g3], 0.26, Yu, Yd, Ye)
    yR = run_sm(y0, MZ, vR, False)
    gR_sm, lamR, YuR, YdR, YeR, _ = unpack_sm(yR, False)
    g1R, g2R, g3R = gR_sm
    b = g3221_b_coefficients(content)
    # one-loop running MU<-vR for g3, gL : g^-2(MU) = g^-2(vR) - b/(8pi^2) ln(MU/vR)
    L = math.log(MU / vR)
    def up(g, bi):
        return 1 / math.sqrt(1 / g**2 - bi * L / (8 * math.pi**2))
    g3U = up(g3R, b[0]); gLU = up(g2R, b[1])
    gRU = gLU                                   # LR-symmetric unification condition at MU (g_R = g_L at M_U)
    gRR = 1 / math.sqrt(1 / gRU**2 + b[2] * L / (8 * math.pi**2))
    # hypercharge matching: 1/g'^2 = 1/g_R^2 + 1/g_BL^2 with g' = sqrt(3/5) g1 and q = (B-L)/2
    gp = math.sqrt(3 / 5) * g1R
    inv = 1 / gp**2 - 1 / gRR**2
    gBLR = 1 / math.sqrt(inv) if inv > 0 else float("nan")
    gBLU = up(gBLR, b[3]) if inv > 0 else float("nan")
    return {"g_MZ": [g1, g2, g3], "sm_at_vR": [g1R, g2R, g3R], "lam_vR": lamR, "g3221_at_vR": [g3R, g2R, gRR, gBLR],
            "g3221_at_MU": [g3U, gLU, gRU, gBLU], "b_g3221": list(b),
            "alpha_inv_MU": [4 * math.pi / g**2 for g in (g3U, gLU, gRU, gBLU * math.sqrt(2 / 3))]}
