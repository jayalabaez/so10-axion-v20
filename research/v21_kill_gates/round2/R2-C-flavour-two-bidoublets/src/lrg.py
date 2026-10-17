"""Frozen-coefficient linearised RG ('LRG') proxy: exact at its reference point, used in a fixed-point iteration to
converge the exact top-down fit.

Along a reference top-down trajectory we integrate the linear transfer objects
  G3221:  Yq_a(v_R) = Lq [sum_b Yq_b(M_U) Oq_ba] Rq,   Yl_a(v_R) = Ll [sum_b Yl_b(M_U) Ol_ba] Rl,   fh(v_R) = Rl^T fh(M_U) Rl wf
          dLq = K1 SLq Lq,  dRq = K1 Rq SRq,  dOq = K1 (Oq T - Gq Oq)   (same for l; wf: K1 (1/2 Tr fh^dag fh - Gf))
  SM:     Yx(M_Z) = Lx Yx(v_R)  (x = u, d, e; two-loop brackets frozen),   kappa(M_Z) = Lk kappa(v_R) Lk^T + Delta_ref
          (Delta_ref = exact reference m_nu(M_Z)/v^2 minus the sandwiched reference seesaw: nu^c threshold effects)
All maps are frozen at the reference; at the reference point the LRG model reproduces the exact chain to integration
accuracy (tested).  The LRG model is batched (matrix products only)."""
import math
import numpy as np
import lib_r2c as L
import model_r2c as M

herm = L.herm
K1 = L.K1; K2 = L.K2


# ----------------------------------------------------------------------------------------------------------------
# augmented G3221 integration
# ----------------------------------------------------------------------------------------------------------------
def _g_aug_rhs(t, y, b_lo, b_hi, lnMS):
    base = y[:94]
    g, Yq, Yl, fh = L._unpack_g(base)
    b = b_hi if t > lnMS else b_lo
    g3, gL, gR, gBL = g
    Gq = 8 * g3**2 + 9 / 4 * (gL**2 + gR**2) + gBL**2 / 6
    Gl = 9 / 4 * (gL**2 + gR**2) + 1.5 * gBL**2
    Gf = 4.5 * gR**2 + 1.5 * gBL**2
    SLq = sum(Y @ herm(Y) for Y in Yq); SRq = sum(herm(Y) @ Y for Y in Yq)
    FF = herm(fh) @ fh
    SLl = sum(Y @ herm(Y) for Y in Yl); SRl = sum(herm(Y) @ Y for Y in Yl) + 0.75 * FF
    Tm = np.array([[3 * np.trace(herm(Yq[c]) @ Yq[a]) + np.trace(herm(Yl[c]) @ Yl[a]) for a in range(2)] for c in range(2)])
    dq = [K1 * (SLq @ Yq[a] + Yq[a] @ SRq + Yq[0] * Tm[0, a] + Yq[1] * Tm[1, a] - Gq * Yq[a]) for a in range(2)]
    dl = [K1 * (SLl @ Yl[a] + Yl[a] @ SRl + Yl[0] * Tm[0, a] + Yl[1] * Tm[1, a] - Gl * Yl[a]) for a in range(2)]
    trf = np.trace(FF).real
    df = K1 * (SRl.T @ fh + fh @ SRl + 0.5 * trf * fh - Gf * fh)
    dg = K1 * b * g**3
    out = [L._pack_g(dg, dq, dl, df)]
    # transfer objects
    i = 94
    Ms = []
    for _ in range(4):
        Ms.append((y[i:i + 9] + 1j * y[i + 9:i + 18]).reshape(3, 3)); i += 18
    Lq, Rq, Ll, Rl = Ms
    Oq = (y[i:i + 4] + 1j * y[i + 4:i + 8]).reshape(2, 2); i += 8
    Ol = (y[i:i + 4] + 1j * y[i + 4:i + 8]).reshape(2, 2); i += 8
    dLq = K1 * SLq @ Lq; dRq = K1 * Rq @ SRq; dLl = K1 * SLl @ Ll; dRl = K1 * Rl @ SRl
    dOq = K1 * (Oq @ Tm - Gq * Oq); dOl = K1 * (Ol @ Tm - Gl * Ol)
    dwf = K1 * (0.5 * trf - Gf)
    aug = []
    for X in (dLq, dRq, dLl, dRl):
        aug += list(X.real.ravel()) + list(X.imag.ravel())
    for X in (dOq, dOl):
        aug += list(X.real.ravel()) + list(X.imag.ravel())
    aug.append(dwf)
    return np.concatenate([out[0], np.array(aug)])


