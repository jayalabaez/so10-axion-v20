"""R2-C library: two-light-bidoublet 10_H + 126bar_H flavour fit for v21-F17-B63-G3221 (no Ytilde10).

CONVENTIONS (stated once, used everywhere in this file)
- Weyl, doublet-LEFT: Y_ij multiplies f_L,i f^c_j.  SO(10) Yukawas Y10, Y126 are complex symmetric.
- Left rotations: E_x = eigvecs(Y_x Y_x^dag) (= U_x^*);  CKM = E_u^T E_d^*,  PMNS = E_e^T N,  N = eigvecs(m^dag m),
  m_nu (flavour basis) = U^* D U^dag.  (Derived in REPORT; round-trip tested in test_conventions.)
- Model at M_U (standard r, s parametrisation; H = v_d^10 Y10 / v, F = v_d^126 Y126 / v):
      Yd = H + F,  Ye = H - 3F,  Yu = r (H + s F),  Ynu = r (H - 3 s F),  M_R = c_R v_R Y126 = c_R v_R F / c_d126.
  r = c_u10/c_d10 (real > 0, its phase is unphysical), s = (c_u126/c_d126)/r (complex);
  light-doublet composition (c_u10, c_u126, c_d10, c_d126) with |c_u10|^2+|c_u126|^2+|c_d10|^2+|c_d126|^2 = 1
  (CORRECTED normalisation: c_d10 = sqrt((1 - c_d126^2 (1 + |r s|^2)) / (1 + r^2)) ).
- RG: SM two-loop (gauge, Yu, Yd, Ye; Luo-Wang-Xiao, copied from round-1 rge.py and re-indexed) + one-loop
  nu^c sector with sequential decoupling below v_R; G3221 one-loop above v_R with TWO bidoublets and NO tilde couplings:
      16pi^2 dY_a/dt   = sum_b (Y_b Y_b^dag Y_a + Y_a Y_b^dag Y_b) + sum_c Y_c T_ca - G_q Y_a          (quarks)
      16pi^2 dYl_a/dt  = sum_b (Yl_b Yl_b^dag Yl_a + Yl_a Yl_b^dag Yl_b) + (3/4) Yl_a fh^dag fh + sum_c Yl_c T_ca - G_l Yl_a
      16pi^2 dfh/dt    = S^T fh + fh S + (1/2) Tr(fh^dag fh) fh - G_f fh,  S = sum_b Yl_b^dag Yl_b + (3/4) fh^dag fh
      T_ca = 3 Tr(Y_c^dag Y_a) + Tr(Yl_c^dag Yl_a);  no vertex terms (all scalars couple holomorphically: X and B-L).
      G_q = 8 g3^2 + 9/4 (gL^2 + gR^2) + 1/6 gBL^2,  G_l = 9/4 (gL^2 + gR^2) + 3/2 gBL^2,  G_f = 9/2 gR^2 + 3/2 gBL^2
      (q = (B-L)/2 normalisation, 1/gY^2 = 1/gR^2 + 1/gBL^2), fh normalised by M_R = fh v_R.
"""
import math, json, os
from fractions import Fraction as Fr
import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
K1 = 1.0 / (16 * math.pi**2)
K2 = K1 * K1
INP = json.load(open(os.path.join(HERE, "inputs_mz.json")))
VEV = INP["VEV"]          # 174.1 GeV
MZ = INP["MZ"]
MASS_KEYS = ["m_u", "m_c", "m_t", "m_d", "m_s", "m_b", "m_e", "m_mu", "m_tau"]
CKM_KEYS = ["s12", "s23", "s13", "delta"]
NU_KEYS = ["sin2_th12", "sin2_th23", "sin2_th13", "dm21", "dm31"]
ALL_KEYS = MASS_KEYS + CKM_KEYS + NU_KEYS
C_R = 2 * math.sqrt(6)    # M_R = C_R v_R Y126_def (round-1 exact Clebsch, Majorana-normalisation caveat x/÷2)
Y10_ACT = 1 / (2 * math.sqrt(2))   # Y10_act = Y10_def * Y10_ACT  (round-1 normalisation map)
Y126_ACT = math.sqrt(3) / 4

