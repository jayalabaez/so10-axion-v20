"""SKEPTIC independent top-down chain for the two-bidoublet 10_H + 126bar_H model (no Ytilde10), v21-F17-B63-G3221.

Written from scratch (no import of the researcher's code).  Conventions:
  * Doublet-LEFT Yukawas everywhere: L_Y = f_L^T Y f^c (Higgs) ; left rotations from Y Y^dag.
  * At M_U (SO(10) relations, standard H/F/r/s parametrisation):
        Yd = H + F, Ye = H - 3F, Yu = r (H + s F), Ynu = r (H - 3 s F)   [these hold for the *proxy* only]
    Top-down: Y10 = H / c_d10, Y126 = F / c_d126 at M_U; G3221 bidoublet Yukawas Yq_10 = Y10, Yq_126 = Y126,
    Yl_10 = Y10, Yl_126 = -3 Y126; Delta_R Majorana coupling f = C_R Y126 (M_R = f v_R).
    Composition: |c_u10|^2+|c_u126|^2+|c_d10|^2+|c_d126|^2 = 1, c_u10 = r c_d10, c_u126 = r s c_d126.
  * G3221 one-loop RGEs (derived independently, see REPORT_SKEPTIC):
        16pi^2 dYq_a = (sum_b Yq_b Yq_b^+) Yq_a + Yq_a (sum_b Yq_b^+ Yq_b) + sum_c Yq_c T_ca - Gq Yq_a
        16pi^2 dYl_a = (sum_b Yl_b Yl_b^+) Yl_a + Yl_a (sum_b Yl_b^+ Yl_b + 3/4 f^+ f) + sum_c Yl_c T_ca - Gl Yl_a
        16pi^2 df    = S^T f + f S + 1/2 Tr(f^+ f) f - Gf f,   S = sum_b Yl_b^+ Yl_b + 3/4 f^+ f
        T_ca = 3 Tr(Yq_c^+ Yq_a) + Tr(Yl_c^+ Yl_a)
        Gq = 8 g3^2 + 9/4 (gL^2+gR^2) + gq^2/6 ; Gl = 9/4 (gL^2+gR^2) + 3/2 gq^2 ; Gf = 9/2 gR^2 + 3/2 gq^2  (q=(B-L)/2)
    gauge couplings one-loop analytic (b's computed here with Fractions).
  * SM: two-loop gauge, two-loop Yukawa (Arason et al. 1992 form, incl. the -2 lambda (3Uu+Dd) cross terms),
    one-loop nu^c sector, one-loop Weinberg operator with lambda_A = 2 lambda (V = lambda/2 (H^+H)^2), sequential
    tree-level decoupling kappa -> kappa - y y^T / M at mu = M_i.
  * Integrator: batched classical RK4 with selectable step (validated by step halving).
"""
import math
from fractions import Fraction as Fr
import numpy as np

K1 = 1.0 / (16 * math.pi**2)
K2 = K1 * K1
MZ = 91.1876
VEV = 174.10           # GeV,  m = y * VEV
C_R = 2 * math.sqrt(6)
Y10_ACT = 1 / (2 * math.sqrt(2))
Y126_ACT = math.sqrt(3) / 4
M_S = 1.0e13

# ---------------------------------------------------------------------------------------------------------------
# DATA (PDG-2024-derived running masses at M_Z, PDG CKM, NuFIT 6.0 NO with SK)
# ---------------------------------------------------------------------------------------------------------------
MASS_KEYS = ["m_u", "m_c", "m_t", "m_d", "m_s", "m_b", "m_e", "m_mu", "m_tau"]
KEYS = MASS_KEYS + ["s12", "s23", "s13", "delta", "sin2_th12", "sin2_th23", "sin2_th13", "dm21", "dm31"]
MZ_MASSES = {  # GeV, (central, exp/conversion 1 sigma)  -- PDG 2024 m(2GeV), m_c(m_c), m_b(m_b), m_t, leptons run to M_Z
    "m_u": (1.2484e-3, 4.21e-5), "m_c": (0.63216, 0.00993), "m_t": (169.49, 0.50),
    "m_d": (2.7165e-3, 4.75e-5), "m_s": (5.4042e-2, 6.79e-4), "m_b": (2.8657, 0.0154),
    "m_e": (4.86670e-4, 1.7e-9), "m_mu": (0.102730, 2.1e-7), "m_tau": (1.74640, 8.9e-5)}
CKM = {"s12": (0.22501, 0.00068), "s23": (0.04182, 0.00080), "s13": (0.003731, 0.000106), "delta": (1.1472, 0.02345)}
NUFIT60_SK = {"sin2_th12": (0.308, 0.012), "sin2_th23": (0.470, 0.015), "sin2_th13": (0.02215, 0.00060),
              "dm21": (7.49e-5, 0.19e-5), "dm31": (2.513e-3, 0.021e-3)}


