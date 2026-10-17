"""R2-A cutting-plane LP v5 = K3's v4 with the light-subspace constraints of a 'sub' block replaced by the
INTERLACING formulation (no invariance constraints):  for a block with Goldstone complement Q0 and a trial light
subspace U (nl columns) with complement Qc (in range Q0):
    Q0^+ A(c) Q0  >= eps_lo            (every non-Goldstone eigenvalue >= eps_lo)
    U^+ A(c) U    <= eps_hi            (compression to U: by Cauchy interlacing lambda_1..nl(A) <= eps_hi)
    Qc^+ A(c) Qc  >= t                 (compression to Qc: by interlacing lambda_{nl+1}(A) >= t)
All three are LMIs in c (handled by eigenvector cutting planes), so a converged optimum at fixed U is the true optimum;
the outer loop resets U to the lowest-nl eigenvectors, and the previous point stays feasible (t is monotone).
The light eigenvalue COUNT is therefore guaranteed by interlacing; the final full-Hessian count is still reported.
Extra options: --cubic <npz> (light-cubic rows at this point; default cubic_rows.npz only for tag Am45, else none),
--no_outer_update (keep U fixed: composition targets), --Ufile <npz with U<k>> (initial/fixed U).

Original K3 v4 docstring follows.
Cutting-plane LP v4 = v3 (light content, heavy gap, unitarity) + global/BFB/Higgs-quartic controls.

New linear/convex constraints (all exact in the coupling vector c = N y, N = stationarity null space):
  competitor energy : V_c(z*) <= V_c(z_k) - mu t  for a bank of SM-singlet-subspace points z_k (and any point found
                      lower by the exact subspace polynomial search, which is re-run on every round and adds points);
  BFB (necessary)   : V4_c(u_k) >= eps_bfb on a bank of unit rays (random 486-rays + the singlet-subspace bank rays);
  light cubics      : |v . b(c)| <= delta_b for every light (v_R-scale) neutral non-doublet eigen-direction v,
                      b_i = d^3 D_i/du du dphi along the neutral up-type H10 doublet direction u (cubic_rows.npz);
  stage B (Kelley)  : rho >= R(y_k) + grad R(y_k).(y - y_k), R(y) = b^T M^-1 b over the heavy modes (convex),
                      objective max lambda_eff = V4(u)/6 - rho/2  (or min rho), with t >= t_min and fixed U.

usage: python -B k3_lp4.py <tag> <out> [--light "label:kind;..."] [--unitarity 0.5] [--stage A|B] [--fixU file]
       [--mu 0.1] [--eps_bfb 1e-4] [--delta_b 1e-5] [--tmin 0.01] [--objective max_leff|min_R] [--lam_direct_max L]
"""
from __future__ import annotations
import sys, json, math, time, argparse, itertools
import numpy as np
from scipy.optimize import linprog, minimize
import k3_common as K

ap = argparse.ArgumentParser()
ap.add_argument("tag"); ap.add_argument("out")
ap.add_argument("--light", default="(1,2)_|Y|=1/2:sub2;(8,3)_|Y|=0:sandwich")
ap.add_argument("--vev_light", default="g3221")
ap.add_argument("--eps_lo", type=float, default=0.5e-6); ap.add_argument("--eps_hi", type=float, default=3.0e-6)
ap.add_argument("--theta", type=float, default=0.0)
ap.add_argument("--outer", type=int, default=5); ap.add_argument("--iters", type=int, default=500)
ap.add_argument("--delta", type=float, default=1.0e-8)
ap.add_argument("--box_quartic", type=float, default=1.0); ap.add_argument("--box_cubic", type=float, default=2.0); ap.add_argument("--box_mass", type=float, default=40.0)
ap.add_argument("--unitarity", type=float, default=None)
ap.add_argument("--fixU", default=None)
ap.add_argument("--mu", type=float, default=0.1, help="competitor margin in units of t")
ap.add_argument("--d0", type=float, default=0.5, help="competitor margin scale: margin = mu t min(1,(d/d0)^4)")
ap.add_argument("--eps_bfb", type=float, default=1.0e-4)
ap.add_argument("--delta_b", type=float, default=1.0e-5)
ap.add_argument("--no_competitor", action="store_true"); ap.add_argument("--no_bfb", action="store_true"); ap.add_argument("--no_lightb", action="store_true")
ap.add_argument("--stage", default="A")
ap.add_argument("--tmin", type=float, default=0.01)
ap.add_argument("--objective", default="max_leff")
ap.add_argument("--lam_direct_max", type=float, default=None)
ap.add_argument("--lam_direct_min", type=float, default=None)
ap.add_argument("--kelley_iters", type=int, default=400)
ap.add_argument("--search_every", type=int, default=15)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--nonneg", default="", help="comma-separated operator prefixes whose lambda:: couplings are constrained >= 0")
ap.add_argument("--box_override", default="", help="per-operator box overrides, e.g. O05:3,O06:3,O07:3")
ap.add_argument("--extra_comp", default="", help="comma-separated npz banks (Q, values, ids) added as competitor points and BFB rays")
ap.add_argument("--cubic", default=None, help="cubic rows npz at this point (b_up, V4_up, u_up)")
ap.add_argument("--no_outer_update", action="store_true")
ap.add_argument("--Ufile", default=None, help="npz with U<k> arrays used as the initial (or fixed) light subspaces")
ap.add_argument("--abs_bound", default="", help="per-operator absolute bounds |c| <= val, e.g. im::O31:0.05,re::O31:0.05")
ap.add_argument("--save_every_outer", action="store_true")
ap.add_argument("--stall", type=int, default=60)
args = ap.parse_args()

