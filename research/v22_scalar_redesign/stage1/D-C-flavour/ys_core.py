"""[v22 D-C-flavour copy of R2-V ys_rg.py: one-step (no G3221) segment option added]
R2-V item (5): own one-loop RG for the S-sector Yukawas of v21-F17-B63 and the y_s window at M_s = 1e13.

S couples to 62 Dirac-equivalent components: three vectorlike 16-pairs (V1'-Vb1, V2-Vb2, V3-Vb3; 16 each),
the 2 x 10_F Majorana pair T (= one Dirac 10), three singlet Dirac pairs N1-N1b, N2-N2b, N3-N3b and the Majorana
pair NMm (= one Dirac singlet).  One loop (complex S, chiral Yukawas y S psi chi, Machacek-Vaughn):
  16 pi^2 dy_c/dt = y_c [ gamma_S + y_c^2 - 6 sum_G g_G^2 C_G(c) (- 3 g_X^2 (X_psi^2 + X_chi^2) above <Phi17>) ]
  gamma_S = sum_c d_c y_c^2 ,   16 pi^2 dlam/dt = 20 lam^2 + 4 lam gamma_S - 2 sum_c d_c y_c^4  (V = lam |S|^4)
Components are resolved (SM below v_R, G3221 between v_R and M_U, SO(10) above M_U); at v_R and M_U the
components of one multiplet are matched by their dimension-weighted RMS ('rms') or by their maximum ('max').
Universal y_c(M_s) = y_s for all 62 components (the round-1 configuration), or singlets scaled by r_N.
Gauge environment = the round-1 one (inputs, not re-derived: SM one loop from PDG M_Z values, complete exotic
multiplets above M_s, G3221 with the round-1 'T2+F17' b's run down from alpha_U^-1 = 25.9 at M_U = 2.13e16,
SO(10) above M_U with b1 = 8 and the MV two-loop b2 = 7267/2 (recomputed here), U(1)_X above 1e17 with
alpha_X(M_Pl,red) = 1 (maximal) or switched off).
"""
from __future__ import annotations

import json
import math
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
PI = math.pi
L16 = 16 * PI ** 2
MZ, MS, VR, MU, VPHI, MPL = 91.1876, 1.0e13, 2.6e13, 2.13e16, 1.0e17, 2.435e18
AINV_MZ = np.array([59.02, 29.58, 8.47])
B_SM = np.array([41 / 10, -19 / 6, -7.0])
DB_EXOTIC = 28 / 3
B_G3221 = np.array([65 / 6, 12.0, 47 / 3, 49 / 3])  # (SU3, SU2L, SU2R, BL) round-1 environment
AINV_U = 25.9
BX = 101203.0


def so10_b():
    CG = Fr(8)
    reps = {"10": (Fr(1), Fr(9, 2)), "16": (Fr(2), Fr(45, 8)), "126": (Fr(35), Fr(25, 2)), "210": (Fr(56), Fr(12))}
    b1 = Fr(-11, 3) * CG
    b2 = Fr(-34, 3) * CG ** 2
    for name, mult in (("16", 11), ("10", 2)):
        T, C = reps[name]
        b1 += Fr(2, 3) * T * mult
        b2 += (Fr(10, 3) * CG + 2 * C) * T * mult
    for name, eta, w in (("210", Fr(1, 6), Fr(1, 2)), ("126", Fr(1, 3), Fr(1)), ("10", Fr(1, 3), Fr(1))):
        T, C = reps[name]
        b1 += eta * T
        b2 += (Fr(2, 3) * CG + 4 * C) * T * w
    return b1, b2


B1_10, B2_10 = so10_b()
_SO10 = solve_ivp(lambda t, y: [-float(B1_10) / (2 * PI) - float(B2_10) / (8 * PI ** 2) / y[0]],
                  [math.log(MU), math.log(MPL) + 0.05], [AINV_U], rtol=1e-10, atol=1e-12, dense_output=True)