def g3221_maps(gU, Yq, Yl, fh, MU, vR, b_lo, b_hi):
    y0 = L._pack_g(gU, Yq, Yl, fh)
    I = np.eye(3, dtype=complex); I2 = np.eye(2, dtype=complex)
    aug = []
    for X in (I, I, I, I):
        aug += list(X.real.ravel()) + list(X.imag.ravel())
    for X in (I2, I2):
        aug += list(X.real.ravel()) + list(X.imag.ravel())
    aug.append(0.0)
    y = np.concatenate([y0, np.array(aug)])
    lnMS = math.log(L.M_S); t0, t1 = math.log(MU), math.log(vR)
    args = (np.array(b_lo), np.array(b_hi), lnMS)
    if t1 < lnMS < t0:
        y = L._rk4(_g_aug_rhs, t0, lnMS, y, args)
        y = L._rk4(_g_aug_rhs, lnMS, t1, y, args)
    else:
        y = L._rk4(_g_aug_rhs, t0, t1, y, args)
    g, Yq2, Yl2, fh2 = L._unpack_g(y[:94])
    i = 94; Ms = []
    for _ in range(4):
        Ms.append((y[i:i + 9] + 1j * y[i + 9:i + 18]).reshape(3, 3)); i += 18
    Oq = (y[i:i + 4] + 1j * y[i + 4:i + 8]).reshape(2, 2); i += 8
    Ol = (y[i:i + 4] + 1j * y[i + 4:i + 8]).reshape(2, 2); i += 8
    wf = math.exp(y[i])
    return {"Lq": Ms[0], "Rq": Ms[1], "Ll": Ms[2], "Rl": Ms[3], "Oq": Oq, "Ol": Ol, "wf": wf,
            "Yq": Yq2, "Yl": Yl2, "fh": fh2, "g": g}


