"""g3: exact rounding and deterministic verification of the degree-3 multiplier-SOS certificate found by g2.

  (1 + h1 I2(Phi)) (V(Phi) - V0) = sum_kappa sum_{a,b} Q^kappa_ab < P_kappa Y_a(Phi), P_kappa Y_b(Phi) >,   Q^kappa >= 0,
  Y_a(Phi) = sum_i alpha^a_i X_i(Phi)  (vanishing combinations of g1; X_i the 41 graph covariants).

Exact ingredients at K integer points (the g2 points):
  * Y_a(Phi_k): exact integers (float64 einsum of small integers, bound-checked);
  * Gram products tr(Y_a P_kappa Y_b) = sum_n p_n [ tr(Y_a C^n Y_b), tr(Y_a C^n K Y_b), tr(Y_a C^n K^2 Y_b) ]:
    the integer traces are computed modulo several 31-bit primes (int64 arithmetic) and reconstructed by CRT;
    rigorous because |tr(A B)| <= |A|_F |B|_F and |C X|_F <= 45 |X|_F, |K X|_F <= 100 |X|_F give an a-priori bound
    below half the product of the primes (checked);
  * V(Phi_k) - V0 and I2(Phi_k): exact rationals (k4lib object arithmetic).
Rounding: the numerical (Q, h1) of g2 phase 2 is rationalised and projected exactly onto the affine identity
subspace; PSD-ness is then checked by exact rational LDL^T.  Deterministic identity proof: both sides are SO(10)
invariants of degree <= 6 (a 30-dimensional space); if 30 known invariants have exact rank 30 on the points, the
exact agreement at the points is a polynomial identity.
"""
import json, os, sys, time
from fractions import Fraction
import numpy as np
import sympy as sp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import k4lib as K
import k4g as G

t0 = time.time()
P0, A0 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (3, 2)
KPTS = int(sys.argv[3]) if len(sys.argv) > 3 else 60
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 2024
DEN_BITS = int(sys.argv[5]) if len(sys.argv) > 5 else 24
lab = f"p{P0}_a{A0}"
proto = json.load(open(os.path.join(HERE, f"t1d_exact_prototype_{lab}.json")))
NAMES = ("I2", "I3", "Ja", "Jb", "Jc", "Je")
c_q = [Fraction(proto["couplings"][n]) for n in NAMES]
basis = json.load(open(os.path.join(HERE, "g1_basis.json")))["basis"]
FULL = len(sys.argv) <= 6 or sys.argv[6] != "symonly"
WITH_TS = FULL and (len(sys.argv) <= 7 or sys.argv[7] != "nots") and os.path.exists(os.path.join(HERE, f"g1_vanishing_{lab}_ts.json"))
lab2 = lab + ("_full" if FULL else "") + ("3" if WITH_TS else "")
basis_anti = json.load(open(os.path.join(HERE, "g1_basis_anti.json")))["basis"] if FULL else []
basis_ts = json.load(open(os.path.join(HERE, "g1_basis_ts.json")))["basis"] if WITH_TS else []
if WITH_TS:
    import k4ts as TS
    TS.set_eigenvalues({"8085": -2, "1050t": 4, "945t": 6, "210t": 10})
    tscovs = {c.name: c for c in TS.all_ts_covariants(3)}
g2 = json.load(open(os.path.join(HERE, f"g2_sdp_{lab2}_K{KPTS}_s{SEED}.json")))
dat = np.load(os.path.join(HERE, f"g2_data_{lab2}_K{KPTS}_s{SEED}.npz"), allow_pickle=True)
pts = dat["pts"]; scale_a = dat["scale_a"]; rscale = float(dat["rscale"]); chan_of = [str(c) for c in dat["chan_of"]]
alphas = [np.asarray(a, dtype=float) for a in dat["alphas"]]
carriers = [str(c) for c in dat["carriers"]]
covs = {c.name: c for c in G.all_graph_covariants(3, include_odd=True)}
nb = len(basis); nc = len(chan_of)
names_all = sorted(set(basis) | set(basis_anti))
blocks = {}
for a, ch in enumerate(chan_of):
    blocks.setdefault(str(ch), []).append(a)
