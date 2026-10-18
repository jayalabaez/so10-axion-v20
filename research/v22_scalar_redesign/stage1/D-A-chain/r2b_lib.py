#!/usr/bin/env python3
"""K1 (decisive G7) for v21-F17-G3221: own RG library, written from scratch.

Conventions
-----------
t = ln(mu/GeV).  For every gauge factor i

    d alpha_i^-1/dt = -b_i/(2 pi) - sum_j b_ij alpha_j/(8 pi^2) + Y_i/(32 pi^3) - b3_i alpha_i^2/(32 pi^3)

equivalently dg_i/dt = g_i^3/(16 pi^2) [ b_i + sum_j b_ij g_j^2/(16 pi^2) - Y_i/(16 pi^2) + b3_i g_i^4/(16 pi^2)^2 ].

b_i, b_ij: Machacek-Vaughn (NPB 222 (1983) 83) with Weyl fermions (kappa = 1/2), complex scalars (eta = 1) and real
scalars (eta = 1/2):
    b_i  = -11/3 C2(G_i) + 2/3 sum_Weyl S_i + 1/3 sum_cplx S_i + 1/6 sum_real S_i
    b_ij = -34/3 C2(G_i)^2 d_ij + sum_Weyl S_i [2 C2_j + 10/3 C2(G_i) d_ij] + sum_cplx S_i [4 C2_j + 2/3 C2(G_i) d_ij]
           + sum_real S_i [2 C2_j + 1/3 C2(G_i) d_ij]
with S_i(R) = T_i(R) prod_{k != i} dim_k(R); U(1) factors GUT-normalised (T = C2 = q^2 with q the normalised charge).
Y_i = (1/d(G_i)) sum_{A, j, k} C2_i(j) |Y_{A,jk}|^2 (Machacek-Vaughn Y_4(F)/d(G)), L = -(1/2) Y_{A,jk} psi_j psi_k Phi_A + h.c.
b3_i: three-loop gauge + matter term of the single-group Pickering-Gracey-Jones formula (hep-ph/0104247 eqs. (28)-(33)),
used only for the SO(10) phase (single simple group); for the product-group phases the three-loop term is estimated
(see k1_run.py).

One-loop MS-bar threshold matching at a scale mu with heavy states k of mass M_k (Weinberg 1980, Hall 1981):
    alpha_i^-1(mu)_low = alpha_i^-1(mu)_high - (1/2 pi) sum_k b_i^k ln(M_k/mu),
    b^k = 2/3 S_i (Weyl), 1/3 S_i (complex scalar), 1/6 S_i (real scalar), -7/2 S_i (massive vector + its Goldstone;
    = -21/6 S_i, the usual "-21").
"""
from __future__ import annotations

import math
from fractions import Fraction as F
from typing import Any, Callable, Sequence

import numpy as np
from scipy.integrate import solve_ivp

PI = math.pi
M_PL_RED = 2.435e18
MZ = 91.1876
A1_MZ, A2_MZ, A3_MZ = 59.02, 29.57, 1.0 / 0.1179  # repo inputs (two_loop_thresholds_v20): alpha_1^-1 GUT-normalised, alpha_2^-1, alpha_3^-1
Y_T_MZ = 0.95  # MS-bar top Yukawa near M_t ~ 0.94 (PDG m_t(m_t) = 163 GeV, v = 246): used only in the two-loop Yukawa terms

# ---------------------------------------------------------------------------------------------------------------
# Representation data (dim, T, C2).  T(fund SU(N)) = 1/2.  U(1): (1, q^2, q^2) with q the GUT-normalised charge.
# ---------------------------------------------------------------------------------------------------------------
SU2 = {"1": (1, F(0), F(0)), "2": (2, F(1, 2), F(3, 4)), "3": (3, F(2), F(2))}
SU3 = {"1": (1, F(0), F(0)), "3": (3, F(1, 2), F(4, 3)), "3b": (3, F(1, 2), F(4, 3)),
       "6": (6, F(5, 2), F(10, 3)), "6b": (6, F(5, 2), F(10, 3)), "8": (8, F(3), F(3))}
