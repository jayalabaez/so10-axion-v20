#!/usr/bin/env python3
"""Stage-2a "model": structural consequence of the corrected invariant list (NUM, exact up to float rounding).

The cubic kappaPPA eps.P.P.A (absent from the Stage-1 list) and the quartics lambdaPPPA1,2 eps.P^3.A are LINEAR in
A: at any Phi210 vev they give A a tadpole.  Here the tadpole direction is evaluated on the Pati-Salam/SM-singlet
210 directions (indices 0..5 = SO(6) ~ SU(4), 6..9 = SO(4) ~ SU(2)_L x SU(2)_R):
    p     = e^{6789}                                  (1,1,1)
    a     = e^{0123} + e^{0145} + e^{2345}             (15,1,1) B-L direction (= *_6 of J)
    omega = J ^ t_R,  J = e^{01}+e^{23}+e^{45},  t_R = e^{67} - e^{89}     (15,1,3), T3R = 0 component
and, conversely, the Phi210 tadpole of kappaPAA P.(A A) at <A> = w_BL T_BL + w_R T3R with T_BL = J (on 0..5),
T3R = t_R (on 6..9).  The tadpole components are projected on {T_BL, T3R, T3L = e^{67}+e^{89}} and on the rest.
(The orientation/sign convention t_R = e67 - e89 vs e67 + e89 only swaps the names L and R.)
Output: vev_structure_v22.json.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_invariants_v22 as BI  # noqa: E402
import explicit_basis_v22 as EB  # noqa: E402

N = 10


def form(terms, k):
    comp = np.zeros(len(EB.combos(k)))
    idx = {tuple(c): i for i, c in enumerate(EB.combos(k))}
    for coef, ind in terms:
        s = EB.perm_parity(np.argsort(ind)) if len(ind) else 1
        comp[idx[tuple(sorted(ind))]] += coef * s
    return EB.form_from_components(comp, k)


def two_form(terms):
    A = np.zeros((N, N))
    for c, (i, j) in terms:
        A[i, j] += c; A[j, i] -= c
    return A


J = two_form([(1, (0, 1)), (1, (2, 3)), (1, (4, 5))])
TR = two_form([(1, (6, 7)), (-1, (8, 9))])
TL = two_form([(1, (6, 7)), (1, (8, 9))])
p4 = form([(1, (6, 7, 8, 9))], 4)
a4 = form([(1, (0, 1, 2, 3)), (1, (0, 1, 4, 5)), (1, (2, 3, 4, 5))], 4)
# omega = J ^ t_R: total antisymmetrisation of J_ab t_cd (overall factor irrelevant)
w4 = sum(EB.perm_parity(p) * np.transpose(np.einsum("ab,cd->abcd", J, TR), p)
         for p in itertools.permutations(range(4))) / 4.0


def grad_A(spec_name, P):
    """gradient of a linear-in-A invariant w.r.t. the 45 independent components A_ij (i<j)."""
    spec = next(s for s in BI.NEW if s[0] == spec_name)
    g = np.zeros((N, N))
    for i, j in itertools.combinations(range(N), 2):
        E = np.zeros((N, N)); E[i, j] = 1; E[j, i] = -1
        F = {"A": E, "P": P, "H": np.zeros(N, complex), "Hb": np.zeros(N, complex),
             "D": np.zeros((N,) * 5, complex), "Db": np.zeros((N,) * 5, complex), "S": 0, "T": 0}
        v = BI.value(spec, F).real
        g[i, j] = v; g[j, i] = -v
    return g


def project(G):
    nrm = lambda X: np.sqrt((X * X).sum() / 2)
    out = {}
    rest = G.copy()
    for nm, T in (("T_BL", J), ("T3R", TR), ("T3L", TL)):
        c = (G * T).sum() / (T * T).sum()
        out[nm] = float(c)
        rest = rest - c * T
    out["norm_total"] = float(nrm(G)); out["norm_rest"] = float(nrm(rest))
    return out


def main():
    res = {}
    for label, P in (("p", p4), ("a", a4), ("omega", w4), ("p+a", p4 + a4), ("p+omega", p4 + w4),
                     ("a+omega", a4 + w4), ("p+a+omega", p4 + a4 + w4), ("0.7071 p - 0.7071 a (A1 point)",
                                                                        0.7071 * p4 - 0.7071 * a4)):
        r = {}
        for nm in ("A04_PPA_eps", "A06_PPPA_eps1", "A07_PPPA_eps2"):
            r[nm] = project(grad_A(nm, P))
        res[label] = r
        print(f"{label:32s}", {k: {kk: round(vv, 6) for kk, vv in v.items()} for k, v in r.items()})
    # Phi210 tadpole of kappaPAA at <A>
    spec = next(s for s in BI.NEW if s[0] == "A05_PAA")
    phi_t = {}
    for label, A in (("T_BL", J), ("T3R", TR), ("T_BL+T3R", J + TR)):
        g = np.zeros(len(EB.combos(4)))
        for n, c in enumerate(EB.combos(4)):
            E = np.zeros(len(EB.combos(4))); E[n] = 1
            Pn = EB.form_from_components(E, 4)
            F = {"A": A, "P": Pn, "H": np.zeros(N, complex), "Hb": np.zeros(N, complex),
                 "D": np.zeros((N,) * 5, complex), "Db": np.zeros((N,) * 5, complex), "S": 0, "T": 0}
            g[n] = BI.value(spec, F).real
        G = EB.form_from_components(g, 4)
        proj = {}
        rest = G.copy()
        for nm, T in (("p", p4), ("a", a4), ("omega", w4)):
            cc = (G * T).sum() / (T * T).sum()
            proj[nm] = float(cc); rest = rest - cc * T
        proj["norm_rest/norm_total"] = float(np.sqrt((rest ** 2).sum() / max((G ** 2).sum(), 1e-300)))
        phi_t[label] = proj
        print("kappaPAA Phi-tadpole at <A> =", label, {k: round(v, 6) for k, v in proj.items()})
    out = {"A_tadpoles_from_linear_in_A_invariants": res, "Phi_tadpole_from_kappaPAA": phi_t,
           "conventions": __doc__}
    (HERE / "vev_structure_v22.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