t_start = time.time()
B = np.load(K.SCRATCH / f"{args.tag}_blocks.npz")
labels = [str(x) for x in B["labels"]]; nb = len(labels)
A = [B[f"A{k}"] for k in range(nb)]; Gold = [B[f"G{k}"] for k in range(nb)]; Wk = [B[f"W{k}"] for k in range(nb)]
mult = B["m"]; stat_rows = B["stat_rows"]; Tgold = B["T"]
ids = [str(x) for x in B["ids"]]; n_par = len(ids)
meta = json.load(open(K.SCRATCH / f"{args.tag}_blocks.json", encoding="utf-8"))["blocks"]
kb = {lab: k for k, lab in enumerate(labels)}
Z = np.load(K.SCRATCH / f"{args.tag}_rows.npz"); HESS = Z["hess"]; VAL0 = Z["values"]; q0 = Z["q"]
assert [str(x) for x in Z["ids"]] == ids
point = json.load(open(K.SCRATCH / f"{args.tag}_rows_meta.json"))["point"]
cubfile = args.cubic if args.cubic else ("cubic_rows.npz" if args.tag == "Am45" else None)
if cubfile is not None:
    CUB = np.load(K.SCRATCH / cubfile); assert [str(x) for x in CUB["ids"]] == ids
    b_up = CUB["b_up"]; V4_up = CUB["V4_up"]; u_up = CUB["u_up"]
else:
    b_up = np.zeros((len(ids), K.TOTAL)); V4_up = np.zeros(len(ids)); u_up = None
    args.no_lightb = True
TR = json.load(open(K.SCRATCH / "unit_rows_traces.json", encoding="utf-8")); DEG = TR["degrees"]


def degree_of(pid):
    return DEG[pid.split("::")[1]]


boxes = np.array([{2: args.box_mass, 3: args.box_cubic, 4: args.box_quartic}[degree_of(p)] for p in ids])
for item in [x for x in args.box_override.split(",") if x]:
    op, val = item.split(":")
    for i, pid in enumerate(ids):
        if pid.split("::")[1].startswith(op): boxes[i] = float(val)
u_, s_, vt = np.linalg.svd(stat_rows, full_matrices=True); Nmat = vt[stat_rows.shape[0]:].T; ny = Nmat.shape[1]
Ay = [np.einsum("ia,ijk->ajk", Nmat, A[k]) for k in range(nb)]
deg4 = np.array([degree_of(p) == 4 for p in ids])

out = args.out
logf = open(K.SCRATCH / f"{out}.log", "w", encoding="utf-8")


def log(msg):
    print(msg, flush=True); logf.write(msg + "\n"); logf.flush()


# ---------------- banks: per-parameter values J (n x 51) from direction values -----------------
def J_from_values(vals, dids):
    dindex = {d: j for j, d in enumerate(dids)}; J = np.zeros((vals.shape[0], n_par))
    for i, pid in enumerate(ids):
        comp, did = pid.split("::"); j = dindex[did]
        J[:, i] = vals[:, j].real if comp == "lambda" else (2 * vals[:, j].real if comp == "re" else -2 * vals[:, j].imag)
    return J


def J_at_state(state):
    dirs = K.potential.evaluate_directions(state); jac = K.potential.coefficient_jacobian(dirs)
    return np.array([jac[pid] for pid in ids])


chart = K.chart; basis = K.direct.singlet_basis()


def pk(**kw):
    d = dict(phi={}, h=np.zeros(10, complex), sigma={}, s=0j, x=0j); d.update(kw); return chart.pack(K.potential.FieldState(**d))


Pv, Av, Ov = pk(phi=basis["p"]), pk(phi=basis["a"]), pk(phi=basis["omega"])
sig_std = K.candidate.sigma_std_unit_coordinates()
Sv = pk(sigma=chart.sigma_from_coordinates(sig_std))
drc = chart.sigma_coordinates(K.direct.delta_r()); drc /= np.linalg.norm(drc); Dv = pk(sigma=chart.sigma_from_coordinates(drc))
Sc = pk(s=1 + 0j); Xc = pk(x=1 + 0j)
SUBDIRS = [Pv, Av, Ov, Sv, Dv, Sc, Xc]
zstar = np.array([point["p"], point["a"], point["omega"], point["r"], 0.0, point["s"], point["x"]])


def state_of_z(z):
    phi = K.phi_form(z[0], z[1], z[2]); sigma = chart.sigma_from_coordinates(z[3] * sig_std + z[4] * drc)
    return K.potential.FieldState(phi=phi, h=np.zeros(10, complex), sigma=sigma, s=complex(z[5]), x=complex(z[6])).validated()


