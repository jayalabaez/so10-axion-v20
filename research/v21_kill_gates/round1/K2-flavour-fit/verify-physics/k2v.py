"""K2 verifier (physics lens): independent GUT-scale fit of the 10_H + 126bar_H Yukawa sector with a free light-doublet
composition (the T3 situation), in the d-diagonal W-parametrisation; plus the structural T2 check (Yu proportional to Yd).

Conventions (mine, stated once): Y_ij multiplies (f_L)_i (f^c)_j (Weyl, SO(10)-symmetric Yukawas are symmetric 3x3).
Left rotations come from eigh(Y Y^dag).  The researcher's rge.py implements the Machacek-Vaughn/LWX/Antusch form in the
(f^c)_i (f_L)_j convention, so it is called ONLY with transposed Yukawas (verified: the CKM then runs by +13% in s23 to
2e16 as it must in the SM; with the researcher's own feed it does not run at all).

Model at M_U (d-diagonal basis):  Yd = diag(yd, ys, yb), Ye = W diag(ye, ymu, ytau) W^T, W in U(3) (3 angles, 6 phases),
H = (3 Yd + Ye)/4, F = (Yd - Ye)/4, Yu = r (H + s F) (r real), Yn = r (H - 3 s F), M_R = F / rho,
m_nu(v_R) = - rnu^2 v^2 Yn F^{-1} Yn^T rho  (rho real; fixed analytically from the two Delta m^2).
Free parameters: W (9), r (1), s (2), rho (1) = 13, plus the six pinned d/e masses in 'free' mode (19 total, as in the
general count: Y10 real diagonal 3 + Y126 complex symmetric 12 + r 1 + s 2 + v_R-scale 1 = 19 for 18 observables).
"""
import sys, os, json, math, time
import numpy as np
from scipy.optimize import least_squares, differential_evolution

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "res")
sys.path.insert(0, RES)
import rge  # researcher's RGE, read-only copy; used in its native (f^c, f_L) convention via transposed feed

K1 = 1 / (16 * math.pi**2)
inp = json.load(open(os.path.join(RES, "inputs_mz.json")))
VEV = inp["VEV"]; MZ = inp["MZ"]
MASS_KEYS = ["m_u", "m_c", "m_t", "m_d", "m_s", "m_b", "m_e", "m_mu", "m_tau"]
CKM_KEYS = ["s12", "s23", "s13", "delta"]
NU_KEYS = ["sin2_th12", "sin2_th23", "sin2_th13", "dm21", "dm31"]
ALL_KEYS = MASS_KEYS + CKM_KEYS + NU_KEYS

def H(m):
    return m.conj().T

def umix(s12, s23, s13, d):
    c12, c23, c13 = math.sqrt(1 - s12**2), math.sqrt(1 - s23**2), math.sqrt(1 - s13**2)
    e = np.exp(1j * d)
    return np.array([[c12 * c13, s12 * c13, s13 * np.conj(e)],
                     [-s12 * c23 - c12 * s23 * s13 * e, c12 * c23 - s12 * s23 * s13 * e, s23 * c13],
                     [s12 * s23 - c12 * c23 * s13 * e, -c12 * s23 - s12 * c23 * s13 * e, c23 * c13]])

def angles_from(V):
    """Standard-parametrisation angles and Dirac phase from the moduli and the Jarlskog invariant."""
    s13 = min(abs(V[0, 2]), 1.0); c13 = math.sqrt(max(1 - s13**2, 1e-300))
    s12 = min(abs(V[0, 1]) / c13, 1.0); s23 = min(abs(V[1, 2]) / c13, 1.0)
    c12 = math.sqrt(max(1 - s12**2, 0.0)); c23 = math.sqrt(max(1 - s23**2, 0.0))
    J = (V[0, 0] * V[1, 1] * np.conj(V[0, 1]) * np.conj(V[1, 0])).imag
    den = c12 * s12 * c23 * s23 * c13**2 * s13
    sind = J / den if den > 1e-300 else 0.0
    num = abs(V[1, 0])**2 - (s12 * c23)**2 - (c12 * s23 * s13)**2
    cosd = num / (2 * s12 * c23 * c12 * s23 * s13) if den > 1e-300 else 1.0
    return s12, s23, s13, math.atan2(sind, cosd)