def g2_env(mu, gx_on):
    """returns dict of g^2 by phase."""
    t = math.log(mu)
    if mu < VR:
        a = AINV_MZ - B_SM / (2 * PI) * math.log(mu / MZ) - (DB_EXOTIC / (2 * PI) * math.log(mu / MS) if mu > MS else 0.0)
        return "SM", (4 * PI / a)[::-1]  # reorder to (g3^2, g2^2, g1^2) to match the Casimir vectors
    if mu < MU:
        a = AINV_U - B_G3221 / (2 * PI) * math.log(mu / MU)
        return "G3221", 4 * PI / a
    a10 = float(_SO10.sol(t)[0])
    gx2 = 0.0
    if gx_on and mu > VPHI:
        gx2 = 4 * PI / (1.0 + BX / (2 * PI) * math.log(MPL / mu))
    return "SO10", np.array([4 * PI / a10, gx2])


# component tables: (name, multiplicity d, Casimir vector per phase)
#  SM Casimirs: (C_SU3, C_SU2, 3/5 Y^2) ; G3221: (C3, C2L, C2R, 3/8 (B-L)^2) ; SO(10): C2
SM_P = [("Q", 6, (4 / 3, 3 / 4, 0.6 / 36)), ("u", 3, (4 / 3, 0, 0.6 * 4 / 9)), ("d", 3, (4 / 3, 0, 0.6 / 9)),
        ("L", 2, (0, 3 / 4, 0.6 / 4)), ("e", 1, (0, 0, 0.6)), ("n", 1, (0, 0, 0))]
SM_T = [("D", 6, (4 / 3, 0, 0.6 / 9)), ("Hd", 4, (0, 3 / 4, 0.6 / 4))]
LR_P = [("321", 6, (4 / 3, 3 / 4, 0, 3 / 8 / 9)), ("312", 6, (4 / 3, 0, 3 / 4, 3 / 8 / 9)),
        ("121", 2, (0, 3 / 4, 0, 3 / 8)), ("112", 2, (0, 0, 3 / 4, 3 / 8))]
LR_T = [("D", 6, (4 / 3, 0, 0, 3 / 8 * 4 / 9)), ("bd", 4, (0, 3 / 4, 3 / 4, 0))]
SM_TO_LR_P = {"321": ["Q"], "312": ["u", "d"], "121": ["L"], "112": ["e", "n"]}
SM_TO_LR_T = {"D": ["D"], "bd": ["Hd"]}
X2_N = [63 ** 2 + 59 ** 2, 58 ** 2 + 54 ** 2, 57 ** 2 + 61 ** 2, 2 * 2 ** 2]  # X^2 sums of the singlet pairs
X2_P = [35 ** 2 + 39 ** 2, 28 ** 2 + 32 ** 2, 34 ** 2 + 30 ** 2]
X2_T = 2 * 2 ** 2


