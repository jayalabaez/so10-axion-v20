"""D4 for the D-C-flavour designs (one-step SO(10) -> SM chains; V1 = A1-EFT): nominal two-loop solutions, threshold
Monte Carlo over the heavy GUT spectrum, proton lifetime (lattice W0 x chain A_R normalisation for kills), two-loop
(and, for information, three-loop-free) SO(10) Landau scale, plus the 120_H Landau check for variant V3.

Heavy spectrum: complete SM decomposition of 210 (real) + 126bar + 10 (complex) from the R2-B skeptic table
(unif_core.SCAL, G3221 Goldstones already removed) minus the extra one-step Goldstones (W_R^+-: one (1,1,1) complex;
Z': one real (1,1,0)), minus the SM Higgs doublet and the light states of the chain.  Each heavy SM multiplet gets a
log-uniform mass ratio in [1/2, 2] x M_U ('GUT x1/2..x2', as R2-B), the non-mediator vectors (3,1,2/3), (1,1,1) too;
the p-decay mediators (3,2,-5/6), (3,2,1/6) define M_U.  Light-state masses are kept (one of them is re-solved).
usage: python -B d4_unif.py <out.json> [nmc]
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as Fr

import numpy as np

import unif_core as U
import unif1s as Q

PI = math.pi
SK = 2.4e34


def heavy_list(light_names):
    """SM pieces (name, kind, reps) of all heavy scalars for the one-step chain."""
    out = []
    removed = {"higgs": False, "WR": False}
    want_light = dict(light_names)       # {piece-name: count to remove}
    for name in U.SCAL:
        for pname, kind, reps in U.sm_pieces(name):
            if name == "126(1,1,3)DR" and pname.endswith("|Y=1") and not removed["WR"]:
                removed["WR"] = True          # W_R^+- Goldstone
                continue
            if name == "10(1,2,2)" and pname.endswith("|Y=1/2") and not removed["higgs"]:
                removed["higgs"] = True       # SM Higgs (any doublet combination; gauge-equivalent)
                continue
            if want_light.get(pname, 0) > 0:
                want_light[pname] -= 1
                continue
            out.append((pname, kind, reps))
    assert all(v == 0 for v in want_light.values()), want_light
    return out


VEC_OTHER = [("V(3,1,2/3)", U.sm(Fr(2, 3), "1", "3")), ("V(1,1,1)", U.sm(1, "1", "1"))]


def thr_shift(heavy, ratios, vec_ratios):
    d = np.zeros(3)
    for (pname, kind, reps), r in zip(heavy, ratios):
        d += np.array([float(x) for x in U.thr_b(kind, reps, 1)]) * math.log(r) / (2 * PI)
    for (vname, reps), r in zip(VEC_OTHER, vec_ratios):
        d += np.array([float(x) for x in U.thr_b("vec", reps, 2)]) * math.log(r) / (2 * PI)
    return d


CHAINS = {
    "a": {"light": {"(8,1,0)210": 1.0e4, "(8,3,0)210": 2.25e9}, "free": "(8,3,0)210",
          "pieces": {"210(8,1,1)|Y=0": 1, "210(8,3,1)|Y=0": 1}, "guess": (math.log(1e16), math.log(2.25e9))},
    "b": {"light": {"(6,2,-1/6)210": 1.0e9, "(8,3,0)210": 2.95e11}, "free": "(8,3,0)210",
          "pieces": {"210(6,2,2)|Y=-1/6": 1, "210(8,3,1)|Y=0": 1}, "guess": (math.log(2.2e16), math.log(3e11))},
}


def evaluate(ch, model, s, extra_so10=()):
    a1, a2 = model.asd(s["M_U"], "ec"), model.asd(s["M_U"], "e")
    t = Q.taus(s["M_U"], s["aU"], a1, a2)
    L2 = Q.landau_2l(s["M_U"], s["aU"], extra=extra_so10)
    return {"M_U": s["M_U"], "m_free": s["m_free"], "aU": s["aU"], "tau_repo": t["repo"], "tau_lat": t["lattice_AR2.726"],
            "tau_lat_chainAR": t["lattice_chainAR"], "A_R_chain": t["A_R_chain"], "Lambda2L_over_MPl": L2,
            "pass_tau": t["lattice_chainAR"] > SK, "pass_L2": L2 > 1.0}


def main():
    out_path = sys.argv[1]
    nmc = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    res = {"S_V_check": Q.check_sv(), "chains": {}}
    for ch, C in CHAINS.items():
        heavy = heavy_list(C["pieces"])
        nominal = {}
        for label, kw in {"MSbar_SV": dict(sv=1.0), "SV_off": dict(sv=0.0), "SV_opposite": dict(sv=-1.0),
                          "Ms=3e12": dict(M_s=3e12), "Ms=1.21e13,ys=0.368": dict(M_s=1.21e13, y_s=0.368),
                          "one_loop": dict(loops=1)}.items():
            m = Q.OneStep(dict(C["light"]), **kw)
            s = m.solve(C["free"], C["guess"])
            nominal[label] = evaluate(ch, m, s) if s["ok"] else {"failed": s}
            print(ch, label, {k: (f"{v:.3e}" if isinstance(v, float) else v) for k, v in nominal[label].items()}, flush=True)
        # light-mass family (fixed second light state scanned)
        fam = []
        other = [k for k in C["light"] if k != C["free"]][0]
        for mo in np.logspace(3, 13, 21):
            light = dict(C["light"]); light[other] = float(mo)
            m = Q.OneStep(light)
            s = m.solve(C["free"], C["guess"])
            if s["ok"]:
                e = evaluate(ch, m, s); e[other] = float(mo); fam.append(e)
        # threshold Monte Carlo
        rng = np.random.default_rng(2026)
        mc = []
        for _ in range(nmc):
            rat = np.exp(rng.uniform(math.log(0.5), math.log(2.0), len(heavy)))
            vr = np.exp(rng.uniform(math.log(0.5), math.log(2.0), len(VEC_OTHER)))
            m = Q.OneStep(dict(C["light"]), heavy_shift=thr_shift(heavy, rat, vr))
            s = m.solve(C["free"], C["guess"])
            if not s["ok"]:
                mc.append(None); continue
            mc.append(evaluate(ch, m, s))
        good = [x for x in mc if x is not None]
        taus = np.array([x["tau_lat_chainAR"] for x in good]); L2s = np.array([x["Lambda2L_over_MPl"] for x in good])
        frac = float(np.mean((taus > SK) & (L2s > 1.0))) if good else 0.0
        res["chains"][ch] = {"light": C["light"], "n_heavy_scalar_multiplets": len(heavy), "nominal": nominal, "family": fam,
                             "mc": {"n": nmc, "n_ok": len(good), "frac_pass_tau_and_L2": frac,
                                    "frac_pass_tau": float(np.mean(taus > SK)) if good else 0.0,
                                    "tau_lat_chainAR_min_med_max": [float(taus.min()), float(np.median(taus)), float(taus.max())] if good else None,
                                    "L2_min_med_max": [float(L2s.min()), float(np.median(L2s)), float(L2s.max())] if good else None,
                                    "MU_min_max": [float(min(x["M_U"] for x in good)), float(max(x["M_U"] for x in good))] if good else None,
                                    "m_free_min_max": [float(min(x["m_free"] for x in good)), float(max(x["m_free"] for x in good))] if good else None}}
        print(ch, "MC:", res["chains"][ch]["mc"], flush=True)
    # V3: + 120_H (complex, X = -2) in the SO(10) phase, same chains (120's light content: none)
    res["V3_120H_Landau"] = {}
    for ch, C in CHAINS.items():
        m = Q.OneStep(dict(C["light"]))
        s = m.solve(C["free"], C["guess"])
        res["V3_120H_Landau"][ch] = {"Lambda2L_over_MPl_with_120H": Q.landau_2l(s["M_U"], s["aU"], extra=[("120", "cplx")]),
                                     "Lambda2L_over_MPl_without": Q.landau_2l(s["M_U"], s["aU"]),
                                     "aU": s["aU"], "M_U": s["M_U"],
                                     "b_SO10_with_120H": [str(x) for x in Q.so10_b(False, [("120", "cplx")])],
                                     "b_SO10_base": [str(x) for x in Q.so10_b(False)]}
        print(ch, "V3 120_H:", res["V3_120H_Landau"][ch], flush=True)
    # V2-type SO(10) content (+45_H real) Landau at the same alpha_U (information only)
    res["V2_45H_Landau_info"] = {ch: Q.landau_2l(res["chains"][ch]["nominal"]["MSbar_SV"]["M_U"],
                                                 res["chains"][ch]["nominal"]["MSbar_SV"]["aU"], extra=[("45", "real")])
                                 for ch in CHAINS}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)


if __name__ == "__main__":
    main()
