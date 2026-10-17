"""Full-486-chart descent of V_c from a given start (global-minimum screening, NUMERICAL).

Trust-region Newton: per step one exact rows call (value, gradient, Hessian of all 51 directions, ~75 s) and a
cheap line search with the value-only evaluator (~0.4-2 s).  Stops at |grad| < gtol or max_steps.
usage: python -B k3_descend.py <solution npz> <start> <out tag> [max_steps]
 start: random:<seed>:<scale> | witness | zstar | z:p,a,om,r1,r2,s,x | npz:<file>
"""
from __future__ import annotations
import sys, json, time, numpy as np
import k3_common as K

solpath, start, tag = sys.argv[1], sys.argv[2], sys.argv[3]
max_steps = int(sys.argv[4]) if len(sys.argv) > 4 else 25
sol = np.load(K.SCRATCH / solpath); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
chart = K.chart
Z = np.load(K.SCRATCH / "Am45_rows.npz"); qstar = Z["q"]; Vstar = float(c @ Z["values"])
basis = K.direct.singlet_basis(); sig_std = K.candidate.sigma_std_unit_coordinates()
drc = chart.sigma_coordinates(K.direct.delta_r()); drc /= np.linalg.norm(drc)


def state_of_z(z):
    phi = K.phi_form(z[0], z[1], z[2]); sigma = chart.sigma_from_coordinates(z[3] * sig_std + z[4] * drc)
    return K.potential.FieldState(phi=phi, h=np.zeros(10, complex), sigma=sigma, s=complex(z[5]), x=complex(z[6])).validated()


BANK_Q, BANK_V, BANK_IDS = [], [], None
def value_at(q):
    global BANK_IDS
    dirs = K.potential.evaluate_directions(chart.unpack(q)); jac = K.potential.coefficient_jacobian(dirs)
    if BANK_IDS is None: BANK_IDS = [d.direction_id for d in dirs]
    BANK_Q.append(np.array(q)); BANK_V.append([d.value for d in dirs])
    np.savez_compressed(K.SCRATCH / f"descend_{tag}_bank.npz", Q=np.array(BANK_Q), values=np.array(BANK_V), ids=np.array(BANK_IDS))
    return float(sum(c[i] * jac[pid] for i, pid in enumerate(ids)))


def rows_at(q):
    rows = K.parameter_rows(chart.unpack(q))
    V = float(sum(c[i] * rows[pid].value for i, pid in enumerate(ids)))
    g = sum(c[i] * np.asarray(rows[pid].gradient, float) for i, pid in enumerate(ids))
    H = sum(c[i] * np.asarray(rows[pid].hessian, float) for i, pid in enumerate(ids)); H = 0.5 * (H + H.T)
    return V, g, H


if start.startswith("random"):
    _, seed, scale = start.split(":"); rng = np.random.default_rng(int(seed)); scale = float(scale)
    q = np.zeros(chart.TOTAL_DIM)
    for name, sl in K.BLOCKS.items():
        n = sl.stop - sl.start; v = rng.normal(size=n); v /= np.linalg.norm(v)
        q[sl] = v * {"Phi210": 1.0, "H10": 0.6, "Sigma126bar": 0.6, "S": 1.0, "Phi17": float(np.linalg.norm(qstar[chart.X_SLICE]))}[name] * scale
    q = chart.pack(chart.unpack(q).validated())
elif start == "witness":
    q = chart.pack(K.candidate.candidate_state(K.candidate.R0, K.candidate.X0))
elif start == "zstar":
    q = qstar.copy()
elif start.startswith("z:"):
    z = [float(v) for v in start[2:].split(",")]; q = chart.pack(state_of_z(z))
elif start.startswith("npz:"):
    q = np.load(start[4:])["q"]
else:
    raise SystemExit("start")

