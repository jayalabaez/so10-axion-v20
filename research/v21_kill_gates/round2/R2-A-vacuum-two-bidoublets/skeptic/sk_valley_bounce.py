"""SKEPTIC (R2-A): (1) explicit near-vacuum lower points along the light Higgs valley when the tree lambda_eff < 0;
(2) straight-path O(4) bounce action (an UPPER bound on the true action) from q* to the deepest R1 descent minimum.

(1) q(h) = q* + h u + (h^2/2) phi2,  phi2 = -P (P^T H P)^-1 P^T b  (P = heavy eigenvectors, H = Hessian, b = d^3V/du du dq),
    evaluated with fresh exact operator values (potential.evaluate_directions path).  Prediction:
    V - V* = m_u^2 h^2 / 2 + (lambda_eff_heavy / 4) h^4 + O(h^5).
(2) V along q* + tau (q_min - q*), tau in [0, 1.2]; 1D O(4) bounce by overshoot/undershoot on a cubic-spline potential.
    Canonical real chart fields are assumed (chart = kinetic-normalised; EST).  Units: |Phi| = M_U.
"""
from __future__ import annotations
import sys, json, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; PARENT = HERE.parent
sys.path.insert(0, str(PARENT))
import k3_common as K  # noqa: E402

chart = K.chart; potential = K.potential
OUT = {}


def J_at(q, ids):
    st = chart.unpack(np.asarray(q, float)).validated()
    jac = potential.coefficient_jacobian(potential.evaluate_directions(st))
    return np.array([float(np.real(jac[p])) for p in ids])


def valley(label, solf, tag, cubf, hs):
    sol = np.load(PARENT / solf); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
    Z = np.load(PARENT / f"{tag}_rows.npz"); q0 = Z["q"]; H = np.einsum("p,pij->ij", c, Z["hess"]); H = 0.5 * (H + H.T)
    C = np.load(PARENT / cubf); assert [str(x) for x in C["ids"]] == ids
    u = C["u_up"] / np.linalg.norm(C["u_up"]); b = c @ C["b_up"]; V4 = float(c @ C["V4_up"])
    w, V = np.linalg.eigh(H); heavy = w >= 3e-5; P = V[:, heavy]
    phi2 = -P @ ((P.T @ b) / w[heavy]); R_h = float(b @ P @ ((P.T @ b) / w[heavy]))
    lam_h = V4 / 6 - R_h / 2; mu2 = float(u @ H @ u)
    Vs = float(c @ J_at(q0, ids)); rows = []
    for h in hs:
        qa = q0 + h * u + 0.5 * h * h * phi2; qb = q0 + h * u
        dVa = float(c @ J_at(qa, ids)) - Vs; dVb = float(c @ J_at(qb, ids)) - Vs
        pred = 0.5 * mu2 * h * h + lam_h / 4 * h ** 4
        rows.append({"h": h, "dV_relaxed": dVa, "dV_ray": dVb, "pred_quartic_EFT": pred})
        print(label, rows[-1], flush=True)
    OUT[label] = {"solution": solf, "tag": tag, "cubic": cubf, "u_mass2": mu2, "lambda_direct": V4 / 6, "R_heavy": R_h,
                  "lambda_eff_heavy": lam_h, "V_star": Vs, "points": rows}
    json.dump(OUT, open(HERE / "sk_valley_bounce.json", "w"), indent=1, default=float)


def bounce_1d(phi, Vphi):
    """O(4) bounce for V(phi) (false vacuum at phi=0, V(0)=0) by shooting; returns (S, phi0)."""
    from scipy.interpolate import CubicSpline
    from scipy.integrate import solve_ivp
    cs = CubicSpline(phi, Vphi); dV = cs.derivative()
    lower = np.where(Vphi < 0)[0]
    if len(lower) == 0: return None, None
    lo, hi = phi[lower[0]], phi[-1]       # release point between first V<0 point and the end of the sampled path

    def shoot(p0):
        def rhs(r, y): return [y[1], dV(y[0]) - 3.0 / max(r, 1e-12) * y[1]]
        r0 = 1e-6
        def over(r, y): return y[0]        # crosses the false vacuum: overshoot
        over.terminal = True; over.direction = -1
        def under(r, y): return y[1]       # turns back: undershoot
        under.terminal = True; under.direction = 1
        sol = solve_ivp(rhs, [r0, 1e4], [p0, 0.0], events=[over, under], rtol=1e-10, atol=1e-12, max_step=0.5, dense_output=True)
        if sol.t_events[0].size: return +1, sol
        return -1, sol
    a, bnd = lo, hi
    if shoot(bnd)[0] < 0: return None, None
    for _ in range(80):
        mid = 0.5 * (a + bnd); s, _ = shoot(mid)
        if s > 0: bnd = mid
        else: a = mid
    s, sol = shoot(bnd)
    r = np.linspace(sol.t[0], sol.t[-1], 20000); y = sol.sol(r)
    dens = 0.5 * y[1] ** 2 + cs(y[0])
    S = 2 * np.pi ** 2 * np.trapezoid(r ** 3 * dens, r)
    return float(S), float(bnd)


def segment(label, solf, tag, descent, taus):
    sol = np.load(PARENT / solf); c = sol["c"]; ids = [str(x) for x in sol["ids"]]
    q0 = np.load(PARENT / f"{tag}_rows.npz")["q"]; qm = np.load(PARENT / f"{descent}.npz")["qmin"]
    L = float(np.linalg.norm(qm - q0)); Vs = float(c @ J_at(q0, ids)); vals = []
    for tau in taus:
        vals.append(float(c @ J_at(q0 + tau * (qm - q0), ids)) - Vs)
        print(label, round(float(tau), 4), vals[-1], flush=True)
    phi = np.array(taus) * L; Vp = np.array(vals)
    S, p0 = bounce_1d(phi, Vp)
    OUT[label] = {"solution": solf, "tag": tag, "descent": descent, "field_distance": L, "tau": list(map(float, taus)), "dV": vals,
                  "barrier_max": float(np.max(Vp)), "tau_at_barrier": float(taus[int(np.argmax(Vp))]),
                  "S_straight_path_upper_bound": S, "release_phi": p0}
    print(label, "S_path =", S, "barrier", float(np.max(Vp)), flush=True)
    json.dump(OUT, open(HERE / "sk_valley_bounce.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    t0 = time.time()
    hs = [0.005, 0.01, 0.02, 0.04, 0.08]
    valley("R1_G7_D470_EW", "G7_D470_C1622_K2.npz", "D470", "cubic_ew_D470_K2.npz", hs)
    valley("R3_G14_Am45_K2dir", "G14_Am45_C2_K2f09_R12.npz", "Am45", "cubic_ew_Am45_K2.npz", hs)
    taus = list(np.concatenate([np.linspace(0, 0.3, 16), np.linspace(0.32, 1.2, 23)]))
    segment("R1_bankA_segment", "G7_D470_C1622_K2.npz", "D470", "descend_R1_bankA", taus)
    print("done", time.time() - t0)
