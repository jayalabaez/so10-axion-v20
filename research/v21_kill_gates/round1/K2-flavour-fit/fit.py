"""K2: top-down 10_H + 126bar_H flavour fit for v21-F17-G3221 (one light SM doublet of free 10/126 composition).

Stage 1 (proxy): bottom-up parametrisation at M_U (targets = data run up with the same RGEs), 14 (+2 type II) real
parameters: W (unitary relating the Ye and Yd Takagi bases: 3 angles + 6 phases), r, s complex, the 126 down-fraction
|c_d126| (sets the seesaw scale), + type II (v_L/c_d126 complex).  d- and e-masses are reproduced exactly by
construction, Yu = r (H + s F), Ynu = r (H - 3 s F), H = (3Yd + Ye)/4, F = (Yd - Ye)/4,
M_R = kappa_R v_R F / c_d126 with kappa_R = 2 sqrt6 (exact Clebsch, so10_clebsch.py; vev convention: canonical
complex component), optionally M_L = kappa_R (v_L / c_d126) F.
Stage 2 (full): forward parametrisation (Y10 real diagonal, Y126 complex symmetric, composition c in C^4, v_L),
top-down running M_U -> v_R (G3221 one loop) -> M_Z (SM two loop + kappa), chi^2 at M_Z.
"""
import json, math, sys, time
import numpy as np
from scipy.optimize import least_squares
import rge

KAPPA_R = 2 * math.sqrt(6)          # M_R = KAPPA_R v_R Y126_def (Y126_def normalised by the (15,2,2) doublet coupling)
N10_ACT = 1 / (2 * math.sqrt(2))     # Y10_act = N10_ACT * Y10_def
N126_ACT = math.sqrt(3) / 4          # Y126_act = N126_ACT * Y126_def
YMAX = 1.5

def H(m):
    return m.conj().T

# ----------------------------------------------------------------------------------------------------------------
def takagi(S):
    """S symmetric complex: S = U diag(s) U^T, s >= 0 ascending."""
    U, s, Vh = np.linalg.svd(S)
    # S = U s Vh ; for symmetric S, Vh = U^T up to phases: fix with Takagi phase
    # Use the standard trick: S S^dag = U s^2 U^dag; then U' = U sqrt(phase) with phase = diag(U^T S^* U)... use iterative
    Z = U.T @ S.conj() @ U.conj()   # should be ~ diag of phases times s... compute phases from U^dag S U^*
    D = U.conj().T @ S @ U.conj()
    ph = np.exp(1j * np.angle(np.diag(D)) / 2)
    U2 = U @ np.diag(ph)
    s2 = np.abs(np.diag(U2.conj().T @ S @ U2.conj()))
    order = np.argsort(s2)
    return U2[:, order], s2[order]

def left_rot(Y):
    """Y = M/v in basis (f_L)_i (f^c)_j: M M^dag = U diag^2 U^dag; returns U (columns ascending) and singular values."""
    w, U = np.linalg.eigh(Y @ H(Y))
    return U, np.sqrt(np.clip(w, 0, None))

def mixing_angles(V):
    s13 = abs(V[0, 2]); c13 = math.sqrt(max(1 - s13**2, 1e-300))
    s12 = abs(V[0, 1]) / c13; s23 = abs(V[1, 2]) / c13
    # Dirac phase via the Jarlskog invariant
    J = (V[0, 0] * V[1, 1] * np.conj(V[0, 1]) * np.conj(V[1, 0])).imag
    c12 = math.sqrt(max(1 - s12**2, 0)); c23 = math.sqrt(max(1 - s23**2, 0))
    den = c12 * s12 * c23 * s23 * c13**2 * s13
    sind = J / den if den > 1e-300 else 0.0
    # cos delta from |V_ud|... use |V_td|? use rephasing-invariant: |V[1,0]|^2 = (s12 c23)^2 + (c12 s23 s13)^2 + 2 s12 c23 c12 s23 s13 cos d
    num = abs(V[1, 0])**2 - (s12 * c23)**2 - (c12 * s23 * s13)**2
    cosd = num / (2 * s12 * c23 * c12 * s23 * s13) if s13 > 1e-300 else 1.0
    delta = math.atan2(sind, cosd)
    return s12, s23, s13, delta