def dataset(floor=0.01, nu=None, th23_sigma=None, mass_err_override=None):
    nu = nu or NUFIT60_SK
    d = {}
    for k in MASS_KEYS:
        c, s = MZ_MASSES[k]
        if mass_err_override and k in mass_err_override:
            s = mass_err_override[k] * c
        d[k] = (c, c * math.sqrt((s / c)**2 + floor**2))
    d.update(CKM)
    d.update(nu)
    if th23_sigma is not None:
        d["sin2_th23"] = (d["sin2_th23"][0], th23_sigma)
    return d


# ---------------------------------------------------------------------------------------------------------------
# exact b coefficients
# ---------------------------------------------------------------------------------------------------------------
_T3 = {1: Fr(0), 3: Fr(1, 2), 6: Fr(5, 2), 8: Fr(3)}
_T2 = {1: Fr(0), 2: Fr(1, 2), 3: Fr(2)}


def _b(d3, dL, dR, q, kind):
    w = {"weyl": Fr(2, 3), "cplx": Fr(1, 3), "real": Fr(1, 6)}[kind]
    return np.array([w * _T3[d3] * dL * dR, w * _T2[dL] * d3 * dR, w * _T2[dR] * d3 * dL, w * Fr(q)**2 * d3 * dL * dR],
                    dtype=object)


FAM = (_b(3, 2, 1, Fr(1, 6), "weyl") + _b(3, 1, 2, Fr(-1, 6), "weyl") + _b(1, 2, 1, Fr(-1, 2), "weyl")
       + _b(1, 1, 2, Fr(1, 2), "weyl"))
TEN_F = _b(1, 2, 2, 0, "weyl") + _b(3, 1, 1, Fr(-1, 3), "weyl") + _b(3, 1, 1, Fr(1, 3), "weyl")
GAUGE = np.array([Fr(-11), Fr(-22, 3), Fr(-22, 3), Fr(0)], dtype=object)
SCAL = {"bid": _b(1, 2, 2, 0, "cplx"), "DR": _b(1, 1, 3, 1, "cplx"), "831": _b(8, 3, 1, 0, "real"),
        "813": _b(8, 1, 3, 0, "real"), "622": _b(6, 2, 2, Fr(1, 3), "cplx"), "131": _b(1, 3, 1, 0, "real")}
CONTENT = {"C2": ["bid", "bid", "DR"], "C1": ["bid", "bid", "831", "DR"],
           "R813": ["bid", "bid", "831", "DR", "813"], "R622": ["bid", "bid", "831", "DR", "622"]}
MU_NOMINAL = {"C2": 6.05e15, "C1": 2.18e15, "R813": 2.4e16, "R622": 1.9e16}


def b3221(content, with_S):
    b = GAUGE + 3 * FAM
    for k in CONTENT[content]:
        b = b + SCAL[k]
    if with_S:
        b = b + 6 * FAM + 2 * TEN_F
    return b


SM_B1 = np.array([41 / 10, -19 / 6, -7.0])
SM_B2 = np.array([[199 / 50, 27 / 10, 44 / 5], [9 / 10, 35 / 6, 12], [11 / 10, 9 / 2, -26]])
SM_CY = np.array([[17 / 10, 1 / 2, 3 / 2], [3 / 2, 3 / 2, 1 / 2], [2, 2, 0]])   # rows g1,g2,g3; cols tr Uu, Dd, Ee
S_SHIFT = 28.0 / 3


def herm(A):
    return np.conj(np.swapaxes(A, -1, -2))


def trr(A):
    return np.real(np.trace(A, axis1=-2, axis2=-1))


def ex(x):
    return np.asarray(x)[..., None, None]


# ---------------------------------------------------------------------------------------------------------------
# SM RHS (batched, N points).  Internally doublet-RIGHT (YR = YL^T) to use the Arason form  dYR = YR * beta.
# state: g (N,3), lam (N,), Yu,Yd,Ye (N,3,3) doublet-right, kap (N,3,3) [L,L], Yn (N,3,3) doublet-right rows=nu^c
# (inactive rows zero), M (N,3,3)
# ---------------------------------------------------------------------------------------------------------------
I3 = np.eye(3)
KAPPA_LAM = 2.0     # lambda_A = 2 lambda (V = lambda/2 (H^+H)^2); researcher's code effectively uses 1.0


