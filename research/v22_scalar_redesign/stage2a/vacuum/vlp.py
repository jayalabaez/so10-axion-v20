#!/usr/bin/env python3
"""Local coupling LP at a G3211 -> SM vacuum point of v22-L2 (531-real chart, 85 couplings).

Own implementation generalising R2-A r2_lp6.py and its skeptic's sk_phase1.py (both only read), with their three known
bug fixes built in: (1) gauge copies of the vacuum are recognised by their exact row-value vector J(q) (any discrete
image of z* has J = J*, so it can never be a competitor; no hand-made orbit test), and only STRICTLY lower points are
cut; (2) no spurious BFB row (the pure-doublet ray is added only when it is computed); (3) every competitor row is
normalised.  Also from the skeptic: the Phi210-doublet admixture beta of the EW target is FREE (iterated), U-iteration
with restarts, a phase-1 objective, and the 40000-sample / 30-polish singlet-subspace screen at the end.

Constraints (all linear in c = N y at fixed light subspaces U; N = exact stationarity null space):
  boxes |c_i| <= box_i (vc.boxes: 40 / 2 / 1 per degree, eps rows / F1 factor)
  heavy  : Q0^+ A_k(c) Q0 >= t for every SM component (Q0 = complement of the Goldstone kernel [and of light parts])
  light  : interlacing  (U^+ A U <= eps_hi, Q0^+ A Q0 >= eps_lo, Qc^+ A Qc >= t), sandwich for m = 1 components
  EW     : exact eigen-equation A_(1,2)(c) a* = lam_ew a*  (composition (|r|, s, f_Sigma) of the H10 / 126bar part,
           beta free: updated each outer iteration so that a* is the light doublet of the current c)
  a0     : |eig sum_i c_i M_i| <= 16 pi * unit  (6x6 singlet channel, trace lemma)
  BFB    : V4_c(u_k) >= eps_bfb on the ray bank (+ the EW doublet ray + the octet rays, when computed)
  competitors: V_c(q*) <= V_c(q_k) - mu t mf_k  (banked deep points, descent endpoints, screen points)
  octet cubics (--octet): |T_c(v,v,v)| <= delta for v in the zero-weight plane of the light (8,1)_0 octet
           (two orthogonal directions bound the unique d-symbol invariant) and along the f eps maximiser of the
           (8,3)_0 octet;  mixed cubics (--mixed): (8,1)(8,3)(8,3) and (8,3)(6,2)(6bar,2) analogues
  light trilinears (--lightb d): |v_l . T_c(u,u,.)| <= d for the light (1,1)_0 eigen-directions v_l (u = EW direction)
Objectives: maxt (default) | phase1 (min s, competitor rows relaxed by s) | rand:<seed> | maxleff (stage B, Kelley)
usage: python -B vlp.py <pt_tag> <out> --content L0|La|Lb|V0|D1|Da|Db [--ew 66,0.43,0.09,0.17] [options]
"""
from __future__ import annotations

import argparse
import json
import warnings
warnings.filterwarnings("ignore")
import math
import sys
import time

import numpy as np
from scipy.optimize import linprog, minimize

import vc
import vdcore
import vprep

C = vc.C
ap = argparse.ArgumentParser()
ap.add_argument("tag")
ap.add_argument("out")
ap.add_argument("--content", default="L0")
ap.add_argument("--ew", default="66,0.43,0.09,0.17")
ap.add_argument("--ew_lambda", type=float, default=1e-7)
ap.add_argument("--eps_lo", type=float, default=5e-7)
ap.add_argument("--eps_hi", type=float, default=3e-6)
ap.add_argument("--tmin", type=float, default=1e-3)
ap.add_argument("--box_scale", type=float, default=1.0)
ap.add_argument("--box_override", default="")
ap.add_argument("--unit", type=float, default=0.5)
ap.add_argument("--mu", type=float, default=0.1)
ap.add_argument("--eps_bfb", type=float, default=1e-4)
ap.add_argument("--banks", default="deep", help="comma list: deep (all banked deep points, A=0 and A=A* embeddings) "
                                                 "and/or npz files with Q (n,531)")
ap.add_argument("--no_rays", action="store_true")
ap.add_argument("--no_subbfb", action="store_true", help="do not add the 4000 SM-singlet-subspace BFB rays")
ap.add_argument("--rays_extra", default="", help="comma list of npz with run_dirs (or Q) used as extra BFB rays")
ap.add_argument("--octet", action="store_true")
ap.add_argument("--delta8", type=float, default=7e-14)
ap.add_argument("--delta83", type=float, default=1.2e-7)
ap.add_argument("--mixed", type=float, default=0.0, help="bound for the mixed light cubics (0 = off)")
ap.add_argument("--lightb", type=float, default=0.0)
ap.add_argument("--screen", action="store_true")
ap.add_argument("--screen_n", type=int, default=20000)
ap.add_argument("--screen_polish", type=int, default=12)
ap.add_argument("--objective", default="maxt")
ap.add_argument("--uiter", type=int, default=6)
ap.add_argument("--restarts", type=int, default=0)
ap.add_argument("--iters", type=int, default=400)
ap.add_argument("--warm", default=None)
ap.add_argument("--lamdir_min", type=float, default=None)
ap.add_argument("--lamdir_max", type=float, default=None)
ap.add_argument("--leff_min", type=float, default=None, help="stage B: require lambda_eff >= value (Kelley)")
ap.add_argument("--leff_max", type=float, default=None, help="require lambda_direct - (stage-B lower) ... (via lamdir)")
ap.add_argument("--final_screen_n", type=int, default=40000)
ap.add_argument("--final_rounds", type=int, default=4)
ap.add_argument("--max_reps", type=int, default=60)
ap.add_argument("--bfbscreen", type=int, default=0, help="random starts of the full-chart quartic BFB search per SDP solve")
ap.add_argument("--dscreen", type=int, default=0, help="quick full-chart descents per SDP solve (in-loop global screen)")
ap.add_argument("--dscreen_maxiter", type=int, default=1500)
ap.add_argument("--track", type=int, default=8, help="lower basins re-descended in every in-loop descent round")
ap.add_argument("--margin_wc", type=float, default=1.0)
ap.add_argument("--margin_wb", type=float, default=1e-2)
ap.add_argument("--margin_max", type=float, default=1.0)
ap.add_argument("--bfb_dom", type=float, default=0.0, help="eps of the sufficient block-norm BFB condition (0 = off)")
ap.add_argument("--dom_safety", type=float, default=0.1)
ap.add_argument("--leff_all", action="store_true", help="the lambda_eff >= leff_min cut uses lambda_eff_all (light singlets integrated out)")
ap.add_argument("--final_screen_polish", type=int, default=30)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--no_sdp", action="store_true")
ap.add_argument("--sdp_verbose", action="store_true")
ap.add_argument("--lp_tol", type=float, default=1e-9)
ap.add_argument("--polish", type=int, default=0, help="LP cutting-plane polish iterations after the SDP (0 = none)")
args = ap.parse_args()
T0 = time.time()
log = vc.Logger(vc.BIG / f"{args.out}.log")

# ------------------------------------------------------------------ point data
P = np.load(vc.BIG / f"pt_{args.tag}.npz")
PJ = json.load(open(vc.BIG / f"pt_{args.tag}.json"))
q0 = P["q"]
VAL0 = P["values"]
labels = [str(x) for x in P["labels"]]
nb = len(labels)
mult = P["m"]
realmult = P["real_mult"]
A = [P[f"A{k}"] for k in range(nb)]
Wk = [P[f"W{k}"] for k in range(nb)]
Gold0 = [P[f"G{k}"].astype(complex) for k in range(nb)]
kb = {l: k for k, l in enumerate(labels)}
kd = kb["(1,2)_{Y=+1/2}"]
ks = kb["(1,1)_{Y=0}"]
Nn = P["neutral"]
meta = [b["meta"] for b in PJ["blocks"]]
pt = PJ["point"]
zstar = np.array([pt["p"], pt["a"], pt["omega"], pt["omega_R"], pt["omega_BL"], pt["r"], pt["s"], pt["x"]])
boxes = vc.boxes(args.box_scale, {k: float(v) for k, v in (it.split(":") for it in args.box_override.split(",") if it)})
# scaled null space: c = D Nt y with D = diag(boxes), Nt orthonormal null space of stat_rows D  (well-conditioned LP/SDP)
Dsc = np.diag(boxes)
_, sv, vt = np.linalg.svd(P["stat_rows"] @ Dsc, full_matrices=True)
rk = int(np.sum(sv > 1e-10 * sv[0]))
Nmat = Dsc @ vt[rk:].T
ny = Nmat.shape[1]
Ay = [np.einsum("ia,ijk->ajk", Nmat, A[k]) for k in range(nb)]
log(f"[{args.out}] point {args.tag} {pt}; ny = {ny}; content {args.content}; objective {args.objective}")

HESS = None


def hess_rows():
    global HESS
    if HESS is None:
        _, _, HESS = vc.rows_at(q0, hessian=True)
    return HESS


def full_hessian(c):
    H = np.einsum("k,kij->ij", c, hess_rows(), optimize=True)
    return 0.5 * (H + H.T)


# ------------------------------------------------------------------ content
SPECS = {
    "V0": {},
    "D1": {"(1,2)_{Y=+1/2}": ("sub", 1)},
    "L0": {"(1,2)_{Y=+1/2}": ("ew",)},
    "La": {"(1,2)_{Y=+1/2}": ("ew",), "(8,1)_{Y=0}": ("sub", 1), "(8,3)_{Y=0}": ("sandwich",)},
    "Lae": {"(1,2)_{Y=+1/2}": ("ew",), "(8,1)_{Y=0}": ("eig", 1), "(8,3)_{Y=0}": ("sandwich",)},
    "Lb": {"(1,2)_{Y=+1/2}": ("ew",), "(8,3)_{Y=0}": ("sandwich",), "(6bar,2)_{Y=+1/6}": ("sandwich",)},
    "Da": {"(1,2)_{Y=+1/2}": ("sub", 1), "(8,1)_{Y=0}": ("sub", 1), "(8,3)_{Y=0}": ("sandwich",)},
    "Db": {"(1,2)_{Y=+1/2}": ("sub", 1), "(8,3)_{Y=0}": ("sandwich",), "(6bar,2)_{Y=+1/6}": ("sandwich",)},
}
spec = {"(1,1)_{Y=0}": ("sub", 2)}
spec.update(SPECS[args.content])
for lab in spec:
    assert lab in kb, lab
