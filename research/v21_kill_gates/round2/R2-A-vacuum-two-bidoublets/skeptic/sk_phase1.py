"""SKEPTIC (R2-A): own phase-1 cutting-plane LP for the 'flavour-composition cells are empty after the feedback cuts' claim.

Written independently of r2_lp6.py (only the researcher's DATA files are read: <tag>_blocks.npz, <tag>_rows.npz,
ew_<tag>_*.npz, S5_* / G* npz for warm-start subspaces, descend_*_bank.npz, ray banks, unit_rows_traces.json).

Problem at a fixed light subspace U (interlacing formulation, same physics as the gate):
  c = N y (stationarity null space), boxes |c_i| <= (40, 2, 1) for mass/cubic/quartic rows,
  EW eigen-equation A_(1,2)(c) a* = lam a* (exact, linear),
  heavy blocks: Q0^H A Q0 >= t;  sandwich blocks: eps_lo <= A <= eps_hi;
  sub blocks:  Q0^H A Q0 >= eps_lo,  U^H A U <= eps_hi,  Qc^H A Qc >= t,
  singlet-channel unitarity |eig(sum c_i M_i)| <= 8 pi,
  BFB rays: V4_c(u_k) >= eps_bfb,
  competitor points (all banked descent points + stored SM-singlet/Delta_R banks):  V*_c - V_c(q_k) + mu t mf_k <= s.
PHASE 1: minimise s (s <= 0  <=>  the cell is feasible with every banked competitor lifted).
THE NEW PART: the gate's infeasible runs fixed U (warm start, no update because no feasible point existed).  Here U is
updated from the phase-1 optimum (every phase-1 point is feasible for the local constraints, so s is monotone), and
random U restarts are tried.  If s* -> <= 0 the 'empty cell' claim is refuted; if s* stays > 0 it is supported (locally).
usage: python -B sk_phase1.py <tag> <content C2e|C1622e> <ew npz> <banks file list (txt)> <out> [--U npz] [--tmin 1e-3]
       [--uiter 6] [--restarts 4] [--cubic npz] [--seed 1]
"""
from __future__ import annotations
import argparse, json, math, time, sys
from pathlib import Path
import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent

ap = argparse.ArgumentParser()
ap.add_argument("tag"); ap.add_argument("content"); ap.add_argument("ew"); ap.add_argument("banks"); ap.add_argument("out")
ap.add_argument("--U", default=None); ap.add_argument("--tmin", type=float, default=1e-3)
ap.add_argument("--uiter", type=int, default=6); ap.add_argument("--restarts", type=int, default=4)
ap.add_argument("--cubic", default=None); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--eps_lo", type=float, default=5e-7); ap.add_argument("--eps_hi", type=float, default=3e-6)
ap.add_argument("--ew_lambda", type=float, default=1e-7); ap.add_argument("--mu", type=float, default=0.1)
ap.add_argument("--d0", type=float, default=0.5); ap.add_argument("--eps_bfb", type=float, default=1e-4)
ap.add_argument("--box_scale", type=float, default=1.0)
ap.add_argument("--no_comp", action="store_true")
ap.add_argument("--no_bfb", action="store_true")
ap.add_argument("--stop_tol", type=float, default=1e-9)
ap.add_argument("--unit", type=float, default=0.5)
ap.add_argument("--screen", action="store_true")
ap.add_argument("--perturb", type=float, default=0.3)
ap.add_argument("--maxt", action="store_true", help="objective max t (s fixed to 0) instead of phase 1")
args = ap.parse_args()
T0 = time.time()
logf = open(HERE / f"{args.out}.log", "w", encoding="utf-8")


def log(m):
    print(m, flush=True); logf.write(m + "\n"); logf.flush()


