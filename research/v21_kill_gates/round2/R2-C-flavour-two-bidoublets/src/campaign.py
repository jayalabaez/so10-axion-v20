"""Global-search campaign on the GUT-scale proxy for one or more configurations.
usage: campaign.py OUTTAG vR[,vR...] I|II nDE nCMA nBH nLM [floor] [nu] [MU]
Saves campaign_<OUTTAG>_<vR>_<type>.json with per-optimiser results and the distinct minima."""
import sys, json, time, math
import numpy as np
import lib_r2c as L, model_r2c as M, search_r2c as S

tag = sys.argv[1]
vRs = [float(v) for v in sys.argv[2].split(",")]
typ = sys.argv[3]
nDE, nCMA, nBH, nLM = [int(v) for v in sys.argv[4:8]]
floor = float(sys.argv[8]) if len(sys.argv) > 8 else 0.01
nu = sys.argv[9] if len(sys.argv) > 9 else "nufit60_sk"
MU = float(sys.argv[10]) if len(sys.argv) > 10 and sys.argv[10] != "auto" else None
content = sys.argv[11] if len(sys.argv) > 11 else "C2"

# literature / round-1 seeds (r, s) -- W re-optimised
SEEDS = {"MummidiPatel2021_r77.4_s0.314-0.028i": (77.4, complex(0.314, -0.028)),
         "OP2019_rescue_r66_s0.39": (66.0, complex(0.39, 0.0)),
         "round1_skeptic_r63.7_s0.475": (63.7, 0.4753 * np.exp(0.0197j))}


def distinct(res, lay, tg, tol=0.05):
    out = []
    for c, x in sorted(((r[0], r[1]) for r in res), key=lambda t: t[0]):
        key = (10**x[9], 10**x[10], (x[11] + math.pi) % (2 * math.pi) - math.pi)
        dup = False
        for o in out:
            if abs(o["chi2"] - c) < tol * max(1.0, 0.002 * c) and abs(o["r"] - key[0]) / key[0] < 0.01 and abs(o["s_abs"] - key[1]) / max(key[1], 1e-6) < 0.01:
                dup = True; break
        if not dup:
            R, cc, aux = M.proxy_eval(x[None], lay, tg, want_obs=True)
            out.append({"chi2": float(c), "chi2_unmasked": float(cc[0]), "r": float(key[0]), "s_abs": float(key[1]), "s_arg": float(key[2]), "x": list(map(float, x)),
                        "pulls": {k: float(R[0, i]) for i, k in enumerate(L.ALL_KEYS)},
                        "delta_pmns_deg": float(math.degrees(aux["delta_pmns"][0]) % 360),
                        "m_nu_eV_proxy": [float(v) for v in aux["mn"][0]], "rho_eff": float(aux["rho_eff"][0])})
        if len(out) >= 25:
            break
    return out


for vR in vRs:
    t00 = time.time()
    d = L.data_set(nu, floor)
    setup = M.make_setup(vR, d, MU=MU, content=content)
    tg = setup["targets"]
    lay = M.Layout(typeII=(typ == "II"))
    P = S.Problem(lay, tg)
    import os
    if os.environ.get("R2C_TCAP"):
        P.tcap = float(os.environ["R2C_TCAP"]); P.hi[12] = min(P.hi[12], P.tcap)
    if os.environ.get("R2C_MASK"):
        P.mask = np.array([k in os.environ["R2C_MASK"].split(",") for k in L.ALL_KEYS])
    rng = np.random.default_rng(abs(hash((tag, vR, typ))) % (2**32))
    allres = {}
    log = open(f"campaign_{tag}_{vR:.0e}_{typ}.log", "a")

    def note(msg):
        log.write(msg + "\n"); log.flush()
    note(f"== {tag} vR={vR:.1e} type={typ} floor={floor} nu={nu} MU={setup['env']['MU']:.3e} content={content} tcap={P.tcap} mask={os.environ.get('R2C_MASK')}")
    for name, fn, n in [("de", S.run_de, nDE), ("cma", S.run_cma, nCMA), ("bh", S.run_bh, nBH), ("ms_lm", S.run_ms_lm, nLM)]:
        t0 = time.time(); P.nev = 0
        res = []
        for i in range(n):
            res += fn(P, rng, 1)
            if (i + 1) % 10 == 0 or i == n - 1:
                note(f"   {name} {i+1}/{n}: best so far {min(r[0] for r in res):.3f}  t={time.time()-t0:.0f}s")
        allres[name] = res
        note(f"{name}: n={n} nev={P.nev} t={time.time()-t0:.0f}s " + json.dumps(S.summarize(res)))
    # literature seeds: fix r,s (narrow box) for a DE over W, then free LM
    seedres = []
    for sname, (r0, s0) in SEEDS.items():
        lo0, hi0 = P.lo.copy(), P.hi.copy()
        P.lo[9], P.hi[9] = math.log10(r0) - 0.004, math.log10(r0) + 0.004
        P.lo[10], P.hi[10] = math.log10(abs(s0)) - 0.004, math.log10(abs(s0)) + 0.004
        P.lo[11], P.hi[11] = np.angle(s0) - 0.01, np.angle(s0) + 0.01
        rr = S.run_de(P, rng, 3)
        P.lo, P.hi = lo0, hi0
        for c, x, cde in rr:
            x2, c2 = S.lm_polish(P, x)
            seedres.append((c2, x2, sname, cde))
        note(f"seed {sname}: fixed-(r,s) DE chi2 = {[round(t[2],2) for t in rr]} -> free LM {[round(t[0],2) for t in seedres[-3:]]}")
    allres["lit_seeds"] = [(c, x) for c, x, _, _ in seedres]
    pooled = [(r[0], r[1]) for k in allres for r in allres[k]]
    dist = distinct(pooled, lay, tg)
    out = {"tag": tag, "vR": vR, "type": typ, "floor": floor, "nu": nu, "content": content, "env": setup["env"],
           "tcap": P.tcap, "mask": os.environ.get("R2C_MASK"),
           "targets": {"T": tg.T.tolist(), "S": tg.S.tolist(), "sd0": tg.sd0.tolist(), "se0": tg.se0.tolist(), "eta": tg.info["eta"]},
           "summary": {k: S.summarize(v) for k, v in allres.items()},
           "all_final_chi2": {k: sorted(float(r[0]) for r in v) for k, v in allres.items()},
           "seed_detail": [{"seed": nm, "chi2_fixed_rs": float(cf), "chi2_free": float(c)} for c, x, nm, cf in seedres],
           "distinct_minima": dist, "time_s": time.time() - t00}
    json.dump(out, open(f"campaign_{tag}_{vR:.0e}_{typ}.json", "w"), indent=1)
    note(f"DONE vR={vR:.1e} best={dist[0]['chi2']:.3f} t={time.time()-t00:.0f}s")
    log.close()
