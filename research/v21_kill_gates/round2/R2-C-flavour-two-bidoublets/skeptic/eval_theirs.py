"""Evaluate the researcher's best points with MY independent chain (skchain), compare chi2 and pulls."""
import sys, os, json, math, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skchain as S

pts = json.load(open(os.path.join(HERE, "their_points.json")))
d = S.dataset(0.01)
envs = {}
rows = []
for p in pts:
    key = (p["vR"], p["content"], p["MU"])
    if key not in envs:
        envs[key] = S.Env(p["vR"], p["content"], p["MU"], d)
    env = envs[key]
    P = np.array(p["P"])[None]
    res = {}
    for lab, kw in [("fine", dict(h_g=0.1, h_hi=0.02, h_lo=0.1)), ("std", dict(h_g=0.25, h_hi=0.05, h_lo=0.25)),
                    ("1loopSM", dict(h_g=0.25, h_hi=0.05, h_lo=0.25, two_loop=False))]:
        m = S.Model(env, d, **kw)
        R = m.resid(P)[0]
        o, ok, info = m.last
        res[lab] = dict(chi2=float(np.sum(R[:18]**2)), pen=float(np.sum(R[18:]**2)), pulls={k: float(R[i]) for i, k in enumerate(S.KEYS)},
                        th23=float(o[0, 14]), fmax=float(max(info["fU"][0], info["fR"][0])), MR=info["MR"][0].tolist())
    rows.append(dict(tag=p["tag"], vR=p["vR"], content=p["content"], chi2_theirs=p["chi2_theirs"], mine=res,
                     env_mine=dict(ainv_vR=env.ainv_vR.tolist(), ainv_MU=env.ainv_MU.tolist(), g_sm_vR=env.g_sm_vR.tolist(),
                                   lam_vR=env.lam_vR),
                     env_theirs=p["env_theirs"], pulls_theirs=p["pulls_theirs"]))
    f = res["fine"]
    print(f"{p['tag'][:28]:28s} vR={p['vR']:.1e} {p['content']:5s} theirs={p['chi2_theirs']:9.2f}  mine(fine)={f['chi2']:9.2f} "
          f"pen={f['pen']:.2g} std={res['std']['chi2']:9.2f} 1loopSM={res['1loopSM']['chi2']:9.2f} th23={f['th23']:.4f} fmax={f['fmax']:.3f}",
          flush=True)
    if p["pulls_theirs"]:
        print("    pulls theirs:", " ".join(f"{k}={p['pulls_theirs'][k]:+.2f}" for k in S.KEYS))
    print("    pulls mine  :", " ".join(f"{k}={f['pulls'][k]:+.2f}" for k in S.KEYS))
json.dump(rows, open(os.path.join(HERE, "eval_theirs.json"), "w"), indent=1)
k0 = list(envs.keys())[0]
print("env check (first):", envs[k0].ainv_vR, rows[0]["env_theirs"]["alpha_inv_vR"], envs[k0].g_sm_vR, rows[0]["env_theirs"]["g_sm_vR"],
      envs[k0].lam_vR, rows[0]["env_theirs"]["lam_vR"])
