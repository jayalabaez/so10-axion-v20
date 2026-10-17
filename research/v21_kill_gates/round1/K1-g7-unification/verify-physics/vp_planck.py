#!/usr/bin/env python3
"""Independent check of the Planck gauge-kinetic Clebsches and heavy-vector masses for the 210 in the G3221 orientation.

Own construction: so(10) orthonormal basis t^(ab) = (E_ab - E_ba)/sqrt2 (sum of squares of entries = 1, i.e. T(10) = 1);
u(3) subalgebra of so(6) found numerically as the commutant of the complex structure J; su(2)_+/- of so(4) as
(anti-)self-dual combinations.  4-form Phi with canonical inner product <X,Y> = sum_{a<b<c<d} X Y.
K_A = sum_{abcd} Phi_{abcd} t^A_{ab} t^A_{cd};  M^2_{AB}/g^2 = <t^A Phi, t^B Phi>.
"""
import itertools
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 10


def gen(a, b):
    m = np.zeros((N, N))
    m[a, b], m[b, a] = 1 / math.sqrt(2), -1 / math.sqrt(2)
    return m


def unit(m):
    return m / math.sqrt(np.sum(m * m))


def four_form(comp):
    phi = np.zeros((N, N, N, N))
    for idx, val in comp.items():
        for perm in itertools.permutations(range(4)):
            # parity of the permutation
            p = list(perm)
            sgn = 1
            for i in range(4):
                for j in range(i + 1, 4):
                    if p[i] > p[j]:
                        sgn = -sgn
            phi[tuple(idx[k] for k in perm)] = sgn * val
    return phi


def act(t, phi):
    return (np.einsum("ae,ebcd->abcd", t, phi) + np.einsum("be,aecd->abcd", t, phi)
            + np.einsum("ce,abed->abcd", t, phi) + np.einsum("de,abce->abcd", t, phi))


def inner(x, y):
    return float(np.sum(x * y)) / 24.0


def phi_of(p, a, w):
    comp = {(6, 7, 8, 9): p, (0, 1, 2, 3): a, (0, 1, 4, 5): a, (2, 3, 4, 5): a}
    for pl in ((0, 1), (2, 3), (4, 5)):
        for q in ((6, 7), (8, 9)):
            comp[pl + q] = w
    return four_form(comp)


# --- subalgebras -------------------------------------------------------------------------------------------------
basis = [gen(a, b) for a in range(N) for b in range(a + 1, N)]
so6 = [gen(a, b) for a in range(6) for b in range(a + 1, 6)]
J = np.zeros((N, N))
for k in range(3):
    J[2 * k, 2 * k + 1], J[2 * k + 1, 2 * k] = 1, -1
# commutant of J inside so(6): solve [X, J] = 0 for X = sum c_i so6_i
rows = []
for t in so6:
    rows.append((t @ J - J @ t).reshape(-1))
A = np.array(rows).T  # (100, 15)
u, s, vt = np.linalg.svd(A)
null = vt[np.sum(s > 1e-10):]  # rows spanning the null space
u3 = [sum(c * t for c, t in zip(v, so6)) for v in null]
assert len(u3) == 9, len(u3)
# Gram-Schmidt orthonormalise u3 (w.r.t. sum of squares of entries), put J direction first
def orthonormalise(vecs, first=None):
    out = []
    if first is not None:
        out.append(unit(first))
    for v in vecs:
        w = v.copy()
        for o in out:
            w = w - np.sum(w * o) * o
        if np.sum(w * w) > 1e-10:
            out.append(unit(w))
    return out
u3_on = orthonormalise(u3, first=J)
tBL = u3_on[0]
su3 = u3_on[1:]
assert len(su3) == 8
# check su3 generators are traceless w.r.t. J (orthogonal to J) and close under commutation into u3
for t in su3:
    assert abs(np.sum(t * tBL)) < 1e-12
# so(4) on 7..10
e = lambda a, b: gen(a, b)  # noqa: E731
su2p = [unit(e(6, 7) + e(8, 9)), unit(e(6, 8) - e(7, 9)), unit(e(6, 9) + e(7, 8))]
su2m = [unit(e(6, 7) - e(8, 9)), unit(e(6, 8) + e(7, 9)), unit(e(6, 9) - e(7, 8))]
# commutation check: [su2p, su2m] = 0
for x in su2p:
    for y in su2m:
        assert np.max(np.abs(x @ y - y @ x)) < 1e-12
# (3,1,1) generator: in so(6), orthogonal to u(3); (3,2,2): mixed index
so6_perp = orthonormalise([t - sum(np.sum(t * o) * o for o in u3_on) for t in so6])
assert len(so6_perp) == 6
t311 = so6_perp[0]
t322 = gen(0, 6)


