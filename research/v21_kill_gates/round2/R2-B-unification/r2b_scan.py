#!/usr/bin/env python3
"""R2-B scans.  Usage: r2b_scan.py MODE [contents...]
MODE grid   : M_s x y_s(B63 window) x S_V sign at 1/2/3 loops; Landau for M_Phi in {M_U, 3e16, 1e17, 1.25e17}
MODE mc     : threshold Monte Carlo (light x1/3..x3 per SM piece incl. W_R; GUT x1/2..x2 per G3221 multiplet) and
              coherent extremes, M_s = 1e13 (and 3e12 combined), y_s = 0.336, Phi pair at 1e17, S_V = MS-bar
MODE planck : Planck kinetic coefficient c in [-1, 1] (step 0.1), s = +-1 (Am45 Clebsches), 2L and 3L
"""
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2b_model as M

SK, HK = 2.4e34, 7.8e34
MODE = sys.argv[1]
CONTS = sys.argv[2:] or ["C0", "C1", "C2", "C1p"]
X_OPTS = (None, 1.0)


def ys_window(M_s):
    """B63 window: y_s >= M_s / <S>_max (<S>_max = 3.29e13, quality) and y_s <= RG cap (K0b: 0.346 at 3e12, 0.368 at
    1e13; log-linear in between, 0.368 above)."""
    lo = M_s / 3.29e13
    if M_s <= 3e12:
        hi = 0.346
    elif M_s >= 1e13:
        hi = 0.368
    else:
        f = math.log(M_s / 3e12) / math.log(1e13 / 3e12)
        hi = 0.346 + f * (0.368 - 0.346)
    return lo, hi


def solve_point(p, landau_cfg=((2, None),), mphis=(1e17,)):
    ch = M.Chain(p)
    r = ch.solve()
    if r.get("ok"):
        M.set_yt(ch, r["v_R"])
        r2 = ch.solve(guesses=[(math.log(r["v_R"]), math.log(r["M_U"]), r["a2R_inv_vR"])])
        if r2.get("ok"):
            r = r2
    row = {k: r.get(k) for k in ("ok", "v_R", "M_U", "alpha_U_inv", "resid_max")}
    if not r.get("ok"):
        return row, ch
    row["tau_p"] = M.proton_lifetime_years(r["M_U"], r["alpha_U_inv"])
    for mphi in mphis:
        p.M_phi = mphi
        for L, xo in landau_cfg:
            if xo is not None and len(mphis) > 1 and mphi != 1e17:
                continue  # U(1)_X shooting only at the nominal Phi-pair mass (speed)
            p.alpha_x_inv_mpl = xo
            lm = ch.landau(r["M_U"], r["alpha_U_inv"], loops=L)
            tag = f"L{L}" + ("" if xo is None else f"x{xo:g}") + ("" if len(mphis) == 1 else f"@{mphi:.3g}")
            row[tag] = lm["Lambda_over_MPl"]
            row[tag + "_a10MPl"] = lm["alpha_inv_MPl"]
        p.alpha_x_inv_mpl = None
    return row, ch


def summarise(rows, keyL="L2"):
    ok = [r for r in rows if r.get("ok")]
    n = len(rows)
    if not ok:
        return {"n": n, "n_ok": 0}

    def stats(vals):
        vals = sorted(vals)
        q = lambda f: vals[min(len(vals) - 1, int(f * (len(vals) - 1) + 0.5))]
        return [vals[0], q(0.05), q(0.5), q(0.95), vals[-1]]
    out = {"n": n, "n_ok": len(ok)}
    for k in ("v_R", "M_U", "alpha_U_inv", "tau_p", "L2", "L3"):
        vals = [r[k] for r in ok if r.get(k) is not None]
        if vals:
            out[k + "_min_p05_med_p95_max"] = stats(vals)
    out["frac_tau_gt_SK"] = sum(1 for r in ok if r["tau_p"] > SK) / n
    out["frac_tau_gt_HK"] = sum(1 for r in ok if r["tau_p"] > HK) / n
    out["frac_L2_gt_1"] = sum(1 for r in ok if (r.get("L2") or 0) > 1) / n
    out["frac_L3_gt_1"] = sum(1 for r in ok if (r.get("L3") or 0) > 1) / n
    out["frac_pass2L(tau>SK & L2>1)"] = sum(1 for r in ok if r["tau_p"] > SK and (r.get("L2") or 0) > 1) / n
    out["frac_vR_1e11_1e14"] = sum(1 for r in ok if 1e11 <= r["v_R"] <= 1e14) / n
    out["frac_all(tau>SK & L2>1 & vR in [1e11,1e14])"] = sum(
        1 for r in ok if r["tau_p"] > SK and (r.get("L2") or 0) > 1 and 1e11 <= r["v_R"] <= 1e14) / n
    return out


out = {"mode": MODE, "contents": CONTS}
t0 = time.time()
logf = open(os.path.join(HERE, f"r2b_scan_{MODE}_{'_'.join(CONTS)}.log"), "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n")
    logf.flush()


