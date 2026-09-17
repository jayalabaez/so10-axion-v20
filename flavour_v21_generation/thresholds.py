"""Right-handed-neutrino threshold effects in the light-neutrino running.

The baseline (so10fit.py) applies the tree-level seesaw at M_I and runs only
the Weinberg operator down to M_Z. With M_R eigenvalues far below M_I, the
neutrino Yukawa is dynamical between M_I and each M_n and must be run, with
the heavy states integrated out one by one at their masses.

Type-II 2HDM (Phi_1 -> d, e ; Phi_2 -> u, nu), one loop, following the
structure of Antusch, Kersten, Lindner, Ratz, Schmidt (hep-ph/0501272).
Conventions: Y (N x lepton), Y_e (e_R x lepton); lepton-doublet index is the
second index of Y and Y_e and both indices of K and m_nu.

  16pi^2 dY/dt   = Y [ 3/2 Y^+Y + 1/2 Y_e^+Y_e ] + (T2 - 9/20 g1^2 - 9/4 g2^2) Y
  16pi^2 dY_e/dt = Y_e [ 3/2 Y_e^+Y_e + 1/2 Y^+Y ] + (T1 - 9/4 g1^2 - 9/4 g2^2) Y_e
  16pi^2 dM/dt   = (Y Y^+) M + M (Y Y^+)^T
  16pi^2 dK/dt   = 1/2 [(Y_e^+Y_e)^T K + K Y_e^+Y_e] + 1/2 [(Y^+Y)^T K + K Y^+Y]
                   + (2 T2 - 3 g2^2 + lam2) K
  T2 = 3 tr Y_u^+Y_u + tr Y^+Y ,  T1 = 3 tr Y_d^+Y_d + tr Y_e^+Y_e

Light mass (mass units, tree vevs):  m_nu = K - v_u^2 Y^T M^-1 Y.
Matching at M_n (lightest active state, M diagonal):  K <- K - v_u^2 y_n^T y_n / M_n.
"""
from __future__ import annotations

import math
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import so10fit as S  # noqa: E402

K16 = 16.0 * math.pi ** 2
MZ = 91.1876


def _c(v):
    return v[0::2] + 1j * v[1::2]


def _r(z):
    z = np.asarray(z).ravel()
    out = np.empty(2 * z.size)
    out[0::2], out[1::2] = z.real, z.imag
    return out


def _pack(g, yu, yd, ye, y, m, k):
    return np.concatenate([g, yu, yd, _r(ye), _r(y), _r(m), _r(k)])


def _unpack(s, n):
    g, yu, yd = s[0:3], s[3:6], s[6:9]
    o = 9
    ye = _c(s[o:o + 18]).reshape(3, 3); o += 18
    y = _c(s[o:o + 6 * n]).reshape(n, 3); o += 6 * n
    m = _c(s[o:o + 2 * n * n]).reshape(n, n); o += 2 * n * n
    k = _c(s[o:o + 18]).reshape(3, 3)
    return g, yu, yd, ye, y, m, k


def _rhs(_t, s, n, lam2, nu_yukawa, match_alpha=False):
    g, yu, yd, ye, y, m, k = _unpack(s, n)
    g1, g2, g3 = g
    hehe = ye.conj().T @ ye
    ydy = y.conj().T @ y if (n and nu_yukawa) else np.zeros((3, 3), complex)
    yyd = y @ y.conj().T if n else np.zeros((0, 0), complex)
    t2 = 3 * np.sum(yu ** 2) + np.trace(ydy).real
    t1 = 3 * np.sum(yd ** 2) + np.trace(hehe).real
    qcd2 = -108.0 * g3 ** 4 / K16
    gu = 8 * g3 ** 2 + 2.25 * g2 ** 2 + 0.85 * g1 ** 2
    gd = 8 * g3 ** 2 + 2.25 * g2 ** 2 + 0.25 * g1 ** 2
    dyu = yu * (1.5 * yu ** 2 + 0.5 * yd ** 2 + t2 - gu + qcd2) / K16
    dyd = yd * (1.5 * yd ** 2 + 0.5 * yu ** 2 + t1 - gd + qcd2) / K16
    dye = (ye @ (1.5 * hehe + 0.5 * ydy) + (t1 - 2.25 * g1 ** 2 - 2.25 * g2 ** 2) * ye) / K16
    if n:
        self_y = 1.5 * (y.conj().T @ y) if nu_yukawa else np.zeros((3, 3), complex)
        universal = (0.5 * (2 * t2 - 3 * g2 ** 2 + lam2)) if match_alpha else (t2 - 0.45 * g1 ** 2 - 2.25 * g2 ** 2)
        dy = (y @ (self_y + 0.5 * hehe) + universal * y) / K16
        dm = ((yyd @ m + m @ yyd.T) / K16) if nu_yukawa else np.zeros_like(m)
    else:
        dy = np.zeros((0, 3), complex)
        dm = np.zeros((0, 0), complex)
    alpha = 2 * t2 - 3 * g2 ** 2 + lam2
    dk = (0.5 * (hehe.T @ k + k @ hehe) + 0.5 * (ydy.T @ k + k @ ydy) + alpha * k) / K16
    dg = np.array([4.2 * g1 ** 3, -3.0 * g2 ** 3, -7.0 * g3 ** 3 - 26.0 * g3 ** 5 / K16]) / K16
    return _pack(dg, dyu, dyd, dye, dy, dm, dk)


