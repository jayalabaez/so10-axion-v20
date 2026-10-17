#!/usr/bin/env python3
"""Verifier chain for K1: own RG integration (fixed-step RK4 on alpha^-1, independent of scipy's DOP853), own
unification solver (nested: crossing alpha_3 = alpha_2L defines M_U; 2-D root in (ln v_R, alpha_2R^-1(v_R)) for the
remaining two residuals), SO(10) Landau scale at 2 and 3 loops.  Coefficients from vp_coeffs (exact, verified).

Conventions as in the researcher's report: t = ln(mu/GeV);
   d a_i/dt = -b_i/(2pi) - sum_j b_ij/(8 pi^2 a_j) + Y_i/(32 pi^3) - b3_i/(32 pi^3 a_i^2),   a_i = alpha_i^-1.
One-loop MS-bar thresholds: a_i(mu)_low = a_i(mu)_high - (1/2pi) sum_k b_i^k ln(M_k/mu) with b^k = 2/3 S (Weyl),
1/3 S (complex), 1/6 S (real), -7/2 S (vector incl. Goldstone); optional vector constant kappa_V S/(12 pi).
"""
from __future__ import annotations

import math
import sys
import os
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import brentq, fsolve

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vp_coeffs as vc  # noqa: E402

PI = math.pi
MPL = 2.435e18
MZ = 91.1876
A_MZ = np.array([59.02, 29.57, 1.0 / 0.1179])
YT_MZ = 0.95


def fl(x):
    return np.array([[float(v) for v in r] for r in x]) if isinstance(x[0], (list, tuple)) else np.array([float(v) for v in x])


class Seg:
    def __init__(self, b, bij, loops=2, Y=None, b3=None):
        self.b = fl(b)
        self.bij = fl(bij)
        self.loops = loops
        self.Y = (lambda t: np.zeros(len(self.b))) if Y is None else Y
        self.b3 = np.zeros(len(self.b)) if b3 is None else fl(b3)

    def rhs(self, t, a):
        d = -self.b / (2 * PI)
        if self.loops >= 2:
            d = d - self.bij.dot(1.0 / a) / (8 * PI**2) + self.Y(t) / (32 * PI**3)
        if self.loops >= 3:
            d = d - self.b3 / (32 * PI**3 * a * a)
        return d


def rk4(seg, a0, t0, t1, h=0.004, stop_at_alpha_inv=None):
    """Fixed-step RK4; if stop_at_alpha_inv is given, stop when min(a) <= it and return (a, t_stop, True)."""
    a = np.array(a0, dtype=float)
    n = max(1, int(math.ceil(abs(t1 - t0) / h)))
    hh = (t1 - t0) / n
    t = t0
    for _ in range(n):
        k1 = seg.rhs(t, a)
        k2 = seg.rhs(t + hh / 2, a + hh / 2 * k1)
        k3 = seg.rhs(t + hh / 2, a + hh / 2 * k2)
        k4 = seg.rhs(t + hh, a + hh * k3)
        anew = a + hh / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if stop_at_alpha_inv is not None and np.min(anew) <= stop_at_alpha_inv:
            # linear interpolation of the crossing within the step
            f0, f1 = np.min(a) - stop_at_alpha_inv, np.min(anew) - stop_at_alpha_inv
            frac = f0 / (f0 - f1)
            return a + frac * (anew - a), t + frac * hh, True
        a = anew
        t += hh
    return a, t, False


# ---------------------------------------------------------------------------------------------------------------
# Threshold multiplets.  Heavy at M_U (G3221 language), light at v_R (SM language).  kinds: W, C, R, V.
# ---------------------------------------------------------------------------------------------------------------
def S_i(reps, i, mult=1):
    s = Fr(reps[i][1]) * mult
    for k, r in enumerate(reps):
        if k != i:
            s *= r[0]
    return s