def left_unitary(Y):
    """eigh(Y Y^dag): columns = conj of the left mass-eigenstate rotation, ascending singular values."""
    w, E = np.linalg.eigh(Y @ H(Y))
    return E, np.sqrt(np.clip(w, 0, None))

def observables(Yu, Yd, Ye, mnu, v=VEV):
    Eu, su = left_unitary(Yu); Ed, sd = left_unitary(Yd); Ee, se = left_unitary(Ye)
    V = H(Eu) @ Ed                       # = conj(V_CKM) in my convention; moduli identical, delta -> -delta (immaterial for chi2)
    s12, s23, s13, dl = angles_from(V)
    wn, N = np.linalg.eigh(H(mnu) @ mnu)   # m = U* D U^dag  =>  m^dag m = U D^2 U^dag
    mn = np.sqrt(np.clip(wn, 0, None))
    U = Ee.T @ N                         # = U_PMNS (moduli)
    n12, n23, n13, nd = angles_from(U)
    o = {"m_u": su[0] * v, "m_c": su[1] * v, "m_t": su[2] * v, "m_d": sd[0] * v, "m_s": sd[1] * v, "m_b": sd[2] * v,
         "m_e": se[0] * v, "m_mu": se[1] * v, "m_tau": se[2] * v, "s12": s12, "s23": s23, "s13": s13, "delta": dl,
         "sin2_th12": n12**2, "sin2_th23": n23**2, "sin2_th13": n13**2, "delta_pmns_deg": math.degrees(nd) % 360,
         "dm21": (mn[1]**2 - mn[0]**2) * 1e18, "dm31": (mn[2]**2 - mn[0]**2) * 1e18, "m_nu_eV": list(mn * 1e9)}
    return o

# ------------------------------------------------------------------------------------------------------------------
# G3221 one-loop b coefficients (independent re-derivation; q = (B-L)/2, non-GUT-normalised)
# ------------------------------------------------------------------------------------------------------------------
def b_g3221(content="T2"):
    # (dim3, dim2L, dim2R, q, multiplicity, kind) ; Dynkin index: fund 1/2, adj N, sextet 5/2 ; Weyl fermions 2/3, complex scalars 1/3
    def T3(d):
        return {1: 0, 3: 0.5, 6: 2.5, 8: 3}[d]
    def T2(d):
        return {1: 0, 2: 0.5, 3: 2}[d]
    F = [(3, 2, 1, 1 / 6), (3, 1, 2, 1 / 6), (1, 2, 1, -1 / 2), (1, 1, 2, -1 / 2)]            # one 16
    b = np.array([-11.0, -22 / 3, -22 / 3, 0.0])
    n16 = 3 + 6            # 3 chiral + 3 vector-like pairs (16+16bar) of the S-sector, all counted above v_R
    for (d3, dL, dR, q) in F:
        mult = dL * dR * d3
        b += (2 / 3) * n16 * np.array([T3(d3) * dL * dR, T2(dL) * d3 * dR, T2(dR) * d3 * dL, mult * q * q])
    for _ in range(2):     # two 10_F : (3,1,1,-1/3) + (3bar,1,1,+1/3) + (1,2,2,0)
        for (d3, dL, dR, q) in [(3, 1, 1, -1 / 3), (3, 1, 1, 1 / 3), (1, 2, 2, 0)]:
            mult = dL * dR * d3
            b += (2 / 3) * np.array([T3(d3) * dL * dR, T2(dL) * d3 * dR, T2(dR) * d3 * dL, mult * q * q])
    S = [(1, 2, 2, 0), (1, 1, 3, 1), (8, 2, 2, 0), (8, 3, 1, 0), (1, 3, 1, 0)]
    if content == "T3":
        S += [(1, 2, 2, 0), (8, 1, 1, 0)]
    for (d3, dL, dR, q) in S:
        mult = dL * dR * d3
        b += (1 / 3) * np.array([T3(d3) * dL * dR, T2(dL) * d3 * dR, T2(dR) * d3 * dL, mult * q * q])
    return b

