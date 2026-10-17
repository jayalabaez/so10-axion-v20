"""Required triplet vev v_L at the best type-II points, and the induced v_L of the one-step G3221 vacuum (EST).
usage: typeII_vL.py RESULT.json
m_II = kappa_II v^2 = tc v^2 Y126_def(v_R),  m_II = C_L v_L Y126_def  (C_L = C_R = 2 sqrt6, K2 exact Clebsch)
=> v_L = |tc| v^2 / C_L.  The type-I part at the same point is reported for comparison."""
import sys, json, math
import numpy as np
import lib_r2c as L, model_r2c as M

J = json.load(open(sys.argv[1]))
d = {k: tuple(v) if isinstance(v, list) else v for k, v in J["data"].items()}
setup = M.make_setup(J["vR"], d, content=J["content"], MU=J["MU"])
tg = setup["targets"]
lay = M.Layout(typeII=True, free=True)
out = []
for r in J["exact_results"][:5]:
    z = np.array(r["z"]); x, lc = z[:-1], z[-1]
    G = M.gut_matrices(np.atleast_2d(x), lay, tg.sd0, tg.se0)
    rr = float(G["r"][0]); s = complex(G["s"][0]); comp = M.composition(rr, s, 10.0**lc)
    Y10 = G["H"][0] / comp["c_d10"]; Y126 = G["F"][0] / comp["c_d126"]
    env = setup["env"]
    g, Yq, Yl, fhR = L.run_g3221(np.array(env["g_MU"]), [Y10, Y126], [Y10, -3 * Y126], L.C_R * Y126, env["MU"], J["vR"], env["b_lo"], env["b_hi"])
    Yn = comp["c_u10"] * Yl[0] + comp["c_u126"] * Yl[1]
    MR = J["vR"] * fhR
    kI = -(Yn @ np.linalg.solve(MR, Yn.T))
    tc = 10.0**x[12] * np.exp(1j * x[13]) * np.linalg.norm(kI) / np.linalg.norm(Yq[1])
    vL = abs(tc) * L.VEV**2 / L.C_R
    mI = np.linalg.svd(kI * L.VEV**2, compute_uv=False) * 1e9
    mII = np.linalg.svd(tc * Yq[1] * L.VEV**2, compute_uv=False) * 1e9
    out.append({"src": r["src"], "chi2": r["chi2"], "log10_t": float(x[12]), "v_L_required_GeV": vL, "v_L_required_eV": vL * 1e9,
                "type_I_sv_eV(vR)": mI.tolist(), "type_II_sv_eV(vR)": mII.tolist(), "M_R_GeV": L.takagi(MR)[0].tolist(),
                "Y126_def_vR_maxabs": float(np.abs(Yq[1]).max())})
    print(json.dumps(out[-1]))
json.dump(out, open(sys.argv[1].replace(".json", "_vL.json"), "w"), indent=1)