def sm_rhs(st, dbS, two_loop=True):
    g, lam, Yu, Yd, Ye, kap, Yn, M = st
    g1s, g2s, g3s = g[:, 0]**2, g[:, 1]**2, g[:, 2]**2
    Uu, Dd, Ee, Nn = herm(Yu) @ Yu, herm(Yd) @ Yd, herm(Ye) @ Ye, herm(Yn) @ Yn
    tu, td, te, tn = trr(Uu), trr(Dd), trr(Ee), trr(Nn)
    T = 3 * tu + 3 * td + te + tn
    gs = g**2
    b1 = SM_B1 + dbS
    dg = K1 * b1[None, :] * g**3
    if two_loop:
        dg = dg + K2 * g**3 * (gs @ SM_B2.T - np.stack([tu, td, te], 1) @ SM_CY.T)
    Gu = 17 / 20 * g1s + 9 / 4 * g2s + 8 * g3s
    Gd = 1 / 4 * g1s + 9 / 4 * g2s + 8 * g3s
    Ge = 9 / 4 * g1s + 9 / 4 * g2s
    Gn = 9 / 20 * g1s + 9 / 4 * g2s
    Bu = 1.5 * (Uu - Dd) + ex(T - Gu) * I3
    Bd = 1.5 * (Dd - Uu) + ex(T - Gd) * I3
    Be = 1.5 * (Ee - Nn) + ex(T - Ge) * I3
    Bn = 1.5 * (Nn - Ee) + ex(T - Gn) * I3
    dYu, dYd, dYe = K1 * Yu @ Bu, K1 * Yd @ Bd, K1 * Ye @ Be
    if two_loop:
        chi4 = 9 / 4 * (3 * trr(Uu @ Uu) + 3 * trr(Dd @ Dd) + trr(Ee @ Ee) - 2 / 3 * trr(Uu @ Dd))
        Y4 = Gu * tu + Gd * td + 3 / 4 * (g1s + g2s) * te
        com = -chi4 + 1.5 * lam**2 + 2.5 * Y4
        Bu2 = (1.5 * Uu @ Uu - Uu @ Dd - 0.25 * Dd @ Uu + 11 / 4 * Dd @ Dd + ex(T) * (5 / 4 * Dd - 9 / 4 * Uu)
               - ex(2 * lam) * (3 * Uu + Dd)
               + ex(223 / 80 * g1s + 135 / 16 * g2s + 16 * g3s) * Uu - ex(43 / 80 * g1s - 9 / 16 * g2s + 16 * g3s) * Dd
               + ex(com + 1187 / 600 * g1s**2 - 9 / 20 * g1s * g2s + 19 / 15 * g1s * g3s - 23 / 4 * g2s**2
                    + 9 * g2s * g3s - 108 * g3s**2) * I3)
        Bd2 = (1.5 * Dd @ Dd - Dd @ Uu - 0.25 * Uu @ Dd + 11 / 4 * Uu @ Uu + ex(T) * (5 / 4 * Uu - 9 / 4 * Dd)
               - ex(2 * lam) * (3 * Dd + Uu)
               + ex(187 / 80 * g1s + 135 / 16 * g2s + 16 * g3s) * Dd - ex(79 / 80 * g1s - 9 / 16 * g2s + 16 * g3s) * Uu
               + ex(com - 127 / 600 * g1s**2 - 27 / 20 * g1s * g2s + 31 / 15 * g1s * g3s - 23 / 4 * g2s**2
                    + 9 * g2s * g3s - 108 * g3s**2) * I3)
        Be2 = (1.5 * Ee @ Ee - ex(9 / 4 * T) * Ee - ex(6 * lam) * Ee + ex(387 / 80 * g1s + 135 / 16 * g2s) * Ee
               + ex(com + 1371 / 200 * g1s**2 + 27 / 20 * g1s * g2s - 23 / 4 * g2s**2) * I3)
        dYu = dYu + K2 * Yu @ Bu2
        dYd = dYd + K2 * Yd @ Bd2
        dYe = dYe + K2 * Ye @ Be2
    dYn = K1 * Yn @ Bn
    P = Yn @ herm(Yn)                       # (nu^c, nu^c)
    dM = K1 * (P @ M + M @ np.swapaxes(P, 1, 2))
    H4 = 3 * trr(Uu @ Uu) + 3 * trr(Dd @ Dd) + trr(Ee @ Ee) + trr(Nn @ Nn)
    dlam = K1 * (12 * lam**2 - (9 / 5 * g1s + 9 * g2s) * lam + 9 / 4 * (3 / 25 * g1s**2 + 2 / 5 * g1s * g2s + g2s**2)
                 + 4 * lam * T - 4 * H4)
    EeT = np.swapaxes(Ee, 1, 2)             # = Ye_L Ye_L^+  (L,L)
    NnT = np.swapaxes(Nn, 1, 2)
    dk = K1 * (-1.5 * (kap @ Ee + EeT @ kap) + 0.5 * (kap @ Nn + NnT @ kap) + ex(2 * T + KAPPA_LAM * lam - 3 * g2s) * kap)
    return [dg, dlam, dYu, dYd, dYe, dk, dYn, dM]


def rk4(f, st, dt, *a, **kw):
    dt = np.asarray(dt, float)

    def ax(x, k, c):
        if dt.ndim == 0:
            return x + c * dt * k
        return x + c * dt.reshape((-1,) + (1,) * (x.ndim - 1)) * k
    k1 = f(st, *a, **kw)
    k2 = f([ax(x, k, 0.5) for x, k in zip(st, k1)], *a, **kw)
    k3 = f([ax(x, k, 0.5) for x, k in zip(st, k2)], *a, **kw)
    k4 = f([ax(x, k, 1.0) for x, k in zip(st, k3)], *a, **kw)
    if dt.ndim == 0:
        return [x + dt / 6 * (p + 2 * q + 2 * r + s) for x, p, q, r, s in zip(st, k1, k2, k3, k4)]
    return [x + dt.reshape((-1,) + (1,) * (x.ndim - 1)) / 6 * (p + 2 * q + 2 * r + s)
            for x, p, q, r, s in zip(st, k1, k2, k3, k4)]


