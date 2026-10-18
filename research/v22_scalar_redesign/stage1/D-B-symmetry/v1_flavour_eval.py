"""Evaluate stored V1 proxy-fit points (out/*.json): Dirac-Yukawa cancellation, perturbativity, composition.
For each best point: singular values of Yu, Ynu = Yu - 4 s'F, F; cancellation ratio sigma_max(Ynu)/y_t; Majorana coupling
f = C_R F / c_d126 at the v_R of the run (c_d126 = v_R / (v_R/c)); Sigma admixture |w_u| = |s'| c_d126, |w_d| = c_d126;
required 10-components |G| = |Yu - s'F| and |H| = |(3 Yd + Ye)/4| (Y10_act <= 1.5 -> |v| >= sigma_max/(1.5/Y10_ACT)).
usage: python -B v1_flavour_eval.py out/<file>.json [...]
"""
import sys, json, math
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import lib_r2c as L, model_r2c as M

for fn in sys.argv[1:]:
    R = json.load(open(HERE / fn)); vR = R["vR"]; content = R["content"]
    data = L.data_set(R.get("nu", "nufit60_sk"), floor=R.get("floor", 0.01))
    setup = M.make_setup(vR, data, content=content, MU=L.R2B_NOMINAL.get(content, (None, None))[1]); tg = setup["targets"]
    T = tg.T; IDX = {k: i for i, k in enumerate(L.ALL_KEYS)}
    yu = T[[0, 1, 2]] / L.VEV; Vstd = L.umix(T[IDX["s12"]], T[IDX["s23"]], T[IDX["s13"]], T[IDX["delta"]])
    b = R["best"][0]; x = np.array(b["x"])
    U = L.umix_b(*[np.array([x[i]]) for i in range(4)])[0]
    W = np.exp(1j * np.array([x[4], x[5], 0.0]))[:, None] * U * np.exp(1j * x[6:9])[None, :]
    Ye = (W * tg.se0[None, :]) @ W.T; Yd = np.diag(tg.sd0).astype(complex)
    Eu = np.exp(1j * x[9:12])[:, None] * Vstd.T * np.exp(1j * x[12:15])[None, :]; Yu = Eu @ np.diag(yu) @ Eu.T
    sp = 10.0 ** x[15] * np.exp(1j * x[16]); F = (Yd - Ye) / 4; Yn = Yu - 4 * sp * F; G = Yu - sp * F; H = (3 * Yd + Ye) / 4
    sv = lambda A: np.linalg.svd(A, compute_uv=False)
    vR_over_c = b["vR_max_from_composition"] / min(1.0, 1.0 / abs(sp))
    c = vR / vR_over_c
    out = {"file": fn, "vR": vR, "chi2": b["chi2_total"], "sv_Yu": sv(Yu).tolist(), "sv_Ynu": sv(Yn).tolist(), "sv_F": sv(F).tolist(),
           "cancellation_sigmaYnu_over_yt": float(sv(Yn)[0] / sv(Yu)[0]), "m_D_GeV": (sv(Yn) * L.VEV).tolist(),
           "c_d126": c, "abs_w_u": abs(sp) * c, "f_max_at_MU": float(L.C_R * sv(F)[0] / c), "sqrt4pi": math.sqrt(4 * math.pi),
           "sv_G": sv(G).tolist(), "sv_H": sv(H).tolist(), "MR_GeV": b["MR_GeV"], "mnu_eV": b["mnu_eV"], "delta_pmns": b["delta_pmns"]}
    print(json.dumps(out, default=float))
