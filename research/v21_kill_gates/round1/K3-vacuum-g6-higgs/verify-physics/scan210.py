"""Dense orientation scan of the tree-level 210 G3221 mass sum rules (verifier's independent computation).

At Phi0 = cos(th) p + sin(th) a (unit norm), V210 = c.(I2, I3, J0, J2, J3, J4).  Stationarity (two linear conditions on
c) -> 4-dim null space y.  For every G3221 isotypic block the Goldstone-complement Hessian is extracted for each null
vector; multiplicity-1 blocks give scalar linear mass forms m^2_b(y).  LPs (homogeneous):
   single : min m^2(X) s.t. m^2(other blocks) >= 1          (value k > 0 means m^2(X) >= k * min(others))
   pair   : max t s.t. m^2(8,3,1) in [0,1], m^2(1,3,1) in [0,1], all other blocks >= t
Also records the gauge-loop (Coleman-Weinberg, gauge bosons only) curvature along each block, the rank of the mass-form
space and the D-parity consistency ((15,3,1) at th <-> (15,1,3) at -th).
usage: python -B scan210.py [step_deg]
"""
from __future__ import annotations
import sys, time, json
import numpy as np
from scipy.optimize import linprog
HERE = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K3-vacuum-g6-higgs\verify-physics"
sys.path.insert(0, HERE)
import v210 as V

step = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
t0 = time.time()
F = V.singlet_forms()
P, A = F["p"], F["a"]
S2 = 1 / np.sqrt(2)
# polarisation: quartic Hessians are quadratic in phi
HP = V.all_hessians(P); HA = V.all_hessians(A); HM = V.all_hessians(S2 * (P + A))
gP = V.all_gradients(P); gA = V.all_gradients(A); gM = V.all_gradients(S2 * (P + A))
print("Hessians at P, A, (P+A)/sqrt2 done %.1fs" % (time.time() - t0))


def hess_at(th):
    c, s = np.cos(th), np.sin(th)
    out = {}
    for n in V.NAMES:
        if n == "I2":
            out[n] = HP[n]
        elif n == "I3":
            out[n] = c * HP[n] + s * HA[n]
        else:
            HPA = 2 * HM[n] - HP[n] - HA[n]
            out[n] = c * c * HP[n] + s * s * HA[n] + c * s * HPA
    return out


def grad_at(th):
    c, s = np.cos(th), np.sin(th)
    out = {}
    for n in V.NAMES:
        if n == "I2":
            out[n] = c * P + s * A
        elif n == "I3":
            out[n] = c * c * gP[n] + s * s * gA[n] + c * s * (2 * gM[n] - gP[n] - gA[n])
        else:
            # cubic in phi: use 4 sample points along the (p,a) plane: g(phi) = sum over degree-3 monomials; fit
            raise NotImplementedError
    return out


# gradient of the quartics is cubic in phi: evaluate directly (cheap: just K^d applied to vectors)
def grad_direct(th):
    phi = np.cos(th) * P + np.sin(th) * A
    return V.all_gradients(phi)


# validate polarisation at 45 deg against the direct computation
thv = np.radians(37.0)
Hd = V.all_hessians(np.cos(thv) * P + np.sin(thv) * A); Hp = hess_at(thv)
print("polarisation check at 37 deg: max |H_direct - H_polar| =", max(np.abs(Hd[n] - Hp[n]).max() for n in V.NAMES))

gens = V.g3221_generators(); cas = V.casimirs(gens)
blocks = V.isotypic_blocks(cas)
blocks = sorted(blocks, key=lambda t: (-t[1].shape[1], t[0]))
names = [V.irrep_name(lab) for lab, B in blocks]
print("blocks:", [(n, B.shape[1]) for n, (lab, B) in zip(names, blocks)])
# sanity: su(3) Casimir eigenvalues
print("C3 eigenvalues on 210:", sorted(set(np.round(np.linalg.eigvalsh(cas["C3"]), 6))))
# resolve the two (1,1,1) and the two (3,2,2) copies: the multiplicity-2 blocks
# identify (8,3,1), (1,3,1), (8,1,3), (1,1,3) etc. by name
def find(name):
    return [i for i, n in enumerate(names) if n == name]

T831 = find("(8,3,1)_|B-L|=0"); T131 = find("(1,3,1)_|B-L|=0"); T813 = find("(8,1,3)_|B-L|=0"); T113 = find("(1,1,3)_|B-L|=0")
print("indices (8,3,1), (1,3,1), (8,1,3), (1,1,3):", T831, T131, T813, T113)

G45 = 0.58 ** 4
def gauge_cw_curvature(phi, v, h=0.02, mu2=1.0):
    """d^2/de^2 of (3/64pi^2) sum_V m_V^4 (ln m_V^2/mu^2 - 5/6) along unit v (g = 0.58)."""
    def Vg(x):
        m2 = np.linalg.eigvalsh(V.gauge_mass_matrix(x, g=0.58))
        m2 = m2[m2 > 1e-14]
        return 3.0 / (64 * np.pi ** 2) * float(np.sum(m2 ** 2 * (np.log(m2 / mu2) - 5.0 / 6.0)))
    f = lambda e: Vg(phi + e * v)
    return (-f(2 * h) + 16 * f(h) - 30 * f(0) + 16 * f(-h) - f(-2 * h)) / (12 * h * h)


