"""g2: full-block (all Sym^2(210) channels) degree-3 multiplier-SOS feasibility SDP for the prototype 210-only
potential at Phi0 = p P + a A:
   h(Phi) (V(Phi) - V0) = sum_kappa sum_{alpha,beta} Q^kappa_{alpha beta} < s_alpha(Phi), s_beta(Phi) >,  Q^kappa >= 0,
   s_alpha = P_kappa( sum_i alpha_i X_i(Phi) )  (the vanishing combinations from g1),  h = h0 + h1 I2, h0 >= 1, h1 >= 0.
The identity is imposed at K random integer points; Gram products are evaluated in float (projections of exact
integer matrices).  Phase 1: residual minimisation (feasibility test).  Phase 2 (if feasible): maximise the
smallest Gram eigenvalue to obtain an interior point for exact rounding (g3)."""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import cvxpy as cp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4g as G

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
KPTS = int(sys.argv[3]) if len(sys.argv) > 3 else 60
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 2024
lab = f"p{P0}_a{A0}"
proto = json.load(open(os.path.join(HERE, f"t1d_exact_prototype_{lab}.json")))
NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
c_q = [Fraction(proto["couplings"][n]) for n in NAMES]
basis = json.load(open(os.path.join(HERE, "g1_basis.json")))["basis"]
van = json.load(open(os.path.join(HERE, f"g1_vanishing_{lab}.json")))
covs = {c.name: c for c in G.all_graph_covariants(3, include_odd=True)}
nb = len(basis)
combos = [("sym", ch, np.array(al, dtype=float)) for ch in G.CHANNELS for al in van["channels"][ch]["alphas"]]
anti_file = os.path.join(HERE, f"g1_vanishing_{lab}_anti.json")
USE_ANTI = os.path.exists(anti_file) and (len(sys.argv) <= 5 or sys.argv[5] != "symonly")
basis_anti = []
if USE_ANTI:
    basis_anti = json.load(open(os.path.join(HERE, "g1_basis_anti.json")))["basis"]
    van_a = json.load(open(anti_file))
    combos += [("anti", ch, np.array(al, dtype=float)) for ch in G.ANTI_CHANNELS for al in van_a["channels"][ch]["alphas"]]
    lab = lab + "_full"
ts_file = os.path.join(HERE, f"g1_vanishing_{lab.replace('_full','')}_ts.json")
USE_TS = USE_ANTI and os.path.exists(ts_file) and (len(sys.argv) <= 6 or sys.argv[6] != "nots")
basis_ts = []
if USE_TS:
    import k4ts as TS
    TS.set_eigenvalues({"8085": -2, "1050t": 4, "945t": 6, "210t": 10})
    basis_ts = json.load(open(os.path.join(HERE, "g1_basis_ts.json")))["basis"]
    van_t = json.load(open(ts_file))
    combos += [("ts", "8085", np.array(al, dtype=float)) for al in van_t["channels"]["8085"]["alphas"]]
    tscovs = {c.name: c for c in TS.all_ts_covariants(3)}
    lab = lab + "3"
names_all = sorted(set(basis) | set(basis_anti))
print("basis", nb, "anti basis", len(basis_anti), "vanishing combinations", len(combos),
      {f"{ch}@{cr}": sum(1 for c in combos if c[0] == cr and c[1] == ch) for (cr, ch, _) in combos}, flush=True)


def V_exact(phi_int):
    vo = np.array([int(x) for x in phi_int], dtype=object)
    inv = K.invariants(vo)
    return sum(c * Fraction(inv[n]) for c, n in zip(c_q, NAMES))


phi0_int = np.array([int(x) for x in K.pao_vector(P0, A0, 0, dtype=object)], dtype=np.int64)
V0 = V_exact(phi0_int)
print("V0 =", V0, float(V0), flush=True)


def project_channel(Y, ch, carrier="sym"):
    if carrier == "ts":
        so_poly, _ = TS.ts_projector(ch)
        acc = float(so_poly[0]) * Y; pw = Y
        for n in range(1, len(so_poly)):
            pw = TS.C_ts(pw)
            if so_poly[n] != 0:
                acc = acc + float(so_poly[n]) * pw
        return acc
    so_poly, gl_poly = (G.PROJ if carrier == "sym" else G.PROJ_ANTI)[ch]
    if len(gl_poly) > 1:
        KY = G.K_gl(Y); KKY = G.K_gl(KY)
        Y = float(gl_poly[0]) * Y + float(gl_poly[1]) * KY + float(gl_poly[2]) * KKY
    acc = float(so_poly[0]) * Y
    pw = Y
    for n in range(1, len(so_poly)):
        pw = G.C_so(pw)
        if so_poly[n] != 0:
            acc = acc + float(so_poly[n]) * pw
    return acc


