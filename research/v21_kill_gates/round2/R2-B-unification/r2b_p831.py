#!/usr/bin/env python3
"""GUT-scale thresholds from an explicit vacuum point of the v20 potential: K3's P831 and P831b (C0 content:
bidoublet + (8,3,1)_0 + Delta_R light, Am45 orientation; local minima, NOT global).  Reads (read-only) the K3 round-1
files Am45_blocks.npz (SM-isotypic reduced Hessians A_k[51], Goldstone vectors) and P831*.npz (coupling vectors c).

1. Block spectra M_k = sum_i c_i A_k[i] on the Goldstone complement (451 = 486 - 35 non-Goldstone real modes).
2. Assignment of every heavy eigenvalue to a G3221 multiplet of 210 + 126bar + 10 by the degeneracy pattern across
   SM blocks (each G3221 multiplet populates the SM blocks of its T3R components with ONE eigenvalue; splitting O(r^2)).
3. Mass ratios m/M_X with M_X = M(3,2,2) = 0.6455 g_U |Phi| (K3 chart), g_U from the solution (iterated); the
   (3,1,1)_{4/3} vector at 0.894 M_X.  Solve C0 (exact content of the point) at 1/2/3 loops with these thresholds.
4. Transplant (EST): the same 210/126bar/10 spectrum used for C1/C2/C1p, with the multiplet that is light there
   removed and the multiplet that is heavy there but light at P831 ((8,3,1)_0) put at f x M_X, f in {0.1, 0.3, 1}.
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
            # real multiplet: Y and -Y components form one complex SM field (one eigenvalue in the |Y| block)
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


out = {}
for tag in ("P831", "P831b"):
    c = np.load(os.path.join(K3, f"{tag}.npz"))["c"]
    spec = block_spectrum(c)
    res, problems, leftover = assign(spec, M.CONTENTS["C0"])
    out[tag] = {"block_spectra_m2_over_Phi2": spec, "assigned_m2_over_Phi2": res, "unassigned_multiplets": problems,
                "leftover_eigenvalues": leftover}
    print(tag, "unassigned", problems, "leftover", leftover)
    for n, v in sorted(res.items(), key=lambda kv: kv[1]):
        print(f"   {n:28s} m2 = {v:.5f}  m/|Phi| = {math.sqrt(v):.4f}")


def solve_with_spectrum(light, m2, loops, extra_heavy=None, sv=+1):
    """Iterate g_U: ratio_k = sqrt(m2_k)/(0.6455 g_U)."""
    aU = 33.0
    row = None
    for it in range(4):
        g = math.sqrt(4 * math.pi / aU)
        mx_phi = M.MX_OVER_G_PHI * g
        gr = {n: math.sqrt(v) / mx_phi for n, v in m2.items() if n not in light}
        if extra_heavy:
            gr.update(extra_heavy)
        p = M.Params(light=light, gut_ratios=gr, loops=loops, sv_sign=sv)
        ll = () if loops == 1 else (loops,)
        row = M.full_point(p, landau_loops=ll, x_opts=(None,))
        if not row.get("ok"):
            break
        if abs(row["alpha_U_inv"] - aU) < 1e-4:
            break
        aU = row["alpha_U_inv"]
    row = {k: v for k, v in row.items() if k in ("ok", "v_R", "M_U", "alpha_U_inv", "tau_p_yr", "L2", "L3")}
    row["ratios_min_max"] = [min(gr.values()), max(gr.values())]
    row["ratio_geomean"] = math.exp(sum(math.log(x) for x in gr.values()) / len(gr))
    return row


for tag in ("P831", "P831b"):
    m2 = out[tag]["assigned_m2_over_Phi2"]
    rows = {}
    for loops in (1, 2, 3):
        rows[f"C0|{loops}L"] = solve_with_spectrum(M.CONTENTS["C0"], m2, loops)
        print(tag, f"C0|{loops}L", rows[f"C0|{loops}L"], flush=True)
    for cont in ("C1", "C2", "C1p"):
        light = M.CONTENTS[cont]
        for f in (0.1, 0.3, 1.0):
            extra = {} if "210:(8,3,1)_0" in light else {"210:(8,3,1)_0": f}
            key = f"{cont}|2L|(8,3,1)x{f:g}" if extra else f"{cont}|2L"
            if key in rows:
                continue
            rows[key] = solve_with_spectrum(light, m2, 2, extra_heavy=extra)
            print(tag, key, rows[key], flush=True)
    out[tag]["solutions"] = rows
with open(os.path.join(HERE, "r2b_p831.json"), "w") as fh:
    json.dump(out, fh, indent=1, default=str)
print("done")
