from pathlib import Path
p = Path("sk_phase1.py"); s = p.read_text(encoding="utf-8")
# 1. screen machinery before solve_fixedU
anchor = 'def solve_fixedU(U, objective="phase1", max_iter=600):'
screen_code = '''# ---------------- dynamic SM-singlet / Delta_R subspace screen (as the gate's LP does on every round) -------------
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
        SCREEN.append({"mode": _mode, "J": _J, "Pinv": np.linalg.pinv(_X(_Z)), "X": _X, "zs": _zs, "Xs": _X(_zs)})
    log(f"dynamic subspace screen on ({[sc['mode'] for sc in SCREEN]})")


def q_of_z(z):
    return sum(zi * d for zi, d in zip(z, SUB))


def run_screen(c, max_new=4):
    """returns lists of new competitor J rows (with margin factors) and new BFB rows found on the two subspaces."""
    newc, newb, info = [], [], []
    for sc in SCREEN:
        coef = sc["Pinv"] @ (sc["J"] @ c); Vz = lambda z: float(sc["X"](np.asarray(z)[None, :])[0] @ coef)
        Vst = Vz(zstar); order = np.argsort(sc["Xs"] @ coef)[:12]; found = []
        for j in list(order) + [None]:
            r = _minimize(Vz, zstar if j is None else sc["zs"][j], method="BFGS", options={"gtol": 1e-9, "maxiter": 400})
            zz = np.array(r.x)
            if sc["mode"] == "smsinglet": zz[4] = 0
            found.append((float(r.fun), zz))
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


'''
assert s.count(anchor) == 1; s = s.replace(anchor, screen_code + anchor)
# 2. CLI flag
s = s.replace('ap.add_argument("--unit", type=float, default=0.5)', 'ap.add_argument("--unit", type=float, default=0.5)\nap.add_argument("--screen", action="store_true")')
# 3. use screen at convergence
old = "        if n_new == 0 or (worst < args.stop_tol and it > 5): break\n"
new = """        if n_new == 0 or (worst < args.stop_tol and it > 5):
            if not SCREEN: break
            newc, newb, info = run_screen(N @ y)
            if not newc and not newb: break
            global COMP_J, MF, BFB
            for jq, mf in newc:
                r = np.zeros(nz); r[:ny] = (VAL0 - jq) @ N; r[IT] = args.mu * mf; r[IS] = -1.0
                sc_ = max(1.0, float(np.max(np.abs(r[:ny])))); Aub.append(r / sc_); bub.append(0.0)
                COMP_J = np.vstack([COMP_J, jq[None, :]]); MF = np.append(MF, mf)
            for jb in newb:
                r = np.zeros(nz); r[:ny] = -(jb @ N); Aub.append(r); bub.append(-args.eps_bfb); BFB = np.vstack([BFB, jb[None, :]])
            log(f"    screen at cut-iteration {it}: added {len(newc)} competitor / {len(newb)} BFB rows {info}")
"""
assert s.count(old) == 1; s = s.replace(old, new)
p.write_text(s, encoding="utf-8"); print("ok")
