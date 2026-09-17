"""Generalised minimal SO(10) 10+126 Yukawa fit with running, CKM and sum rules.

Relative to flavour_clebsch_fit_v20 (which fixes M_u = tan(beta) * M_d, i.e.
the degenerate case with identical 10/126 doublet vev ratios, predicting
V_CKM = 1 and m_u/m_d = m_c/m_s = m_t/m_b), this uses the general structure of
the minimal Yukawa sector with independent doublet vev ratios:

  at mu = M_I (Pati-Salam relations; mass units with tree vevs)
    M_d = H + F                 M_e = H - 3F
    M_u = r_H H + r_F F         M_D = r_H H - 3 r_F F
    M_R = (v_R rho / v_d) F     M_L = eps F             (Type-II)
    m_nu = M_L - M_D M_R^-1 M_D^T

  r_H = v10^u/v10^d  (real > 0),   r_F = v126^u/v126^d  (complex),
  rho = v_d/|v126^d| >= 1.
  Vev sum rules:  |v10^d|^2+|v126^d|^2 <= v_d^2,  |v10^u|^2+|v126^u|^2 <= v_u^2.
  Perturbativity: |Y10|,|Y126| <= Y_MAX.

Charged fermion masses and CKM are run M_Z -> M_I (2HDM-II, rg.py, validated to
<1.6% against Huang and Zhou 2021); the light neutrino matrix is run M_I -> M_Z.
"""
from __future__ import annotations

import math
import sys

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import flavour_clebsch_fit_v20 as R  # noqa: E402
import rg  # noqa: E402

NUFIT = R.NUFIT
PLANCK, DESI = 0.12, 0.072
NPAR = 17
NRES = 19


def _takagi(M):
    return R.takagi(0.5 * (M + M.T))


