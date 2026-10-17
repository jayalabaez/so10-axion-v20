"""R2-A tuning count at a solution: independent cancellations demanded by the light content.

For each light block (sub/sandwich, excluding the vev-light (1,1)_0/(1,1)_2 which follow from stationarity) the light
compression entries U^+ A_a U (a over the stationarity null-space basis, scaled by the coupling boxes) form a linear map;
its singular values sigma_k give the natural size of each independent light-mass combination; each must be cancelled to
the light window eps_hi = 3e-6, i.e. a tuning of relative size eps_hi / (sigma_k * |y|_typ).  Also Barbieri-Giudice
sensitivities of every light level (Hellmann-Feynman).
usage: python -B r2_tunings.py <tag> <solution npz> <spec string>
"""
from __future__ import annotations
import sys, json, numpy as np
import k3_common as K

tag, solpath, specstr = sys.argv[1], sys.argv[2], sys.argv[3]
B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); HESS = Z["hess"]; ids = [str(x) for x in Z["ids"]]
sol = np.load(K.SCRATCH / solpath); c = sol["c"]
TR = json.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8")); DEG = TR["degrees"]
box = np.array([{2: 40.0, 3: 2.0, 4: 1.0}[DEG[p.split("::")[1]]] for p in ids])
st = B["stat_rows"]; u_, s_, vt = np.linalg.svd(st, full_matrices=True); N = vt[st.shape[0]:].T
spec = dict(item.split(":") for item in specstr.split(";") if item)
out = {"tag": tag, "solution": solpath, "blocks": {}}
total = 0
for lab, kind in spec.items():
    k = labels.index(lab); A = B[f"A{k}"]; Ac = np.einsum("p,pij->ij", c, A); w, V = np.linalg.eigh(0.5 * (Ac + Ac.conj().T))
    nl = int(kind[-1]) if kind.startswith("sub") else A.shape[1]
    U = V[:, :nl]
    M = np.einsum("ji,pjl,lm->pim", np.conj(U), A, U)   # 51 x nl x nl
    feats = []
    for i in range(nl):
        for j in range(i, nl):
            feats.append(np.real(M[:, i, j]))
            if i != j: feats.append(np.imag(M[:, i, j]))
    F = np.array(feats) * box[None, :]           # natural scale: coupling at its box value
    F = F @ N                                    # restricted to stationary couplings
    sv = np.linalg.svd(F, compute_uv=False)
    rank = int(np.sum(sv > 1e-6 * sv[0])) if sv.size else 0
    levels = (3e-6 / sv[:rank]).tolist()
    out["blocks"][lab] = {"kind": kind, "n_light": nl, "light_eigs": w[:nl].tolist(), "n_conditions": rank, "singular_values": sv.tolist(), "tuning_levels": levels}
    total += rank
    print(f"{lab:16s} {kind:9s} light eigs {np.array2string(w[:nl], precision=3)}  independent cancellations {rank}; natural sizes {np.array2string(sv[:rank], precision=3)}; tuning levels {np.array2string(np.array(levels), precision=2)}")
out["total_conditions"] = total
# BG on light levels (full Hessian, Hellmann-Feynman)
H = np.einsum("p,pij->ij", c, HESS); H = 0.5 * (H + H.T); w, V = np.linalg.eigh(H)
ops = K.candidate.sm_label_operators(); C2L, C3 = ops["C2L"], ops["C3"]
levels = {}
for j in [j for j in range(len(w)) if 1e-9 < w[j] < 3e-5]:
    v = V[:, j]; d = np.array([v @ HESS[i] @ v for i in range(len(ids))]); sens = np.abs(c * d) / w[j]
    c2l = float(v @ C2L @ v); c3 = float(v @ C3 @ v)
    labl = "(1,2)" if abs(c2l - 0.75) < 1e-4 and abs(c3) < 1e-4 else ("(8,3)" if abs(c2l - 2) < 1e-4 and abs(c3 - 3) < 1e-4 else ("(1,3)" if abs(c2l - 2) < 1e-4 and abs(c3) < 1e-4 else ("(1,1)" if c2l < 1e-4 and c3 < 1e-4 else f"C2L={c2l:.2f},C3={c3:.2f}")))
    key = (labl, round(float(w[j]), 10)); kk = int(np.argmax(sens))
    levels.setdefault(key, []).append((float(sens[kk]), ids[kk]))
out["BG"] = [{"label": k[0], "m2": k[1], "mult": len(v), "BG_max": max(x[0] for x in v), "driver": max(v)[1]} for k, v in sorted(levels.items(), key=lambda kv: kv[0][1])]
for e in out["BG"]: print(f"  BG {e['label']:6s} m2 = {e['m2']:.4e} x{e['mult']:2d}  BG_max = {e['BG_max']:.3g}  driver {e['driver']}")
json.dump(out, open(K.SCRATCH / (solpath.replace('.npz', '') + "_tunings.json"), "w"), indent=1, default=float)
print("total independent cancellations:", total)