# ---------------------------------------------------------------------------------------------------------------
# gauge environment
# ---------------------------------------------------------------------------------------------------------------
def gauge_mz():
    aem = 1 / 127.951; s2 = 0.23122; als = 0.1180
    e2 = 4 * math.pi * aem
    return np.array([math.sqrt(5 / 3 * e2 / (1 - s2)), math.sqrt(e2 / s2), math.sqrt(4 * math.pi * als)])


def data_yukawas(d):
    """Yukawas at M_Z (doublet-right) from central values: Yu diagonal, Yd = (V^* diag)^T etc."""
    m = {k: d[k][0] for k in KEYS}
    s12, s23, s13, dl = m["s12"], m["s23"], m["s13"], m["delta"]
    c12, c23, c13 = math.sqrt(1 - s12**2), math.sqrt(1 - s23**2), math.sqrt(1 - s13**2)
    e = np.exp(1j * dl)
    V = np.array([[c12 * c13, s12 * c13, s13 / e],
                  [-s12 * c23 - c12 * s23 * s13 * e, c12 * c23 - s12 * s23 * s13 * e, s23 * c13],
                  [s12 * s23 - c12 * c23 * s13 * e, -c12 * s23 - s12 * c23 * s13 * e, c23 * c13]])
    YuL = np.diag([m["m_u"], m["m_c"], m["m_t"]]).astype(complex) / VEV
    YdL = V.conj() @ np.diag([m["m_d"], m["m_s"], m["m_b"]]) / VEV   # left rotation E_d = V^* (E_u = 1): CKM = E_u^T E_d^*
    YeL = np.diag([m["m_e"], m["m_mu"], m["m_tau"]]).astype(complex) / VEV
    return YuL.T, YdL.T, YeL.T


def sm_bottom_up(d, mu_top, lam0=0.27, h=0.05):
    """Run the data (no nu^c) from M_Z to mu_top: returns g, lam at mu_top and the Yukawas (doublet-right)."""
    YuR, YdR, YeR = data_yukawas(d)
    N = 1
    st = [gauge_mz()[None], np.array([lam0]), YuR[None], YdR[None], YeR[None], np.zeros((1, 3, 3), complex),
          np.zeros((1, 3, 3), complex), np.zeros((1, 3, 3), complex)]
    t0, t1 = math.log(MZ), math.log(mu_top)
    nodes = [t0] + ([math.log(M_S)] if t0 < math.log(M_S) < t1 else []) + [t1]
    for a, c in zip(nodes[:-1], nodes[1:]):
        dbS = S_SHIFT if 0.5 * (a + c) > math.log(M_S) else 0.0
        n = max(2, int(math.ceil((c - a) / h))); dt = (c - a) / n
        for _ in range(n):
            st = rk4(sm_rhs, st, dt, dbS)
    return st


class Env:
    """Gauge environment for a given v_R, content, M_U (same conventions as specified for the gate:
    g3, gL from SM at v_R, gR(M_U) = gL(M_U), 1/gY^2 = 1/gR^2 + 1/gq^2 at v_R; one-loop above v_R)."""
    def __init__(self, vR, content, MU=None, d=None, lam0=0.27):
        self.vR = vR; self.content = content; self.MU = MU or MU_NOMINAL[content]
        d = d or dataset()
        st = sm_bottom_up(d, vR, lam0)
        self.g_sm_vR = st[0][0].copy(); self.lam_vR = float(st[1][0])
        self.b_lo = np.array([float(x) for x in b3221(content, False)])
        self.b_hi = np.array([float(x) for x in b3221(content, True)])
        g1, g2, g3 = self.g_sm_vR
        aY = 4 * math.pi / (0.6 * g1**2)
        a3, aL = 4 * math.pi / g3**2, 4 * math.pi / g2**2
        # alpha_L at M_U then alpha_R(vR) from alpha_R(MU) = alpha_L(MU)
        aLU = self.ainv_run(np.array([a3, aL, aL, 1.0]), vR, self.MU)[1]
        aRvR = self.ainv_run(np.array([0, 0, aLU, 0]), self.MU, vR)[2]
        aq = aY - aRvR
        self.ainv_vR = np.array([a3, aL, aRvR, aq])
        self.ainv_MU = self.ainv_run(self.ainv_vR, vR, self.MU)

    def ainv_run(self, a0, mu0, mu1):
        """one-loop alpha^-1 from mu0 to mu1 with the b switch at M_S"""
        a = np.array(a0, float)
        lo, hi = sorted([mu0, mu1])
        sgn = 1 if mu1 > mu0 else -1
        # split
        pts = [mu0]
        if lo < M_S < hi:
            pts.append(M_S)
        pts.append(mu1)
        for x, y in zip(pts[:-1], pts[1:]):
            mid = math.sqrt(x * y)
            b = self.b_hi if mid > M_S else self.b_lo
            a = a - b / (2 * math.pi) * math.log(y / x)
        return a

    def g2_at(self, t):
        """squared couplings (g3^2, gL^2, gR^2, gq^2) at ln mu = t (scalar)"""
        a = self.ainv_run(self.ainv_vR, self.vR, math.exp(t))
        return 4 * math.pi / a