# ------------------------------------------------------------------ data
B = np.load(PARENT / f"{args.tag}_blocks.npz")
labels = [str(x) for x in B["labels"]]; nb = len(labels); mult = B["m"]
A = [B[f"A{k}"] for k in range(nb)]; Gold = [B[f"G{k}"].astype(complex) for k in range(nb)]
ids = [str(x) for x in B["ids"]]; npar = len(ids)
Z = np.load(PARENT / f"{args.tag}_rows.npz"); VAL0 = Z["values"]; q0 = Z["q"]; HESS = Z["hess"]
assert [str(x) for x in Z["ids"]] == ids
TR = json.load(open(PARENT / "unit_rows_traces.json", encoding="utf-8")); DEG = TR["degrees"]
deg = np.array([DEG[p.split("::")[1]] for p in ids]); deg4 = deg == 4
boxes = np.array([{2: 40.0, 3: 2.0, 4: 1.0}[d] for d in deg]) * args.box_scale
# stationarity null space (own SVD)
_, sv, vt = np.linalg.svd(B["stat_rows"], full_matrices=True); rk = int(np.sum(sv > 1e-10 * sv[0])); N = vt[rk:].T; ny = N.shape[1]
Ay = [np.einsum("ia,ijk->ajk", N, A[k]) for k in range(nb)]
kb = {l: k for k, l in enumerate(labels)}; kd = kb["(1,2)_|Y|=1/2"]; ks = kb["(1,1)_|Y|=0"]

NOEW = args.ew == "none"
if NOEW:
    a_ew = np.zeros(mult[kd], complex); a_ew[1] = 1.0
else:
    a_ew = np.asarray(np.load(PARENT / args.ew)["a"], complex); a_ew /= np.linalg.norm(a_ew)
    Gold[kd] = np.column_stack([Gold[kd], a_ew]) if Gold[kd].shape[1] else a_ew[:, None]

SPECS = {"C2e": {"(1,2)_|Y|=1/2": 3, "(1,1)_|Y|=0": 2, "(1,1)_|Y|=2": "sandwich"},
         "C1622e": {"(1,2)_|Y|=1/2": 3, "(1,1)_|Y|=0": 2, "(1,1)_|Y|=2": "sandwich", "(8,3)_|Y|=0": "sandwich",
                    "(6,2)_|Y|=1/6": "sandwich", "(6,2)_|Y|=5/6": "sandwich"},
         "V0": {"(1,1)_|Y|=0": 2, "(1,1)_|Y|=2": "sandwich"},
         "C2": {"(1,2)_|Y|=1/2": 4, "(1,1)_|Y|=0": 2, "(1,1)_|Y|=2": "sandwich"}}
spec = SPECS[args.content]
if args.content == "V0":
    Gold[kd] = B[f"G{kd}"].astype(complex)


def J_from_values(vals, dids):
    di = {d: j for j, d in enumerate(dids)}; J = np.zeros((vals.shape[0], npar))
    for i, pid in enumerate(ids):
        comp, did = pid.split("::"); j = di[did]
        J[:, i] = vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag)
    return J


def load_bank(fn):
    z = np.load(PARENT / fn)
    if "J" in z.files:
        assert [str(x) for x in z["ids"]] == ids; return z["Q"], np.asarray(z["J"], float)
    return z["Q"], J_from_values(z["values"], [str(x) for x in z["ids"]])


# competitor + BFB banks
COMP_Q, COMP_J, BFB = [], [], []
bank_files = [x.strip() for x in open(HERE / args.banks).read().replace(",", "\n").split("\n") if x.strip()] if args.banks != "none" else []
for fn in bank_files:
    Q, J = load_bank(fn)
    for qq, jj in zip(Q, J):
        if np.linalg.norm(qq - q0) > 1e-6: COMP_Q.append(qq); COMP_J.append(jj)
    BFB.append(J * deg4[None, :] / np.linalg.norm(Q, axis=1)[:, None] ** 4)
# stored SM-singlet / Delta_R banks: competitor points unless inside the G3221 orbit of z* (subspace coordinates)
meta = json.load(open(PARENT / f"{args.tag}_rows_meta.json"))["point"]
zstar = np.array([meta["p"], meta["a"], meta["omega"], meta["r"], 0.0, meta["s"], meta["x"]])
SUB = np.load(HERE / "subdirs.npz")["D"]   # 7 x 486 subspace directions (built once by sk_subdirs.py with the repo chart)


def zcoords(q):
    return np.array([float(q @ d) / float(d @ d) for d in SUB])


def in_orbit(z):
    return (abs(abs(z[0]) - abs(zstar[0])) < 2e-3 and abs(abs(z[1]) - abs(zstar[1])) < 2e-3 and abs(z[2]) < 2e-3
            and abs(z[6] - zstar[6]) < 2e-2 and math.hypot(z[3], z[4]) < 0.02)