rng = np.random.default_rng(SEED)
pts = []
while len(pts) < KPTS:
    v = rng.integers(-3, 4, size=210) * (rng.random(210) < 0.35)
    if np.count_nonzero(v) >= 8:
        pts.append(v.astype(np.int64))
nc = len(combos)
chan_of = [f"{c[1]}@{c[0]}" for c in combos]
Gram = np.zeros((KPTS, nc, nc))
Ynorm = np.zeros((KPTS, nc))
rhs = np.zeros(KPTS); I2s = np.zeros(KPTS)
t1 = time.time()
for k, p in enumerate(pts):
    pf = p.astype(float)
    T4 = G.dense4(pf); T6 = G.dense6_fast(G.HODGE @ pf)
    Xraw = {n: covs[n].evaluate(T4, T6) for n in names_all}
    Xst = np.array([Xraw[n] + Xraw[n].T for n in basis])                       # (nb, 210, 210)
    Xan = np.array([Xraw[n] - Xraw[n].T for n in basis_anti]) if basis_anti else None
    assert np.abs(Xst).max() < 2.0 ** 52
    if basis_ts:
        Zst = np.array([TS.sym_traceless(tscovs[n].evaluate(T4, T6)) for n in basis_ts])
        assert np.abs(Zst).max() < 2.0 ** 52
    Ys = [np.tensordot(al, {"sym": Xst, "anti": Xan, "ts": (Zst if basis_ts else None)}[cr], axes=(0, 0)) for cr, ch, al in combos]
    PY = [project_channel(Y, ch, cr) for (cr, ch, al), Y in zip(combos, Ys)]
    for a in range(nc):
        Ynorm[k, a] = np.linalg.norm(PY[a])
        for b in range(nc):
            if chan_of[a] == chan_of[b]:
                Gram[k, a, b] = np.sum(Ys[a] * PY[b])
    rhs[k] = float(V_exact(p) - V0)
    I2s[k] = float(p @ p)
    if k % 10 == 0:
        print(f"  point {k}/{KPTS}", f"[{time.time()-t1:.0f}s]", flush=True)
# symmetrise Gram (tr(Y_a P Y_b) = tr(P Y_a . P Y_b) is symmetric up to float error)
asym = np.abs(Gram - np.transpose(Gram, (0, 2, 1))).max() / np.abs(Gram).max()
print("Gram asymmetry (float):", asym, flush=True)
Gram = 0.5 * (Gram + np.transpose(Gram, (0, 2, 1)))
# power-of-two scaling of each combination so that typical projected norms are O(1)
scale_a = np.array([2.0 ** np.round(np.log2(np.sqrt(np.mean(Ynorm[:, a] ** 2)))) for a in range(nc)])
Gs = Gram / scale_a[None, :, None] / scale_a[None, None, :]
rscale = 2.0 ** np.round(np.log2(np.sqrt(np.mean(rhs ** 2))))
r_s = rhs / rscale
np.savez(os.path.join(HERE, f"g2_data_{lab}_K{KPTS}_s{SEED}.npz"), pts=np.array(pts), Gram=Gram, rhs=rhs, I2s=I2s, scale_a=scale_a,
         rscale=rscale, chan_of=np.array(chan_of), alphas=np.array([al for cr, ch, al in combos], dtype=object), carriers=np.array([cr for cr, ch, al in combos]))
print("data saved", f"[{time.time()-t0:.0f}s]", flush=True)

# ---- SDP phase 1: feasibility by residual minimisation
blocks = {}
for a, ch in enumerate(chan_of):
    blocks.setdefault(ch, []).append(a)
Qs = {ch: cp.Variable((len(idx), len(idx)), PSD=True) for ch, idx in blocks.items()}
h0 = cp.Variable(); h1 = cp.Variable()
cons = [h0 >= 1.0, h1 >= 0.0]
res = []
for k in range(KPTS):
    lhs = (h0 + h1 * I2s[k]) * r_s[k]
    tot = 0
    for ch, idx in blocks.items():
        sub = Gs[k][np.ix_(idx, idx)]
        tot = tot + cp.sum(cp.multiply(Qs[ch], sub))
    res.append(lhs - tot)
