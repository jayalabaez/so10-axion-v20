#!/usr/bin/env python3
"""Skeptic unification solver (independent of r2b_*): top-down/bottom-up shooting, LSODA integration."""
from __future__ import annotations
import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root
import sk_lib as L

PI = math.pi
SV_MU = np.array([float(x) for x in L.SV()[0]])
SV_Y = float(L.SV()[1])
R311 = math.sqrt(0.8)          # Am45 ratio M(3,1,1)/M(3,2,2) (input from K3, checked separately)
YT_MZ = 0.95

class Model:
    def __init__(self, content, loops=2, M_s=1e13, y_s=0.336, M_phi=1e17, y_phi=1.0, sv=+1, r311=R311,
                 light_r=None, gut_r=None, yuk_g=(4, 4, 4, 4), yukawa=True, method="LSODA", rtol=1e-10,
                 yt_mode="researcher", light_list=None, gut_list=None, planck_c=0.0, planck_s=+1, yt_mz=0.95):
        self.light = L.CONTENTS[content] if isinstance(content, str) else list(content)
        self.loops, self.M_s, self.y_s, self.M_phi, self.y_phi = loops, M_s, y_s, M_phi, y_phi
        self.sv, self.r311 = sv, r311
        self.light_r = light_r or {}
        self.gut_r = gut_r or {}
        self.yuk_g = np.array(yuk_g, float)
        self.yukawa, self.method, self.rtol, self.yt_mode = yukawa, method, rtol, yt_mode
        f = lambda bB: (np.array([float(x) for x in bB[0]]), np.array([[float(x) for x in r] for r in bB[1]]))
        self.sm0 = f(L.mv(L.SM_CG, L.fields_sm(False)))
        self.sm1 = f(L.mv(L.SM_CG, L.fields_sm(True)))
        self.g0 = f(L.mv(L.G3221_CG, L.fields_g(self.light, False)))
        self.g1 = f(L.mv(L.G3221_CG, L.fields_g(self.light, True)))
        # light thresholds at v_R (SM language) and heavy at M_U (G3221 language)
        self.Dl = np.zeros(3)
        for idx, (kind, reps, m, name) in enumerate(L.light_thr_states(self.light)):
            r = self.light_r.get(name, self.light_r.get("*", 1.0)) if kind != "vector" else self.light_r.get("W_R", self.light_r.get("*", 1.0))
            if light_list is not None:
                r = light_list[idx]
            if r != 1.0:
                self.Dl += np.array([float(L.thr_b(kind, reps, i, m)) for i in range(3)]) * math.log(r) / (2 * PI)
        self.Dl[0] += sv * SV_Y / (12 * PI)
        self.Dg = np.zeros(4)
        for idx, (kind, reps, m, name) in enumerate(L.heavy_states(self.light)):
            r = self.gut_r.get(name, self.gut_r.get("*", 1.0))
            if gut_list is not None:
                r = gut_list[idx]
            if r != 1.0:
                self.Dg += np.array([float(L.thr_b(kind, reps, i, m)) for i in range(4)]) * math.log(r) / (2 * PI)
        kind, reps, m, _ = L.HEAVY_VEC[1]
        self.Dg += np.array([float(L.thr_b(kind, reps, i, m)) for i in range(4)]) * math.log(self.r311) / (2 * PI)
        self.Dg += sv * SV_MU / (12 * PI)
        self.yt_vR = None
        self.planck_c, self.planck_s, self.yt_mz = planck_c, planck_s, yt_mz

    def eps(self, tU, aU):
        if self.planck_c == 0.0:
            return np.zeros(4)
        p, a = 1 / math.sqrt(2), -1 / math.sqrt(6)
        g = math.sqrt(4 * PI / aU)
        phi = math.exp(tU) / (0.6454972243679028 * g)
        K = np.array([-2 * a, 2 * self.planck_s * p, -2 * self.planck_s * p, 4 * a]) * phi
        return self.planck_c * K / L.MPL

    # ---- RHS ----
    def rhs_sm(self, bB, withS):
        b, B = bB
        cy = np.array([1.7, 1.5, 2.0])
        def f(t, y):
            a = y[:3]
            d = -b / (2 * PI)
            if self.loops >= 2:
                d = d - B.dot(1.0 / a) / (8 * PI ** 2)
                if self.yukawa:
                    d = d + (cy * y[3] ** 2 + (14 * self.y_s ** 2 if withS else 0.0)) / (32 * PI ** 3)
            g2 = 4 * PI / a
            dyt = y[3] / (16 * PI ** 2) * (4.5 * y[3] ** 2 - 8 * g2[2] - 2.25 * g2[1] - 0.85 * g2[0])
            return np.append(d, dyt)
        return f

    def rhs_g(self, bB, withS, yt):
        b, B = bB
        def f(t, a):
            d = -b / (2 * PI)
            if self.loops >= 2:
                d = d - B.dot(1.0 / a) / (8 * PI ** 2)
                if self.yukawa:
                    d = d + (self.yuk_g * yt ** 2 + (14 * self.y_s ** 2 if withS else 0.0)) / (32 * PI ** 3)
            return d
        return f

    def integ(self, f, y0, t0, t1):
        if abs(t1 - t0) < 1e-14:
            return np.array(y0, float)
        s = solve_ivp(f, (t0, t1), np.array(y0, float), method=self.method, rtol=self.rtol, atol=1e-12)
        if not s.success:
            raise RuntimeError(s.message)
        return s.y[:, -1]

    # ---- bottom-up SM part ----
    def sm_to(self, tR):
        t0, ts = math.log(L.MZ), math.log(self.M_s)
        y = np.append(L.AINV_MZ, self.yt_mz)
        if ts < tR:
            y = self.integ(self.rhs_sm(self.sm0, False), y, t0, ts)
            y = self.integ(self.rhs_sm(self.sm1, True), y, ts, tR)
        else:
            y = self.integ(self.rhs_sm(self.sm0, False), y, t0, tR)
        return y

    # ---- top-down G3221 part ----
    def g_down(self, tU, aU, tR, yt):
        ts = math.log(self.M_s)
        a = aU * (1 + self.eps(tU, aU)) - self.Dg
        if ts >= tU:
            a = self.integ(self.rhs_g(self.g0, False, yt), a, tU, tR)
        elif ts > tR:
            a = self.integ(self.rhs_g(self.g1, True, yt), a, tU, ts)
            a = self.integ(self.rhs_g(self.g0, False, yt), a, ts, tR)
        else:
            a = self.integ(self.rhs_g(self.g1, True, yt), a, tU, tR)
        return a

    def resid(self, x):
        tR, tU, aU = x
        y = self.sm_to(tR)
        asm, yt = y[:3], y[3]
        ag = self.g_down(tU, aU, tR, yt)
        a1h, a2h, a3h = asm + self.Dl
        return np.array([ag[0] - a3h, ag[1] - a2h, 0.6 * ag[2] + 0.4 * ag[3] - a1h]), yt

    def solve(self, guess=(math.log(1e11), math.log(5e15), 34.0)):
        best = None
        for g in [guess, (math.log(1e10), math.log(6e15), 34.6), (math.log(7e12), math.log(2.5e15), 33.5),
                  (math.log(1e12), math.log(1e16), 30.0), (math.log(3e13), math.log(2e16), 27.0)]:
            try:
                sol = root(lambda x: self.resid(x)[0], np.array(g, float), method="hybr", tol=1e-13)
            except Exception:
                continue
            r = np.max(np.abs(self.resid(sol.x)[0]))
            if r < 1e-9 and sol.x[0] < sol.x[1]:
                best = sol.x
                break
        if best is None:
            return None
        tR, tU, aU = best
        yt = self.resid(best)[1]
        self.yt_vR = yt
        return {"v_R": math.exp(tR), "M_U": math.exp(tU), "aU": aU, "yt_vR": yt,
                "resid": float(np.max(np.abs(self.resid(best)[0])))}

    # ---- SO(10) Landau ----
    def landau(self, M_U, aU, loops=2, yt=None, b3=None, tmax=math.log(1e25)):
        yt = self.yt_vR if yt is None else yt
        blo, Blo = [float(x) for x in L.mv_so10(L.SO10_LO)]
        bhi, Bhi = [float(x) for x in L.mv_so10(L.SO10_HI)]
        b3lo, b3hi = (b3 if b3 is not None else (142437589 / 864, 5041501 / 32))
        Ylo = 14 * self.y_s ** 2 + 10 * yt ** 2 + 2 * (126 / 16) * 0.5
        Yhi = Ylo + 4 * self.y_phi ** 2
        def mk(b, B, Y, b3v):
            def f(t, a):
                d = -b / (2 * PI) - B / (8 * PI ** 2 * a[0]) + (Y / (32 * PI ** 3) if self.yukawa else 0)
                if loops >= 3:
                    d = d - b3v / (32 * PI ** 3 * a[0] ** 2)
                return [d]
            return f
        ev = lambda t, a: a[0] - 1.0
        ev.terminal, ev.direction = True, -1
        tU, tphi = math.log(M_U), math.log(max(self.M_phi, M_U))
        s = solve_ivp(mk(blo, Blo, Ylo, b3lo), (tU, tphi), [aU], method="RK45", rtol=1e-11, atol=1e-12, events=ev)
        if s.t_events[0].size:
            return math.exp(s.t_events[0][0]) / L.MPL
        s2 = solve_ivp(mk(bhi, Bhi, Yhi, b3hi), (tphi, tmax), [s.y[0, -1]], method="RK45", rtol=1e-11, atol=1e-12,
                       events=ev)
        if s2.t_events[0].size:
            return math.exp(s2.t_events[0][0]) / L.MPL
        return float("inf")

