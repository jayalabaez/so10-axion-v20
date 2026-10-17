"""BATCHED exact top-down chain (same physics as model_r2c.top_down, vectorised over N parameter points):
  M_U -> v_R : G3221 two-bidoublet one-loop RG (fixed-step RK4, split at M_S)
  v_R        : light-doublet matching (corrected composition), M_R = v_R fh(v_R), optional type II kappa
  v_R -> M_Z : SM two-loop (gauge, Yu, Yd, Ye; LWX), one-loop nu^c sector (Yn, M_R) and Weinberg operator, with
               SEQUENTIAL nu^c decoupling at each point's own threshold (per-point RK4 sub-step to the threshold,
               tree-level matching kappa += -y y^T / M), B63 vector-like shift above M_S.
Internally Yu, Yd, Ye, Yn are stored doublet-RIGHT (Y_R = Y_L^T, Yn_R rows = nu^c), kappa symmetric (doublet indices).
Parameter vector z = free-layout x (18 [+2 type II]) + lc = log10 c_d126."""
import math
import numpy as np
import lib_r2c as L
import model_r2c as M

K1 = L.K1; K2 = L.K2
I3 = np.eye(3)


def H(A):
    return np.conj(np.swapaxes(A, -1, -2))


def tr(A):
    return np.real(np.trace(A, axis1=-2, axis2=-1))


# ----------------------------------------------------------------------------------------------------------------
# G3221 batched
# ----------------------------------------------------------------------------------------------------------------
def g_rhs(s, b):
    g, Yq0, Yq1, Yl0, Yl1, fh = s
    g3, gL, gR, gBL = g[:, 0], g[:, 1], g[:, 2], g[:, 3]
    Gq = (8 * g3**2 + 9 / 4 * (gL**2 + gR**2) + gBL**2 / 6)[:, None, None]
    Gl = (9 / 4 * (gL**2 + gR**2) + 1.5 * gBL**2)[:, None, None]
    Gf = (4.5 * gR**2 + 1.5 * gBL**2)[:, None, None]
    SLq = Yq0 @ H(Yq0) + Yq1 @ H(Yq1); SRq = H(Yq0) @ Yq0 + H(Yq1) @ Yq1
    FF = H(fh) @ fh
    SLl = Yl0 @ H(Yl0) + Yl1 @ H(Yl1); SRl = H(Yl0) @ Yl0 + H(Yl1) @ Yl1 + 0.75 * FF
    T00 = (3 * np.trace(H(Yq0) @ Yq0, axis1=1, axis2=2) + np.trace(H(Yl0) @ Yl0, axis1=1, axis2=2))[:, None, None]
    T01 = (3 * np.trace(H(Yq0) @ Yq1, axis1=1, axis2=2) + np.trace(H(Yl0) @ Yl1, axis1=1, axis2=2))[:, None, None]
    T10 = (3 * np.trace(H(Yq1) @ Yq0, axis1=1, axis2=2) + np.trace(H(Yl1) @ Yl0, axis1=1, axis2=2))[:, None, None]
    T11 = (3 * np.trace(H(Yq1) @ Yq1, axis1=1, axis2=2) + np.trace(H(Yl1) @ Yl1, axis1=1, axis2=2))[:, None, None]
    # sum_c Y_c T_ca : a=0 -> Y0 T00 + Y1 T10 ; a=1 -> Y0 T01 + Y1 T11
    dq0 = K1 * (SLq @ Yq0 + Yq0 @ SRq + Yq0 * T00 + Yq1 * T10 - Gq * Yq0)
    dq1 = K1 * (SLq @ Yq1 + Yq1 @ SRq + Yq0 * T01 + Yq1 * T11 - Gq * Yq1)
    dl0 = K1 * (SLl @ Yl0 + Yl0 @ SRl + Yl0 * T00 + Yl1 * T10 - Gl * Yl0)
    dl1 = K1 * (SLl @ Yl1 + Yl1 @ SRl + Yl0 * T01 + Yl1 * T11 - Gl * Yl1)
    trF = tr(FF)[:, None, None]
    df = K1 * (np.swapaxes(SRl, 1, 2) @ fh + fh @ SRl + 0.5 * trF * fh - Gf * fh)
    dg = K1 * b[None, :] * g**3
    return [dg, dq0, dq1, dl0, dl1, df]