# ------------------------------------------------------------------------------------------------------------------
# data
# ------------------------------------------------------------------------------------------------------------------
NUFIT60_SK = {"sin2_th12": (0.308, 0.012), "sin2_th23": (0.470, 0.015), "sin2_th13": (0.02215, 0.00060),
              "dm21": (7.49e-5, 0.19e-5), "dm31": (2.513e-3, 0.021e-3), "delta_deg": (212.0, 35.0)}
NUFIT60_NOSK = {"sin2_th12": (0.308, 0.012), "sin2_th23": (0.561, 0.014), "sin2_th13": (0.02195, 0.00057),
                "dm21": (7.49e-5, 0.19e-5), "dm31": (2.534e-3, 0.024e-3), "delta_deg": (177.0, 20.0)}
NUFIT32_2018 = {"sin2_th12": (0.307, 0.013), "sin2_th23": (0.538, 0.069), "sin2_th13": (0.02206, 0.00075),
                "dm21": (7.40e-5, 0.21e-5), "dm31": (2.494e-3, 0.033e-3), "delta_deg": (234.0, 40.0)}


def data_set(nu="nufit60_sk", floor=0.01, lepton_floor=None):
    """Central values and 1-sigma errors at M_Z.  floor: relative theory floor added in quadrature to all 9 masses
    (lepton_floor overrides it for e, mu, tau)."""
    d = {}
    for k in MASS_KEYS:
        c, s = INP["masses_GeV_MZ"][k]
        fl = floor if (lepton_floor is None or k not in ("m_e", "m_mu", "m_tau")) else lepton_floor
        d[k] = (c, c * math.sqrt((s / c)**2 + fl**2))
    for k in CKM_KEYS:
        d[k] = tuple(INP["ckm_MZ"][k])
    P = {"nufit60_sk": NUFIT60_SK, "nufit60_nosk": NUFIT60_NOSK, "nufit32": NUFIT32_2018}[nu]
    for k in NU_KEYS:
        d[k] = P[k]
    d["delta_pmns_deg"] = P["delta_deg"]
    return d


# ------------------------------------------------------------------------------------------------------------------
# mixing matrices (scalar and batched)
# ------------------------------------------------------------------------------------------------------------------
def umix(s12, s23, s13, d):
    c12, c23, c13 = math.sqrt(1 - s12**2), math.sqrt(1 - s23**2), math.sqrt(1 - s13**2)
    e = np.exp(1j * d)
    return np.array([[c12 * c13, s12 * c13, s13 * np.conj(e)],
                     [-s12 * c23 - c12 * s23 * s13 * e, c12 * c23 - s12 * s23 * s13 * e, s23 * c13],
                     [s12 * s23 - c12 * c23 * s13 * e, -c12 * s23 - s12 * c23 * s13 * e, c23 * c13]])


def umix_b(th12, th13, th23, d):
    """Batched standard-parametrisation unitary from ANGLES (any real values) -> (N,3,3)."""
    s12, c12 = np.sin(th12), np.cos(th12)
    s13, c13 = np.sin(th13), np.cos(th13)
    s23, c23 = np.sin(th23), np.cos(th23)
    e = np.exp(1j * d)
    N = th12.shape[0]
    U = np.empty((N, 3, 3), complex)
    U[:, 0, 0] = c12 * c13; U[:, 0, 1] = s12 * c13; U[:, 0, 2] = s13 * np.conj(e)
    U[:, 1, 0] = -s12 * c23 - c12 * s23 * s13 * e; U[:, 1, 1] = c12 * c23 - s12 * s23 * s13 * e; U[:, 1, 2] = s23 * c13
    U[:, 2, 0] = s12 * s23 - c12 * c23 * s13 * e; U[:, 2, 1] = -c12 * s23 - s12 * c23 * s13 * e; U[:, 2, 2] = c23 * c13
    return U


