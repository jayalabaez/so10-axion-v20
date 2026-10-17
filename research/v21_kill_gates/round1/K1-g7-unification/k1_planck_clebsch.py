#!/usr/bin/env python3
"""Exact Clebsches of the Planck gauge-kinetic operator (c/(4 M_Pl)) Phi_{abcd} F^{ab} F^{cd} for the G3221 orientation
of the 210, and the heavy gauge-boson masses in terms of the 210 vev components (p, a, omega).

Conventions: SO(10) vector indices 1..10; SO(6) on 1..6 (SU(3) x U(1)_{B-L} = U(3) preserving z_k = x_{2k-1} + i x_{2k}),
SO(4) on 7..10 = SU(2)_1 (self-dual) x SU(2)_2 (anti-self-dual).  210 = real 4-form, canonical kinetic term
(1/2) sum_{a<b<c<d} (d Phi_{abcd})^2.  Generators t^A real antisymmetric, normalised sum_{ij} (t^A_ij)^2 = 1 (T(10) = 1,
the repository's index normalisation).  Vev: p = Phi_{7 8 9 10}, a = Phi_{1234} = Phi_{1256} = Phi_{3456},
omega = Phi_{1278} = Phi_{3478} = Phi_{5678} = Phi_{1 2 9 10} = Phi_{3 4 9 10} = Phi_{5 6 9 10}.
Gauge-boson masses: M^2_{AB} = g^2 (t^A Phi).(t^B Phi).  Planck operator with canonical F: alpha_i^-1 -> alpha_U^-1 (1 + c K_i/M_Pl),
K_i = sum_{abcd} Phi_{abcd} t^A_{ab} t^A_{cd} for any normalised generator A of factor i (checked to be A-independent).
"""
from __future__ import annotations

import itertools
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 10


def Tab(a: int, b: int) -> np.ndarray:
    m = np.zeros((N, N))
    m[a, b], m[b, a] = 1.0, -1.0
    return m


def normalise(t: np.ndarray) -> np.ndarray:
    return t / math.sqrt(np.sum(t * t))


def act(t: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """Infinitesimal action of the generator t on the 4-form phi (all four indices)."""
    return (np.einsum("ae,ebcd->abcd", t, phi) + np.einsum("be,aecd->abcd", t, phi)
            + np.einsum("ce,abed->abcd", t, phi) + np.einsum("de,abce->abcd", t, phi))


def four_form(components: dict[tuple[int, int, int, int], float]) -> np.ndarray:
    phi = np.zeros((N, N, N, N))
    for idx, val in components.items():
        for perm in itertools.permutations(range(4)):
            sign = np.linalg.det(np.eye(4)[list(perm)])
            phi[tuple(idx[k] for k in perm)] = sign * val
    return phi


def norm2(phi: np.ndarray) -> float:
    return float(np.sum(phi * phi) / 24.0)  # sum over a<b<c<d


def u3_generator(h: np.ndarray) -> np.ndarray:
    """Real 6x6 antisymmetric matrix of the u(3) element i h (h Hermitian 3x3) on (x1..x6), z_k = x_{2k-1} + i x_{2k}."""
    a = 1j * h
    R = np.zeros((N, N))
    for k in range(3):
        for l in range(3):
            re, im = a[k, l].real, a[k, l].imag
            R[2 * k, 2 * l] += re
            R[2 * k, 2 * l + 1] += -im
            R[2 * k + 1, 2 * l] += im
            R[2 * k + 1, 2 * l + 1] += re
    assert np.allclose(R, -R.T)
    return R


# Gell-Mann matrices
GM = [np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex),
      np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]]),
      np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex),
      np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=complex),
      np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]]),
      np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=complex),
      np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]]),
      np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=complex) / math.sqrt(3)]

gens = {}
gens["SU3"] = [normalise(u3_generator(g / 2)) for g in GM]
gens["BL"] = [normalise(u3_generator(np.eye(3)))]  # proportional to T12 + T34 + T56
gens["SU2_1"] = [normalise(Tab(6, 7) + Tab(8, 9)), normalise(Tab(6, 8) - Tab(7, 9)), normalise(Tab(6, 9) + Tab(7, 8))]
gens["SU2_2"] = [normalise(Tab(6, 7) - Tab(8, 9)), normalise(Tab(6, 8) + Tab(7, 9)), normalise(Tab(6, 9) - Tab(7, 8))]
# full orthonormal basis of so(10)
basis = [normalise(Tab(a, b)) for a in range(N) for b in range(a + 1, N)]


def K_values(phi: np.ndarray) -> dict[str, list[float]]:
    out = {}
    for name, gl in gens.items():
        out[name] = [float(np.einsum("abcd,ab,cd->", phi, t, t)) for t in gl]
    return out