def observables(Yu, Yd, Ye, mnu, v):
    Uu, su = left_rot(Yu); Ud, sd = left_rot(Yd); Ue, se = left_rot(Ye)
    V = H(Uu) @ Ud
    s12, s23, s13, dl = mixing_angles(V)
    Un, mn = takagi(mnu)
    U = H(Ue) @ Un
    n12, n23, n13, nd = mixing_angles(U)
    obs = {"m_u": su[0] * v, "m_c": su[1] * v, "m_t": su[2] * v, "m_d": sd[0] * v, "m_s": sd[1] * v, "m_b": sd[2] * v,
           "m_e": se[0] * v, "m_mu": se[1] * v, "m_tau": se[2] * v,
           "s12": s12, "s23": s23, "s13": s13, "delta": dl,
           "sin2_th12": n12**2, "sin2_th23": n23**2, "sin2_th13": n13**2, "delta_deg": math.degrees(nd) % 360,
           "dm21": (mn[1]**2 - mn[0]**2) * 1e18, "dm31": (mn[2]**2 - mn[0]**2) * 1e18,
           "m_nu_eV": list(mn * 1e9), "sum_mnu_eV": float(mn.sum() * 1e9)}
    return obs

MASS_KEYS = ["m_u", "m_c", "m_t", "m_d", "m_s", "m_b", "m_e", "m_mu", "m_tau"]
CKM_KEYS = ["s12", "s23", "s13", "delta"]
NU_KEYS = ["sin2_th12", "sin2_th23", "sin2_th13", "dm21", "dm31"]

def build_targets(inputs, floor_mass=0.01, lepton_floor=None):
    t = {}
    for k in MASS_KEYS:
        c, s = inputs["masses_GeV_MZ"][k]
        fl = floor_mass if (lepton_floor is None or k not in ("m_e", "m_mu", "m_tau")) else lepton_floor
        t[k] = (c, math.sqrt(s**2 + (fl * c)**2))
    for k in CKM_KEYS:
        t[k] = tuple(inputs["ckm_MZ"][k])
    for k in NU_KEYS:
        t[k] = tuple(inputs["pmns"][k])
    return t

def pulls(obs, targets, log_masses=False):
    out = {}
    for k, (c, s) in targets.items():
        if k == "delta":
            d = (obs[k] - c + math.pi) % (2 * math.pi) - math.pi
            out[k] = d / s
        elif log_masses and k in MASS_KEYS:
            out[k] = math.log(max(obs[k], 1e-300) / c) * c / s
        else:
            out[k] = (obs[k] - c) / s
    return out

# ----------------------------------------------------------------------------------------------------------------
# top-down running
# ----------------------------------------------------------------------------------------------------------------
class Runner:
    def __init__(self, inputs, vR, MU, content="T2"):
        self.inputs = inputs; self.vR = vR; self.MU = MU; self.content = content
        self.v = inputs["VEV"]; self.MZ = inputs["MZ"]
        self.gauge = rge.gauge_bottom_up(inputs, None, vR, MU, content)
        self.b = rge.g3221_b_coefficients(content)

    def top_down(self, Yu, Yd, Ye, Yn, MR, ML=None, rtol=1e-7):
        g = self.gauge["g3221_at_MU"]
        y = rge.pack_g3221(g, Yu, Yd, Ye, Yn)
        y = rge.run_g3221(y, self.MU, self.vR, self.b, rtol)
        _, Yu, Yd, Ye, Yn = rge.unpack_g3221(y)
        MD = Yn * self.v
        mnu = -MD @ np.linalg.solve(MR, MD.T)
        if ML is not None:
            mnu = mnu + ML
        kap = mnu / self.v**2
        gsm = self.gauge["sm_at_vR"]
        ysm = rge.pack_sm(gsm, self.gauge["lam_vR"], Yu, Yd, Ye, kap)
        ysm = rge.run_sm(ysm, self.vR, self.MZ, True, rtol)
        _, _, Yu, Yd, Ye, kap = rge.unpack_sm(ysm, True)
        return Yu, Yd, Ye, kap * self.v**2

    def bottom_up_targets(self, targets):
        """Run central data up: SM (MZ->vR) then G3221 (vR->MU); returns Yukawas at MU and kappa at vR."""
        inp = self.inputs; v = self.v
        m = {k: inp["masses_GeV_MZ"][k][0] for k in MASS_KEYS}
        s12, s23, s13, dl = [inp["ckm_MZ"][k][0] for k in CKM_KEYS]
        V = ckm_matrix(s12, s23, s13, dl)
        Yu = np.diag([m["m_u"], m["m_c"], m["m_t"]]) / v
        Yd = (V @ np.diag([m["m_d"], m["m_s"], m["m_b"]])).astype(complex) / v
        Ye = np.diag([m["m_e"], m["m_mu"], m["m_tau"]]).astype(complex) / v
        p = inp["pmns"]
        U = pmns_matrix(math.sqrt(p["sin2_th12"][0]), math.sqrt(p["sin2_th23"][0]), math.sqrt(p["sin2_th13"][0]), math.radians(p["delta_deg"][0]))
        mn = np.array([0.0, math.sqrt(p["dm21"][0]), math.sqrt(p["dm31"][0])]) * 1e-9
        mnu = U @ np.diag(mn) @ U.T
        g = self.gauge["g_MZ"]
        y = rge.pack_sm(g, 0.26, Yu.astype(complex), Yd, Ye, mnu / v**2)
        y = rge.run_sm(y, self.MZ, self.vR, True)
        _, _, Yu, Yd, Ye, kap = rge.unpack_sm(y, True)
        mnu_vR = kap * v**2
        y2 = rge.pack_g3221(self.gauge["g3221_at_vR"], Yu, Yd, Ye, np.zeros((3, 3), complex))
        y2 = rge.run_g3221(y2, self.vR, self.MU, self.b)
        _, Yu, Yd, Ye, _ = rge.unpack_g3221(y2)
        # neutrino Yukawa running factor (gauge-dominated) for the proxy stage: run a unit Ynu from MU to vR
        y3 = rge.pack_g3221(self.gauge["g3221_at_MU"], Yu, Yd, Ye, 1e-3 * np.eye(3, dtype=complex))
        y3 = rge.run_g3221(y3, self.MU, self.vR, self.b)
        _, _, _, _, Yn3 = rge.unpack_g3221(y3)
        rnu = float(np.abs(Yn3).max() / 1e-3)
        return {"Yu": Yu, "Yd": Yd, "Ye": Ye, "mnu_vR": mnu_vR, "rnu": rnu}

