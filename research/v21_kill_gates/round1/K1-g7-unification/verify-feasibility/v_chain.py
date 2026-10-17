#!/usr/bin/env python3
"""Independent re-derivation (verifier): one- and two-loop MV chain SM -> G3221 -> SO(10) for v21-F17-G3221,
own field tables and own MV routine (no import of the researcher's k1_lib/k1_model).  Three-loop SO(10) uses the
researcher's b3 numbers as INPUT only to test the Landau-scale integration (b3 itself is checked separately).
Also: K3-compatible light contents (one and two loops) to test the cross-gate conflict.
"""
import json, math, sys
from fractions import Fraction as F
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

PI = math.pi
MPL = 2.435e18
MZ = 91.1876
A1, A2, A3 = 59.02, 29.57, 1.0 / 0.1179

# rep data: (dim, T, C2)
SU2 = {1: (1, F(0), F(0)), 2: (2, F(1, 2), F(3, 4)), 3: (3, F(2), F(2))}
SU3 = {1: (1, F(0), F(0)), 3: (3, F(1, 2), F(4, 3)), 6: (6, F(5, 2), F(10, 3)), 8: (8, F(3), F(3))}


def u1(q2):
    q2 = F(q2)
    return (1, q2, q2)


def ysm(y):  # GUT-normalised hypercharge
    return u1(F(3, 5) * F(y) ** 2)


def bl(q):  # GUT-normalised B-L
    return u1(F(3, 8) * F(q) ** 2)


def mv(cg, fields):
    """fields: list of (kind, reps, mult); kind weyl/cplx/real.  Returns (b, bij) Fractions."""
    n = len(cg)
    b = [F(-11, 3) * c for c in cg]
    bij = [[(F(-34, 3) * c * c if i == j else F(0)) for j in range(n)] for i, c in enumerate(cg)]
    for kind, reps, mult in fields:
        for i in range(n):
            s = reps[i][1] * F(mult)
            for k in range(n):
                if k != i:
                    s *= reps[k][0]
            if s == 0:
                continue
            if kind == "weyl":
                b[i] += F(2, 3) * s
                for j in range(n):
                    bij[i][j] += 2 * s * reps[j][2]
                bij[i][i] += F(10, 3) * cg[i] * s
            elif kind == "cplx":
                b[i] += F(1, 3) * s
                for j in range(n):
                    bij[i][j] += 4 * s * reps[j][2]
                bij[i][i] += F(2, 3) * cg[i] * s
            elif kind == "real":
                b[i] += F(1, 6) * s
                for j in range(n):
                    bij[i][j] += 2 * s * reps[j][2]
                bij[i][i] += F(1, 3) * cg[i] * s
    return b, bij


# ---------------- SM phase (U1_Y, SU2, SU3)
CG_SM = (F(0), F(2), F(3))


def sm_gen():
    return [("weyl", (ysm(F(1, 6)), SU2[2], SU3[3]), 1), ("weyl", (ysm(F(-2, 3)), SU2[1], SU3[3]), 1),
            ("weyl", (ysm(F(1, 3)), SU2[1], SU3[3]), 1), ("weyl", (ysm(F(-1, 2)), SU2[2], SU3[1]), 1),
            ("weyl", (ysm(F(1)), SU2[1], SU3[1]), 1), ("weyl", (ysm(F(0)), SU2[1], SU3[1]), 1)]


def ten_sm():
    return [("weyl", (ysm(F(-1, 3)), SU2[1], SU3[3]), 1), ("weyl", (ysm(F(1, 3)), SU2[1], SU3[3]), 1),
            ("weyl", (ysm(F(1, 2)), SU2[2], SU3[1]), 1), ("weyl", (ysm(F(-1, 2)), SU2[2], SU3[1]), 1)]


def sm_fields(n16, n10, nH=1):
    f = [(k, r, m * (3 + n16)) for k, r, m in sm_gen()]
    f += [(k, r, m * n10) for k, r, m in ten_sm()]
    f.append(("cplx", (ysm(F(1, 2)), SU2[2], SU3[1]), nH))
    return f


# ---------------- G3221 phase (SU3, SU2L, SU2R, BL)
CG_G = (F(3), F(2), F(2), F(0))


def g(su3, l, r, q):
    return (SU3[su3], SU2[l], SU2[r], bl(q))


def g16():
    return [("weyl", g(3, 2, 1, F(1, 3)), 1), ("weyl", g(3, 1, 2, F(-1, 3)), 1),
            ("weyl", g(1, 2, 1, F(-1)), 1), ("weyl", g(1, 1, 2, F(1)), 1)]