def run(y_s, r_N=1.0, gauge=True, gx_on=False, match="rms", lam0=None, mu_end=MPL):
    """returns (max over components and scales of y, final values, min/max lambda) ; singlet couplings each tracked."""
    state = {}
    # SM phase: P sector three copies (identical in gauge, distinct X: X only matters above VPHI)
    yP = {c: y_s for c, _d, _C in SM_P}
    yT = {c: y_s for c, _d, _C in SM_T}
    yN = [y_s * r_N] * 4
    lam = 0.0 if lam0 is None else lam0
    track = {"ymax": y_s, "lam_min": lam, "lam_max": lam, "who": None}

    def integrate(phase, t0, t1, names_P, names_T, cas_P, cas_T, vec0):
        dP = [d for _c, d, _C in names_P]
        dT = [d for _c, d, _C in names_T]
        nP, nT = len(dP), len(dT)

        def rhs(t, v):
            mu = math.exp(t)
            ph, g2 = g2_env(mu, gx_on)
            P = v[:nP]
            Tt = v[nP:nP + nT]
            N = v[nP + nT:nP + nT + 4]
            l = v[-1]
            gam = 3 * sum(d * y * y for d, y in zip(dP, P)) + sum(d * y * y for d, y in zip(dT, Tt)) + sum(y * y for y in N)
            y4 = 3 * sum(d * y ** 4 for d, y in zip(dP, P)) + sum(d * y ** 4 for d, y in zip(dT, Tt)) + sum(y ** 4 for y in N)
            out = []
            for i in range(nP):
                gt = 6 * float(np.dot(g2[:len(cas_P[i])] if ph != "SO10" else [g2[0]], cas_P[i])) if gauge else 0.0
                out.append(P[i] * (gam + P[i] ** 2 - gt) / L16)
            for i in range(nT):
                gt = 6 * float(np.dot(g2[:len(cas_T[i])] if ph != "SO10" else [g2[0]], cas_T[i])) if gauge else 0.0
                out.append(Tt[i] * (gam + Tt[i] ** 2 - gt) / L16)
            for i in range(4):
                gx = 3 * g2[1] * X2_N[i] if (ph == "SO10" and gauge) else 0.0
                out.append(N[i] * (gam + N[i] ** 2 - gx) / L16)
            out.append((20 * l * l + 4 * l * gam - 2 * y4) / L16)
            return out

        def blow(t, v):
            return max(abs(x) for x in v[:-1]) - 12.0
        blow.terminal = True
        sol = solve_ivp(rhs, [t0, t1], vec0, rtol=1e-8, atol=1e-11, max_step=0.05, events=blow)
        return sol

    segs = [("SM", MS, VR), ("G3221", VR, MU), ("SO10", MU, mu_end)]
    if VR >= MU:      # v22 one-step environment: no G3221 segment, SM components matched directly to SO(10)
        segs = [("SM", MS, MU), ("SO10", MU, mu_end)]
    for ph, a, b in segs:
        if ph == "SM":
            names_P, names_T = SM_P, SM_T
            v0 = [yP[c] for c, _d, _C in SM_P] + [yT[c] for c, _d, _C in SM_T] + yN + [lam]
        elif ph == "G3221":
            names_P, names_T = LR_P, LR_T
            dsm = {c: d for c, d, _C in SM_P}
            dsmT = {c: d for c, d, _C in SM_T}
            def comb(vals, ds, keys):
                if match == "rms":
                    return math.sqrt(sum(ds[k] * vals[k] ** 2 for k in keys) / sum(ds[k] for k in keys))
                return max(vals[k] for k in keys)
            v0 = [comb(yP, dsm, SM_TO_LR_P[c]) for c, _d, _C in LR_P] + [comb(yT, dsmT, SM_TO_LR_T[c]) for c, _d, _C in LR_T] + yN + [lam]
        else:
            names_P = [("16", 16, (45 / 8,))]
            names_T = [("10", 10, (9 / 2,))]
            dl = {c: d for c, d, _C in LR_P}
            dlT = {c: d for c, d, _C in LR_T}
            if "Q" in yP:   # v22: coming directly from the SM phase
                dl = {c: d for c, d, _C in SM_P}
                dlT = {c: d for c, d, _C in SM_T}
            if match == "rms":
                p = math.sqrt(sum(dl[c] * yP[c] ** 2 for c in dl) / 16)
                tt = math.sqrt(sum(dlT[c] * yT[c] ** 2 for c in dlT) / 10)
            else:
                p, tt = max(yP.values()), max(yT.values())
            v0 = [p, tt] + yN + [lam]
        cas_P = [C for _c, _d, C in names_P]
        cas_T = [C for _c, _d, C in names_T]
        sol = integrate(ph, math.log(a), math.log(b), names_P, names_T, cas_P, cas_T, v0)
        nP, nT = len(names_P), len(names_T)
        Y = sol.y
        m = float(np.max(np.abs(Y[:-1])))
        if m > track["ymax"]:
            track["ymax"] = m
            idx = int(np.unravel_index(np.argmax(np.abs(Y[:-1])), Y[:-1].shape)[0])
            labs = ["P:" + c for c, _d, _C in names_P] + ["T:" + c for c, _d, _C in names_T] + ["N1", "N2", "N3", "NMm"]
            track["who"] = labs[idx]
        track["lam_min"] = min(track["lam_min"], float(np.min(Y[-1])))
        track["lam_max"] = max(track["lam_max"], float(np.max(Y[-1])))
        if len(sol.t_events[0]):
            track["blowup_at"] = math.exp(sol.t_events[0][0])
            return track
        end = Y[:, -1]
        yP = {c: end[i] for i, (c, _d, _C) in enumerate(names_P)}
        yT = {c: end[nP + i] for i, (c, _d, _C) in enumerate(names_T)}
        yN = list(end[nP + nT:nP + nT + 4])
        lam = end[-1]
    track["final"] = {"P": {k: float(v) for k, v in yP.items()}, "T": {k: float(v) for k, v in yT.items()},
                      "N": [float(v) for v in yN], "lam": float(lam)}
    return track


