"""g0: validate k4g (graph enumeration counts, pair-operator spectra, projector completeness) and compute the
rank (as maps) of the graph-generated Sym^2(210)-covariants per degree against the exact multiplicities
(constant 1, linear 1, quadratic 10, cubic 29; total 41)."""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4g as G

t0 = time.time()
rng = np.random.default_rng(5)
out = {}
covs = G.all_graph_covariants(3, include_odd=True)
counts = {}
for c in covs:
    counts.setdefault((c.degree, c.parity), 0); counts[(c.degree, c.parity)] += 1
print("graph covariants:", {f"deg{d}_par{p}": n for (d, p), n in counts.items()}, flush=True)
out["graph_counts"] = {f"deg{d}_par{p}": n for (d, p), n in counts.items()}

# ---- operator spectra
X = rng.standard_normal((210, 210)); X = X + X.T
CX = G.C_so(X); KX = G.K_gl(X)
comm = np.linalg.norm(G.C_so(KX) - G.K_gl(CX)) / np.linalg.norm(KX)
print("commutator |[C,K]X|/|KX| =", comm, flush=True)
Y = X.copy()
for c in G.SO_VALUES:
    Y = G.C_so(Y) - c * Y
print("so minimal polynomial residual:", np.linalg.norm(Y) / np.linalg.norm(X), flush=True)
Z = X.copy()
for k in G.GL_VALUES:
    Z = G.K_gl(Z) - k * Z
print("gl minimal polynomial residual:", np.linalg.norm(Z) / np.linalg.norm(X), flush=True)
out["commutator"] = comm; out["so_minpoly_resid"] = float(np.linalg.norm(Y) / np.linalg.norm(X)); out["gl_minpoly_resid"] = float(np.linalg.norm(Z) / np.linalg.norm(X))
P = G.project_all(X)
tot = sum(P.values())
print("sum of projections residual:", np.linalg.norm(tot - X) / np.linalg.norm(X), flush=True)
out["projector_sum_resid"] = float(np.linalg.norm(tot - X) / np.linalg.norm(X))
idem = {}
for ch, PX in P.items():
    PP = G.project_all(PX)
    idem[ch] = float(np.linalg.norm(PP[ch] - PX) / max(np.linalg.norm(PX), 1e-300))
    off = max(np.linalg.norm(PP[c2]) for c2 in G.CHANNELS if c2 != ch) / max(np.linalg.norm(PX), 1e-300)
    idem[ch + "_off"] = float(off)
print("idempotency / orthogonality residuals:", {k: f"{v:.1e}" for k, v in idem.items()}, flush=True)
out["idempotency"] = idem
# stochastic trace estimate of channel dimensions (Hutchinson on symmetric Gaussian matrices)
est = {ch: 0.0 for ch in G.CHANNELS}; ns = 60
for _ in range(ns):
    W = rng.standard_normal((210, 210)); W = (W + W.T) / np.sqrt(2.0)
    PW = G.project_all(W)
    for ch in G.CHANNELS:
        est[ch] += np.sum(W * PW[ch]) / ns
print("stochastic channel dims:", {ch: round(v) for ch, v in est.items()}, "expected", G.CHANNEL_DIM, f"[{time.time()-t0:.0f}s]", flush=True)
out["stochastic_dims"] = {ch: float(v) for ch, v in est.items()}

# ---- evaluate all graph covariants at random points; ranks per degree
NPTS = 3
pts = []
for _ in range(NPTS):
    v = rng.integers(-3, 4, size=210) * (rng.random(210) < 0.35)
    pts.append(v.astype(float))
vals = {c.name: [] for c in covs}
times = {}
for p in pts:
    T4 = G.dense4(p)
    T6 = G.dense6_fast(G.HODGE @ p)
    for c in covs:
        t1 = time.time()
        Xc = c.evaluate(T4, T6)
        times[c.name] = time.time() - t1
        vals[c.name].append(Xc)
print("evaluation done; slowest:", sorted(times.items(), key=lambda kv: -kv[1])[:5], f"[{time.time()-t0:.0f}s]", flush=True)
out["eval_times"] = times


def rank_of(names, part):
    rows = []
    for n in names:
        v = np.concatenate([(X + X.T).ravel() if part == "sym" else (X - X.T).ravel() for X in vals[n]])
        rows.append(v)
    A = np.array(rows)
    if A.shape[0] == 0:
        return 0, []
    sv = np.linalg.svd(A, compute_uv=False)
    rk = int(np.sum(sv > 1e-9 * sv[0])) if sv[0] > 0 else 0
    return rk, sv[:min(len(sv), rk + 2)].tolist()


ranks = {}
for d in range(4):
    for par in (+1, -1):
        names = [c.name for c in covs if c.degree == d and c.parity == par]
        if not names:
            continue
        for part in ("sym", "anti"):
            rk, sv = rank_of(names, part)
            ranks[f"deg{d}_par{par}_{part}"] = rk
    names = [c.name for c in covs if c.degree == d]
    for part in ("sym", "anti"):
        rk, sv = rank_of(names, part)
        ranks[f"deg{d}_all_{part}"] = rk
        print(f"degree {d} {part}: rank {rk} of {len(names)} graphs", flush=True)
names = [c.name for c in covs]
for part in ("sym", "anti"):
    rk, sv = rank_of(names, part)
    ranks[f"total_{part}"] = rk
print("ranks:", ranks, flush=True)
out["ranks"] = ranks
out["expected_sym"] = {"deg0": 1, "deg1": 1, "deg2": 10, "deg3": 29, "total": 41}
out["elapsed_s"] = time.time() - t0
json.dump(out, open(os.path.join(HERE, "g0_test.json"), "w"), indent=1, default=str)
