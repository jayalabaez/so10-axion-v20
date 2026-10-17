#!/usr/bin/env python3
"""Continuation check (2026-10-17): independent threshold evaluation of R2-A's IN-PROGRESS explicit C2 points at Am45.

R2-A (parallel gate, folder ../R2-A-vacuum-two-bidoublets, read-only here) has stage-A LP coupling points with exactly
the C2 light content (both bidoublets + vev-light Delta_R; 35 zero / 0 negative / 20 light / 431 heavy) at the Am45
orientation.  They are heavy-gap-maximising LP points WITHOUT BFB/competitor cuts (lambda_direct = -1 along the H ray),
i.e. spectra of the C2 family, not certified vacua.  This script recomputes their heavy spectra from K3's Am45 SM-isotypic
reduced Hessians (same chart point as R2-A's Am45 runs: checked block by block against R2-A's stored eigenvalues),
assigns every heavy eigenvalue to its G3221 multiplet with this gate's own assignment routine (copied from r2b_p831.py)
and solves the B63 chain at 1/2/3 loops with those thresholds (g_U iterated).  Nothing is written outside this folder.
"""
import json
import math
import os
import sys
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2b_model as M

K3 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "wfV21", "K3-vacuum-g6-higgs")
R2A = os.path.join(os.path.dirname(HERE), "R2-A-vacuum-two-bidoublets")
B = np.load(os.path.join(K3, "Am45_blocks.npz"))
labels = [str(x) for x in B["labels"]]


def block_spectrum(c):
    spec = {}
    for k, lab in enumerate(labels):
        A = B[f"A{k}"]
        Mk = np.einsum("i,ijk->jk", c, A)
        Mk = 0.5 * (Mk + Mk.conj().T)
        G = B[f"G{k}"]
        m = Mk.shape[0]
        if G.shape[1] > 0:
            uu, ss, _ = np.linalg.svd(G, full_matrices=True)
            Q = uu[:, G.shape[1]:]
        else:
            Q = np.eye(m)
        spec[lab] = sorted(np.linalg.eigvalsh(Q.conj().T @ Mk @ Q).tolist())
    return spec


def k3_label(su3, su2l, y):
    d3 = {"1": 1, "3": 3, "3b": 3, "6": 6, "6b": 6, "8": 8}[su3]
    ya = abs(F(y))
    ys = str(ya.numerator) if ya.denominator == 1 else f"{ya.numerator}/{ya.denominator}"
    return f"({d3},{su2l})_|Y|={ys}"


def pieces_blocks(name):
    kind, c3, l, r, q = M.SCALAR_TABLE[name]
    out = []
    nr = int(r)
    seen_real = set()
    for k in range(nr):
        t3r = F(nr - 1, 2) - k
        y = t3r + q / 2
        lab = k3_label(c3, l, y)
        if kind == "real":
            key = (lab, abs(y))
            if key in seen_real:
                continue
            seen_real.add(key)
        out.append(lab)
    return out


def assign(spec, light, heavy_floor=1e-4, rtol=3e-3):
    avail = {lab: [v for v in vals if v > heavy_floor] for lab, vals in spec.items()}
    heavy = [n for n in M.SCALAR_TABLE if n not in light]
    order = sorted(heavy, key=lambda n: -len(pieces_blocks(n)))
    res, problems = {}, []
    for n in order:
        pb = pieces_blocks(n)
        need = {}
        for lab in pb:
            need[lab] = need.get(lab, 0) + 1
        first = pb[0]
        best = None
        for cand in sorted(set(avail.get(first, []))):
            ok = all(sum(1 for v in avail.get(lab, []) if abs(v - cand) <= rtol * cand) >= cnt for lab, cnt in need.items())
            if ok:
                best = cand
                break
        if best is None:
            problems.append(n)
            continue
        for lab, cnt in need.items():
            for _ in range(cnt):
                j = min(range(len(avail[lab])), key=lambda i: abs(avail[lab][i] - best))
                avail[lab].pop(j)
        res[n] = best
    leftover = {lab: v for lab, v in avail.items() if v}
    return res, problems, leftover


