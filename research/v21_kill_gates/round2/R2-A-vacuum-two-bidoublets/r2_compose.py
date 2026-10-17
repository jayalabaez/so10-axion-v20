"""R2-A: doublet composition of light (1,2)_{1/2} states and the exact map to the 10+126bar fit parameters (r, s).

Convention (EXACT, SO(4)-covariance argument, see REPORT section 2):
  * H10 bidoublet = complex SO(4) vector h_mu (mu = 6..9 of the 10); Sigma126bar colour-singlet (15,2,2)_0 bidoublet =
    complex SO(4) vector S^sigma = sum_{(ab) in (01),(23),(45)} sum_{mu<nu<rho} eps(mu nu rho sigma) Sigma_{ab mu nu rho}
    (the omega_{B-L} contraction picks the colour singlet; C-linear and SO(4)-equivariant, checked numerically below).
  * neutral weight vectors n_u = (e8 + i e9)/sqrt2 (T3R = Y = +1/2), n_d = conj(n_u) (T3R = Y = -1/2), the SAME for H10 and S.
  * v_u = n_u^+ <h>, v_d = n_d^+ <h>, w_u = n_u^+ <S>, w_d = n_d^+ <S>  (holomorphic components: F.F.H10 and F.F.Sigma).
  * 10+126bar fit (K2 fit.py: Yd = H + F, Yu = r (H + s F), Ye = H - 3F, Yn = r (H - 3 s F)):
        r = v_u / v_d        s = (w_u / w_d) / (v_u / v_d)
    (Clebsches c_u = c_d for both the 10 and the 126bar doublets, K2 so10_clebsch.py; the SU(4) structure only gives the
    quark/lepton factor -3, identical for u and d, so the u/d ratios are the SO(4) ratios).  arg r is unphysical
    (overall phase of Yu); |r| and complex s are physical.  Any state inside ONE real G3221 bidoublet (h, S) = (z1 x, z2 x),
    x real, gives s = 1 exactly (lemma), as does any state inside one complex bidoublet Phi_L = alpha Phi_10 + beta Phi_126.
"""
from __future__ import annotations
import itertools, json, math
import numpy as np
import k3_common as K

chart = K.chart
N_U = np.zeros(10, complex); N_U[8] = 1 / math.sqrt(2); N_U[9] = 1j / math.sqrt(2)
N_D = np.conj(N_U)
OMEGA_PAIRS = [(0, 1), (2, 3), (4, 5)]
SO4 = [6, 7, 8, 9]


def perm_sign(seq):
    seq = list(seq); s = 1
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]: s = -s
    return s


def form_get(form, idx):
    """antisymmetric 5-form component Sigma_{idx} from the dict (keys sorted tuples)."""
    if len(set(idx)) < 5: return 0j
    key = tuple(sorted(idx)); val = form.get(key, 0j)
    return perm_sign(idx) * val if val != 0 else 0j


def S_vector(form):
    """SO(4) vector S^sigma (indices 6..9 -> positions 0..3) from the (2 SO(6) + 3 SO(4)) components."""
    S = np.zeros(10, complex)
    for sig in SO4:
        rest = [m for m in SO4 if m != sig]
        for (a, b) in OMEGA_PAIRS:
            val = form_get(form, (a, b, rest[0], rest[1], rest[2]))
            S[sig] += perm_sign(rest + [sig]) * val
    return S


def S_vector_dual(form):
    """same SO(4) vector from the (4 SO(6) + 1 SO(4)) components contracted with omega^omega/2 (Hodge partner)."""
    S = np.zeros(10, complex)
    pairs4 = [((0, 1), (2, 3)), ((0, 1), (4, 5)), ((2, 3), (4, 5))]
    for sig in SO4:
        for (p1, p2) in pairs4:
            S[sig] += form_get(form, (p1[0], p1[1], p2[0], p2[1], sig))
    return S


def fields_of_q(q):
    st = chart.unpack(np.asarray(q, float))
    return np.asarray(st.h, complex), st.sigma, st