def rk4_step(f, s, dt, *args):
    """s: list of arrays with leading batch dim N; dt: scalar or (N,) array."""
    dt = np.asarray(dt, float)

    def bc(x, a):
        if dt.ndim == 0:
            return a * dt
        return a * dt.reshape((-1,) + (1,) * (x.ndim - 1))
    k1 = f(s, *args)
    s2 = [x + bc(x, 0.5 * k) for x, k in zip(s, k1)]
    k2 = f(s2, *args)
    s3 = [x + bc(x, 0.5 * k) for x, k in zip(s, k2)]
    k3 = f(s3, *args)
    s4 = [x + bc(x, k) for x, k in zip(s, k3)]
    k4 = f(s4, *args)
    return [x + bc(x, (a + 2 * b_ + 2 * c + d) / 6) for x, a, b_, c, d in zip(s, k1, k2, k3, k4)]


def run_g3221_b(s, MU, vR, b_lo, b_hi, h=0.5):
    t0, t1 = math.log(MU), math.log(vR)
    lnMS = math.log(L.M_S)
    segs = [(t0, lnMS, b_hi), (lnMS, t1, b_lo)] if t1 < lnMS < t0 else [(t0, t1, b_hi if t1 >= lnMS else b_lo)]
    for a, c, b in segs:
        n = max(2, int(math.ceil(abs(c - a) / h)))
        dt = (c - a) / n
        for _ in range(n):
            s = rk4_step(g_rhs, s, dt, np.array(b))
    return s


# ----------------------------------------------------------------------------------------------------------------
# SM batched (doublet-RIGHT storage)
# ----------------------------------------------------------------------------------------------------------------
B2 = np.array([[199 / 50, 27 / 10, 44 / 5], [9 / 10, 35 / 6, 12], [11 / 10, 9 / 2, -26]])
CU, CD, CE = np.array([17 / 10, 3 / 2, 2]), np.array([1 / 2, 3 / 2, 2]), np.array([3 / 2, 1 / 2, 0])


def sm_rhs(s, db):
    g, lam, Yu, Yd, Ye, kap, Yn, MR = s
    g1, g2, g3 = g[:, 0], g[:, 1], g[:, 2]
    Uu, Dd, Ee, Nn = H(Yu) @ Yu, H(Yd) @ Yd, H(Ye) @ Ye, H(Yn) @ Yn
    tu, td, te, tn = tr(Uu), tr(Dd), tr(Ee), tr(Nn)
    T = 3 * tu + 3 * td + te + tn
    g1s, g2s, g3s = g1 * g1, g2 * g2, g3 * g3
    b = np.array([41 / 10, -19 / 6, -7]) + db
    gs = g * g
    dg = K1 * b[None, :] * g**3 + K2 * g**3 * (gs @ B2.T - (tu[:, None] * CU + td[:, None] * CD + te[:, None] * CE))
    Gu = 17 / 20 * g1s + 9 / 4 * g2s + 8 * g3s
    Gd = 1 / 4 * g1s + 9 / 4 * g2s + 8 * g3s
    Ge = 9 / 4 * g1s + 9 / 4 * g2s
    Gn = 9 / 20 * g1s + 9 / 4 * g2s
    e = lambda x: x[:, None, None]
    chi4 = 9 / 4 * (3 * tr(Uu @ Uu) + 3 * tr(Dd @ Dd) + tr(Ee @ Ee) - 2 / 3 * tr(Uu @ Dd))
    Y4 = Gu * tu + Gd * td + (3 / 4 * g1s + 3 / 4 * g2s) * te
    Iq = I3[None]
    UuUu, UuDd, DdUu, DdDd, EeEe = Uu @ Uu, Uu @ Dd, Dd @ Uu, Dd @ Dd, Ee @ Ee
    bu = K1 * (1.5 * (Uu - Dd) + e(T - Gu) * Iq) + K2 * (
        1.5 * UuUu - UuDd - 0.25 * DdUu + 11 / 4 * DdDd + e(T) * (5 / 4 * Dd - 9 / 4 * Uu)
        + e(-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 + 1187 / 600 * g1s**2 - 23 / 4 * g2s**2 - 108 * g3s**2
            - 9 / 20 * g1s * g2s + 19 / 15 * g1s * g3s + 9 * g2s * g3s) * Iq
        - e(6 * lam) * Uu + e(223 / 80 * g1s + 135 / 16 * g2s + 16 * g3s) * Uu - e(43 / 80 * g1s - 9 / 16 * g2s + 16 * g3s) * Dd)
    bd = K1 * (1.5 * (Dd - Uu) + e(T - Gd) * Iq) + K2 * (
        1.5 * DdDd - DdUu - 0.25 * UuDd + 11 / 4 * UuUu + e(T) * (5 / 4 * Uu - 9 / 4 * Dd)
        + e(-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 - 127 / 600 * g1s**2 - 23 / 4 * g2s**2 - 108 * g3s**2
            - 27 / 20 * g1s * g2s + 31 / 15 * g1s * g3s + 9 * g2s * g3s) * Iq
        - e(6 * lam) * Dd + e(187 / 80 * g1s + 135 / 16 * g2s + 16 * g3s) * Dd - e(79 / 80 * g1s - 9 / 16 * g2s + 16 * g3s) * Uu)
    be = K1 * (1.5 * (Ee - Nn) + e(T - Ge) * Iq) + K2 * (
        1.5 * EeEe - 9 / 4 * e(T) * Ee
        + e(-chi4 + 1.5 * lam**2 + 5 / 2 * Y4 + 1371 / 200 * g1s**2 - 23 / 4 * g2s**2 + 27 / 20 * g1s * g2s) * Iq
        - e(6 * lam) * Ee + e(387 / 80 * g1s + 135 / 16 * g2s) * Ee)
    dYu = Yu @ bu; dYd = Yd @ bd; dYe = Ye @ be
    dYn = K1 * Yn @ (1.5 * (Nn - Ee) + e(T - Gn) * Iq)
    P = Yn @ H(Yn)
    dM = K1 * (P @ MR + MR @ np.swapaxes(P, 1, 2))
    H4 = 3 * tr(UuUu) + 3 * tr(DdDd) + tr(EeEe) + tr(Nn @ Nn)
    dlam = K1 * (12 * lam**2 - (9 / 5 * g1s + 9 * g2s) * lam + 9 / 4 * (3 / 25 * g1s**2 + 2 / 5 * g1s * g2s + g2s**2)
                 + 4 * lam * T - 4 * H4)
    dk = K1 * (-1.5 * (kap @ Ee + np.swapaxes(Ee, 1, 2) @ kap) + 0.5 * (kap @ Nn + np.swapaxes(Nn, 1, 2) @ kap)
               + e(2 * T + lam - 3 * g2s) * kap)
    return [dg, dlam, dYu, dYd, dYe, dk, dYn, dM]