def angles_b(V):
    """Batched angles: returns s12, s23, s13, delta (delta in (-pi, pi]) for (N,3,3) unitary V."""
    A = np.abs(V)
    s13 = np.clip(A[:, 0, 2], 0, 1)
    c13 = np.sqrt(np.clip(1 - s13**2, 1e-300, None))
    s12 = np.clip(A[:, 0, 1] / c13, 0, 1)
    s23 = np.clip(A[:, 1, 2] / c13, 0, 1)
    c12 = np.sqrt(np.clip(1 - s12**2, 0, None)); c23 = np.sqrt(np.clip(1 - s23**2, 0, None))
    J = (V[:, 0, 0] * V[:, 1, 1] * np.conj(V[:, 0, 1]) * np.conj(V[:, 1, 0])).imag
    den = c12 * s12 * c23 * s23 * c13**2 * s13
    den = np.where(np.abs(den) < 1e-300, 1e-300, den)
    sind = J / den
    num = A[:, 1, 0]**2 - (s12 * c23)**2 - (c12 * s23 * s13)**2
    cosd = num / (2 * s12 * c23 * c12 * s23 * s13 + 1e-300)
    return s12, s23, s13, np.arctan2(sind, cosd)


def herm(M):
    return np.conj(np.swapaxes(M, -1, -2))


# ------------------------------------------------------------------------------------------------------------------
# observables from Yukawas (scalar, doublet-left convention)
# ------------------------------------------------------------------------------------------------------------------
def observables(Yu, Yd, Ye, mnu, v=VEV):
    Yb = np.stack([Yu, Yd, Ye])
    w, E = np.linalg.eigh(Yb @ herm(Yb))
    sv = np.sqrt(np.clip(w, 0, None)) * v
    Eu, Ed, Ee = E[0], E[1], E[2]
    V = Eu.T @ Ed.conj()
    s12, s23, s13, dl = [float(x[0]) for x in angles_b(V[None])]
    wn, N = np.linalg.eigh(mnu.conj().T @ mnu)
    mn = np.sqrt(np.clip(wn, 0, None))
    U = Ee.T @ N
    n12, n23, n13, nd = [float(x[0]) for x in angles_b(U[None])]
    o = {"m_u": sv[0, 0], "m_c": sv[0, 1], "m_t": sv[0, 2], "m_d": sv[1, 0], "m_s": sv[1, 1], "m_b": sv[1, 2],
         "m_e": sv[2, 0], "m_mu": sv[2, 1], "m_tau": sv[2, 2], "s12": s12, "s23": s23, "s13": s13, "delta": dl,
         "sin2_th12": n12**2, "sin2_th23": n23**2, "sin2_th13": n13**2, "delta_pmns": nd,
         "dm21": (mn[1]**2 - mn[0]**2) * 1e18, "dm31": (mn[2]**2 - mn[0]**2) * 1e18, "m_nu_eV": (mn * 1e9).tolist()}
    # Majorana phases and m_betabeta (PDG convention U = V(delta) diag(1, e^{i a21/2}, e^{i a31/2}))
    o["U_pmns"] = U
    return o


def mbb_and_majorana(U, mn_eV):
    """|m_bb| = |sum_i U_ei^2 m_i| (rephasing-invariant modulus; mn in eV)."""
    return float(abs(np.sum(U[0, :]**2 * np.array(mn_eV))))


def pulls(o, d):
    pl = {}
    for k in ALL_KEYS:
        c, s = d[k]
        if k in MASS_KEYS:
            pl[k] = math.log(max(o[k], 1e-300) / c) * c / s
        elif k == "delta":
            pl[k] = ((abs(o[k]) - c + math.pi) % (2 * math.pi) - math.pi) / s
        else:
            pl[k] = (o[k] - c) / s
    return pl


# ------------------------------------------------------------------------------------------------------------------
# G3221 one-loop b coefficients (exact Fractions), q = (B-L)/2 normalisation
# ------------------------------------------------------------------------------------------------------------------
T3D = {1: Fr(0), 3: Fr(1, 2), 6: Fr(5, 2), 8: Fr(3)}
T2D = {1: Fr(0), 2: Fr(1, 2), 3: Fr(2)}


def b_rep(d3, dL, dR, q, kind):
    f = {"weyl": Fr(2, 3), "cplx": Fr(1, 3), "real": Fr(1, 6)}[kind]
    n = d3 * dL * dR
    return [f * T3D[d3] * dL * dR, f * T2D[dL] * d3 * dR, f * T2D[dR] * d3 * dL, f * Fr(q)**2 * n]


def addv(*rows):
    return [sum(r[i] for r in rows) for i in range(4)]


ONE16 = addv(b_rep(3, 2, 1, Fr(1, 6), "weyl"), b_rep(3, 1, 2, Fr(-1, 6), "weyl"), b_rep(1, 2, 1, Fr(-1, 2), "weyl"),
             b_rep(1, 1, 2, Fr(1, 2), "weyl"))
