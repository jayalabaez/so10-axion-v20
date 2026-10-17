"""Seesaw cancellation diagnostic at my best points: size of each nu^c contribution vs the total m_nu at v_R."""
import sys, os, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import skchain as S, skopt as O
S.KAPPA_LAM = 2.0
d = S.dataset(0.01)
out = []
for e in json.load(open(os.path.join(HERE, "polish_K2.json"))):
    vR = e["vR"]; c = e["content"]; env = S.Env(vR, c, S.MU_NOMINAL[c], d)
    H, F, r, s, cd = O.w_to_gut(np.array(e["x"])[None])
    ok, cd10, cu10, cu126 = S.composition(r, s, cd)
    Y10 = H / cd10[:, None, None]; Y126 = F / cd[:, None, None]
    st = S.run_g3221([Y10, Y126, Y10, -3 * Y126, S.C_R * Y126], env, 0.1)
    Yq0, Yq1, Yl0, Yl1, f = st
    Yn = cu10[:, None, None] * Yl0 + cu126[:, None, None] * Yl1
    M = vR * f
    m, U = S.takagi(M)
    Ynb = Yn[0] @ U[0]                        # columns = nu^c mass eigenstates (doublet-left)
    parts = [S.VEV**2 * np.outer(Ynb[:, i], Ynb[:, i]) / m[0, i] * 1e9 for i in range(3)]   # eV
    tot = sum(parts)
    sv = np.linalg.svd(tot, compute_uv=False)
    rec = dict(vR=vR, M_R=m[0].tolist(), part_norms_eV=[float(np.linalg.norm(p, 2)) for p in parts], total_sv_eV=sv.tolist(),
               cancellation=float(max(np.linalg.norm(p, 2) for p in parts) / sv.max()),
               yD_sv=np.linalg.svd(Yn[0], compute_uv=False).tolist())
    out.append(rec)
    print(f"vR={vR:.0e}: M_R={np.round(m[0]/1e9,2)} GeV*1e9  |m_i| (eV) = {np.round(rec['part_norms_eV'],4)}  "
          f"|m_tot| = {np.round(sv,4)}  max|m_i|/|m_tot| = {rec['cancellation']:.1f}  yD sv = {np.round(rec['yD_sv'],4)}")
json.dump(out, open(os.path.join(HERE, "finetune_diag.json"), "w"), indent=1)