print("combos", nc, "blocks", {ch: len(v) for ch, v in blocks.items()}, flush=True)

PRIMES = [2147483647, 2147483629, 2147483587, 2147483579, 2147483563, 2147483549, 2147483543, 2147483497]
PRIMES = [p for p in PRIMES if sp.isprime(p)]
assert len(PRIMES) >= 7
MODULUS = 1
for p in PRIMES:
    MODULUS *= p


def crt(residues):
    """symmetric-range CRT."""
    x = 0; M = 1
    for r, p in zip(residues, PRIMES):
        # solve x' = x mod M, x' = r mod p
        t = ((r - x) * pow(M, -1, p)) % p
        x = x + M * t; M *= p
    x %= M
    if x > M // 2:
        x -= M
    return x


def apply_C_mod(X, p):
    out = np.zeros_like(X)
    for r, c, s in G.GEN_IDX:
        Y = np.zeros_like(X); Y[:, r] = s[None, :] * X[:, c]      # X g^T
        Z = np.zeros_like(X); Z[r, :] = s[:, None] * Y[c, :]      # g X g^T
        out += Z
    return out % p


def apply_K_mod(X, p):
    out = np.zeros_like(X)
    for i in range(G.N):
        for j in range(G.N):
            r, c, s = G.RHO_IDX[i][j]
            Y = np.zeros_like(X); Y[:, c] = s[None, :] * X[:, r]      # X rho
            Z = np.zeros_like(X); Z[r, :] = s[:, None] * Y[c, :]      # rho X rho
            out += Z
        out %= p
    return out % p


def tr_mod(A, B, p):
    return int(np.sum((A * B) % p) % p)


def V_exact(phi_int):
    vo = np.array([int(x) for x in phi_int], dtype=object)
    inv = K.invariants(vo)
    return sum(c * Fraction(inv[n]) for c, n in zip(c_q, NAMES)), inv


phi0_int = np.array([int(x) for x in K.pao_vector(P0, A0, 0, dtype=object)], dtype=np.int64)
V0, _ = V_exact(phi0_int)