def takagi_b(A):
    """batched Takagi of symmetric (n,k,k): U^T A U = diag(m) ascending."""
    w, V = np.linalg.eigh(H(A) @ A)
    m = np.sqrt(np.clip(w, 0, None))
    D = np.swapaxes(V, 1, 2) @ A @ V
    d = np.diagonal(D, axis1=1, axis2=2)
    ph = np.exp(-0.5j * np.angle(d))
    return m, V * ph[:, None, :]


def decouple(s, kact, idx):
    """For points idx (with kact[idx] > 0): Takagi the active block, integrate out the heaviest active nu^c."""
    g, lam, Yu, Yd, Ye, kap, Yn, MR = s
    k_before = kact[idx].copy()                 # group BEFORE modifying (one nu^c per point per call)
    for k in (3, 2, 1):
        sel = idx[k_before == k]
        if sel.size == 0:
            continue
        blk = MR[np.ix_(sel, range(k), range(k))]
        m, U = takagi_b(blk)
        Ynb = np.swapaxes(U, 1, 2) @ Yn[sel][:, :k, :]          # rows rotate: Yn_R -> U^T Yn_R
        y = Ynb[:, k - 1, :]                                     # heaviest (ascending)
        kap[sel] = kap[sel] - (y[:, :, None] * y[:, None, :]) / m[:, k - 1][:, None, None]
        Ynb[:, k - 1, :] = 0
        Ynew = Yn[sel].copy(); Ynew[:, :k, :] = Ynb
        Mnew = np.zeros_like(MR[sel])
        for j in range(k - 1):
            Mnew[:, j, j] = m[:, j]
        Yn[sel] = Ynew; MR[sel] = Mnew
        kact[sel] = k - 1
    return [g, lam, Yu, Yd, Ye, kap, Yn, MR], kact


def heaviest_active(MR, kact):
    N = MR.shape[0]
    out = np.full(N, -np.inf)
    for k in (1, 2, 3):
        sel = np.where(kact == k)[0]
        if sel.size:
            out[sel] = np.log(np.abs(MR[sel, k - 1, k - 1]) + 1e-300)
    return out