n_orbit = 0
for fn in ("smsinglet_pts.npz", "deltar_pts.npz"):
    Q, J = load_bank(fn)
    for qq, jj in zip(Q, J):
        if in_orbit(zcoords(qq)): n_orbit += 1; continue
        COMP_Q.append(qq); COMP_J.append(jj)
    BFB.append(J * deg4[None, :] / np.linalg.norm(Q, axis=1)[:, None] ** 4)
for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz", "hsrays_pts.npz"):
    try:
        Q, J = load_bank(fn); BFB.append(J * deg4[None, :] / np.linalg.norm(Q, axis=1)[:, None] ** 4)
    except FileNotFoundError:
        pass
if args.cubic:
    V4u = np.load(PARENT / args.cubic)["V4_up"]; BFB.append((V4u * deg4 / 24.0)[None, :])
COMP_Q = np.array(COMP_Q); COMP_J = np.array(COMP_J); BFB = np.vstack(BFB)
if args.no_bfb: BFB = BFB[:0]
dist = np.linalg.norm(COMP_Q - q0[None, :], axis=1); MF = np.minimum(1.0, (dist / args.d0) ** 4)
# the gate uses the subspace margin for the stored subspace banks; Euclidean margin is <= that only where both are < 1;
# with t >= tmin small the margin term is negligible either way (reported).
if args.no_comp: COMP_J = COMP_J[:0]; MF = MF[:0]
log(f"[{args.out}] tag {args.tag} content {args.content} ew {args.ew}: ny={ny}, competitor points {len(COMP_J)} (orbit-excluded {n_orbit}), BFB rays {len(BFB)}")

# unitarity matrices (singlet channel, exact trace lemma normalisation of K3)
ub = ["Phi210", "H10", "Sigma126bar", "S", "Phi17"]
nsz = {"Phi210": 210, "H10": 20, "Sigma126bar": 252, "S": 2, "Phi17": 2}   # real chart dimensions (sum 486)
Mi = np.zeros((npar, 5, 5))
for i, pid in enumerate(ids):
    if deg[i] != 4: continue
    for jb, Bn in enumerate(ub):
        for ia, An in enumerate(ub):
            val = TR["blocks"][Bn]["traces"][pid][An]
            Mi[i, ia, jb] = val if ia == jb else math.sqrt(nsz[Bn] / nsz[An]) * val
Mi = 0.5 * (Mi + np.transpose(Mi, (0, 2, 1))); MiY = np.einsum("ia,ijk->ajk", N, Mi); UB = 16 * math.pi * args.unit

# EW equalities (reduced rank)
Mv = np.einsum("ajk,k->aj", Ay[kd], a_ew); E = np.vstack([Mv.real.T, Mv.imag.T])
rhs = args.ew_lambda * np.concatenate([a_ew.real, a_ew.imag])
uE, sE, vE = np.linalg.svd(E, full_matrices=False); kE = int(np.sum(sE > 1e-10 * sE[0]))
EQ_y = vE[:kE]; EQ_b = (uE[:, :kE].T @ rhs) / sE[:kE]; ew_out = float(np.linalg.norm(rhs - uE[:, :kE] @ (uE[:, :kE].T @ rhs)))
if args.content == "V0" or NOEW: kE = 0
log(f"EW eigen-equation rank {kE} of {E.shape[0]}; rhs outside range {ew_out:.2e}")

nz = ny + 2; IT, IS = ny, ny + 1   # variables: y, t, s


def compl(M, m):
    if M is None or M.shape[1] == 0: return np.eye(m, dtype=complex)
    u, s_, _ = np.linalg.svd(M, full_matrices=True); r = int(np.sum(s_ > 1e-10)); return u[:, r:]


def ray_row(k, v):
    r = np.zeros(nz); r[:ny] = np.real(np.einsum("i,pij,j->p", v.conj(), Ay[k], v)); return r


def Ablk(k, y):
    M = np.einsum("p,pij->ij", y, Ay[k]); return 0.5 * (M + M.conj().T)