def solve_with_spectrum(light, m2, loops, sv=+1, scale=1.0):
    aU = 33.0
    row, gr = None, {}
    for _ in range(6):
        g = math.sqrt(4 * math.pi / aU)
        mx_phi = M.MX_OVER_G_PHI * g
        gr = {n: scale * math.sqrt(v) / mx_phi for n, v in m2.items() if n not in light}
        p = M.Params(light=light, gut_ratios=gr, loops=loops, sv_sign=sv)
        ll = () if loops == 1 else (loops,)
        row = M.full_point(p, landau_loops=ll, x_opts=(None,))
        if not row.get("ok"):
            break
        if abs(row["alpha_U_inv"] - aU) < 1e-5:
            break
        aU = row["alpha_U_inv"]
    out = {k: v for k, v in row.items() if k in ("ok", "v_R", "M_U", "alpha_U_inv", "tau_p_yr", "L2", "L3")}
    if out.get("ok"):
        out["tau_dir_yr"] = M.proton_lifetime_direct_years(out["M_U"], out["alpha_U_inv"])
    out["ratios_min_max"] = [min(gr.values()), max(gr.values())] if gr else None
    out["ratio_geomean"] = math.exp(sum(math.log(x) for x in gr.values()) / len(gr)) if gr else None
    return out


result = {}
for tag in ("S5_Am45_C2", "L5_Am45_C2_loc", "L_Am45_C2_d6"):
    npz = os.path.join(R2A, tag + ".npz")
    js = os.path.join(R2A, tag + ".json")
    if not os.path.exists(npz):
        continue
    c = np.load(npz)["c"]
    meta = json.load(open(js))
    spec = block_spectrum(c)
    # chart-consistency check against R2-A's stored block eigenvalues
    stored = {b["label"]: b["eigenvalues"] for b in meta.get("blocks", []) if isinstance(b, dict)}
    maxdev = 0.0
    nchk = 0
    for lab, ev in stored.items():
        if lab in spec and len(spec[lab]) == len(ev):
            d = max(abs(a - b) for a, b in zip(sorted(spec[lab]), sorted(ev)))
            maxdev = max(maxdev, d)
            nchk += 1
    res, problems, leftover = assign(spec, M.CONTENTS["C2"])
    row = {"stage": meta.get("stage"), "t": meta.get("t"), "lambda": str(meta.get("lambda"))[:160],
           "chart_check_blocks": nchk, "chart_check_max_abs_dev": maxdev,
           "assigned_m2_over_Phi2": res, "unassigned": problems,
           "leftover": {k: [x for x in v if x < 50] for k, v in leftover.items()}}
    sols = {}
    if not problems:
        for loops in (1, 2, 3):
            sols[f"{loops}L"] = solve_with_spectrum(M.CONTENTS["C2"], res, loops)
        sols["2L|sv-"] = solve_with_spectrum(M.CONTENTS["C2"], res, 2, sv=-1)
        sols["2L|sv0"] = solve_with_spectrum(M.CONTENTS["C2"], res, 2, sv=0)
        for sc in (0.5, 2.0):
            sols[f"2L|spectrum x{sc:g}"] = solve_with_spectrum(M.CONTENTS["C2"], res, 2, scale=sc)
    row["solutions"] = sols
    result[tag] = row
    print(tag, "stage", row["stage"], "t", row["t"], "chart check", nchk, f"{maxdev:.2e}", "unassigned", problems, flush=True)
    for n, v in sorted(res.items(), key=lambda kv: kv[1]):
        print(f"   {n:28s} m/|Phi| = {math.sqrt(v):.4f}", flush=True)
    for k, s in sols.items():
        print("  ", k, {kk: (f"{vv:.4g}" if isinstance(vv, float) else vv) for kk, vv in s.items()}, flush=True)
with open(os.path.join(HERE, "r2b_r2a_c2check.json"), "w") as fh:
    json.dump(result, fh, indent=1, default=str)
print("done")
