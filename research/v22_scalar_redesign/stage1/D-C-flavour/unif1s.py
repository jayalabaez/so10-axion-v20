"""D4 for one-step SO(10) -> SM chains (design V1 = A1-EFT and variants): two-loop unification with exact
Machacek-Vaughn coefficients, proton lifetime in the lattice x chain-A_R normalisation, two-loop SO(10) Landau scale.

Building blocks are imported from unif_core.py = verbatim copy of the R2-B skeptic library sk2_lib.py (exact MV
one/two-loop coefficients for product groups, heavy-vector MS-bar constant, tau_lattice, SO(10) running conventions).
New here: a one-step SM chain  M_Z -> [light SM multiplets at their own masses m_k, B63 S-sector at M_s] -> M_U,
matching at M_U to SO(10) with  alpha_U^-1 = alpha_i^-1(M_U) + sum_heavy b_i ln(M_k/M_U)/(2 pi) + S_V,i/(12 pi),
S_V = (8, 6, 5) for (U1_Y GUT-normalised, SU2, SU3) from the 33 heavy vectors (3,2,-5/6)+(3,2,1/6)+(3,1,2/3)+(1,1,1)+(1,1,0)
(EXACT: C2(SO10) - C2(H_i) = 8 - (0, 2, 3)).  M_U := mass of the (3,2,-5/6) and (3,2,1/6) vectors (p-decay mediators).
Conventions as unif_core: t = ln(mu/GeV), d alpha^-1/dt = -b/(2 pi) - B alpha/(8 pi^2) + Y/(32 pi^3).
"""
from __future__ import annotations

import math
from fractions import Fraction as Fr

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

import unif_core as U

PI = math.pi
MPL = 2.435e18

# --------------------------------------------------------------------------------------------- light-state catalogue
# SM-language multiplets available from 210 (real), 126bar and 10 (complex); 'safe' = no renormalizable coupling to
# fermion bilinears (210 states; the 126bar colour triplets/sextets couple through F.F.Delta and mediate p decay).
LIGHT = {
    "(8,1,0)210": ("real", U.sm(0, "1", "8"), True),
    "(1,3,0)210": ("real", U.sm(0, "3", "1"), True),
    "(8,3,0)210": ("real", U.sm(0, "3", "8"), True),
    "(3,2,1/6)210": ("cplx", U.sm(Fr(1, 6), "2", "3"), True),
    "(6,2,-1/6)210": ("cplx", U.sm(Fr(-1, 6), "2", "6"), True),
    "(6,2,5/6)210": ("cplx", U.sm(Fr(5, 6), "2", "6"), True),
    "(3,3,2/3)210": ("cplx", U.sm(Fr(2, 3), "3", "3"), True),
    "(8,1,1)210": ("cplx", U.sm(1, "1", "8"), True),
    "(1,2,1/2)2nd": ("cplx", U.sm(Fr(1, 2), "2", "1"), True),
    "(1,2,3/2)210": ("cplx", U.sm(Fr(3, 2), "2", "1"), True),
    "(8,2,1/2)126": ("cplx", U.sm(Fr(1, 2), "2", "8"), False),
    "(1,3,1)126DL": ("cplx", U.sm(1, "3", "1"), True),
    "(6,3,1/3)126": ("cplx", U.sm(Fr(1, 3), "3", "6"), False),
    "(3,3,-1/3)126": ("cplx", U.sm(Fr(-1, 3), "3", "3"), False),
}

SV_SM = np.array([8.0, 6.0, 5.0])     # (U1_Y, SU2, SU3) heavy-vector index sums, EXACT


def check_sv():
    vecs = [(U.sm(Fr(-5, 6), "2", "3"), 2), (U.sm(Fr(1, 6), "2", "3"), 2), (U.sm(Fr(2, 3), "1", "3"), 2),
            (U.sm(1, "1", "1"), 2), (U.sm(0, "1", "1"), 1)]
    tot = [Fr(0)] * 3
    for reps, m in vecs:
        sv = U.sv_const(reps, m)
        tot = [a + b for a, b in zip(tot, sv)]
    return [str(x) for x in tot]