# ----------------------------------------------------------------------------------------------------------------
# augmented SM integration with nu^c thresholds
# ----------------------------------------------------------------------------------------------------------------
def _sm_brackets(st, db):
    """Return d(state) and the frozen LEFT-multiplier matrices Au, Ad, Ae (doublet-left: dYx = Ax Yx) and P (kappa)."""
    k = st.Yn.shape[1]
    YuR, YdR, YeR = st.Yu.T, st.Yd.T, st.Ye.T
    YnR = st.Yn.T if k else None
    g1, g2, g3 = st.g
    lam = st.lam
    Uu, Dd, Ee = herm(YuR) @ YuR, herm(YdR) @ YdR, herm(YeR) @ YeR
    Nn = herm(YnR) @ YnR if k else np.zeros((3, 3), complex)
    tu, td, te, tn = np.trace(Uu).real, np.trace(Dd).real, np.trace(Ee).real, np.trace(Nn).real
    T = 3 * tu + 3 * td + te + tn
    g1s, g2s, g3s = g1 * g1, g2 * g2, g3 * g3
    Gu = 17 / 20 * g1s + 9 / 4 * g2s + 8 * g3s
    Gd = 1 / 4 * g1s + 9 / 4 * g2s + 8 * g3s
    Ge = 9 / 4 * g1s + 9 / 4 * g2s
    I3 = np.eye(3)
    chi4 = 9 / 4 * (3 * np.trace(Uu @ Uu) + 3 * np.trace(Dd @ Dd) + np.trace(Ee @ Ee) - 2 / 3 * np.trace(Uu @ Dd)).real
    Y4 = Gu * tu + Gd * td + (3 / 4 * g1s + 3 / 4 * g2s) * te
    Bu = K1 * (1.5 * (Uu - Dd) + (T - Gu) * I3) + K2 * (
        1.5 * Uu @ Uu - Uu @ Dd - 0.25 * Dd @ Uu + 11 / 4 * Dd @ Dd + T * (5 / 4 * Dd - 9 / 4 * Uu)
        + (-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 + 1187 / 600 * g1s**2 - 23 / 4 * g2s**2 - 108 * g3s**2
           - 9 / 20 * g1s * g2s + 19 / 15 * g1s * g3s + 9 * g2s * g3s) * I3
        - 6 * lam * Uu + (223 / 80 * g1s + 135 / 16 * g2s + 16 * g3s) * Uu - (43 / 80 * g1s - 9 / 16 * g2s + 16 * g3s) * Dd)
    Bd = K1 * (1.5 * (Dd - Uu) + (T - Gd) * I3) + K2 * (
        1.5 * Dd @ Dd - Dd @ Uu - 0.25 * Uu @ Dd + 11 / 4 * Uu @ Uu + T * (5 / 4 * Uu - 9 / 4 * Dd)
        + (-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 - 127 / 600 * g1s**2 - 23 / 4 * g2s**2 - 108 * g3s**2
           - 27 / 20 * g1s * g2s + 31 / 15 * g1s * g3s + 9 * g2s * g3s) * I3
        - 6 * lam * Dd + (187 / 80 * g1s + 135 / 16 * g2s + 16 * g3s) * Dd - (79 / 80 * g1s - 9 / 16 * g2s + 16 * g3s) * Uu)
    Be = K1 * (1.5 * (Ee - Nn) + (T - Ge) * I3) + K2 * (
        1.5 * Ee @ Ee - 9 / 4 * T * Ee
        + (-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 + 1371 / 200 * g1s**2 - 23 / 4 * g2s**2 + 27 / 20 * g1s * g2s) * I3
        - 6 * lam * Ee + (387 / 80 * g1s + 135 / 16 * g2s) * Ee)
    # doublet-right: dY_R = Y_R B  ->  doublet-left: dY = B^T Y
    P = K1 * (-1.5 * Ee.T + 0.5 * Nn.T + 0.5 * (2 * T + lam - 3 * g2s) * I3)
    return Bu.T, Bd.T, Be.T, P


def _sm_aug_rhs(t, y, k, db):
    n0 = len(y) - 72
    base = y[:n0]
    st = L._unpack_sm(base, k)
    dbase = np.asarray(L._sm_rhs(t, base, k, db))
    Au, Ad, Ae, P = _sm_brackets(st, db)
    i = n0; Ms = []
    for _ in range(4):
        Ms.append((y[i:i + 9] + 1j * y[i + 9:i + 18]).reshape(3, 3)); i += 18
    Lu, Ld, Le, Lk = Ms
    aug = []
    for X in (Au @ Lu, Ad @ Ld, Ae @ Le, P @ Lk):
        aug += list(X.real.ravel()) + list(X.imag.ravel())
    return np.concatenate([dbase, np.array(aug)])


def _run_sm_aug(st, Ls, mu0, mu1, db):
    y0, k = L._pack_sm(st)
    aug = []
    for X in Ls:
        aug += list(X.real.ravel()) + list(X.imag.ravel())
    y = L._rk4(_sm_aug_rhs, math.log(mu0), math.log(mu1), np.concatenate([y0, np.array(aug)]), (k, db))
    n0 = len(y0)
    st2 = L._unpack_sm(y[:n0], k)
    i = n0; Ms = []
    for _ in range(4):
        Ms.append((y[i:i + 9] + 1j * y[i + 9:i + 18]).reshape(3, 3)); i += 18
    return st2, Ms