THR_COEF = {"W": Fr(2, 3), "C": Fr(1, 3), "R": Fr(1, 6), "V": Fr(-7, 2)}


def heavy_at_MU(content):
    g = vc.g_rep
    h = [("210 (3,3,1)4/3", "C", g(3, 3, 1, Fr(4, 3))), ("210 (8,1,3)0", "R", g(8, 1, 3, 0)),
         ("210 (3,1,3)4/3", "C", g(3, 1, 3, Fr(4, 3))), ("210 (1,1,3)0", "R", g(1, 1, 3, 0)),
         ("210 (6,2,2)2/3", "C", g(6, 2, 2, Fr(2, 3))), ("210 (3,2,2)-2/3", "C", g(3, 2, 2, Fr(-2, 3))),
         ("210 (1,2,2)-2", "C", g(1, 2, 2, Fr(-2))),
         ("126 (3,1,1)-2/3", "C", g(3, 1, 1, Fr(-2, 3))), ("126 (3b,1,1)2/3", "C", g(3, 1, 1, Fr(2, 3))),
         ("126 (6,3,1)2/3", "C", g(6, 3, 1, Fr(2, 3))), ("126 (3,3,1)-2/3", "C", g(3, 3, 1, Fr(-2, 3))),
         ("126 (1,3,1)-2", "C", g(1, 3, 1, Fr(-2))), ("126 (6b,1,3)-2/3", "C", g(6, 1, 3, Fr(-2, 3))),
         ("126 (3b,1,3)2/3", "C", g(3, 1, 3, Fr(2, 3))), ("126 (3,2,2)4/3", "C", g(3, 2, 2, Fr(4, 3))),
         ("126 (3b,2,2)-4/3", "C", g(3, 2, 2, Fr(-4, 3))),
         ("10 (3,1,1)-2/3", "C", g(3, 1, 1, Fr(-2, 3))), ("10 (3b,1,1)2/3", "C", g(3, 1, 1, Fr(2, 3)))]
    if content == "T2":
        h += [("10/126 heavy (1,2,2)0", "C", g(1, 2, 2, 0)), ("210 (8,1,1)0", "R", g(8, 1, 1, 0))]
    elif content != "T3":
        raise ValueError(content)
    return h


HEAVY_V311 = ("V (3,1,1)4/3 + cc", "V", vc.g_rep(3, 1, 1, Fr(4, 3)), 2)
HEAVY_V322 = ("V (3,2,2)-2/3 + cc", "V", vc.g_rep(3, 2, 2, Fr(-2, 3)), 2)


def light_at_vR(content):
    s = vc.sm_rep
    l = [("W_R", "V", s(Fr(1), 1, 1), 2), ("Z_R", "V", s(Fr(0), 1, 1), 1),
         ("Delta_R++", "C", s(Fr(2), 1, 1), 1), ("Delta_R+ (eaten? no: physical)", "C", s(Fr(1), 1, 1), 0),
         ("second doublet", "C", s(Fr(1, 2), 2, 1), 1), ("(8,2)1/2", "C", s(Fr(1, 2), 2, 8), 1),
         ("(8,2)-1/2", "C", s(Fr(-1, 2), 2, 8), 1), ("(8,3)0", "R", s(Fr(0), 3, 8), 1), ("(1,3)0", "R", s(Fr(0), 3, 1), 1)]
    if content == "T3":
        l += [("second bidoublet", "C", s(Fr(1, 2), 2, 1), 2), ("(8,1)0", "R", s(Fr(0), 1, 8), 1)]
    return l