# ----------------------------------------------------------------------------------------------- chain model
class OneStep:
    def __init__(self, light: dict, loops=2, M_s=1e13, y_s=0.336, yt2=0.30, sv=1.0, heavy_shift=None,
                 extra_so10=None, M_phi=1e17):
        """light: {name: mass_GeV}; heavy_shift: optional (3,) extra threshold vector added at M_U (alpha^-1 units)."""
        self.light = dict(light)
        self.loops, self.M_s, self.y_s, self.yt2, self.sv = loops, M_s, y_s, yt2, sv
        self.heavy_shift = np.zeros(3) if heavy_shift is None else np.asarray(heavy_shift, float)
        self.extra_so10 = extra_so10 or []
        self.M_phi = M_phi
        self._cache = {}

    def fields_at(self, mu):
        withS = mu > self.M_s
        f = U.sm_fields(withS)
        for name, m in self.light.items():
            if mu > m:
                kind, reps, _safe = LIGHT[name]
                f.append((kind, reps, 1))
        return f, withS

    def seg_rhs(self, mu):
        f, withS = self.fields_at(mu)
        key = (tuple(sorted(n for n, m in self.light.items() if mu > m)), withS)
        if key not in self._cache:
            b, bij = U.mv(U.CG_SM, f)
            L2 = 1.0 if self.loops >= 2 else 0.0
            bij = [[x * Fr(int(L2)) for x in row] for row in bij]
            yk = np.array([1.7, 1.5, 2.0]) * self.yt2 + (14 * self.y_s ** 2 if withS else 0.0)
            self._cache[key] = (b, bij, U.make_rhs(b, bij, yk * L2))
        return self._cache[key]

    def run_to(self, MU, gam=None):
        """alpha_i^-1 (U1,SU2,SU3) at MU from M_Z; optionally accumulate int sum gamma_i alpha_i/(2pi) dt."""
        scales = sorted([m for m in self.light.values() if U.MZ < m < MU] + ([self.M_s] if U.MZ < self.M_s < MU else []))
        pts = [U.MZ] + scales + [MU]
        a = np.array([U.A1I_MZ, U.A2I_MZ, 1 / U.A3_MZ])
        I = 0.0
        for lo, hi in zip(pts[:-1], pts[1:]):
            rhs = self.seg_rhs(math.sqrt(lo * hi))[2]
            t0, t1 = math.log(lo), math.log(hi)
            if gam is None:
                a = U.run(rhs, a, t0, t1)
            else:
                def f(t, y):
                    return np.concatenate([rhs(t, y[:-1]), [float(np.sum(gam / y[:-1])) / (2 * PI)]])
                s = solve_ivp(f, (t0, t1), np.concatenate([a, [0.0]]), method="DOP853", rtol=1e-11, atol=1e-12)
                a, I = s.y[:-1, -1], I + s.y[-1, -1]
        return (a, I) if gam is not None else a

    def at_MU(self, lMU):
        MU = math.exp(lMU)
        a = self.run_to(MU)
        return a + self.sv * SV_SM / (12 * PI) + self.heavy_shift

    def solve(self, free, guess):
        """free = name of the light state whose mass is solved for (or None: then a two-condition solve with
        unknowns (ln M_U) only is over-determined -> returns the mismatch).  guess = (ln M_U, ln m_free)."""
        def f(x):
            lMU, lm = x
            self.light[free] = math.exp(lm)
            self._cache.clear()
            E = self.at_MU(lMU)
            return [E[0] - E[1], E[2] - E[1]]
        x, info, ier, msg = fsolve(f, np.array(guess, float), full_output=True, xtol=1e-12)
        r = f(x)
        E = self.at_MU(x[0])
        return {"M_U": math.exp(x[0]), "m_free": math.exp(x[1]), "aU": float(E[1]), "res": float(max(map(abs, r))),
                "ok": bool(max(map(abs, r)) < 1e-8 and math.exp(x[1]) < math.exp(x[0]))}

    def mismatch(self, lMU):
        E = self.at_MU(lMU)
        return E

    def asd(self, MU, chir="ec"):
        g1 = 23 / 20 if chir == "ec" else 11 / 20
        _a, I = self.run_to(MU, gam=np.array([g1, 2.25, 2.0]))
        return math.exp(I)


