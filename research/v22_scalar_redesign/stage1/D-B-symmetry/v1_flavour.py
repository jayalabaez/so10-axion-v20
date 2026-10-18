"""D-B-symmetry, criterion D2 for design V1 ('two-10 split'): GUT-scale proxy fit of the V1 Yukawa structure.

V1 Yukawas (renormalisable; X allows F.F.H1, F.F.H2, F.F.Delta only):
   light SM doublet h = (v_u1, v_d1) [H1 bidoublet] + (v_u2, v_d2) [H2 bidoublet] + (w_u, w_d) [Sigma (15,2,2)]
   Yd = H + F,  Ye = H - 3F,  Yu = G + s'F,  Ynu = G - 3 s'F,   M_R = C_R v_R Y126 = C_R (v_R / c_d126) F
   H = Y1 v_d1 + Y2 v_d2,  G = Y1 v_u1 + Y2 v_u2  (INDEPENDENT symmetric matrices when det[[v_d1,v_d2],[v_u1,v_u2]] != 0),
   F = Y126 w_d,  s' = w_u / w_d,  c_d126 = |w_d|.
=> Yu is an arbitrary symmetric matrix (fixed by the up masses, CKM and 6 free phases),  F = (Yd - Ye)/4,
   Ynu = Yu - 4 s' F.  (R2-C's 10+126 structure is the special case G = r H.)
Proxy (as R2-C's model_r2c.py): data run bottom-up (SM 2-loop to v_R, universal G3221 gauge factors to M_U, R2-C code
copied unedited); d, e, u masses and CKM pinned at M_U (exactly reproduced by construction); fitted: 3 PMNS angles and
the two Delta m^2 (overall scale analytic).  M_R3 = (v^2/kappa) sigma_max(F) with m_nu = kappa * (-Ynu F^-1 Ynu^T).
Perturbativity: f = C_R F / c_d126 <= sqrt(4 pi)  ->  v_R >= M_R3 / sqrt(4 pi);  |w_u| = |s'| c_d126 <= 1.
(The X-allowed d=5 terms are not needed by V1; see v1_flavour_d5.py for the robustness check with them.)
usage: python -B v1_flavour.py <vR> <content> <Mcap_or_0> <nstarts> <seed> [--floor f] [--tag t] [--nu set]
"""
from __future__ import annotations
import sys, math, json, time, argparse
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lib_r2c as L          # noqa: E402  (copied unedited from R2-C v2)
import model_r2c as M        # noqa: E402  (copied unedited from R2-C v2)

ap = argparse.ArgumentParser()
ap.add_argument("vR", type=float); ap.add_argument("content"); ap.add_argument("Mcap", type=float)
ap.add_argument("nstarts", type=int); ap.add_argument("seed", type=int)
ap.add_argument("--floor", type=float, default=0.01)
ap.add_argument("--tag", default="")
ap.add_argument("--nu", default="nufit60_sk")
ap.add_argument("--tunemin", type=float, default=0.0, help="require m_nu3 / (sigma_max(Ynu) v)^2 / M_R3) >= tunemin (no seesaw cancellation)")
args = ap.parse_args()

data = L.data_set(args.nu, floor=args.floor)
setup = M.make_setup(args.vR, data, content=args.content, MU=L.R2B_NOMINAL.get(args.content, (None, None))[1])
tg = setup["targets"]
T, S = tg.T, tg.S
sd0, se0 = tg.sd0, tg.se0
IDX = {k: i for i, k in enumerate(L.ALL_KEYS)}
VEV = L.VEV
C_R = L.C_R
yu = T[[0, 1, 2]] / VEV
Vstd = L.umix(T[IDX["s12"]], T[IDX["s23"]], T[IDX["s13"]], T[IDX["delta"]])


def unitary(p):
    U = L.umix_b(np.array([p[0]]), np.array([p[1]]), np.array([p[2]]), np.array([p[3]]))[0]
    P1 = np.exp(1j * np.array([p[4], p[5], 0.0])); P2 = np.exp(1j * np.array(p[6:9]))
    return P1[:, None] * U * P2[None, :]


def model(x):
    W = unitary(x[0:9])
    Ye = (W * se0[None, :]) @ W.T
    Yd = np.diag(sd0).astype(complex)
    Pb = np.exp(1j * np.array(x[9:12])); Pa = np.exp(1j * np.array(x[12:15]))
    Eu = Pb[:, None] * Vstd.T * Pa[None, :]          # CKM = Eu^T (E_d = 1) up to rephasing
    Yu = Eu @ np.diag(yu) @ Eu.T
    sp = 10.0**x[15] * np.exp(1j * x[16])
    F = (Yd - Ye) / 4.0
    Yn = Yu - 4.0 * sp * F
    return W, Ye, Yd, Yu, F, Yn, sp


