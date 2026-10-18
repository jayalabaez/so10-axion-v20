#!/usr/bin/env python3
"""Descent / BFB-search core shared by vdesc.py (global search) and vlp.py (in-loop screens).

descend(F, q0, Vstar): L-BFGS on the exact polynomial V_c (vc.FastV), saddle escapes along the most negative Hessian
eigenvector (dense exact Hessian), runaway detection (V < V* - runaway_V, or |q| > runaway_q while V < V*: the
quartic dominates there, so the direction is unbounded below at tree level).
quartic_min(F4, u0): local minimum of V4(u)/|u|^4 on the unit sphere (F4 = FastV of the degree-4 couplings only).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import minimize

import vc


class Runaway(Exception):
    def __init__(self, q):
        super().__init__("runaway")
        self.q = q


def descend(F, q_start, Vstar, maxiter=4000, escapes=6, runaway_V=1e7, runaway_q=2e3, hess_check=True):
    best = {"V": np.inf, "q": None}
    n_eval = [0]

    def fg(q):
        V, g = F.value_grad(q)
        n_eval[0] += 1
        if V < best["V"]:
            best["V"] = V
            best["q"] = q.copy()
        if V < Vstar - runaway_V or (np.linalg.norm(q) > runaway_q and V < Vstar):
            raise Runaway(q.copy())
        return V, g

    q = np.asarray(q_start, float).copy()
    n_esc = 0
    runaway = False
    q_run = None
    lam_min = None
    hist = []
    while True:
        try:
            r = minimize(fg, q, jac=True, method="L-BFGS-B",
                         options={"maxiter": maxiter, "maxcor": 30, "ftol": 1e-15, "gtol": 1e-10, "maxfun": 3 * maxiter})
            q = r.x
            nit = int(r.nit)
        except Runaway as e:
            runaway = True
            q_run = e.q
            break
        V, g = F.value_grad(q)
        gn = float(np.linalg.norm(g))
        if not hess_check:
            hist.append({"V-V*": V - Vstar, "grad": gn, "iters": nit})
            break
        H = F.hessian(q)
        w, vec = np.linalg.eigh(H)
        lam_min = float(w[0])
        hist.append({"V-V*": V - Vstar, "grad": gn, "lam_min": lam_min, "iters": nit})
        if lam_min < -1e-6 and n_esc < escapes:
            step = max(1e-3, min(0.3, math.sqrt(abs(lam_min))))
            cands = [q + step * vec[:, 0], q - step * vec[:, 0]]
            vals = [F.value(x) for x in cands]
            q = cands[int(np.argmin(vals))]
            n_esc += 1
            continue
        break
    qe = best["q"] if runaway else q
    Ve = best["V"] if runaway else float(F.value(q))
    return {"runaway": runaway, "V_end-V*": Ve - Vstar, "V_min_seen-V*": best["V"] - Vstar, "escapes": n_esc,
            "lam_min": lam_min, "n_eval": n_eval[0], "history": hist}, qe, q_run


class _Found(Exception):
    pass


def quartic_min(F4, u0, maxiter=500, stop_below=None):
    """minimise f(u) = V4(u)/|u|^4 locally from u0; returns (f_min, unit u).  stop_below: return as soon as
    f < stop_below (a violating ray is all a BFB cut needs)."""
    best = {"f": np.inf, "u": None}

    def fg(u):
        n2 = float(u @ u)
        V, g = F4.value_grad(u)
        f = V / n2 ** 2
        if f < best["f"]:
            best["f"] = f
            best["u"] = u.copy()
        if stop_below is not None and f < stop_below:
            raise _Found()
        gf = g / n2 ** 2 - 4.0 * V * u / n2 ** 3
        return f, gf
    u0 = np.asarray(u0, float) / np.linalg.norm(u0)
    try:
        minimize(fg, u0, jac=True, method="L-BFGS-B", options={"maxiter": maxiter, "gtol": 1e-12, "ftol": 1e-15})
    except _Found:
        pass
    u = best["u"] / np.linalg.norm(best["u"])
    return float(best["f"]), u