# ------------------------------------------------------------------------------------------------------------------
# targets at M_U (data run up) and the neutrino targets at v_R
# ------------------------------------------------------------------------------------------------------------------
def gauge_g3221(vR, MU, content, g_sm_vR):
    g1R, g2R, g3R = g_sm_vR
    b = b_g3221(content)
    L = math.log(MU / vR)
    up = lambda g, bi: 1 / math.sqrt(1 / g**2 - bi * L / (8 * math.pi**2))
    g3U, gLU = up(g3R, b[0]), up(g2R, b[1])
    gRU = gLU
    gRR = 1 / math.sqrt(1 / gRU**2 + b[2] * L / (8 * math.pi**2))
    gp = math.sqrt(3 / 5) * g1R
    gBLR = 1 / math.sqrt(1 / gp**2 - 1 / gRR**2)
    gBLU = up(gBLR, b[3])
    return b, [g3R, g2R, gRR, gBLR], [g3U, gLU, gRU, gBLU]

def build_targets(vR, MU, content, floor=0.01, lepton_floor=None):
    m = {k: inp["masses_GeV_MZ"][k][0] for k in MASS_KEYS}
    s12, s23, s13, dl = [inp["ckm_MZ"][k][0] for k in CKM_KEYS]
    V = umix(s12, s23, s13, dl)
    Yu = np.diag([m["m_u"], m["m_c"], m["m_t"]]).astype(complex) / VEV
    Yd = (V @ np.diag([m["m_d"], m["m_s"], m["m_b"]])).astype(complex) / VEV       # (left,right): Yd Yd^dag = V D^2 V^dag
    Ye = np.diag([m["m_e"], m["m_mu"], m["m_tau"]]).astype(complex) / VEV
    p = inp["pmns"]
    U = umix(math.sqrt(p["sin2_th12"][0]), math.sqrt(p["sin2_th23"][0]), math.sqrt(p["sin2_th13"][0]), math.radians(p["delta_deg"][0]))
    mn = np.array([0.0, math.sqrt(p["dm21"][0]), math.sqrt(p["dm31"][0])]) * 1e-9
    mnu = U.conj() @ np.diag(mn) @ H(U)                                                   # m = U* D U^dag
    # self-test: round trip at MZ
    o = observables(Yu, Yd, Ye, mnu)
    chk = max(abs(o["s12"] - s12), abs(o["s23"] - s23), abs(o["s13"] - s13), abs(abs(o["delta"]) - dl),
              abs(o["sin2_th12"] - p["sin2_th12"][0]), abs(o["sin2_th23"] - p["sin2_th23"][0]), abs(o["sin2_th13"] - p["sin2_th13"][0]))
    assert chk < 1e-9, chk
    # SM two-loop running MZ -> vR (researcher's rge in its native convention: transposed feed)
    a_em = 1 / inp["gauge_MZ"]["alpha_em_inv"]; s2 = inp["gauge_MZ"]["sin2_thw_MSbar"]; a_s = inp["gauge_MZ"]["alpha_s"]
    g1 = math.sqrt(4 * math.pi * a_em / (1 - s2) * 5 / 3); g2 = math.sqrt(4 * math.pi * a_em / s2); g3 = math.sqrt(4 * math.pi * a_s)
    y = rge.pack_sm([g1, g2, g3], 0.26, Yu.T, Yd.T, Ye.T, mnu / VEV**2)
    y = rge.run_sm(y, MZ, vR, True)
    g_vR, lam_vR, YuT, YdT, YeT, kap = rge.unpack_sm(y, True)
    Yu_vR, Yd_vR, Ye_vR = YuT.T, YdT.T, YeT.T
    mnu_vR = kap * VEV**2
    # G3221 one loop vR -> MU (same transposed feed; structure = researcher's, cross terms at the 1% level)
    b, g_g3221_vR, g_g3221_MU = gauge_g3221(vR, MU, content, g_vR)
    y2 = rge.pack_g3221(g_g3221_vR, Yu_vR.T, Yd_vR.T, Ye_vR.T, np.zeros((3, 3), complex))
    y2 = rge.run_g3221(y2, vR, MU, b)
    _, YuT, YdT, YeT, _ = rge.unpack_g3221(y2)
    Yu_MU, Yd_MU, Ye_MU = YuT.T, YdT.T, YeT.T
    # universal running factor of a (small) Dirac neutrino Yukawa MU -> vR
    y3 = rge.pack_g3221(g_g3221_MU, Yu_MU.T, Yd_MU.T, Ye_MU.T, 1e-3 * np.eye(3, dtype=complex))
    y3 = rge.run_g3221(y3, MU, vR, b)
    _, _, _, _, YnT = rge.unpack_g3221(y3)
    rnu = float(np.abs(YnT).max() / 1e-3)
    oU = observables(Yu_MU, Yd_MU, Ye_MU, mnu_vR)
    oR = observables(Yu_vR, Yd_vR, Ye_vR, mnu_vR)
    T = {}
    for k in MASS_KEYS:
        c, s = inp["masses_GeV_MZ"][k]
        fl = floor if (lepton_floor is None or k not in ("m_e", "m_mu", "m_tau")) else lepton_floor
        rel = math.sqrt((s / c)**2 + fl**2)
        T[k] = (oU[k], rel * oU[k])
    for k in CKM_KEYS:
        c, s = inp["ckm_MZ"][k]
        T[k] = (oU[k], s if k == "delta" else s / c * oU[k])        # relative errors kept for the angles
    for k in NU_KEYS:
        c, s = inp["pmns"][k]
        T[k] = (oU[k], s if k.startswith("sin2") else s / c * oU[k])
    info = {"vR": vR, "MU": MU, "content": content, "b_g3221": b.tolist(), "g_sm_vR": list(map(float, g_vR)),
            "alpha_inv_MU": [4 * math.pi / g**2 for g in g_g3221_MU[:3]] + [4 * math.pi / (g_g3221_MU[3]**2 * 2 / 3)],
            "rnu": rnu, "obs_MU": {k: (float(v) if not isinstance(v, list) else v) for k, v in oU.items()},
            "obs_vR": {k: (float(v) if not isinstance(v, list) else v) for k, v in oR.items()},
            "kappa_scale_factor_mnu(vR)/mnu(MZ)": float(np.abs(mnu_vR).max() / np.abs(mnu).max())}
    return T, info, (Yu_MU, Yd_MU, Ye_MU, mnu_vR)