def sm_maps(st, vR):
    """Run v_R -> M_Z with thresholds (as lib_r2c.run_sm_with_seesaw) carrying Lu, Ld, Le, Lk."""
    I = np.eye(3, dtype=complex)
    Ls = [I, I, I, I]
    mu = vR
    while st.Yn.shape[1] > 0:
        m, _ = L.takagi(st.MR)
        if m[-1] >= mu:
            st, _ = L.decouple_heaviest(st)
        else:
            break
    while True:
        k = st.Yn.shape[1]
        nxt = L.MZ; from_nu = False
        if k:
            m, _ = L.takagi(st.MR)
            if m[-1] > L.MZ:
                nxt = m[-1]; from_nu = True
        if L.MZ < L.M_S < mu and L.M_S > nxt:
            nxt = L.M_S; from_nu = False
        db = L.db_sm(math.sqrt(mu * nxt))
        if nxt < mu:
            st, Ls = _run_sm_aug(st, Ls, mu, nxt, db)
        mu = nxt
        if from_nu:
            st, _ = L.decouple_heaviest(st)
            continue
        if mu <= L.MZ * (1 + 1e-12):
            break
    while st.Yn.shape[1] > 0:
        st, _ = L.decouple_heaviest(st)
    return st, {"Lu": Ls[0], "Ld": Ls[1], "Le": Ls[2], "Lk": Ls[3]}