ONE10 = addv(b_rep(1, 2, 2, 0, "weyl"), b_rep(3, 1, 1, Fr(-1, 3), "weyl"), b_rep(3, 1, 1, Fr(1, 3), "weyl"))
GAUGE = [Fr(-11), Fr(-22, 3), Fr(-22, 3), Fr(0)]
SCAL = {"bid": b_rep(1, 2, 2, 0, "cplx"), "DR": b_rep(1, 1, 3, 1, "cplx"), "831": b_rep(8, 3, 1, 0, "real"),
        "822": b_rep(8, 2, 2, 0, "cplx"), "131": b_rep(1, 3, 1, 0, "real"), "811": b_rep(8, 1, 1, 0, "real")}
CONTENTS = {
    "C2": ["bid", "bid", "DR", "831"],            # two light bidoublets + (8,3,1)_0 + Delta_R  (R2 default)
    "C2m": ["bid", "bid", "DR"],                  # without the colour octet (RG-robustness variant)
    "T3": ["bid", "bid", "DR", "831", "822", "131", "811"],
}


def b_g3221(content="C2", s_sector=True):
    rows = [GAUGE] + [ONE16] * 3
    if s_sector:      # B63: 4 x (16 + 16bar) [3 conj-S pairs + 1 Phi17 pair] + 2 x 10_F
        rows += [ONE16] * 8 + [ONE10] * 2
    rows += [SCAL[k] for k in CONTENTS[content]]
    return addv(*rows)


B63_SM_SHIFT = 12.0     # complete SO(10) multiplets 4 x (16+16bar) + 2 x 10 (Weyl): +12 to each SM b_i above M_s


# ------------------------------------------------------------------------------------------------------------------
# SM RG: two-loop gauge + Yukawa (doublet-RIGHT internally, as in round-1 rge.py), one-loop nu^c sector, kappa
# ------------------------------------------------------------------------------------------------------------------
def _sm_core(g, lam, Yu, Yd, Ye, Yn, db):
    """All matrices in doublet-RIGHT convention (index order f^c, f_L).  Yn may be None or (k x 3) for k active nu^c."""
    g1, g2, g3 = g
    Uu, Dd, Ee = herm(Yu) @ Yu, herm(Yd) @ Yd, herm(Ye) @ Ye
    Nn = herm(Yn) @ Yn if Yn is not None and Yn.shape[0] > 0 else np.zeros((3, 3), complex)
    tu, td, te, tn = np.trace(Uu).real, np.trace(Dd).real, np.trace(Ee).real, np.trace(Nn).real
    T = 3 * tu + 3 * td + te + tn
    g1s, g2s, g3s = g1 * g1, g2 * g2, g3 * g3
    b = np.array([41 / 10, -19 / 6, -7]) + db
    B = np.array([[199 / 50, 27 / 10, 44 / 5], [9 / 10, 35 / 6, 12], [11 / 10, 9 / 2, -26]])
    cu, cd, ce = np.array([17 / 10, 3 / 2, 2]), np.array([1 / 2, 3 / 2, 2]), np.array([3 / 2, 1 / 2, 0])
    ga = np.array([g1, g2, g3]); gs = ga * ga
    dg = K1 * b * ga**3 + K2 * ga**3 * (B @ gs - (cu * tu + cd * td + ce * te))
    Gu = 17 / 20 * g1s + 9 / 4 * g2s + 8 * g3s
    Gd = 1 / 4 * g1s + 9 / 4 * g2s + 8 * g3s
    Ge = 9 / 4 * g1s + 9 / 4 * g2s
    Gn = 9 / 20 * g1s + 9 / 4 * g2s
    I3 = np.eye(3)
    bu1 = Yu @ (1.5 * (Uu - Dd) + (T - Gu) * I3)
    bd1 = Yd @ (1.5 * (Dd - Uu) + (T - Gd) * I3)
    be1 = Ye @ (1.5 * (Ee - Nn) + (T - Ge) * I3)
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
    H4 = 3 * np.trace(Uu @ Uu).real + 3 * np.trace(Dd @ Dd).real + np.trace(Ee @ Ee).real + np.trace(Nn @ Nn).real
    dlam = K1 * (12 * lam**2 - (9 / 5 * g1s + 9 * g2s) * lam + 9 / 4 * (3 / 25 * g1s**2 + 2 / 5 * g1s * g2s + g2s**2)
                 + 4 * lam * T - 4 * H4)
    dYn = None
    if Yn is not None and Yn.shape[0] > 0:
        dYn = K1 * Yn @ (1.5 * (Nn - Ee) + (T - Gn) * I3)
    return dg, dlam, dYu, dYd, dYe, dYn, Ee, Nn, T, g2s


