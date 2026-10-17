"""Verifier re-analysis of the pure-sector tree-level sum rules (210 sector: O07, O17, O48x4; 126bar sector: O05, O14,
O25, O26, O27x4, O44x6) from the researcher's <tag>_blocks.npz / <tag>_blocks.json (read-only) and my scan tags.

Differences from k3_sumrules.py: (1) the sector null space is taken from the stored stationarity rows restricted to the
sector couplings (identical to J[:, sector] null space); (2) identical mass forms (SU(2)_R partners of one G3221
multiplet, e.g. (8,2)_{1/2}#0/#1 of the (8,2,2)) are merged into one multiplet so that a multiplet is never constrained
by its own partner; (3) besides single-target ratios it computes the pair ratio and enumerates every subset of distinct
multiplets that can be exactly massless with all others >= 1 (LP feasibility; homogeneous, so 'light with the rest
heavy at any ratio').  Necessary conditions only (mixed SM blocks with Phi+Sigma members are not in the pure sectors).
usage: python -B sector_lp_check.py <folder> <tag> [<tag> ...]
"""
from __future__ import annotations
import sys, json, itertools
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

folder = Path(sys.argv[1]); tags = sys.argv[2:]
SECTOR_PARS = {"phi": ("O07", "O17", "O48"), "sigma": ("O05", "O14", "O25", "O26", "O27", "O44")}
SECTOR_BLOCK = {"phi": "Phi210", "sigma": "Sigma126bar"}
TARGETS = {"phi": ["(8,3)_|Y|=0", "(1,3)_|Y|=0"], "sigma": ["(8,2)_|Y|=1/2"]}


def complement(U, m):
    if U is None or U.shape[1] == 0: return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True); r = int(np.sum(ss > 1e-10)); return uu[:, r:]


def mass_forms(B, meta, labels, ids, sector):
    par = [i for i, p in enumerate(ids) if p.split("::")[1][:3] in SECTOR_PARS[sector]]
    S = B["stat_rows"][:, par]
    u, s, vt = np.linalg.svd(S, full_matrices=True); rk = int(np.sum(s > 1e-10 * max(s[0], 1e-300)))
    N = vt[rk:].T
    rows = {}
    for k, lab in enumerate(labels):
        cols = meta[k]["meta"]
        if not all(c["block"] == SECTOR_BLOCK[sector] for c in cols): continue
        Q = complement(B[f"G{k}"], int(B["m"][k]))
        if Q.shape[1] == 0: continue
        Ar = np.einsum("ji,pjl,lm->pim", np.conj(Q), B[f"A{k}"][par], Q)
        Ay = np.einsum("ia,ijk->ajk", N, Ar); mc = Q.shape[1]
        if mc == 1:
            rows[lab] = np.real(Ay[:, 0, 0])
        else:
            rng = np.random.default_rng(3); comb = np.einsum("a,ajk->jk", rng.normal(size=N.shape[1]), Ay)
            w, v = np.linalg.eigh(0.5 * (comb + comb.conj().T))
            off = max(float(np.max(np.abs((v.conj().T @ Ay[a] @ v) - np.diag(np.diag(v.conj().T @ Ay[a] @ v))))) for a in range(N.shape[1]))
            if off > 1e-8:
                print(f"   WARNING {lab}: block not simultaneously diagonalisable over the free parameters (off = {off:.2e}); skipped", flush=True); continue
            for j in range(mc): rows[f"{lab}#{j}"] = np.real(np.einsum("i,aij,j->a", np.conj(v[:, j]), Ay, v[:, j]))
    # the vev-light (1,1)_2 of Delta_R is light by the vev condition: not a constraint and not a target (as k3_sumrules)
    rows = {n: f for n, f in rows.items() if not n.startswith("(1,1)_|Y|=2")}
    # merge identical forms (partners)
    names = list(rows); merged = []  # list of (display name, form)
    used = set()
    for i, n in enumerate(names):
        if n in used: continue
        grp = [n]
        for m2 in names[i + 1:]:
            if m2 not in used and np.max(np.abs(rows[n] - rows[m2])) < 1e-9 * max(1.0, np.max(np.abs(rows[n]))):
                grp.append(m2); used.add(m2)
        used.add(n); merged.append(("+".join(grp), rows[n]))
    return merged, rk, N.shape[1]