def cap(limit=math.sqrt(4 * PI), **kw):
    lo, hi = 0.05, 1.5
    for _ in range(45):
        mid = 0.5 * (lo + hi)
        tr = run(mid, **kw)
        ok = ("blowup_at" not in tr) and tr["ymax"] <= limit
        if ok:
            lo = mid
        else:
            hi = mid
    tr = run(lo, **kw)
    return lo, tr.get("who")


def lam_window(y_s, **kw):
    """lambda_S(M_s) = 2 lam window: lam stays > 0 and < 4 pi up to M_Pl (all couplings as in run)."""
    def ok_pos(l0):
        tr = run(y_s, lam0=l0, **kw)
        return "blowup_at" not in tr and tr["lam_min"] > 0
    def ok_pert(l0):
        tr = run(y_s, lam0=l0, **kw)
        return "blowup_at" not in tr and tr["lam_max"] < 4 * PI
    lo, hi = 0.0, 2.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if ok_pos(mid):
            hi = mid
        else:
            lo = mid
    lmin = hi
    lo, hi = lmin, 6.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if ok_pert(mid):
            lo = mid
        else:
            hi = mid
    return 2 * lmin, 2 * lo


def main():
    out = {"so10_b1": str(B1_10), "so10_b2": str(B2_10), "alpha10_inv_MPl_2loop": float(_SO10.sol(math.log(MPL))[0])}
    # analytic no-gauge universal cap: 1/y^2(M_s) = 1/(4pi) + 2*63/(16pi^2) ln(MPl/M_s)
    out["no_gauge_universal_analytic"] = 1 / math.sqrt(1 / (4 * PI) + 2 * 63 / L16 * math.log(MPL / MS))
    cases = {
        "no_gauge (all 62 universal)": dict(gauge=False),
        "gauge, singlets ungauged (g_X off), rms matching": dict(gauge=True, gx_on=False, match="rms"),
        "gauge, singlets ungauged (g_X off), max matching": dict(gauge=True, gx_on=False, match="max"),
        "gauge + U(1)_X with alpha_X(MPl)=1 (maximal), rms": dict(gauge=True, gx_on=True, match="rms"),
        "gauge, g_X off, singlet Yukawas = 0.5 y_s": dict(gauge=True, gx_on=False, r_N=0.5),
        "gauge, g_X off, singlet Yukawas = 0.25 y_s": dict(gauge=True, gx_on=False, r_N=0.25),
    }
    out["caps_M_s=1e13"] = {}
    for k, kw in cases.items():
        c, who = cap(**kw)
        out["caps_M_s=1e13"][k] = {"y_s_cap(y<=sqrt(4pi) to MPl)": c, "binding_coupling": who}
        print("%-55s cap %.4f (binding %s)" % (k, c, who), flush=True)
    for y in (0.304, 0.33, 0.35):
        lw = lam_window(y, gauge=True, gx_on=False)
        out.setdefault("lambda_S_window", {})["y_s=%.3f gauge, g_X off" % y] = lw
        print("lambda_S window at y_s=%.3f: [%.3f, %.3f]" % (y, lw[0], lw[1]), flush=True)
    (HERE / "ys_rg.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "caps_M_s=1e13"}, indent=1))


if __name__ == "__main__":
    pass  # v22: library use only (ys_window_1s.py)