def mass_spectrum(phi: np.ndarray) -> dict:
    """M^2/g^2 eigenvalues (sorted) and the masses of the (3,2,2) and (3,1,1) generators."""
    vecs = [act(t, phi).reshape(-1) / math.sqrt(24.0) for t in basis]
    M2 = np.array([[v.dot(w) for w in vecs] for v in vecs])
    ev = np.sort(np.linalg.eigvalsh(M2))
    # unbroken generators: those with t phi = 0
    unbroken = int(np.sum(ev < 1e-10 * max(1.0, ev[-1])))
    return {"eigenvalues_over_g2": ev.tolist(), "n_unbroken": unbroken, "n_broken": 45 - unbroken}


def analyse(p: float, a: float, w: float) -> dict:
    comps = {(6, 7, 8, 9): p, (0, 1, 2, 3): a, (0, 1, 4, 5): a, (2, 3, 4, 5): a,
             (0, 1, 6, 7): w, (2, 3, 6, 7): w, (4, 5, 6, 7): w, (0, 1, 8, 9): w, (2, 3, 8, 9): w, (4, 5, 8, 9): w}
    phi = four_form(comps)
    n2 = norm2(phi)
    K = K_values(phi)
    spec = mass_spectrum(phi)
    # invariance check of the vev under each factor
    inv = {name: max(float(np.max(np.abs(act(t, phi)))) for t in gl) for name, gl in gens.items()}
    return {"p": p, "a": a, "omega": w, "norm2": n2, "norm2_expected": p * p + 3 * a * a + 6 * w * w, "K": K,
            "invariance_max_abs": inv, "spectrum": spec}


def mass_of(phi: np.ndarray, t: np.ndarray) -> float:
    v = act(t, phi).reshape(-1) / math.sqrt(24.0)
    return float(v.dot(v))


results = {}
# the (3,2,2) and (3,1,1) generators: (3,1,1)_{4/3} ~ complex-structure-breaking SO(6) generators, e.g. T13 - T24 type;
# (3,2,2) ~ mixed SO(6)-SO(4) generators, e.g. T17.
t311 = normalise(Tab(0, 2) - Tab(1, 3))  # in so(6) but not in u(3): check it is orthogonal to all u(3) generators
t322 = normalise(Tab(0, 6))
for name in ("SU3", "BL"):
    for t in gens[name]:
        assert abs(np.sum(t * t311)) < 1e-12, "t311 not orthogonal to u(3)"
for pa in [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (1.0, -1.0, 0.0), (1.0, 0.5, 0.0), (1.0, 2.0, 0.0),
           (1.0, -0.5, 0.0), (1.0, -2.0, 0.0), (0.0, 0.0, 1.0), (1.0, 1.0, 1.0)]:
    r = analyse(*pa)
    phi = four_form({(6, 7, 8, 9): pa[0], (0, 1, 2, 3): pa[1], (0, 1, 4, 5): pa[1], (2, 3, 4, 5): pa[1],
                     (0, 1, 6, 7): pa[2], (2, 3, 6, 7): pa[2], (4, 5, 6, 7): pa[2], (0, 1, 8, 9): pa[2],
                     (2, 3, 8, 9): pa[2], (4, 5, 8, 9): pa[2]})
    r["M2_over_g2_(3,2,2)"] = mass_of(phi, t322)
    r["M2_over_g2_(3,1,1)"] = mass_of(phi, t311)
    results[str(pa)] = r
    print(f"(p,a,w)={pa}: norm2={r['norm2']:.4f} unbroken={r['spectrum']['n_unbroken']} K={ {k: [round(x, 6) for x in v] for k, v in r['K'].items()} } "
          f"M2(322)/g2={r['M2_over_g2_(3,2,2)']:.4f} M2(311)/g2={r['M2_over_g2_(3,1,1)']:.4f} inv={ {k: round(v, 12) for k, v in r['invariance_max_abs'].items()} }")

# Exact symbolic form: K is linear in (p, a, omega); extract coefficients per factor.
coef = {}
for name in gens:
    kp = results[str((1.0, 0.0, 0.0))]["K"][name][0]
    ka = results[str((0.0, 1.0, 0.0))]["K"][name][0]
    kw = results[str((0.0, 0.0, 1.0))]["K"][name][0]
    coef[name] = {"p": kp, "a": ka, "omega": kw}
print("K_i = kp p + ka a + kw omega:", json.dumps(coef, indent=1))
m2 = {"(3,2,2)": {}, "(3,1,1)": {}}
for key, lab in (("M2_over_g2_(3,2,2)", "(3,2,2)"), ("M2_over_g2_(3,1,1)", "(3,1,1)")):
    m2[lab] = {"p^2": results[str((1.0, 0.0, 0.0))][key], "a^2": results[str((0.0, 1.0, 0.0))][key],
               "omega^2": results[str((0.0, 0.0, 1.0))][key],
               "p a cross (from (1,1,0) minus squares)": results[str((1.0, 1.0, 0.0))][key] - results[str((1.0, 0.0, 0.0))][key] - results[str((0.0, 1.0, 0.0))][key]}
print("M^2/g^2:", json.dumps(m2, indent=1))
with open(os.path.join(HERE, "k1_planck_clebsch.json"), "w") as fh:
    json.dump({"results": results, "K_linear_coefficients": coef, "M2_over_g2": m2}, fh, indent=1)