def ckm_matrix(s12, s23, s13, d):
    c12, c23, c13 = math.sqrt(1 - s12**2), math.sqrt(1 - s23**2), math.sqrt(1 - s13**2)
    e = np.exp(1j * d)
    return np.array([[c12 * c13, s12 * c13, s13 * np.conj(e)],
                     [-s12 * c23 - c12 * s23 * s13 * e, c12 * c23 - s12 * s23 * s13 * e, s23 * c13],
                     [s12 * s23 - c12 * c23 * s13 * e, -c12 * s23 - s12 * c23 * s13 * e, c23 * c13]])
pmns_matrix = ckm_matrix

# ----------------------------------------------------------------------------------------------------------------
# Stage 1: proxy (bottom-up parametrisation at MU)
# ----------------------------------------------------------------------------------------------------------------
def unitary_from_params(p):
    """3 angles + 6 phases -> general U(3)."""
    th12, th13, th23, d, a1, a2, b1, b2, b3 = p
    V = ckm_matrix(math.sin(th12), math.sin(th23), math.sin(th13), d)
    return np.diag(np.exp(1j * np.array([a1, a2, 0]))) @ V @ np.diag(np.exp(1j * np.array([b1, b2, b3])))

class Proxy:
    def __init__(self, runner, targets, type2=False, strict=None):
        self.R = runner; self.T = targets; self.type2 = type2
        bu = runner.bottom_up_targets(targets)
        self.bu = bu
        v = runner.v
        # GUT-scale targets: masses and CKM at MU from the run-up data; relative errors as at MZ
        obs = observables(bu["Yu"], bu["Yd"], bu["Ye"], bu["mnu_vR"], v)
        self.obsU = obs
        self.TU = {}
        for k in MASS_KEYS:
            c, s = targets[k]; self.TU[k] = (obs[k], s / c * obs[k])
        for k in CKM_KEYS:
            c, s = targets[k]; self.TU[k] = (obs[k], s)
        for k in NU_KEYS:
            self.TU[k] = targets[k]
        self.sd = np.array([obs["m_d"], obs["m_s"], obs["m_b"]]) / v
        self.se = np.array([obs["m_e"], obs["m_mu"], obs["m_tau"]]) / v
        self.n = 14 + (2 if type2 else 0)

    def matrices(self, p):
        W = unitary_from_params(p[0:9])
        r = p[9] * np.exp(1j * p[10]); s = p[11] * np.exp(1j * p[12]); cd126 = p[13]
        Yd = np.diag(self.sd).astype(complex)
        Ye = W @ np.diag(self.se) @ W.T
        Hm = (3 * Yd + Ye) / 4; F = (Yd - Ye) / 4
        Yu = r * (Hm + s * F); Yn = r * (Hm - 3 * s * F)
        MR = KAPPA_R * self.R.vR * F / cd126
        ML = None
        if self.type2:
            vL = 10 ** p[14] * np.exp(1j * p[15])
            ML = KAPPA_R * vL * F / cd126
        return Yu, Yd, Ye, Yn, MR, ML, Hm, F, r, s, cd126

    def composition(self, Hm, F, r, s, cd126):
        rs = r * s
        # |cd10|^2 (1+|r|^2) + cd126^2 (1+|rs|^2) = 1
        rem = 1 - cd126**2 * (1 + abs(rs)**2)
        self._rem = rem
        cd10 = math.sqrt(max(rem, 1e-8))
        Y10 = Hm / cd10
        Y126 = F / cd126
        return cd10, Y10, Y126

    def pert_penalty(self, Y10, Y126):
        a = np.abs(Y10 * N10_ACT).max(); b = np.abs(Y126 * N126_ACT).max()
        pen = []
        for x in (a, b):
            pen.append(max(0.0, (x - YMAX) / 0.05))
        return pen, a, b

    nu_weight = 1.0

    def residuals(self, p, full=False, charged_only=False, log_masses=True):
        Yu, Yd, Ye, Yn, MR, ML, Hm, F, r, s, cd126 = self.matrices(p)
        cd10, Y10, Y126 = self.composition(Hm, F, r, s, cd126)
        v = self.R.v
        if full:
            Yu2, Yd2, Ye2, mnu = self.R.top_down(Yu, Yd, Ye, Yn, MR, ML)
            obs = observables(Yu2, Yd2, Ye2, mnu, v)
            T = self.T
        else:
            MD = Yn * self.bu["rnu"] * v
            try:
                mnu = -MD @ np.linalg.solve(MR, MD.T)
            except np.linalg.LinAlgError:
                mnu = np.full((3, 3), 1e-3)
            if ML is not None:
                mnu = mnu + ML
            obs = observables(Yu, Yd, Ye, mnu, v)
            T = self.TU
        pl = pulls(obs, T, log_masses)
        res = [pl[k] for k in MASS_KEYS + CKM_KEYS] + ([0.0] * len(NU_KEYS) if charged_only else [self.nu_weight * pl[k] for k in NU_KEYS])
        pen, a, b = self.pert_penalty(Y10, Y126)
        pen.append(0.0 if self._rem > 0 else 50.0 * (1 - self._rem))
        return np.array(res + pen), obs, pl, (a, b, cd10, cd126, r, s)

    def random_start(self, rng):
        p = np.zeros(self.n)
        wide = rng.uniform() < 0.3
        p[0:3] = rng.uniform(0, math.pi / 2, 3) if wide else np.abs(rng.normal(0, 0.35, 3)); p[3:9] = rng.uniform(0, 2 * math.pi, 6)
        r0 = self.obsU["m_t"] / self.obsU["m_b"]
        p[9] = r0 * 10 ** rng.normal(0, 0.15); p[10] = rng.uniform(0, 2 * math.pi)
        p[11] = 10 ** rng.uniform(-1.3, 0.5); p[12] = rng.uniform(0, 2 * math.pi)
        p[13] = 10 ** rng.uniform(-2.5, -0.5)
        if self.type2:
            p[14] = rng.uniform(-12, -9); p[15] = rng.uniform(0, 2 * math.pi)
        return p

    def bounds(self):
        lo = [-10] * 9 + [1e-3, -50, 1e-4, -50, 1e-4]; hi = [10] * 9 + [1e4, 50, 1e3, 50, 0.9999]
        if self.type2:
            lo += [-16, -50]; hi += [-6, 50]
        return (np.array(lo), np.array(hi))