def ratio_lp(forms, targets_idx):
    """max k s.t. others >= k, targets in [0, 1]  (k = sup of min(others)/max(targets)); 'inf' if the LP is unbounded."""
    nf = forms[0][1].size; obj = np.zeros(nf + 1); obj[-1] = -1; Aub, bub = [], []
    for j, (_, f) in enumerate(forms):
        if j in targets_idx:
            r = np.zeros(nf + 1); r[:nf] = f; Aub.append(r); bub.append(1.0)
            r = np.zeros(nf + 1); r[:nf] = -f; Aub.append(r); bub.append(0.0)
        else:
            r = np.zeros(nf + 1); r[:nf] = -f; r[-1] = 1; Aub.append(r); bub.append(0.0)
    res = linprog(obj, A_ub=np.array(Aub), b_ub=np.array(bub), bounds=[(-1e6, 1e6)] * nf + [(None, None)], method="highs")
    if res.status == 3: return float("inf")
    if res.status != 0: return None
    k = -res.fun
    return float("inf") if k > 1e5 else float(k)


def exact_light_feasible(forms, targets_idx):
    """feasibility: targets == 0, others >= 1."""
    nf = forms[0][1].size
    Aeq = np.array([forms[j][1] for j in targets_idx]) if targets_idx else None
    beq = np.zeros(len(targets_idx)) if targets_idx else None
    others = [j for j in range(len(forms)) if j not in targets_idx]
    if not others: return False  # 'everything light' is not a hierarchy
    Aub = -np.array([forms[j][1] for j in others]); bub = -np.ones(len(others))
    res = linprog(np.zeros(nf), A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=[(-1e6, 1e6)] * nf, method="highs")
    return res.status == 0


out = {}
for tag in tags:
    B = np.load(folder / f"{tag}_blocks.npz"); meta = json.load(open(folder / f"{tag}_blocks.json", encoding="utf-8"))["blocks"]
    labels = [str(x) for x in B["labels"]]; ids = [str(x) for x in B["ids"]]
    rec = {}
    for sector in ("phi", "sigma"):
        forms, rk, nfree = mass_forms(B, meta, labels, ids, sector)
        M = np.array([f for _, f in forms]); rank = int(np.linalg.matrix_rank(M, tol=1e-9))
        names = [n for n, _ in forms]
        single = {}
        for j, n in enumerate(names):
            single[n] = ratio_lp(forms, {j})
        srec = {"n_multiplets": len(names), "names": names, "stationarity_rank": rk, "free": nfree, "mass_rank": rank, "single_target_max_ratio_minothers_over_target": single}
        if sector == "phi":
            ti = [j for j, n in enumerate(names) if n.startswith("(8,3)") or n.startswith("(1,3)_|Y|=0")]
            srec["pair_(8,3)+(1,3)_max_ratio"] = ratio_lp(forms, set(ti))
        # subset enumeration (exactly massless targets, others >= 1): maximal feasible subsets
        feas = []
        for r in range(1, len(names) + 1):
            for sub in itertools.combinations(range(len(names)), r):
                if exact_light_feasible(forms, set(sub)): feas.append(sub)
        maximal = [s for s in feas if not any(set(s) < set(t) for t in feas)]
        srec["n_feasible_subsets"] = len(feas)
        srec["maximal_light_sets"] = [[names[j] for j in s] for s in maximal]
        rec[sector] = srec
        print(tag, sector, "rank", rank, "pair" if sector == "phi" else "", srec.get("pair_(8,3)+(1,3)_max_ratio", ""),
              "| single:", {n: (round(v, 3) if isinstance(v, float) and v != float('inf') else v) for n, v in single.items()}, flush=True)
        print("   maximal light sets:", srec["maximal_light_sets"], flush=True)
    out[tag] = rec
json.dump(out, open(Path(__file__).parent / f"sector_lp_check_{'_'.join(tags)[:60]}.json", "w"), indent=1, default=str)