def g10():
    return [("weyl", g(3, 1, 1, F(-2, 3)), 1), ("weyl", g(3, 1, 1, F(2, 3)), 1), ("weyl", g(1, 2, 2, 0), 1)]


LIGHT = {
    "bid": ("cplx", g(1, 2, 2, 0), 1),
    "DR": ("cplx", g(1, 1, 3, 2), 1),
    "822": ("cplx", g(8, 2, 2, 0), 1),
    "831": ("real", g(8, 3, 1, 0), 1),
    "131": ("real", g(8 if False else 1, 3, 1, 0), 1),
    "811": ("real", g(8, 1, 1, 0), 1),
    "bid2": ("cplx", g(1, 2, 2, 0), 1),
    "DR_full_6": ("cplx", g(6, 1, 3, F(-2, 3)), 1),
    "DR_full_3": ("cplx", g(3, 1, 3, F(2, 3)), 1),
}
CONTENTS = {
    "T2": ["bid", "DR", "822", "831", "131"],
    "T3": ["bid", "DR", "822", "831", "131", "bid2", "811"],
    "K3a_bid_DR": ["bid", "DR"],
    "K3b_bid_DR_831": ["bid", "DR", "831"],
    "K3c_bid_DR_131": ["bid", "DR", "131"],
    "T2_minus_822": ["bid", "DR", "831", "131"],
    "T2_fullPS_DR": ["bid", "DR", "DR_full_6", "DR_full_3", "822", "831", "131"],
}


def g_fields(content, with_s):
    n16 = 3 + (6 if with_s else 0)
    f = [(k, r, m * n16) for k, r, m in g16()]
    if with_s:
        f += [(k, r, m * 2) for k, r, m in g10()]
    f += [LIGHT[x] for x in CONTENTS[content]]
    return f


# SM-language light thresholds at v_R for threshold-free nominal run: none (all at v_R).

# ---------------- SO(10) phase: (b1, b2) from own MV single-group, b3 from the researcher (input only)
SO10 = {"16": (16, F(2), F(45, 8)), "10": (10, F(1), F(9, 2)), "210": (210, F(56), F(12)), "126": (126, F(35), F(25, 2))}


def so10_b12(with_phi):
    fields = [("weyl", (SO10["16"],), 9 + (2 if with_phi else 0)), ("weyl", (SO10["10"],), 2),
              ("real", (SO10["210"],), 1), ("cplx", (SO10["126"],), 1), ("cplx", (SO10["10"],), 1)]
    b, bij = mv((F(8),), fields)
    return b[0], bij[0][0]


B3_LO = F(142437589, 864)
B3_HI = F(5041501, 32)


class Seg:
    def __init__(self, b, bij, b3=None, loops=2, Y=None):
        self.b = np.array([float(x) for x in b])
        self.bij = np.array([[float(x) for x in r] for r in bij])
        self.b3 = np.zeros(len(b)) if b3 is None else np.array([float(x) for x in b3])
        self.loops = loops
        self.Y = np.zeros(len(b)) if Y is None else np.array(Y, dtype=float)

    def rhs(self, t, y):
        d = -self.b / (2 * PI)
        if self.loops >= 2:
            a = 1.0 / y
            d = d - self.bij.dot(a) / (8 * PI**2) + self.Y / (32 * PI**3)
        if self.loops >= 3:
            d = d - self.b3 * (1.0 / y) ** 2 / (32 * PI**3)
        return d


def run(seg, y0, t0, t1, landau=False):
    if abs(t1 - t0) < 1e-14:
        return np.array(y0, float), t0, False
    ev = None
    if landau:
        def ev(t, y):
            return float(np.min(y) - 1.0)
        ev.terminal = True
        ev.direction = -1
    sol = solve_ivp(seg.rhs, (t0, t1), np.array(y0, float), method="DOP853", rtol=1e-10, atol=1e-12, events=ev, max_step=0.5)
    if landau and sol.t_events[0].size:
        return sol.y_events[0][0], float(sol.t_events[0][0]), True
    return sol.y[:, -1], float(sol.t[-1]), False