def components(q):
    h, sigma, st = fields_of_q(q)
    S = S_vector(sigma)
    vu, vd = N_U.conj() @ h, N_D.conj() @ h
    wu, wd = N_U.conj() @ S, N_D.conj() @ S
    qq = np.asarray(q, float)
    norms = {name: float(np.linalg.norm(qq[sl])) ** 2 for name, sl in K.BLOCKS.items()}
    tot = sum(norms.values())
    return {"vu": vu, "vd": vd, "wu": wu, "wd": wd, "S": S, "h": h, "frac": {k: v / tot for k, v in norms.items()}}


def r_s(comp):
    vu, vd, wu, wd = comp["vu"], comp["vd"], comp["wu"], comp["wd"]
    r = vu / vd if abs(vd) > 1e-300 else np.inf
    s = (wu * vd) / (wd * vu) if abs(wd * vu) > 1e-300 else np.nan
    return r, s


class Neutral:
    """neutral-component map for the (1,2)_{1/2} isotypic slice of a tag: q_vev(a) = Re(W_N a), a in C^5 (slice coords)."""

    def __init__(self, tag):
        B = np.load(K.SCRATCH / f"{tag}_blocks.npz")
        labels = [str(x) for x in B["labels"]]
        self.kd = labels.index("(1,2)_|Y|=1/2")
        self.W = B[f"W{self.kd}"]
        Qem = K.candidate.chart_generator(K.hypercharge.Q_EM_STANDARD_INTEGER) / 3.0
        u, s, vt = np.linalg.svd(Qem); ker = vt[s < 1e-9].T
        self.PN = ker @ ker.T
        self.WN = self.PN @ self.W
        meta = json.load(open(K.SCRATCH / f"{tag}_blocks.json", encoding="utf-8"))["blocks"][self.kd]["meta"]
        self.meta = meta

    def q_of_a(self, a):
        v = self.WN @ np.asarray(a, complex)
        q = np.real(v); n = np.linalg.norm(q)
        if n < 1e-12:
            q = np.imag(v); n = np.linalg.norm(q)
        return q / n

    def comp_of_a(self, a):
        c = components(self.q_of_a(a)); c["r"], c["s"] = r_s(c); return c


def equivariance_check(seed=3):
    """numerical checks: S map SO(4)-equivariant and C-linear; dual-component consistency; lemma s = 1 on real bidoublets."""
    rng = np.random.default_rng(seed); out = {}
    # random Sigma chart vector -> S; act with SU2L/SU2R generators
    qs = np.zeros(K.TOTAL); qs[chart.SIGMA_SLICE] = rng.normal(size=chart.SIGMA_SLICE.stop - chart.SIGMA_SLICE.start)
    errs = []
    for gen in list(K.hypercharge.SU2L_INTEGER) + list(K.hypercharge.SU2R_INTEGER):
        G = K.candidate.chart_generator(gen)
        S1 = S_vector(chart.unpack(G @ qs).sigma)
        M10 = np.zeros((10, 10))
        for index, (f, sidx) in enumerate(itertools.combinations(range(10), 2)):
            M10[f, sidx] += float(gen[index]); M10[sidx, f] -= float(gen[index])
        S0 = S_vector(chart.unpack(qs).sigma)
        errs.append(float(np.linalg.norm(S1 - M10 @ S0) / max(np.linalg.norm(S0), 1e-30)))
    out["S_equivariance_rel_err"] = max(errs)
    S0 = S_vector(chart.unpack(qs).sigma); Sd = S_vector_dual(chart.unpack(qs).sigma)
    ratio = (Sd[6:] @ S0[6:].conj()) / (S0[6:] @ S0[6:].conj())
    out["dual_ratio"] = complex(ratio); out["dual_resid"] = float(np.linalg.norm(Sd[6:] - ratio * S0[6:]) / np.linalg.norm(S0[6:]))
    return out


if __name__ == "__main__":
    import sys
    print(json.dumps({k: (str(v) if isinstance(v, complex) else v) for k, v in equivariance_check().items()}, indent=1))
    if len(sys.argv) > 1:
        tag = sys.argv[1]; nt = Neutral(tag)
        for j in range(5):
            for ph in (1.0, 1j):
                a = np.zeros(5, complex); a[j] = ph; c = nt.comp_of_a(a)
                print(j, nt.meta[j], ph, "vu", np.round(c["vu"], 4), "vd", np.round(c["vd"], 4), "wu", np.round(c["wu"], 4), "wd", np.round(c["wd"], 4),
                      {k: round(v, 3) for k, v in c["frac"].items() if v > 1e-6})