# ------------------------------------------------------------------------------------------------------------------
# model
# ------------------------------------------------------------------------------------------------------------------
def unitary(p):
    th12, th13, th23, d, a1, a2, b1, b2, b3 = p
    V = umix(math.sin(th12), math.sin(th23), math.sin(th13), d)
    return np.diag(np.exp(1j * np.array([a1, a2, 0]))) @ V @ np.diag(np.exp(1j * np.array([b1, b2, b3])))

class Model:
    """p = [W(9), log10 r, log10|s|, arg s] (+ 6 log-mass offsets in free mode).  rho is analytic."""
    def __init__(self, T, rnu, v=VEV, free_masses=False, nu_weight=1.0):
        self.T = T; self.rnu = rnu; self.v = v; self.free = free_masses; self.nuw = nu_weight
        self.sd = np.array([T["m_d"][0], T["m_s"][0], T["m_b"][0]]) / v
        self.se = np.array([T["m_e"][0], T["m_mu"][0], T["m_tau"][0]]) / v
        self.n = 12 + (6 if free_masses else 0)
        self.keys = ["m_u", "m_c", "m_t"] + CKM_KEYS + NU_KEYS + (["m_d", "m_s", "m_b", "m_e", "m_mu", "m_tau"] if free_masses else [])

    def matrices(self, p):
        W = unitary(p[0:9]); r = 10 ** p[9]; s = 10 ** p[10] * np.exp(1j * p[11])
        sd, se = self.sd, self.se
        if self.free:
            sd = sd * np.exp(p[12:15]); se = se * np.exp(p[15:18])
        Yd = np.diag(sd).astype(complex)
        Ye = W @ np.diag(se) @ W.T
        Hm = (3 * Yd + Ye) / 4; F = (Yd - Ye) / 4
        Yu = r * (Hm + s * F); Yn = r * (Hm - 3 * s * F)
        return Yu, Yd, Ye, Yn, Hm, F, r, s

    def mnu_unit(self, Yn, F):
        """m_nu at rho = 1 (GeV): -rnu^2 v^2 Yn F^-1 Yn^T"""
        X = np.linalg.solve(F, Yn.T)
        return -(self.rnu**2) * self.v**2 * (Yn @ X)

    def residuals(self, p, with_rho=None):
        Yu, Yd, Ye, Yn, Hm, F, r, s = self.matrices(p)
        try:
            m1 = self.mnu_unit(Yn, F)
        except np.linalg.LinAlgError:
            return np.full(len(self.keys), 1e3), None, None
        mx = float(np.abs(m1).max()) if np.all(np.isfinite(m1)) else float('inf')
        if not (1e-300 < mx < 1e300):
            return np.full(len(self.keys), 1e3), None, None
        m1 = m1 / mx                                   # rho is analytic: evaluate at unit scale
        o = observables(Yu, Yd, Ye, m1, self.v)
        if not all(np.isfinite([o[k] for k in self.keys if k != 'delta'])):
            return np.full(len(self.keys), 1e3), None, None
        # analytic rho: dm2 scale as rho^2 =: lam ; minimise sum ((lam a_i - c_i)/sig_i)^2
        a = np.array([o["dm21"], o["dm31"]]); c = np.array([self.T["dm21"][0], self.T["dm31"][0]]); sg = np.array([self.T["dm21"][1], self.T["dm31"][1]])
        if with_rho is None:
            lam = float(np.sum(a * c / sg**2) / max(np.sum(a * a / sg**2), 1e-300))
            lam = max(lam, 1e-300)
        else:
            lam = (with_rho * mx)**2
        rho = math.sqrt(lam) / mx                      # m_nu = rho * m1_unscaled = sqrt(lam) * (m1/mx)  =>  rho = sqrt(lam)/mx
        o["dm21"] *= lam; o["dm31"] *= lam; o["m_nu_eV"] = [x * math.sqrt(lam) for x in o["m_nu_eV"]]
        res = []
        for k in self.keys:
            cen, sig = self.T[k]
            if k in MASS_KEYS:
                res.append(math.log(max(o[k], 1e-300) / cen) * cen / sig)
            elif k == "delta":
                d = (abs(o[k]) - cen + math.pi) % (2 * math.pi) - math.pi      # |delta|: conjugation symmetry of the fit
                res.append(d / sig)
            else:
                w = self.nuw if k in NU_KEYS else 1.0
                res.append(w * (o[k] - cen) / sig)
        return np.array(res), o, rho

    def chi2(self, p):
        return float(np.sum(self.residuals(p)[0]**2))

    def random_start(self, rng):
        p = np.zeros(self.n)
        p[0:3] = np.arcsin(np.sqrt(rng.uniform(0, 1, 3)))          # roughly Haar-like
        if rng.uniform() < 0.5:
            p[0:3] = np.abs(rng.normal(0, 0.3, 3))
        p[3:9] = rng.uniform(-math.pi, math.pi, 6)
        p[9] = math.log10(self.T["m_t"][0] / self.T["m_b"][0]) + rng.normal(0, 0.15)
        p[10] = rng.uniform(-1.5, 1.2); p[11] = rng.uniform(-math.pi, math.pi)
        return p

    def bounds(self):
        lo = [0, 0, 0] + [-2 * math.pi] * 6 + [0.5, -2.5, -2 * math.pi] + ([-0.2] * 6 if self.free else [])
        hi = [math.pi / 2] * 3 + [2 * math.pi] * 6 + [3.0, 2.0, 2 * math.pi] + ([0.2] * 6 if self.free else [])
        return np.array(lo), np.array(hi)

    def pulls_full(self, p):
        """All 18 pulls (pinned masses give 0 in pinned mode) and bookkeeping (composition, perturbativity)."""
        res, o, rho = self.residuals(p)
        if o is None:
            return None
        pl = {}
        for k in ALL_KEYS:
            cen, sig = self.T[k]
            if k in MASS_KEYS:
                pl[k] = math.log(o[k] / cen) * cen / sig
            elif k == "delta":
                pl[k] = ((abs(o[k]) - cen + math.pi) % (2 * math.pi) - math.pi) / sig
            else:
                pl[k] = (o[k] - cen) / sig
        return pl, o, rho