EW = any(v[0] == "ew" for v in spec.values())
expected_light = sum(int(realmult[kb[l]]) * (v[1] if v[0] == "sub" else (1 if v[0] in ("ew", "eig") else int(mult[kb[l]])))
                     for l, v in spec.items())
log(f"spec {spec}; expected light real modes {expected_light}")

# ------------------------------------------------------------------ EW composition map (H10 / 126bar slots)
N_U = np.zeros(10, complex)
N_U[8] = 1 / math.sqrt(2)
N_U[9] = 1j / math.sqrt(2)
N_D = np.conj(N_U)
OMEGA_PAIRS = [(0, 1), (2, 3), (4, 5)]
SO4 = [6, 7, 8, 9]


def perm_sign(seq):
    seq = list(seq)
    s = 1
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                s = -s
    return s


def form_get(form, idx):
    if len(set(idx)) < 5:
        return 0j
    key = tuple(sorted(idx))
    val = form.get(key, 0j)
    return perm_sign(idx) * val if val != 0 else 0j


def S_vector(form):
    """126bar colour-singlet (15,2,2) bidoublet as an SO(4) vector (R2-A r2_compose convention)."""
    S = np.zeros(10, complex)
    for sig in SO4:
        rest = [m_ for m_ in SO4 if m_ != sig]
        for (a_, b_) in OMEGA_PAIRS:
            S[sig] += perm_sign(rest + [sig]) * form_get(form, (a_, b_, rest[0], rest[1], rest[2]))
    return S


def comp_of_q(q):
    st = C.chart.unpack(np.asarray(q[:486], float))
    h = np.asarray(st.h, complex)
    S = S_vector(st.sigma)
    vu, vd, wu, wd = N_U.conj() @ h, N_D.conj() @ h, N_U.conj() @ S, N_D.conj() @ S
    norms = vc.block_norms(q)
    tot = sum(v * v for v in norms.values())
    return {"vu": vu, "vd": vd, "wu": wu, "wd": wd, "frac": {k: v * v / tot for k, v in norms.items()}}


def config_of_a(a):
    return np.real(Nn @ a)


def comp_of_a(a):
    c = comp_of_q(config_of_a(a))
    r = c["vu"] / c["vd"] if abs(c["vd"]) > 0 else np.inf
    s = (c["wu"] / c["wd"]) / r if abs(c["wd"]) > 0 and np.isfinite(r) and r != 0 else np.nan
    c.update(r=r, s=s)
    return c


slots_HS = [j for j, mm in enumerate(meta[kd]) if mm["block"] in ("H10", "Sigma126bar")]
slots_P = [j for j, mm in enumerate(meta[kd]) if mm["block"] not in ("H10", "Sigma126bar")]
A_EW = None
BETA = np.zeros(len(slots_P), complex)
X_HS = None
EW_INFO = {}
if EW:
    r_t, sre, sim, fsig = map(float, args.ew.split(","))
    s_t = sre + 1j * sim
    md = int(mult[kd])

    def lin(x8):
        a_ = np.zeros(md, complex)
        a_[slots_HS] = x8[:4] + 1j * x8[4:]
        c_ = comp_of_q(config_of_a(a_))
        return np.array([c_["vu"], c_["vd"], c_["wu"], c_["wd"]])

    Lm = np.zeros((8, 8))
    for j in range(8):
        e = np.zeros(8)
        e[j] = 1.0
        v = lin(e)
        Lm[:, j] = np.concatenate([v.real, v.imag])
    log(f"EW map rank {np.linalg.matrix_rank(Lm)} cond {np.linalg.cond(Lm):.3g}; slots H/Sigma {slots_HS}, Phi {slots_P}")

    def x_for(zeta):
        tgt = np.array([r_t, 1.0, s_t * r_t * zeta, zeta], complex)
        x8 = np.linalg.solve(Lm, np.concatenate([tgt.real, tgt.imag]))
        a_ = np.zeros(md, complex)
        a_[slots_HS] = x8[:4] + 1j * x8[4:]
        return a_ / np.linalg.norm(a_)

    from scipy.optimize import brentq
    g_ = lambda z: comp_of_a(x_for(z))["frac"]["Sigma126bar"] - fsig
    zs = np.logspace(-5, 5, 201)
    gv = [g_(z) for z in zs]
    z0 = None
    for i in range(len(zs) - 1):
        if gv[i] * gv[i + 1] < 0:
            z0 = brentq(g_, zs[i], zs[i + 1], xtol=1e-14)
            break
    assert z0 is not None, "no zeta for f_Sigma"
    X_HS = x_for(z0)
    A_EW = X_HS.copy()
    cm = comp_of_a(A_EW)
    EW_INFO = {"target": {"|r|": r_t, "s": [sre, sim], "f_Sigma": fsig}, "zeta": z0,
               "achieved_beta0": {"|r|": float(abs(cm["r"])), "s": [float(np.real(cm["s"])), float(np.imag(cm["s"]))],
                                  "frac": cm["frac"]}}
    log(f"EW target: |r| = {abs(cm['r']):.6g}, s = {cm['s']:.6g}, f_Sigma = {cm['frac']['Sigma126bar']:.4f}")


def set_beta(beta):
    global A_EW
    a_ = X_HS.copy()
    a_[slots_P] = beta
    A_EW = a_ / np.linalg.norm(a_)


def beta_update(c):
    """beta such that the Phi-slot rows of A a* = lam a* hold for the current c (heavy Phi doublet responds)."""
    Ad = np.einsum("k,kij->ij", c, A[kd])
    Ad = 0.5 * (Ad + Ad.conj().T)
    App = Ad[np.ix_(slots_P, slots_P)] - args.ew_lambda * np.eye(len(slots_P))
    ApH = Ad[np.ix_(slots_P, slots_HS)]
    return -np.linalg.solve(App, ApH @ X_HS[slots_HS])


# ------------------------------------------------------------------ unitarity, BFB, competitors
UT = np.load(vc.BIG / "unit_traces.npz")
Mi = UT["Mi"]
MiY = np.einsum("ia,ijk->ajk", Nmat, Mi)
UB = 16 * math.pi * args.unit
BFB_J = np.zeros((0, vc.NPAR))
if not args.no_rays:
    BFB_J = np.load(vc.BIG / "rays.npz")["J4"]
COMP_J = []
COMP_M = []
ADDED_Q = []
COMP_SRC = []
Jstar = VAL0.copy()


# GAUGE-INVARIANT competitor margin (fix of the R2-A bug-1 class): the Euclidean distance |q_k - q*| is large for a
# gauge-rotated near-copy of the vacuum, which then received the full margin mu t and squeezed t artificially.  The
# margin factor now uses the row-value distance |J(q_k) - J*| (zero on the whole gauge orbit), normalised by the value
# distance of a displacement of 0.5 orthogonal to the orbit:  mf = min(1, (|dJ| / dJ_ref)^4).
def _jref():
    rng_ = np.random.default_rng(424)
    Tq = np.linalg.svd(P["tangents"], full_matrices=False)[0][:, :35]
    vals_ = []
    for _ in range(4):
        v = rng_.normal(size=vc.N)
        v -= Tq @ (Tq.T @ v)
        v /= np.linalg.norm(v)
        vals_.append(float(np.linalg.norm(vc.J_values((q0 + 0.5 * v)[None, :])[0] - VAL0)))
    return float(np.mean(vals_))


JREF = _jref()


def margin_factor(q, J=None):
    if J is None:
        J = vc.J_values(np.asarray(q)[None, :])[0]
    return min(1.0, (float(np.linalg.norm(J - VAL0)) / JREF) ** 4)


def is_copy(J):
    return float(np.max(np.abs(J - Jstar))) <= 1e-9 * max(1.0, float(np.max(np.abs(Jstar))))


def add_points(Q, src):
    """append non-copy points to the competitor bank; returns the list of new indices."""
    Q = np.atleast_2d(Q)
    J = vc.J_values(Q)
    new = []
    for qq, jj, ss in zip(Q, J, src):
        if is_copy(jj):
            continue
        COMP_J.append(jj)
        COMP_M.append(margin_factor(qq, jj))
        COMP_SRC.append(ss)
        new.append(len(COMP_J) - 1)
        if not ss.startswith(("R2A/", "R2Ask/", "DA/", "DAsk/")):
            ADDED_Q.append(np.asarray(qq, float))
    if new and ADDED_Q:
        np.savez_compressed(vc.BIG / f"{args.out}_comp.npz", Q=np.array(ADDED_Q))
    return new


for item in [x for x in args.banks.split(",") if x]:
    if item == "deep":
        D = np.load(vc.BIG / "deep486.npz")
        Q486 = D["Q"]
        src = [str(s) for s in D["src"]]
        Astar = q0[vc.BLOCKS["A45"]]
        nphi = np.linalg.norm(q0[vc.BLOCKS["Phi210"]])
        Qa = np.hstack([Q486, np.zeros((len(Q486), 45))])
        scale = (np.linalg.norm(Q486[:, :210], axis=1) / nphi)[:, None]
        Qb = np.hstack([Q486, scale * Astar[None, :]])
        n1 = len(add_points(Qa, [s + "|A=0" for s in src]))
        n2 = len(add_points(Qb, [s + "|A=A*" for s in src]))
        log(f"bank deep486: {n1} + {n2} competitor points (A = 0 / A = A* x |Phi_k|/|Phi*|)")
    else:
        Z = np.load(item if (":" in item or item.startswith("/")) else vc.BIG / item)
        Qx = Z["Q"]
        if Qx.shape[1] == 486:
            Qx = np.hstack([Qx, np.zeros((len(Qx), 45))])
        n1 = len(add_points(Qx, [f"{item}#{i}" for i in range(len(Qx))]))
        log(f"bank {item}: {n1} competitor points")
