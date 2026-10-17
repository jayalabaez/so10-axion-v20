"""g5: EXACT infeasibility certificate (Farkas dual) for the complete degree-3 multiplier-SOS ansatz.

Primal (g2, all 13 blocks):  (h0 + h1 I2_k) r_k = sum_kappa <Q^kappa, G^kappa(k)>  (k = 1..K points),  Q >= 0, h0 >= 1, h1 >= 0.
Dual ray: w in R^K with  M^kappa(w) := sum_k w_k G^kappa(k) <= 0 for every block,  S1 := sum_k w_k r_k > 0,
S2 := sum_k w_k I2_k r_k >= 0.  Then for any admissible (Q, h):  0 < h0 S1 + h1 S2 = sum_kappa <Q^kappa, M^kappa(w)> <= 0,
a contradiction - so NO certificate of this form exists (the point equations are necessary conditions of the
polynomial identity).  The dual is found numerically (maximal margin t with -M >= t I in the scaled basis) and then
verified EXACTLY: exact rational Gram values at the points (mod-p traces + CRT, as in g3), rational w, exact LDL^T.
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import sympy as sp
import cvxpy as cp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4g as G
import k4ts as TS

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
KPTS = int(sys.argv[3]) if len(sys.argv) > 3 else 60
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 2024
TAG = sys.argv[5] if len(sys.argv) > 5 else "_full3"
NEXACT = int(sys.argv[6]) if len(sys.argv) > 6 else KPTS
lab = f"p{P0}_a{A0}"
TS.set_eigenvalues({"8085": -2, "1050t": 4, "945t": 6, "210t": 10})
proto = json.load(open(os.path.join(HERE, f"t1d_exact_prototype_{lab}.json")))
NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
c_q = [Fraction(proto["couplings"][n]) for n in NAMES]
dat = np.load(os.path.join(HERE, f"g2_data_{lab}{TAG}_K{KPTS}_s{SEED}.npz"), allow_pickle=True)
pts = dat["pts"]; Gram = dat["Gram"]; rhs = dat["rhs"]; I2s = dat["I2s"]; scale_a = dat["scale_a"]; rscale = float(dat["rscale"])
chan_of = [str(c) for c in dat["chan_of"]]; alphas = [np.asarray(a, dtype=float) for a in dat["alphas"]]; carriers = [str(c) for c in dat["carriers"]]
nc = len(chan_of); Kp = len(pts)
blocks = {}
for a, ch in enumerate(chan_of):
    blocks.setdefault(ch, []).append(a)
Gs = Gram / scale_a[None, :, None] / scale_a[None, None, :]
r_s = rhs / rscale
print("blocks", {ch: len(v) for ch, v in blocks.items()}, "points", Kp, flush=True)

# ---------------------------------------------------------------- dual SDP (numerical)
# row scaling: equation k is divided by rho_k = max(|Gs_k|, |r_s_k|) (reparametrisation w_k = u_k / rho_k)
rho = np.array([max(np.abs(Gs[k]).max(), abs(r_s[k]), 1e-300) for k in range(Kp)])
rs_n = r_s / rho; I2rs_n = I2s * r_s / rho
Gn = {ch: np.array([Gs[k][np.ix_(idx, idx)] / rho[k] for k in range(Kp)]) for ch, idx in blocks.items()}


def solve(prob):
    for solver, kw in ((cp.CLARABEL, {"max_iter": 2000}), (cp.SCS, {"max_iters": 100000, "eps": 1e-10})):
        try:
            prob.solve(solver=solver, **kw)
            if prob.value is not None and prob.status in ("optimal", "optimal_inaccurate"):
                return prob.status
        except Exception as e:
            print("solver", solver, "failed:", e, flush=True)
    return prob.status


# stage 1: maximal separation S1 under ||u||_2 <= 1 (value > 0 <=> the sampled primal system is infeasible)
u = cp.Variable(Kp)
cons = [cp.norm(u, 2) <= 1.0, cp.sum(cp.multiply(u, I2rs_n)) >= 0.0]
for ch, idx in blocks.items():
    M = sum(u[k] * Gn[ch][k] for k in range(Kp))
    cons.append(-M >> 0)
prob1 = cp.Problem(cp.Maximize(cp.sum(cp.multiply(u, rs_n))), cons)
st1 = solve(prob1)
s_star = float(prob1.value) if prob1.value is not None else None
print("stage 1: status", st1, "max separation S1 (||u||<=1) =", s_star, "||r_s/rho|| =", float(np.linalg.norm(rs_n)), f"[{time.time()-t0:.0f}s]", flush=True)
# stage 2: strict margin t with S1 >= s*/2
t = cp.Variable(); u2 = cp.Variable(Kp)
cons2 = [cp.norm(u2, 2) <= 1.0, cp.sum(cp.multiply(u2, I2rs_n)) >= 0.0, cp.sum(cp.multiply(u2, rs_n)) >= 0.5 * (s_star if s_star else 0.0)]
for ch, idx in blocks.items():
    M = sum(u2[k] * Gn[ch][k] for k in range(Kp))
    cons2.append(-M - t * np.eye(len(idx)) >> 0)
prob2 = cp.Problem(cp.Maximize(t), cons2)
st2 = solve(prob2)
status = f"stage1:{st1}; stage2:{st2}"
print("stage 2: status", st2, "margin t =", t.value, f"[{time.time()-t0:.0f}s]", flush=True)
if t.value is not None and t.value > 0:
    uv = np.asarray(u2.value).ravel()
else:
    uv = np.asarray(u.value).ravel() if u.value is not None else None
    t.value = 0.0 if uv is not None else None
wv = uv / rho if uv is not None else None
out = {"point": [P0, A0], "K": Kp, "tag": TAG, "dual_status": status, "dual_margin_t": float(t.value) if t.value is not None else None,
       "stage1_separation": s_star}
if wv is None or s_star is None or s_star <= 0:
    print("no separating dual functional found: the sampled primal is (numerically) feasible or the solver failed", flush=True)
    json.dump(out, open(os.path.join(HERE, f"g5_dual_{lab}{TAG}.json"), "w"), indent=1)
    sys.exit(0)
# sanity in float with the UNscaled Grams (congruence by diag(scale) preserves semidefiniteness)
worst = -np.inf
for ch, idx in blocks.items():
    M = sum(wv[k] * Gram[k][np.ix_(idx, idx)] for k in range(Kp))
    Dm = np.diag(scale_a[idx])
    worst = max(worst, np.linalg.eigvalsh(np.linalg.solve(Dm, M) @ np.linalg.inv(Dm)).max())
print("float check: max eigenvalue of scaled M over blocks =", worst, "(should be <= -t =", -t.value, ")", flush=True)

# ---------------------------------------------------------------- exact Grams at the points (mod-p CRT), as in g3
PRIMES = [p for p in [2147483647, 2147483629, 2147483587, 2147483579, 2147483563, 2147483549, 2147483543, 2147483497] if sp.isprime(p)]
MODULUS = 1
for p in PRIMES:
    MODULUS *= p
covs = {c.name: c for c in G.all_graph_covariants(3, include_odd=True)}
tscovs = {c.name: c for c in TS.all_ts_covariants(3)}
basis = json.load(open(os.path.join(HERE, "g1_basis.json")))["basis"]
basis_anti = json.load(open(os.path.join(HERE, "g1_basis_anti.json")))["basis"] if "anti" in carriers else []
basis_ts = json.load(open(os.path.join(HERE, "g1_basis_ts.json")))["basis"] if "ts" in carriers else []
names_all = sorted(set(basis) | set(basis_anti))


def crt(residues):
    x = 0; M = 1
    for r, p in zip(residues, PRIMES):
        tt = ((r - x) * pow(M, -1, p)) % p
        x = x + M * tt; M *= p
    x %= M
    return x - M if x > M // 2 else x


def apply_C_mod(X, p):
    out = np.zeros_like(X)
    for r, c, s in G.GEN_IDX:
        Y = np.zeros_like(X); Y[:, r] = s[None, :] * X[:, c]
        Z = np.zeros_like(X); Z[r, :] = s[:, None] * Y[c, :]
        out += Z
    return out % p


def apply_K_mod(X, p):
    out = np.zeros_like(X)
    for i in range(G.N):
        for j in range(G.N):
            r, c, s = G.RHO_IDX[i][j]
            Y = np.zeros_like(X); Y[:, c] = s[None, :] * X[:, r]
            Z = np.zeros_like(X); Z[r, :] = s[:, None] * Y[c, :]
            out += Z
        out %= p
    return out % p


def tr_mod(A, B, p):
    return int(np.sum((A * B) % p) % p)


def V_exact(phi_int):
    vo = np.array([int(x) for x in phi_int], dtype=object)
    inv = K.invariants(vo)
    return sum(c * Fraction(inv[n]) for c, n in zip(c_q, NAMES))


phi0_int = np.array([int(x) for x in K.pao_vector(P0, A0, 0, dtype=object)], dtype=np.int64)
V0 = V_exact(phi0_int)
pairs = [(a, b) for ch, idx in blocks.items() for ia, a in enumerate(idx) for b in idx[ia:]]
# choose the exact points: the NEXACT points with the largest |w| (the dual may be supported on a subset)
order = np.argsort(-np.abs(wv))[:NEXACT]
use = sorted(int(k) for k in order)
GramX = {}; rhsX = {}; I2X = {}
t1 = time.time()
for ii, k in enumerate(use):
    p_int = pts[k]; pf = p_int.astype(float)
    T4 = G.dense4(pf); T6 = G.dense6_fast(G.HODGE @ pf)
    Xraw = {n: covs[n].evaluate(T4, T6) for n in names_all}
    Xst = np.array([Xraw[n] + Xraw[n].T for n in basis])
    Xan = np.array([Xraw[n] - Xraw[n].T for n in basis_anti]) if basis_anti else None
    Zst = np.array([TS.sym_traceless(tscovs[n].evaluate(T4, T6)) for n in basis_ts]) if basis_ts else None
    Ys = [np.tensordot(alphas[a], {"sym": Xst, "anti": Xan, "ts": Zst}[carriers[a]], axes=(0, 0)) for a in range(nc)]
    for Y in Ys:
        assert np.abs(Y).max() < 2.0 ** 52
    Ynorm = [float(np.linalg.norm(Y)) for Y in Ys]
    bound = max((45.0 ** 7) * (100.0 ** 2), 180.0 ** 3) * max(Ynorm) ** 2
    assert bound < MODULUS / 2.0
    mat_idx = [a for a in range(nc) if carriers[a] != "ts"]; ts_idx = [a for a in range(nc) if carriers[a] == "ts"]
    T = {}
    for p in PRIMES:
        CY = {}; CKY = {}
        for a in mat_idx:
            Y = np.rint(Ys[a]).astype(np.int64) % p
            pw = [Y]
            for _ in range(4):
                pw.append(apply_C_mod(pw[-1], p))
            CY[a] = pw
            KY = apply_K_mod(Y, p); pw2 = [KY]
            for _ in range(4):
                pw2.append(apply_C_mod(pw2[-1], p))
            CKY[a] = pw2
        for a in ts_idx:
            Y2 = (np.rint(Ys[a]).astype(np.int64) % p).reshape(210, 100)
            pw = [Y2]
            for _ in range(2):
                pw.append(TS.C_ts_mod(pw[-1], p))
            CY[a] = pw
        for (a, b) in pairs:
            if carriers[a] == "ts":
                for n in range(4):
                    i_ = min(n, 2); j_ = n - i_
                    T.setdefault((a, b, 0, n), []).append(tr_mod(CY[a][i_], CY[b][j_], p))
                continue
            for n in range(8):
                i_ = min(n, 4); j_ = n - i_
                T.setdefault((a, b, 0, n), []).append(tr_mod(CY[a][i_], CY[b][j_], p))
                T.setdefault((a, b, 1, n), []).append(tr_mod(CY[a][i_], CKY[b][j_], p))
                T.setdefault((a, b, 2, n), []).append(tr_mod(CKY[a][i_], CKY[b][j_], p))
    Tint = {key: crt(res) for key, res in T.items()}
    for (a, b) in pairs:
        chname, cr = chan_of[a].split("@")
        so_poly, gl_poly = TS.ts_projector(chname) if cr == "ts" else (G.PROJ if cr == "sym" else G.PROJ_ANTI)[chname]
        val = Fraction(0)
        for n, pn in enumerate(so_poly):
            if pn == 0:
                continue
            if len(gl_poly) == 1:
                val += pn * Tint[(a, b, 0, n)]
            else:
                val += pn * (gl_poly[0] * Tint[(a, b, 0, n)] + gl_poly[1] * Tint[(a, b, 1, n)] + gl_poly[2] * Tint[(a, b, 2, n)])
        GramX[(k, a, b)] = val
    rhsX[k] = V_exact(p_int) - V0; I2X[k] = Fraction(int(p_int @ p_int))
    if ii % 5 == 0:
        print(f"  exact point {ii}/{len(use)}", f"[{time.time()-t1:.0f}s]", flush=True)
err = max(abs(float(GramX[(k, a, b)]) - Gram[k, a, b]) / max(abs(Gram[k, a, b]), 1.0) for (k, a, b) in GramX)
errr = max(abs(float(rhsX[k]) - rhs[k]) for k in use)
print("exact vs float: Gram max rel dev", err, " rhs max dev", errr, flush=True)
out["float_vs_exact_gram_maxrel"] = err

# ---------------------------------------------------------------- exact verification of the dual ray
DEN = 2 ** 24
wq = {k: Fraction(int(round(wv[k] * DEN)), DEN) for k in use}
S1 = sum(wq[k] * rhsX[k] for k in use)
S2 = sum(wq[k] * I2X[k] * rhsX[k] for k in use)
print("exact S1 =", float(S1), " S2 =", float(S2), flush=True)


def exact_psd_strict(Mf):
    """rational LDL^T; True iff positive definite."""
    n = len(Mf)
    Mf = [row[:] for row in Mf]
    for kk in range(n):
        piv = Mf[kk][kk]
        if piv <= 0:
            return False
        for i in range(kk + 1, n):
            f = Mf[i][kk] / piv
            for j in range(kk, n):
                Mf[i][j] -= f * Mf[kk][j]
    return True


def exact_psd(Mf):
    """rational elimination test for positive SEMIdefiniteness (zero pivot => its row/column must vanish)."""
    n = len(Mf)
    Mf = [row[:] for row in Mf]
    for kk in range(n):
        piv = Mf[kk][kk]
        if piv < 0:
            return False
        if piv == 0:
            if any(Mf[kk][j] != 0 for j in range(n)) or any(Mf[i][kk] != 0 for i in range(n)):
                return False
            continue
        for i in range(kk + 1, n):
            f = Mf[i][kk] / piv
            for j in range(kk, n):
                Mf[i][j] -= f * Mf[kk][j]
    return True


all_ok = True; block_info = {}
tq = Fraction(int(round(float(t.value) * DEN / 2)), DEN) if float(t.value) > 0 else Fraction(0)
for ch, idx in blocks.items():
    n = len(idx)
    M = [[Fraction(0)] * n for _ in range(n)]
    for ia, a in enumerate(idx):
        for ib, b in enumerate(idx):
            key = (a, b) if a <= b else (b, a)
            for k in use:
                M[ia][ib] += wq[k] * GramX[(k,) + key]
    # -M - tq * D^2 must be PSD (D = scale); then -M >= tq D^2 > 0
    negM = [[-M[i][j] - (tq * Fraction(int(scale_a[idx[i]])) ** 2 * Fraction(1) if i == j else 0) for j in range(n)] for i in range(n)]
    ok_strict = exact_psd_strict(negM)
    ok_semi = exact_psd([[-M[i][j] for j in range(n)] for i in range(n)])
    block_info[ch] = {"neg_M_minus_margin_PD": ok_strict, "neg_M_PSD": ok_semi,
                      "float_eigs_of_M": np.linalg.eigvalsh(np.array([[float(x) for x in row] for row in M])).tolist()}
    all_ok &= ok_semi
    print(ch, "-M PSD:", ok_semi, " strict with margin:", ok_strict, flush=True)
verdict = bool(all_ok and S1 > 0 and S2 >= 0)
out.update({"S1": str(S1), "S2": str(S2), "S1_positive": bool(S1 > 0), "S2_nonneg": bool(S2 >= 0), "all_blocks_negM_PSD": bool(all_ok),
            "EXACT_infeasibility_proved": verdict, "n_points_used": len(use), "w_den_bits": 24, "blocks": block_info,
            "w": {int(k): str(wq[k]) for k in use}, "elapsed_s": time.time() - t0})
json.dump(out, open(os.path.join(HERE, f"g5_dual_{lab}{TAG}.json"), "w"), indent=1)
print("EXACT infeasibility of the complete degree-3 multiplier-SOS ansatz proved:", verdict, f"[{time.time()-t0:.0f}s]", flush=True)