class SMState:
    """SM (+ active nu^c) state in doublet-LEFT convention for the public interface."""
    def __init__(self, g, lam, Yu, Yd, Ye, kappa, Yn=None, MR=None):
        self.g = np.array(g, float); self.lam = float(lam)
        self.Yu, self.Yd, self.Ye = Yu, Yd, Ye
        self.kappa = kappa                                   # symmetric 3x3, m_nu = kappa v^2 (GeV units / GeV^2)
        self.Yn = Yn if Yn is not None else np.zeros((3, 0), complex)   # 3 x k, doublet-left
        self.MR = MR if MR is not None else np.zeros((0, 0), complex)   # k x k symmetric


def _pack_sm(st):
    k = st.Yn.shape[1]
    y = [st.g[0], st.g[1], st.g[2], st.lam]
    for M in (st.Yu, st.Yd, st.Ye, st.kappa):
        y += list(M.real.ravel()) + list(M.imag.ravel())
    if k:
        y += list(st.Yn.real.ravel()) + list(st.Yn.imag.ravel())
        y += list(st.MR.real.ravel()) + list(st.MR.imag.ravel())
    return np.array(y, float), k


def _unpack_sm(y, k):
    g = y[0:3]; lam = y[3]; i = 4
    out = []
    for _ in range(4):
        out.append((y[i:i + 9] + 1j * y[i + 9:i + 18]).reshape(3, 3)); i += 18
    Yn = np.zeros((3, 0), complex); MR = np.zeros((0, 0), complex)
    if k:
        Yn = (y[i:i + 3 * k] + 1j * y[i + 3 * k:i + 6 * k]).reshape(3, k); i += 6 * k
        MR = (y[i:i + k * k] + 1j * y[i + k * k:i + 2 * k * k]).reshape(k, k); i += 2 * k * k
    return SMState(g, lam, out[0], out[1], out[2], out[3], Yn, MR)


def _sm_rhs(t, y, k, db):
    st = _unpack_sm(y, k)
    YuR, YdR, YeR = st.Yu.T, st.Yd.T, st.Ye.T
    YnR = st.Yn.T if k else None                              # k x 3 (nu^c, L)
    dg, dlam, dYuR, dYdR, dYeR, dYnR, Ee, Nn, T, g2s = _sm_core(st.g, st.lam, YuR, YdR, YeR, YnR, db)
    kap = st.kappa
    # Weinberg operator (doublet indices): -3/2 [kap Ee + Ee^T kap] + 1/2 [kap Nn + Nn^T kap] + (2T + lam - 3 g2^2) kap
    dk = K1 * (-1.5 * (kap @ Ee + Ee.T @ kap) + 0.5 * (kap @ Nn + Nn.T @ kap) + (2 * T + st.lam - 3 * g2s) * kap)
    out = [dg[0], dg[1], dg[2], dlam]
    for M in (dYuR.T, dYdR.T, dYeR.T, dk):
        out += list(M.real.ravel()) + list(M.imag.ravel())
    if k:
        dYn = dYnR.T
        P = YnR @ herm(YnR)                                   # (nu^c, nu^c)
        dM = K1 * (P @ st.MR + st.MR @ P.T)
        out += list(dYn.real.ravel()) + list(dYn.imag.ravel())
        out += list(dM.real.ravel()) + list(dM.imag.ravel())
    return out


def run_sm(st, mu0, mu1, db=0.0, rtol=1e-7):
    y0, k = _pack_sm(st)
    sol = solve_ivp(_sm_rhs, (math.log(mu0), math.log(mu1)), y0, args=(k, db), method="DOP853", rtol=rtol, atol=1e-13)
    if not sol.success:
        raise RuntimeError("SM RG failed: " + sol.message)
    return _unpack_sm(sol.y[:, -1], k)