class SubspaceFit:
    """Exact polynomial of V_c restricted to the (p,a,om,r1[,r2],s,x) subspace; fitted per c from the stored bank."""

    def __init__(self, npz, mode, rng):
        pts = np.load(K.SCRATCH / npz); self.mode = mode
        self.Q = pts["Q"]; self.J = J_from_values(pts["values"], [str(x) for x in pts["ids"]])
        coords = np.array([[float(q @ d) / float(d @ d) for d in SUBDIRS] for q in self.Q])
        self.degs = [1, 1, 1, 2, 2, 2] if mode == "smsinglet" else [1, 1, 1, 2, 2, 2, 2]
        self.monos = np.array([pw for pw in itertools.product(range(5), repeat=len(self.degs)) if sum(p * d for p, d in zip(pw, self.degs)) <= 4])
        X = self.mono_matrix(coords); self.Pinv = np.linalg.pinv(X); self.X = X
        self.rank = np.linalg.matrix_rank(X)
        # fixed random sample for the global pre-screen
        n = 30000
        zs = np.column_stack([rng.uniform(-1.5, 1.5, (n, 3)), rng.uniform(0, 1.5, (n, 2)), rng.uniform(0, 1.5, (n, 1)), rng.uniform(0, 6, (n, 1))])
        self.sample = zs; self.Xs = self.mono_matrix(zs)

    def var(self, z):
        z = np.atleast_2d(z)
        if self.mode == "smsinglet": return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3] ** 2, z[:, 5] ** 2, z[:, 6] ** 2])
        return np.column_stack([z[:, 0], z[:, 1], z[:, 2], z[:, 3] ** 2, z[:, 4] ** 2, z[:, 5] ** 2, z[:, 6] ** 2])

    def mono_matrix(self, zs):
        v = self.var(zs); return np.prod(v[:, None, :] ** self.monos[None, :, :], axis=2)

    def fit(self, c):
        Vvals = self.J @ c; coef = self.Pinv @ Vvals; resid = float(np.max(np.abs(self.X @ coef - Vvals))); return coef, resid

    def V(self, coef, z):
        return float(self.mono_matrix(np.asarray(z)[None, :])[0] @ coef)

    def search(self, c, n_polish=12):
        coef, resid = self.fit(c); vs = self.Xs @ coef; order = np.argsort(vs)[:n_polish]
        found = []
        for j in order:
            r = minimize(lambda z: self.V(coef, z), self.sample[j], method="BFGS", options={"gtol": 1e-9, "maxiter": 400})
            found.append((float(r.fun), np.array(r.x)))
        # also polish from z* itself
        r = minimize(lambda z: self.V(coef, z), zstar, method="BFGS", options={"gtol": 1e-9, "maxiter": 400}); found.append((float(r.fun), np.array(r.x)))
        found.sort(key=lambda t: t[0]); return found, coef, resid


def in_g3221_orbit(z):
    """gauge copies of z* inside the subspace: same |p|,|a|, om = 0, x = x*, and (essentially) no Sigma vev."""
    return (abs(abs(z[0]) - abs(zstar[0])) < 2e-3 and abs(abs(z[1]) - abs(zstar[1])) < 2e-3 and abs(z[2]) < 2e-3
            and abs(z[6] - zstar[6]) < 2e-2 and math.hypot(z[3], z[4]) < 0.02)


rng = np.random.default_rng(args.seed)
fits = []
if not args.no_competitor:
    fits = [SubspaceFit("smsinglet_pts.npz", "smsinglet", rng), SubspaceFit("deltar_pts.npz", "deltar", rng)]
    log(f"subspace fits: ranks {[f.rank for f in fits]} of {[len(f.monos) for f in fits]} monomials")
# competitor bank (J rows) initialised from the stored banks (excluding points inside the G3221 orbit)
COMP_J = []; COMP_M = []
def margin_factor(q): d = float(np.linalg.norm(q - q0)); return min(1.0, (d / args.d0) ** 4)
for f in fits:
    coords = np.array([[float(q @ d) / float(d @ d) for d in SUBDIRS] for q in f.Q])
    for row, z, qq in zip(f.J, coords, f.Q):
        if not in_g3221_orbit(z): COMP_J.append(row); COMP_M.append(margin_factor(qq))
EXTRA_BFB = []
for fn in [x for x in args.extra_comp.split(",") if x]:
    eb = np.load(K.SCRATCH / fn)
    if "J" in eb.files:
        assert [str(x) for x in eb["ids"]] == ids; Je = np.asarray(eb["J"], float)
    else:
        Je = J_from_values(eb["values"], [str(x) for x in eb["ids"]])
    ne = np.linalg.norm(eb["Q"], axis=1)
    for row, qq in zip(Je, eb["Q"]):
        if np.linalg.norm(qq - q0) > 1e-6: COMP_J.append(row); COMP_M.append(margin_factor(qq))
    EXTRA_BFB.append((Je * deg4[None, :]) / ne[:, None] ** 4)
    log(f"extra bank {fn}: {len(ne)} points")
COMP_J = np.array(COMP_J) if COMP_J else np.zeros((0, n_par)); COMP_M = np.array(COMP_M)
# BFB bank: degree-4 parts of rays (random 486 rays) + the singlet bank points normalised (homogeneous degree-4 part scales as |q|^4)
BFB_J = []
if not args.no_bfb:
    for fn in ("rays_pts.npz", "blockrays_pts.npz", "tripletrays_pts.npz", "hsrays_pts.npz"):
        try:
            rp = np.load(K.SCRATCH / fn); Jr = J_from_values(rp["values"], [str(x) for x in rp["ids"]])
            nr = np.linalg.norm(rp["Q"], axis=1); BFB_J.append((Jr * deg4[None, :]) / nr[:, None] ** 4)
            log(f"BFB: {len(nr)} rays loaded from {fn}")
        except FileNotFoundError:
            log(f"BFB: {fn} not found (skipped)")
    for f in fits:
        nr = np.linalg.norm(f.Q, axis=1); BFB_J.append((f.J * deg4[None, :]) / nr[:, None] ** 4)
    # the pure doublet ray: V4(u) = sum_i c_i V4_i / 24
    BFB_J.append((V4_up * deg4 / 24.0)[None, :])
    BFB_J += EXTRA_BFB
BFB_J = np.vstack(BFB_J) if BFB_J else np.zeros((0, n_par))
log(f"competitor bank {COMP_J.shape[0]} points; BFB bank {BFB_J.shape[0]} rays")

# ---------------- light content spec, initial subspaces (as lp3) -----------------
Xop = np.zeros((K.TOTAL, K.TOTAL))
for name, sl in K.BLOCKS.items():
    charge = {"Phi210": 0, "H10": -2, "Sigma126bar": -2, "S": 4, "Phi17": 17}[name]
    if charge == 0: continue
    idx = np.arange(sl.start, sl.stop)
    for i in range(0, len(idx), 2):
        Xop[idx[i], idx[i + 1]] = -charge; Xop[idx[i + 1], idx[i]] = charge