res = cp.hstack(res)
prob = cp.Problem(cp.Minimize(cp.norm(res, 2)), cons)
try:
    prob.solve(solver=cp.CLARABEL, max_iter=500)
except Exception as e:
    print("Clarabel failed:", e, flush=True)
    prob.solve(solver=cp.SCS, max_iters=100000, eps=1e-10)
resv = np.asarray(res.value).ravel()
rel = float(np.linalg.norm(resv) / np.linalg.norm((h0.value + h1.value * I2s) * r_s))
out = {"point": [P0, A0], "K": KPTS, "seed": SEED, "n_basis": nb, "n_combos": nc, "blocks": {ch: len(idx) for ch, idx in blocks.items()},
       "phase1_status": prob.status, "phase1_residual_rel": rel, "phase1_residual_max": float(np.abs(resv).max()),
       "h0": float(h0.value), "h1": float(h1.value),
       "Q_eigs": {ch: np.linalg.eigvalsh(Q.value).tolist() for ch, Q in Qs.items()}}
print(json.dumps({k: v for k, v in out.items() if k != "Q_eigs"}, indent=1), flush=True)
print("Q eigenvalues:", {ch: [f"{e:.2e}" for e in v] for ch, v in out["Q_eigs"].items()}, flush=True)
# ---- span test (indefinite Q)
cols = []; keys = []
for ch, idx in blocks.items():
    for ia, a in enumerate(idx):
        for ib, b in enumerate(idx):
            if ib < ia:
                continue
            cols.append(Gs[:, a, b] * (1.0 if a == b else 2.0)); keys.append((ch, a, b))
A = np.column_stack(cols)
x, _, rk, sv = np.linalg.lstsq(np.column_stack([A, -r_s * I2s]), r_s, rcond=None)
span_res = float(np.linalg.norm(np.column_stack([A, -r_s * I2s]) @ x - r_s) / np.linalg.norm(r_s))
out["span_test_residual_free_h1"] = span_res; out["span_rank"] = int(rk); out["span_cols"] = A.shape[1] + 1
print("span test (indefinite):", span_res, "rank", rk, "/", A.shape[1] + 1, flush=True)

# ---- SDP phase 2: interior point (max min eigenvalue) with equality constraints (only if phase 1 feasible)
if rel < 1e-6:
    Qs2 = {ch: cp.Variable((len(idx), len(idx)), symmetric=True) for ch, idx in blocks.items()}
    h1b = cp.Variable(nonneg=True); tt = cp.Variable()
    cons2 = []
    for ch, idx in blocks.items():
        cons2.append(Qs2[ch] - tt * np.eye(len(idx)) >> 0)
        cons2.append(cp.trace(Qs2[ch]) <= 1e3)
    for k in range(KPTS):
        lhs = (1.0 + h1b * I2s[k]) * r_s[k]
        tot = 0
        for ch, idx in blocks.items():
            tot = tot + cp.sum(cp.multiply(Qs2[ch], Gs[k][np.ix_(idx, idx)]))
        cons2.append(lhs == tot)
    prob2 = cp.Problem(cp.Maximize(tt), cons2)
    try:
        prob2.solve(solver=cp.CLARABEL, max_iter=500)
    except Exception as e:
        print("phase 2 Clarabel failed:", e, flush=True)
    out["phase2_status"] = prob2.status
    out["phase2_t_max"] = float(tt.value) if tt.value is not None else None
    out["phase2_h1"] = float(h1b.value) if h1b.value is not None else None
    if tt.value is not None:
        out["phase2_Q"] = {ch: Qs2[ch].value.tolist() for ch in blocks}
        out["phase2_Q_eigs"] = {ch: np.linalg.eigvalsh(Qs2[ch].value).tolist() for ch in blocks}
        print("phase 2: t_max", tt.value, "h1", h1b.value, {ch: [f"{e:.2e}" for e in v] for ch, v in out["phase2_Q_eigs"].items()}, flush=True)
out["elapsed_s"] = time.time() - t0
json.dump(out, open(os.path.join(HERE, f"g2_sdp_{lab}_K{KPTS}_s{SEED}.json"), "w"), indent=1)