def takagi(M):
    """M symmetric complex: returns (masses ascending, U) with U^T M U = diag(m) >= 0."""
    w, V = np.linalg.eigh(herm(M) @ M)
    m = np.sqrt(np.clip(w, 0, None))
    # fix phases: D = V^T M V should be diagonal; absorb phases
    D = V.T @ M @ V
    ph = np.exp(-0.5j * np.angle(np.diag(D)))
    U = V * ph[None, :]
    return m, U


def decouple_heaviest(st):
    """Integrate out the heaviest active nu^c at tree level: kappa += -Yn_n Yn_n^T / M_n (doublet-left)."""
    k = st.Yn.shape[1]
    m, U = takagi(st.MR)                                      # U^T MR U = diag(m)
    Yn = st.Yn @ U                                            # rotate nu^c basis
    MRd = np.diag(m).astype(complex)
    n = k - 1                                                 # heaviest (ascending order)
    col = Yn[:, n:n + 1]
    kap = st.kappa - (col @ col.T) / m[n]
    st2 = SMState(st.g, st.lam, st.Yu, st.Yd, st.Ye, kap, Yn[:, :n], MRd[:n, :n])
    return st2, m[n]


def run_sm_with_seesaw(st, mu_top, mu_bot, db_func=None, rtol=1e-7, thresholds_extra=()):
    """Run down from mu_top to mu_bot, integrating out nu^c sequentially at their masses (tree-level matching)
    and switching the one-loop gauge shift db_func(mu) at the scales in thresholds_extra (descending)."""
    mu = mu_top
    st = st
    # immediately integrate out any nu^c heavier than mu_top
    while st.Yn.shape[1] > 0:
        m, _ = takagi(st.MR)
        if m[-1] >= mu:
            st, _ = decouple_heaviest(st)
        else:
            break
    while True:
        k = st.Yn.shape[1]
        nxt = mu_bot
        from_nu = False
        if k:
            m, _ = takagi(st.MR)
            if m[-1] > mu_bot:
                nxt = m[-1]; from_nu = True
        for th in thresholds_extra:
            if mu_bot < th < mu and th > nxt:
                nxt = th; from_nu = False
        db = db_func(math.sqrt(mu * nxt)) if db_func else 0.0
        if nxt < mu:
            st = run_sm_fast(st, mu, nxt, db=db, rtol=rtol)
        mu = nxt
        if from_nu:
            st, _ = decouple_heaviest(st)        # running mass evaluated at the start of the interval (1-loop accurate)
            continue
        if mu <= mu_bot * (1 + 1e-12):
            break
    while st.Yn.shape[1] > 0:                                 # any nu^c below M_Z (not expected)
        st, _ = decouple_heaviest(st)
    return st


# ------------------------------------------------------------------------------------------------------------------
# gauge couplings: M_Z inputs, SM running to v_R, G3221 above (one loop), M_U from g3 = gL
# ------------------------------------------------------------------------------------------------------------------
def gauge_mz():
    a_em = 1 / INP["gauge_MZ"]["alpha_em_inv"]; s2 = INP["gauge_MZ"]["sin2_thw_MSbar"]; a_s = INP["gauge_MZ"]["alpha_s"]
    g1 = math.sqrt(4 * math.pi * a_em / (1 - s2) * 5 / 3); g2 = math.sqrt(4 * math.pi * a_em / s2); g3 = math.sqrt(4 * math.pi * a_s)
    return np.array([g1, g2, g3])


M_S = 1.0e13      # B63 vector-like 16+16bar / 10_F masses (y_s <S> ~ 1e13, quality window reference)


def db_sm(mu):
    return B63_SM_SHIFT if mu > M_S else 0.0