# ---------------- dynamic SM-singlet / Delta_R subspace screen (as the gate's LP does on every round) -------------
import itertools as _it
from scipy.optimize import minimize as _minimize
SCREEN = []
if args.screen:
    sys.path.insert(0, str(PARENT))
    import k3_common as _K
    _chart, _pot = _K.chart, _K.potential
    def J_at(q):
        jac = _pot.coefficient_jacobian(_pot.evaluate_directions(_chart.unpack(np.asarray(q, float)).validated()))
        return np.array([float(np.real(jac[p_])) for p_ in ids])
    _rs = np.random.default_rng(5)
    for _fn, _mode in (("smsinglet_pts.npz", "smsinglet"), ("deltar_pts.npz", "deltar")):
        _Q, _J = load_bank(_fn); _Z = np.array([zcoords(qq) for qq in _Q])
        _degs = [1, 1, 1, 2, 2, 2] if _mode == "smsinglet" else [1, 1, 1, 2, 2, 2, 2]
        _monos = np.array([pw for pw in _it.product(range(5), repeat=len(_degs)) if sum(a_ * d_ for a_, d_ in zip(pw, _degs)) <= 4])
        def _var(z, mode=_mode):
            z = np.atleast_2d(z)
            if mode == "smsinglet": return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3] ** 2, z[:, 5] ** 2, z[:, 6] ** 2])
            return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3] ** 2, z[:, 4] ** 2, z[:, 5] ** 2, z[:, 6] ** 2])
        def _X(zs, var=_var, monos=_monos): return np.prod(var(zs)[:, None, :] ** monos[None, :, :], axis=2)
        _n = 30000
        _zs = np.column_stack([_rs.uniform(-2, 2, (_n, 3)), _rs.uniform(-2, 2, (_n, 2)), _rs.uniform(-1.5, 1.5, (_n, 1)), _rs.uniform(-7, 7, (_n, 1))])
        if _mode == "smsinglet": _zs[:, 4] = 0
        _d = _rs.normal(size=(20000, 7))
        if _mode == "smsinglet": _d[:, 4] = 0
        _d /= np.linalg.norm(_d, axis=1)[:, None]
        SCREEN.append({"mode": _mode, "J": _J, "Pinv": np.linalg.pinv(_X(_Z)), "X": _X, "zs": _zs, "Xs": _X(_zs), "monos": _monos, "dirs": _d, "Xd": _X(_d)})
    log(f"dynamic subspace screen on ({[sc['mode'] for sc in SCREEN]})")


def q_of_z(z):
    return sum(zi * d for zi, d in zip(z, SUB))


def run_screen(c, max_new=4):
    """returns lists of new competitor J rows (with margin factors) and new BFB rows found on the two subspaces."""
    newc, newb, info = [], [], []
    for sc in SCREEN:
        coef = sc["Pinv"] @ (sc["J"] @ c); Vz = lambda z: float(sc["X"](np.asarray(z)[None, :])[0] @ coef)
        Vst = Vz(zstar); order = np.argsort(sc["Xs"] @ coef)[:30]; found = []
        for j in list(order) + [None]:
            r = _minimize(Vz, zstar if j is None else sc["zs"][j], method="BFGS", options={"gtol": 1e-9, "maxiter": 400})
            zz = np.array(r.x)
            if sc["mode"] == "smsinglet": zz[4] = 0
            found.append((float(r.fun), zz))
        # quartic (BFB) part on the unit sphere of the subspace: homogeneous degree-4 monomials only
        top = np.array([sum(a_ * d_ for a_, d_ in zip(pw, [1, 1, 1, 2, 2, 2] if sc["mode"] == "smsinglet" else [1, 1, 1, 2, 2, 2, 2])) == 4 for pw in sc["monos"]])
        V4z = lambda z: float((sc["X"](np.asarray(z)[None, :])[0] * top) @ coef)
        dirs = sc["dirs"]; v4s = (sc["Xd"] * top[None, :]) @ coef
        for j in np.argsort(v4s)[:6]:
            r = _minimize(lambda z: V4z(z / np.linalg.norm(z)), dirs[j], method="BFGS", options={"gtol": 1e-10, "maxiter": 300})
            zh = np.array(r.x) / np.linalg.norm(r.x)
            if sc["mode"] == "smsinglet": zh[4] = 0; zh /= np.linalg.norm(zh)
            if V4z(zh) < args.eps_bfb * 0.5:
                found.append((-1e30, zh * 1e3))   # treated as a runaway direction below
        found.sort(key=lambda tt: tt[0]); k_ = 0
        for Vm, zm in found:
            if k_ >= max_new: break
            if np.max(np.abs(zm)) > 30:
                qd = q_of_z(zm / np.linalg.norm(zm)); Jq = J_at(qd); newb.append(Jq * deg4 / float(np.linalg.norm(qd)) ** 4); k_ += 1
                info.append((sc["mode"], "runaway", float(np.max(np.abs(zm)))))
            elif Vm < Vst - 1e-10 * max(1.0, abs(Vst)) and not in_orbit(zm):
                qm = q_of_z(zm); Jq = J_at(qm); mf = min(1.0, (float(np.linalg.norm(qm - q0)) / args.d0) ** 4)
                newc.append((Jq, mf)); k_ += 1; info.append((sc["mode"], "lower", float(c @ Jq - VAL0 @ c)))
    return newc, newb, info