# ---------------------------------------------------------------------------------------------------------------
# G3221 batched RHS
# ---------------------------------------------------------------------------------------------------------------
EXTRA_T10 = 0.0     # extra H10-bidoublet WF from the B63 Yukawa lam23 H10.Vb2.Vb3 above M_S (EST ~ 8 lam23^2); 0 = researcher's model


def g_rhs(st, G2, xT=0.0):
    Yq0, Yq1, Yl0, Yl1, f = st
    g3s, gLs, gRs, gqs = G2
    Gq = 8 * g3s + 9 / 4 * (gLs + gRs) + gqs / 6
    Gl = 9 / 4 * (gLs + gRs) + 1.5 * gqs
    Gf = 4.5 * gRs + 1.5 * gqs
    SLq = Yq0 @ herm(Yq0) + Yq1 @ herm(Yq1)
    SRq = herm(Yq0) @ Yq0 + herm(Yq1) @ Yq1
    FF = herm(f) @ f
    SLl = Yl0 @ herm(Yl0) + Yl1 @ herm(Yl1)
    SRl = herm(Yl0) @ Yl0 + herm(Yl1) @ Yl1 + 0.75 * FF
    t = lambda A, B: np.trace(herm(A) @ B, axis1=1, axis2=2)[:, None, None]
    T00 = 3 * t(Yq0, Yq0) + t(Yl0, Yl0) + xT
    T01 = 3 * t(Yq0, Yq1) + t(Yl0, Yl1)     # T_{c=0,a=1}
    T10 = 3 * t(Yq1, Yq0) + t(Yl1, Yl0)
    T11 = 3 * t(Yq1, Yq1) + t(Yl1, Yl1)
    dq0 = SLq @ Yq0 + Yq0 @ SRq + Yq0 * T00 + Yq1 * T10 - Gq * Yq0
    dq1 = SLq @ Yq1 + Yq1 @ SRq + Yq0 * T01 + Yq1 * T11 - Gq * Yq1
    dl0 = SLl @ Yl0 + Yl0 @ SRl + Yl0 * T00 + Yl1 * T10 - Gl * Yl0
    dl1 = SLl @ Yl1 + Yl1 @ SRl + Yl0 * T01 + Yl1 * T11 - Gl * Yl1
    df = np.swapaxes(SRl, 1, 2) @ f + f @ SRl + 0.5 * np.real(np.trace(FF, axis1=1, axis2=2))[:, None, None] * f - Gf * f
    return [K1 * dq0, K1 * dq1, K1 * dl0, K1 * dl1, K1 * df]


def run_g3221(st, env, h=0.25):
    t0, t1 = math.log(env.MU), math.log(env.vR)
    lnS = math.log(M_S)
    nodes = [t0] + ([lnS] if t1 < lnS < t0 else []) + [t1]
    for a, c in zip(nodes[:-1], nodes[1:]):
        n = max(2, int(math.ceil(abs(c - a) / h))); dt = (c - a) / n
        t = a
        for _ in range(n):
            # RK4 with couplings evaluated at the stage scales (one-loop analytic)
            G0 = env.g2_at(t); Gm = env.g2_at(t + dt / 2); G1 = env.g2_at(t + dt)
            xT = EXTRA_T10 if 0.5 * (a + c) > lnS else 0.0
            k1 = g_rhs(st, G0, xT)
            k2 = g_rhs([x + 0.5 * dt * k for x, k in zip(st, k1)], Gm, xT)
            k3 = g_rhs([x + 0.5 * dt * k for x, k in zip(st, k2)], Gm, xT)
            k4 = g_rhs([x + dt * k for x, k in zip(st, k3)], G1, xT)
            st = [x + dt / 6 * (p + 2 * q + 2 * r + s) for x, p, q, r, s in zip(st, k1, k2, k3, k4)]
            t += dt
    return st


# ---------------------------------------------------------------------------------------------------------------
# batched Takagi / decoupling
# ---------------------------------------------------------------------------------------------------------------
def takagi(A):
    bad = ~np.all(np.isfinite(A.reshape(A.shape[:-2] + (-1,))), -1)
    if np.any(bad):
        A = np.where(bad[..., None, None], np.eye(A.shape[-1]), A)
    w, V = np.linalg.eigh(herm(A) @ A)
    m = np.sqrt(np.clip(w, 0, None))
    D = np.swapaxes(V, -1, -2) @ A @ V
    ph = np.exp(-0.5j * np.angle(np.diagonal(D, axis1=-2, axis2=-1)))
    return m, V * ph[..., None, :]


