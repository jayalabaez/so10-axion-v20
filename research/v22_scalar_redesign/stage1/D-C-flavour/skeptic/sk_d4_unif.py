"""SKEPTIC D4: independent two-loop unification / proton / Landau recomputation for V1 chain b (own code; no designer
or repo unification module imported).

Own Machacek-Vaughn coefficients from SM-rep content (Weyl fermions, complex/real scalars):
  b_i  = -11/3 C2(G_i) + 2/3 sum_F S_i(F) + 1/3 sum_S S_i(S)            (real scalar: x 1/2)
  b_ij = -34/3 C2(G_i)^2 d_ij + sum_F S_i(F) [2 C2_j(F) + 10/3 C2(G_i) d_ij] + sum_S S_i(S) [4 C2_j(S) + 2/3 C2(G_i) d_ij]
  (validated against the SM matrix [[199/50,27/10,44/5],[9/10,35/6,12],[11/10,9/2,-26]]).
  d alpha_i^-1/dt = -b_i/(2pi) - sum_j b_ij alpha_j/(8pi^2) + c_i yt^2/(32 pi^3), c = (17/10, 3/2, 2); yt one loop.
Inputs PDG 2024 (MS-bar at M_Z): alpha^-1 = 127.930, sin^2 = 0.23129, alpha_s = 0.1180; yt(M_Z) = 0.97 (EST).
Matching at M_U (MS-bar heavy vectors, all 33 at M_U): alpha_U^-1 = alpha_i^-1(M_U) + S_V,i/(12 pi), S_V = (8,6,5).
Chain b light content: (6,2,-1/6) complex scalar at 1e9 (fixed), (8,3,0) real scalar at m8 (solved), B63 S-sector
(6 Weyl 16 + 2 Weyl 10) at M_s = 1e13.  Unknowns (ln M_U, ln m8) from alpha_1 = alpha_2 = alpha_3 at M_U.
Proton: A_SD = exp(int sum gamma_i alpha_i/(2pi) dt), gamma = (23/20, 9/4, 2) [e^c] / (11/20, 9/4, 2) [e];
  A_R = 1.25 x mean(A_SD); Gamma = pi m_p (1 - m_pi^2/m_p^2)^2 A_R^2 W0^2 alpha_U^2 (1+|Vud|^2)^2 / M_U^4 (W0 = 0.131 GeV^2,
  the lattice-normalised form; equals the designer's 'tau_lattice') and a x4 more pessimistic variant (rate x4).
Landau: SO(10) two-loop from M_U with b = 16/3, b2 = 20891/6 (+ Phi17 16+16bar pair above 1e17: 8, 21801/6), no Yukawas
  (conservative: Yukawas only delay the pole); Lambda defined at alpha_10 = 1 (designer's definition) and alpha^-1 = 0.
Output: sk_d4_unif.json
"""
from __future__ import annotations
import json, math
from fractions import Fraction as Fr
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

PI = math.pi
MZ, MPL = 91.1876, 2.435e18
AINV, S2W, AS = 127.930, 0.23129, 0.1180
A1I = (3 / 5) * (1 - S2W) * AINV          # GUT-normalised U(1): alpha1 = (5/3) alpha/cos^2
A2I = S2W * AINV
A3I = 1 / AS
CG = [Fr(0), Fr(2), Fr(3)]
C3 = {1: (Fr(0), Fr(0)), 3: (Fr(4, 3), Fr(1, 2)), 6: (Fr(10, 3), Fr(5, 2)), 8: (Fr(3), Fr(3))}   # (C2, T)
C2_ = {1: (Fr(0), Fr(0)), 2: (Fr(3, 4), Fr(1, 2)), 3: (Fr(2), Fr(2))}


def rep_data(Y, d2, d3):
    """(S_i, C2_i) for i = U1(GUT), SU2, SU3 of an SM multiplet (3-dim d3, 2-dim d2, hypercharge Y)."""
    c3, t3 = C3[d3]; c2, t2 = C2_[d2]
    y2 = Fr(3, 5) * Y * Y
    S = [y2 * d2 * d3, t2 * d3, t3 * d2]
    C = [y2, c2, c3]
    return S, C