def _integrate_out(y, m, k, vu, mu_now, *, all_states=False):
    """Diagonalise M, move every state with mass >= mu_now (or all) into K."""
    n = m.shape[0]
    if n == 0:
        return y, m, k
    d, w = S.R.takagi(0.5 * (m + m.T))
    y = w.conj().T @ y
    keep = []
    for i in range(n):
        if all_states or d[i] >= mu_now * (1 - 1e-9):
            k = k - vu ** 2 * np.outer(y[i], y[i]) / d[i]
        else:
            keep.append(i)
    y = y[keep]
    m = np.diag(d[keep]).astype(complex)
    return y, m, k


def run_down(st, p, *, lam2=0.5, nu_yukawa=True, collapse_at_mi=False, rtol=1e-8, match_alpha=False,
             time_budget=None):
    """Run the lepton sector from M_I to M_Z with right-handed-neutrino thresholds."""
    b = st.build(p)
    vu, vd = st.vu, st.vd
    su, _ = S._takagi(b["mu"])
    gauge = st.run["gauge"]
    g = np.array([gauge["g1"], gauge["g2"], gauge["g3"]])
    yu = np.asarray(su) / vu
    yd = np.real(np.diag(b["md"])) / vd
    ye = b["me"] / vd
    y = b["mD"].T / vu
    m = b["mR"].astype(complex)
    k = (b["eps"] * b["F"]).astype(complex)
    t, t_end = math.log(st.v_r), math.log(MZ)
    thresholds = []
    y, m, k = _integrate_out(y, m, k, vu, math.exp(t), all_states=collapse_at_mi)
    for _ in range(8):
        n = m.shape[0]
        state = _pack(g, yu, yd, ye, y, m, k)
        events = None
        if n:
            def ev(tt, s, n_active, _lam2, _nu_yukawa, _match=False):
                # Running downward, the first threshold crossed is the HEAVIEST
                # active state, so watch the largest singular value of M.
                _, _, _, _, _, mm, _ = _unpack(s, n_active)
                return tt - math.log(np.linalg.svd(mm, compute_uv=False).max())
            ev.terminal, ev.direction = True, -1
            events = [ev]
        rhs = _rhs
        if time_budget is not None:
            import time as _time
            deadline = _time.time() + time_budget

            def rhs(tt, s, *a, _deadline=deadline):
                if _time.time() > _deadline:
                    raise TimeoutError("threshold running exceeded its time budget")
                return _rhs(tt, s, *a)
        sol = solve_ivp(rhs, (t, t_end), state, args=(n, lam2, nu_yukawa, match_alpha), method="DOP853",
                        rtol=rtol, atol=1e-14, events=events)
        g, yu, yd, ye, y, m, k = _unpack(sol.y[:, -1], n)
        t = sol.t[-1]
        if n and sol.status == 1:
            thresholds.append(math.exp(t))
            y, m, k = _integrate_out(y, m, k, vu, math.exp(t))
            continue
        break
    hehe = ye.conj().T @ ye
    evals, u = np.linalg.eigh(hehe)
    order = np.argsort(evals)
    u = u[:, order]
    ml = np.sqrt(np.clip(evals[order], 0, None)) * vd
    mprime = u.T @ (0.5 * (k + k.T)) @ u
    return {"mnu_Z": mprime, "charged_lepton_masses_Z": ml, "thresholds_GeV": thresholds,
            "remaining_states": m.shape[0]}


def observables_with_thresholds(st, p, **kw):
    out = run_down(st, p, **kw)
    ml = out["charged_lepton_masses_Z"]
    lep = S.R._pmns_from_matrices(out["mnu_Z"], np.diag(ml).astype(complex))
    return lep, out


if __name__ == "__main__":
    import json
    import time
    wit = json.load(open(__import__("pathlib").Path(__file__).resolve().parent / "predict.json"))
    point = [w for w in wit if abs(w["target"] - 0.069) < 1e-9][0]
    st = S.Stratum(25.0, 6.313855e11, planck=False)
    p = np.array(point["x"])

    base = st.observables(p)["lep"]
    t0 = time.time()
    lep_eq, out_eq = observables_with_thresholds(st, p, nu_yukawa=False, collapse_at_mi=True)
    print("EQUIVALENCE CHECK (all N integrated out at M_I, no nu-Yukawa running):")
    for key in ("sum_mnu_eV", "dm21_eV2", "dm31_eV2", "sin2_th12", "sin2_th23", "sin2_th13", "delta_cp_deg"):
        a, bb = base[key], lep_eq[key]
        print(f"   {key:13s} baseline={a:.7g}  new-code={bb:.7g}  rel={abs(a - bb) / max(abs(a), 1e-30):.2e}")
    print("   charged leptons at M_Z:", [f"{v:.6g}" for v in out_eq["charged_lepton_masses_Z"]],
          " inputs:", [S.rg.MASS_MZ[k] for k in ("e", "mu", "tau")])
    print(f"   ({time.time() - t0:.2f} s)")