def fit_proxy(proxy, p0, full=False, max_nfev=4000, charged_only=False, method="trf"):
    f = lambda p: proxy.residuals(p, full, charged_only)[0]
    if method == "lm":
        r = least_squares(f, p0, method="lm", max_nfev=max_nfev, xtol=1e-10, ftol=1e-10, gtol=1e-10, x_scale="jac")
    else:
        r = least_squares(f, p0, bounds=proxy.bounds(), max_nfev=max_nfev, xtol=1e-9, ftol=1e-9, gtol=1e-9, x_scale="jac")
    w = proxy.nu_weight; proxy.nu_weight = 1.0
    res, obs, pl, extra = proxy.residuals(r.x, full, charged_only, log_masses=False)
    proxy.nu_weight = w
    nobs = len(MASS_KEYS + CKM_KEYS + NU_KEYS)
    chi2 = float(np.sum(res[:nobs]**2)); pen = float(np.sum(res[nobs:]**2))
    return {"x": list(r.x), "chi2": chi2, "penalty": pen, "obs": {k: (float(v) if not isinstance(v, list) else v) for k, v in obs.items()},
            "pulls": {k: float(v) for k, v in pl.items()}, "ymax10_act": float(extra[0]), "ymax126_act": float(extra[1]),
            "cd10": float(extra[2]), "cd126": float(extra[3]), "r": [float(abs(extra[4])), float(np.angle(extra[4]))],
            "s": [float(abs(extra[5])), float(np.angle(extra[5]))], "nfev": int(r.nfev)}