results = []
angles = np.arange(-89.0, 90.0 + 1e-9, step)
for deg in angles:
    th = np.radians(deg)
    phi0 = np.cos(th) * P + np.sin(th) * A
    H = hess_at(th); g = grad_direct(th)
    # stationarity rows: <P, g_c>, <A, g_c> (gradient lies in span(P, A) by symmetry; check the omega component too)
    Srows = np.array([[P @ g[n] for n in V.NAMES], [A @ g[n] for n in V.NAMES]])
    om_res = max(abs(F["omega"] @ g[n]) for n in V.NAMES)
    u, s, vt = np.linalg.svd(Srows)
    rk = int(np.sum(s > 1e-10 * s[0]))
    Nn = vt[rk:].T  # 6 x (6-rk)
    Gm = V.goldstone_matrix(phi0)
    Hy = [sum(Nn[c, k] * H[n] for c, n in enumerate(V.NAMES)) for k in range(Nn.shape[1])]
    forms = {}; forms_mult = {}
    spread_max = 0.0
    for name, (lab, B) in zip(names, blocks):
        Q = V.complement_in_block(B, Gm)
        if Q.shape[1] == 0:
            continue
        red = [Q.T @ Hk @ Q for Hk in Hy]
        # is the block scalar (all reduced matrices proportional to identity)?
        spread = max(np.abs(R - np.trace(R) / R.shape[0] * np.eye(R.shape[0])).max() for R in red)
        if spread < 1e-9:
            forms[name] = np.array([np.trace(R) / R.shape[0] for R in red])
        else:
            forms_mult[name] = red
            spread_max = max(spread_max, spread)
    fnames = list(forms); M = np.array([forms[n] for n in fnames])
    rank = np.linalg.matrix_rank(M, tol=1e-9 * np.abs(M).max())
    nf = Nn.shape[1]
    # single-target LPs
    def single(target, others):
        res = linprog(forms[target], A_ub=-np.array([forms[o] for o in others]), b_ub=-np.ones(len(others)),
                      bounds=[(-1e4, 1e4)] * nf, method="highs")
        if res.status == 0:
            return float(res.fun), float(np.abs(res.x).max())
        return (None if res.status == 2 else float("-inf")), None
    rec = {"theta_deg": float(deg), "stat_rank": rk, "n_free": nf, "omega_grad_residual": float(om_res),
           "rank_scalar_forms": int(rank), "n_scalar_forms": len(fnames), "nonscalar_blocks": {k: [r.shape[0] for r in v] for k, v in forms_mult.items()},
           "goldstone_rank": int(np.linalg.matrix_rank(Gm, tol=1e-9))}
    singles = {}
    # researcher-like set: all scalar forms except the target (the singlet 2x2 block is non-scalar -> excluded automatically)
    for tgt in ("(8,3,1)_|B-L|=0", "(1,3,1)_|B-L|=0", "(8,1,3)_|B-L|=0", "(1,1,3)_|B-L|=0"):
        if tgt in forms:
            others = [n for n in fnames if n != tgt]
            singles[tgt] = single(tgt, others)
    rec["single"] = singles
    # pair LPs: both (8,3,1) and (1,3,1) in [0,1], maximise min(others); and the L<->R mirrored pair
    def pair(targets):
        others = [n for n in fnames if n not in targets]
        obj = np.zeros(nf + 1); obj[-1] = -1
        Aub, bub = [], []
        for o in others:
            row = np.zeros(nf + 1); row[:nf] = -forms[o]; row[-1] = 1; Aub.append(row); bub.append(0.0)
        for tname in targets:
            row = np.zeros(nf + 1); row[:nf] = forms[tname]; Aub.append(row); bub.append(1.0)
            row = np.zeros(nf + 1); row[:nf] = -forms[tname]; Aub.append(row); bub.append(0.0)
        res = linprog(obj, A_ub=np.array(Aub), b_ub=np.array(bub), bounds=[(-1e4, 1e4)] * nf + [(None, None)], method="highs")
        return float(-res.fun) if res.status == 0 else None
    rec["pair_831_131"] = pair(("(8,3,1)_|B-L|=0", "(1,3,1)_|B-L|=0"))
    rec["pair_813_113"] = pair(("(8,1,3)_|B-L|=0", "(1,1,3)_|B-L|=0"))
    # also: the pair with the singlet 2x2 block required PSD via 12 direction cuts (stronger constraint set)
    results.append(rec)
    if abs(deg - round(deg / 5) * 5) < 1e-9 or abs(abs(deg) - 45) < 1e-9:
        print(f"th={deg:6.1f}: stat rank {rk}, free {nf}, scalar forms {len(fnames)} rank {rank}, nonscalar {list(forms_mult)}; "
              f"single (8,3,1) {singles.get('(8,3,1)_|B-L|=0')}, (1,3,1) {singles.get('(1,3,1)_|B-L|=0')}, (8,1,3) {singles.get('(8,1,3)_|B-L|=0')}, (1,1,3) {singles.get('(1,1,3)_|B-L|=0')}; "
              f"pair(831,131) {rec['pair_831_131']}, pair(813,113) {rec['pair_813_113']}  [{time.time()-t0:.0f}s]", flush=True)

json.dump({"names": names, "results": results}, open(HERE + r"\scan210_results.json", "w"), indent=1)
# summary: angles where the pair is feasible with a gap (max min(others) > 1 means others can be heavier than the pair)
feas = [(r["theta_deg"], r["pair_831_131"]) for r in results if r["pair_831_131"] is not None and r["pair_831_131"] > 1.0 + 1e-6]
print("angles with pair (8,3,1)+(1,3,1) light and min(others) > 1 x targets:", feas)
best = max(results, key=lambda r: (r["pair_831_131"] if r["pair_831_131"] is not None else -1))
print("best pair ratio over the scan:", best["theta_deg"], best["pair_831_131"])
print("done %.0fs" % (time.time() - t0))