# ----------------------------------------------------------------------------------------------------------------
# reference build + batched LRG evaluation
# ----------------------------------------------------------------------------------------------------------------
class LRG:
    def __init__(self, setup, tg, typeII=False, data=None):
        self.setup = setup; self.tg = tg; self.lay = M.Layout(typeII=typeII, free=True)
        self.data = data or setup["data"]
        self.T = np.array([self.data[k][0] for k in L.ALL_KEYS]); self.S = np.array([self.data[k][1] for k in L.ALL_KEYS])
        self.maps = None

    def _gut(self, Z):
        Z = np.atleast_2d(Z)
        X, lc = Z[:, :-1], Z[:, -1]
        G = M.gut_matrices(X, self.lay, self.tg.sd0, self.tg.se0)
        r = G["r"]; s = G["s"]; cd126 = 10.0**lc
        rem = 1 - cd126**2 * (1 + np.abs(r * s)**2)
        ok = rem > 0
        cd10 = np.sqrt(np.clip(rem, 1e-300, None) / (1 + r**2))
        return G, X, r, s, cd126, cd10, ok

    def build(self, z):
        """Exact reference run at z (also returns exact observables)."""
        env, vR = self.setup["env"], self.setup["vR"]
        G, X, r, s, cd126, cd10, ok = self._gut(z)
        if not ok[0]:
            raise ValueError("unphysical composition at reference")
        Hm, F = G["H"][0], G["F"][0]
        Y10 = Hm / cd10[0]; Y126 = F / cd126[0]
        fh = L.C_R * Y126
        gm = g3221_maps(np.array(env["g_MU"]), [Y10, Y126], [Y10, -3 * Y126], fh, env["MU"], vR, env["b_lo"], env["b_hi"])
        cu10 = r[0] * cd10[0]; cu126 = r[0] * s[0] * cd126[0]
        Yq, Yl, fhR = gm["Yq"], gm["Yl"], gm["fh"]
        Yu = cu10 * Yq[0] + cu126 * Yq[1]; Yd = cd10[0] * Yq[0] + cd126[0] * Yq[1]
        Ye = cd10[0] * Yl[0] + cd126[0] * Yl[1]; Yn = cu10 * Yl[0] + cu126 * Yl[1]
        MR = vR * fhR
        kap0 = np.zeros((3, 3), complex)
        if self.lay.typeII:
            kap0 = self._kII(np.atleast_2d(z)[0], Yn, MR, Yq[1])
        st = L.SMState(env["g_sm_vR"], env["lam_vR"], Yu, Yd, Ye, kap0, Yn, MR)
        stZ, sm = sm_maps(st, vR)
        kss = -(Yn @ np.linalg.solve(MR, Yn.T)) + kap0
        Delta = stZ.kappa - sm["Lk"] @ kss @ sm["Lk"].T
        self.maps = dict(gm, **sm, Delta=Delta)
        o = L.observables(stZ.Yu, stZ.Yd, stZ.Ye, stZ.kappa * L.VEV**2)
        return o

    def _kII(self, z, Yn, MR, Y126R):
        kI = -(Yn @ np.linalg.solve(MR, Yn.T))
        t = z[12:14]
        tc = 10.0**t[0] * np.exp(1j * t[1]) * np.linalg.norm(kI) / np.linalg.norm(Y126R)
        return tc * Y126R

    def eval(self, Z, want=False):
        mp = self.maps
        vR = self.setup["vR"]
        G, X, r, s, cd126, cd10, ok = self._gut(Z)
        N = len(r)
        Hm, F = G["H"], G["F"]
        cd10 = np.where(ok, cd10, 1.0); cd126 = np.where(ok, cd126, 1.0)
        Y10 = Hm / cd10[:, None, None]; Y126 = F / cd126[:, None, None]
        Oq, Ol = mp["Oq"], mp["Ol"]
        Yq0 = Y10 * Oq[0, 0] + Y126 * Oq[1, 0]; Yq1 = Y10 * Oq[0, 1] + Y126 * Oq[1, 1]
        Yl0 = Y10 * Ol[0, 0] - 3 * Y126 * Ol[1, 0]; Yl1 = Y10 * Ol[0, 1] - 3 * Y126 * Ol[1, 1]
        Lq, Rq, Ll, Rl = mp["Lq"], mp["Rq"], mp["Ll"], mp["Rl"]
        Yq0 = Lq @ Yq0 @ Rq; Yq1 = Lq @ Yq1 @ Rq; Yl0 = Ll @ Yl0 @ Rl; Yl1 = Ll @ Yl1 @ Rl
        fhR = (Rl.T @ (L.C_R * Y126) @ Rl) * mp["wf"]
        cu10 = (r * cd10)[:, None, None]; cu126 = (r * s * cd126)[:, None, None]
        c10 = cd10[:, None, None]; c126 = cd126[:, None, None]
        Yu = cu10 * Yq0 + cu126 * Yq1; Yd = c10 * Yq0 + c126 * Yq1
        Ye = c10 * Yl0 + c126 * Yl1; Yn = cu10 * Yl0 + cu126 * Yl1
        MR = vR * fhR
        MR = np.where(np.isfinite(MR), MR, 0.0)
        bad = np.abs(np.linalg.det(MR)) < 1e-300
        MR[bad] = np.eye(3)
        kss = -(Yn @ np.linalg.solve(MR, np.swapaxes(Yn, 1, 2)))
        kss[bad] = np.nan
        if self.lay.typeII:
            Zz = np.atleast_2d(Z)
            nI = np.linalg.norm(kss, axis=(1, 2)); nY = np.linalg.norm(Yq1, axis=(1, 2))
            tc = 10.0**Zz[:, 12] * np.exp(1j * Zz[:, 13]) * nI / nY
            kss = kss + tc[:, None, None] * Yq1
        YuZ = mp["Lu"] @ Yu; YdZ = mp["Ld"] @ Yd; YeZ = mp["Le"] @ Ye
        kZ = mp["Lk"] @ kss @ mp["Lk"].T + mp["Delta"]
        mnu = kZ * L.VEV**2
        # observables (batched); NaN-safe
        Yb = np.stack([YuZ, YdZ, YeZ], 1)                 # (N,3,3,3)
        fin = np.all(np.isfinite(Yb.reshape(N, -1)), axis=1) & np.all(np.isfinite(mnu.reshape(N, -1)), axis=1)
        sc = np.abs(mnu).reshape(N, -1).max(axis=1)
        fin &= (sc > 0) & (sc < 1e30) & (np.abs(Yb).reshape(N, -1).max(axis=1) < 1e6)
        Yb = np.where(fin[:, None, None, None], Yb, 0.0)
        mnu = np.where(fin[:, None, None], mnu, 0.0)
        w, E = np.linalg.eigh(Yb @ herm(Yb))
        sv = np.sqrt(np.clip(w, 0, None)) * L.VEV
        V = np.swapaxes(E[:, 0], 1, 2) @ np.conj(E[:, 1])
        c12, c23, c13, cd = L.angles_b(V)
        wn, Nv = np.linalg.eigh(herm(mnu) @ mnu)
        mn = np.sqrt(np.clip(wn, 0, None))
        U = np.swapaxes(E[:, 2], 1, 2) @ Nv
        n12, n23, n13, nd = L.angles_b(U)
        obs = np.zeros((N, 18))
        obs[:, 0:3] = sv[:, 0]; obs[:, 3:6] = sv[:, 1]; obs[:, 6:9] = sv[:, 2]
        obs[:, 9] = c12; obs[:, 10] = c23; obs[:, 11] = c13; obs[:, 12] = cd
        obs[:, 13] = n12**2; obs[:, 14] = n23**2; obs[:, 15] = n13**2
        obs[:, 16] = (mn[:, 1]**2 - mn[:, 0]**2) * 1e18; obs[:, 17] = (mn[:, 2]**2 - mn[:, 0]**2) * 1e18
        T, S = self.T, self.S
        R = np.empty((N, 18))
        for i, k in enumerate(L.ALL_KEYS):
            if k in L.MASS_KEYS:
                R[:, i] = np.log(np.clip(obs[:, i], 1e-300, None) / T[i]) * T[i] / S[i]
            elif k == "delta":
                R[:, i] = ((np.abs(obs[:, i]) - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
            else:
                R[:, i] = (obs[:, i] - T[i]) / S[i]
        R[obs[:, 17] <= 0] += 1e3
        R = np.where(np.isfinite(R), R, 1e3)
        R[~ok] = 1e3
        R[~fin] = 1e3
        if want:
            return R, obs
        return R


# ----------------------------------------------------------------------------------------------------------------
# fixed-point iteration + exact polish
# ----------------------------------------------------------------------------------------------------------------
from scipy.optimize import least_squares


def exact_resid(setup, tg, lay, data, z):
    try:
        o = M.top_down(z[:-1], lay, setup, tg, z[-1])
    except Exception:
        return np.full(18, 1e3), None
    if o is None:
        return np.full(18, 1e3), None
    r, _ = M.td_residuals(o, data)
    if o["dm31"] <= 0:
        r = r + 1e3
    return np.where(np.isfinite(r), r, 1e3), o


def lrg_fit(setup, tg, z0, typeII=False, data=None, iters=12, verbose=False, polish_nfev=0):
    L.USE_RK4 = True
    lr = LRG(setup, tg, typeII, data)
    data = lr.data
    lay = lr.lay
    z = np.array(z0, float)
    r0, _ = exact_resid(setup, tg, lay, data, z)
    c = float(np.sum(r0**2))
    hist = [c]
    for it in range(iters):
        try:
            lr.build(z)
        except Exception as e:
            break
        f = lambda zz: lr.eval(zz[None])[0]

        def jac(zz, h=1e-6):
            n = len(zz)
            Z = np.tile(zz, (n + 1, 1)); Z[1:] += np.eye(n) * h
            R = lr.eval(Z)
            return ((R[1:] - R[0]) / h).T
        try:
            sol = least_squares(f, z, jac=jac, method="trf", max_nfev=400, xtol=1e-12, ftol=1e-12, gtol=1e-12, x_scale="jac")
            zn = sol.x
        except Exception:
            break
        # trust: accept only exact improvements, else damp
        acc = False
        for damp in (1.0, 0.5, 0.25, 0.1):
            zt = z + damp * (zn - z)
            rt, _ = exact_resid(setup, tg, lay, data, zt)
            ct = float(np.sum(rt**2))
            if ct < c:
                acc = True
                break
        if verbose:
            print(f"     LRG it {it}: lrg-min {float(np.sum(sol.fun**2)):.3f}  exact {ct:.3f} (damp {damp}) prev {c:.3f}", flush=True)
        if not acc:
            break
        rel = (c - ct) / max(c, 1e-9)
        z, c = zt, ct
        hist.append(c)
        if rel < 1e-4:
            break
    if polish_nfev:
        sol = least_squares(lambda zz: exact_resid(setup, tg, lay, data, zz)[0], z, method="trf", max_nfev=polish_nfev,
                            xtol=1e-12, ftol=1e-12, gtol=1e-12, x_scale="jac", diff_step=1e-7)
        rt, _ = exact_resid(setup, tg, lay, data, sol.x)
        ct = float(np.sum(rt**2))
        if ct < c:
            z, c = sol.x, ct
            hist.append(c)
    return z, c, hist