def run_sm_b(s, vR, h=1.0):
    """v_R -> M_Z with per-point sequential decoupling.  s holds full 3x3 Yn/MR (all active at start)."""
    N = s[0].shape[0]
    kact = np.full(N, 3)
    # Takagi at v_R (diagonalise), decouple those heavier than v_R
    g, lam, Yu, Yd, Ye, kap, Yn, MR = s
    m, U = takagi_b(MR)
    Yn = np.swapaxes(U, 1, 2) @ Yn
    MR = np.zeros_like(MR); MR[:, [0, 1, 2], [0, 1, 2]] = m
    s = [g, lam, Yu, Yd, Ye, kap, Yn, MR]
    tv = math.log(vR)
    for _ in range(3):
        lh = heaviest_active(s[7], kact)
        idx = np.where((kact > 0) & (lh >= tv))[0]
        if idx.size == 0:
            break
        s, kact = decouple(s, kact, idx)
    lnMS = math.log(L.M_S); tZ = math.log(L.MZ)
    nodes = [tv] + ([lnMS] if tZ < lnMS < tv else []) + [tZ]
    for a, c in zip(nodes[:-1], nodes[1:]):
        db = L.B63_SM_SHIFT if 0.5 * (a + c) > lnMS else 0.0
        n = max(2, int(math.ceil(abs(c - a) / h)))
        dt = (c - a) / n
        t = a
        for _ in range(n):
            t_end = t + dt
            rem = np.full(N, dt)
            tcur = np.full(N, t)
            for _sub in range(6):
                lh = heaviest_active(s[7], kact)
                imm = np.where((kact > 0) & (lh >= tcur + 1e-12))[0]      # mass ran above the current scale
                if imm.size:
                    s, kact = decouple(s, kact, imm)
                    lh = heaviest_active(s[7], kact)
                flag = (kact > 0) & (lh < tcur + 1e-12) & (lh > t_end) & (rem < 0)
                if not flag.any():
                    break
                d1 = np.where(flag, lh - tcur, rem)                # partial step to threshold (flagged) / full rest
                s = rk4_step(sm_rhs, s, d1, db)
                tcur = tcur + d1
                rem = rem - d1
                idx = np.where(flag)[0]
                s, kact = decouple(s, kact, idx)
            if np.any(rem < 0):
                s = rk4_step(sm_rhs, s, rem, db)
            t = t_end
    # anything still active (below M_Z) -> decouple
    for _ in range(3):
        idx = np.where(kact > 0)[0]
        if idx.size == 0:
            break
        s, kact = decouple(s, kact, idx)
    return s


