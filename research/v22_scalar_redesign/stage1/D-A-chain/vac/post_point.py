"""D-A-chain post-processing of an lp_sm.py solution at an SM-direct point (NUM):
  1. light SM-doublet eigenvector a of the (1,2)_{1/2} block -> composition (v_u, v_d, w_u, w_d), r, s (r2_compose map)
     [D2 structural check: s != 1 and w_d != 0 <=> no one-bidoublet / up-type-only obstruction on this orientation];
  2. cubic/quartic rows along u = q_vev(a) (two exact rows calls, as R2-A r2a_cubic_for_a.py) -> exact tree lambda_eff
     = V4(u)/6 - sum_heavy b^2/(2 m^2) (light terms listed separately), and the largest single heavy contribution;
  3. block spectra of the light unification states and the heavy gap.
usage: python -B post_point.py <tag> <solution npz stem> [eps_hi]
"""
import sys, json, time, math
import numpy as np
import k3_common as K
import r2_compose as RC

tag, stem = sys.argv[1], sys.argv[2]
eps_hi = float(sys.argv[3]) if len(sys.argv) > 3 else 3e-6
sol = np.load(K.SCRATCH / f"{stem}.npz"); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
B = np.load(K.SCRATCH / f"{tag}_blocks.npz"); labels = [str(x) for x in B["labels"]]
meta = json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))["blocks"]
Z = np.load(K.SCRATCH / f"{tag}_rows.npz"); q0 = Z["q"]; H0 = Z["hess"]; assert [str(x) for x in Z["ids"]] == ids
out = {"tag": tag, "solution": stem, "blocks": {}}
for k, lab in enumerate(labels):
    Ac = np.einsum("p,pij->ij", c, B[f"A{k}"]); w = np.linalg.eigvalsh(0.5 * (Ac + Ac.conj().T))
    out["blocks"][lab] = w.tolist()
kd = labels.index("(1,2)_|Y|=1/2")
Ac = np.einsum("p,pij->ij", c, B[f"A{kd}"]); Ac = 0.5 * (Ac + Ac.conj().T); w, Vv = np.linalg.eigh(Ac)
a = Vv[:, 0]
nt = RC.Neutral(tag); cm = nt.comp_of_a(a)
out["doublet"] = {"eigs": w.tolist(), "a_abs2": (np.abs(a) ** 2).tolist(),
                  "a_blocks": [m["block"] for m in meta[kd]["meta"]],
                  "comp": {k: (complex(v).real, complex(v).imag) if isinstance(v, (complex, np.complexfloating)) else v
                           for k, v in cm.items() if k in ("vu", "vd", "wu", "wd", "r", "s")},
                  "frac": cm.get("frac")}
print("doublet eigs", np.round(w, 8), "|r| =", abs(cm["r"]), "s =", cm["s"], "frac", cm.get("frac"), flush=True)
# cubic rows along u
u = nt.q_of_a(a); eta = 0.1; t0 = time.time()
rp = K.parameter_rows(K.chart.unpack(q0 + eta * u)); rm = K.parameter_rows(K.chart.unpack(q0 - eta * u))
Hp = np.array([np.asarray(rp[i].hessian, float) for i in ids]); Hm = np.array([np.asarray(rm[i].hessian, float) for i in ids])
Hp = 0.5 * (Hp + np.transpose(Hp, (0, 2, 1))); Hm = 0.5 * (Hm + np.transpose(Hm, (0, 2, 1)))
dH = (Hp - Hm) / (2 * eta); d2H = (Hp + Hm - 2 * H0) / eta ** 2
b_up = np.einsum("pij,j->pi", dH, u); V4_up = np.einsum("i,pij,j->p", u, d2H, u)
np.savez_compressed(K.SCRATCH / f"cubic_{stem}.npz", ids=np.array(ids), eta=eta, b_up=b_up, V4_up=V4_up, u_up=u, a=a)
H = np.einsum("p,pij->ij", c, H0); H = 0.5 * (H + H.T); wf, Vf = np.linalg.eigh(H)
bvec = c @ b_up; V4 = float(c @ V4_up)
gold = np.abs(wf) < 1e-9; heavy = wf >= 10 * eps_hi; light = (~gold) & (~heavy)
bh = Vf[:, heavy].T @ bvec; bl = Vf[:, light].T @ bvec
Rh_terms = bh ** 2 / wf[heavy]; Rl_terms = bl ** 2 / wf[light]
lam = {"lambda_direct(V4/6)": V4 / 6, "R_heavy": float(np.sum(Rh_terms)), "lambda_eff_heavy": V4 / 6 - float(np.sum(Rh_terms)) / 2,
       "R_light": float(np.sum(Rl_terms)), "lambda_eff_all": V4 / 6 - float(np.sum(Rh_terms) + np.sum(Rl_terms)) / 2,
       "largest_heavy_terms(b^2/m^2, m^2)": sorted([(float(x), float(m)) for x, m in zip(Rh_terms, wf[heavy])], reverse=True)[:6],
       "light_terms": sorted([(float(x), float(m)) for x, m in zip(Rl_terms, wf[light])], reverse=True)[:6],
       "n_light": int(np.sum(light)), "n_heavy": int(np.sum(heavy)), "n_zero": int(np.sum(gold)), "min_eig": float(wf[0])}
out["lambda_tree"] = lam
print("lambda_tree:", json.dumps({k: v for k, v in lam.items() if not isinstance(v, list)}), f"[{time.time()-t0:.0f}s]", flush=True)
# portal sizes: the H10-Sigma mixed couplings and the 126bar self couplings
out["c_selected"] = {pid: float(c[i]) for i, pid in enumerate(ids) if any(s in pid for s in ("O31", "O28", "O27", "O15", "O38", "O45", "O33", "O35"))}
json.dump(out, open(K.SCRATCH / f"post_{stem}.json", "w"), indent=1, default=str)
print("saved", f"post_{stem}.json")
