"""Verifier: robustness of the quality kill and the decay-operator dimensions.
(1) Closure variants that avoid every doubtful ingredient: no H10 lines (hence no kappa lock), no operator with
    >= 3 identical Weyl fields (Fermi statistics), optionally no Delta vev; NDA at M_s = 1e13 and 3e12 with
    <S> = M_s / y_s at the window edges.
(2) Minimal dimension of operators changing f1, f2, f3 by one unit (decays of the Vec1, Vec3/PhiV and tensor
    sectors), centre/X-level ILP followed by an SO(10) singlet verification with my Klimyk counter.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from so10_singlets_klimyk import singlets  # noqa: E402
from v3_closure_ilp import FIELDS, FERMS, YUK, enumerate_ops, build_ilp, label, nda  # noqa: E402

MPL = 2.435e18
CHI = 0.0755 ** 4


def identical_max(op):
    return max(op["counts"].values()) if op["counts"] else 0


def main():
    out = {}
    ops, _ = enumerate_ops()
    safe = [op for op in ops if max([k for (n, b), k in op["counts"].items() if FIELDS[n][2]] or [0]) <= 2]
    safe_idx = {id(op) for op in safe}
    print("ops:", len(ops), "| Fermi-safe (<=2 identical Weyl fields):", len(safe))
    phi = ("PhiV", "PhiVbar")
    h10yuk = ("lamF2", "lam3P", "yAM", "yBN")
    variants = {
        "safe_noH10_noPhi_noFamily": dict(forbid_names=phi + ("H10",), forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126")),
        "safe_noH10_noPhi_noFamily_noDeltaVev": dict(forbid_names=phi + ("H10",), forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126"), require_no_delta_vev=True),
        "safe_noH10_noPhi_noFamily_noDelta_noTensors": dict(forbid_names=phi + ("H10", "Delta", "F", "TenA", "TenB", "SingN", "SingM"),
                                                            forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126", "yAB", "yNM")),
        "safe_all_with_H10": dict(),
        "safe_noPhi_noH10Yuk_noFamily(with_kappa)": dict(forbid_names=phi, forbid_yuk=("yP",) + h10yuk + ("Y10", "Y126")),
    }
    res = {}
    for tag, kw in variants.items():
        d = build_ilp(safe, **kw)
        if d is None:
            print("==", tag, "infeasible")
            res[tag] = None
            continue
        rows = {}
        for ms, ys in ((1.0e13, 0.304), (1.0e13, 0.374), (3.0e12, 0.091), (3.0e12, 0.35)):
            S = ms / ys
            e = nda(d, Ms=ms, S=S, y=ys)
            rows["Ms=%.0e,ys=%.3f" % (ms, ys)] = {"log10_dtheta": round(e["log10_dtheta"], 2), "log10_dtheta_H10_at_MU": round(nda(d, Ms=ms, S=S, y=ys, mH=2.1e16)["log10_dtheta_H10_at_mH"], 2)}
        d["nda_rows"] = rows
        res[tag] = d
        print("==", tag, "K =", d["K"], "loops", d["loops"], "vev", d["vev_monomial"], "kappa", d["kappa"])
        for o in d["ops"]:
            print("     ", o)
        print("      yukawas", d["yukawas"])
        for k, v in rows.items():
            print("      %s: log10 dtheta = %s (H10 lines at M_U: %s)" % (k, v["log10_dtheta"], v["log10_dtheta_H10_at_MU"]))
    out["closures_fermi_safe"] = res

    # ---- (2) decay operators: centre-level ILP (X=0, Z4 centre, Lorentz, f-targets) then singlet verification
    Z = {16: 1, -16: 3, 10: 2, -126: 2, 1: 0}
    G2 = {"Phi17": 1, "PhiV": -1}
    F1 = {"Vec1": 1, "Vec1bar": -1}
    F2 = {"Vec3": -1, "Vec3bar": 1, "PhiV": 1, "PhiVbar": -1}
    F3 = {"TenA": 1, "TenB": -1, "SingN": 1, "SingM": -1}
    names = list(FIELDS)

    def cols(allowed):
        c = []
        for n in names:
            if n not in allowed:
                continue
            r, x, f = FIELDS[n]
            cost = 1.5 if f else 1.0
            for b in (False, True):
                s = -1 if b else 1
                c.append(dict(name=n, barred=b, X=s * x, z=(s * Z[r]) % 4, f1=s * F1.get(n, 0), f2=s * F2.get(n, 0), f3=s * F3.get(n, 0),
                              ferm=f, cost=cost))
        return c

    def solve(allowed, ftarget, nf_exact=None):
        c = cols(allowed)
        n = len(c)
        best = None
        for parity in (0, 1):
            cost = np.array([v["cost"] for v in c] + [0, 0, 0])
            rows, lb, ub = [], [], []
            rows.append([v["X"] for v in c] + [0, 0, 0]); lb.append(0); ub.append(0)
            rows.append([v["z"] for v in c] + [-4, 0, 0]); lb.append(0); ub.append(0)
            rows.append([1 if (v["ferm"] and not v["barred"]) else 0 for v in c] + [0, -2, 0]); lb.append(parity); ub.append(parity)
            rows.append([1 if (v["ferm"] and v["barred"]) else 0 for v in c] + [0, 0, -2]); lb.append(parity); ub.append(parity)
            for key, t in zip(("f1", "f2", "f3"), ftarget):
                rows.append([v[key] for v in c] + [0, 0, 0]); lb.append(t); ub.append(t)
            if nf_exact is not None:
                rows.append([1 if v["ferm"] else 0 for v in c] + [0, 0, 0]); lb.append(nf_exact); ub.append(nf_exact)
            rows.append([1] * n + [0, 0, 0]); lb.append(1); ub.append(200)
            lo = np.zeros(n + 3); hi = np.full(n + 3, 60.0); lo[n:] = -60
            r = milp(cost, constraints=LinearConstraint(np.array(rows, dtype=float), lb, ub), integrality=np.ones(n + 3), bounds=Bounds(lo, hi))
            if r.success:
                counts = {(c[i]["name"], c[i]["barred"]): int(round(r.x[i])) for i in range(n) if round(r.x[i]) > 0}
                dim = r.fun + parity
                if best is None or dim < best[0]:
                    best = (dim, counts, parity)
        return best

    def verify(counts):
        reps = []
        for (n, b), k in counts.items():
            r = FIELDS[n][0]
            rr = r if (abs(r) in (1, 10) or not b) else -r
            if rr != 1:
                reps += [rr] * k
        return singlets(reps)

    dec = {}
    sectors = {"f1": (("F", "Vec1", "Vec1bar", "H10", "Delta", "S", "Phi17"), (1, 0, 0)),
               "f2": (("F", "Vec3", "Vec3bar", "PhiV", "PhiVbar", "H10", "Delta", "S", "Phi17"), (0, 1, 0)),
               "f3": (("F", "TenA", "TenB", "SingN", "SingM", "H10", "Delta", "S", "Phi17"), (0, 0, 1))}
    for key, (allowed, ft) in sectors.items():
        rows = {}
        for sign in (1, -1):
            t = tuple(sign * v for v in ft)
            for nf in (2, 4):
                r = solve(allowed, t, nf_exact=nf)
                if r is None:
                    rows["f=%s,nf=%d" % (t, nf)] = "infeasible"
                else:
                    rows["f=%s,nf=%d" % (t, nf)] = {"dim": r[0], "op": label(r[1]), "so10_singlets": verify(r[1])}
        dec[key] = rows
        print(key, json.dumps(rows, indent=1))
    out["decay_operators"] = dec
    # Vec3 lifetime estimate (mixing through the dim-10 operator)
    S, vR, Phi, Ms = 3.3e13, 2.6e13, 1.0e17, 1.0e13
    mmix = vR * S ** 5 * Phi / MPL ** 6
    theta = mmix / Ms
    gamma = theta ** 2 * (1 / 137.0) * Ms
    tau = 6.582e-25 / gamma
    out["Vec3_lifetime"] = dict(mixing_mass_GeV=mmix, angle=theta, Gamma_GeV=gamma, tau_s=tau)
    print("Vec3 mixing:", out["Vec3_lifetime"])
    (HERE / "v5_robustness.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
