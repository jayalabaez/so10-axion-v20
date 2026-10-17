"""R2-C model layer: parametrisation, batched GUT-scale proxy, bottom-up target map B, exact top-down chain.

Parameter vector x (proxy, 'pinned' masses):
  x[0:9]   W in U(3): th12, th13, th23, delta, a1, a2, b1, b2, b3  (Ye = W diag(se) W^T, Yd = diag(sd) at M_U)
  x[9]     log10 r          (r > 0)
  x[10]    log10 |s|
  x[11]    arg s
  type II: x[12] = log10 |t|, x[13] = arg t    (m_nu ∝ -Ynu F^-1 Ynu^T + t * (||.||/||F||) F)
  free masses: + 6 log offsets for (sd, se)
Top-down adds one parameter: lc = log10 c_d126 (fixes M_R = C_R v_R F / c_d126 and the composition).
"""
import math, json
import numpy as np
import lib_r2c as L

IDX_MASS = {k: i for i, k in enumerate(L.ALL_KEYS)}


class Layout:
    def __init__(self, typeII=False, free=False):
        self.typeII = typeII; self.free = free
        self.n_core = 12 + (2 if typeII else 0)
        self.n = self.n_core + (6 if free else 0)

    def split(self, X):
        X = np.atleast_2d(X)
        core = X[:, :12]
        t = X[:, 12:14] if self.typeII else None
        off = X[:, self.n_core:self.n_core + 6] if self.free else None
        return core, t, off


def W_batch(core):
    U = L.umix_b(core[:, 0], core[:, 1], core[:, 2], core[:, 3])
    P1 = np.exp(1j * np.stack([core[:, 4], core[:, 5], np.zeros(len(core))], 1))
    P2 = np.exp(1j * core[:, 6:9])
    return P1[:, :, None] * U * P2[:, None, :]


def gut_matrices(X, lay, sd0, se0):
    core, t, off = lay.split(X)
    N = core.shape[0]
    sd = np.tile(sd0, (N, 1)); se = np.tile(se0, (N, 1))
    if off is not None:
        sd = sd * np.exp(off[:, 0:3]); se = se * np.exp(off[:, 3:6])
    W = W_batch(core)
    Ye = (W * se[:, None, :]) @ np.swapaxes(W, 1, 2)
    Yd = np.zeros((N, 3, 3), complex)
    Yd[:, [0, 1, 2], [0, 1, 2]] = sd
    Hm = (3 * Yd + Ye) / 4
    F = (Yd - Ye) / 4
    r = 10.0**core[:, 9]
    s = 10.0**core[:, 10] * np.exp(1j * core[:, 11])
    Yu = r[:, None, None] * (Hm + s[:, None, None] * F)
    Yn = r[:, None, None] * (Hm - 3 * s[:, None, None] * F)
    return dict(W=W, Yd=Yd, Ye=Ye, H=Hm, F=F, Yu=Yu, Yn=Yn, r=r, s=s, sd=sd, se=se, t=t)


class Targets:
    """Proxy-space targets: central values T (18,) and errors S (18,), plus pinned eigenvalues sd0, se0 at M_U."""
    def __init__(self, T, S, sd0, se0, info=None):
        self.T = np.array(T, float); self.S = np.array(S, float)
        self.sd0 = np.array(sd0, float); self.se0 = np.array(se0, float); self.info = info or {}

    def shifted(self, delta):
        """Corrected targets T' = T + delta (masses: log-space delta)."""
        T2 = self.T.copy()
        for i, k in enumerate(L.ALL_KEYS):
            if k in L.MASS_KEYS:
                T2[i] = self.T[i] * math.exp(delta[i])
            else:
                T2[i] = self.T[i] + delta[i]
        sd0 = T2[[IDX_MASS["m_d"], IDX_MASS["m_s"], IDX_MASS["m_b"]]] / L.VEV
        se0 = T2[[IDX_MASS["m_e"], IDX_MASS["m_mu"], IDX_MASS["m_tau"]]] / L.VEV
        return Targets(T2, self.S, sd0, se0, dict(self.info, shifted=True))