for item in [x for x in args.rays_extra.split(",") if x]:
    Z = np.load(item if (":" in item) else vc.BIG / item)
    Rd = Z["run_dirs"] if "run_dirs" in Z.files else Z["Q"]
    if len(Rd):
        Rd = Rd / np.linalg.norm(Rd, axis=1)[:, None]
        BFB_J = np.vstack([BFB_J, vc.J_values(Rd) * (vc.DEG == 4)[None, :]])
        log(f"extra BFB rays from {item}: {len(Rd)}")
log(f"competitors {len(COMP_J)}, BFB rays {len(BFB_J)}")

# ------------------------------------------------------------------ singlet-subspace screen
SF = np.load(vc.BIG / "subfit.npz")
MONS = SF["mons"]
KFIT = SF["Kfit"]
TOP = (MONS @ vprep.SUB_DEGS) == 4
RNG = np.random.default_rng(args.seed)


def sub_sample(n, rng):
    return np.column_stack([rng.uniform(-2.5, 2.5, (n, 5)), rng.uniform(0, 3, (n, 1)), rng.uniform(0, 2.5, (n, 1)),
                            rng.uniform(0, 8, (n, 1))])


SCR_Z = sub_sample(args.screen_n, RNG)
SCR_X = vprep.sub_X(SCR_Z, MONS)
# dense BFB rays on the SM-singlet subspace (exact through the subspace polynomial fit): sign conventions z5..z7 >= 0
_dz = RNG.normal(size=(4000, 8))
_dz[:, 5:] = np.abs(_dz[:, 5:])
_dz /= np.linalg.norm(_dz, axis=1)[:, None]
_qn = np.array([np.linalg.norm(vprep.q_of_z(z_)) for z_ in _dz])
SUB_BFB = ((vprep.sub_X(_dz, MONS) * TOP[None, :]) @ KFIT) / _qn[:, None] ** 4
if not args.no_subbfb:
    BFB_J = np.vstack([BFB_J, SUB_BFB])
    log(f"added {len(SUB_BFB)} SM-singlet-subspace BFB rays (total {len(BFB_J)})")


def screen(c, n_polish, Zs=None, Xs=None):
    """minimise V_c on the SM-singlet subspace (exact polynomial): returns V*(fit), the polished points
    [(V, z, converged)], and runaway directions [(V4, zhat)] (quartic part < eps_bfb on the subspace unit sphere)."""
    coef = KFIT @ c
    Xf = lambda z: vprep.sub_X(np.asarray(z)[None, :], MONS)[0]
    Vz = lambda z: float(Xf(z) @ coef)
    Vst = Vz(zstar)
    Zs = SCR_Z if Zs is None else Zs
    Xs = SCR_X if Xs is None else Xs
    vs = Xs @ coef
    order = np.argsort(vs)[:n_polish]
    found = []
    for j in list(order) + [None]:
        z0_ = zstar.copy() if j is None else Zs[j]
        with np.errstate(all="ignore"):
            r = minimize(Vz, z0_, method="BFGS", options={"gtol": 1e-9, "maxiter": 2000})
        zz = np.array(r.x)
        zz[5:] = np.abs(zz[5:])
        conv = bool(np.all(np.isfinite(zz)) and np.max(np.abs(zz)) < 1e4 and np.isfinite(r.fun))
        found.append((float(r.fun) if np.isfinite(r.fun) else -np.inf, zz, conv))
    V4z = lambda z: float((Xf(z) * TOP) @ coef)
    dirs = RNG.normal(size=(4000, 8))
    dirs[:, 5:] = np.abs(dirs[:, 5:])
    dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    v4 = (vprep.sub_X(dirs, MONS) * TOP[None, :]) @ coef
    runaways = []
    for j in np.argsort(v4)[:8]:
        with np.errstate(all="ignore"):
            r = minimize(lambda z: V4z(z / np.linalg.norm(z)), dirs[j], method="BFGS", options={"gtol": 1e-11, "maxiter": 400})
        zh = np.array(r.x) / np.linalg.norm(r.x)
        zh[5:] = np.abs(zh[5:])
        if V4z(zh) < args.eps_bfb * float(np.linalg.norm(vprep.q_of_z(zh))) ** 4:
            runaways.append((V4z(zh), zh))
    for Vm, zm, conv in found:
        if not conv:
            zh = zm / np.linalg.norm(zm)
            zh[5:] = np.abs(zh[5:])
            runaways.append((V4z(zh), zh))
    found.sort(key=lambda t_: t_[0])
    return Vst, found, runaways


# ------------------------------------------------------------------ cubic rows (third derivatives) helpers
GRAD0 = None


def grads_at(q):
    return vc.rows_at(q, hessian=False)[1]


def T_uu(u, h=0.3):
    """T_k(u,u,.) for every row (85 x 531): exact second difference of the (cubic) row gradients."""
    global GRAD0
    if GRAD0 is None:
        GRAD0 = P["grads"]
    gp = grads_at(q0 + h * u)
    gm = grads_at(q0 - h * u)
    return (gp - 2 * GRAD0 + gm) / h ** 2


ops = C.label_operators()
H1, H2 = ops["H1"], ops["H2"]


def real_span(k, U):
    M = Wk[k] @ U
    X = np.hstack([M.real, M.imag])
    u_, s_, _ = np.linalg.svd(X, full_matrices=False)
    return u_[:, s_ > 1e-8 * s_[0]]


def octet_space(k, c, nl=1):
    """real light octet subspace (8 nl dims) of component k at couplings c: lowest eigenspace of the real block."""
    comp = [x for x in C.real_components("SM") if x["label"] == labels[k]][0]
    R = comp["W"]
    Hc = R.T @ full_hessian(c) @ R
    w, V = np.linalg.eigh(0.5 * (Hc + Hc.T))
    dim = 8 * nl if labels[k].startswith("(8,1)") else R.shape[1]
    return R @ V[:, :dim], w[:dim]


def zero_weight_plane(L):
    """zero-weight vectors of the colour Cartan subalgebra inside the real subspace L (columns orthonormal)."""
    M = np.vstack([L.T @ H1 @ L, L.T @ H2 @ L])
    _, s_, vt_ = np.linalg.svd(M)
    nz = int(np.sum(s_ < 1e-8 * max(1.0, s_[0])))
    return L @ vt_[-nz:].T if nz else np.zeros((L.shape[0], 0))


OCT = {}


def setup_octet_constraints(c):
    """vectors v and per-row cubic values T_k(v,v,v) for the octet-cubic constraints (fixed at this U)."""
    rows = []
    info = {}
    if "(8,1)_{Y=0}" in spec:
        k8 = kb["(8,1)_{Y=0}"]
        L, w = octet_space(k8, c)
        if k8 in EIGV:      # exact eigenvector: the light octet is exactly the lift of u8 (orthonormal real span)
            comp_ = [x for x in C.real_components("SM") if x["label"] == "(8,1)_{Y=0}"][0]
            R_ = comp_["W"]
            Hc_ = R_.T @ full_hessian(c) @ R_
            w_, V_ = np.linalg.eigh(0.5 * (Hc_ + Hc_.T))
            L = R_ @ V_[:, :8]
        Z = zero_weight_plane(L)
        info["(8,1) light eigenvalues"] = w.tolist()
        info["(8,1) zero-weight dim"] = int(Z.shape[1])
        for j in range(Z.shape[1]):
            v = Z[:, j]
            T = T_uu(v)
            rows.append(("(8,1)_zw%d" % j, T @ v, args.delta8, v))
        OCT["L8"] = L
    if "(8,3)_{Y=0}" in spec:
        k83 = kb["(8,3)_{Y=0}"]
        comp = [x for x in C.real_components("SM") if x["label"] == "(8,3)_{Y=0}"][0]
        R = comp["W"]
        if "v83" not in OCT:
            # reference invariant from the Phi^3 row: maximise |T_ref(v,v,v)| over unit v in the (8,3) space
            ref = vc.IDX["lambda::O17_B01_Phi_cubic"]
            p_ = vc.POLYS[vc.IDS[ref]]
            Tref = np.zeros((R.shape[1], R.shape[1], R.shape[1]))
            for a_ in range(R.shape[1]):
                # cubic row: Hessian is linear in q -> T(e_a,.,.) = H(q0 + e_a) - H(q0)
                Hp = C.poly_derivatives(p_, C.w_of_q(q0 + R[:, a_]))[2]
                Hm = C.poly_derivatives(p_, C.w_of_q(q0))[2]
                Hd = np.real(C._hess_to_q(Hp - Hm))
                Tref[a_] = R.T @ Hd @ R
            f = lambda x: -abs(np.einsum("abc,a,b,c->", Tref, x, x, x)) / np.linalg.norm(x) ** 3
            best = None
            rng = np.random.default_rng(7)
            for _ in range(20):
                r = minimize(f, rng.normal(size=R.shape[1]), method="BFGS")
                if best is None or r.fun < best.fun:
                    best = r
            v83 = R @ (best.x / np.linalg.norm(best.x))
            OCT["v83"] = v83
            OCT["Tref83"] = float(-best.fun)
        v = OCT["v83"]
        T = T_uu(v)
        rows.append(("(8,3)_feps", T @ v, args.delta83, v))
        info["(8,3) ref |T(v,v,v)| of O17"] = OCT["Tref83"]
        if args.mixed > 0 and "L8" in OCT:
            # (8,1)(8,3)(8,3): sum over an orthonormal basis of the (8,3) space of T(v8, e, e) for v8 in the light (8,1)
            Z = zero_weight_plane(OCT["L8"])
            for j in range(Z.shape[1]):
                v8 = Z[:, j]
                Tm = np.zeros(vc.NPAR)
                for a_ in range(R.shape[1]):
                    e = R[:, a_]
                    Tp = T_uu(e)
                    Tm += Tp @ v8
                rows.append(("mixed(8,1)(8,3)^2_zw%d" % j, Tm, args.mixed, v8))
    OCT["rows"] = rows
    OCT["info"] = info
    return rows


LIGHTB = {}