def nu_obs(x):
    W, Ye, Yd, Yu, F, Yn, sp = model(x)
    try:
        m1 = -Yn @ np.linalg.solve(F, Yn.T)
    except np.linalg.LinAlgError:
        return None
    sc = np.abs(m1).max()
    if not np.isfinite(sc) or sc <= 0:
        return None
    m1s = m1 / sc
    wn, Nv = np.linalg.eigh(m1s.conj().T @ m1s)
    mn = np.sqrt(np.clip(wn, 0, None))
    U = W.T @ Nv
    n12, n23, n13, nd = [float(z[0]) for z in L.angles_b(U[None])]
    a21 = mn[1]**2 - mn[0]**2; a31 = mn[2]**2 - mn[0]**2
    i21, i31 = IDX["dm21"], IDX["dm31"]
    num = a21 * T[i21] / S[i21]**2 + a31 * T[i31] / S[i31]**2
    den = a21**2 / S[i21]**2 + a31**2 / S[i31]**2
    lam = max(num / den, 1e-300)
    kappa = 1e-9 * math.sqrt(lam) / sc          # GeV:  m_nu = kappa * m1
    sF = np.linalg.svd(F, compute_uv=False)
    MR = (VEV**2 / kappa) * sF                  # GeV, ascending order reversed
    MRs = np.sort(MR)
    tune = (mn[-1] * math.sqrt(lam) * 1e-9) / ((np.linalg.svd(Yn, compute_uv=False)[0] * VEV) ** 2 / MRs[-1])
    return dict(s12=n12, s23=n23, s13=n13, delta=nd, dm21=lam * a21, dm31=lam * a31, kappa=kappa, MR=MRs,
                mnu_eV=mn * math.sqrt(lam), sp=sp, sF=sF, tune=tune)


def residuals(x):
    o = nu_obs(x)
    if o is None:
        return np.full(6, 1e3)
    r = [(o["s12"]**2 - T[IDX["sin2_th12"]]) / S[IDX["sin2_th12"]],
         (o["s23"]**2 - T[IDX["sin2_th23"]]) / S[IDX["sin2_th23"]],
         (o["s13"]**2 - T[IDX["sin2_th13"]]) / S[IDX["sin2_th13"]],
         (o["dm21"] - T[IDX["dm21"]]) / S[IDX["dm21"]],
         (o["dm31"] - T[IDX["dm31"]]) / S[IDX["dm31"]]]
    pen = 0.0
    if args.Mcap > 0:
        MR3 = o["MR"][-1]
        pen = 10.0 * max(0.0, math.log10(MR3 / args.Mcap))
    r.append(pen)
    if args.tunemin > 0:
        r.append(10.0 * max(0.0, math.log10(args.tunemin / max(o["tune"], 1e-300))))
    return np.array(r)


rng = np.random.default_rng(args.seed)
npar = 17
lo = np.array([-np.pi] * 15 + [-1.0, -np.pi])
hi = np.array([np.pi] * 15 + [3.0, np.pi])
blo = np.array([-4 * np.pi] * 15 + [-2.0, -4 * np.pi])     # |s'| <= 1e3 (composition needs |s'| c_d126 <= 1)
bhi = np.array([4 * np.pi] * 15 + [3.0, 4 * np.pi])
best = []
t0 = time.time()
for k in range(args.nstarts):
    x0 = rng.uniform(lo, hi)
    try:
        res = least_squares(residuals, x0, method="trf", max_nfev=2000, x_scale="jac", bounds=(blo, bhi))
    except Exception:
        continue
    c2 = float(np.sum(res.fun**2))
    best.append((c2, res.x))
best.sort(key=lambda z: z[0])
out = {"vR": args.vR, "content": args.content, "Mcap": args.Mcap, "floor": args.floor, "nu": args.nu, "tunemin": args.tunemin,
       "nstarts": args.nstarts, "seconds": time.time() - t0, "best": []}
for c2, x in best[:8]:
    o = nu_obs(x); r = residuals(x)
    sp = o["sp"]
    MR3 = o["MR"][-1]
    vR_min = MR3 / math.sqrt(4 * math.pi)
    vR_over_c = VEV**2 / (C_R * o["kappa"])
    cmin = C_R * o["sF"].max() / math.sqrt(4 * math.pi)
    vR_max = vR_over_c * min(1.0, 1.0 / abs(sp))
    rec = {"chi2_total": c2, "chi2_nu": float(np.sum(r[:5]**2)), "pulls_nu": r[:5].tolist(), "MR_GeV": o["MR"].tolist(),
           "sin2": [o["s12"]**2, o["s23"]**2, o["s13"]**2], "delta_pmns": o["delta"], "mnu_eV": o["mnu_eV"].tolist(),
           "abs_sprime": abs(sp), "arg_sprime": float(np.angle(sp)), "vR_min_from_f<=sqrt4pi": vR_min,
           "vR_max_from_composition": vR_max, "vR_window_contains_vR": bool(vR_min <= args.vR <= vR_max),
           "c_d126_min": cmin, "seesaw_tuning_m3_over_mD3sq_MR3": o["tune"], "x": x.tolist()}
    out["best"].append(rec)
tag = args.tag or f"v1_{args.content}_{args.vR:.0e}_cap{args.Mcap:.0e}_s{args.seed}"
(HERE / "out").mkdir(exist_ok=True)
(HERE / "out" / f"{tag}.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
b = out["best"][0]
print(f"{tag}: best chi2 = {b['chi2_total']:.4g} (nu {b['chi2_nu']:.4g}), M_R = {['%.3g' % m for m in b['MR_GeV']]}, "
      f"|s'| = {b['abs_sprime']:.3g}, vR window [{b['vR_min_from_f<=sqrt4pi']:.3g}, {b['vR_max_from_composition']:.3g}], "
      f"sin2 = {['%.4f' % s for s in b['sin2']]}, tuning {b['seesaw_tuning_m3_over_mD3sq_MR3']:.3g}, {out['seconds']:.0f}s", flush=True)