# SO(10) with T(10) = 1 (so that T(16) = 2, C2(45) = C_G = 8): Weyl-dimension-formula values (repo-consistent).
SO10 = {"1": (1, F(0), F(0)), "10": (10, F(1), F(9, 2)), "16": (16, F(2), F(45, 8)), "16b": (16, F(2), F(45, 8)),
        "45": (45, F(8), F(8)), "54": (54, F(12), F(10)), "120": (120, F(28), F(21, 2)),
        "126": (126, F(35), F(25, 2)), "126b": (126, F(35), F(25, 2)), "210": (210, F(56), F(12))}
C_G_SO10 = F(8)


def so10_rep_data_from_weyl_formula() -> dict[str, tuple[int, F, F]]:
    """Independent re-derivation of the SO(10) table: Weyl dimension formula and C2 = (L, L + 2 rho), C2(10) = 9/2."""
    rho = (4, 3, 2, 1, 0)
    h = F(1, 2)
    hw = {"10": (1, 0, 0, 0, 0), "16": (h, h, h, h, h), "16b": (h, h, h, h, -h), "45": (1, 1, 0, 0, 0),
          "54": (2, 0, 0, 0, 0), "120": (1, 1, 1, 0, 0), "126": (1, 1, 1, 1, 1), "126b": (1, 1, 1, 1, -1),
          "210": (1, 1, 1, 1, 0)}
    roots = []
    for i in range(5):
        for j in range(i + 1, 5):
            for s in (1, -1):
                r = [0] * 5
                r[i], r[j] = 1, s
                roots.append(r)
    raw = {}
    for name, w in hw.items():
        lam = [F(x) for x in w]
        num = den = F(1)
        for r in roots:
            num *= sum((lam[k] + rho[k]) * r[k] for k in range(5))
            den *= sum(rho[k] * r[k] for k in range(5))
        dim = num / den
        assert dim.denominator == 1
        raw[name] = (int(dim), sum(lam[k] * (lam[k] + 2 * rho[k]) for k in range(5)))
    norm = F(9, 2) / raw["10"][1]
    out = {"1": (1, F(0), F(0))}
    for name, (dim, c2raw) in raw.items():
        c2 = c2raw * norm
        out[name] = (dim, c2 * dim / 45, c2)
    return out


def u1(q: F) -> tuple[int, F, F]:
    q = F(q)
    return (1, q * q, q * q)


def ysm(y: F) -> tuple[int, F, F]:
    """U(1)_Y GUT-normalised: q = sqrt(3/5) Y -> T = C2 = 3/5 Y^2."""
    return u1_sq(F(3, 5) * F(y) ** 2)


def bl(q: F) -> tuple[int, F, F]:
    """U(1)_{B-L} GUT-normalised: q = sqrt(3/8) (B-L) -> T = C2 = 3/8 (B-L)^2."""
    return u1_sq(F(3, 8) * F(q) ** 2)


def u1_sq(q2: F) -> tuple[int, F, F]:
    return (1, F(q2), F(q2))


# ---------------------------------------------------------------------------------------------------------------
# Field tables.  A field = (name, kind, reps, multiplicity); kind in {weyl, cplx, real, vector}.
# ---------------------------------------------------------------------------------------------------------------
Field = tuple[str, str, tuple, Any]


def s_factor(reps: Sequence[tuple], i: int) -> F:
    """S_i(R) = T_i(R) prod_{k != i} dim_k(R)."""
    s = F(reps[i][1])
    for k, r in enumerate(reps):
        if k != i:
            s *= r[0]
    return s