def scalar_decomposition_check(content):
    """Heavy + light + Goldstones must reproduce the SO(10) scalar b_i = 64/3 in every G3221 factor."""
    tot = [Fr(0)] * 4
    for name, kind, reps in heavy_at_MU(content):
        for i in range(4):
            tot[i] += THR_COEF[kind] * S_i(reps, i)
    for kind, reps, mult in vc.g3221_fields(content, with_s=False):
        if kind in ("C", "R"):
            for i in range(4):
                tot[i] += THR_COEF[kind] * S_i(reps, i, mult)
    # Goldstones: 30 real = the heavy vectors' reps as real scalars: (3,2,2)+cc complex (24 real) + (3,1,1)+cc (6 real)
    for name, kind, reps, mult in (HEAVY_V322, HEAVY_V311):
        for i in range(4):
            tot[i] += Fr(1, 3) * S_i(reps, i, 1)  # one complex multiplet each
    return [str(x) for x in tot]


# ---------------------------------------------------------------------------------------------------------------
class Model:
    def __init__(self, content="T2", loops=2, M_s=1e13, y_s=0.345, M_phi=1e17, y_phi=1.0, yukawa=True, Y126=0.5,
                 gut_ratios=None, light_ratios=None, v311_ratio=1.0, planck_eps=(0, 0, 0, 0), planck_c=0.0,
                 kappa_V=0.0, b3_factor=1.0, n_higgs=1):
        self.content, self.loops, self.M_s, self.y_s, self.M_phi, self.y_phi = content, loops, M_s, y_s, M_phi, y_phi
        self.yukawa, self.Y126, self.gut_ratios, self.light_ratios = yukawa, Y126, gut_ratios or {}, light_ratios or {}
        self.v311_ratio, self.planck_eps, self.planck_c, self.kappa_V, self.b3_factor = v311_ratio, planck_eps, planck_c, kappa_V, b3_factor
        lo = min(loops, 2)
        b, bij = vc.mv(vc.SM_CG, vc.sm_fields(0, 0, n_higgs))
        self.sm0 = Seg(b, bij, lo, Y=(lambda t: self._yt2(t) * np.array([1.7, 1.5, 2.0])) if yukawa else None)
        b, bij = vc.mv(vc.SM_CG, vc.sm_fields(6, 2, n_higgs))
        self.sm1 = Seg(b, bij, lo, Y=(lambda t: self._yt2(t) * np.array([1.7, 1.5, 2.0]) + 14 * y_s**2) if yukawa else None)
        b, bij = vc.mv(vc.G_CG, vc.g3221_fields(content, True))
        self.gS = Seg(b, bij, lo, Y=(lambda t: self._yt2(t) * np.array([4.0, 4.0, 4.0, 4.0]) + 14 * y_s**2) if yukawa else None)
        b, bij = vc.mv(vc.G_CG, vc.g3221_fields(content, False))
        self.gN = Seg(b, bij, lo, Y=(lambda t: self._yt2(t) * np.array([4.0, 4.0, 4.0, 4.0])) if yukawa else None)
        self.so_lo = vc.b123_single(8, vc.SO10_CONTENT)
        self.so_hi = vc.b123_single(8, vc.SO10_CONTENT + vc.SO10_PHI)
        self.heavy = heavy_at_MU(content)
        self.light = light_at_vR(content)
        self.yt_cache = None  # (ln v_R, y_t(v_R))

    # crude one-loop y_t running in the SM, frozen above v_R (as the researcher did; the term is < 2%)
    def _yt2(self, t):
        if self.yt_cache is None:
            return YT_MZ**2
        tv, ytv = self.yt_cache
        if t >= tv:
            return ytv**2
        f = (t - math.log(MZ)) / (tv - math.log(MZ))
        return (YT_MZ + f * (ytv - YT_MZ))**2

    def set_yt(self, ln_vR):
        y, a, t = YT_MZ, A_MZ.copy(), math.log(MZ)
        n = 400
        h = (ln_vR - t) / n
        for _ in range(n):
            g2 = 4 * PI / a
            y += h * y / (16 * PI**2) * (4.5 * y * y - 8 * g2[2] - 2.25 * g2[1] - 0.85 * g2[0])
            a = a + h * self.sm0.rhs(t, a)
            t += h
        self.yt_cache = (ln_vR, y)

    def D_light(self):
        d = np.zeros(3)
        for name, kind, reps, mult in self.light:
            r = self.light_ratios.get(name, 1.0)
            if mult == 0:
                continue
            for i in range(3):
                d[i] += float(THR_COEF[kind] * S_i(reps, i, mult)) * math.log(r) / (2 * PI)
                if kind == "V":
                    d[i] += self.kappa_V * float(S_i(reps, i, mult)) / (12 * PI)
        return d

    def D_gut(self):
        d = np.zeros(4)
        for name, kind, reps in self.heavy:
            r = self.gut_ratios.get(name, 1.0)
            if r != 1.0:
                for i in range(4):
                    d[i] += float(THR_COEF[kind] * S_i(reps, i)) * math.log(r) / (2 * PI)
        for (name, kind, reps, mult), r in ((HEAVY_V311, self.v311_ratio), (HEAVY_V322, 1.0)):
            for i in range(4):
                d[i] += float(THR_COEF[kind] * S_i(reps, i, mult)) * math.log(r) / (2 * PI)
                d[i] += self.kappa_V * float(S_i(reps, i, mult)) / (12 * PI)
        return d

    def sm_to_vR(self, ln_vR):
        t0, ts = math.log(MZ), math.log(self.M_s)
        if ts < ln_vR:
            a, _, _ = rk4(self.sm0, A_MZ, t0, ts)
            a, _, _ = rk4(self.sm1, a, ts, ln_vR)
        else:
            a, _, _ = rk4(self.sm0, A_MZ, t0, ln_vR)
        return a

    def g3221_start(self, a_sm, a2R):
        a1, a2, a3 = a_sm + self.D_light()
        aBL = (a1 - 0.6 * a2R) / 0.4
        return np.array([a3, a2, a2R, aBL])

    def run_g(self, g0, t0, t1):
        ts = math.log(self.M_s)
        if ts <= t0:
            g, _, _ = rk4(self.gS, g0, t0, t1)
        elif ts >= t1:
            g, _, _ = rk4(self.gN, g0, t0, t1)
        else:
            g, _, _ = rk4(self.gN, g0, t0, ts)
            g, _, _ = rk4(self.gS, g, ts, t1)
        return g

    def residuals(self, x):
        ln_vR, ln_MU, a2R = x
        a_sm = self.sm_to_vR(ln_vR)
        g0 = self.g3221_start(a_sm, a2R)
        g = self.run_g(g0, ln_vR, ln_MU)
        E = g + self.D_gut()
        aU = E / (1.0 + self.planck_c * np.array(self.planck_eps))
        return np.array([aU[0] - aU[1], aU[2] - aU[1], aU[3] - aU[1]]), aU, g0, g

    def solve(self, guess=(math.log(2.5e13), math.log(2.5e16), 44.0)):
        self.set_yt(guess[0])
        f = lambda x: self.residuals(x)[0]  # noqa: E731
        x, info, ier, msg = fsolve(f, np.array(guess), full_output=True, xtol=1e-12)
        self.set_yt(x[0])
        x, info, ier, msg = fsolve(f, x, full_output=True, xtol=1e-12)
        r, aU, g0, g = self.residuals(x)
        ok = ier == 1 and np.max(np.abs(r)) < 1e-7
        return {"ok": bool(ok), "v_R": math.exp(x[0]), "M_U": math.exp(x[1]), "a2R_vR": float(x[2]),
                "alpha_U_inv": float(aU[1]), "aU_i": aU.tolist(), "g_vR": g0.tolist(), "g_MU": g.tolist(),
                "resid": float(np.max(np.abs(r))), "x": x.tolist()}

    def landau(self, M_U, aU, loops=None, b3_factor=None, t_end=math.log(1e23), h=0.002):
        loops = self.loops if loops is None else loops
        b3f = self.b3_factor if b3_factor is None else b3_factor
        tu, tphi = math.log(M_U), math.log(max(self.M_phi, M_U))
        yt2 = self._yt2(tu)
        Ylo = (14 * self.y_s**2 + 10 * yt2 + 15.75 * self.Y126**2) if self.yukawa else 0.0
        Yhi = Ylo + (4 * self.y_phi**2 if self.yukawa else 0.0)
        seg_lo = Seg([self.so_lo[0]], [[self.so_lo[1]]], loops, Y=lambda t: np.array([Ylo]), b3=[self.so_lo[2] * b3f])
        seg_hi = Seg([self.so_hi[0]], [[self.so_hi[1]]], loops, Y=lambda t: np.array([Yhi]), b3=[self.so_hi[2] * b3f])
        a, t, hit = rk4(seg_lo, [aU], tu, tphi, h, stop_at_alpha_inv=1.0)
        if not hit:
            a, t, hit = rk4(seg_hi, a, tphi, t_end, h, stop_at_alpha_inv=1.0)
        lam = math.exp(t) if hit else float("inf")
        # alpha^-1 at M_Pl
        tpl = math.log(MPL)
        a2, _, h2 = rk4(seg_lo, [aU], tu, min(tphi, tpl), h, stop_at_alpha_inv=1.0)
        if not h2 and tphi < tpl:
            a2, _, h2 = rk4(seg_hi, a2, tphi, tpl, h, stop_at_alpha_inv=1.0)
        return {"Lambda": lam, "ratio": lam / MPL, "a_inv_MPl": (None if h2 else float(a2[0])), "Ylo": Ylo, "Yhi": Yhi}