def run_sm_seesaw(st, vR, h_hi=0.05, h_lo=0.25, two_loop=True):
    """st doublet-right SM state at v_R with all three nu^c active (Yn rows = nu^c, M 3x3).  Runs to M_Z with
    per-point sequential decoupling: after each step any active nu^c with mass >= mu is integrated out at tree level
    (threshold placement error <= one step)."""
    N = st[0].shape[0]
    g, lam, Yu, Yd, Ye, kap, Yn, M = st
    # go to the M mass basis
    m, U = takagi(M)
    Yn = np.swapaxes(U, 1, 2) @ Yn
    M = np.zeros_like(M); M[:, [0, 1, 2], [0, 1, 2]] = m
    st = [g, lam, Yu, Yd, Ye, kap, Yn, M]
    kact = np.full(N, 3)

    def decouple_check(st, kact, t):
        mu = math.exp(t)
        for _ in range(3):
            g, lam, Yu, Yd, Ye, kap, Yn, M = st
            changed = False
            for k in (3, 2, 1):
                sel = np.where(kact == k)[0]
                if sel.size == 0:
                    continue
                blk = M[np.ix_(sel, range(k), range(k))]
                mm, UU = takagi(blk)
                hv = mm[:, k - 1] >= mu
                if not hv.any():
                    continue
                sel2 = sel[hv]; UU = UU[hv]; mm = mm[hv]
                Ynb = np.swapaxes(UU, 1, 2) @ Yn[sel2][:, :k, :]          # rotate active rows
                y = Ynb[:, k - 1, :]                                       # (n,3) doublet index (row of YnR)
                kap[sel2] = kap[sel2] - (y[:, :, None] * y[:, None, :]) / mm[:, k - 1][:, None, None]
                Ynew = Yn[sel2].copy(); Ynew[:, :k, :] = Ynb; Ynew[:, k - 1, :] = 0
                Mnew = np.zeros((sel2.size, 3, 3), complex)
                for j in range(k - 1):
                    Mnew[:, j, j] = mm[:, j]
                Yn[sel2] = Ynew; M[sel2] = Mnew
                kact[sel2] = k - 1
                changed = True
            st = [g, lam, Yu, Yd, Ye, kap, Yn, M]
            if not changed:
                break
        return st, kact

    tv, tZ = math.log(vR), math.log(MZ)
    lnS = math.log(M_S)
    st, kact = decouple_check(st, kact, tv)
    t = tv
    while t > tZ + 1e-12:
        active = (kact > 0).any()
        h = h_hi if active else h_lo
        tn = max(tZ, t - h)
        if t > lnS > tn:
            tn = lnS
        dbS = S_SHIFT if 0.5 * (t + tn) > lnS else 0.0
        st = rk4(sm_rhs, st, tn - t, dbS, two_loop=two_loop)
        t = tn
        if active:
            st, kact = decouple_check(st, kact, t)
    if (kact > 0).any():
        st, kact = decouple_check(st, kact, -50.0)
    return st


# ---------------------------------------------------------------------------------------------------------------
# observables
# ---------------------------------------------------------------------------------------------------------------
def angles(V):
    A = np.abs(V)
    s13 = np.clip(A[:, 0, 2], 0, 1)
    c13 = np.sqrt(np.clip(1 - s13**2, 1e-300, None))
    s12 = np.clip(A[:, 0, 1] / c13, 0, 1); s23 = np.clip(A[:, 1, 2] / c13, 0, 1)
    c12, c23 = np.sqrt(1 - s12**2), np.sqrt(1 - s23**2)
    J = np.imag(V[:, 0, 0] * V[:, 1, 1] * np.conj(V[:, 0, 1]) * np.conj(V[:, 1, 0]))
    den = c12 * s12 * c23 * s23 * c13**2 * s13 + 1e-300
    sd = J / den
    cd = (A[:, 1, 0]**2 - (s12 * c23)**2 - (c12 * s23 * s13)**2) / (2 * s12 * c23 * c12 * s23 * s13 + 1e-300)
    return s12, s23, s13, np.arctan2(sd, cd)


def observables(YuL, YdL, YeL, mnu):
    N = YuL.shape[0]
    out = np.zeros((N, 18))
    Es = []
    for i, Y in enumerate((YuL, YdL, YeL)):
        w, E = np.linalg.eigh(Y @ herm(Y))
        out[:, 3 * i:3 * i + 3] = np.sqrt(np.clip(w, 0, None)) * VEV
        Es.append(E)
    Vc = np.swapaxes(Es[0], 1, 2) @ np.conj(Es[1])
    out[:, 9], out[:, 10], out[:, 11], out[:, 12] = angles(Vc)
    wn, Nn = np.linalg.eigh(herm(mnu) @ mnu)
    mn = np.sqrt(np.clip(wn, 0, None))
    Up = np.swapaxes(Es[2], 1, 2) @ Nn
    a, b, c, dp = angles(Up)
    out[:, 13], out[:, 14], out[:, 15] = a**2, b**2, c**2
    out[:, 16] = (mn[:, 1]**2 - mn[:, 0]**2) * 1e18
    out[:, 17] = (mn[:, 2]**2 - mn[:, 0]**2) * 1e18
    return out, dict(U=Up, mn=mn, dpmns=dp)


