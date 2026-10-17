"""g6: which isotypic components of Sym^3(210) does the vector v = Phi0 (x) Phi0 (x) Phi0 have?
For a block lambda of multiplicity ONE in Sym^3(210) the unique cubic covariant into lambda vanishes at Phi0 iff v has
no lambda-component.  The triple Casimir C3 = sum_A (T_A(x)1(x)1 + 1(x)T_A(x)1 + 1(x)1(x)T_A)^2 acts on v with eigenvalue
-C2(lambda) on the lambda-isotypic component; plain Lanczos (3-term recurrence, 210^3 dense float64 tensors) gives the
Ritz values, which converge to exactly the eigenvalues present in v.  Spurious (ghost) copies may appear, but the SET of
values is reliable once converged; we report the distinct converged values and compare with the C2 list of Sym^3(210).
C2 values: 1:0 45:16 54:20 210:24 945:32 770/1050:36 1386:40 5940:44 4125/8085:48 6930:52 8910:56 17920:58 7644:60
23040:62 72765/73710:68 50688:74 128700:76 189189:80 210210:81 165165:90."""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4g as G

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
NIT = int(sys.argv[3]) if len(sys.argv) > 3 else 70
phi0 = K.pao_vector(P0, A0, 0)
v = np.einsum("a,b,c->abc", phi0, phi0, phi0)
v /= np.linalg.norm(v)
IDX = G.GEN_IDX    # (rows, cols, signs) per generator: (T X)[r] = s X[c]


def slot(X, a, k):
    """apply generator a on tensor slot k (k = 0,1,2)."""
    r, c, s = IDX[a]
    out = np.zeros_like(X)
    if k == 0:
        out[r, :, :] = s[:, None, None] * X[c, :, :]
    elif k == 1:
        out[:, r, :] = s[None, :, None] * X[:, c, :]
    else:
        out[:, :, r] = s[None, None, :] * X[:, :, c]
    return out


def C3(X):
    """sum_A (T_A^(0) + T_A^(1) + T_A^(2))^2 X = -72 X + 2 sum_A sum_{i<j} T_A^(i) T_A^(j) X   (sum_A T_A^2 = -24 on each slot)."""
    acc = np.zeros_like(X)
    for a in range(45):
        w0 = slot(X, a, 0); w1 = slot(X, a, 1); w2 = slot(X, a, 2)
        acc += slot(w1, a, 0) + slot(w2, a, 0) + slot(w2, a, 1)
    return -72.0 * X + 2.0 * acc


# sanity: C3 on a pure product of a random vector with itself should respect the Sym^3 spectrum; check self-adjointness
rng = np.random.default_rng(1)
x = rng.standard_normal((210, 210, 210)); y = rng.standard_normal((210, 210, 210))
sa = abs(np.sum(x * C3(y)) - np.sum(C3(x) * y)) / (np.linalg.norm(x) * np.linalg.norm(y))
print("self-adjointness residual", sa, f"[{time.time()-t0:.0f}s]", flush=True)
del x, y
# Lanczos
alphas = []; betas = []
q_prev = np.zeros_like(v); q = v.copy(); beta = 0.0
ritz_hist = []
for it in range(NIT):
    w = C3(q)
    alpha = float(np.sum(w * q))
    w -= alpha * q + beta * q_prev
    beta_new = float(np.linalg.norm(w))
    alphas.append(alpha); betas.append(beta_new)
    T = np.diag(alphas) + np.diag(betas[:-1], 1) + np.diag(betas[:-1], -1)
    ritz = np.linalg.eigvalsh(T)
    if it % 5 == 4 or beta_new < 1e-8:
        print(f"it {it+1}: beta {beta_new:.3e}; distinct Ritz values (as C2 = -eig):",
              sorted(set(np.round(-ritz, 2))), f"[{time.time()-t0:.0f}s]", flush=True)
    if beta_new < 1e-8:
        break
    q_prev = q; q = w / beta_new; beta = beta_new
T = np.diag(alphas) + np.diag(betas[:-1], 1) + np.diag(betas[:-1], -1)
ritz = -np.linalg.eigvalsh(T)
C2 = {"1": 0, "45": 16, "54": 20, "210": 24, "945": 32, "770|1050": 36, "1386": 40, "5940": 44, "4125|8085": 48, "6930": 52,
      "8910": 56, "17920": 58, "7644": 60, "23040": 62, "72765|73710": 68, "50688": 74, "128700": 76, "189189": 80, "210210": 81, "165165": 90}
present = {name: bool(np.min(np.abs(ritz - val)) < 0.05) for name, val in C2.items()}
# Ritz-vector weights: component of v along each Ritz value (first component of eigenvectors squared)
evals, evecs = np.linalg.eigh(T)
weights = {}
for name, val in C2.items():
    sel = np.abs(-evals - val) < 0.05
    weights[name] = float(np.sum(evecs[0, sel] ** 2))
print("present (Ritz value within 0.05):", present, flush=True)
print("weights |P_lambda v|^2 (Ritz):", {k: round(w_, 6) for k, w_ in weights.items()}, flush=True)
out = {"point": [P0, A0], "iterations": len(alphas), "final_beta": betas[-1], "ritz_C2_values": sorted(np.round(ritz, 4).tolist()),
       "present": present, "weights": weights, "self_adjointness_residual": sa, "elapsed_s": time.time() - t0}
json.dump(out, open(os.path.join(HERE, f"g6_lanczos_p{P0}_a{A0}.json"), "w"), indent=1)