# ---------------------------------------------------------------- exact Gram products at the points
pairs = [(a, b) for ch, idx in blocks.items() for ia, a in enumerate(idx) for b in idx[ia:]]
GramX = {}            # (k, a, b) -> Fraction
rhs = []; I2s = []; invrows = []
t1 = time.time()
for k, p_int in enumerate(pts):
    pf = p_int.astype(float)
    T4 = G.dense4(pf); T6 = G.dense6_fast(G.HODGE @ pf)
    Xraw = {n: covs[n].evaluate(T4, T6) for n in names_all}
    Xst = np.array([Xraw[n] + Xraw[n].T for n in basis])
    Xan = np.array([Xraw[n] - Xraw[n].T for n in basis_anti]) if basis_anti else None
    assert np.abs(Xst).max() < 2.0 ** 50
    if basis_ts:
        Zst = np.array([TS.sym_traceless(tscovs[n].evaluate(T4, T6)) for n in basis_ts])
        assert np.abs(Zst).max() < 2.0 ** 50
    Ys = [np.tensordot(alphas[a], {"sym": Xst, "anti": Xan, "ts": (Zst if basis_ts else None)}[carriers[a]], axes=(0, 0)) for a in range(nc)]
    for Y in Ys:
        assert np.abs(Y).max() < 2.0 ** 52
    Ynorm = [float(np.linalg.norm(Y)) for Y in Ys]
    # a-priori bound on every trace: 45^7 * 100^2 * |Y_a| |Y_b| (matrix carriers), 180^3 |Y_a||Y_b| (ts carrier)
    bound = max((45.0 ** 7) * (100.0 ** 2), 180.0 ** 3) * max(Ynorm) ** 2
    assert bound < MODULUS / 2.0, ("CRT modulus too small", bound, MODULUS)
    mat_idx = [a for a in range(nc) if carriers[a] != "ts"]
    ts_idx = [a for a in range(nc) if carriers[a] == "ts"]
    # traces mod each prime
    T = {}      # (a, b, kind, n) -> list of residues
    for p in PRIMES:
        CY = {}; CKY = {}
        for a in mat_idx:
            Y = np.rint(Ys[a]).astype(np.int64) % p
            pw = [Y]
            for _ in range(4):
                pw.append(apply_C_mod(pw[-1], p))
            CY[a] = pw
            KY = apply_K_mod(Y, p)
            pw2 = [KY]
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
        if cr == "ts":
            so_poly, gl_poly = TS.ts_projector(chname)
        else:
            so_poly, gl_poly = (G.PROJ if cr == "sym" else G.PROJ_ANTI)[chname]
        val = Fraction(0)
        for n, pn in enumerate(so_poly):
            if pn == 0:
                continue
            if len(gl_poly) == 1:
                val += pn * Tint[(a, b, 0, n)]
            else:
                val += pn * (gl_poly[0] * Tint[(a, b, 0, n)] + gl_poly[1] * Tint[(a, b, 1, n)] + gl_poly[2] * Tint[(a, b, 2, n)])
        GramX[(k, a, b)] = val
    Vp, inv = V_exact(p_int)
    rhs.append(Vp - V0); I2s.append(Fraction(int(p_int @ p_int)))
    I2, I3, Ja, Jb, Jc, Je = (Fraction(inv[n]) for n in NAMES)
    invrows.append([Fraction(1), I2, I3, Ja, Jb, Jc, Je, I2 * I3, I2 * Ja, I2 * Jb, I2 * Jc, I2 * Je, I3 * I3])
    if k % 5 == 0:
        print(f"  exact point {k}/{len(pts)}", f"[{time.time()-t1:.0f}s]", flush=True)
# float cross-check against g2's float Grams
Gf = dat["Gram"]
err = max(abs(float(GramX[(k, a, b)]) - Gf[k, a, b]) / max(abs(Gf[k, a, b]), 1.0) for (k, a, b) in GramX)
print("max relative deviation exact vs float Gram:", err, flush=True)

# ---------------------------------------------------------------- exact affine system
cols = [(a, b) for (a, b) in pairs]
nvar = len(cols) + 1
Kp = len(pts)
A = sp.zeros(Kp, nvar); bvec = sp.zeros(Kp, 1)
for k in range(Kp):
    for j, (a, b) in enumerate(cols):
        v = GramX[(k, a, b)] * (1 if a == b else 2)
        A[k, j] = sp.Rational(v.numerator, v.denominator)
    r = rhs[k]
    A[k, nvar - 1] = -sp.Rational((r * I2s[k]).numerator, (r * I2s[k]).denominator)
    bvec[k, 0] = sp.Rational(r.numerator, r.denominator)
rankA = A.rank(); rankAb = A.row_join(bvec).rank()
print("exact identity system: rank A", rankA, "rank [A|b]", rankAb, "unknowns", nvar, "points", Kp, f"[{time.time()-t0:.0f}s]", flush=True)
out = {"point": [P0, A0], "K": Kp, "n_combos": nc, "n_unknowns": nvar, "rank_A": int(rankA), "rank_Ab": int(rankAb),
       "exact_consistent": bool(rankAb == rankA), "float_vs_exact_gram_maxrel": err}
if rankAb != rankA:
    print("EXACT: inconsistent identity system -> no exact certificate in this ansatz", flush=True)
    json.dump(out, open(os.path.join(HERE, f"g3_exact_{lab2}.json"), "w"), indent=1)
    sys.exit(0)