def g3221_couplings(vR, g_sm_vR, content="C2", MU=None):
    """Return dict with b's (below/above M_S), M_U (g3 = gL one-loop crossing unless given), couplings at vR and MU.
    gR(vR) fixed by gR(MU) = gL(MU); gBL from 1/gY^2 = 1/gR^2 + 1/gBL^2 (q = (B-L)/2)."""
    g1, g2, g3 = g_sm_vR
    b_lo = np.array([float(x) for x in b_g3221(content, s_sector=False)])
    b_hi = np.array([float(x) for x in b_g3221(content, s_sector=True)])

    def inv_a(inv0, b, mu0, mu1):
        return inv0 - b / (2 * math.pi) * math.log(mu1 / mu0)

    def couplings_at(mu, inv_vR):
        if mu <= M_S or vR >= M_S:
            if vR >= M_S:
                return inv_a(inv_vR, b_hi, vR, mu)
            return inv_a(inv_vR, b_lo, vR, mu)
        invS = inv_a(inv_vR, b_lo, vR, M_S)
        return inv_a(invS, b_hi, M_S, mu)
    a3, aL = 4 * math.pi / g3**2, 4 * math.pi / g2**2
    inv_vR = np.array([a3, aL, aL, 1.0])
    if MU is None:
        lo, hi = math.log(vR * 1.0001), math.log(1e19)
        f = lambda L: couplings_at(math.exp(L), inv_vR)[0] - couplings_at(math.exp(L), inv_vR)[1]
        if f(lo) * f(hi) < 0:
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if f(lo) * f(mid) <= 0:
                    hi = mid
                else:
                    lo = mid
            MU = math.exp(0.5 * (lo + hi))
            mu_status = "g3=gL one-loop crossing"
        else:
            MU = 2e16
            mu_status = "no g3=gL crossing below 1e19: M_U fixed at 2e16"
    else:
        mu_status = "given"
    invU = couplings_at(MU, inv_vR)
    aL_U = invU[1]
    # gR: alpha_R^-1(MU) = alpha_L^-1(MU)  ->  run down with b_R
    if vR >= M_S:
        aR_vR = aL_U + b_hi[2] / (2 * math.pi) * math.log(MU / vR)
    elif MU <= M_S:
        aR_vR = aL_U + b_lo[2] / (2 * math.pi) * math.log(MU / vR)
    else:
        aR_S = aL_U + b_hi[2] / (2 * math.pi) * math.log(MU / M_S)
        aR_vR = aR_S + b_lo[2] / (2 * math.pi) * math.log(M_S / vR)
    gY = math.sqrt(3 / 5) * g1
    aY = 4 * math.pi / gY**2
    aBL_vR = aY - aR_vR
    status_bl = "ok"
    if aBL_vR <= 0.5:
        # fallback: gR = gL at vR
        aR_vR = aL
        aBL_vR = aY - aR_vR
        status_bl = "fallback gR(vR) = gL(vR)"
    inv_vR = np.array([a3, aL, aR_vR, aBL_vR])
    invU = couplings_at(MU, inv_vR)
    gs_vR = np.sqrt(4 * math.pi / inv_vR)
    gs_U = np.sqrt(4 * math.pi / np.clip(invU, 1e-6, None))
    return {"vR": vR, "MU": MU, "MU_status": mu_status, "gBL_status": status_bl, "b_lo": b_lo.tolist(), "b_hi": b_hi.tolist(),
            "alpha_inv_vR": inv_vR.tolist(), "alpha_inv_MU": invU.tolist(), "g_vR": gs_vR.tolist(), "g_MU": gs_U.tolist(),
            "alpha_BL_GUT_inv_MU": float(invU[3] * 2 / 3)}


# ------------------------------------------------------------------------------------------------------------------
# G3221 two-bidoublet one-loop RG (doublet-left)
# ------------------------------------------------------------------------------------------------------------------
def _pack_g(g, Yq, Yl, fh):
    y = list(g)
    for M in list(Yq) + list(Yl) + [fh]:
        y += list(M.real.ravel()) + list(M.imag.ravel())
    return np.array(y, float)


def _unpack_g(y):
    g = y[0:4]; i = 4; Ms = []
    for _ in range(5):
        Ms.append((y[i:i + 9] + 1j * y[i + 9:i + 18]).reshape(3, 3)); i += 18
    return g, Ms[0:2], Ms[2:4], Ms[4]