for k in range(nb):
    xs = np.real(np.einsum("ij,jk,ki->i", Wk[k].conj().T, 1j * Xop, Wk[k]))
    for j, m_ in enumerate(meta[k]["meta"]): m_["X"] = round(float(xs[j]), 3)
VEV = {"(1,1)_|Y|=0": "sub2", "(1,1)_|Y|=2": "sandwich"}
spec = dict(VEV)
for item in [x for x in args.light.split(";") if x]:
    lab, kind = item.split(":")
    if kind == "heavy": spec.pop(lab, None)
    else: spec[lab] = kind
for lab in spec: assert lab in kb, lab
eps_lo, eps_hi, delta = args.eps_lo, args.eps_hi, args.delta


def complement(U, m):
    if U is None or U.shape[1] == 0: return np.eye(m, dtype=complex)
    uu, ss, _ = np.linalg.svd(U, full_matrices=True); r = int(np.sum(ss > 1e-10)); return uu[:, r:]


def orth(cols):
    M = np.column_stack(cols); uu, ss, _ = np.linalg.svd(M, full_matrices=False); return uu[:, ss > 1e-8]


def initial_U(k, kind):
    cols = meta[k]["meta"]; m = mult[k]; lab = labels[k]; nl = int(kind[-1])
    Q = complement(Gold[k], m); PQ = Q @ Q.conj().T
    e = lambda j: np.eye(m, dtype=complex)[:, j]
    th = math.radians(args.theta)
    if lab == "(1,1)_|Y|=0":
        js = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar"][:1] + [j for j, c in enumerate(cols) if c["block"] == "S"][:1]
        return orth([PQ @ e(j) for j in js])
    if lab == "(1,2)_|Y|=1/2":
        hu = [j for j, c in enumerate(cols) if c["block"] == "H10" and c["X"] < 0][0]
        hd = [j for j, c in enumerate(cols) if c["block"] == "H10" and c["X"] > 0][0]
        su = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar" and c["X"] < 0][0]
        sd = [j for j, c in enumerate(cols) if c["block"] == "Sigma126bar" and c["X"] > 0][0]
        U = [math.cos(th) * e(hu) + math.sin(th) * e(su), math.cos(th) * e(hd) + math.sin(th) * e(sd)]
        if nl == 4: U += [-math.sin(th) * e(hu) + math.cos(th) * e(su), -math.sin(th) * e(hd) + math.cos(th) * e(sd)]
        return orth(U)[:, :nl]
    return Q[:, :nl]


sub_blocks = {kb[lab]: int(kind[-1]) for lab, kind in spec.items() if kind.startswith("sub")}
U_cur = {}
if args.fixU:
    Zu = np.load(K.SCRATCH / args.fixU if not args.fixU.startswith(("C:", "/")) else args.fixU)
    for k in sub_blocks: U_cur[k] = Zu[f"U{k}"]
else:
    Zuf = np.load(K.SCRATCH / args.Ufile) if args.Ufile else None
    for k, nl in sub_blocks.items():
        if Zuf is not None and f"U{k}" in Zuf.files and Zuf[f"U{k}"].shape[1] == nl: U_cur[k] = Zuf[f"U{k}"]
        else: U_cur[k] = initial_U(k, spec[labels[k]])
if args.no_outer_update: args.fixU = args.fixU or "__fixed__"

# unitarity matrices
UNIT = None
if args.unitarity is not None:
    ublocks = list(K.BLOCKS); nblk = {b: K.BLOCKS[b].stop - K.BLOCKS[b].start for b in ublocks}
    Mi = np.zeros((n_par, 5, 5))
    for i, pid in enumerate(ids):
        if degree_of(pid) != 4: continue
        for jb, Bn in enumerate(ublocks):
            for ia, An in enumerate(ublocks):
                val = TR["blocks"][Bn]["traces"][pid][An]
                Mi[i, ia, jb] = val if ia == jb else math.sqrt(nblk[Bn] / nblk[An]) * val
    Mi = 0.5 * (Mi + np.transpose(Mi, (0, 2, 1)))
    UNIT = np.einsum("ia,ijk->ajk", Nmat, Mi); UNIT_BOUND = 16 * math.pi * args.unitarity

# variables: y (ny), t, rho(stage B)
STAGE_B = args.stage.upper() == "B"
nz = ny + 1 + (1 if STAGE_B else 0); T_IDX = ny; R_IDX = ny + 1
by = np.einsum("ia,ij->aj", Nmat, b_up)   # ny x 486 : b(y) = y @ by
V4y = Nmat.T @ V4_up  # ny
# doublet subspace (lifted) for exclusion from light-cubic constraints
kd = kb["(1,2)_|Y|=1/2"]
# lifted light subspaces for sub-blocks: W_k U_k (complex) -> real span
def lift_real(k, U):
    M = Wk[k] @ U; return orth([np.real(M[:, j]) for j in range(M.shape[1])] + [np.imag(M[:, j]) for j in range(M.shape[1])])


def rayleigh_row(k, v):
    row = np.zeros(nz); row[:ny] = np.real(np.einsum("i,pij,j->p", np.conj(v), Ay[k], v)); return row