class Stratum:
    """RG-dependent data for a fixed (tan beta, v_R)."""

    def __init__(self, tan_beta, v_r, lam2=0.5, floor=0.05, s12_floor=0.01,
                 y_max=3.0, planck=True):
        self.tb, self.v_r, self.y_max, self.planck = tan_beta, v_r, y_max, planck
        run = rg.run(v_r, tan_beta=tan_beta, mode="2hdm", lam2=lam2)
        self.run = run
        self.m = run["masses"]
        self.vu, self.vd = run["vu"], run["vd"]
        self.ckm = run["ckm_high"]
        self.nu_scale, self.nu_f = run["nu_scale"], run["nu_flavour"]

        def rel(k):
            return max(rg.REL_ERR_MZ[k], floor)

        self.sig_up = {k: rel(k) * self.m[k] for k in ("u", "c", "t")}
        self.rel_down = {k: rel(k) for k in ("d", "s", "b")}
        lo = rg.CKM_LOW
        self.sig_ckm = {
            "s12": max(lo["s12"][1] / lo["s12"][0], s12_floor) * self.ckm["s12"],
            "s23": max(lo["s23"][1] / lo["s23"][0], floor) * self.ckm["s23"],
            "s13": max(lo["s13"][1] / lo["s13"][0], floor) * self.ckm["s13"],
            "J": max(lo["J"][1] / lo["J"][0], floor) * self.ckm["J"],
        }
        self.run_ok = run["yukawas_max"] < y_max
        self.me_diag = np.diag([self.m["e"], self.m["mu"], self.m["tau"]]).astype(complex)

    def build(self, p):
        def s(x):
            return 0.5 * (1.0 + math.tanh(x))

        z = p[14:17]
        md = np.diag([self.m["d"] * (1 + self.rel_down["d"] * z[0]),
                      self.m["s"] * (1 + self.rel_down["s"] * z[1]),
                      self.m["b"] * (1 + self.rel_down["b"] * z[2])]).astype(complex)
        rot = R._rotation(s(p[0]), s(p[1]), s(p[2]), p[3])
        left = np.diag([1.0, np.exp(1j * p[4]), np.exp(1j * p[5])])
        de = np.diag([self.m["e"] * np.exp(1j * p[6]),
                      self.m["mu"] * np.exp(1j * p[7]),
                      self.m["tau"] * np.exp(1j * p[8])])
        v = left @ rot
        me = v @ de @ v.T
        H = (3.0 * md + me) / 4.0
        F = (md - me) / 4.0
        r_h = math.exp(p[9])
        r_f = math.exp(p[10]) * np.exp(1j * p[11])
        rho = 1.0 + math.exp(p[12])
        eps = 10.0 ** p[13]
        mu = r_h * H + r_f * F
        m_dirac = r_h * H - 3.0 * r_f * F
        m_r = (self.v_r * rho / self.vd) * F
        m_l = eps * F
        mnu = m_l - m_dirac @ np.linalg.solve(m_r, m_dirac.T)
        return {"md": md, "me": me, "H": H, "F": F, "mu": mu, "mD": m_dirac,
                "mR": m_r, "mnu": 0.5 * (mnu + mnu.T), "rH": r_h, "rF": r_f,
                "rho": rho, "eps": eps}

    def observables(self, p):
        b = self.build(p)
        su, vu = _takagi(b["mu"])
        c = vu.conj().T
        ckm = {"s12": abs(c[0, 1]), "s23": abs(c[1, 2]), "s13": abs(c[0, 2]),
               "J": abs(np.imag(c[0, 1] * c[1, 2] * np.conj(c[0, 2]) * np.conj(c[1, 1])))}
        _, ve = _takagi(b["me"])
        mprime = ve.conj().T @ b["mnu"] @ ve.conj()
        f = self.nu_f
        mz = self.nu_scale * (np.outer(f, f) * mprime)
        lep = R._pmns_from_matrices(0.5 * (mz + mz.T), self.me_diag)
        rho, r_h, r_f = b["rho"], b["rH"], abs(b["rF"])
        y126 = rho * np.max(np.abs(b["F"])) / self.vd
        x_lo = np.max(np.abs(b["H"])) / (self.y_max * self.vd)
        up_room = self.tb ** 2 - r_f ** 2 / rho ** 2
        x_hi = min(math.sqrt(max(0.0, 1.0 - 1.0 / rho ** 2)),
                   math.sqrt(max(0.0, up_room)) / r_h)
        return {"up": {"u": su[0], "c": su[1], "t": su[2]}, "ckm": ckm, "lep": lep,
                "y126": y126, "x_lo": x_lo, "x_hi": x_hi, "build": b}

    def residuals(self, p):
        try:
            o = self.observables(p)
        except Exception:
            return np.full(NRES, 1e4)
        r = []
        for k in ("u", "c", "t"):
            r.append((o["up"][k] - self.m[k]) / self.sig_up[k])
        for k in ("s12", "s23", "s13", "J"):
            r.append((o["ckm"][k] - self.ckm[k]) / self.sig_ckm[k])
        lep = o["lep"]
        for key, obs in (("sin2_th12", "sin2_th12"), ("sin2_th23", "sin2_th23"),
                         ("sin2_th13", "sin2_th13"), ("dm21", "dm21_eV2"),
                         ("dm31", "dm31_eV2")):
            c, sg = NUFIT[key]
            r.append((lep[obs] - c) / sg)
        c, sg = NUFIT["delta_deg"]
        r.append(((lep["delta_cp_deg"] - c + 180.0) % 360.0 - 180.0) / sg)
        r.extend(list(p[14:17]))
        r.append(math.sqrt(1e5) * max(0.0, lep["sum_mnu_eV"] - PLANCK) if self.planck else 0.0)
        r.append(1e2 * max(0.0, o["y126"] - self.y_max))
        r.append(1e2 * max(0.0, o["x_lo"] - o["x_hi"]))
        r = np.asarray(r, dtype=float)
        return np.where(np.isfinite(r), r, 1e4)

    def chi2_parts(self, p):
        r = self.residuals(p)
        return {"chi2_total": float(r @ r),
                "chi2_fermion": float(r[:13] @ r[:13]),
                "chi2_nuisance": float(r[13:16] @ r[13:16]),
                "penalty": float(r[16:] @ r[16:])}


def random_start(rng):
    p = np.empty(NPAR)
    p[0:3] = rng.normal(scale=1.5, size=3)
    p[3:9] = rng.uniform(0, 2 * math.pi, size=6)
    p[9] = rng.uniform(-3, 5)
    p[10] = rng.uniform(-3, 6)
    p[11] = rng.uniform(0, 2 * math.pi)
    p[12] = rng.uniform(-3, 3)
    p[13] = rng.uniform(-14, -8)
    p[14:17] = rng.normal(scale=0.5, size=3)
    return p


if __name__ == "__main__":
    import time
    st = Stratum(10.0, 6.313855e11)
    print("stratum tanb=10, v_R=6.31e11 GeV")
    print("  masses at M_I:", {k: f"{v:.4g}" for k, v in st.m.items()})
    print("  CKM at M_I   :", {k: f"{v:.5g}" for k, v in st.ckm.items()})
    print("  nu running   : scale", round(st.nu_scale, 4), " flavour", np.round(st.nu_f, 5))
    rng = np.random.default_rng(1)
    p = random_start(rng)
    t = time.time()
    for _ in range(300):
        st.residuals(p)
    print("  residual eval: %.2f ms" % ((time.time() - t) / 300 * 1000))
    p[10] = p[9]
    p[11] = 0.0
    b = st.build(p)
    print("  degenerate limit r_F=r_H -> ||M_u - r_H M_d|| =",
          float(np.linalg.norm(b["mu"] - b["rH"] * b["md"])))