def proxy_eval(X, lay, tg, want_obs=False):
    """Batched proxy residuals (N,18) [order L.ALL_KEYS] and chi2 (N,)."""
    G = gut_matrices(X, lay, tg.sd0, tg.se0)
    N = G["Yu"].shape[0]
    v = L.VEV
    w, Eu = np.linalg.eigh(G["Yu"] @ L.herm(G["Yu"]))
    mu = np.sqrt(np.clip(w, 0, None)) * v
    CKM = np.swapaxes(Eu, 1, 2)                       # E_u^T E_d^*, E_d = 1 (d-diagonal, ascending)
    c12, c23, c13, cd = L.angles_b(CKM)
    F = G["F"]
    ok = np.ones(N, bool)
    try:
        X1 = np.linalg.solve(F, np.swapaxes(G["Yn"], 1, 2))
    except np.linalg.LinAlgError:
        X1 = np.full((N, 3, 3), np.nan, complex)
    m1 = -G["Yn"] @ X1
    if lay.typeII:
        t = G["t"]
        nm1 = np.linalg.norm(m1, axis=(1, 2)); nF = np.linalg.norm(F, axis=(1, 2))
        tc = 10.0**t[:, 0] * np.exp(1j * t[:, 1]) * nm1 / np.where(nF > 0, nF, 1)
        m1 = m1 + tc[:, None, None] * F
    sc = np.abs(m1).max(axis=(1, 2))
    bad = ~np.isfinite(sc) | (sc <= 0)
    sc = np.where(bad, 1.0, sc)
    m1 = m1 / sc[:, None, None]
    m1 = np.where(np.isfinite(m1), m1, 0)
    wn, Nv = np.linalg.eigh(L.herm(m1) @ m1)
    mn = np.sqrt(np.clip(wn, 0, None))
    U = np.swapaxes(G["W"], 1, 2) @ Nv               # PMNS = E_e^T N, E_e = W
    n12, n23, n13, nd = L.angles_b(U)
    a21 = mn[:, 1]**2 - mn[:, 0]**2; a31 = mn[:, 2]**2 - mn[:, 0]**2
    T, S = tg.T, tg.S
    i21, i31 = IDX_MASS["dm21"], IDX_MASS["dm31"]
    num = a21 * T[i21] / S[i21]**2 + a31 * T[i31] / S[i31]**2
    den = a21**2 / S[i21]**2 + a31**2 / S[i31]**2
    lam = np.clip(num / np.where(den > 0, den, 1e-300), 1e-300, None)
    obs = np.zeros((N, 18))
    obs[:, 0:3] = mu
    obs[:, 3:6] = G["sd"] * v
    obs[:, 6:9] = G["se"] * v
    obs[:, 9] = c12; obs[:, 10] = c23; obs[:, 11] = c13; obs[:, 12] = cd
    obs[:, 13] = n12**2; obs[:, 14] = n23**2; obs[:, 15] = n13**2
    obs[:, 16] = lam * a21; obs[:, 17] = lam * a31
    R = np.empty((N, 18))
    for i, k in enumerate(L.ALL_KEYS):
        if k in L.MASS_KEYS:
            R[:, i] = np.log(np.clip(obs[:, i], 1e-300, None) / T[i]) * T[i] / S[i]
        elif k == "delta":
            R[:, i] = ((np.abs(obs[:, i]) - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
        else:
            R[:, i] = (obs[:, i] - T[i]) / S[i]
    R = np.where(np.isfinite(R), R, 1e3)
    R[bad] = 1e3
    chi2 = np.sum(R * R, axis=1)
    if want_obs:
        rho_eff = np.sqrt(lam) / sc       # m_nu (proxy units: v^2 rnu^2 dropped) = rho_eff * m1_unscaled
        return R, chi2, dict(obs=obs, delta_pmns=nd, mn=mn * np.sqrt(lam)[:, None], U=U, rho_eff=rho_eff, G=G)
    return R, chi2


# ------------------------------------------------------------------------------------------------------------------
# setup per v_R: gauge environment + bottom-up targets B(data)
# ------------------------------------------------------------------------------------------------------------------
def data_matrices(d):
    """Yukawas (doublet-left) and kappa at M_Z built from an observable dict d (central values)."""
    m = {k: (d[k][0] if isinstance(d[k], (tuple, list)) else d[k]) for k in L.ALL_KEYS}
    V = L.umix(m["s12"], m["s23"], m["s13"], m["delta"])
    Yu = np.diag([m["m_u"], m["m_c"], m["m_t"]]).astype(complex) / L.VEV
    Yd = V.conj() @ np.diag([m["m_d"], m["m_s"], m["m_b"]]).astype(complex) / L.VEV     # CKM = E_d^* with E_u = 1
    Ye = np.diag([m["m_e"], m["m_mu"], m["m_tau"]]).astype(complex) / L.VEV
    dpm = d.get("delta_pmns_deg", (212.0, 35.0))
    dpm = math.radians(dpm[0] if isinstance(dpm, (tuple, list)) else dpm)
    U = L.umix(math.sqrt(m["sin2_th12"]), math.sqrt(m["sin2_th23"]), math.sqrt(m["sin2_th13"]), dpm)
    mn = np.array([1e-3, math.sqrt(1e-6 + m["dm21"]), math.sqrt(1e-6 + m["dm31"])]) * 1e-9      # m1 = 1 meV (NO) GeV
    mnu = U.conj() @ np.diag(mn) @ U.conj().T
    return Yu, Yd, Ye, mnu / L.VEV**2


def bottom_up(d, vR, gz, env, lam0=0.26):
    """B map: SM two-loop M_Z -> v_R (+B63 shift above M_S), then universal G3221 gauge factors v_R -> M_U.
    Returns proxy-space observable vector (18,) and info."""
    Yu, Yd, Ye, kap = data_matrices(d)
    st = L.SMState(gz, lam0, Yu, Yd, Ye, kap)
    mu = L.MZ
    if vR > L.M_S:
        st = L.run_sm(st, L.MZ, L.M_S, db=0.0); mu = L.M_S
        st = L.run_sm(st, L.M_S, vR, db=L.B63_SM_SHIFT)
    else:
        st = L.run_sm(st, L.MZ, vR, db=0.0)
    o_vR = L.observables(st.Yu, st.Yd, st.Ye, st.kappa * L.VEV**2)
    # universal gauge factors above v_R (one loop, from the G3221 couplings of env)
    eta = gauge_factors(env)
    obs = np.zeros(18)
    for i, k in enumerate(L.ALL_KEYS):
        if k in ("m_u", "m_c", "m_t", "m_d", "m_s", "m_b"):
            obs[i] = o_vR[k] * eta["q"]
        elif k in ("m_e", "m_mu", "m_tau"):
            obs[i] = o_vR[k] * eta["l"]
        elif k == "delta":
            obs[i] = abs(o_vR[k])
        else:
            obs[i] = o_vR[k]
    return obs, {"o_vR": {k: (float(v) if not isinstance(v, (list, np.ndarray)) else None) for k, v in o_vR.items()},
                 "g_sm_vR": st.g.tolist(), "lam_vR": st.lam, "eta": eta}


def gauge_factors(env, n=400):
    """exp(-(1/16pi^2) int G dt) from v_R to M_U for quark and lepton Yukawas (one-loop gauge couplings of env)."""
    vR, MU = env["vR"], env["MU"]
    a_vR = np.array(env["alpha_inv_vR"]); b_lo = np.array(env["b_lo"]); b_hi = np.array(env["b_hi"])
    ts = np.linspace(math.log(vR), math.log(MU), n + 1)
    Iq = Il = 0.0
    for j in range(n):
        tm = 0.5 * (ts[j] + ts[j + 1]); mu = math.exp(tm)
        if vR >= L.M_S:
            a = a_vR - b_hi / (2 * math.pi) * (tm - math.log(vR))
        elif mu <= L.M_S:
            a = a_vR - b_lo / (2 * math.pi) * (tm - math.log(vR))
        else:
            aS = a_vR - b_lo / (2 * math.pi) * (math.log(L.M_S) - math.log(vR))
            a = aS - b_hi / (2 * math.pi) * (tm - math.log(L.M_S))
        g2 = 4 * math.pi / a
        Gq = 8 * g2[0] + 9 / 4 * (g2[1] + g2[2]) + g2[3] / 6
        Gl = 9 / 4 * (g2[1] + g2[2]) + 1.5 * g2[3]
        dt = ts[j + 1] - ts[j]
        Iq += Gq * dt; Il += Gl * dt
    return {"q": math.exp(-L.K1 * Iq), "l": math.exp(-L.K1 * Il)}


def make_setup(vR, data, content="C2", MU=None, lam0=0.26):
    gz = L.gauge_mz()
    # SM gauge couplings at v_R from a data run (Yukawas included two-loop)
    Yu, Yd, Ye, kap = data_matrices(data)
    st = L.SMState(gz, lam0, Yu, Yd, Ye, kap)
    if vR > L.M_S:
        st = L.run_sm(L.run_sm(st, L.MZ, L.M_S), L.M_S, vR, db=L.B63_SM_SHIFT)
    else:
        st = L.run_sm(st, L.MZ, vR)
    env = L.g3221_couplings(vR, st.g, content=content, MU=MU)
    env["g_sm_vR"] = st.g.tolist(); env["lam_vR"] = st.lam; env["content"] = content
    obs, info = bottom_up(data, vR, gz, env, lam0)
    T = obs.copy(); S = np.zeros(18)
    for i, k in enumerate(L.ALL_KEYS):
        c, s = data[k]
        if k in L.MASS_KEYS or k in ("s12", "s23", "s13", "dm21", "dm31"):
            S[i] = s / c * T[i]
        else:
            S[i] = s
    sd0 = T[[3, 4, 5]] / L.VEV; se0 = T[[6, 7, 8]] / L.VEV
    tg = Targets(T, S, sd0, se0, dict(info, vR=vR))
    return {"vR": vR, "env": env, "targets": tg, "data": data, "lam0": lam0, "gz": gz.tolist()}


# ------------------------------------------------------------------------------------------------------------------
# exact top-down chain
# ------------------------------------------------------------------------------------------------------------------
def composition(r, s, cd126):
    """Corrected normalisation.  Returns dict or None if unphysical."""
    rem = 1 - cd126**2 * (1 + abs(r * s)**2)
    if rem <= 0:
        return None
    cd10 = math.sqrt(rem / (1 + r**2))
    return {"c_d10": cd10, "c_u10": r * cd10, "c_d126": cd126, "c_u126": r * s * cd126,
            "abs": [r * cd10, abs(r * s) * cd126, cd10, cd126],
            "frac_126_in_H": float(abs(r * s * cd126)**2 + cd126**2)}


def top_down(x, lay, setup, tg, lc, rtol=1e-7, want=False, tau=(1.0, 1.0)):
    """x: proxy-layout parameters (pinned eigenvalues from tg unless lay.free); lc = log10 c_d126.
    Type II (top-down): kappa_II(v_R) = t * Y126(v_R) * (scale), t from x[12:14] relative to the type-I size."""
    vR, env = setup["vR"], setup["env"]
    G = gut_matrices(np.atleast_2d(x), lay, tg.sd0, tg.se0)
    Hm, F = G["H"][0] / tau[0], G["F"][0] / tau[1]     # GUT inputs (tau: fixed reparametrisation constants;
    r = float(G["r"][0]); s = complex(G["s"][0])        #  r, s are v_R-level composition ratios, unchanged)
    cd126 = 10.0**lc
    comp = composition(r, s, cd126)
    if comp is None:
        return None
    cd10, cu10, cu126 = comp["c_d10"], comp["c_u10"], comp["c_u126"]
    Y10 = Hm / cd10; Y126 = F / cd126
    fh = L.C_R * Y126
    gU = np.array(env["g_MU"])
    g, Yq, Yl, fhR = L.run_g3221_fast(gU, [Y10, Y126], [Y10, -3 * Y126], fh, env["MU"], vR, env["b_lo"], env["b_hi"], rtol=rtol)
    Yu = cu10 * Yq[0] + cu126 * Yq[1]
    Yd = cd10 * Yq[0] + cd126 * Yq[1]
    Ye = cd10 * Yl[0] + cd126 * Yl[1]
    Yn = cu10 * Yl[0] + cu126 * Yl[1]
    MR = vR * fhR
    kap0 = np.zeros((3, 3), complex)
    if lay.typeII:
        # size relative to the type-I kappa at v_R
        mR, UR = L.takagi(MR)
        kI = -(Yn @ np.linalg.solve(MR, Yn.T))
        t = np.atleast_2d(x)[0, 12:14]
        Y126R = Yq[1]
        tc = 10.0**t[0] * np.exp(1j * t[1]) * np.linalg.norm(kI) / np.linalg.norm(Y126R)
        kap0 = tc * Y126R
    st = L.SMState(env["g_sm_vR"], env["lam_vR"], Yu, Yd, Ye, kap0, Yn, MR)
    st = L.run_sm_with_seesaw(st, vR, L.MZ, db_func=L.db_sm, rtol=rtol, thresholds_extra=(L.M_S,))
    o = L.observables(st.Yu, st.Yd, st.Ye, st.kappa * L.VEV**2)
    if not want:
        return o
    extra = {"comp": comp, "Y10_def_sv": np.linalg.svd(Y10, compute_uv=False).tolist(),
             "Y126_def_sv": np.linalg.svd(Y126, compute_uv=False).tolist(),
             "Y10_act_max": float(np.abs(Y10).max() * L.Y10_ACT), "Y126_act_max": float(np.abs(Y126).max() * L.Y126_ACT),
             "fh_MU_max": float(np.abs(fh).max()), "fh_vR_sv": np.linalg.svd(fhR, compute_uv=False).tolist(),
             "M_R_GeV": L.takagi(MR)[0].tolist(), "Yq10_vR_sv": np.linalg.svd(Yq[0], compute_uv=False).tolist(),
             "g_vR_G3221": g.tolist()}
    return o, extra


def td_residuals(o, data):
    pl = L.pulls(o, data)
    return np.array([pl[k] for k in L.ALL_KEYS]), pl


def mass_ordering_ok(o):
    return o["dm31"] > 0
