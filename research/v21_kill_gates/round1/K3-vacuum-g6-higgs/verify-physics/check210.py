"""Validate v210: generators, pair Casimir vs repo, analytic Hessians vs 5-point finite differences, span of the
repo's O48/O17/O07 rows at A45 inside my invariant space, G3221 decomposition of the 210."""
from __future__ import annotations
import sys, time, json
import numpy as np
sys.path.insert(0, r"C:\Users\jayal\Downloads\So10Theory2\So10Theory\_g6_nogo")
HERE = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K3-vacuum-g6-higgs"
sys.path.insert(0, HERE + r"\verify-physics")
import v210 as V

t0 = time.time()
G = V.generators()
# antisymmetry and a commutator check: [L_01, L_12] = -L_02 ? (convention check only; we print the sign)
for T in G[:5]:
    assert abs((T + T.T)).max() < 1e-12
L01, L12, L02 = G[V.POS2[(0, 1)]], G[V.POS2[(1, 2)]], G[V.POS2[(0, 2)]]
comm = (L01 @ L12 - L12 @ L01).toarray()
sgn = np.sign(np.sum(comm * L02.toarray())) if np.abs(comm).max() > 0 else 0
print("commutator [L01,L12] = %+d L02, residual %.1e" % (sgn, np.abs(comm - sgn * L02.toarray()).max()))
# Casimir of the 210 under SO(10): -sum T^2 should be a multiple of the identity (C2(210) with L normalisation)
Cas = sum((-(T @ T)).toarray() for T in G)
print("SO(10) Casimir on 210: diag spread %.1e, value %.6f" % (np.ptp(np.diag(Cas)), Cas[0, 0]), "offdiag max %.1e" % np.abs(Cas - np.diag(np.diag(Cas))).max())
K = V.pair_casimir()
print("K nnz", K.nnz, "time %.1fs" % (time.time() - t0))
# compare with the repo's pair Casimir on a random vector
import exact_210_pati_salam_global_vacuum_v20 as repo210
Kr = repo210.pair_casimir_sparse()
rng = np.random.default_rng(1)
v = rng.normal(size=210 * 210)
a, b = K @ v, Kr @ v
ratio = (a @ b) / (b @ b)
print("my K vs repo K: ratio %.6f, residual %.2e" % (ratio, np.linalg.norm(a - ratio * b) / np.linalg.norm(a)))

# finite-difference validation of gradients/Hessians at a random phi
phi = rng.normal(size=210); phi /= np.linalg.norm(phi)
vals = V.all_values(phi); grads = V.all_gradients(phi); hess = V.all_hessians(phi)
h = 1e-2
u = rng.normal(size=210); u /= np.linalg.norm(u)
w = rng.normal(size=210); w /= np.linalg.norm(w)
def fd1(f, x, d, h):
    return (-f(x + 2 * h * d) + 8 * f(x + h * d) - 8 * f(x - h * d) + f(x - 2 * h * d)) / (12 * h)
for name in V.NAMES:
    f = lambda x, n=name: V.all_values(x)[n]
    gfd = fd1(f, phi, u, h)
    gan = grads[name] @ u
    # Hessian: directional derivative of the gradient along w
    gw = lambda x, n=name: V.all_gradients(x)[n] @ u
    hfd = fd1(gw, phi, w, h)
    han = u @ hess[name] @ w
    print(f"{name}: value {vals[name]: .6e}  grad.u an {gan: .6e} fd {gfd: .6e}  |diff| {abs(gan-gfd):.1e}   uHw an {han: .6e} fd {hfd: .6e} |diff| {abs(han-hfd):.1e}")

# rank of the quartic invariant space (values at random points)
pts = [rng.normal(size=210) for _ in range(12)]
M = np.array([[V.all_values(p)[n] for n in ("J0", "J2", "J3", "J4")] for p in pts])
print("rank of {J0,J2,J3,J4} values on 12 random points:", np.linalg.matrix_rank(M, tol=1e-9 * np.abs(M).max()), " singular values", np.linalg.svd(M, compute_uv=False))

# repo rows at A45: Phi-only parameters O07, O17, O48_B01..B04 lie in my span?
Z = np.load(HERE + r"\A45_rows.npz")
ids = [str(x) for x in Z["ids"]]
phiA45 = Z["q"][:210]
F = V.singlet_forms()
print("A45 q phi-block vs my (p+a)/sqrt2: residual %.2e" % np.linalg.norm(phiA45 - (F["p"] + F["a"]) / np.sqrt(2)), " |q_phi| =", np.linalg.norm(phiA45))
Hm = V.all_hessians(phiA45)
mine = np.array([Hm[n].ravel() for n in V.NAMES])
for pid in ("lambda::O07_B01_Phi_norm", "lambda::O17_B01_Phi_cubic", "lambda::O48_B01_Phi_self_quartics", "lambda::O48_B02_Phi_self_quartics", "lambda::O48_B03_Phi_self_quartics", "lambda::O48_B04_Phi_self_quartics"):
    k = ids.index(pid)
    Hr = Z["hess"][k]
    off = np.abs(Hr[210:, :]).max()
    Hp = Hr[:210, :210]
    coef, res, _, _ = np.linalg.lstsq(mine.T, Hp.ravel(), rcond=None)
    rel = np.linalg.norm(mine.T @ coef - Hp.ravel()) / np.linalg.norm(Hp)
    print(f"{pid}: off-Phi max {off:.1e}; in my span: rel residual {rel:.2e}; coefficients on (I2,I3,J0,J2,J3,J4) = {np.round(coef, 8)}")

# G3221 decomposition of the 210
gens = V.g3221_generators()
cas = V.casimirs(gens)
# check all 15 generators commute with the full SO(10) Casimir structure trivially; check they annihilate p and a
for key, lst in gens.items():
    print(key, "max |T p|, |T a|, |T omega|:", max(np.abs(T @ F["p"]).max() for T in lst), max(np.abs(T @ F["a"]).max() for T in lst), max(np.abs(T @ F["omega"]).max() for T in lst))
blocks = V.isotypic_blocks(cas)
tot = 0
for lab, B in sorted(blocks, key=lambda t: (-t[1].shape[1], t[0])):
    print("  block", V.irrep_name(lab), "dim", B.shape[1])
    tot += B.shape[1]
print("total dim", tot, "n blocks", len(blocks))
# Goldstone rank at theta = 45 deg and at 0, 90
for th in (0.0, 45.0, 90.0, -45.0):
    p = np.cos(np.radians(th)) * F["p"] + np.sin(np.radians(th)) * F["a"]
    Gm = V.goldstone_matrix(p)
    print("theta", th, "Goldstone rank", np.linalg.matrix_rank(Gm, tol=1e-9))
print("done %.1fs" % (time.time() - t0))