def setup_lightb(c, Ucur):
    """b_k = T_k(u,u,.) along the EW direction u; light (1,1)_0 directions from U."""
    u = config_of_a(A_EW)
    u = u / np.linalg.norm(u)
    Tb = T_uu(u)                      # 85 x 531
    Vl = real_span(ks, Ucur[ks])
    LIGHTB["u"] = u
    LIGHTB["Tb"] = Tb
    LIGHTB["Vl"] = Vl
    LIGHTB["J4u"] = vc.J_values(u[None, :])[0] * (vc.DEG == 4)
    return Tb, Vl


# ------------------------------------------------------------------ LP machinery
def compl(M, m):
    if M is None or M.shape[1] == 0:
        return np.eye(m, dtype=complex)
    u_, s_, _ = np.linalg.svd(M, full_matrices=True)
    r = int(np.sum(s_ > 1e-10))
    return u_[:, r:]


EIGV = {}     # k -> exact light eigenvector (slot coordinates) for "eig" components


def gold_k(k):
    G = Gold0[k]
    if k == kd and EW and A_EW is not None:
        G = np.column_stack([G, A_EW]) if G.shape[1] else A_EW[:, None]
    if k in EIGV:
        G = np.column_stack([G, EIGV[k]]) if G.shape[1] else EIGV[k][:, None]
    return G


def Ablk(k, y):
    M = np.einsum("p,pij->ij", y, Ay[k])
    return 0.5 * (M + M.conj().T)


STAGE_B = args.objective == "maxleff"
PHASE1 = args.objective == "phase1"
MARGIN = args.objective == "maxmargin"
nz = ny + 1 + (1 if (PHASE1 or MARGIN) else 0) + (1 if STAGE_B else 0)
IT = ny
IS = ny + 1 if (PHASE1 or MARGIN) else None
IR = nz - 1 if STAGE_B else None


def ray_row(k, v):
    r = np.zeros(nz)
    r[:ny] = np.real(np.einsum("i,pij,j->p", v.conj(), Ay[k], v))
    return r