def _g3221_rhs(t, y, b_lo, b_hi, lnMS):
    g, Yq, Yl, fh = _unpack_g(y)
    b = b_hi if t > lnMS else b_lo
    g3, gL, gR, gBL = g
    Gq = 8 * g3**2 + 9 / 4 * (gL**2 + gR**2) + gBL**2 / 6
    Gl = 9 / 4 * (gL**2 + gR**2) + 1.5 * gBL**2
    Gf = 4.5 * gR**2 + 1.5 * gBL**2
    SLq = sum(Y @ herm(Y) for Y in Yq); SRq = sum(herm(Y) @ Y for Y in Yq)
    FF = herm(fh) @ fh
    SLl = sum(Y @ herm(Y) for Y in Yl); SRl = sum(herm(Y) @ Y for Y in Yl) + 0.75 * FF
    Tm = np.array([[3 * np.trace(herm(Yq[c]) @ Yq[a]) + np.trace(herm(Yl[c]) @ Yl[a]) for a in range(2)] for c in range(2)])
    dq = [K1 * (SLq @ Yq[a] + Yq[a] @ SRq + Yq[0] * Tm[0, a] + Yq[1] * Tm[1, a] - Gq * Yq[a]) for a in range(2)]
    dl = [K1 * (SLl @ Yl[a] + Yl[a] @ SRl + Yl[0] * Tm[0, a] + Yl[1] * Tm[1, a] - Gl * Yl[a]) for a in range(2)]
    df = K1 * (SRl.T @ fh + fh @ SRl + 0.5 * np.trace(FF).real * fh - Gf * fh)
    dg = K1 * b * g**3
    return _pack_g(dg, dq, dl, df)


def run_g3221(g_MU, Yq, Yl, fh, MU, vR, b_lo, b_hi, rtol=1e-7):
    y0 = _pack_g(g_MU, Yq, Yl, fh)
    sol = solve_ivp(_g3221_rhs, (math.log(MU), math.log(vR)), y0, args=(np.array(b_lo), np.array(b_hi), math.log(M_S)),
                    method="DOP853", rtol=rtol, atol=1e-13)
    if not sol.success:
        raise RuntimeError("G3221 RG failed: " + sol.message)
    return _unpack_g(sol.y[:, -1])


# ------------------------------------------------------------------------------------------------------------------
# fixed-step RK4 drivers (speed; validated against DOP853 in test_rk4.py)
# ------------------------------------------------------------------------------------------------------------------
RK4_H = 0.5


def _rk4(f, t0, t1, y, args, h=None):
    h = h or RK4_H
    n = max(2, int(math.ceil(abs(t1 - t0) / h)))
    dt = (t1 - t0) / n
    t = t0
    y = np.array(y, float)
    for _ in range(n):
        k1 = np.asarray(f(t, y, *args))
        k2 = np.asarray(f(t + dt / 2, y + dt / 2 * k1, *args))
        k3 = np.asarray(f(t + dt / 2, y + dt / 2 * k2, *args))
        k4 = np.asarray(f(t + dt, y + dt * k3, *args))
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
    return y


USE_RK4 = False


def run_sm_fast(st, mu0, mu1, db=0.0, rtol=1e-7):
    if not USE_RK4:
        return run_sm(st, mu0, mu1, db, rtol)
    y0, k = _pack_sm(st)
    return _unpack_sm(_rk4(_sm_rhs, math.log(mu0), math.log(mu1), y0, (k, db)), k)


def run_g3221_fast(g_MU, Yq, Yl, fh, MU, vR, b_lo, b_hi, rtol=1e-7):
    if not USE_RK4:
        return run_g3221(g_MU, Yq, Yl, fh, MU, vR, b_lo, b_hi, rtol)
    y0 = _pack_g(g_MU, Yq, Yl, fh)
    lnMS = math.log(M_S)
    t0, t1 = math.log(MU), math.log(vR)
    args = (np.array(b_lo), np.array(b_hi), lnMS)
    if t1 < lnMS < t0:      # split at the S-sector threshold
        y = _rk4(_g3221_rhs, t0, lnMS, y0, args)
        y = _rk4(_g3221_rhs, lnMS, t1, y, args)
    else:
        y = _rk4(_g3221_rhs, t0, t1, y0, args)
    return _unpack_g(y)


def tau_factors(g_MU, Yq, Yl, MU, vR, b_lo, b_hi, n=40):
    """Universal per-bidoublet wave-function factors tau_a = exp(K1 int T_aa dt) along a (frozen-Yukawa x gauge-scaled)
    flow; used only to map proxy matrices to GUT inputs for the starting point (exactness not required)."""
    out = []
    for a in range(2):
        Taa = 3 * np.trace(herm(Yq[a]) @ Yq[a]).real + np.trace(herm(Yl[a]) @ Yl[a]).real
        out.append(math.exp(K1 * Taa * math.log(MU / vR)))
    return out