def mv(fields):
    """fields: list of (kind, Y, d2, d3, mult) with kind in {'weyl','cplx','real'}."""
    b = [Fr(-11, 3) * CG[i] for i in range(3)]
    B = [[Fr(-34, 3) * CG[i] ** 2 if i == j else Fr(0) for j in range(3)] for i in range(3)]
    for kind, Y, d2, d3, m in fields:
        S, C = rep_data(Fr(Y), d2, d3)
        w = Fr(m) * (Fr(1, 2) if kind == "real" else Fr(1))
        for i in range(3):
            if kind == "weyl":
                b[i] += Fr(2, 3) * w * S[i]
                for j in range(3):
                    B[i][j] += w * S[i] * (2 * C[j] + (Fr(10, 3) * CG[i] if i == j else 0))
            else:
                b[i] += Fr(1, 3) * w * S[i]
                for j in range(3):
                    B[i][j] += w * S[i] * (4 * C[j] + (Fr(2, 3) * CG[i] if i == j else 0))
    return b, B


GEN = [("weyl", Fr(1, 6), 2, 3, 1), ("weyl", Fr(-2, 3), 1, 3, 1), ("weyl", Fr(1, 3), 1, 3, 1), ("weyl", Fr(-1, 2), 2, 1, 1),
       ("weyl", Fr(1), 1, 1, 1)]
SM = [(k, Y, d2, d3, 3 * m) for k, Y, d2, d3, m in GEN] + [("cplx", Fr(1, 2), 2, 1, 1)]
SIXTEEN = GEN + [("weyl", Fr(0), 1, 1, 1)]
TEN = [("weyl", Fr(-1, 3), 1, 3, 1), ("weyl", Fr(1, 3), 1, 3, 1), ("weyl", Fr(1, 2), 2, 1, 1), ("weyl", Fr(-1, 2), 2, 1, 1)]
SSECTOR = [(k, Y, d2, d3, 6 * m) for k, Y, d2, d3, m in SIXTEEN] + [(k, Y, d2, d3, 2 * m) for k, Y, d2, d3, m in TEN]
L62 = ("cplx", Fr(-1, 6), 2, 6, 1)
L83 = ("real", Fr(0), 3, 8, 1)

bSM, BSM = mv(SM)
assert [str(x) for x in bSM] == ["41/10", "-19/6", "-7"], bSM
assert BSM == [[Fr(199, 50), Fr(27, 10), Fr(44, 5)], [Fr(9, 10), Fr(35, 6), Fr(12)], [Fr(11, 10), Fr(9, 2), Fr(-26)]], BSM
SV = np.array([8.0, 6.0, 5.0])


class Chain:
    def __init__(self, m6=1e9, m8=3e11, Ms=1e13, loops=2, yt0=0.97, sv=1.0):
        self.m6, self.m8, self.Ms, self.loops, self.yt0, self.sv = m6, m8, Ms, loops, yt0, sv

    def content(self, mu):
        f = list(SM)
        if mu > self.m6: f.append(L62)
        if mu > self.m8: f.append(L83)
        if mu > self.Ms: f += SSECTOR
        return f

    def run(self, MU, gam=None):
        pts = sorted({MZ, MU} | {m for m in (self.m6, self.m8, self.Ms) if MZ < m < MU})
        y = np.array([A1I, A2I, A3I, self.yt0, 0.0])
        for lo, hi in zip(pts[:-1], pts[1:]):
            b, B = mv(self.content(math.sqrt(lo * hi)))
            b = np.array([float(x) for x in b]); B = np.array([[float(x) for x in r] for r in B]) * (1.0 if self.loops >= 2 else 0.0)
            ct = np.array([1.7, 1.5, 2.0]) * (1.0 if self.loops >= 2 else 0.0)
            g = np.zeros(3) if gam is None else np.asarray(gam)

            def rhs(t, z):
                a = 1 / z[:3]; yt = z[3]
                g1s, g2s, g3s = 4 * PI * a
                da = -b / (2 * PI) - B @ a / (8 * PI ** 2) + ct * yt ** 2 / (32 * PI ** 3)
                dyt = yt / (16 * PI ** 2) * (4.5 * yt ** 2 - 17 / 20 * g1s - 9 / 4 * g2s - 8 * g3s)
                return np.concatenate([da, [dyt, float(g @ a) / (2 * PI)]])
            s = solve_ivp(rhs, (math.log(lo), math.log(hi)), y, method="DOP853", rtol=1e-11, atol=1e-13)
            y = s.y[:, -1]
        return y

    def at_MU(self, MU):
        y = self.run(MU)
        return y[:3] + self.sv * SV / (12 * PI)