def mv_coefficients(group_c2: Sequence[F], fields: Sequence[Field]) -> tuple[list[F], list[list[F]]]:
    """Exact Machacek-Vaughn (b_i, b_ij) for a product group with Weyl / complex / real fields."""
    n = len(group_c2)
    b = [F(-11, 3) * F(c) for c in group_c2]
    bij = [[(F(-34, 3) * F(c) * F(c) if i == j else F(0)) for j in range(n)] for i, c in enumerate(group_c2)]
    for name, kind, reps, mult in fields:
        m = F(mult)
        if kind == "vector":
            raise ValueError("vectors are part of the gauge term, not the field table")
        for i in range(n):
            s = s_factor(reps, i) * m
            if s == 0:
                continue
            if kind == "weyl":
                b[i] += F(2, 3) * s
                for j in range(n):
                    bij[i][j] += 2 * s * reps[j][2]
                bij[i][i] += F(10, 3) * group_c2[i] * s
            elif kind == "cplx":
                b[i] += F(1, 3) * s
                for j in range(n):
                    bij[i][j] += 4 * s * reps[j][2]
                bij[i][i] += F(2, 3) * group_c2[i] * s
            elif kind == "real":
                b[i] += F(1, 6) * s
                for j in range(n):
                    bij[i][j] += 2 * s * reps[j][2]
                bij[i][i] += F(1, 3) * group_c2[i] * s
            else:
                raise ValueError(kind)
    return b, bij


def threshold_b(kind: str, reps: Sequence[tuple], i: int, mult: Any = 1) -> F:
    """b_i^k of one heavy state for the one-loop matching (vector: -7/2 S, incl. its Goldstone)."""
    s = s_factor(reps, i) * F(mult)
    return {"weyl": F(2, 3), "cplx": F(1, 3), "real": F(1, 6), "vector": F(-7, 2)}[kind] * s


# ---------------------------------------------------------------------------------------------------------------
# Pickering-Gracey-Jones three-loop (gauge + matter), single simple group.
# beta_g = -g [a1 + 2 b1 + 3 c1] (loop order), (16 pi^2)^n factors absorbed; b3 = -3 c1 in dg/dt = ... + b3 g^7/(16pi^2)^3.
# T(R), T(S): sums of indices over two-component fermions and REAL scalars; CR2 = sum T C2, CR3 = sum T C2^2 etc.
# ---------------------------------------------------------------------------------------------------------------
PGJ = {
    "a1.CG": F(11, 3), "a1.TR": F(-2, 3), "a1.TS": F(-1, 6),
    "b1.CG^2": F(17, 3), "b1.CG*TR": F(-5, 3), "b1.CG*TS": F(-1, 6), "b1.CS2": F(-1), "b1.CR2": F(-1),
    "c1.CG^3": F(2857, 162), "c1.CG^2*TR": F(-1415, 162), "c1.CG*TR^2": F(79, 162), "c1.CG^2*TS": F(-545, 648),
    "c1.CG*TR*TS": F(29, 162), "c1.CG*TS^2": F(-1, 324), "c1.CG*CS2": F(-1129, 216), "c1.TR*CS2": F(25, 54),
    "c1.TS*CS2": F(49, 216), "c1.CG*CR2": F(-205, 54), "c1.TR*CR2": F(11, 27), "c1.TS*CR2": F(23, 108),
    "c1.CR3": F(1, 3), "c1.CS3": F(-29, 12),
}


def pgj_invariants(content: Sequence[tuple[str, str, Any]], reps: dict, cg: F) -> dict[str, F]:
    inv = {"CG": F(cg), "TR": F(0), "TS": F(0), "CR2": F(0), "CS2": F(0), "CR3": F(0), "CS3": F(0)}
    for rep, kind, mult in content:
        d, t, c = reps[rep]
        m = F(mult)
        if kind == "weyl":
            inv["TR"] += m * t
            inv["CR2"] += m * t * c
            inv["CR3"] += m * t * c * c
        elif kind in ("real", "cplx"):
            nreal = m * (2 if kind == "cplx" else 1)
            inv["TS"] += nreal * t
            inv["CS2"] += nreal * t * c
            inv["CS3"] += nreal * t * c * c
        else:
            raise ValueError(kind)
    return inv


def pgj_b(inv: dict) -> tuple[Any, Any, Any]:
    sums = {"a1": 0, "b1": 0, "c1": 0}
    for key, coef in PGJ.items():
        order, expr = key.split(".", 1)
        val = coef
        for tok in expr.split("*"):
            if "^" in tok:
                nm, p = tok.split("^")
                val = val * inv[nm] ** int(p)
            else:
                val = val * inv[tok]
        sums[order] = sums[order] + val
    return (-sums["a1"], -2 * sums["b1"], -3 * sums["c1"])