def composition(model, p, vR, kappa_R=2 * math.sqrt(6)):
    """Light-doublet composition with |c_d10|^2 (1+r^2) + |c_d126|^2 (1+|rs|^2) = 1 (c_u10 = r c_d10, c_u126 = r s c_d126)
    and M_R = kappa_R v_R F / c_d126  =>  c_d126 = rho kappa_R v_R.  Y10 = H/c_d10, Y126 = F/c_d126.
    Perturbativity map of the researcher (unverified here): Y10_act = Y10/(2 sqrt2), Y126_act = (sqrt3/4) Y126."""
    res, o, rho = model.residuals(p)
    Yu, Yd, Ye, Yn, Hm, F, r, s = model.matrices(p)
    cd126 = rho * kappa_R * vR
    rem = 1 - cd126**2 * (1 + abs(r * s)**2)
    out = {"rho": rho, "c_d126": cd126, "rem": rem, "r": r, "s_abs": abs(s), "s_arg": float(np.angle(s))}
    MR = F / rho
    out["M_R_GeV"] = np.linalg.svd(MR)[1].tolist()
    if rem > 0:
        cd10 = math.sqrt(rem / (1 + r**2))
        out.update({"c_d10": cd10, "c_u10": r * cd10, "c_u126": abs(r * s) * cd126,
                    "Y10_act_max": float(np.abs(Hm / cd10).max() / (2 * math.sqrt(2))),
                    "Y126_act_max": float(np.abs(F / cd126).max() * math.sqrt(3) / 4),
                    "Y10_act_sv": (np.linalg.svd(Hm / cd10)[1] / (2 * math.sqrt(2))).tolist(),
                    "Y126_act_sv": (np.linalg.svd(F / cd126)[1] * math.sqrt(3) / 4).tolist()})
    return out

