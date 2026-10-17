import sys, json, numpy as np
import k3_common as K, k3_verify as VF
sol = np.load(K.SCRATCH / sys.argv[1]); c = sol["c"]; tag = sys.argv[2]
rep = VF.verify(c, screen=True)
# gauge boson masses from the chart tangents at the Am45 point (index-1 normalisation M^2 = g^2/2 G^T G), g = 0.58
Zr = np.load(K.SCRATCH / "Am45_rows.npz"); G = Zr["tangents"][:, :45]; g = 0.58
M2 = 0.5 * g * g * (G.T @ G); mv = np.sqrt(np.clip(np.linalg.eigvalsh(M2), 0, None))
rep["gauge_masses_over_gPhi"] = sorted(set(np.round(mv / g, 5).tolist()))
rep["heavy_scalar_min_mass_over_Phi"] = float(np.sqrt(rep["full_hessian"]["min_heavy"]))
json.dump(rep, open(K.SCRATCH / f"final_verify_{tag}.json", "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in rep.items() if k not in ("subspace_screen", "lambda_dn")}, default=float)[:2500])
for s in rep["subspace_screen"]:
    print(f"screen {s['mode']}: V* = {s['V_star']:.9g}, V_min_all = {s['V_min_all']:.9g}, n_lower_non_orbit = {s['n_lower_non_orbit']}, runaway = {s['runaway']}, lowest_non_orbit (V-V*, z) = {(s['lowest_non_orbit'][0][0]-s['V_star'], [round(x,4) for x in s['lowest_non_orbit'][0][1]]) if s['lowest_non_orbit'] else None}")
