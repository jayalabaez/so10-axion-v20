#!/usr/bin/env python3
"""Where are the lower vacua?  Gauge-align the deepest end point of every class to q* (Gauss-Newton on
SO(10) x U(1)_X x PQ with my own tensor rotations, 24 random starting rotations) and decompose the aligned
displacement d = g.q_low - q* on the Hessian eigenbasis at q* (zero / light / heavy) and by SM multiplet (Casimirs).
A lower point reached mainly along LIGHT directions is a light-sector instability (negative effective quartic or
untuned light cubic); a point far away along heavy directions is a genuinely different vacuum.
usage: python -B vsk_align.py <content Lb|Lae>
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np
from scipy.linalg import expm

import vsk_eval as E

sys.path.insert(0, str(E.HERE.parent))
import vc  # noqa: E402

C = vc.C
content = sys.argv[1]
P = np.load(E.BIGV / "pt_O11.npz")
qs = P["q"]
ops = C.label_operators()
Cc, Cw = ops["C3"], ops["C2L"]
GENS = []
for a, b in E.PAIRS:
    L = np.zeros((10, 10))
    L[a, b], L[b, a] = 1.0, -1.0
    GENS.append(L)


GEN531 = [C.generator(np.eye(45)[k]).toarray() for k in range(45)] + [C.u1x_generator().toarray(),
                                                                        C.pq_generator().toarray()]


def tangents(q):
    return np.column_stack([G @ q for G in GEN531])


def apply_step(q, om):
    M = sum(w_ * G for w_, G in zip(om, GEN531))
    return expm(M) @ q


def align(q, rng, n_starts=8):
    best = (np.inf, None)
    for s in range(n_starts):
        if s == 0:
            x = q.copy()
        else:
            t = E.tensors(q)
            t = E.phase(E.phase(E.rotate(t, E.random_rotation(rng)), E.XCH, rng.uniform(0, 6.3)), E.pq_charges(),
                        rng.uniform(0, 6.3))
            x = E.pack(t)
        prev = np.inf
        for it in range(80):
            T = tangents(x)
            r = x - qs
            step, *_ = np.linalg.lstsq(T, -r, rcond=None)
            nst = np.linalg.norm(step)
            x_new = apply_step(x, step * min(1.0, 0.5 / max(1e-12, nst)))
            if np.linalg.norm(x_new - qs) > np.linalg.norm(r):
                x_new = apply_step(x, 0.2 * step * min(1.0, 0.5 / max(1e-12, nst)))
            x = x_new
            d = np.linalg.norm(x - qs)
            if prev - d < 1e-10 * max(1.0, d):
                break
            prev = d
        d = float(np.linalg.norm(x - qs))
        if d < best[0]:
            best = (d, x)
    return best


sols = {"Lb": ["R1d_Lb_O11.npz", "R2d_Lb_O11.npz", "R3d_Lb_O11.npz"],
        "Lae": ["R1d_Lae_O11.npz", "R2d_Lae_O11.npz", "R3d_Lae_O11.npz"]}[content]
ep = json.load(open(E.BIGS / f"endpoints_{content}.json"))
rng = np.random.default_rng(3)
out = []
for r_, sol in zip(ep["rounds"], sols):
    assert r_["sol"] == sol
    Z = np.load(E.BIGS / f"endpoints_{content}_{sol[:2]}.npz")
    Q, dV = Z["Q"], Z["dV"]
    c = E.load_c(sol)
    cv = np.array([c[p] for p in vc.IDS])
    F = vc.FastV(cv)
    H = F.hessian(qs)
    w, U = np.linalg.eigh(H)
    zero, light, heavy = np.abs(w) < 1e-9, (w >= 1e-9) & (w < 3e-5), w >= 3e-5
    # one representative (deepest) per class
    classes = {}
    for i, rec in enumerate(r_["records"]):
        if dV[i] >= -2.5e-6:
            continue
        b = rec["block_norms"]
        key = ("H" if b["H"] > 1e-3 else "-") + ("Sig" if b["Sig"] > 1e-2 else "-") + ("S" if b["S"] > 1e-2 else "-") + \
              ("Phi" if b["Phi"] > 0.3 else "phi0")
        if key not in classes or dV[i] < dV[classes[key]]:
            classes[key] = i
    for key, i in classes.items():
        t0 = time.time()
        dmin, xa = align(Q[i], rng)
        dlt = xa - qs
        cz = U[:, zero].T @ dlt
        cl = U[:, light].T @ dlt
        ch = U[:, heavy].T @ dlt
        # SM content of the light part
        Ul = U[:, light]
        dl = Ul @ cl
        cas = (float(dl @ Cc @ dl) / max(1e-30, float(dl @ dl)), float(dl @ Cw @ dl) / max(1e-30, float(dl @ dl)))
        # energy decomposition along the straight line q* -> aligned point
        ts = np.linspace(0, 1, 11)
        prof = [float(F.value(qs + s * dlt) - F.value(qs)) for s in ts]
        rec = {"sol": sol, "class": key, "label": r_["records"][i]["label"], "dV": float(dV[i]),
               "dist_mod_gauge": dmin, "|zero part|": float(np.linalg.norm(cz)), "|light part|": float(np.linalg.norm(cl)),
               "|heavy part|": float(np.linalg.norm(ch)), "light_part_casimirs(C3,C2L)": cas,
               "block_norms": r_["records"][i]["block_norms"],
               "block_norms_qstar": {k: float(np.linalg.norm(qs[s])) for k, s in vc.BLOCKS.items()},
               "line_profile_dV": prof, "seconds": time.time() - t0}
        print(json.dumps(rec, default=float), flush=True)
        out.append(rec)
        json.dump(out, open(E.HERE / f"vsk_align_{content}.json", "w"), indent=1, default=float)