def lm_fit(model, p0, max_nfev=3000):
    f = lambda p: model.residuals(p)[0]
    r = least_squares(f, p0, method="lm", max_nfev=max_nfev, xtol=1e-12, ftol=1e-12, gtol=1e-12, x_scale="jac")
    return r.x, float(np.sum(r.fun**2)), r.nfev

def result_record(model, p, vR, label=""):
    pl, o, rho = model.pulls_full(p)
    chi2_18 = float(sum(v * v for v in pl.values()))
    rec = {"label": label, "x": list(map(float, p)), "chi2_18": chi2_18, "pulls": {k: float(v) for k, v in pl.items()},
           "max_abs_pull": float(max(abs(v) for v in pl.values())),
           "obs": {k: (float(v) if not isinstance(v, list) else v) for k, v in o.items()}, "comp": composition(model, p, vR)}
    return rec

if __name__ == "__main__":
    mode = sys.argv[1]
    content = sys.argv[2] if len(sys.argv) > 2 else "T3"
    vR, MU = (2.6e13, 2.13e16) if content == "T2" else (3.08e13, 3.05e16)
    T, info, _ = build_targets(vR, MU, content)
    if mode == "targets":
        print(json.dumps(info, indent=1))
        print({k: (round(v[0], 6), round(v[1] / v[0], 4)) for k, v in T.items()})
        sys.exit()
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rng = np.random.default_rng(seed)
    narrow = os.environ.get("K2_NARROW", "0") == "1"
    inflate = float(os.environ.get("K2_INFLATE", "1.0"))
    M = Model(T, info["rnu"], nu_weight=1.0 / inflate)
    out = os.path.join(HERE, f"{mode}_{content}_{seed}{'_n' if narrow else ''}{'_i%g' % inflate if inflate != 1 else ''}.json")
    best = None; recs = []
    t0 = time.time()
    if mode == "lm":
        nstart = int(sys.argv[4]) if len(sys.argv) > 4 else 300
        for i in range(nstart):
            p0 = M.random_start(rng)
            try:
                x, c2, nf = lm_fit(M, p0)
            except Exception as e:
                continue
            if best is None or c2 < best[1]:
                best = (x, c2)
                print(f"start {i}: chi2={c2:.3f} nfev={nf} t={time.time()-t0:.0f}s", flush=True)
            if c2 < 60:
                recs.append(result_record(M, x, vR, f"lm{i}"))
    elif mode == "de":
        popsize = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        maxiter = int(sys.argv[5]) if len(sys.argv) > 5 else 2000
        lo, hi = M.bounds()
        if narrow:
            lo[9], hi[9], lo[10], hi[10] = 1.5, 2.1, -0.9, 0.2
        de = differential_evolution(M.chi2, list(zip(lo, hi)), seed=seed, popsize=popsize, maxiter=maxiter, tol=1e-12,
                                    mutation=(0.5, 1.0), recombination=0.9, polish=False, init="latinhypercube")
        print(f"DE: chi2={de.fun:.3f} nfev={de.nfev} t={time.time()-t0:.0f}s", flush=True)
        M.nuw = 1.0
        x, c2, nf = lm_fit(M, de.x)
        print(f"LM polish (true nu errors): chi2={c2:.4f}", flush=True)
        best = (x, c2)
        for k in range(30):     # basin hopping around the polished point
            pk = best[0] + rng.normal(0, 0.05, M.n)
            try:
                xk, ck, _ = lm_fit(M, pk)
            except Exception:
                continue
            if ck < best[1] - 1e-9:
                best = (xk, ck); print(f"hop {k}: chi2={ck:.4f}", flush=True)
        recs.append(result_record(M, best[0], vR, "de"))
    recs.sort(key=lambda r: r["chi2_18"])
    json.dump({"content": content, "vR": vR, "MU": MU, "seed": seed, "best_chi2": best[1] if best else None,
               "records": recs[:20], "info": info}, open(out, "w"), indent=1)
    if best is not None:
        rec = result_record(M, best[0], vR, "best")
        print("BEST chi2_18 =", round(rec["chi2_18"], 4), "max|pull| =", round(rec["max_abs_pull"], 3))
        print("pulls:", {k: round(v, 2) for k, v in rec["pulls"].items()})
        print("comp:", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in rec["comp"].items()})