def chain(content, loops, M_s=1e13, y_s=0.345, Y126=0.5, yuk=True):
    """Returns the solver for (ln vR, ln MU, a2R_inv) at the given loop order (<=2 in product phases)."""
    lo = min(loops, 2)
    bsm0, bijsm0 = mv(CG_SM, sm_fields(0, 0))
    bsm1, bijsm1 = mv(CG_SM, sm_fields(6, 2))
    bg, bijg = mv(CG_G, g_fields(content, True))
    bgn, bijgn = mv(CG_G, g_fields(content, False))
    yt2 = 0.95**2 if yuk else 0.0   # crude, frozen (EST; effect on roots is tiny)
    Ysm0 = np.array([1.7, 1.5, 2.0]) * yt2 * 0.6   # y_t falls to ~0.7 by 1e13: use 0.6*0.9 ~ 0.54 average
    Ysm1 = Ysm0 + (14.0 * y_s**2 if yuk else 0.0)
    Yg = np.array([4, 4, 4, 4]) * yt2 * 0.3 + (14.0 * y_s**2 if yuk else 0.0)
    s0 = Seg(bsm0, bijsm0, loops=lo, Y=Ysm0)
    s1 = Seg(bsm1, bijsm1, loops=lo, Y=Ysm1)
    sg = Seg(bg, bijg, loops=lo, Y=Yg)
    sgn = Seg(bgn, bijgn, loops=lo, Y=Yg - (14.0 * y_s**2 if yuk else 0.0))
    t0, ts = math.log(MZ), math.log(M_s)

    def to_MU(x):
        tv, tu, a2r = x
        a = np.array([A1, A2, A3])
        if ts < tv:
            a, _, _ = run(s0, a, t0, ts)
            a, _, _ = run(s1, a, ts, tv)
        else:
            a, _, _ = run(s0, a, t0, tv)
        a1, a2, a3 = a
        abl = 2.5 * (a1 - 0.6 * a2r)
        gg = np.array([a3, a2, a2r, abl])
        if ts < tv:
            gg, _, _ = run(sg, gg, tv, tu)
        else:
            gg, _, _ = run(sgn, gg, tv, min(ts, tu))
            if ts < tu:
                gg, _, _ = run(sg, gg, ts, tu)
        return gg

    def resid(x):
        try:
            gg = to_MU(x)
            return np.array([gg[0] - gg[1], gg[2] - gg[1], gg[3] - gg[1]])
        except Exception:
            return np.array([1e3, 1e3, 1e3])

    best = None
    for guess in ([math.log(2.5e13), math.log(2.5e16), 46.0], [math.log(1e11), math.log(1e16), 40.0],
                  [math.log(1e13), math.log(5e16), 44.0], [math.log(1e10), math.log(3e15), 38.0]):
        x, info, ier, msg = fsolve(resid, np.array(guess), full_output=True, xtol=1e-12)
        r = resid(x)
        if ier == 1 and np.max(np.abs(r)) < 1e-7:
            best = x
            break
    if best is None:
        return {"ok": False, "content": content, "loops": loops}
    gg = to_MU(best)
    return {"ok": True, "content": content, "loops": loops, "v_R": math.exp(best[0]), "M_U": math.exp(best[1]),
            "alpha_U_inv": float(gg[1]), "a2R_inv_vR": float(best[2]), "b_G3221": [str(x) for x in bg],
            "bij_G3221": [[str(x) for x in r] for r in bijg]}


def landau(M_U, aU, loops, M_phi=1e17, y_s=0.345, Y126=0.5, yt2=0.2, yuk=True, b3fac=1.0):
    b1lo, b2lo = so10_b12(False)
    b1hi, b2hi = so10_b12(True)
    Ylo = (14 * y_s**2 + 10 * yt2 + 15.75 * Y126) if yuk else 0.0
    Yhi = Ylo + (4 * (M_phi / 1e17) ** 2 if yuk else 0.0)
    slo = Seg([b1lo], [[b2lo]], b3=[B3_LO * b3fac], loops=loops, Y=[Ylo])
    shi = Seg([b1hi], [[b2hi]], b3=[B3_HI * b3fac], loops=loops, Y=[Yhi])
    tu, tp = math.log(M_U), math.log(max(M_phi, M_U))
    y, t, hit = run(slo, [aU], tu, tp, landau=True)
    if not hit:
        y, t, hit = run(shi, y, tp, math.log(1e24), landau=True)
    lam = math.exp(t) if hit else float("inf")
    # loop-term ratios at M_U
    a = 1.0 / aU
    one = float(b1lo) / (2 * PI)
    two = float(b2lo) * a / (8 * PI**2) - Ylo / (32 * PI**3)
    three = float(B3_LO) * a * a / (32 * PI**3)
    return {"Lambda": lam, "Lambda_over_MPl": lam / MPL, "b_lo": [str(b1lo), str(b2lo)], "b_hi": [str(b1hi), str(b2hi)],
            "ratio_2L_over_1L_at_MU": two / one, "ratio_3L_over_2L_at_MU": three / two, "loops": loops}


