"""Map a proxy minimum to an exact top-down starting point by inverting the G3221 quark-sector transfer:
choose GUT inputs (Y10, Y126) such that the exact v_R-level quark Yukawas equal the proxy's v_R-level quark Yukawas
(eta_q * proxy matrices), iterating the (weakly input-dependent) transfer maps; then express the GUT matrices in the
top-down parametrisation (basis rotation by Takagi of Yd, W decomposition)."""
import math
import numpy as np
import lib_r2c as L
import model_r2c as M
import lrg


def w_decompose(W):
    A = np.abs(W)
    s13 = min(A[0, 2], 1.0); th13 = math.asin(s13); c13 = math.cos(th13)
    th12 = math.asin(min(A[0, 1] / c13, 1.0)); th23 = math.asin(min(A[1, 2] / c13, 1.0))
    _, _, _, dl = L.angles_b(W[None])
    d = float(dl[0])
    b3 = float(np.angle(W[2, 2]))
    a2 = float(np.angle(W[1, 2])) - b3
    a1 = float(np.angle(W[0, 2])) + d - b3
    b1 = float(np.angle(W[0, 0])) - a1
    b2 = float(np.angle(W[0, 1])) - a1
    p = np.array([th12, th13, th23, d, a1, a2, b1, b2, b3])
    Wr = M.W_batch(np.concatenate([p, [0, 0, 0]])[None])[0]
    return p, float(np.abs(Wr - W).max())


def matrices_to_x(Yd, Ye, r, s, tg, typeII_t=None):
    """GUT-scale Yd = H + F, Ye = H - 3F (complex symmetric, any basis) -> free-layout x (offsets w.r.t. tg)."""
    md, U = L.takagi(Yd)                       # U^T Yd U = diag(md) ascending
    Yep = U.T @ Ye @ U
    me, V = L.takagi(Yep)                      # V^T Ye' V = diag(me)  ->  Ye' = V^* diag V^dag  ->  W = V^*
    W = V.conj()
    p, err = w_decompose(W)
    core = list(p) + [math.log10(r), math.log10(abs(s)), float(np.angle(s))]
    if typeII_t is not None:
        core += list(typeII_t)
    off = list(np.log(md / tg.sd0)) + list(np.log(me / tg.se0))
    return np.array(core + off), err


def proxy_to_exact(setup, tg, x_proxy, typeII=False, lc=None, iters=6, verbose=False):
    lay_p = M.Layout(typeII=typeII)
    G = M.gut_matrices(np.atleast_2d(x_proxy), lay_p, tg.sd0, tg.se0)
    Hp, Fp = G["H"][0], G["F"][0]
    r = float(G["r"][0]); s = complex(G["s"][0])
    if lc is None:
        _, _, aux = M.proxy_eval(np.atleast_2d(x_proxy), lay_p, tg, want_obs=True)
        lc = math.log10(float(aux["rho_eff"][0]) * 1e-9 * L.C_R * setup["vR"] / L.VEV**2)
    comp = M.composition(r, s, 10.0**lc)
    if comp is None:
        return None
    cd10, cd126, cu10, cu126 = comp["c_d10"], comp["c_d126"], comp["c_u10"], comp["c_u126"]
    eq = tg.info["eta"]["q"]
    Yu_t = r * (Hp + s * Fp) / eq; Yd_t = (Hp + Fp) / eq     # v_R-level = M_U-equivalent / eta_q
    det = cu10 * cd126 - cu126 * cd10
    Yq0_t = (cd126 * Yu_t - cu126 * Yd_t) / det
    Yq1_t = (-cd10 * Yu_t + cu10 * Yd_t) / det
    env = setup["env"]; vR = setup["vR"]
    Y10, Y126 = Yq0_t * eq, Yq1_t * eq
    err = None
    for it in range(iters):
        gm = lrg.g3221_maps(np.array(env["g_MU"]), [Y10, Y126], [Y10, -3 * Y126], L.C_R * Y126, env["MU"], vR, env["b_lo"], env["b_hi"])
        err = max(np.abs(gm["Yq"][0] - Yq0_t).max() / np.abs(Yq0_t).max(), np.abs(gm["Yq"][1] - Yq1_t).max() / np.abs(Yq1_t).max())
        if verbose:
            print(f"      inverse it {it}: rel err {err:.2e}")
        if err < 1e-12:
            break
        Li = np.linalg.inv(gm["Lq"])
        Yt = [Li @ Yq0_t @ Li.T, Li @ Yq1_t @ Li.T]
        Oi = np.linalg.inv(gm["Oq"])
        Y10 = Yt[0] * Oi[0, 0] + Yt[1] * Oi[1, 0]
        Y126 = Yt[0] * Oi[0, 1] + Yt[1] * Oi[1, 1]
        Y10 = 0.5 * (Y10 + Y10.T); Y126 = 0.5 * (Y126 + Y126.T)
    H = cd10 * Y10; F = cd126 * Y126
    tII = list(np.atleast_2d(x_proxy)[0, 12:14]) if typeII else None
    x, werr = matrices_to_x(H + F, H - 3 * F, r, s, tg, tII)
    return {"x": x, "lc": lc, "inverse_rel_err": err, "w_err": werr}