def solve_b(**kw):
    def f(x):
        ch = Chain(m8=math.exp(x[1]), **kw)
        E = ch.at_MU(math.exp(x[0]))
        return [E[0] - E[1], E[2] - E[1]]
    x = fsolve(f, [math.log(2e16), math.log(3e11)], xtol=1e-13)
    ch = Chain(m8=math.exp(x[1]), **kw); MU = math.exp(x[0]); E = ch.at_MU(MU)
    return ch, MU, float(E[1]), max(map(abs, f(x)))


HBAR, YEAR = 6.582119569e-25, 365.25 * 24 * 3600


def tau_lat(MU, aUinv, AR, W0=0.131, Vud=0.97373, extra_rate=1.0):
    mp, mpi = 0.9382720813, 0.1349768
    gam = PI * mp * (1 - (mpi / mp) ** 2) ** 2 * AR ** 2 * W0 ** 2 * (1 / aUinv) ** 2 * (1 + Vud ** 2) ** 2 / MU ** 4 * extra_rate
    return HBAR / gam / YEAR


def landau(MU, aUinv, M_phi=1e17, stop=1.0, loops=2):
    b1, b2 = 16 / 3, 20891 / 6
    bh1, bh2 = 8.0, 20891 / 6 + 2 * 2 * (2 * 45 / 8 + 10 / 3 * 8)
    L2 = 1.0 if loops >= 2 else 0.0

    def mk(b, bb):
        return lambda t, a: [-b / (2 * PI) - L2 * bb / (8 * PI ** 2 * a[0])]

    def ev(t, a):
        return a[0] - stop
    ev.terminal = True
    t0, t1 = math.log(MU), math.log(max(M_phi, MU))
    s = solve_ivp(mk(b1, b2), (t0, t1), [aUinv], events=ev, rtol=1e-11, atol=1e-12, method="DOP853", max_step=0.01)
    if s.t_events[0].size:
        return math.exp(s.t_events[0][0]) / MPL
    s2 = solve_ivp(mk(bh1, bh2), (t1, math.log(1e30)), [s.y[0, -1]], events=ev, rtol=1e-11, atol=1e-12, method="DOP853", max_step=0.01)
    return math.exp(s2.t_events[0][0]) / MPL if s2.t_events[0].size else float("inf")


out = {"inputs": {"alpha^-1": AINV, "sin2": S2W, "alpha_s": AS, "yt(MZ)": 0.97}, "runs": {}}
for label, kw in {"nominal 2L": {}, "1L": {"loops": 1}, "no S_V": {"sv": 0.0}, "S_V opposite": {"sv": -1.0},
                  "M_s=3.9e12": {"Ms": 3.9e12}, "M_s=1.21e13": {"Ms": 1.21e13}, "yt=0.94": {"yt0": 0.94}}.items():
    ch, MU, aU, res = solve_b(**kw)
    yec = ch.run(MU, gam=[23 / 20, 9 / 4, 2.0])[4]; ye = ch.run(MU, gam=[11 / 20, 9 / 4, 2.0])[4]
    AR = 1.25 * 0.5 * (math.exp(yec) + math.exp(ye))
    t1 = tau_lat(MU, aU, AR); t4 = tau_lat(MU, aU, AR, extra_rate=4.0)
    lam1 = landau(MU, aU, stop=1.0); lam0 = landau(MU, aU, stop=1e-6)
    rec = {"M_U": MU, "m(8,3,0)": ch.m8, "aU^-1": aU, "residual": res, "A_R_chain": AR, "tau_lattice_yr": t1,
           "tau_lattice_x4rate_yr": t4, "tau/SK(2.4e34)": t1 / 2.4e34, "Lambda_2L(alpha=1)/MPl": lam1, "Lambda_2L(alpha^-1=0)/MPl": lam0}
    out["runs"][label] = rec
    print(f"{label:14s} M_U = {MU:.3e}  m8 = {ch.m8:.3e}  aU^-1 = {aU:.3f}  A_R = {AR:.3f}  tau = {t1:.3e} (x4 rate: {t4:.3e})  "
          f"Lambda(alpha=1) = {lam1:.3f} MPl  Lambda(1/alpha=0) = {lam0:.3f} MPl  res {res:.1e}", flush=True)
# designer nominal point re-evaluated: M_U = 2.16e16, aU^-1 = 25.71
out["designer_point_check"] = {"tau_lattice(AR=3.23)": tau_lat(2.16e16, 25.71, 3.23), "Lambda(alpha=1)": landau(2.16e16, 25.71)}
print("designer point:", out["designer_point_check"])
json.dump(out, open(Path(__file__).with_name("sk_d4_unif.json"), "w"), indent=1)