# ----------------------------------------------------------------------------------------------- SO(10) Landau
SO10R = {"16": (16, Fr(2), Fr(45, 8)), "10": (10, Fr(1), Fr(9, 2)), "126": (126, Fr(35), Fr(25, 2)),
         "210": (210, Fr(56), Fr(12)), "45": (45, Fr(8), Fr(8)), "54": (54, Fr(12), Fr(10)),
         "120": (120, Fr(28), Fr(21, 2))}


def so10_b(withPhi, extra=()):
    """B63 + 210 (real) + 126bar + 10 (complex) [+ extra scalars [(rep, 'real'|'cplx')]]; Phi17 pair above M_Phi."""
    CA = Fr(8)
    b1 = Fr(-11, 3) * CA
    b2 = Fr(-34, 3) * CA ** 2
    weyl = [("16", 3), ("16", 6), ("10", 2)] + ([("16", 2)] if withPhi else [])
    for rep, m in weyl:
        d, T, C = SO10R[rep]
        b1 += Fr(2, 3) * T * m
        b2 += m * T * (2 * C + Fr(10, 3) * CA)
    for rep, kind in [("210", "real"), ("126", "cplx"), ("10", "cplx")] + list(extra):
        d, T, C = SO10R[rep]
        w = Fr(1) if kind == "cplx" else Fr(1, 2)
        b1 += Fr(1, 3) * w * T
        b2 += w * T * (4 * C + Fr(2, 3) * CA)
    return b1, b2


def landau_2l(M_U, aU, extra=(), M_phi=1e17, y_s=0.336, yt2=0.30, yuk=True, loops=2):
    b1l, b2l = so10_b(False, extra)
    b1h, b2h = so10_b(True, extra)
    Ylo = (14 * y_s ** 2 + 10 * yt2 + 2 * (126 / 16) * 0.5) if yuk else 0.0
    Yhi = Ylo + (4.0 if yuk else 0.0)
    L2 = 1.0 if loops >= 2 else 0.0

    def mk(b1, b2, Y):
        return lambda t, a: [-float(b1) / (2 * PI) - L2 * float(b2) / (8 * PI ** 2 * a[0]) + L2 * Y / (32 * PI ** 3)]

    def ev(t, a):
        return a[0] - 1.0
    ev.terminal = True
    tU, tP = math.log(M_U), math.log(max(M_phi, M_U))
    s = solve_ivp(mk(b1l, b2l, Ylo), (tU, tP), [aU], method="DOP853", rtol=1e-11, atol=1e-12, events=ev)
    if s.t_events[0].size:
        return math.exp(s.t_events[0][0]) / MPL
    s2 = solve_ivp(mk(b1h, b2h, Yhi), (tP, math.log(1e30)), [s.y[0, -1]], method="DOP853", rtol=1e-11,
                   atol=1e-12, events=ev)
    return math.exp(s2.t_events[0][0]) / MPL if s2.t_events[0].size else float("inf")


def taus(MX, aU, asd_ec, asd_e):
    """tau(p -> e+ pi0) [yr]: repository formula (A_R = 2.726), lattice W0 = 0.131 with A_R = 2.726, and lattice with the
    chain A_R = 1.25 * A_SD (mean of the two chiralities; EST +-25%)."""
    A_ch = 1.25 * 0.5 * (asd_ec + asd_e)
    return {"repo": U.tau_repo(MX, aU), "lattice_AR2.726": U.tau_lattice(MX, aU),
            "lattice_chainAR": U.tau_lattice(MX, aU, A_R=A_ch), "A_R_chain": A_ch}