def lp_solve(obj, Aub, bub, bounds):
    for method, opts in (("highs", {"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10}),
                         ("highs-ipm", {"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9}),
                         ("highs-ds", {"primal_feasibility_tolerance": 1e-9, "dual_feasibility_tolerance": 1e-9}),
                         ("highs", {})):
        res = linprog(obj, A_ub=Aub, b_ub=bub, bounds=bounds, method=method, options=opts)
        if res.status == 0: return res
    return res


def full_hessian(c):
    H = np.einsum("p,pij->ij", c, HESS); return 0.5 * (H + H.T)


# ---------------- heavy projector and response R (stage B) -----------------
P_heavy = None; M_a = None; beta_a = None
def setup_response(c_ref):
    global P_heavy, M_a, beta_a
    H = full_hessian(c_ref); w, V = np.linalg.eigh(H)
    heavy = [j for j in range(len(w)) if w[j] >= 10 * eps_hi]
    P_heavy = V[:, heavy]
    tmp = np.tensordot(Nmat.T, HESS, axes=(1, 0))  # ny x 486 x 486 (BLAS)
    M_a = np.array([P_heavy.T @ tmp[a] @ P_heavy for a in range(ny)]); del tmp  # ny x nh x nh
    beta_a = by @ P_heavy  # ny x nh
    log(f"response setup: {len(heavy)} heavy modes; min heavy eigenvalue {w[heavy[0]]:.4g}")


def response(y):
    M = np.einsum("a,aij->ij", y, M_a); b = y @ beta_a
    Mi_b = np.linalg.solve(M, b); R = float(b @ Mi_b)
    grad = 2 * beta_a @ Mi_b - np.einsum("i,aij,j->a", Mi_b, M_a, Mi_b)
    return R, grad, float(np.linalg.eigvalsh(M)[0])


def lambda_eff_exact(c):
    """lambda_eff from the full Hessian at c: heavy = all non-Goldstone, non-doublet modes >= 10 eps_hi; light listed."""
    H = full_hessian(c); w, V = np.linalg.eigh(H); b = c @ b_up; V4 = float(c @ V4_up)
    gold = np.abs(w) < 1e-9; heavy = w >= 10 * eps_hi; light = (~gold) & (~heavy)
    bh = V[:, heavy].T @ b; bl = V[:, light].T @ b; bg = V[:, gold].T @ b
    Rh = float(np.sum(bh ** 2 / w[heavy])); Rl_terms = (bl ** 2 / w[light]); Rl = float(np.sum(Rl_terms))
    return {"lambda_direct": V4 / 6, "R_heavy": Rh, "lambda_eff_heavy": V4 / 6 - Rh / 2, "R_light": Rl,
            "lambda_eff_all": V4 / 6 - (Rh + Rl) / 2, "max_b_goldstone": float(np.max(np.abs(bg))) if bg.size else 0.0,
            "light_terms_sorted": sorted([(float(x), float(m)) for x, m in zip(Rl_terms, w[light])], reverse=True)[:6]}


# ---------------- main cutting-plane solve -----------------
def solve(Ucur, max_iter):
    global COMP_J, BFB_J, COMP_M
    fixed_A, fixed_b, fixed_cls = [], [], []
    def add_fixed(row, rhs, cls='other'): fixed_A.append(row); fixed_b.append(rhs); fixed_cls.append(cls)
    for i in range(n_par):
        row = np.zeros(nz); row[:ny] = Nmat[i]; add_fixed(row.copy(), boxes[i], 'box'); add_fixed(-row, boxes[i], 'box')
    for item in [x for x in args.abs_bound.split(",") if x]:
        pid_pref, val = item.rsplit(":", 1)
        for i, pid in enumerate(ids):
            if pid.startswith(pid_pref):
                row = np.zeros(nz); row[:ny] = Nmat[i]; add_fixed(row.copy(), float(val), 'absbound'); add_fixed(-row, float(val), 'absbound')
    for op in [x for x in args.nonneg.split(",") if x]:
        for i, pid in enumerate(ids):
            if pid.startswith("lambda::") and pid.split("::")[1].startswith(op):
                row = np.zeros(nz); row[:ny] = -Nmat[i]; add_fixed(row, 0.0, "nonneg")
    comps = {}
    for k in range(nb):
        m = mult[k]; kind = spec.get(labels[k], "heavy")
        if kind.startswith("sub"):
            # interlacing formulation: no invariance constraints; Qc compression >= t (heavy cuts below),
            # U compression <= eps_hi, full Goldstone-complement block >= eps_lo (cuts generated in the loop)
            U = Ucur[k]; Qc = complement(np.column_stack([U] + ([Gold[k]] if Gold[k].shape[1] else [])), m); comps[k] = (kind, Qc)
        elif kind == "sandwich": comps[k] = (kind, np.eye(m, dtype=complex))
        else: comps[k] = (kind, complement(Gold[k], m))
    # competitor cuts: (VAL0 - J_k) . N y + mu t <= 0
    for row_J, mf in zip(COMP_J, COMP_M):
        row = np.zeros(nz); row[:ny] = (VAL0 - row_J) @ Nmat; row[T_IDX] = args.mu * mf; add_fixed(row, 0.0, 'competitor')
    # BFB cuts: -J4 . N y <= -eps_bfb
    for row_J in BFB_J:
        row = np.zeros(nz); row[:ny] = -(row_J @ Nmat); add_fixed(row, -args.eps_bfb, 'bfb')
    if args.lam_direct_max is not None:
        row = np.zeros(nz); row[:ny] = V4y / 6; add_fixed(row, args.lam_direct_max, 'lamdir')
    if args.lam_direct_min is not None:
        row = np.zeros(nz); row[:ny] = -V4y / 6; add_fixed(row, -args.lam_direct_min, 'lamdir')
    cuts_A, cuts_b, cuts_cls = [], [], []
    rng2 = np.random.default_rng(1)
    for k in range(nb):
        kind, Q = comps[k]; m = mult[k]
        vecs = [Q[:, j] for j in range(Q.shape[1])]
        for _ in range(2):
            if Q.shape[1] == 0: break
            w = rng2.normal(size=Q.shape[1]) + 1j * rng2.normal(size=Q.shape[1]); vecs.append(Q @ (w / np.linalg.norm(w)))
        for v in vecs:
            row = rayleigh_row(k, v)
            if kind == "sandwich": cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi); cuts_cls += ['light', 'light']
            else: row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0); cuts_cls.append('heavy')
        if kind.startswith("sub"):
            U = Ucur[k]
            for l in range(U.shape[1]):
                row = rayleigh_row(k, U[:, l]); cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_A.append(row.copy()); cuts_b.append(eps_hi); cuts_cls += ['light', 'light']
    if UNIT is not None:
        for j in range(5):
            for sgn in (1.0, -1.0):
                row = np.zeros(nz); row[:ny] = sgn * UNIT[:, j, j]; cuts_A.append(row); cuts_b.append(UNIT_BOUND); cuts_cls.append('unitarity')
    obj = np.zeros(nz)
    if STAGE_B:
        if args.objective == "max_leff": obj[:ny] = -V4y / 6; obj[R_IDX] = 0.5
        elif args.objective == "min_R": obj[R_IDX] = 1.0
        elif args.objective == "max_t": obj[T_IDX] = -1.0
        else: raise SystemExit("objective")
        bounds = [(None, None)] * ny + [(args.tmin, None), (0.0, None)]
        # initial Kelley cuts: none (rho >= 0 only); added from iterates
    else:
        obj[T_IDX] = -1.0; bounds = [(None, None)] * ny + [(0.0, None)]
    # lifted doublet subspace for the light-cubic exclusion
    D_lift = lift_real(kd, Ucur[kd]) if kd in Ucur else np.zeros((K.TOTAL, 0))
    result = None; res = None; n_comp_added = 0; n_bfb_added = 0; n_lightb = 0; last_search = None; t_hist = []
    for it in range(max_iter):
        res = lp_solve(obj, np.array(fixed_A + cuts_A), np.array(fixed_b + cuts_b), bounds)
        if res.status != 0:
            log(f"  LP status {res.status}: {res.message}"); return result, res, last_search
        z = res.x; y = z[:ny]; t = z[T_IDX]; worst = 0.0; n_new = 0; c = Nmat @ y; n_comp_added_this = 0
        for k in range(nb):
            kind, Q = comps[k]; Ac = np.einsum("p,pij->ij", y, Ay[k]); m = mult[k]
            if kind == "sandwich":
                w, v = np.linalg.eigh(Ac)
                for j in range(m):
                    row = rayleigh_row(k, v[:, j])
                    if w[j] < eps_lo - 1e-13: cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_cls.append('light'); n_new += 1; worst = max(worst, eps_lo - w[j])
                    if w[j] > eps_hi + 1e-13: cuts_A.append(row.copy()); cuts_b.append(eps_hi); cuts_cls.append('light'); n_new += 1; worst = max(worst, w[j] - eps_hi)
            else:
                if Q.shape[1] > 0:
                    Ar = Q.conj().T @ Ac @ Q; w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T))
                    for j in range(Q.shape[1]):
                        if w[j] < t - 1e-13:
                            row = rayleigh_row(k, Q @ v[:, j]); row[T_IDX] = -1.0; cuts_A.append(-row); cuts_b.append(0.0); cuts_cls.append('heavy'); n_new += 1; worst = max(worst, t - w[j])
                if kind.startswith("sub"):
                    U = Ucur[k]; E = U.conj().T @ Ac @ U; w, v = np.linalg.eigh(0.5 * (E + E.conj().T))
                    for j in range(U.shape[1]):
                        if w[j] > eps_hi + 1e-13:
                            row = rayleigh_row(k, U @ v[:, j]); cuts_A.append(row.copy()); cuts_b.append(eps_hi); cuts_cls.append('light'); n_new += 1; worst = max(worst, w[j] - eps_hi)
                    Q0 = complement(Gold[k], m) if Gold[k].shape[1] else np.eye(m, dtype=complex)
                    A0 = Q0.conj().T @ Ac @ Q0; w0, v0 = np.linalg.eigh(0.5 * (A0 + A0.conj().T))
                    for j in range(Q0.shape[1]):
                        if w0[j] < eps_lo - 1e-13:
                            row = rayleigh_row(k, Q0 @ v0[:, j]); cuts_A.append(-row); cuts_b.append(-eps_lo); cuts_cls.append('light'); n_new += 1; worst = max(worst, eps_lo - w0[j])
        if UNIT is not None:
            Mc = np.einsum("p,pij->ij", y, UNIT); w, v = np.linalg.eigh(Mc)
            for j in range(5):
                if abs(w[j]) > UNIT_BOUND - 1e-12:
                    row = np.zeros(nz); row[:ny] = np.einsum("i,pij,j->p", v[:, j], UNIT, v[:, j]) * np.sign(w[j])
                    cuts_A.append(row); cuts_b.append(UNIT_BOUND); cuts_cls.append('unitarity'); n_new += 1; worst = max(worst, abs(w[j]) - UNIT_BOUND)
        # light-cubic constraints: light non-doublet eigen-directions of the full Hessian
        if not args.no_lightb:
            H = full_hessian(c); wf, Vf = np.linalg.eigh(H)
            light_idx = [j for j in range(len(wf)) if 1e-9 < wf[j] < 10 * eps_hi]
            bvec = c @ b_up
            for j in light_idx:
                v = Vf[:, j]
                if D_lift.shape[1] and np.linalg.norm(D_lift.T @ v) > 0.5: continue
                val = float(v @ bvec)
                if abs(val) > args.delta_b:
                    row = np.zeros(nz); row[:ny] = np.sign(val) * (by @ v); cuts_A.append(row); cuts_b.append(args.delta_b); cuts_cls.append('lightb'); n_new += 1; n_lightb += 1
                    worst = max(worst, abs(val) - args.delta_b)
        # Kelley cut on the response (stage B)
        if STAGE_B:
            R, gR, mmin = response(y); rho = z[R_IDX]
            if R > rho + 1e-9:
                row = np.zeros(nz); row[:ny] = gR; row[R_IDX] = -1.0; rhs = float(gR @ y - R); sc = max(1.0, float(np.max(np.abs(row))))
                cuts_A.append(row / sc); cuts_b.append(rhs / sc); cuts_cls.append('kelley'); n_new += 1; worst = max(worst, R - rho)
        # competitor search every search_every iterations and at convergence
        if fits and (it % args.search_every == args.search_every - 1 or n_new == 0):
            lowest_total = None
            for f in fits:
                found, coef, resid = f.search(c)
                Vst = f.V(coef, zstar)
                for Vm, zm in found:
                    if in_g3221_orbit(zm): continue
                    if np.max(np.abs(zm)) > 30:  # runaway: BFB violation along this subspace ray
                        qd = chart.pack(state_of_z(zm / np.linalg.norm(zm))); Jq = J_at_state(chart.unpack(qd))
                        BFB_J_row = Jq * deg4 / float(np.linalg.norm(qd)) ** 4; BFB_J = np.vstack([BFB_J, BFB_J_row[None, :]])
                        row = np.zeros(nz); row[:ny] = -(BFB_J_row @ Nmat); fixed_A.append(row); fixed_b.append(-args.eps_bfb); fixed_cls.append('bfb'); n_new += 1; n_bfb_added += 1
                        log(f"  [{f.mode}] runaway at |z| = {np.max(np.abs(zm)):.1f}: BFB cut added"); continue
                    qm = chart.pack(state_of_z(zm)); mf = margin_factor(qm)
                    if Vm < Vst - 1e-10 * max(1.0, abs(Vst)):   # strictly lower only; near-degenerate higher points are reported, not cut
                        Jq = J_at_state(state_of_z(zm)); COMP_J = np.vstack([COMP_J, Jq[None, :]]); COMP_M = np.append(COMP_M, mf)
                        row = np.zeros(nz); row[:ny] = (VAL0 - Jq) @ Nmat; row[T_IDX] = args.mu * mf; fixed_A.append(row); fixed_b.append(0.0); fixed_cls.append('competitor')
                        n_new += 1; n_comp_added += 1; n_comp_added_this += 1; worst = max(worst, Vst - Vm)
                        if lowest_total is None or Vm - Vst < lowest_total[0]: lowest_total = (Vm - Vst, zm.tolist(), f.mode + f" d={np.linalg.norm(qm - q0):.3f} mf={mf:.2e}")
                        break  # one new point per fit per round
                last_search = {"mode": f.mode, "V_star": Vst, "V_min": found[0][0], "argmin": found[0][1].tolist(), "fit_residual": resid}
            if lowest_total is not None: log(f"  it {it}: competitor lower by {-lowest_total[0]:.4g} at z = {np.round(lowest_total[1], 4)} [{lowest_total[2]}]")
            elif last_search is not None and it % 50 == 49: log(f"  it {it}: subspace min - V* = {last_search['V_min'] - last_search['V_star']:.3e} [{last_search['mode']}]")
        if it % 10 == 0 or n_new == 0:
            extra = f", rho = {z[R_IDX]:.4g}, R = {R:.4g}, lam_eff = {float(c @ V4_up)/6 - R/2:.5g}" if STAGE_B else ""
            log(f"  it {it:3d}: t = {t:.6g}, cuts = {len(cuts_A)}, new = {n_new}, worst = {worst:.3e}, comp+ {n_comp_added}, bfb+ {n_bfb_added}, lightb {n_lightb}{extra}")
        result = (z, t)
        if it % 10 == 0:
            np.savez(K.SCRATCH / f"{out}_iter.npz", c=c, t=t, z=z, ids=np.array(ids), it=it, **{f"U{k}": Ucur[k] for k in sub_blocks})
        tol_stop = 1e-6 if STAGE_B else 1e-8
        if n_new == 0 or (worst < tol_stop and it > 5 and n_comp_added_this == 0): break
        t_hist.append(t)
        if len(t_hist) > args.stall and abs(t_hist[-1] - t_hist[-1 - args.stall]) <= 1e-7 * max(abs(t), 1e-12) and not STAGE_B:
            log(f'  stalled at it {it}: t = {t:.6g} unchanged for {args.stall} iterations, worst = {worst:.3e} (upper bound; point checked below)'); break
    Aall = np.array(fixed_A + cuts_A); ball = np.array(fixed_b + cuts_b); clsall = fixed_cls + cuts_cls
    slack = ball - Aall @ z; active = {}
    for cl, sl_ in zip(clsall, slack):
        if abs(sl_) < 1e-9: active[cl] = active.get(cl, 0) + 1
    log(f"  active constraints at optimum: {active} (of {len(clsall)})")
    return result, res, last_search