# ----------------------------------------------------------------------------------------------------------------
# full chain
# ----------------------------------------------------------------------------------------------------------------
class Exact:
    def __init__(self, setup, tg, typeII=False, data=None, h_g=0.5, h_sm=1.0):
        self.setup = setup; self.tg = tg; self.typeII = typeII
        self.lay = M.Layout(typeII=typeII, free=True)
        self.data = data or setup["data"]
        self.T = np.array([self.data[k][0] for k in L.ALL_KEYS]); self.S = np.array([self.data[k][1] for k in L.ALL_KEYS])
        self.h_g = h_g; self.h_sm = h_sm; self.nev = 0
        self.mask = None

    def run(self, Z):
        Z = np.atleast_2d(Z)
        N = Z.shape[0]
        self.nev += N
        env, vR = self.setup["env"], self.setup["vR"]
        X, lc = Z[:, :-1], Z[:, -1]
        G = M.gut_matrices(X, self.lay, self.tg.sd0, self.tg.se0)
        r = G["r"]; sp = G["s"]; cd126 = 10.0**lc
        rem = 1 - cd126**2 * (1 + np.abs(r * sp)**2)
        ok = rem > 0
        cd10 = np.sqrt(np.clip(rem, 1e-300, None) / (1 + r**2))
        cd10 = np.where(ok, cd10, 1.0); cd126 = np.where(ok, cd126, 1.0)
        Y10 = G["H"] / cd10[:, None, None]; Y126 = G["F"] / cd126[:, None, None]
        gU = np.tile(np.array(env["g_MU"]), (N, 1))
        s = [gU, Y10, Y126, Y10, -3 * Y126, L.C_R * Y126]
        with np.errstate(all="ignore"):
            s = run_g3221_b(s, env["MU"], vR, env["b_lo"], env["b_hi"], self.h_g)
            gq, Yq0, Yq1, Yl0, Yl1, fh = s
            cu10 = (r * cd10)[:, None, None]; cu126 = (r * sp * cd126)[:, None, None]
            c10 = cd10[:, None, None]; c126 = cd126[:, None, None]
            YuL = cu10 * Yq0 + cu126 * Yq1; YdL = c10 * Yq0 + c126 * Yq1
            YeL = c10 * Yl0 + c126 * Yl1; YnL = cu10 * Yl0 + cu126 * Yl1
            MR = vR * fh
            kap0 = np.zeros((N, 3, 3), complex)
            fin = np.all(np.isfinite(MR.reshape(N, -1)), 1) & np.all(np.isfinite(YnL.reshape(N, -1)), 1)
            fin &= np.abs(np.linalg.det(np.where(fin[:, None, None], MR, np.eye(3)))) > 0
            MRs = np.where(fin[:, None, None], MR, np.eye(3))
            if self.typeII:
                kI = -(YnL @ np.linalg.solve(MRs, np.swapaxes(YnL, 1, 2)))
                tc = 10.0**Z[:, 12] * np.exp(1j * Z[:, 13]) * np.linalg.norm(kI, axis=(1, 2)) / np.linalg.norm(Yq1, axis=(1, 2))
                kap0 = tc[:, None, None] * Yq1
            gsm = np.tile(np.array(env["g_sm_vR"]), (N, 1)); lam = np.full(N, env["lam_vR"])
            Yn_R = np.swapaxes(np.where(fin[:, None, None], YnL, 0), 1, 2)
            st = [gsm, lam, np.swapaxes(YuL, 1, 2), np.swapaxes(YdL, 1, 2), np.swapaxes(YeL, 1, 2), kap0, Yn_R, MRs]
            st = [np.where(np.isfinite(a), a, 0) if a.ndim > 1 else a for a in st]
            st = run_sm_b(st, vR, self.h_sm)
        g, lam, YuR, YdR, YeR, kap, Yn, MRf = st
        return np.swapaxes(YuR, 1, 2), np.swapaxes(YdR, 1, 2), np.swapaxes(YeR, 1, 2), kap * L.VEV**2, ok & fin

    def obs(self, Z):
        Yu, Yd, Ye, mnu, ok = self.run(Z)
        N = Yu.shape[0]
        with np.errstate(all="ignore"):
            Yb = np.stack([Yu, Yd, Ye], 1)
            fin = ok & np.all(np.isfinite(Yb.reshape(N, -1)), 1) & np.all(np.isfinite(mnu.reshape(N, -1)), 1)
            fin &= (np.abs(mnu).reshape(N, -1).max(1) > 0) & (np.abs(Yb).reshape(N, -1).max(1) < 1e6)
            Yb = np.where(fin[:, None, None, None], Yb, np.eye(3)); mnu = np.where(fin[:, None, None], mnu, np.eye(3))
            w, E = np.linalg.eigh(Yb @ H(Yb))
            sv = np.sqrt(np.clip(w, 0, None)) * L.VEV
            V = np.swapaxes(E[:, 0], 1, 2) @ np.conj(E[:, 1])
            c12, c23, c13, cd = L.angles_b(V)
            wn, Nv = np.linalg.eigh(H(mnu) @ mnu)
            mn = np.sqrt(np.clip(wn, 0, None))
            U = np.swapaxes(E[:, 2], 1, 2) @ Nv
            n12, n23, n13, nd = L.angles_b(U)
        o = np.zeros((N, 18))
        o[:, 0:3] = sv[:, 0]; o[:, 3:6] = sv[:, 1]; o[:, 6:9] = sv[:, 2]
        o[:, 9] = c12; o[:, 10] = c23; o[:, 11] = c13; o[:, 12] = cd
        o[:, 13] = n12**2; o[:, 14] = n23**2; o[:, 15] = n13**2
        o[:, 16] = (mn[:, 1]**2 - mn[:, 0]**2) * 1e18; o[:, 17] = (mn[:, 2]**2 - mn[:, 0]**2) * 1e18
        return o, fin, dict(U=U, mn=mn, delta_pmns=nd)

    def resid(self, Z):
        o, fin, _ = self.obs(Z)
        T, S = self.T, self.S
        N = o.shape[0]
        R = np.empty((N, 18))
        with np.errstate(all="ignore"):
            for i, k in enumerate(L.ALL_KEYS):
                if k in L.MASS_KEYS:
                    R[:, i] = np.log(np.clip(o[:, i], 1e-300, None) / T[i]) * T[i] / S[i]
                elif k == "delta":
                    R[:, i] = ((np.abs(o[:, i]) - T[i] + math.pi) % (2 * math.pi) - math.pi) / S[i]
                else:
                    R[:, i] = (o[:, i] - T[i]) / S[i]
        R[o[:, 17] <= 0] += 1e3
        R = np.where(np.isfinite(R), R, 1e3)
        R[~fin] = 1e3
        if self.mask is not None:
            R = R * (~self.mask)
        return R

    def chi2(self, Z):
        R = self.resid(Z)
        return np.sum(R * R, axis=1)
