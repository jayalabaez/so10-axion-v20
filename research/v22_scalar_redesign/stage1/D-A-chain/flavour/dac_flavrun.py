#!/usr/bin/env python3
"""Staged multi-start driver for flavour_proxy (screen -> polish -> basin hops).  NUM: the result is an upper bound on
chi2_min of the stated structure (local optimiser).
usage: python -B flavour_run.py <content> <floor> <mode ren|d5> <minutes> [gmax] [Rmin]"""
import sys, json, math, time
import numpy as np
from scipy.optimize import least_squares
import flavour_proxy as P

content, floor, mode, minutes = sys.argv[1], float(sys.argv[2]), sys.argv[3], float(sys.argv[4])
gmax = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
Rmin = float(sys.argv[6]) if len(sys.argv) > 6 else None
tg, info = P.gut_targets(content, floor=floor)
rng = np.random.default_rng(7)
T0 = time.time(); TL = minutes * 60
lb = np.full(P.NP_D5 if mode == "d5" else P.NP_REN, -np.inf); ub = -lb
if Rmin is not None:
    lb[18] = math.log(Rmin)


def solve(x0, nfev):
    x0 = np.clip(x0, lb + 1e-9, ub)
    # 'lm' needs n_residuals >= n_params (19 < 28 for d5): use trf throughout
    kw = dict(bounds=(lb, ub)) if Rmin is not None else {}
    r = least_squares(P.residuals, x0, args=(mode, tg, gmax), method="trf", max_nfev=nfev, x_scale="jac", **kw)
    return float(np.sum(r.fun ** 2)), r.x


screen = []
while time.time() - T0 < 0.45 * TL:
    x0 = P.start(rng, mode, tg)
    if Rmin is not None:
        x0[18] = max(x0[18], math.log(Rmin) + abs(rng.normal(0, 1)))
    try:
        screen.append(solve(x0, 700))
    except Exception as ex:
        nerr = globals().get("nerr", 0) + 1; globals()["nerr"] = nerr
        if nerr < 5: print("solve error (skipped):", repr(ex)[:120], flush=True)
screen.sort(key=lambda t: t[0])
print(f"[{content} {mode} f={floor}] screened {len(screen)} starts; best 8: {[round(c, 1) for c, _ in screen[:8]]}", flush=True)
pol = []
for c0, x in screen[:8]:
    if time.time() - T0 > 0.7 * TL:
        break
    try:
        pol.append(solve(x, 6000))
    except Exception:
        pass
pol.sort(key=lambda t: t[0])
best = pol[0] if pol else screen[0]
print(f"   polished: {[round(c, 2) for c, _ in pol]}", flush=True)
# basin hops around the best
nh = 0
while time.time() - T0 < TL:
    x = best[1] + rng.normal(0, 1, len(best[1])) * np.where(np.arange(len(best[1])) < 6, 0.0, 0.15)
    try:
        c, xn = solve(x, 3000)
    except Exception:
        continue
    nh += 1
    if c < best[0]:
        best = (c, xn); print(f"   hop {nh}: chi2 -> {c:.3f}", flush=True)
rep = P.report(best[1], mode, tg, gmax)
print(f"[{content} {mode} floor={floor} gmax={gmax} Rmin={Rmin}] chi2_min = {rep['chi2']:.3f} (penalty {rep['penalty']:.2e}); "
      f"pulls>2: { {k: round(v, 2) for k, v in rep['pulls'].items() if abs(v) > 2} }; ms/md = {rep['ms_md_model_MU']:.2f}; "
      f"G_max = {rep['G_max_GeV']:.3g} GeV; c(e,u,D) = {np.round(rep['c_e_u_D'], 3).tolist()}; R = {rep['R_scale_MR_over_F']:.3e}; "
      f"MR = {['%.2e' % m for m in rep['MR_eigs_GeV']]}; F svals = {['%.3g' % m for m in rep['F_eigs_GeV']]}; r = {rep['r']:.3g}, s = {np.round(rep['s'], 3).tolist()}", flush=True)
out = {"content": content, "floor": floor, "mode": mode, "gmax": gmax, "Rmin": Rmin, "info": info, "n_screen": len(screen), "n_hops": nh,
       "screen_best": [c for c, _ in screen[:20]], "polished": [c for c, _ in pol], "best": rep, "x": best[1].tolist(),
       "targets": {k: list(map(float, v)) for k, v in tg.items()}}
json.dump(out, open(f"fit_{content}_{mode}_f{floor:g}_g{gmax:g}" + (f"_R{Rmin:.0e}" if Rmin else "") + ".json", "w"), indent=1, default=float)
