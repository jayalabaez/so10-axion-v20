"""D3 post-processing of an LP point: light-doublet composition (r, s, field fractions), the H-Sigma portal coupling
sizes, and the EW-direction npz for the cubic rows (tree lambda_eff via r2a_cubic_for_a.py + lp_sm.py --stage B).
usage: python -B post_lp.py <tag> <lp_out>"""
import sys, json
import numpy as np
import k3_common as K
import r2_compose as RC

tag, out = sys.argv[1], sys.argv[2]
B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
ids = [str(x) for x in B["ids"]]
L = np.load(K.SCRATCH / f"{out}.npz"); c = L["c"]
kd = labels.index("(1,2)_|Y|=1/2")
A = np.einsum("p,pij->ij", c, B[f"A{kd}"]); A = 0.5 * (A + A.conj().T)
w, V = np.linalg.eigh(A)
a = V[:, 0]
nt = RC.Neutral(tag); cm = nt.comp_of_a(a)
meta = json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))["blocks"][kd]["meta"]
np.savez(K.SCRATCH / f"ew_{out}.npz", a=a)
rep = json.load(open(K.SCRATCH / f"{out}.json", encoding="utf-8"))
cc = rep["c"]
portal = {k: v for k, v in cc.items() if any(o in k for o in ("O15", "O28", "O31", "O35", "O38", "O45"))}
big = {k: v for k, v in cc.items() if abs(v) > 0.9 and k.split("::")[1][:3] not in ()}
res = {"tag": tag, "out": out, "t": rep["t"], "full_hessian": rep["full_hessian"], "a0": rep["singlet_channel_a0"],
       "competitor_min_gap": rep["competitor_bank_min_gap"], "bfb_min": rep["bfb_bank_min_V4"],
       "doublet_eigs": w.tolist(), "light_doublet_slice_weights": [{"col": meta[i], "w2": float(abs(a[i]) ** 2)} for i in range(len(a))],
       "r_abs": float(abs(cm["r"])), "s": [float(np.real(cm["s"])), float(np.imag(cm["s"]))], "field_fractions": cm["frac"],
       "HSigma_portal_couplings": portal, "couplings_at_|c|>0.9": big,
       "screen_n_lower": [sc["n_lower_non_orbit"] for sc in rep["subspace_screen"]]}
json.dump(res, open(f"post_{out}.json", "w", encoding="utf-8"), indent=1, default=float)
print(json.dumps({k: res[k] for k in ("t", "full_hessian", "a0", "competitor_min_gap", "r_abs", "s", "field_fractions", "screen_n_lower")}, default=float)[:1500])
print("doublet eigenvalues:", np.round(w, 6))
print("H-Sigma portals:", {k: round(v, 3) for k, v in portal.items()})
print("|c| > 0.9:", {k: round(v, 3) for k, v in big.items()})