# ---------------------------------------------------------------------------------------------------------------
# Numerical running of a segment: state = alpha_i^-1 (numpy), optional Yukawa term and three-loop term.
# ---------------------------------------------------------------------------------------------------------------
class Segment:
    def __init__(self, b, bij, b3=None, yuk: Callable[[float, np.ndarray], np.ndarray] | None = None, loops: int = 2,
                 label: str = ""):
        self.b = np.array([float(x) for x in b])
        self.bij = np.array([[float(x) for x in r] for r in bij])
        self.n = len(self.b)
        self.b3 = np.zeros(self.n) if b3 is None else np.array([float(x) for x in b3])
        self.yuk = yuk
        self.loops = loops
        self.label = label

    def rhs(self, t: float, ainv: np.ndarray) -> np.ndarray:
        d = -self.b / (2.0 * PI)
        if self.loops >= 2:
            a = 1.0 / ainv
            d = d - self.bij.dot(a) / (8.0 * PI**2)
            if self.yuk is not None:
                d = d + self.yuk(t, ainv) / (32.0 * PI**3)
        if self.loops >= 3:
            d = d - self.b3 * (1.0 / ainv) ** 2 / (32.0 * PI**3)
        return d


def run_segment(seg: Segment, ainv0: np.ndarray, t0: float, t1: float, rtol: float = 1e-10,
                landau_event: bool = False, alpha_stop: float = 1.0, event_index=None) -> tuple[np.ndarray, float, bool]:
    """Integrate from t0 to t1.  Returns (ainv(t_end), t_end, hit) where hit=True if alpha_i reached alpha_stop."""
    if abs(t1 - t0) < 1e-15:
        return np.array(ainv0, dtype=float), t0, False
    events = None
    if landau_event:
        def ev(t, y):
            if event_index is not None:
                return float(y[event_index] - 1.0 / alpha_stop)
            return float(np.min(y) - 1.0 / alpha_stop)
        ev.terminal = True
        ev.direction = -1
        events = ev
    sol = solve_ivp(seg.rhs, (t0, t1), np.array(ainv0, dtype=float), method="DOP853", rtol=rtol, atol=1e-12,
                    events=events, max_step=0.5)
    if not sol.success:
        raise RuntimeError(sol.message)
    if landau_event and sol.t_events[0].size > 0:
        return sol.y_events[0][0], float(sol.t_events[0][0]), True
    return sol.y[:, -1], float(sol.t[-1]), False


def rk4_run(seg: Segment, ainv0: np.ndarray, t0: float, t1: float, h: float = 0.01) -> np.ndarray:
    """Independent fixed-step RK4 integrator (cross-check of DOP853)."""
    n = max(1, int(math.ceil(abs(t1 - t0) / h)))
    hh = (t1 - t0) / n
    y = np.array(ainv0, dtype=float)
    t = t0
    for _ in range(n):
        k1 = seg.rhs(t, y)
        k2 = seg.rhs(t + hh / 2, y + hh / 2 * k1)
        k3 = seg.rhs(t + hh / 2, y + hh / 2 * k2)
        k4 = seg.rhs(t + hh, y + hh * k3)
        y = y + hh / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += hh
    return y


# ---------------------------------------------------------------------------------------------------------------
# Simple one-loop top-Yukawa running (for the two-loop gauge-Yukawa terms only; EST-level accuracy is enough).
# ---------------------------------------------------------------------------------------------------------------
def yt_run_sm(yt0: float, ainv0: np.ndarray, t0: float, t1: float, seg: Segment, steps: int = 200) -> float:
    """SM one-loop: dy/dt = y/(16pi^2) [9/2 y^2 - 8 g3^2 - 9/4 g2^2 - 17/20 g1^2], gauge couplings from seg at one loop."""
    y = yt0
    a = np.array(ainv0, dtype=float)
    h = (t1 - t0) / steps
    t = t0
    for _ in range(steps):
        g2 = 4.0 * PI / a  # g_i^2
        dy = y / (16 * PI**2) * (4.5 * y * y - 8 * g2[2] - 2.25 * g2[1] - 0.85 * g2[0])
        y += h * dy
        a = a + h * seg.rhs(t, a)
        t += h
    return y