# ---------------------------------------------------------------- numerical solution -> rational -> exact projection
Qnum = {ch: np.array(g2["phase2_Q"][ch]) for ch in blocks}
h1num = g2["phase2_h1"]
x_num = []
for (a, b) in cols:
    ch = str(chan_of[a]); idx = blocks[ch]
    ia, ib = idx.index(a), idx.index(b)
    # unscale: Q_ab = Qs_ab * rscale / (scale_a scale_b)
    x_num.append(Qnum[ch][ia, ib] * rscale / (scale_a[a] * scale_a[b]))
x_num.append(h1num)
D = 2 ** DEN_BITS
x_r = sp.Matrix([sp.Rational(int(round(v * D)), D) for v in x_num])
_, piv = A.T.rref()
rows = list(piv)
Ar = A.extract(rows, list(range(nvar))); br = bvec.extract(rows, [0])
resid = Ar * x_r - br
corr = Ar.T * (Ar * Ar.T).inv() * resid
x_ex = x_r - corr
assert (A * x_ex - bvec) == sp.zeros(Kp, 1)
maxcorr = max(abs(float(v)) for v in corr)
print("exact projection done; max |correction| =", maxcorr, "max |x| =", max(abs(v) for v in x_num), f"[{time.time()-t0:.0f}s]", flush=True)
h1_ex = x_ex[nvar - 1]
Qex = {}
for ch, idx in blocks.items():
    n = len(idx); M = sp.zeros(n, n)
    for j, (a, b) in enumerate(cols):
        if str(chan_of[a]) == ch:
            ia, ib = idx.index(a), idx.index(b)
            M[ia, ib] = x_ex[j]; M[ib, ia] = x_ex[j]
    Qex[ch] = M


def exact_pd(M):
    """rational LDL^T: returns (all pivots > 0, min pivot) ; PSD with zero pivots handled as failure (strict PD required)."""
    n = M.shape[0]
    Mf = [[Fraction(int(M[i, j].p), int(M[i, j].q)) for j in range(n)] for i in range(n)]
    minpiv = None
    for k in range(n):
        piv_ = Mf[k][k]
        if piv_ <= 0:
            return False, float(piv_)
        minpiv = piv_ if minpiv is None else min(minpiv, piv_)
        for i in range(k + 1, n):
            f = Mf[i][k] / piv_
            for j in range(k, n):
                Mf[i][j] -= f * Mf[k][j]
    return True, float(minpiv)


pd_all = True; pdinfo = {}
for ch, M in Qex.items():
    ok, mp = exact_pd(M)
    pd_all &= ok
    pdinfo[ch] = {"exact_PD": ok, "min_pivot": mp, "float_eigs": np.linalg.eigvalsh(np.array(M.tolist(), dtype=float)).tolist()}
    print(ch, "exact PD:", ok, "min pivot", mp, flush=True)
out.update({"h1_exact": str(h1_ex), "h1_nonneg": bool(h1_ex >= 0), "all_blocks_exact_PD": bool(pd_all), "pd_info": pdinfo,
            "max_projection_correction": maxcorr, "den_bits": DEN_BITS,
            "Q_exact": {ch: [[str(M[i, j]) for j in range(M.shape[0])] for i in range(M.shape[0])] for ch, M in Qex.items()}})

# ---------------------------------------------------------------- deterministic identity proof: rank of invariants on the points
famrows = []
for k in range(Kp):
    row = list(invrows[k])
    for (a, b) in cols:
        row.append(GramX[(k, a, b)])
    famrows.append([sp.Rational(x.numerator, x.denominator) for x in row])
famM = sp.Matrix(famrows)
fam_rank = famM.rank()
print("rank of {13 lower products + Gram products} on the points:", fam_rank, "(dim Inv_<=6 = 30)", flush=True)
out["invariant_family_rank"] = int(fam_rank)
out["deterministic_identity_proof"] = bool(fam_rank == 30 and pd_all and h1_ex >= 0)
out["certificate_valid_exact"] = bool(pd_all and h1_ex >= 0 and fam_rank == 30)
out["elapsed_s"] = time.time() - t0
json.dump(out, open(os.path.join(HERE, f"g3_exact_{lab2}.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("Q_exact", "pd_info")}, indent=1), flush=True)