# ---- proton decay ----
HBAR, YEAR = 6.582119569e-25, 365.25 * 24 * 3600

def tau_repo(MX, aUinv, alpha_h=0.012):
    f_pi, m_p, A_R, F_q = 0.139, 0.9382720813, 2.726, 7.6
    G = (PI * m_p / (4 * f_pi ** 2)) * (1 / aUinv) ** 2 * F_q * A_R ** 2 * alpha_h ** 2 / MX ** 4
    return HBAR / G / YEAR

def tau_lattice(MX, aUinv, W0=0.131, A=2.726, Vud=0.9737, kRL=None):
    """Gamma = m_p/(32 pi) (1-x)^2 A^2 W0^2 (|C_LR|^2+|C_RL|^2) with C = g^2/(2 M^2) * c ."""
    m_p, m_pi = 0.9382720813, 0.1349768
    g2 = 4 * PI / aUinv
    k2 = g2 / (2 * MX ** 2)
    cLR = 2 * k2 * (1 + Vud ** 2)
    cRL = (4 * k2) if kRL is None else kRL * k2
    G = m_p / (32 * PI) * (1 - (m_pi / m_p) ** 2) ** 2 * A ** 2 * W0 ** 2 * (cLR ** 2 + cRL ** 2)
    return HBAR / G / YEAR

def point(content, two_pass=True, **kw):
    m = Model(content, **kw)
    r = m.solve()
    if r is None:
        return None, m
    r["tau_repo"] = tau_repo(r["M_U"], r["aU"])
    r["tau_lat"] = tau_lattice(r["M_U"], r["aU"])
    return r, m