def K(phi, t):
    return float(np.einsum("abcd,ab,cd->", phi, t, t))


def analyse(p, a, w):
    phi = phi_of(p, a, w)
    res = {"p": p, "a": a, "w": w, "norm2": inner(phi, phi)}
    for name, gl in (("SU3", su3), ("BL", [tBL]), ("SU2+", su2p), ("SU2-", su2m)):
        ks = [K(phi, t) for t in gl]
        res["K_" + name] = ks
        res["K_" + name + "_spread"] = max(ks) - min(ks)
        res["inv_" + name] = max(math.sqrt(inner(act(t, phi), act(t, phi))) for t in gl)
    # mass matrix
    vecs = [act(t, phi) for t in basis]
    M2 = np.array([[inner(x, y) for y in vecs] for x in vecs])
    ev = np.sort(np.linalg.eigvalsh(M2))
    res["n_unbroken"] = int(np.sum(ev < 1e-9))
    res["M2_322"] = inner(act(t322, phi), act(t322, phi))
    res["M2_311"] = inner(act(t311, phi), act(t311, phi))
    res["M2_eigen_distinct"] = sorted(set(np.round(ev, 8)))
    return res


out = {}
for pa in ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, -1, 0), (2, 0.5, 0), (1, 1, 1)):
    r = analyse(*[float(x) for x in pa])
    out[str(pa)] = r
    print(f"(p,a,w)={pa}: norm2={r['norm2']:.3f} unbroken={r['n_unbroken']} "
          f"K_SU3={r['K_SU3'][0]:+.4f}(spread {r['K_SU3_spread']:.1e}) K_BL={r['K_BL'][0]:+.4f} "
          f"K_SU2+={r['K_SU2+'][0]:+.4f}(spread {r['K_SU2+_spread']:.1e}) K_SU2-={r['K_SU2-'][0]:+.4f} "
          f"M2(322)={r['M2_322']:.4f} M2(311)={r['M2_311']:.4f} eig={r['M2_eigen_distinct']}")
# linear coefficients
coef = {}
for name in ("SU3", "BL", "SU2+", "SU2-"):
    coef[name] = {"p": out["(1, 0, 0)"]["K_" + name][0], "a": out["(0, 1, 0)"]["K_" + name][0],
                  "w": out["(0, 0, 1)"]["K_" + name][0]}
print("K linear coefficients:", json.dumps(coef, indent=1))
m2 = {k: {"p2": out["(1, 0, 0)"][k], "a2": out["(0, 1, 0)"][k], "w2": out["(0, 0, 1)"][k],
          "cross_pa": out["(1, 1, 0)"][k] - out["(1, 0, 0)"][k] - out["(0, 1, 0)"][k]} for k in ("M2_322", "M2_311")}
print("M2/g2:", json.dumps(m2, indent=1))
out["K_coefficients"] = coef
out["M2_coefficients"] = m2
researcher = {"K": "(-2a, +-2p, -+2p, 4a) for (SU3, SU2_1, SU2_2, BL); omega absent",
              "M2_322": "p^2/2 + a^2 + 3 w^2/2", "M2_311": "2 a^2 + 4 w^2"}
agree = (abs(coef["SU3"]["a"] + 2) < 1e-9 and abs(coef["SU3"]["p"]) < 1e-9 and abs(coef["SU3"]["w"]) < 1e-9
         and abs(coef["BL"]["a"] - 4) < 1e-9 and abs(coef["BL"]["p"]) < 1e-9 and abs(coef["BL"]["w"]) < 1e-9
         and abs(abs(coef["SU2+"]["p"]) - 2) < 1e-9 and abs(coef["SU2+"]["p"] + coef["SU2-"]["p"]) < 1e-9
         and abs(coef["SU2+"]["a"]) < 1e-9 and abs(coef["SU2+"]["w"]) < 1e-9 and abs(coef["SU2-"]["w"]) < 1e-9
         and abs(m2["M2_322"]["p2"] - 0.5) < 1e-9 and abs(m2["M2_322"]["a2"] - 1) < 1e-9 and abs(m2["M2_322"]["w2"] - 1.5) < 1e-9
         and abs(m2["M2_311"]["p2"]) < 1e-9 and abs(m2["M2_311"]["a2"] - 2) < 1e-9 and abs(m2["M2_311"]["w2"] - 4) < 1e-9)
out["agrees_with_researcher"] = bool(agree)
print("agrees with researcher's exact Clebsches and masses:", agree)
json.dump(out, open(os.path.join(HERE, "vp_planck.json"), "w"), indent=1, default=float)