log(f"stage {args.stage} spec={spec} eps=[{eps_lo},{eps_hi}] boxes=({args.box_quartic},{args.box_cubic},{args.box_mass}) theta0={args.theta} "
    f"unitarity={args.unitarity} mu={args.mu} eps_bfb={args.eps_bfb} delta_b={args.delta_b} tmin={args.tmin} objective={args.objective}")
if STAGE_B:
    cref = np.load(K.SCRATCH / args.fixU if not args.fixU.startswith(("C:", "/")) else args.fixU)["c"]; setup_response(cref)
final = None; last_search = None; t_prev = 0.0
for outer in range(args.outer if (sub_blocks and not args.fixU) else 1):
    t0 = time.time()
    result, res, last_search = solve(U_cur, args.iters if not STAGE_B else args.kelley_iters)
    if result is None: log("INFEASIBLE or failed"); break
    z, t = result; y = z[:ny]; c = Nmat @ y
    log(f"outer {outer}: solved in {time.time()-t0:.1f}s: t = {t:.6g} (LP status {res.status})")
    final = (z, t, c)
    changed = 0.0
    if not args.fixU:
        for k, nl in sub_blocks.items():
            Ac = np.einsum("p,pij->ij", y, Ay[k]); m = mult[k]
            Q = complement(Gold[k], m) if Gold[k].shape[1] else np.eye(m, dtype=complex)
            Ar = Q.conj().T @ Ac @ Q; w, v = np.linalg.eigh(0.5 * (Ar + Ar.conj().T)); Unew = Q @ v[:, :nl]
            ov = np.linalg.svd(U_cur[k].conj().T @ Unew, compute_uv=False); chg = float(1 - np.min(ov) ** 2); changed = max(changed, chg)
            log(f"  {labels[k]}: eigenvalues (Goldstone complement) {np.array2string(w, precision=3)}; subspace change {chg:.3e}")
            U_cur[k] = Unew
    if args.save_every_outer:
        np.savez(K.SCRATCH / f"{out}_outer.npz", c=c, t=t, z=z, ids=np.array(ids), outer=outer, **{f"U{k}": U_cur[k] for k in sub_blocks})
    gain = (t - t_prev) / max(t, 1e-300) if outer > 0 else 1.0
    t_prev = t
    if changed < 1e-10 or (outer >= 1 and gain < 1e-4): break

