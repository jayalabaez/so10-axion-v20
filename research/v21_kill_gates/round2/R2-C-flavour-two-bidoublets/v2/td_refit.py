"""Exact top-down refit (G3221 two-bidoublet one-loop M_U -> v_R, SM two-loop + sequential nu^c decoupling v_R -> M_Z)
starting from a proxy minimum.  Parameters: free-mass proxy layout (+ type II) + lc = log10 c_d126; tau fixed at start."""
import math, json, time
import numpy as np
from scipy.optimize import least_squares
import lib_r2c as L
import model_r2c as M


def lc_guess(rho_eff, vR):
    return math.log10(max(rho_eff * 1e-9 * L.C_R * vR / L.VEV**2, 1e-12))


def gut_inputs_for_tau(x, lay, tg, lc):
    G = M.gut_matrices(np.atleast_2d(x), lay, tg.sd0, tg.se0)
    r = float(G["r"][0]); s = complex(G["s"][0])
    comp = M.composition(r, s, 10.0**lc)
    if comp is None:
        return None
    Y10 = G["H"][0] / comp["c_d10"]; Y126 = G["F"][0] / comp["c_d126"]
    return [Y10, Y126], [Y10, -3 * Y126]


class TD:
    def __init__(self, setup, tg, typeII=False, data=None, tau=(1.0, 1.0)):
        self.setup = setup; self.tg = tg; self.lay = M.Layout(typeII=typeII, free=True)
        self.data = data or setup["data"]; self.tau = tau; self.nev = 0

    def unpack(self, z):
        return z[:-1], z[-1]

    def resid(self, z):
        x, lc = self.unpack(z)
        self.nev += 1
        try:
            o = M.top_down(x, self.lay, self.setup, self.tg, lc, tau=self.tau)
        except Exception:
            o = None
        if o is None or not np.isfinite(o["m_t"]):
            return np.full(18, 1e3)
        r, _ = M.td_residuals(o, self.data)
        if o["dm31"] <= 0:
            r = r + 1e3
        return np.where(np.isfinite(r), r, 1e3)

    def chi2(self, z):
        r = self.resid(z)
        return float(np.sum(r * r))


def to_free(x_proxy, lay_proxy):
    """proxy (pinned) x -> free layout (offsets 0), keeping type II entries."""
    x = list(x_proxy[:lay_proxy.n_core])
    return np.array(x + [0.0] * 6, float)


def refit(setup, tg, x_proxy, typeII=False, rho_eff=None, max_nfev=150, data=None, verbose=False, lc0=None):
    lay_p = M.Layout(typeII=typeII)
    x0 = to_free(x_proxy, lay_p)
    if lc0 is None:
        if rho_eff is None:
            _, _, aux = M.proxy_eval(np.atleast_2d(x_proxy), lay_p, tg, want_obs=True)
            rho_eff = float(aux["rho_eff"][0])
        lc0 = lc_guess(rho_eff, setup["vR"])
    # tau at the start
    td = TD(setup, tg, typeII, data)
    lay = td.lay
    gi = gut_inputs_for_tau(x0, lay, tg, lc0)
    tau = (1.0, 1.0)
    if gi is not None:
        env = setup["env"]
        tau = tuple(L.tau_factors(env["g_MU"], gi[0], gi[1], env["MU"], setup["vR"], env["b_lo"], env["b_hi"]))
    td.tau = tau
    # 1-d scan of lc
    best = None
    for dl in np.linspace(-0.6, 0.6, 13):
        z = np.concatenate([x0, [lc0 + dl]])
        c = td.chi2(z)
        if best is None or c < best[0]:
            best = (c, z)
    c_start = best[0]
    t0 = time.time()
    r = least_squares(td.resid, best[1], method="trf", max_nfev=max_nfev, xtol=1e-10, ftol=1e-10, gtol=1e-10,
                      x_scale="jac", diff_step=1e-6)
    z = r.x
    c_end = td.chi2(z)
    if verbose:
        print(f"   td refit: tau={tuple(round(t,4) for t in tau)} start chi2 {c_start:.2f} -> {c_end:.3f}  nev={td.nev} t={time.time()-t0:.0f}s", flush=True)
    return {"z": z, "chi2_start": c_start, "chi2": c_end, "tau": tau, "td": td}


def report_point(td, z):
    x, lc = td.unpack(z)
    o, ex = M.top_down(x, td.lay, td.setup, td.tg, lc, want=True, tau=td.tau)
    r, pl = M.td_residuals(o, td.data)
    U = o["U_pmns"]
    mn = o["m_nu_eV"]
    rec = {"chi2": float(np.sum(r**2)), "max_abs_pull": float(np.max(np.abs(r))), "pulls": {k: float(v) for k, v in pl.items()},
           "obs_MZ": {k: (float(v) if isinstance(v, (float, int, np.floating)) else None) for k, v in o.items() if k not in ("U_pmns", "m_nu_eV")},
           "m_nu_eV": [float(v) for v in mn], "m_lightest_eV": float(min(mn)), "sum_mnu_eV": float(sum(mn)),
           "m_betabeta_eV": L.mbb_and_majorana(U, mn), "delta_pmns_deg": float(math.degrees(o["delta_pmns"]) % 360),
           "r": float(10**x[9]), "s": [float(10**x[10] * math.cos(x[11])), float(10**x[10] * math.sin(x[11]))],
           "s_abs": float(10**x[10]), "s_arg": float(x[11]), "c_d126": float(10**lc), "tau": list(td.tau),
           "comp": {k: (v if not isinstance(v, complex) else [v.real, v.imag]) for k, v in ex["comp"].items()},
           "Y10_act_max": ex["Y10_act_max"], "Y126_act_max": ex["Y126_act_max"], "Y10_def_sv": ex["Y10_def_sv"],
           "Y126_def_sv": ex["Y126_def_sv"], "fh_vR_sv": ex["fh_vR_sv"], "M_R_GeV": ex["M_R_GeV"], "z": list(map(float, z))}
    # sign convention: physical delta_CKM > 0; if our extracted delta_CKM < 0 the physical point is the CP conjugate
    if o["delta"] < 0:
        rec["delta_pmns_deg"] = float((360 - rec["delta_pmns_deg"]) % 360)
        rec["cp_conjugated_for_report"] = True
    comp = ex["comp"]
    rec["perturbative_Y_act_le_1.5"] = bool(ex["Y10_act_max"] <= 1.5 and ex["Y126_act_max"] <= 1.5)
    return rec