log = open(K.SCRATCH / f"descend_{tag}.log", "w", encoding="utf-8")
def say(m): print(m, flush=True); log.write(m + "\n"); log.flush()
say(f"start {start}: |q| blocks {[round(float(np.linalg.norm(q[sl])), 4) for sl in K.BLOCKS.values()]}; V* (G3221 point) = {Vstar:.9f}")
t0 = time.time(); Delta = 0.5; hist = []
V0 = value_at(q); say(f"V(start) = {V0:.9f}  ({time.time()-t0:.0f}s)")
for step in range(max_steps):
    V, g, H = rows_at(q); gn = float(np.linalg.norm(g)); w, U = np.linalg.eigh(H)
    hist.append({"step": step, "V": V, "grad": gn, "min_eig": float(w[0]), "n_neg": int(np.sum(w < -1e-9)), "n_zero": int(np.sum(np.abs(w) < 1e-9))})
    say(f"step {step:2d}: V = {V:.9f}  |g| = {gn:.3e}  eig[min] = {w[0]:.3e}  neg = {hist[-1]['n_neg']}  zero = {hist[-1]['n_zero']}  ({time.time()-t0:.0f}s)")
    if gn < 1e-9: break
    gU = U.T @ g
    # trust-region step via eigen-decomposition: d = -sum gU_j/(w_j + sigma) U_j, sigma >= max(0, -w_min) + small, |d| <= Delta
    sigma = max(0.0, -w[0]) + 1e-6
    def step_of(sig):
        return -(U @ (gU / (w + sig)))
    d = step_of(sigma)
    if np.linalg.norm(d) > Delta:
        lo, hi = sigma, sigma + 1e3
        for _ in range(80):
            mid = 0.5 * (lo + hi); dm = step_of(mid)
            if np.linalg.norm(dm) > Delta: lo = mid
            else: hi = mid
        d = step_of(hi)
    # line search on the exact value (cheap evaluator)
    best = (V, 0.0)
    for alpha in (1.0, 0.5, 0.25, 0.1, 2.0):
        Vn = value_at(q + alpha * d)
        if Vn < best[0]: best = (Vn, alpha)
    if best[1] == 0.0:
        Delta *= 0.25; say(f"   no decrease (|d| = {np.linalg.norm(d):.3e}); shrink Delta -> {Delta:.3e}")
        if Delta < 1e-10: break
        continue
    q = q + best[1] * d; Delta = min(2.0, Delta * (1.5 if best[1] >= 1.0 else 1.0))
    q = chart.pack(chart.unpack(q).validated())
    say(f"   accepted alpha = {best[1]} |d| = {np.linalg.norm(d):.3e}  V -> {best[0]:.9f}")
V, g, H = rows_at(q); w = np.linalg.eigvalsh(H)
final = {"start": start, "V_final": V, "V_star": Vstar, "lower_than_star": bool(V < Vstar - 1e-9 * max(1, abs(Vstar))), "grad": float(np.linalg.norm(g)),
         "min_eig": float(w[0]), "n_neg": int(np.sum(w < -1e-9)), "n_zero": int(np.sum(np.abs(w) < 1e-9)),
         "block_norms": {name: float(np.linalg.norm(q[sl])) for name, sl in K.BLOCKS.items()},
         "singlet_coords": {"p": float(q @ chart.pack(K.potential.FieldState(phi=basis["p"], h=np.zeros(10, complex), sigma={}, s=0j, x=0j))),
                            "a": float(q @ chart.pack(K.potential.FieldState(phi=basis["a"], h=np.zeros(10, complex), sigma={}, s=0j, x=0j))),
                            "omega": float(q @ chart.pack(K.potential.FieldState(phi=basis["omega"], h=np.zeros(10, complex), sigma={}, s=0j, x=0j)))},
         "history": hist, "seconds": time.time() - t0}
say(json.dumps({k: v for k, v in final.items() if k != "history"}, default=float))
json.dump(final, open(K.SCRATCH / f"descend_{tag}.json", "w"), indent=1, default=float); np.savez(K.SCRATCH / f"descend_{tag}.npz", q=q)