def residuals(o, d):
    N = o.shape[0]
    R = np.zeros((N, 18))
    for i, k in enumerate(KEYS):
        c, s = d[k]
        if k in MASS_KEYS:
            R[:, i] = np.log(np.clip(o[:, i], 1e-300, None) / c) * c / s
        elif k == "delta":
            R[:, i] = ((np.abs(o[:, i]) - c + math.pi) % (2 * math.pi) - math.pi) / s
        else:
            R[:, i] = (o[:, i] - c) / s
    return R


# ---------------------------------------------------------------------------------------------------------------
# model: parameters -> observables
# ---------------------------------------------------------------------------------------------------------------
def composition(r, s, cd126):
    rem = 1 - cd126**2 * (1 + np.abs(r * s)**2)
    ok = rem > 0
    cd10 = np.sqrt(np.clip(rem, 1e-300, None) / (1 + r**2))
    return ok, cd10, r * cd10, r * s * cd126


def chain(H, F, r, s, cd126, env, h_g=0.25, h_hi=0.05, h_lo=0.25, two_loop=True, typeII=None, want=False, thr=None):
    """H, F: (N,3,3) complex symmetric at M_U (down-type pieces).  r (N,), s (N,) complex, cd126 (N,).
    Returns observables (N,18), ok mask, info (perturbativity)."""
    N = H.shape[0]
    ok, cd10, cu10, cu126 = composition(r, s, cd126)
    cd10s = np.where(ok, cd10, 1.0); cd126s = np.where(ok, cd126, 1.0)
    Y10 = H / ex(cd10s); Y126 = F / ex(cd126s)
    st = [Y10.copy(), Y126.copy(), Y10.copy(), -3 * Y126, C_R * Y126]
    info = {"y10U": np.abs(Y10).reshape(N, -1).max(1) * Y10_ACT, "y126U": np.abs(Y126).reshape(N, -1).max(1) * Y126_ACT,
            "fU": np.abs(C_R * Y126).reshape(N, -1).max(1)}
    with np.errstate(all="ignore"):
        st = run_g3221(st, env, h_g)
        fin0 = np.ones(N, bool)
        for A in st:
            fin0 &= np.all(np.isfinite(A.reshape(N, -1)), 1) & (np.abs(A).reshape(N, -1).max(1) < 1e3)
        st = [np.where(fin0[:, None, None], A, 1e-3 * np.eye(3)) for A in st]
        Yq0, Yq1, Yl0, Yl1, f = st
        info["y10R"] = np.abs(Yq0).reshape(N, -1).max(1) * Y10_ACT
        info["y126R"] = np.abs(Yq1).reshape(N, -1).max(1) * Y126_ACT
        info["fR"] = np.abs(f).reshape(N, -1).max(1)
        info["f_sv_vR"] = np.linalg.svd(f, compute_uv=False)
        YuL = ex(cu10) * Yq0 + ex(cu126) * Yq1
        YdL = ex(cd10s) * Yq0 + ex(cd126s) * Yq1
        YeL = ex(cd10s) * Yl0 + ex(cd126s) * Yl1
        YnL = ex(cu10) * Yl0 + ex(cu126) * Yl1
        if thr is not None:      # nuisance: flavour-universal threshold factors (1+eps_u, 1+eps_d, 1+eps_e) at v_R
            YuL = YuL * ex(1 + thr[:, 0]); YdL = YdL * ex(1 + thr[:, 1]); YeL = YeL * ex(1 + thr[:, 2])
        M = env.vR * f
        fin = fin0 & np.all(np.isfinite(M.reshape(N, -1)), 1) & np.all(np.isfinite(YnL.reshape(N, -1)), 1)
        fin &= np.abs(np.linalg.det(np.where(fin[:, None, None], f, np.eye(3)))) > 1e-30
        M = np.where(fin[:, None, None], M, np.eye(3)); YnL = np.where(fin[:, None, None], YnL, 0)
        kap0 = np.zeros((N, 3, 3), complex)
        if typeII is not None:
            kap0 = typeII[:, None, None] * Yq1      # kappa_II = t * Y126(v_R)  (t complex per point)
        info["MR"] = takagi(M)[0]
        st2 = [np.tile(env.g_sm_vR, (N, 1)), np.full(N, env.lam_vR), np.swapaxes(YuL, 1, 2), np.swapaxes(YdL, 1, 2),
               np.swapaxes(YeL, 1, 2), kap0, np.swapaxes(YnL, 1, 2), M]
        st2 = [np.where(np.isfinite(a), a, 0) for a in st2]
        st2 = run_sm_seesaw(st2, env.vR, h_hi, h_lo, two_loop)
        g, lam, YuR, YdR, YeR, kap, Yn, Mf = st2
        fin2 = np.ones(N, bool)
        for A in (YuR, YdR, YeR, kap):
            fin2 &= np.all(np.isfinite(A.reshape(N, -1)), 1)
        fin &= fin2
        YuR, YdR, YeR = [np.where(fin[:, None, None], A, np.eye(3)) for A in (YuR, YdR, YeR)]
        kap = np.where(fin[:, None, None], kap, np.eye(3))
        o, extra = observables(np.swapaxes(YuR, 1, 2), np.swapaxes(YdR, 1, 2), np.swapaxes(YeR, 1, 2), kap * VEV**2)
    ok = ok & fin & np.all(np.isfinite(o), 1) & (o[:, 17] > 0)
    info.update(extra)
    info["cd10"] = cd10; info["cu10"] = cu10; info["cu126"] = cu126
    return o, ok, info


