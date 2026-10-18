#!/usr/bin/env python3
"""D-D-literature, criterion D4: two-loop unification / proton decay / Landau for chains in which SU(2)_R and SU(4)
break at M_U (one-step SO(10) -> SM, or SO(10) -> G3211 -> SM; at one loop and, for SM-like content between v_R and
M_U, also at two loops up to U(1) kinetic mixing, G3211 is SM-equivalent for the unification of alpha_Y: EXACT at one
loop, see REPORT), with the B63 S-sector at M_s and light scalar multiplets taken from 210 / 126bar / 10 (/ 45 / 54).

Conventions (r2b_lib.py, copied unchanged from R2-B): t = ln(mu/GeV), exact Machacek-Vaughn b_i, b_ij (Fractions),
DOP853; two-loop Yukawa term: top (SM coefficients 1.7, 1.5, 2.0) + 14 y_s^2 above M_s (T_S = 14), as in R2-B.
Matching at M_U (one loop, MS-bar): alpha_i^-1(M_U)|_SM = alpha_U^-1 - S_V,i/(12 pi) - (1/2pi) sum_heavy b_i^k ln(M_k/M_U),
M_U := mass of the (3,2,-5/6) and (3,2,1/6) vectors (proton-decay mediators); S_V from the 33 heavy vectors
(3,2,-5/6)+(3,2,1/6)+(3,1,2/3) (+cc) + (1,1,1)(+cc) + (1,1,0).  Light states: step decoupling at their masses (MS-bar
one-loop matching with no constant for scalars).
Proton: tau(p -> e+ pi0) in the DIRECT LATTICE normalisation of R2-B (W0 = 0.131 GeV^2, both X and X' exchange,
F = (1 + |V_ud|^2)^2 + 4) with the CHAIN-SPECIFIC A_R = A_L x A_SD (A_L = 1.25; A_SD from the actual one-loop segment
b's with gamma = (23/20, 9/4, 2), i.e. the larger e^c-type exponent -> conservative).  Kill threshold 2.4e34 yr.
Landau: r2b_model.Chain.landau (SO(10) x U(1)_X, B63 + Phi pair at 1e17, two-loop with Yukawas), with the SO(10)-phase
scalar content of the design.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import warnings
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from scipy.optimize import fsolve, brentq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from r2b_lib import (A1_MZ, A2_MZ, A3_MZ, M_PL_RED, MZ, PI, SO10, SU2, SU3, Y_T_MZ, Segment, mv_coefficients,
                     run_segment, s_factor, threshold_b, ysm, pgj_b, pgj_invariants, C_G_SO10)
import r2b_model as RM

SM_C2 = (F(0), F(2), F(3))


def smrep(y, su2, su3):
    return (ysm(F(y)), SU2[su2], SU3[su3])


# ------------------------------------------------------------------------------------------------------------------
# SM decomposition of the Pati-Salam pieces (Y = T3R + (B-L)/2), exact.
# ------------------------------------------------------------------------------------------------------------------
SU4_TO_SU3 = {
    "1": [("1", F(0))], "4": [("3", F(1, 3)), ("1", F(-1))], "4b": [("3b", F(-1, 3)), ("1", F(1))],
    "6": [("3", F(-2, 3)), ("3b", F(2, 3))], "10": [("6", F(2, 3)), ("3", F(-2, 3)), ("1", F(-2))],
    "10b": [("6b", F(-2, 3)), ("3b", F(2, 3)), ("1", F(2))],
    "15": [("8", F(0)), ("3", F(4, 3)), ("3b", F(-4, 3)), ("1", F(0))],
    "20p": [("6", F(-4, 3)), ("6b", F(4, 3)), ("8", F(0))],
}
PS = {   # SO(10) irrep -> list of (SU4, dim2L, dim2R); 'real' flag
    "210": ([("1", 1, 1), ("15", 1, 1), ("6", 2, 2), ("15", 3, 1), ("15", 1, 3), ("10", 2, 2), ("10b", 2, 2)], True),
    "126b": ([("6", 1, 1), ("10", 3, 1), ("10b", 1, 3), ("15", 2, 2)], False),
    "10": ([("6", 1, 1), ("1", 2, 2)], False),
    "45": ([("15", 1, 1), ("1", 3, 1), ("1", 1, 3), ("6", 2, 2)], True),
    "54": ([("1", 1, 1), ("20p", 1, 1), ("1", 3, 3), ("6", 2, 2)], True),
}


def sm_pieces(irrep):
    """List of SM pieces (su3, su2L, Y, weight) where weight = 1/2 for pieces of a real irrep (each SM piece counted
    with its conjugate separately), 1 for a complex irrep.  b-contribution of a piece = weight * (1/3) S."""
    content, real = PS[irrep]
    w = F(1, 2) if real else F(1)
    out = []
    for su4, dL, dR in content:
        for su3, bl in SU4_TO_SU3[su4]:
            for k in range(dR):
                t3r = F(dR - 1, 2) - k
                y = t3r + bl / 2
                out.append((su3, str(dL), y, w))
    return out


def key(su3, su2, y):
    c = {"3b": "3", "6b": "6"}.get(su3, su3)
    # conjugate pairs have identical b's: canonical key uses |Y| and the non-barred colour rep
    return (c, su2, abs(F(y)))


GOLDSTONES = [("3", "2", F(-5, 6)), ("3b", "2", F(5, 6)), ("3", "2", F(1, 6)), ("3b", "2", F(-1, 6)),
              ("3", "1", F(2, 3)), ("3b", "1", F(-2, 3)), ("1", "1", F(1)), ("1", "1", F(-1)), ("1", "1", F(0))]


def heavy_scalar_list(so10_scalars, light):
    """SM pieces of the SO(10) scalars minus Goldstones (33 real) minus the light states (and the SM Higgs)."""
    pieces = []
    for irrep in so10_scalars:
        pieces += [list(p) for p in sm_pieces(irrep)]

    def remove(su3, su2, y, w):
        for p in pieces:
            if key(p[0], p[1], p[2]) == key(su3, su2, y) and p[3] >= w and p[3] > 0:
                p[3] -= w
                return True
        return False
    for g in GOLDSTONES:              # each Goldstone piece is one real dof-set = weight 1/2 of a complex piece
        assert remove(g[0], g[1], g[2], F(1, 2)), g
    assert remove("1", "2", F(1, 2), F(1, 2)) and remove("1", "2", F(-1, 2), F(1, 2))   # SM Higgs (complex doublet)
    for (su3, su2, y, kind) in light:
        w = F(1, 2) if kind == "real" else F(1)
        if kind == "real":
            assert remove(su3, su2, y, F(1, 2)), (su3, su2, y)
        else:
            assert remove(su3, su2, y, F(1, 2)) and remove({"3": "3b", "6": "6b", "8": "8", "1": "1"}[su3] if y != 0 else su3,
                                                             su2, -y, F(1, 2)), (su3, su2, y)
    return [p for p in pieces if p[3] > 0]


# ------------------------------------------------------------------------------------------------------------------
# field tables
# ------------------------------------------------------------------------------------------------------------------
SIXTEEN_SM = RM.SIXTEEN_SM
TEN_SM = RM.TEN_SM
N16_S, N10_S = 6, 2


def light_field(su3, su2, y, kind):
    return (f"({su3},{su2},{y})", kind, smrep(y, su2, su3), 1)


def sm_fields(active_light, with_s):
    out = [(n, k, r, 3 + (N16_S if with_s else 0)) for n, k, r in SIXTEEN_SM]
    if with_s:
        out += [(n, k, r, N10_S) for n, k, r in TEN_SM]
    out.append(("H", "cplx", smrep(F(1, 2), "2", "1"), 1))
    for (su3, su2, y, kind) in active_light:
        out.append(light_field(su3, su2, y, kind))
    return out


HEAVY_VECTORS = [("X", "vector", smrep(F(-5, 6), "2", "3"), 2), ("Xp", "vector", smrep(F(1, 6), "2", "3"), 2),
                 ("V3", "vector", smrep(F(2, 3), "1", "3"), 2), ("WR", "vector", smrep(F(1), "1", "1"), 2),
                 ("Zp", "vector", smrep(F(0), "1", "1"), 1)]


def sv_sm():
    return np.array([float(sum(s_factor(r, i) * m for _n, _k, r, m in HEAVY_VECTORS)) for i in range(3)])


SV = sv_sm()


class Chain1:
    def __init__(self, light, M_light, M_s=1e13, y_s=0.336, so10_scalars=("210", "126b", "10"), loops=2,
                 sv_sign=+1, heavy_ratios=None, vec_ratios=None):
        self.light = list(light)           # (su3, su2, Y, kind)
        self.M_light = list(M_light)
        self.M_s, self.y_s, self.loops, self.sv_sign = M_s, y_s, loops, sv_sign
        self.so10_scalars = so10_scalars
        self.heavy = heavy_scalar_list(so10_scalars, light)
        self.heavy_ratios = heavy_ratios or {}
        self.vec_ratios = vec_ratios or {}
        self._seg_cache = {}

    def seg(self, active_mask, with_s):
        k = (tuple(active_mask), with_s)
        if k not in self._seg_cache:
            act = [l for l, a in zip(self.light, active_mask) if a]
            b, bij = mv_coefficients(SM_C2, sm_fields(act, with_s))
            ys = self.y_s
            yuk = (lambda t, a, ws=with_s: np.array([1.7, 1.5, 2.0]) * Y_T_MZ ** 2 * 0.0 + self._yt2(t) * np.array([1.7, 1.5, 2.0])
                   + (14.0 * ys ** 2 if ws else 0.0))
            self._seg_cache[k] = (Segment(b, bij, yuk=yuk, loops=self.loops), [float(x) for x in b])
        return self._seg_cache[k][0]

    def _yt2(self, t):
        # one-loop SM top Yukawa interpolation (EST-level, two-loop term only): y_t(M_Z)=0.95 -> ~0.45 at 1e16
        f = min(max((t - math.log(MZ)) / (math.log(1e16) - math.log(MZ)), 0.0), 1.2)
        return (Y_T_MZ + f * (0.45 - Y_T_MZ)) ** 2

    def thresholds(self, M_U):
        pts = [(m, i) for i, m in enumerate(self.M_light)] + [(self.M_s, "S")]
        return sorted([p for p in pts if p[0] < M_U], key=lambda p: p[0])

    def run(self, ln_MU, need_segments=False):
        M_U = math.exp(ln_MU)
        a = np.array([A1_MZ, A2_MZ, A3_MZ])
        t = math.log(MZ)
        active = [False] * len(self.light)
        with_s = False
        segs = []
        for m, which in self.thresholds(M_U):
            tm = math.log(max(m, MZ))
            if tm > t:
                sg = self.seg(active, with_s)
                a0 = a.copy()
                a, _, _ = run_segment(sg, a, t, tm)
                segs.append((t, tm, a0.copy(), a.copy(), sg.b.copy()))
                t = tm
            if which == "S":
                with_s = True
            else:
                active[which] = True
        sg = self.seg(active, with_s)
        a0 = a.copy()
        a, _, _ = run_segment(sg, a, t, ln_MU)
        segs.append((t, ln_MU, a0.copy(), a.copy(), sg.b.copy()))
        return (a, segs) if need_segments else a

    def D_gut(self):
        d = self.sv_sign * SV / (12 * PI)
        for p in self.heavy:
            r = self.heavy_ratios.get(key(p[0], p[1], p[2]), self.heavy_ratios.get("*", 1.0))
            if r != 1.0:
                reps = smrep(p[2], p[1], {"3b": "3", "6b": "6"}.get(p[0], p[0]))
                for i in range(3):
                    d[i] += float(F(1, 3) * p[3] * s_factor(reps, i)) * math.log(r) / (2 * PI)
        for n, kind, reps, mult in HEAVY_VECTORS:
            r = self.vec_ratios.get(n, 1.0)
            if r != 1.0:
                for i in range(3):
                    d[i] += float(threshold_b("vector", reps, i, mult)) * math.log(r) / (2 * PI)
        return d

    def resid(self, x, free_idx):
        ln_MU, aU = x[0], x[1]
        if free_idx is not None:
            self.M_light[free_idx] = math.exp(x[2])
        a = self.run(ln_MU)
        E = a + self.D_gut()          # alpha_i^-1(M_U)|_SM + corrections = alpha_U^-1
        return E - aU

    def solve(self, free_idx=None, guess=(math.log(1e16), 35.0, math.log(1e8))):
        def f(x):
            try:
                r = self.resid(x, free_idx)
                return r if free_idx is not None else r[:2]
            except Exception:
                return np.array([1e3, 1e3, 1e3])[: (3 if free_idx is not None else 2)]
        best = None
        g0 = list(guess)
        starts = [g0]
        for lmu in (math.log(3e15), math.log(3e16)):
            for ll in (math.log(1e4), math.log(1e9), math.log(1e13)):
                starts.append([lmu, 35.0, ll])
        for s in starts:
            x0 = np.array(s[: (3 if free_idx is not None else 2)], float)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                x, info, ier, msg = fsolve(f, x0, full_output=True, xtol=1e-12)
            r = np.max(np.abs(f(x)))
            if r < 1e-7:
                ok = True
                if free_idx is not None:
                    ml = math.exp(x[2])
                    ok = (MZ < ml < math.exp(x[0]))
                if ok and (best is None or r < best[1]):
                    best = (x, r)
                    break
        if best is None:
            return None
        x = best[0]
        if free_idx is not None:
            self.M_light[free_idx] = math.exp(x[2])
        return {"M_U": math.exp(x[0]), "alpha_U_inv": float(x[1]), "M_light": list(self.M_light), "resid": best[1]}

    def A_SD(self, M_U, gam=(23 / 20, 9 / 4, 2.0)):
        a, segs = self.run(math.log(M_U), need_segments=True)
        A = 1.0
        for (t0, t1, a0, a1, b) in segs:
            for i in range(3):
                if abs(b[i]) < 1e-12:
                    A *= math.exp(gam[i] * (t1 - t0) / (2 * PI) / a0[i])
                else:
                    # one-loop exact: (alpha(mu_lo)/alpha(mu_hi))^(gam/b) with alpha_i^-1 from the actual run
                    A *= (a1[i] / a0[i]) ** (-gam[i] / b[i])   # r2b sign: d a^-1/dt = -b/2pi
        return A


def tau_direct(M_X, aU_inv, A_R, W0=0.131, Vud=0.9737):
    m_p, m_pi = 0.9382720813, 0.1349768
    hbar, year = 6.582119569e-25, 365.25 * 24 * 3600
    fq = (1 + Vud ** 2) ** 2 + 4
    gam = (PI * m_p / 2) * (1 - (m_pi / m_p) ** 2) ** 2 * A_R ** 2 * W0 ** 2 * (1 / aU_inv) ** 2 * fq / M_X ** 4
    return hbar / gam / year


def landau(M_U, aU_inv, so10_scalars, M_s=1e13, y_s=0.336, loops=2):
    p = RM.Params(M_s=M_s, y_s=y_s, loops=loops)
    ch = RM.Chain(p)
    extra = []
    for s in so10_scalars:
        if s in ("45", "54"):
            extra.append((s, "real", 1))
    base = [c for c in RM.SO10_BASE if not (c[0] == "210" and "210" not in so10_scalars)]
    if extra or len(base) != len(RM.SO10_BASE):
        ch.b_so10_lo = RM.so10_coeffs(base + extra)
        ch.b_so10_hi = RM.so10_coeffs(base + RM.SO10_PHI_PAIR + extra)
    RM.set_yt(ch, 1e13)
    out = {}
    for L in ((2, 3) if loops >= 2 else (1,)):
        lm = ch.landau(M_U, aU_inv, loops=L)
        out[f"L{L}"] = lm["Lambda_over_MPl"]
    out["b_so10"] = [str(x) for x in ch.b_so10_lo]
    return out


# light-state catalogue (su3, su2, Y, kind) with the SO(10) irreps that contain them
CAT = {
    "(8,1,0)": ("8", "1", F(0), "real"),      # 210 (15,1,1)/(15,1,3); 45 (15,1,1); 54 (20',1,1)
    "(8,3,0)": ("8", "3", F(0), "real"),      # 210 (15,3,1)
    "(1,3,0)": ("1", "3", F(0), "real"),      # 210 (15,3,1); 45 (1,3,1)
    "(8,2,1/2)": ("8", "2", F(1, 2), "cplx"),  # 126bar (15,2,2)
    "(1,3,1)": ("1", "3", F(1), "cplx"),      # 126bar (10,3,1) Delta_L
    "(6,3,1/3)": ("6", "3", F(1, 3), "cplx"),  # 126bar (10,3,1)
    "(3,3,-1/3)": ("3", "3", F(-1, 3), "cplx"),  # 126bar (10,3,1)
    "(6,1,4/3)": ("6", "1", F(4, 3), "cplx"),  # 126bar (10b,1,3)
    "(3,2,1/6)": ("3", "2", F(1, 6), "cplx"),  # 210 (6,2,2)/(10,2,2), 126bar (15,2,2), 45 (6,2,2)
    "(6,2,5/6)": ("6", "2", F(5, 6), "cplx"),  # 210 (10,2,2)
    "(3,3,2/3)": ("3", "3", F(2, 3), "cplx"),  # 210 (15,3,1)
    "(1,3,3)?": ("1", "3", F(1), "real"),
}


def point(names, masses, free, so10=("210", "126b", "10"), M_s=1e13, y_s=0.336, loops=2, sv_sign=+1,
          heavy_ratios=None, vec_ratios=None):
    light = [CAT[n] for n in names]
    ch = Chain1(light, list(masses), M_s=M_s, y_s=y_s, so10_scalars=so10, loops=loops, sv_sign=sv_sign,
                heavy_ratios=heavy_ratios, vec_ratios=vec_ratios)
    r = ch.solve(free_idx=free)
    if r is None:
        return None
    A = 1.25 * ch.A_SD(r["M_U"])
    r["A_R"] = A
    r["tau_lat_yr"] = tau_direct(r["M_U"], r["alpha_U_inv"], A)
    r["tau_lat_A2.726_yr"] = tau_direct(r["M_U"], r["alpha_U_inv"], 2.726)
    r["names"] = names
    return r


def main():
    out = {"SV_SM": SV.tolist(), "checks": {}, "scans": {}}
    # sanity: SM-only A_SD and the S_V vector
    ch0 = Chain1([], [], M_s=1e13)
    out["checks"]["A_R_SM_to_1e16"] = 1.25 * ch0.A_SD(1e16)
    print("S_V(SM) =", SV, " A_R(SM, M_U=1e16) =", out["checks"]["A_R_SM_to_1e16"], flush=True)
    # one light state alone (free mass)
    single = {}
    for n in CAT:
        if n.endswith("?"):
            continue
        r = point([n], [1e8], 0)
        single[n] = r
        if r:
            print(f"single {n:12s}: M_light {r['M_light'][0]:.3g}  M_U {r['M_U']:.3g}  aU^-1 {r['alpha_U_inv']:.2f}  "
                  f"tau_lat {r['tau_lat_yr']:.3g} (A_R {r['A_R']:.2f})", flush=True)
        else:
            print(f"single {n:12s}: no solution", flush=True)
    out["scans"]["single"] = single
    # pairs: first mass scanned on a grid, second free
    pairs = {}
    names = [n for n in CAT if not n.endswith("?")]
    grid = [1e3, 1e4, 1e6, 1e8, 1e10, 1e12]
    for a, b in itertools.permutations(names, 2):
        rows = []
        for m in grid:
            r = point([a, b], [m, 1e8], 1)
            if r and r["M_light"][1] < r["M_U"]:
                rows.append({"M_a": m, "M_b": r["M_light"][1], "M_U": r["M_U"], "aU_inv": r["alpha_U_inv"],
                             "tau_lat": r["tau_lat_yr"], "A_R": r["A_R"]})
        if rows:
            pairs[f"{a}@grid + {b}@free"] = rows
            best = max(rows, key=lambda z: z["tau_lat"])
            print(f"pair {a:10s}(grid) + {b:10s}(free): best tau_lat {best['tau_lat']:.3g} at M_a {best['M_a']:.0e}, "
                  f"M_b {best['M_b']:.3g}, M_U {best['M_U']:.3g}, aU^-1 {best['aU_inv']:.2f}", flush=True)
    out["scans"]["pairs"] = pairs
    (HERE / "d4_unif_scan.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