# ----------------------------------------------------------------------------------------------------------------
# Stage 1 (improved): up-diagonal parametrisation.  Basis where Yu = D_u (real, the three up masses at MU):
# H + sF = D_u/r  ->  Yd = D_u/r + (1-s)F,  Ye = D_u/r - (3+s)F,  Ynu = D_u - 4 r s F  (times 1; M_D = v Ynu)
# params: F complex symmetric (12), r (|r|, arg), s (|s|, arg), cd126, [log10 vL, arg vL]
# ----------------------------------------------------------------------------------------------------------------
class Proxy2(Proxy):
    def __init__(self, runner, targets, type2=False):
        super().__init__(runner, targets, type2)
        v = runner.v
        self.su = np.array([self.obsU["m_u"], self.obsU["m_c"], self.obsU["m_t"]]) / v
        self.n = 17 + (2 if type2 else 0)

    def matrices(self, p):
        F = np.zeros((3, 3), complex)
        k = 0
        for i in range(3):
            for j in range(i, 3):
                F[i, j] = F[j, i] = p[k] + 1j * p[k + 1]; k += 2
        r = p[12] * np.exp(1j * p[13]); s = p[14] * np.exp(1j * p[15]); cd126 = 10 ** p[16]
        Du = np.diag(self.su).astype(complex)
        Hm = Du / r - s * F
        Yu = Du.copy(); Yd = Hm + F; Ye = Hm - 3 * F; Yn = r * (Hm - 3 * s * F)
        MR = KAPPA_R * self.R.vR * F / cd126
        ML = None
        if self.type2:
            vL = 10 ** p[17] * np.exp(1j * p[18])
            ML = KAPPA_R * vL * F / cd126
        return Yu, Yd, Ye, Yn, MR, ML, Hm, F, r, s, cd126

    def random_start(self, rng):
        yb, ytau, yt = self.sd[2], self.se[2], self.su[2]
        ys, ymu, yc = self.sd[1], self.se[1], self.su[1]
        yd, ye, yu = self.sd[0], self.se[0], self.su[0]
        p = np.zeros(self.n)
        for _ in range(100):
            r = (yt / yb) * 10 ** rng.normal(0, 0.2) * np.exp(1j * rng.uniform(0, 2 * math.pi))
            phb, pht = rng.uniform(0, 2 * math.pi, 2)
            F33 = (yb * np.exp(1j * phb) - ytau * np.exp(1j * pht)) / 4
            s = 1 - (yb * np.exp(1j * phb) - yt / r) / F33
            if abs(s) < 30:
                break
        phs, phm, phd, phe = rng.uniform(0, 2 * math.pi, 4)
        F22 = (ys * np.exp(1j * phs) - ymu * np.exp(1j * phm)) / 4
        F11 = (yd * np.exp(1j * phd) - ye * np.exp(1j * phe)) / 4
        scale = abs(F33)
        F12 = scale * 10 ** rng.uniform(-3.5, -1.5) * np.exp(1j * rng.uniform(0, 2 * math.pi))
        F13 = scale * 10 ** rng.uniform(-3, -1) * np.exp(1j * rng.uniform(0, 2 * math.pi))
        F23 = scale * 10 ** rng.uniform(-2.5, -0.5) * np.exp(1j * rng.uniform(0, 2 * math.pi))
        vals = [F11, F12, F13, F22, F23, F33]
        for k, z in enumerate(vals):
            p[2 * k] = z.real; p[2 * k + 1] = z.imag
        p[12] = abs(r); p[13] = np.angle(r); p[14] = abs(s); p[15] = np.angle(s)
        p[16] = rng.uniform(-3.0, -1.0)
        if self.type2:
            p[17] = rng.uniform(-12, -9); p[18] = rng.uniform(0, 2 * math.pi)
        return p

    def bounds(self):
        lo = [-1.0] * 12 + [1e-2, -50, 1e-5, -50, -6]; hi = [1.0] * 12 + [1e4, 50, 1e3, 50, -0.0001]
        if self.type2:
            lo += [-16, -50]; hi += [-6, 50]
        return (np.array(lo), np.array(hi))