if __name__ == "__main__":
    out = {}
    # 0. coefficient tables
    for c in CONTENTS:
        b, bij = mv(CG_G, g_fields(c, True))
        out[f"b_G3221_{c}_withS"] = [str(x) for x in b]
    out["b_SM"] = [str(x) for x in mv(CG_SM, sm_fields(0, 0))[0]]
    out["b_SM_S"] = [str(x) for x in mv(CG_SM, sm_fields(6, 2))[0]]
    out["bij_SM"] = [[str(x) for x in r] for r in mv(CG_SM, sm_fields(0, 0))[1]]
    out["so10_b12_lo"] = [str(x) for x in so10_b12(False)]
    out["so10_b12_hi"] = [str(x) for x in so10_b12(True)]
    print(json.dumps({k: v for k, v in out.items()}, indent=1))
    # 1. one-loop and two-loop roots for all contents
    roots = {}
    for c in CONTENTS:
        for L in (1, 2):
            r = chain(c, L)
            roots[f"{c}_L{L}"] = r
            print(f"{c:16s} {L}L: ", {k: (f"{v:.4e}" if isinstance(v, float) else v) for k, v in r.items() if k in ("ok", "v_R", "M_U", "alpha_U_inv")})
    out["roots"] = roots
    # 2. Landau scales at the T2/T3 two-loop roots
    lands = {}
    for c in ("T2", "T3"):
        r = roots[f"{c}_L2"]
        if not r["ok"]:
            continue
        for L in (2, 3):
            for mphi in (1e17, 1.25e17):
                ld = landau(r["M_U"], r["alpha_U_inv"], L, M_phi=mphi)
                lands[f"{c}_L{L}_Mphi{mphi:.3g}"] = ld
                print(f"{c} {L}L Mphi={mphi:.3g}: Lambda/MPl = {ld['Lambda_over_MPl']:.4f}  2L/1L(MU)={ld['ratio_2L_over_1L_at_MU']:.3f} 3L/2L(MU)={ld['ratio_3L_over_2L_at_MU']:.3f}")
        # gauge-only (Yukawa off) check against the critic table / researcher's first run
        ld = landau(r["M_U"], r["alpha_U_inv"], 3, M_phi=1e17, yuk=False)
        lands[f"{c}_L3_noYuk"] = ld
        print(f"{c} 3L no-Yukawa: Lambda/MPl = {ld['Lambda_over_MPl']:.4f}")
    # 3. M_s crossing at three loops (T2): y_s = M_s/2.9e13
    cross = {}
    for M_s in (7e12, 8e12, 9e12, 9.5e12, 1e13, 1.08e13):
        r = chain("T2", 2, M_s=M_s, y_s=M_s / 2.9e13)
        ld = landau(r["M_U"], r["alpha_U_inv"], 3, M_phi=1e17, y_s=M_s / 2.9e13)
        ld2 = landau(r["M_U"], r["alpha_U_inv"], 2, M_phi=1e17, y_s=M_s / 2.9e13)
        cross[f"{M_s:.3g}"] = {"v_R": r["v_R"], "M_U": r["M_U"], "aU": r["alpha_U_inv"], "L3": ld["Lambda_over_MPl"], "L2": ld2["Lambda_over_MPl"]}
        print(f"T2 M_s={M_s:.3g}: v_R={r['v_R']:.3e} M_U={r['M_U']:.3e} aU={r['alpha_U_inv']:.3f} L2/MPl={ld2['Lambda_over_MPl']:.3f} L3/MPl={ld['Lambda_over_MPl']:.3f}")
    out["landau"] = lands
    out["crossing_T2"] = cross
    # 4. K3-compatible contents: Landau at their two-loop roots
    for c in ("K3a_bid_DR", "K3b_bid_DR_831", "K3c_bid_DR_131", "T2_minus_822", "T2_fullPS_DR"):
        r = roots[f"{c}_L2"]
        if r["ok"]:
            ld2 = landau(r["M_U"], r["alpha_U_inv"], 2)
            ld3 = landau(r["M_U"], r["alpha_U_inv"], 3)
            out["landau"][f"{c}_L2"] = ld2
            out["landau"][f"{c}_L3"] = ld3
            print(f"{c}: 2L root v_R={r['v_R']:.3e} M_U={r['M_U']:.3e} aU={r['alpha_U_inv']:.3f}; Lambda2/MPl={ld2['Lambda_over_MPl']:.3f} Lambda3/MPl={ld3['Lambda_over_MPl']:.3f}")
    with open(sys.argv[1] if len(sys.argv) > 1 else "v_chain.json", "w") as fh:
        json.dump(out, fh, indent=1, default=str)