def lp(obj, Aub, bub, Aeq, beq, bounds):
    res = None
    for meth, opts in (("highs-ds", {"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10}),
                       ("highs-ipm", {"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9}),
                       ("highs", {})):
        res = linprog(obj, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=bounds, method=meth, options=opts)
        if res.status == 0:
            return res
    return res


RESP = {}


def setup_response(c_ref, Ucur):
    """stage B: heavy projector = complement of Goldstones, the EW direction and every light direction at c_ref."""
    H = full_hessian(c_ref)
    w, V = np.linalg.eigh(H)
    heavy = w >= 10 * args.eps_hi
    Ph = V[:, heavy]
    Hy = np.tensordot(Nmat.T, hess_rows(), axes=(1, 0))
    RESP["M"] = np.array([Ph.T @ Hy[a] @ Ph for a in range(ny)])
    del Hy
    Tb = LIGHTB["Tb"]
    RESP["beta"] = (Nmat.T @ Tb) @ Ph          # ny x nh
    RESP["V4y"] = Nmat.T @ (4.0 * LIGHTB["J4u"])   # lambda_direct = 4 J4(u)
    log(f"stage B response: {int(heavy.sum())} heavy modes, min heavy {w[heavy][0]:.4g}")


def response(y):
    M = np.einsum("a,aij->ij", y, RESP["M"])
    b = y @ RESP["beta"]
    Mib = np.linalg.solve(M, b)
    R = float(b @ Mib)
    g = 2 * RESP["beta"] @ Mib - np.einsum("i,aij,j->a", Mib, RESP["M"], Mib)
    return R, g


def comp_row(jj, mf):
    r = np.zeros(nz)
    r[:ny] = (VAL0 - jj) @ Nmat
    r[IT] = args.mu * mf
    if PHASE1:
        r[IS] = -1.0
    sc = max(1.0, float(np.max(np.abs(r[:ny]))))
    if MARGIN:
        r[IS] = args.margin_wc * sc      # V_k - V* >= mu t mf + w_c tau
    return r / sc


def bfb_row(J4):
    r = np.zeros(nz)
    r[:ny] = -(J4 @ Nmat)
    sc = max(1.0, float(np.max(np.abs(r[:ny]))))
    if MARGIN:
        r[IS] = args.margin_wb * sc      # V4(u) >= eps + w_b tau
    return r / sc, -args.eps_bfb / sc


def herm_embed(Mst):
    """(n_y, d, d) complex Hermitian -> (n_y, 2d, 2d) real symmetric embedding."""
    Re, Im = Mst.real, Mst.imag
    return np.concatenate([np.concatenate([Re, -Im], axis=2), np.concatenate([Im, Re], axis=2)], axis=1)


DOM = None


def dominance_setup():
    """sufficient BFB condition from block-norm bounds (vbound.py): V4(q) >= x^T N(c) x, x_B = |q_B|^2, N copositive
    certified by N - eps I = Pm + Nn (Pm PSD, Nn >= 0 entrywise)."""
    Z = np.load(vc.BIG / "quartic_bounds.npz")
    assert [str(x) for x in Z["ids"]] == list(vc.IDS)
    L, U, MD = Z["L"], Z["U"], Z["MD"]
    q4 = [k for k in range(vc.NPAR) if vc.DEG[k] == 4]
    mid = 0.5 * (L + U)
    dlt = 0.5 * (U - L) * (1 + args.dom_safety) + 1e-3 * np.abs(mid)
    types = {}
    for k in q4:
        types.setdefault(tuple(MD[k]), []).append(k)
    even, odd = [], []
    for md, ks_ in types.items():
        md = np.array(md)
        W = np.zeros((6, 6))
        nz_ = [b for b in range(6) if md[b] > 0]
        if np.all(md % 2 == 0):
            if len(nz_) == 1:
                W[nz_[0], nz_[0]] = 1.0
            else:
                a_, b_ = nz_
                W[a_, b_] = W[b_, a_] = 0.5
            even.append((ks_, W))
        else:
            degs = sorted([(md[b], b) for b in nz_], reverse=True)
            if len(nz_) == 2:            # (3,1)
                (_, A_), (_, B_) = degs
                W[A_, A_] = 0.5
                W[A_, B_] = W[B_, A_] = 0.25
            elif len(nz_) == 3:          # (2,1,1)
                (_, A_), (_, B_), (_, C_) = degs
                W[A_, B_] = W[B_, A_] = 0.25
                W[A_, C_] = W[C_, A_] = 0.25
            else:                         # (1,1,1,1): pair H with Sigma if both present
                bs = list(nz_)
                iH, iS = 1, 2
                if iH in bs and iS in bs:
                    p1 = (iH, iS)
                    rest = [b for b in bs if b not in p1]
                else:
                    p1 = (bs[0], bs[1])
                    rest = bs[2:]
                p2 = tuple(rest)
                for (a_, b_) in (p1, p2):
                    W[a_, b_] = W[b_, a_] = 0.25
            odd.append((ks_, W))
    return {"mid": mid, "dlt": dlt, "even": even, "odd": odd, "q4": q4}


def dominance_constraints(cp, y):
    global DOM
    if DOM is None:
        DOM = dominance_setup()
        log(f"dominance BFB: {len(DOM['even'])} even and {len(DOM['odd'])} odd monomial types")
    c = Nmat @ y
    a = cp.Variable(vc.NPAR)
    cons = [a >= c, a >= -c]
    Nexpr = 0
    for ks_, W in DOM["even"]:
        g = sum(DOM["mid"][k] * c[k] - DOM["dlt"][k] * a[k] for k in ks_)
        Nexpr = Nexpr + g * W
    for ks_, W in DOM["odd"]:
        g = sum(DOM["mid"][k] * c[k] - DOM["dlt"][k] * a[k] for k in ks_)
        h = cp.Variable(nonneg=True)
        cons.append(h >= -g)
        Nexpr = Nexpr - h * W
    Pm = cp.Variable((6, 6), PSD=True)
    Nn = cp.Variable((6, 6), symmetric=True)
    cons += [Nn >= 0, Nexpr - args.bfb_dom * np.eye(6) == Pm + Nn]
    return cons


def sdp_solve(comps, Ucur, Aub, bub, Aeq, beq, obj, bounds):
    """the fixed-U problem as an SDP (cvxpy + Clarabel); returns z or None."""
    import cvxpy as cp
    from cvxpy.reductions.solvers.conic_solvers import clarabel_conif as _cc
    from cvxpy.settings import OPTIMAL_INACCURATE as _OI
    for _k in list(_cc.CLARABEL.STATUS_MAP):
        if str(_k) in ("NumericalError", "InsufficientProgress", "MaxIterations"):
            _cc.CLARABEL.STATUS_MAP[_k] = _OI     # keep the (primal-feasible) iterate; the LP polish verifies it
    z = cp.Variable(nz)
    y = z[:ny]
    t = z[IT]
    cons = []
    if len(Aub):
        cons.append(np.array(Aub) @ z <= np.array(bub))
    if Aeq is not None and len(Aeq):
        cons.append(Aeq @ z == beq)
    for i, (lo, hi) in enumerate(bounds):
        if lo is not None:
            cons.append(z[i] >= lo)
        if hi is not None:
            cons.append(z[i] <= hi)

    def expr(k, Qx):
        B = herm_embed(np.einsum("im,aij,jn->amn", Qx.conj(), Ay[k], Qx))
        d2 = B.shape[1]
        E = cp.reshape(B.reshape(ny, -1).T @ y, (d2, d2), order="C")
        return 0.5 * (E + E.T), d2

    for k, (kind, Q0, Qc) in comps.items():
        if kind == "heavy" and Q0.shape[1]:
            E, d2 = expr(k, Q0)
            cons.append(E - t * np.eye(d2) >> 0)
        elif kind == "sandwich":
            E, d2 = expr(k, Q0)
            cons += [E - args.eps_lo * np.eye(d2) >> 0, args.eps_hi * np.eye(d2) - E >> 0]
        elif kind == "sub":
            if Qc.shape[1]:
                E, d2 = expr(k, Qc)
                cons.append(E - t * np.eye(d2) >> 0)
            E, d2 = expr(k, Q0)
            cons.append(E - args.eps_lo * np.eye(d2) >> 0)
            E, d2 = expr(k, Ucur[k])
            cons.append(args.eps_hi * np.eye(d2) - E >> 0)
    Mu = cp.reshape(MiY.reshape(ny, -1).T @ y, (6, 6), order="C")
    Mu = 0.5 * (Mu + Mu.T)
    cons += [UB * np.eye(6) - Mu >> 0, Mu + UB * np.eye(6) >> 0]
    if args.bfb_dom > 0:
        cons += dominance_constraints(cp, y)
    prob = cp.Problem(cp.Minimize(obj @ z), cons)
    try:
        prob.solve(solver="CLARABEL", tol_gap_abs=1e-7, tol_gap_rel=1e-7, tol_feas=1e-8, max_iter=500,
                   reduced_tol_gap_abs=1e-5, reduced_tol_gap_rel=1e-5, reduced_tol_feas=1e-6,
                   chordal_decomposition_enable=False, verbose=bool(args.sdp_verbose))
    except Exception as e:  # pragma: no cover
        log(f"    SDP failed: {e!r}")
        return None, "error"
    if prob.status not in ("optimal", "optimal_inaccurate"):
        log(f"    SDP status {prob.status}")
        return None, prob.status
    return np.asarray(z.value, float), prob.status


KELLEY = []
BASINS = []
RUN_DIRS = []
FOUND_RAYS = []
DSC_COUNTER = [0]


def excluded_subspace(Ucur):
    """real chart subspace of Goldstones + EW doublet + every lifted light subspace (fixed at fixed U)."""
    cols = [np.linalg.svd(P["tangents"], full_matrices=False)[0][:, :35]]
    if EW and A_EW is not None:
        cols.append(real_span(kd, A_EW[:, None]))
    for k, Uk in Ucur.items():
        if args.leff_all:
            break       # lambda_eff_all: the light (1,1)_0 modes are integrated out too (tree matching below v_R)
        cols.append(real_span(k, Uk))
    for lab, kind in spec.items():
        if args.leff_all:
            break
        if kind[0] == "sandwich":
            comp = [x for x in C.real_components("SM") if x["label"] == lab][0]
            cols.append(comp["W"])
    E = np.hstack(cols)
    u_, s_, _ = np.linalg.svd(E, full_matrices=True)
    r_ = int(np.sum(s_ > 1e-8))
    return u_[:, :r_], u_[:, r_:]


def lambda_heavy(y, Ucur):
    """lambda_eff_heavy = lambda_direct - R/2 with R = b^T P (P^T H P)^-1 P^T b and the gradient of R in y."""
    c = Nmat @ y
    _, Pc = excluded_subspace(Ucur)
    H = full_hessian(c)
    M = Pc.T @ H @ Pc
    b = c @ LIGHTB["Tb"]
    pb = Pc.T @ b
    try:
        xr = np.linalg.solve(M, pb)
    except np.linalg.LinAlgError:
        return None
    R = float(pb @ xr)
    x = Pc @ xr
    ba = Nmat.T @ (LIGHTB["Tb"] @ x)                         # b_a . x
    xHx = np.einsum("i,kij,j->k", x, hess_rows(), x, optimize=True)
    gR = 2 * ba - Nmat.T @ xHx
    lam_dir = 4.0 * float(c @ LIGHTB["J4u"])
    return lam_dir, R, gR, float(np.linalg.eigvalsh(M)[0])


def inloop(y, Ucur, comps, rep):
    """screens at the current SDP point; returns new linear rows [(row, rhs)]."""
    global BFB_J
    c = Nmat @ y
    rows = []
    msgs = []
    # (1) SM-singlet subspace screen
    if args.screen:
        Vst, found, runaways = screen(c, args.screen_polish)
        n_c = 0
        for Vm, zm, conv in found:
            if conv and Vm < Vst - 1e-10 * max(1.0, abs(Vst)):
                for i_ in add_points(vprep.q_of_z(zm)[None, :], [f"screen:{np.round(zm, 4).tolist()}"]):
                    rows.append((comp_row(COMP_J[i_], COMP_M[i_]), 0.0))
                    n_c += 1
                if n_c >= 3:
                    break
        n_b = 0
        for v4, zh in runaways[:3]:
            qd = vprep.q_of_z(zh)
            qd = qd / np.linalg.norm(qd)
            J4 = vc.J_values(qd[None, :])[0] * (vc.DEG == 4)
            BFB_J = np.vstack([BFB_J, J4[None, :]])
            rows.append(bfb_row(J4))
            n_b += 1
        if n_c or n_b:
            msgs.append(f"subspace +{n_c} comp +{n_b} bfb (min {found[0][0] - Vst:.3g})")
    # (2) full-chart quartic BFB search
    if args.bfbscreen > 0:
        F4 = vc.FastV(c * (vc.DEG == 4))
        rng = np.random.default_rng(1000 + rep + 97 * DSC_COUNTER[0])
        starts = [u for u in RUN_DIRS[-20:]]
        for _ in range(args.bfbscreen):
            v = np.zeros(vc.N)
            for name, sl_ in vc.BLOCKS.items():
                if rng.uniform() < 0.7:
                    x = rng.normal(size=sl_.stop - sl_.start)
                    v[sl_] = x / np.linalg.norm(x) * rng.uniform(0.2, 1.0)
            if np.linalg.norm(v) == 0:
                v = rng.normal(size=vc.N)
            starts.append(v)
        n_b = 0
        worst = 0.0
        found_u = []
        for u0 in starts:
            f, u = vdcore.quartic_min(F4, u0, maxiter=200, stop_below=-1e-3)
            worst = min(worst, f)
            if f < args.eps_bfb:
                found_u.append(u)
                if len(found_u) >= 40:
                    break
        if found_u:
            FOUND_RAYS.extend(found_u)
            np.savez_compressed(vc.BIG / f"{args.out}_rays.npz", Q=np.array(FOUND_RAYS))
            J4s = vc.J_values(np.array(found_u)) * (vc.DEG == 4)[None, :]
            BFB_J = np.vstack([BFB_J, J4s])
            for J4 in J4s:
                rows.append(bfb_row(J4))
            n_b = len(found_u)
        if n_b:
            msgs.append(f"quartic +{n_b} bfb (min V4 {worst:.3g})")
    # (4) lambda_eff_heavy >= leff_min (Kelley cut of the convex response R)
    if args.leff_min is not None and LIGHTB and EW:
        out = lambda_heavy(y, Ucur)
        if out is not None:
            lam_dir, R, gR, mmin = out
            lam = lam_dir - R / 2
            if lam < args.leff_min - 1e-6:
                r = np.zeros(nz)
                r[:ny] = gR - 2.0 * (Nmat.T @ (4.0 * LIGHTB["J4u"]))
                rhs = float(gR @ y - R - 2.0 * args.leff_min)
                sc = max(1.0, float(np.max(np.abs(r))))
                KELLEY.append((r / sc, rhs / sc))
                rows.append((r / sc, rhs / sc))
                msgs.append(f"lambda_eff_{'all' if args.leff_all else 'heavy'} {lam:.4g} (direct {lam_dir:.4g}, R {R:.4g}) -> Kelley cut")
    # (3) quick full-chart descents (only once the cheaper screens are clean)
    if args.dscreen > 0 and not rows:
        F = vc.FastV(c)
        Vst = float(c @ VAL0)
        rng = np.random.default_rng(5000 + DSC_COUNTER[0])
        DSC_COUNTER[0] += 1
        nbk = {k: float(np.linalg.norm(q0[sl_])) for k, sl_ in vc.BLOCKS.items()}
        D486 = np.load(vc.BIG / "deep486.npz")
        dq = D486["Q"][D486["endpoint"]]
        starts = []
        for i in range(args.dscreen):
            mode = i % 4
            q = np.zeros(vc.N)
            if mode == 3 and len(dq):
                q[:486] = dq[rng.integers(len(dq))]
                q[vc.BLOCKS["A45"]] = q0[vc.BLOCKS["A45"]] * rng.uniform(0, 1.5)
            elif mode == 2 and LIGHTB:
                q = q0 + rng.choice([-1, 1]) * rng.uniform(0.02, 1.0) * LIGHTB["u"]
            else:
                ph = nbk["Phi210"] * rng.uniform(0.3, 1.4)
                for name, lo, hi in (("Phi210", ph, ph), ("H10", 0.0, 2.0 * ph), ("Sigma126bar", 0.0, 5.0 * ph),
                                     ("S", 0.0, 2.0 * ph), ("Phi17", 0.5 * nbk["Phi17"], 1.2 * nbk["Phi17"]),
                                     ("A45", 0.0, 1.5 * max(nbk["A45"], 0.3))):
                    sl_ = vc.BLOCKS[name]
                    x = rng.normal(size=sl_.stop - sl_.start)
                    q[sl_] = x / np.linalg.norm(x) * rng.uniform(lo, hi)
            starts.append(q)
        # basin tracking: re-descend from the last endpoints of every known lower basin (their minimisers move with c)
        starts = [b_[0].copy() for b_ in BASINS[-args.track:]] + starts
        F4 = None
        n_c = n_b = 0
        deepest = 0.0
        for q in starts:
            res, qe, q_run = vdcore.descend(F, q, Vst, maxiter=args.dscreen_maxiter, escapes=2, hess_check=False)
            if q_run is None and res["V_end-V*"] < -1e-9 * max(1.0, abs(Vst)):
                Je = vc.J_values(qe[None, :])[0]
                hit = None
                for ib, (qb, Jb) in enumerate(BASINS):
                    if np.linalg.norm(Je - Jb) <= 0.02 * max(1.0, np.linalg.norm(Jb)):
                        hit = ib
                        break
                if hit is None:
                    BASINS.append((qe.copy(), Je))
                else:
                    BASINS[hit] = (qe.copy(), Je)
            if q_run is not None:
                if F4 is None:
                    F4 = vc.FastV(c * (vc.DEG == 4))
                f, u = vdcore.quartic_min(F4, q_run, maxiter=300)
                RUN_DIRS.append(u)
                FOUND_RAYS.append(u)
                J4 = vc.J_values(u[None, :])[0] * (vc.DEG == 4)
                BFB_J = np.vstack([BFB_J, J4[None, :]])
                rows.append(bfb_row(J4))
                n_b += 1
            elif res["V_end-V*"] < -1e-9 * max(1.0, abs(Vst)):
                deepest = min(deepest, res["V_end-V*"])
                for i_ in add_points(qe[None, :], [f"dscreen{DSC_COUNTER[0]}:{res['V_end-V*']:.4g}"]):
                    rows.append((comp_row(COMP_J[i_], COMP_M[i_]), 0.0))
                    n_c += 1
        msgs.append(f"descents {len(starts)}: +{n_c} comp (deepest {deepest:.3g}) +{n_b} runaway bfb; basins {len(BASINS)}")
    if msgs:
        log("    in-loop: " + "; ".join(msgs))
    return rows


def solve_fixedU(Ucur, max_iter):
    global BFB_J
    Aub, bub = [], []
    for i in range(vc.NPAR):
        r = np.zeros(nz)
        r[:ny] = Nmat[i]
        Aub += [r, -r]
        bub += [boxes[i], boxes[i]]
    for jj, mf in zip(COMP_J, COMP_M):
        r = comp_row(jj, mf)
        Aub.append(r)
        bub.append(0.0)
    for jj in BFB_J:
        r, b_ = bfb_row(jj)
        Aub.append(r)
        bub.append(b_)
    for r, b_ in KELLEY:
        Aub.append(r)
        bub.append(b_)
    if args.octet and OCT.get("rows"):
        for name, Tv, dlt, _ in OCT["rows"]:
            r = np.zeros(nz)
            r[:ny] = Tv @ Nmat
            sc = max(1.0, float(np.max(np.abs(r[:ny]))))
            Aub += [r / sc, -r / sc]
            bub += [dlt / sc, dlt / sc]
    if args.lightb > 0 and LIGHTB:
        for j in range(LIGHTB["Vl"].shape[1]):
            r = np.zeros(nz)
            r[:ny] = (LIGHTB["Tb"] @ LIGHTB["Vl"][:, j]) @ Nmat
            sc = max(1.0, float(np.max(np.abs(r[:ny]))))
            Aub += [r / sc, -r / sc]
            bub += [args.lightb / sc, args.lightb / sc]
    if LIGHTB and EW:
        # BFB along the pure EW doublet ray
        r = np.zeros(nz)
        r[:ny] = -(LIGHTB["J4u"] @ Nmat)
        Aub.append(r)
        bub.append(-args.eps_bfb)
        if args.lamdir_min is not None:
            r = np.zeros(nz)
            r[:ny] = -(4.0 * LIGHTB["J4u"] @ Nmat)
            Aub.append(r)
            bub.append(-args.lamdir_min)
        if args.lamdir_max is not None:
            r = np.zeros(nz)
            r[:ny] = 4.0 * LIGHTB["J4u"] @ Nmat
            Aub.append(r)
            bub.append(args.lamdir_max)
    Aeq, beq = None, None
    if EW:
        Mv = np.einsum("ajk,k->aj", Ay[kd], A_EW)
        E = np.vstack([Mv.real.T, Mv.imag.T])
        rhs = args.ew_lambda * np.concatenate([A_EW.real, A_EW.imag])
        uE, sE, vE = np.linalg.svd(E, full_matrices=False)
        kE = int(np.sum(sE > 1e-10 * sE[0]))
        Aeq = np.zeros((kE, nz))
        Aeq[:, :ny] = vE[:kE]
        beq = (uE[:, :kE].T @ rhs) / sE[:kE]
        EW_INFO["rank_eq"] = kE
        EW_INFO["rhs_out_of_range"] = float(np.linalg.norm(rhs - uE[:, :kE] @ (uE[:, :kE].T @ rhs)))
    for k, u8 in EIGV.items():
        lam8 = 0.5 * (args.eps_lo + args.eps_hi)
        Mv = np.einsum("ajk,k->aj", Ay[k], u8)
        E = np.vstack([Mv.real.T, Mv.imag.T])
        rhs = lam8 * np.concatenate([u8.real, u8.imag])
        uE, sE, vE = np.linalg.svd(E, full_matrices=False)
        kE = int(np.sum(sE > 1e-10 * sE[0]))
        A8 = np.zeros((kE, nz))
        A8[:, :ny] = vE[:kE]
        b8 = (uE[:, :kE].T @ rhs) / sE[:kE]
        Aeq = A8 if Aeq is None else np.vstack([Aeq, A8])
        beq = b8 if beq is None else np.concatenate([beq, b8])
    comps = {}
    for k in range(nb):
        m = int(mult[k])
        kind = spec.get(labels[k], ("heavy",))
        G = gold_k(k)
        Q0 = compl(G, m)
        if kind[0] == "sub":
            Uk = Ucur[k]
            Qc = compl(np.column_stack([Uk, G]) if G.shape[1] else Uk, m)
            comps[k] = ("sub", Q0, Qc)
        elif kind[0] == "sandwich":
            comps[k] = ("sandwich", Q0, None)
        else:
            comps[k] = ("heavy", Q0, None)
    cuts_A, cuts_b = [], []
    for k, (kind, Q0, Qc) in comps.items():
        H_ = Qc if kind == "sub" else Q0
        if H_ is None or H_.shape[1] == 0:
            continue
        for j in range(H_.shape[1]):
            r = ray_row(k, H_[:, j])
            if kind == "sandwich":
                cuts_A += [-r, r.copy()]
                cuts_b += [-args.eps_lo, args.eps_hi]
            else:
                r[IT] = -1.0
                cuts_A.append(-r)
                cuts_b.append(0.0)
        if kind == "sub":
            for l_ in range(Ucur[k].shape[1]):
                r = ray_row(k, Ucur[k][:, l_])
                cuts_A += [-r, r.copy()]
                cuts_b += [-args.eps_lo, args.eps_hi]
    for j in range(6):
        for sg in (1.0, -1.0):
            r = np.zeros(nz)
            r[:ny] = sg * MiY[:, j, j]
            cuts_A.append(r)
            cuts_b.append(UB)
    obj = np.zeros(nz)
    if PHASE1:
        obj[IS] = 1.0
        obj[IT] = -1e-6
        bounds = [(None, None)] * ny + [(args.tmin, 5.0), (-100.0, None)]
    elif MARGIN:
        obj[IS] = -1.0
        obj[IT] = -1e-3
        bounds = [(None, None)] * ny + [(args.tmin, 5.0), (0.0, args.margin_max)]
    elif STAGE_B:
        obj[:ny] = -RESP["V4y"]
        obj[IR] = 0.5
        bounds = [(None, None)] * ny + [(args.tmin, 5.0), (0.0, None)]
    elif args.objective.startswith("rand"):
        rg = np.random.default_rng(int(args.objective.split(":")[1]))
        wv = rg.normal(size=vc.NPAR) / boxes
        obj[:ny] = Nmat.T @ wv
        bounds = [(None, None)] * ny + [(args.tmin, 5.0)]
    else:
        obj[IT] = -1.0
        bounds = [(None, None)] * ny + [(0.0, 5.0)]
    res = None
    worst = None
    n_screen_added = 0
    if not STAGE_B and not args.no_sdp:
        for rep in range(args.max_reps):
            t_s = time.time()
            zs_, st_ = sdp_solve(comps, Ucur, Aub, bub, Aeq, beq, obj, bounds)
            if zs_ is None:
                log(f"    SDP: {st_} ({time.time()-t_s:.1f}s)")
                if st_ in ("infeasible", "infeasible_inaccurate"):
                    return 2, None, None, None
                break
            ys_ = zs_[:ny]
            if Aeq is not None and len(Aeq):     # exact projection onto the EW eigen-equations (min-norm correction)
                corr = np.linalg.lstsq(Aeq[:, :ny], Aeq[:, :ny] @ ys_ - beq, rcond=None)[0]
                ys_ = ys_ - corr
                zs_[:ny] = ys_
            log(f"    SDP {st_}: t = {zs_[IT]:.6g}{'' if IS is None else f', s/tau = {zs_[IS]:.4g}'}, rows {len(Aub)} ({time.time()-t_s:.1f}s)")
            np.savez(vc.BIG / f"{args.out}_cur.npz", c=Nmat @ ys_, ids=np.array(vc.IDS), t=zs_[IT],
                     beta_re=BETA.real, beta_im=BETA.imag, a_ew=A_EW if A_EW is not None else np.zeros(0))
            new_rows = inloop(ys_, Ucur, comps, rep)
            if new_rows:
                for r, b_ in new_rows:
                    Aub.append(r)
                    bub.append(b_)
                continue
            if args.polish == 0:
                return 0, ys_, float(zs_[IT]), (float(zs_[IS]) if PHASE1 else None)
            break
        else:
            log(f"    WARNING: screen loop exhausted ({args.max_reps} rounds); returning the last SDP point (re-checked by the final screens)")
            if args.polish == 0 and zs_ is not None:
                return 0, ys_, float(zs_[IT]), (float(zs_[IS]) if PHASE1 else None)
        if zs_ is not None:
            # seed the LP polish with every eigen-direction of every block at the SDP solution
            for k, (kind, Q0, Qc) in comps.items():
                M = Ablk(k, ys_)
                for Hx, lohi in (((Qc if kind == "sub" else Q0), "lo"), ((Ucur[k] if kind == "sub" else None), "hi")):
                    if Hx is None or Hx.shape[1] == 0:
                        continue
                    w, V = np.linalg.eigh(Hx.conj().T @ M @ Hx)
                    for j in range(len(w)):
                        r = ray_row(k, Hx @ V[:, j])
                        if kind == "sandwich":
                            cuts_A += [-r, r.copy()]
                            cuts_b += [-args.eps_lo, args.eps_hi]
                        elif lohi == "hi":
                            cuts_A.append(r.copy()); cuts_b.append(args.eps_hi)
                        else:
                            r[IT] = -1.0
                            cuts_A.append(-r); cuts_b.append(0.0)
                if kind == "sub":
                    w, V = np.linalg.eigh(Q0.conj().T @ M @ Q0)
                    for j in range(len(w)):
                        cuts_A.append(-ray_row(k, Q0 @ V[:, j])); cuts_b.append(-args.eps_lo)
            max_iter = min(max_iter, args.polish)
    for it in range(max_iter):
        res = lp(obj, np.array(Aub + cuts_A), np.array(bub + cuts_b), Aeq, beq, bounds)
        if res.status != 0:
            log(f"    LP status {res.status} at cut iteration {it}: {str(res.message)[:120]}")
            return res.status, None, None, None
        z = res.x
        y = z[:ny]
        t = z[IT]
        n_new = 0
        worst = 0.0
        for k, (kind, Q0, Qc) in comps.items():
            M = Ablk(k, y)
            if kind == "sandwich":
                w, V = np.linalg.eigh(Q0.conj().T @ M @ Q0)
                for j in range(len(w)):
                    v = Q0 @ V[:, j]
                    if w[j] < args.eps_lo - 1e-13:
                        cuts_A.append(-ray_row(k, v)); cuts_b.append(-args.eps_lo); n_new += 1; worst = max(worst, args.eps_lo - w[j])
                    if w[j] > args.eps_hi + 1e-13:
                        cuts_A.append(ray_row(k, v)); cuts_b.append(args.eps_hi); n_new += 1; worst = max(worst, w[j] - args.eps_hi)
                continue
            H_ = Qc if kind == "sub" else Q0
            if H_.shape[1]:
                w, V = np.linalg.eigh(H_.conj().T @ M @ H_)
                for j in range(len(w)):
                    if w[j] < t - 1e-13:
                        r = ray_row(k, H_ @ V[:, j]); r[IT] = -1.0
                        cuts_A.append(-r); cuts_b.append(0.0); n_new += 1; worst = max(worst, t - w[j])
            if kind == "sub":
                Uk = Ucur[k]
                w, V = np.linalg.eigh(Uk.conj().T @ M @ Uk)
                for j in range(len(w)):
                    if w[j] > args.eps_hi + 1e-13:
                        cuts_A.append(ray_row(k, Uk @ V[:, j])); cuts_b.append(args.eps_hi); n_new += 1; worst = max(worst, w[j] - args.eps_hi)
                w, V = np.linalg.eigh(Q0.conj().T @ M @ Q0)
                for j in range(len(w)):
                    if w[j] < args.eps_lo - 1e-13:
                        cuts_A.append(-ray_row(k, Q0 @ V[:, j])); cuts_b.append(-args.eps_lo); n_new += 1; worst = max(worst, args.eps_lo - w[j])
        Mu = np.einsum("p,pij->ij", y, MiY)
        w, V = np.linalg.eigh(Mu)
        for j in range(6):
            if abs(w[j]) > UB - 1e-12:
                r = np.zeros(nz)
                r[:ny] = np.einsum("i,pij,j->p", V[:, j], MiY, V[:, j]) * np.sign(w[j])
                cuts_A.append(r); cuts_b.append(UB); n_new += 1; worst = max(worst, abs(w[j]) - UB)
        if STAGE_B:
            R, gR = response(y)
            if R > z[IR] + 1e-9:
                r = np.zeros(nz)
                r[:ny] = gR
                r[IR] = -1.0
                rhs = float(gR @ y - R)
                sc = max(1.0, float(np.max(np.abs(r))))
                cuts_A.append(r / sc); cuts_b.append(rhs / sc); n_new += 1; worst = max(worst, R - z[IR])
        if it % 25 == 0:
            log(f"    it {it}: t = {t:.6g}{'' if not PHASE1 else f', s = {z[IS]:.4g}'}, cuts {len(cuts_A)}, new {n_new}, worst {worst:.2e}")
        if n_new == 0 or (worst < args.lp_tol and it > 3):
            if args.screen:
                c = Nmat @ y
                Vst, found, runaways = screen(c, args.screen_polish)
                added = 0
                for Vm, zm, conv in found:
                    if conv and Vm < Vst - 1e-10 * max(1.0, abs(Vst)):
                        idx = add_points(vprep.q_of_z(zm)[None, :], [f"screen:{np.round(zm, 4).tolist()}"])
                        for i_ in idx:
                            Aub.append(comp_row(COMP_J[i_], COMP_M[i_]))
                            bub.append(0.0)
                            added += 1
                        if idx:
                            break
                for v4, zh in runaways[:2]:
                    qd = vprep.q_of_z(zh)
                    qd = qd / np.linalg.norm(qd)
                    J4 = vc.J_values(qd[None, :])[0] * (vc.DEG == 4)
                    BFB_J = np.vstack([BFB_J, J4[None, :]])
                    r = np.zeros(nz)
                    r[:ny] = -(J4 @ Nmat)
                    sc = max(1.0, float(np.max(np.abs(r[:ny]))))
                    Aub.append(r / sc)
                    bub.append(-args.eps_bfb / sc)
                    added += 1
                if added:
                    n_screen_added += added
                    log(f"    screen at it {it}: added {added} rows (lowest subspace V - V* = {found[0][0] - Vst:.4g}, "
                        f"{len(runaways)} runaway dirs)")
                    continue
            break
    return 0, res.x[:ny], res.x[IT], (res.x[IS] if PHASE1 else None)


def initial_U(warm=None):
    U = {}
    for k in range(nb):
        kind = spec.get(labels[k], ("heavy",))
        if kind[0] != "sub":
            continue
        m = int(mult[k])
        G = gold_k(k)
        Q0 = compl(G, m)
        if warm is not None and f"U{k}" in warm.files and warm[f"U{k}"].shape == (m, kind[1]):
            Uk = Q0 @ (Q0.conj().T @ warm[f"U{k}"])
            u_, _, _ = np.linalg.svd(Uk, full_matrices=False)
            U[k] = u_[:, :kind[1]]
        elif k == ks:
            js = [j for j, mm in enumerate(meta[k]) if mm["block"] == "Sigma126bar"][:1] + \
                 [j for j, mm in enumerate(meta[k]) if mm["block"] == "S"][:1]
            E = np.eye(m, dtype=complex)[:, js]
            u_, _, _ = np.linalg.svd(Q0 @ (Q0.conj().T @ E), full_matrices=False)
            U[k] = u_[:, :kind[1]]
        elif k == kd:
            js = [j for j, mm in enumerate(meta[k]) if mm["block"] == "H10"][:1]
            E = np.eye(m, dtype=complex)[:, js]
            U[k] = E
        else:
            U[k] = Q0[:, :kind[1]]
    return U


def update_U(y, Ucur):
    U = {}
    for k in Ucur:
        kind = spec[labels[k]]
        Q0 = compl(gold_k(k), int(mult[k]))
        w, V = np.linalg.eigh(Q0.conj().T @ Ablk(k, y) @ Q0)
        U[k] = Q0 @ V[:, :kind[1]]
    return U


def lambda_eff_exact(c):
    if not LIGHTB:
        return None
    H = full_hessian(c)
    w, V = np.linalg.eigh(H)
    b = c @ LIGHTB["Tb"]
    lam_dir = 4.0 * float(c @ LIGHTB["J4u"])
    u = LIGHTB["u"]
    gold = np.abs(w) < 1e-9
    # exclude the EW doublet eigenspace itself (eigenvalue lam_ew, 4 real modes) from the response
    ew = np.abs(w - args.ew_lambda) < 0.3 * args.ew_lambda
    heavy = (w >= 10 * args.eps_hi) & ~ew
    light = (~gold) & (~heavy) & (~ew)
    bh = V[:, heavy].T @ b
    bl = V[:, light].T @ b
    bg = V[:, gold].T @ b
    Rh = float(np.sum(bh ** 2 / w[heavy]))
    Rl = float(np.sum(bl ** 2 / w[light])) if light.any() else 0.0
    return {"lambda_direct": lam_dir, "R_heavy": Rh, "lambda_eff_heavy": lam_dir - Rh / 2, "R_light": Rl,
            "lambda_eff_all": lam_dir - (Rh + Rl) / 2, "max_b_goldstone": float(np.max(np.abs(bg))) if bg.size else 0.0,
            "ew_eigenvalue": float(w[ew][0]) if ew.any() else None,
            "light_terms": sorted([(float(x * x / m_), float(m_)) for x, m_ in zip(bl, w[light])], reverse=True)[:6]}


def verify(c, Ucur):
    H = full_hessian(c)
    w = np.linalg.eigvalsh(H)
    out = {"n_zero": int(np.sum(np.abs(w) < 1e-9)), "n_neg": int(np.sum(w < -1e-9)),
           "n_light": int(np.sum((w >= 1e-9) & (w < 10 * args.eps_hi))), "n_heavy": int(np.sum(w >= 10 * args.eps_hi)),
           "expected_light": expected_light, "min_eig": float(w[0]),
           "min_heavy": float(np.min(w[w >= 10 * args.eps_hi])), "lowest_45": w[:45].tolist()}
    out["grad_residual"] = float(np.max(np.abs(P["grads"].T @ c)))
    out["V_star"] = float(VAL0 @ c)
    if len(COMP_J):
        gaps = np.array(COMP_J) @ c - out["V_star"]
        out["competitor_min_gap"] = float(np.min(gaps))
        out["n_competitors_below"] = int(np.sum(gaps < 0))
    out["bfb_min"] = float(np.min(BFB_J @ c)) if len(BFB_J) else None
    out["a0"] = (np.linalg.eigvalsh(np.einsum("k,kij->ij", c, Mi)) / (16 * math.pi)).tolist()
    out["max_box_ratio"] = float(np.max(np.abs(c) / boxes))
    blocks = []
    for k in range(nb):
        M = np.einsum("k,kij->ij", c, A[k])
        blocks.append({"label": labels[k], "kind": spec.get(labels[k], ("heavy",))[0],
                       "eigenvalues": np.linalg.eigvalsh(0.5 * (M + M.conj().T)).tolist()})
    out["blocks"] = blocks
    if EW:
        Ad = np.einsum("k,kij->ij", c, A[kd])
        Ad = 0.5 * (Ad + Ad.conj().T)
        wd, Vd = np.linalg.eigh(Ad)
        out["ew"] = {"eig_residual": float(np.linalg.norm(Ad @ A_EW - args.ew_lambda * A_EW)),
                     "doublet_eigs": wd.tolist(), "overlap_lowest": float(abs(np.vdot(Vd[:, 0], A_EW))),
                     "beta": [[float(b.real), float(b.imag)] for b in BETA]}
        cm = comp_of_a(Vd[:, 0])
        out["ew"].update(r_abs=float(abs(cm["r"])), s=[float(np.real(cm["s"])), float(np.imag(cm["s"]))],
                         frac=cm["frac"])
    if args.octet and OCT.get("rows"):
        out["octet_cubics"] = {name: float(Tv @ c) for name, Tv, _, _ in OCT["rows"]}
    if LIGHTB:
        out["lightb"] = [float(c @ (LIGHTB["Tb"] @ LIGHTB["Vl"][:, j])) for j in range(LIGHTB["Vl"].shape[1])]
        out["lambda"] = lambda_eff_exact(c)
    return out


# ------------------------------------------------------------------ main loop
warm = np.load(args.warm if (":" in args.warm) else vc.BIG / args.warm) if args.warm else None
if EW and warm is not None and "beta_re" in warm.files:
    BETA = warm["beta_re"] + 1j * warm["beta_im"]
if EW:
    set_beta(BETA)
for lab_, kind_ in spec.items():
    if kind_[0] == "eig":
        k_ = kb[lab_]
        if warm is not None and f"U{k_}" in warm.files:
            u_ = warm[f"U{k_}"][:, 0]
        else:
            M_ = np.einsum("k,kij->ij", warm["c"], A[k_])
            u_ = np.linalg.eigh(0.5 * (M_ + M_.conj().T))[1][:, 0]
        EIGV[k_] = u_ / np.linalg.norm(u_)
        log(f"exact light eigenvector for {lab_}: {np.round(EIGV[k_], 4)}")
U = initial_U(warm)
best = None
c_prev = warm["c"] if warm is not None else None
if c_prev is not None:
    if EW:
        BETA = beta_update(c_prev)
        set_beta(BETA)
        setup_lightb(c_prev, U)
    if args.octet:
        setup_octet_constraints(c_prev)
if STAGE_B:
    assert c_prev is not None, "stage B needs --warm"
    setup_response(c_prev, U)
hist = []


def run_starts(U0):
    global BETA
    all_last = []
    starts = [("warm", U0)]
    for rr in range(args.restarts):
        Up = {}
        rgp = np.random.default_rng(100 + rr)
        for k, Uk in U0.items():
            Q0 = compl(gold_k(k), int(mult[k]))
            X = Uk + 0.5 * (1 + rr) * (Q0 @ (rgp.normal(size=(Q0.shape[1], Uk.shape[1])) + 1j * rgp.normal(size=(Q0.shape[1], Uk.shape[1]))))
            u_, _, _ = np.linalg.svd(X, full_matrices=False)
            Up[k] = u_
        starts.append((f"restart{rr}", Up))
    for sname, Ucur in starts:
        t_prev = -1.0
        last_of_start = None
        for ui in range(args.uiter):
            t1 = time.time()
            st, y, t, s_ = solve_fixedU(Ucur, args.iters)
            if st != 0:
                hist.append({"start": sname, "uiter": ui, "status": int(st)})
                log(f"  [{sname}] U-iter {ui}: status {st} -> infeasible at this U")
                break
            c = Nmat @ y
            if PHASE1:
                key = s_
            elif STAGE_B:
                key = -(float(RESP["V4y"] @ y) - 0.5 * response(y)[0])
            else:
                key = -t
            hist.append({"start": sname, "uiter": ui, "t": float(t), "s": None if s_ is None else float(s_)})
            log(f"  [{sname}] U-iter {ui}: t = {t:.6g}{'' if s_ is None else f', s = {s_:+.5g}'} ({time.time()-t1:.0f}s)")
            # cuts only accumulate, so the LATEST solve satisfies every constraint known so far
            last_of_start = (key, y.copy(), {k: v.copy() for k, v in Ucur.items()}, BETA.copy(), t)
            Unew = update_U(y, Ucur)
            chg = max([1 - np.min(np.linalg.svd(Ucur[k].conj().T @ Unew[k], compute_uv=False)) ** 2 for k in Ucur] + [0.0])
            bchg = 0.0
            if EW:
                bnew = beta_update(c)
                bchg = float(np.max(np.abs(bnew - BETA))) if BETA.size else 0.0
                BETA = bnew
                set_beta(BETA)
                setup_lightb(c, Unew)
            if args.octet:
                setup_octet_constraints(c)
            Ucur = Unew
            log(f"     U change {chg:.2e}, beta change {bchg:.2e}, |beta|^2 = {float(np.sum(np.abs(BETA) ** 2)):.3e}")
            if chg < 1e-10 and bchg < 1e-10:
                break
            if not PHASE1 and ui >= 1 and abs(t - t_prev) <= 1e-6 * max(abs(t), 1e-12) and chg < 1e-6 and bchg < 1e-6:
                break
            t_prev = t
        if last_of_start is not None:
            all_last.append(last_of_start)
    return min(all_last, key=lambda c_: c_[0]) if all_last else None


best = None
final_screen_info = None
for fround in range(args.final_rounds):
    best = run_starts(U)
    if best is None:
        break
    _, y, Ubest, BETA, tbest = best
    c = Nmat @ y
    if EW:
        set_beta(BETA)
    rng = np.random.default_rng(args.seed + 1000 + fround)
    Zs = sub_sample(args.final_screen_n, rng)
    Vst, found, runaways = screen(c, args.final_screen_polish, Zs, vprep.sub_X(Zs, MONS))
    lower = [(Vm, zm) for Vm, zm, conv in found if conv and Vm < Vst - 1e-9 * max(1.0, abs(Vst))]
    lower_exact = []
    for Vm, zm in lower[:5]:
        Jm = vc.J_values(vprep.q_of_z(zm)[None, :])[0]
        lower_exact.append({"z": zm.tolist(), "|q|": float(np.linalg.norm(vprep.q_of_z(zm))), "V_fit-V*": Vm - Vst,
                            "V_exact-V*": float(c @ Jm - c @ VAL0), "copy": is_copy(Jm)})
    final_screen_info = {"round": fround, "n_samples": args.final_screen_n, "n_polish": args.final_screen_polish,
                         "V_star_fit": Vst, "V_star_rows": float(c @ VAL0), "lowest-V*": found[0][0] - Vst,
                         "argmin": found[0][1].tolist(), "n_lower": len(lower), "lower_exact": lower_exact,
                         "n_runaway_dirs": len(runaways),
                         "runaway_min_V4": (min(r_[0] for r_ in runaways) if runaways else None)}
    log(f"final screen round {fround}: lowest - V* = {found[0][0] - Vst:.4g}, n_lower {len(lower)}, runaways {len(runaways)}")
    if not lower and not runaways:
        break
    for Vm, zm in lower[:6]:
        add_points(vprep.q_of_z(zm)[None, :], [f"finalscreen{fround}:{np.round(zm, 4).tolist()}"])
    for v4, zh in runaways[:6]:
        qd = vprep.q_of_z(zh)
        qd = qd / np.linalg.norm(qd)
        BFB_J = np.vstack([BFB_J, (vc.J_values(qd[None, :])[0] * (vc.DEG == 4))[None, :]])
    U = Ubest
report = {"tag": args.tag, "out": args.out, "args": vars(args), "point": pt, "spec": {k: list(v) for k, v in spec.items()},
          "ny": ny, "history": hist, "ew_info": EW_INFO, "n_competitors": int(len(COMP_J)), "n_bfb": int(len(BFB_J))}
if best is None:
    report["status"] = "INFEASIBLE"
    log("NO FEASIBLE POINT")
else:
    _, y, Ubest, BETA, tbest = best
    c = Nmat @ y
    if EW:
        set_beta(BETA)
        setup_lightb(c, Ubest)
    ver = verify(c, Ubest)
    ver["final_screen"] = final_screen_info
    lower = [0] * final_screen_info["n_lower"]
    runaways = [0] * final_screen_info["n_runaway_dirs"]
    report.update(status="FEASIBLE", t=float(tbest), c=vc.cdict(c), verify=ver,
                  octet_info=OCT.get("info"), seconds=time.time() - T0)
    np.savez(vc.BIG / f"{args.out}.npz", c=c, y=y, t=tbest, ids=np.array(vc.IDS), beta_re=BETA.real, beta_im=BETA.imag,
             a_ew=A_EW if A_EW is not None else np.zeros(0), **{f"U{k}": v for k, v in Ubest.items()})
    log(f"RESULT t = {tbest:.6g}; zero {ver['n_zero']} neg {ver['n_neg']} light {ver['n_light']} (expected {expected_light}) "
        f"heavy {ver['n_heavy']} min heavy {ver['min_heavy']:.4g}; |grad| {ver['grad_residual']:.2e}; "
        f"competitor min gap {ver.get('competitor_min_gap')}; BFB min {ver['bfb_min']}; a0 max {max(np.abs(ver['a0'])):.3f}; "
        f"box ratio {ver['max_box_ratio']:.3f}")
    if EW:
        log(f"EW: residual {ver['ew']['eig_residual']:.2e}, |r| {ver['ew']['r_abs']:.4g}, s {ver['ew']['s']}, frac {ver['ew']['frac']}")
    if "lambda" in ver and ver["lambda"]:
        lam = ver["lambda"]
        log(f"lambda: direct {lam['lambda_direct']:.4g}, eff_heavy {lam['lambda_eff_heavy']:.4g}, eff_all {lam['lambda_eff_all']:.4g}")
    if "octet_cubics" in ver:
        log(f"octet cubics {ver['octet_cubics']}")
    log(f"final screen: lowest - V* = {ver['final_screen']['lowest-V*']:.4g}, n_lower {len(lower)}, runaways {len(runaways)}")
json.dump(vc.jsonable(report), open(vc.BIG / f"{args.out}.json", "w"), indent=1)
log(f"done {time.time()-T0:.0f}s")