def proton_tau_years(M_X, aU_inv):
    f_pi, m_p, alpha_h, a_r, f_q = 0.139, 0.9382720813, 0.012, 2.726, 7.6
    tau = (4 / PI) * (f_pi**2 / m_p) * M_X**4 * aU_inv**2 / (alpha_h**2 * a_r**2 * f_q)
    return tau * 6.582119569e-25 / (365.25 * 86400)


def full_point(**kw):
    m = Model(**kw)
    s = m.solve()
    out = dict(s)
    if s["ok"]:
        for L in (2, 3):
            lam = m.landau(s["M_U"], s["alpha_U_inv"], loops=L)
            out[f"L{L}"] = lam["Lambda"]
            out[f"L{L}_ratio"] = lam["ratio"]
            out[f"ainv_MPl_{L}L"] = lam["a_inv_MPl"]
        out["tau_p"] = proton_tau_years(s["M_U"], s["alpha_U_inv"])
    return out, m


if __name__ == "__main__":
    import json
    res = {}
    print("scalar decomposition check (should be 64/3 x4):", scalar_decomposition_check("T2"), scalar_decomposition_check("T3"))
    # nominal reproduction
    for content in ("T2", "T3"):
        for M_s, y_s in ((5e12, 5e12 / 2.9e13), (1e13, 1e13 / 2.9e13)):
            for loops in (1, 2, 3):
                for yuk in (False, True):
                    for mphi in (1e10, 1e17):
                        r, m = full_point(content=content, loops=loops, M_s=M_s, y_s=y_s, M_phi=mphi, yukawa=yuk)
                        key = f"{content}_{loops}L_Ms{M_s:.0e}_yuk{int(yuk)}_Mphi{mphi:.0e}"
                        res[key] = r
                        print(f"{key}: ok={r['ok']} v_R={r['v_R']:.4e} M_U={r['M_U']:.4e} aU^-1={r['alpha_U_inv']:.4f} "
                              f"L2={r.get('L2',0):.4e} ({r.get('L2_ratio',0):.4f}) L3={r.get('L3',0):.4e} ({r.get('L3_ratio',0):.4f}) "
                              f"tau_p={r.get('tau_p',0):.3e} resid={r['resid']:.1e}", flush=True)
    json.dump(res, open(os.path.join(HERE, "vp_chain_nominal.json"), "w"), indent=1)
