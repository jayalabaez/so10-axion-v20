"""t2: EXACT degree-2 (quadric) ideal of the SO(10) orbit of Phi0 = p P + a A (+ w W) and the
flat-mode count of any degree-2 SOS certificate.

Theory (see REPORT): a degree-<=2 polynomial vanishes on the orbit O = G.Phi0 iff it lies in
  I_2(O) = span{ I2 - v^2 }  (+)  sum over pair-Casimir channels kappa with P_kappa(Phi0 x Phi0) = 0 of V_kappa^*
         (+) [210-isotypic combination  grad I3(Phi) - c Phi  iff grad I3(Phi0) is parallel to Phi0].
The gradient span W_2 of I_2(O) at Phi0 bounds the rank of the Hessian of any SOS-of-quadrics certificate:
  flat modes = (210 - dim orbit) - dim W_2.
This script evaluates each ingredient exactly (integers / Fractions) for several (p,a,w) points.
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo"
sys.path.insert(0, HERE); sys.path.insert(0, REPO)
import k4lib as K
import exact_210_self_invariant_basis_v20 as self210
import exact_phisigma_casimir_projectors_v20 as proj
import sympy as sp

t0 = time.time()
CHANNEL_DIMS = {"1": 1, "45": 45, "54": 54, "210": 210, "770_plus_1050_plus_1050bar": 2870, "4125": 4125, "5940": 5940, "8910": 8910}
assert sum(CHANNEL_DIMS.values()) == 22155


def channel_values(vec_int):
    moments = self210.integer_pair_moments(np.asarray(vec_int, dtype=np.int64))
    vals = {}
    for name, eig in proj.SPECTRAL_EIGENVALUES.items():
        poly = proj.projector_polynomial(eig)
        vals[name] = sum(Fraction(poly[d]) * moments[d] for d in range(8))
    return vals, moments


def grad_I3_exact(vo):
    """grad I3 = 3 LA^T vec(A^2) (exact object arithmetic)."""
    A = K.A_matrix(vo)
    A2 = A.dot(A)
    return 3 * K.A_to_phi_dual(A2)


def exact_normal_basis(vo):
    """exact rational basis of the normal space N = (tangent space)^perp."""
    tans = K.exact_tangent_matrix(vo)
    T = sp.Matrix([[int(x) for x in t] for t in tans])     # 45 x 210, rows = tangents
    ns = T.nullspace()                                     # vectors orthogonal to all tangents
    return T, ns


out = {}
for (p, a, w) in [(2, 1, 0), (1, 1, 0), (3, 1, 0), (1, 2, 0), (0, 1, 0), (1, 0, 0), (2, 1, 1), (0, 1, 1), (0, 0, 1)]:
    lab = f"p{p}_a{a}_w{w}"
    vo = K.pao_vector(p, a, w, dtype=object)
    vi = np.array([int(x) for x in vo])
    vals, moments = channel_values(vi)
    I2 = int(vi @ vi)
    assert sum(vals.values()) == Fraction(I2 * I2), "channels must sum to I2^2"
    vanishing = [n for n, v in vals.items() if v == 0]
    g3 = grad_I3_exact(vo)
    # parallel test: rank of [phi0 ; grad I3]
    Mpar = sp.Matrix([[int(x) for x in vi], [int(x) for x in g3]])
    parallel = Mpar.rank() <= 1
    T, ns = exact_normal_basis(vo)
    orbit_dim = T.rank()
    normal_dim = 210 - orbit_dim
    assert len(ns) == normal_dim
    # gradient span W_2: radial (phi0) + vanishing channel contributions + 210-combination contribution
    grads = [sp.Matrix([int(x) for x in vi])]          # grad(I2 - v^2) = 2 phi0
    details = {}
    if parallel and any(x != 0 for x in g3):
        # quadrics q_I = (grad I3)_I - c Phi_I ; gradient map xi -> d(grad I3)[xi] - c xi = 6 LA^T vec(A0 * A(xi)) sym - c xi
        c = None
        for i in range(210):
            if vi[i] != 0:
                c = Fraction(int(g3[i]), int(vi[i])); break
        A0 = K.A_matrix(vo)
        cols = []
        for j in range(210):
            e = np.zeros(210, dtype=object); e[:] = 0; e[j] = 1
            Ae = K.A_matrix(e)
            prod = A0.dot(Ae) + Ae.dot(A0)
            col = 3 * K.A_to_phi_dual(prod)
            col = [Fraction(int(x)) - c * (1 if i == j else 0) for i, x in enumerate(col)]
            cols.append(col)
        Jm = sp.Matrix(cols).T   # 210 x 210: column j = gradient of q_j
        rk = Jm.rank()
        details["210_combination_gradient_rank_total"] = rk
        # restrict to normal space: gradient of q_j are vectors; their span intersect/project: we need span of the
        # gradients (as functionals) restricted to N.  rank of Nbasis^T Jm
        Nb = sp.Matrix.hstack(*ns)   # 210 x normal_dim
        rkN = (Nb.T * Jm).rank()
        details["210_combination_gradient_rank_on_N"] = rkN
        for j in range(210):
            grads.append(Jm[:, j])
    for n in vanishing:
        details[f"vanishing_channel_{n}"] = CHANNEL_DIMS[n]
    # vanishing channels: gradient map xi -> P_kappa(phi0 (x) xi) has rank <= dim V_kappa; we bound W_2 by adding dim V_kappa
    Wb = sp.Matrix.hstack(*grads)
    Nb = sp.Matrix.hstack(*ns)
    W2_explicit = (Nb.T * Wb).rank()
    W2_bound = W2_explicit + sum(CHANNEL_DIMS[n] for n in vanishing)
    out[lab] = {
        "I2": I2, "channel_values": {n: str(v) for n, v in vals.items()}, "vanishing_channels": vanishing,
        "grad_I3_parallel_to_phi0": bool(parallel), "grad_I3_nonzero": bool(any(x != 0 for x in g3)),
        "orbit_dim": orbit_dim, "normal_dim": normal_dim,
        "W2_explicit_rank_on_N": int(W2_explicit), "W2_upper_bound": int(min(W2_bound, normal_dim)),
        "flat_modes_min": int(normal_dim - min(W2_bound, normal_dim)), "flat_modes_if_no_vanishing_channels": int(normal_dim - W2_explicit),
        "details": details,
    }
    print(lab, json.dumps({k: v for k, v in out[lab].items() if k != "channel_values"}), f"[{time.time() - t0:.0f}s]", flush=True)
out["elapsed_s"] = time.time() - t0
json.dump(out, open(os.path.join(HERE, "t2_degree2_channels.json"), "w"), indent=1)