def solve_fixedU(U, objective="phase1", max_iter=600):
    """cutting-plane LP at fixed U; returns (status, y, t, s, worst)."""
    global COMP_J, MF, BFB
    Aub, bub = [], []
    for i in range(npar):
        r = np.zeros(nz); r[:ny] = N[i]; Aub += [r, -r]; bub += [boxes[i], boxes[i]]
    for jj, mf in zip(COMP_J, MF):
        r = np.zeros(nz); r[:ny] = (VAL0 - jj) @ N; r[IT] = args.mu * mf; r[IS] = -1.0
        sc = max(1.0, float(np.max(np.abs(r[:ny])))); Aub.append(r / sc); bub.append(0.0)
    for jj in BFB:
        r = np.zeros(nz); r[:ny] = -(jj @ N); Aub.append(r); bub.append(-args.eps_bfb)
    comps = {}
    for k in range(nb):
        m = mult[k]; kind = spec.get(labels[k], "heavy"); Q0 = compl(Gold[k], m)
        if isinstance(kind, int):
            Qc = compl(np.column_stack([U[k], Gold[k]]) if Gold[k].shape[1] else U[k], m); comps[k] = ("sub", Q0, Qc)
        else:
            comps[k] = (kind, Q0, None)
    cuts_A, cuts_b = [], []
    rng = np.random.default_rng(3)
    for k, (kind, Q0, Qc) in comps.items():
        if Q0.shape[1] == 0: continue
        H = Qc if kind == "sub" else Q0
        vecs = [H[:, j] for j in range(H.shape[1])] if H is not None else []
        for v in vecs:
            r = ray_row(k, v)
            if kind == "sandwich": cuts_A += [-r, r.copy()]; cuts_b += [-args.eps_lo, args.eps_hi]
            else: r[IT] = -1.0; cuts_A.append(-r); cuts_b.append(0.0)
        if kind == "sub":
            for l in range(U[k].shape[1]):
                r = ray_row(k, U[k][:, l]); cuts_A += [-r, r.copy()]; cuts_b += [-args.eps_lo, args.eps_hi]
    for j in range(5):
        for sg in (1, -1):
            r = np.zeros(nz); r[:ny] = sg * MiY[:, j, j]; cuts_A.append(r); cuts_b.append(UB)
    obj = np.zeros(nz)
    if objective == "phase1": obj[IS] = 1.0; obj[IT] = -1e-6
    else: obj[IT] = -1.0
    bounds = [(None, None)] * ny + [(args.tmin, 2.0), (-50.0, None) if objective == "phase1" else (0.0, 0.0)]
    res = None; worst = None
    for it in range(max_iter):
        for meth, opts in (("highs-ds", {"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10}),
                           ("highs-ipm", {"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9}),
                           ("highs", {})):
            res = linprog(obj, A_ub=np.array(Aub + cuts_A), b_ub=np.array(bub + cuts_b), A_eq=(np.hstack([EQ_y, np.zeros((kE, 2))]) if kE else None),
                          b_eq=(EQ_b if kE else None), bounds=bounds, method=meth, options=opts)
            if res.status == 0: break
        if res.status != 0:
            log(f"    LP status {res.status} at cut iteration {it}: {res.message[:120]}")
            return res.status, None, None, None, None
        z = res.x; y = z[:ny]; t = z[IT]; n_new = 0; worst = 0.0
        for k, (kind, Q0, Qc) in comps.items():
            M = Ablk(k, y)
            if kind == "sandwich":
                w, V = np.linalg.eigh(Q0.conj().T @ M @ Q0)
                for j in range(len(w)):
                    v = Q0 @ V[:, j]
                    if w[j] < args.eps_lo - 1e-13: cuts_A.append(-ray_row(k, v)); cuts_b.append(-args.eps_lo); n_new += 1; worst = max(worst, args.eps_lo - w[j])
                    if w[j] > args.eps_hi + 1e-13: cuts_A.append(ray_row(k, v)); cuts_b.append(args.eps_hi); n_new += 1; worst = max(worst, w[j] - args.eps_hi)
                continue
            H = Qc if kind == "sub" else Q0
            if H.shape[1]:
                w, V = np.linalg.eigh(H.conj().T @ M @ H)
                for j in range(len(w)):
                    if w[j] < t - 1e-13:
                        r = ray_row(k, H @ V[:, j]); r[IT] = -1.0; cuts_A.append(-r); cuts_b.append(0.0); n_new += 1; worst = max(worst, t - w[j])
            if kind == "sub":
                Uk = U[k]; w, V = np.linalg.eigh(Uk.conj().T @ M @ Uk)
                for j in range(len(w)):
                    if w[j] > args.eps_hi + 1e-13: cuts_A.append(ray_row(k, Uk @ V[:, j])); cuts_b.append(args.eps_hi); n_new += 1; worst = max(worst, w[j] - args.eps_hi)
                w, V = np.linalg.eigh(Q0.conj().T @ M @ Q0)
                for j in range(len(w)):
                    if w[j] < args.eps_lo - 1e-13: cuts_A.append(-ray_row(k, Q0 @ V[:, j])); cuts_b.append(-args.eps_lo); n_new += 1; worst = max(worst, args.eps_lo - w[j])
        Mu = np.einsum("p,pij->ij", y, MiY); w, V = np.linalg.eigh(Mu)
        for j in range(5):
            if abs(w[j]) > UB - 1e-12:
                r = np.zeros(nz); r[:ny] = np.einsum("i,pij,j->p", V[:, j], MiY, V[:, j]) * np.sign(w[j]); cuts_A.append(r); cuts_b.append(UB); n_new += 1
        if n_new == 0 or (worst < args.stop_tol and it > 5):
            if not SCREEN: break
            newc, newb, info = run_screen(N @ y)
            if not newc and not newb: break
            for jq, mf in newc:
                r = np.zeros(nz); r[:ny] = (VAL0 - jq) @ N; r[IT] = args.mu * mf; r[IS] = -1.0
                sc_ = max(1.0, float(np.max(np.abs(r[:ny])))); Aub.append(r / sc_); bub.append(0.0)
                COMP_J = np.vstack([COMP_J, jq[None, :]]); MF = np.append(MF, mf)
            for jb in newb:
                r = np.zeros(nz); r[:ny] = -(jb @ N); Aub.append(r); bub.append(-args.eps_bfb); BFB = np.vstack([BFB, jb[None, :]])
            log(f"    screen at cut-iteration {it}: added {len(newc)} competitor / {len(newb)} BFB rows {info}")
    z = res.x
    return 0, z[:ny], z[IT], z[IS], worst


def update_U(y):
    U = {}
    for k in range(nb):
        kind = spec.get(labels[k], "heavy")
        if not isinstance(kind, int): continue
        Q0 = compl(Gold[k], mult[k]); w, V = np.linalg.eigh(Q0.conj().T @ Ablk(k, y) @ Q0); U[k] = Q0 @ V[:, :kind]
    return U


def initial_U():
    U = {}
    if args.U:
        zu = np.load(PARENT / args.U)
    for k in range(nb):
        kind = spec.get(labels[k], "heavy")
        if not isinstance(kind, int): continue
        Q0 = compl(Gold[k], mult[k])
        if args.U and f"U{k}" in zu.files and zu[f"U{k}"].shape[1] in (kind, kind + 1):
            Uk = zu[f"U{k}"]; Uk = Q0 @ (Q0.conj().T @ Uk); u_, s_, _ = np.linalg.svd(Uk, full_matrices=False); U[k] = u_[:, :kind]
        elif k == kd:
            # heavy = the Phi210 doublet (index 0): U = complement of (Phi210 doublet, a*)  (the gate's initial_U)
            e0 = np.zeros(mult[k], complex); e0[0] = 1; U[k] = compl(np.column_stack([Gold[k], e0]), mult[k])
        else:
            U[k] = Q0[:, :kind]
    return U


def perturb_U(U, rng, amp):
    Un = {}
    for k, Uk in U.items():
        Q0 = compl(Gold[k], mult[k]); X = Uk + amp * (Q0 @ (rng.normal(size=(Q0.shape[1], Uk.shape[1])) + 1j * rng.normal(size=(Q0.shape[1], Uk.shape[1]))))
        u_, s_, _ = np.linalg.svd(X, full_matrices=False); Un[k] = u_
    return Un


def verify(y):
    c = N @ y; H = np.einsum("p,pij->ij", c, HESS); H = 0.5 * (H + H.T); w = np.linalg.eigvalsh(H)
    out = {"n_zero": int(np.sum(np.abs(w) < 1e-9)), "n_neg": int(np.sum(w < -1e-9)), "n_light": int(np.sum((w >= 1e-9) & (w < 10 * args.eps_hi))),
           "n_heavy": int(np.sum(w >= 10 * args.eps_hi)), "min_eig": float(w[0]), "min_heavy": float(np.min(w[w >= 10 * args.eps_hi]))}
    Vs = float(VAL0 @ c); gaps = COMP_J @ c - Vs
    out["V_star"] = Vs; out["competitor_min_gap"] = float(np.min(gaps)) if len(gaps) else None
    out["n_competitors_below"] = int(np.sum(gaps < 0)); out["bfb_min"] = float(np.min(BFB @ c))
    Mu = np.einsum("p,pij->ij", c, Mi); out["a0"] = (np.linalg.eigvalsh(Mu) / (16 * math.pi)).tolist()
    M = Ablk(kd, y); out["ew_residual"] = float(np.linalg.norm(M @ a_ew - args.ew_lambda * a_ew))
    out["doublet_eigs"] = np.linalg.eigvalsh(M).tolist(); out["singlet_eigs"] = np.linalg.eigvalsh(Ablk(ks, y)).tolist()
    out["max_box_ratio"] = float(np.max(np.abs(c) / boxes))
    return out, c


rng = np.random.default_rng(args.seed)
results = {"args": vars(args), "ny": ny, "n_comp": int(len(COMP_J)), "n_bfb": int(len(BFB)), "runs": []}
best = (np.inf, None, None)
U0 = initial_U()
starts = [("warm", U0)]
for r_ in range(args.restarts):
    starts.append((f"perturb{r_}", perturb_U(U0, rng, args.perturb * (1 + r_))))
for name, U in starts:
    hist = []
    for ui in range(args.uiter):
        st, y, t, s, worst = solve_fixedU(U, "maxt" if args.maxt else "phase1")
        if st != 0:
            hist.append({"uiter": ui, "status": int(st)}); log(f"  [{name}] U-iter {ui}: LP status {st} (local constraints infeasible at this U)"); break
        Vs = float(VAL0 @ (N @ y))
        hist.append({"uiter": ui, "s": float(s), "t": float(t), "worst_cut": float(worst)})
        log(f"  [{name}] U-iter {ui}: phase-1 s* = {s:+.6g} (t = {t:.4g}, worst local violation {worst:.2e}, V* = {Vs:.4f})  {time.time()-T0:.0f}s")
        key = -t if args.maxt else s
        if key < best[0]: best = (float(key), y.copy(), {k: v.copy() for k, v in U.items()})
        Unew = update_U(y)
        chg = max(1 - np.min(np.linalg.svd(U[k].conj().T @ Unew[k], compute_uv=False)) ** 2 for k in U)
        U = Unew
        if chg < 1e-12: break
    results["runs"].append({"start": name, "history": hist})
    json.dump(results, open(HERE / f"{args.out}.json", "w"), indent=1, default=float)
if best[1] is not None:
    ver, c = verify(best[1]); results["best_s"] = best[0]; results["best_verify"] = ver
    np.savez(HERE / f"{args.out}.npz", c=c, y=best[1], ids=np.array(ids), **{f"U{k}": v for k, v in best[2].items()})
    log(f"BEST s* = {best[0]:+.6g}; verify: {json.dumps({k: v for k, v in ver.items() if k not in ('doublet_eigs', 'singlet_eigs')}, default=float)}")
json.dump(results, open(HERE / f"{args.out}.json", "w"), indent=1, default=float)
log(f"done {time.time()-T0:.0f}s")