# ---------------------------------------------------------------------------------------------------------------
# my parametrisation p (19): [log10 h1,h2,h3 | Re F11,F22,F33,F12,F13,F23 | Im ... | log10 r | Re s | Im s | log10 cd126]
# F entries scaled: F_ij = Fscale_ij * p ; Fscale = sqrt(h_i h_j)  (dimensionless shape variables)
# ---------------------------------------------------------------------------------------------------------------
IJ = [(0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2)]


def unpack(P):
    P = np.atleast_2d(P)
    N = P.shape[0]
    h = 10.0**P[:, 0:3]
    H = np.zeros((N, 3, 3), complex); H[:, [0, 1, 2], [0, 1, 2]] = h
    F = np.zeros((N, 3, 3), complex)
    for j, (a, b) in enumerate(IJ):
        sc = np.sqrt(h[:, a] * h[:, b])
        v = (P[:, 3 + j] + 1j * P[:, 9 + j]) * sc
        F[:, a, b] = v; F[:, b, a] = v
    r = 10.0**P[:, 15]; s = P[:, 16] + 1j * P[:, 17]; cd = 10.0**P[:, 18]
    return H, F, r, s, cd


def pack(H, F, r, s, cd):
    """H must be real positive diagonal (call to_Hdiag first)."""
    N = H.shape[0]
    h = np.real(np.diagonal(H, axis1=1, axis2=2))
    P = np.zeros((N, 19))
    P[:, 0:3] = np.log10(h)
    for j, (a, b) in enumerate(IJ):
        sc = np.sqrt(h[:, a] * h[:, b])
        P[:, 3 + j] = np.real(F[:, a, b]) / sc; P[:, 9 + j] = np.imag(F[:, a, b]) / sc
    P[:, 15] = np.log10(r); P[:, 16] = np.real(s); P[:, 17] = np.imag(s); P[:, 18] = np.log10(cd)
    return P


def to_Hdiag(H, F):
    """Basis change so that H is real positive diagonal ascending: U^T H U = diag, F -> U^T F U."""
    m, U = takagi(H)
    Hd = np.swapaxes(U, 1, 2) @ H @ U
    Fd = np.swapaxes(U, 1, 2) @ F @ U
    Hd = np.zeros_like(Hd); Hd[:, [0, 1, 2], [0, 1, 2]] = m
    return Hd, Fd


class Model:
    def __init__(self, env, d, fbound=math.sqrt(4 * math.pi), ybound=1.5, wpen=100.0, **kw):
        self.env = env; self.d = d; self.fbound = fbound; self.ybound = ybound; self.wpen = wpen; self.kw = kw
        self.nev = 0

    def resid(self, P):
        P = np.atleast_2d(P)
        H, F, r, s, cd = unpack(P)
        o, ok, info = chain(H, F, r, s, cd, self.env, **self.kw)
        self.nev += P.shape[0]
        R = residuals(o, self.d)
        BAD = 1e6
        R = np.where(np.isfinite(R), R, BAD)
        R[~ok] = BAD
        ym10 = np.maximum(info["y10U"], info["y10R"]); ym126 = np.maximum(info["y126U"], info["y126R"])
        fm = np.maximum(info["fU"], info["fR"])
        pen = np.stack([self.wpen * np.clip(ym10 / self.ybound - 1, 0, None),
                        self.wpen * np.clip(ym126 / self.ybound - 1, 0, None),
                        self.wpen * np.clip(fm / self.fbound - 1, 0, None) if np.isfinite(self.fbound) else 0 * fm], 1)
        pen = np.where(np.isfinite(pen), pen, BAD)
        pen[~ok] = 0
        self.last = (o, ok, info)
        return np.concatenate([R, pen], 1)

    def chi2(self, P):
        R = self.resid(P)
        return np.sum(R * R, 1)