if final is not None:
    z, t, c = final
    H = full_hessian(c); wfull = np.linalg.eigvalsh(H)
    n_zero = int(np.sum(np.abs(wfull) < 1e-9)); n_neg = int(np.sum(wfull < -1e-9))
    n_light = int(np.sum((wfull >= 1e-9) & (wfull < 10 * eps_hi))); n_heavy = int(np.sum(wfull >= 10 * eps_hi))
    lam = lambda_eff_exact(c)
    # final exact subspace screen
    screen = []
    for f in fits:
        found, coef, resid = f.search(c, n_polish=25); Vst = f.V(coef, zstar)
        others = [(Vm, zm.tolist()) for Vm, zm in found if not in_g3221_orbit(zm)]
        screen.append({"mode": f.mode, "fit_residual": resid, "V_star": Vst, "V_min_all": found[0][0], "argmin_all": found[0][1].tolist(),
                       "lowest_non_orbit": others[:3], "n_lower_non_orbit": int(sum(1 for Vm, _ in others if Vm < Vst - 1e-9 * max(1, abs(Vst))))})
    bfb_min = float(np.min(BFB_J @ c)) if BFB_J.shape[0] else None
    comp_min_gap = float(np.min(COMP_J @ c - VAL0 @ c)) if COMP_J.shape[0] else None
    a0 = None
    if UNIT is not None:
        Mc = np.einsum("p,pij->ij", c, Mi); a0 = (np.linalg.eigvalsh(Mc) / (16 * math.pi)).tolist()
    report = {"tag": args.tag, "out": out, "stage": args.stage, "args": vars(args), "spec": spec, "t": float(t),
              "c": {ids[i]: float(c[i]) for i in range(n_par)}, "grad_residual": float(np.max(np.abs(Z["grads"].T @ c))),
              "full_hessian": {"n_zero(<1e-9)": n_zero, "n_negative(<-1e-9)": n_neg, "n_light(<10 eps_hi)": n_light, "n_heavy": n_heavy,
                               "min_eigenvalue": float(wfull[0]), "lowest_60": wfull[:60].tolist(), "min_heavy": float(np.min(wfull[wfull >= 10 * eps_hi])) if n_heavy else None},
              "lambda": lam, "subspace_screen": screen, "bfb_bank_min_V4": bfb_min, "competitor_bank_min_gap": comp_min_gap,
              "singlet_channel_a0": a0, "V_star": float(VAL0 @ c), "seconds": time.time() - t_start, "blocks": []}
    for k in range(nb):
        Ac = np.einsum("p,pij->ij", c, A[k]); w, v = np.linalg.eigh(Ac)
        report["blocks"].append({"label": labels[k], "m": int(mult[k]), "kind": spec.get(labels[k], "heavy"), "eigenvalues": w.tolist(),
                                 "eigenvectors": [[{"block": meta[k]["meta"][i]["block"], "T3R": meta[k]["meta"][i]["T3R"], "X": meta[k]["meta"][i]["X"], "w2": float(abs(v[i, j]) ** 2)} for i in range(mult[k])] for j in range(mult[k])]})
        log(f"{labels[k]:22s} {spec.get(labels[k], 'heavy'):9s} eig = {np.array2string(w, precision=4, max_line_width=250)}")
    np.savez(K.SCRATCH / f"{out}.npz", c=c, t=t, z=z, ids=np.array(ids), **{f"U{k}": U_cur[k] for k in sub_blocks})
    json.dump(report, open(K.SCRATCH / f"{out}.json", "w", encoding="utf-8"), indent=1, default=float)
    log(f"lambda: {json.dumps({k: v for k, v in lam.items() if k != 'light_terms_sorted'})}")
    log(f"light terms (3b^2/m^2 -> b^2/m^2, m^2): {lam['light_terms_sorted'][:4]}")
    log(f"screen: {json.dumps(screen, default=float)[:1500]}")
    log(f"saved {out}: t = {t:.6g}; |grad| = {report['grad_residual']:.3e}; full Hessian: zero {n_zero}, neg {n_neg}, light {n_light}, heavy {n_heavy}, min {wfull[0]:.3e}; "
        f"BFB bank min V4 = {bfb_min}; competitor min gap = {comp_min_gap}; a0 = {None if a0 is None else np.round(a0, 3).tolist()}; {time.time()-t_start:.0f}s")
else:
    log("no solution")