if MODE == "grid":
    for cont in CONTS:
        res = {}
        for M_s in (3e12, 5e12, 7e12, 8.2e12, 1e13, 1.21e13):
            lo, hi = ys_window(M_s)
            for ys in sorted({round(lo, 4), round(hi, 4)}):
                for sv in (+1, 0, -1):
                    for loops in (1, 2, 3):
                        p = M.Params(light=M.CONTENTS[cont], M_s=M_s, y_s=ys, sv_sign=sv, loops=loops)
                        if loops == 1:
                            row, _ = solve_point(p, landau_cfg=(), mphis=(1e17,))
                        else:
                            row, _ = solve_point(p, landau_cfg=((loops, None), (loops, 1.0)),
                                                 mphis=(1.0, 3e16, 1e17, 1.25e17))  # 1.0 = Phi pair at M_U
                        key = f"Ms{M_s:.3g}|ys{ys}|sv{sv:+d}|{loops}L"
                        res[key] = row
                        if sv == 1 or loops == 2:
                            log(cont, key, {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in row.items()})
        out[cont] = res
elif MODE == "mc":
    rng = random.Random(20261016)
    N = int(os.environ.get("R2B_MC_N", "200"))
    for cont in CONTS:
        light = M.CONTENTS[cont]
        res = {}
        base = M.Params(light=light)
        ch0 = M.Chain(base)
        lnames = [x[0] for x in ch0.light_thr]
        hnames = [x[0] for x in ch0.heavy]
        for scen in ("light", "gut", "both", "both_Ms3e12", "gut_half"):
            rows = []
            nsc = N if scen in ("both",) else max(N // 2, 60)
            for i in range(nsc):
                lr = {n: math.exp(rng.uniform(math.log(1 / 3), math.log(3))) for n in lnames} if scen in ("light", "both", "both_Ms3e12") else {}
                if scen in ("gut", "both", "both_Ms3e12"):
                    gr = {n: math.exp(rng.uniform(math.log(0.5), math.log(2.0))) for n in hnames}
                elif scen == "gut_half":
                    gr = {n: math.exp(rng.uniform(math.log(0.5), math.log(1.0))) for n in hnames}
                else:
                    gr = {}
                M_s = 3e12 if scen == "both_Ms3e12" else 1e13
                ys = 0.2 if scen == "both_Ms3e12" else 0.336
                p = M.Params(light=light, light_ratios=lr, gut_ratios=gr, M_s=M_s, y_s=ys, loops=3)
                row, _ = solve_point(p, landau_cfg=((2, None), (3, None)), mphis=(1e17,))
                rows.append(row)
            res[scen] = {"summary": summarise(rows), "rows": rows}
            log(cont, scen, json.dumps(res[scen]["summary"], default=str))
        # coherent extremes (all GUT scalars x f_g, all light states x f_l)
        coh = {}
        for fg in (0.5, 1.0, 2.0):
            for fl in (1 / 3, 1.0, 3.0):
                p = M.Params(light=light, light_ratios={"*": fl}, gut_ratios={"*": fg}, loops=3)
                row, _ = solve_point(p, landau_cfg=((2, None), (3, None)), mphis=(1e17,))
                coh[f"GUTx{fg:g}_lightx{fl:.3g}"] = row
                log(cont, "coherent", fg, round(fl, 3), {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in row.items()})
        res["coherent"] = coh
        # light thresholds at v_R only but with 3L unification also (sm3L) for nominal
        out[cont] = res
elif MODE == "planck":
    for cont in CONTS:
        res = {}
        for s in (+1, -1):
            for loops in (2, 3):
                prev = None
                for ci in list(range(0, 11)) + list(range(-1, -11, -1)):
                    c = ci / 10.0
                    if ci == -1:
                        prev = res.get(f"s{s:+d}|{loops}L|c0.0")
                    p = M.Params(light=M.CONTENTS[cont], planck_c=c, planck_s=s, loops=loops)
                    ch = M.Chain(p)
                    gs = None
                    if prev and prev.get("ok"):
                        gs = [(math.log(prev["v_R"]), math.log(prev["M_U"]), prev["a2R_inv_vR"])]
                    r = ch.solve(guesses=gs) if gs else ch.solve()
                    if not r.get("ok") and gs:
                        r = ch.solve()
                    row = {k: r.get(k) for k in ("ok", "v_R", "M_U", "alpha_U_inv", "a2R_inv_vR", "eps")}
                    if r.get("ok"):
                        M.set_yt(ch, r["v_R"])
                        row["tau_p"] = M.proton_lifetime_years(r["M_U"], r["alpha_U_inv"])
                        lm = ch.landau(r["M_U"], r["alpha_U_inv"], loops=loops)
                        row[f"L{loops}"] = lm["Lambda_over_MPl"]
                        prev = row
                    key = f"s{s:+d}|{loops}L|c{c:.1f}"
                    res[key] = row
                    log(cont, key, {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in row.items() if k != "eps"})
        out[cont] = res
out["seconds"] = time.time() - t0
with open(os.path.join(HERE, f"r2b_scan_{MODE}_{'_'.join(CONTS)}.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=str)
log("done", out["seconds"])
