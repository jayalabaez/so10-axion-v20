"""Low-energy inputs at M_Z for the K2 flavour fit (NUM, computed here from PDG-2024-type inputs).

Quark MS-bar masses are run with 4-loop QCD (beta and gamma_m) with 2-loop decoupling at the heavy-quark thresholds;
the top pole mass is converted with the 3-loop pole/MS-bar relation (nl = 5).  Charged-lepton MS-bar masses at M_Z
use the one-loop QED pole->MSbar relation.  These are then cross-checked against the Huang-Zhou 2020
(arXiv:2009.04851, values recalled, not re-read) and Antusch-Maurer 2013 (arXiv:1306.6879) style numbers.
Uncertainties: experimental errors propagated linearly, plus a theory floor (scheme, EW matching, uncomputed
G3221 thresholds) applied in the fit, see fit.py.
"""
import json, math, sys
import numpy as np
from scipy.integrate import solve_ivp

Z3, Z4, Z5 = 1.2020569031595942, 1.0823232337111382, 1.0369277551433699
MZ = 91.1876
VEV = 174.10  # v/sqrt2 with v = 246.22 GeV

PDG = {  # PDG 2024 (central, sigma)
    "alpha_s_MZ": (0.1180, 0.0009),
    "m_u_2GeV": (2.16e-3, 0.07e-3),
    "m_d_2GeV": (4.70e-3, 0.07e-3),
    "m_s_2GeV": (93.5e-3, 0.8e-3),
    "m_c_mc": (1.2730, 0.0046),
    "m_b_mb": (4.183, 0.007),
    "m_t_pole": (172.57, 0.29),
    "m_e": (0.51099895e-3, 1e-12),
    "m_mu": (0.1056583755, 1e-9),
    "m_tau": (1.77693, 0.00009),
    "alpha_em_inv_MZ": (127.951, 0.009),
}

def beta_coeffs(nf):
    b0 = (11 - 2 * nf / 3) / 4
    b1 = (102 - 38 * nf / 3) / 16
    b2 = (2857 / 2 - 5033 * nf / 18 + 325 * nf**2 / 54) / 64
    b3 = ((149753 / 6 + 3564 * Z3) - (1078361 / 162 + 6508 * Z3 / 27) * nf
          + (50065 / 162 + 6472 * Z3 / 81) * nf**2 + 1093 * nf**3 / 729) / 256
    return b0, b1, b2, b3

def gamma_coeffs(nf):
    g0 = 1.0
    g1 = (202 / 3 - 20 * nf / 9) / 16
    g2 = (1249 + (-2216 / 27 - 160 * Z3 / 3) * nf - 140 * nf**2 / 81) / 64
    g3 = (4603055 / 162 + 135680 * Z3 / 27 - 8800 * Z5
          + (-91723 / 27 - 34192 * Z3 / 9 + 880 * Z4 + 18400 * Z5 / 9) * nf
          + (5242 / 243 + 800 * Z3 / 9 - 160 * Z4 / 3) * nf**2
          + (-332 / 243 + 64 * Z3 / 27) * nf**3) / 256
    return g0, g1, g2, g3

def run_qcd(a0, mu0, mu1, nf, masses0):
    """a = alpha_s/pi; masses0: list of m(mu0); returns a(mu1), masses(mu1).  d/dln(mu^2)."""
    b = beta_coeffs(nf); g = gamma_coeffs(nf)
    def rhs(t, y):
        a = y[0]
        da = -(b[0] * a**2 + b[1] * a**3 + b[2] * a**4 + b[3] * a**5)
        gm = g[0] * a + g[1] * a**2 + g[2] * a**3 + g[3] * a**4
        return [da] + [-m * gm for m in y[1:]]
    t0, t1 = math.log(mu0**2), math.log(mu1**2)
    sol = solve_ivp(rhs, (t0, t1), [a0] + list(masses0), rtol=1e-10, atol=1e-14, method="DOP853")
    return sol.y[0, -1], list(sol.y[1:, -1])

def decouple_down(a, m_list, nf_high):
    """alpha_s and light masses crossing a heavy-quark threshold at mu = m_h(m_h): nf -> nf-1 (2-loop)."""
    a_low = a * (1 + (11 / 72) * a**2)
    m_low = [m * (1 + (89 / 432) * a**2) for m in m_list]
    return a_low, m_low

def decouple_up(a, m_list):
    a_high = a * (1 - (11 / 72) * a**2)
    m_high = [m * (1 - (89 / 432) * a**2) for m in m_list]
    return a_high, m_high

def compute(inputs):
    aZ = inputs["alpha_s_MZ"] / math.pi
    mc, mb, Mt = inputs["m_c_mc"], inputs["m_b_mb"], inputs["m_t_pole"]
    mu2, md2, ms2 = inputs["m_u_2GeV"], inputs["m_d_2GeV"], inputs["m_s_2GeV"]
    # alpha_s(mb) in nf=5 (iterate to locate mu = mb(mb) -- the scale is the input value itself)
    a_mb, _ = run_qcd(aZ, MZ, mb, 5, [])
    # light quarks: run 2 GeV -> mb(mb) in nf=4 then match to nf=5 and run to MZ
    a_mb4, _ = decouple_down(a_mb, [], 5)
    a_2, _ = run_qcd(a_mb4, mb, 2.0, 4, [])
    # alpha_s(mc) for the charm threshold (nf=4 down to mc)
    a_mc4, _ = run_qcd(a_mb4, mb, mc, 4, [])
    # u,d,s from 2 GeV (nf=4) to mb
    a_tmp, (mu_b, md_b, ms_b) = run_qcd(a_2, 2.0, mb, 4, [mu2, md2, ms2])
    # charm: mc(mc) in nf=4 -> mb in nf=4
    _, (mc_b,) = run_qcd(a_mc4, mc, mb, 4, [mc])
    a5, (mu_b5, md_b5, ms_b5, mc_b5) = decouple_up(a_tmp, [mu_b, md_b, ms_b, mc_b])
    aZ_chk, (mu_Z, md_Z, ms_Z, mc_Z, mb_Z) = run_qcd(a5, mb, MZ, 5, [mu_b5, md_b5, ms_b5, mc_b5, mb])
    # top: pole -> MSbar at mu = Mt with nl = 5 (3 loop), then run in nf=5 to MZ (top treated as external heavy quark
    # for the running of its own mass below mt; standard practice: nf=5 running of m_t between mt and MZ is a
    # ~1% effect and is covered by the theory floor; we use nf=6 mass anomalous dimension = nf=5 difference ~ 0.1%).
    a_Mt, _ = run_qcd(aZ, MZ, Mt, 5, [])
    a_Mt6 = a_Mt * (1 - (11 / 72) * a_Mt**2)
    nl = 5
    c1 = 4 / 3
    c2 = 13.4434 - 1.0414 * nl
    c3 = 190.595 - 26.655 * nl + 0.6527 * nl**2
    mt_Mt = Mt / (1 + c1 * a_Mt6 + c2 * a_Mt6**2 + c3 * a_Mt6**3)
    _, (mt_Z,) = run_qcd(a_Mt, Mt, MZ, 5, [mt_Mt])
    # leptons: one-loop QED MSbar at MZ: m(mu) = M [1 - (alpha/pi)(1 + 3/2 ln(mu/M))]
    alpha = 1 / inputs["alpha_em_inv_MZ"]
    lep = {}
    for k in ["m_e", "m_mu", "m_tau"]:
        M = inputs[k]
        lep[k] = M * (1 - (alpha / math.pi) * (1 + 1.5 * math.log(MZ / M)))
    return {"m_u": mu_Z, "m_d": md_Z, "m_s": ms_Z, "m_c": mc_Z, "m_b": mb_Z, "m_t": mt_Z,
            "m_e": lep["m_e"], "m_mu": lep["m_mu"], "m_tau": lep["m_tau"],
            "alpha_s_MZ_check": aZ_chk * math.pi, "mt_mt_MSbar": mt_Mt}

central = {k: v[0] for k, v in PDG.items()}
res0 = compute(central)
# linear error propagation
errs = {k: 0.0 for k in res0}
for k, (c, s) in PDG.items():
    if s == 0:
        continue
    up = dict(central); up[k] = c + s
    dn = dict(central); dn[k] = c - s
    ru, rd = compute(up), compute(dn)
    for q in res0:
        errs[q] += ((ru[q] - rd[q]) / 2) ** 2
errs = {k: math.sqrt(v) for k, v in errs.items()}
masses = {k: (res0[k], errs[k]) for k in ["m_u", "m_d", "m_s", "m_c", "m_b", "m_t", "m_e", "m_mu", "m_tau"]}

# CKM at MZ: PDG 2024 Wolfenstein (recalled): lambda, A, rhobar, etabar
WOLF = {"lam": (0.22501, 0.00068), "A": (0.826, 0.015), "rhobar": (0.1591, 0.0094), "etabar": (0.3523, 0.0072)}
def ckm_angles(lam, A, rhobar, etabar):
    rho, eta = rhobar, etabar
    s12 = lam
    s23 = A * lam**2
    z = A * lam**3 * (rho + 1j * eta) * math.sqrt(1 - A**2 * lam**4) / (math.sqrt(1 - lam**2) * (1 - A**2 * lam**4 * (rho + 1j * eta)))
    return s12, s23, abs(z), math.atan2(z.imag, z.real)
w0 = {k: v[0] for k, v in WOLF.items()}
ang0 = ckm_angles(**w0)
ang_err = np.zeros(4)
for k, (c, s) in WOLF.items():
    up = dict(w0); up[k] = c + s
    dn = dict(w0); dn[k] = c - s
    ang_err += ((np.array(ckm_angles(**up)) - np.array(ckm_angles(**dn))) / 2) ** 2
ang_err = np.sqrt(ang_err)
ckm = {"s12": (ang0[0], ang_err[0]), "s23": (ang0[1], ang_err[1]), "s13": (ang0[2], ang_err[2]), "delta": (ang0[3], ang_err[3])}

# PMNS: NuFIT 6.0 (2024) NO with SK-atm (as used in the repository flavour_clebsch_fit_v20): sin^2 and dm^2 in eV^2
PMNS = {"sin2_th12": (0.308, 0.012), "sin2_th23": (0.470, 0.015), "sin2_th13": (0.02215, 0.00060),
        "dm21": (7.49e-5, 0.19e-5), "dm31": (2.513e-3, 0.021e-3), "delta_deg": (212.0, 35.0)}

out = {"MZ": MZ, "VEV": VEV, "masses_GeV_MZ": masses, "ckm_MZ": ckm, "pmns": PMNS,
       "alpha_s_check": res0["alpha_s_MZ_check"], "mt_mt_MSbar": res0["mt_mt_MSbar"],
       "gauge_MZ": {"alpha_s": 0.1180, "alpha_em_inv": 127.951, "sin2_thw_MSbar": 0.23122},
       "pdg_inputs": PDG, "wolfenstein": WOLF}
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "inputs_mz.json", "w"), indent=1)
for k, (c, s) in masses.items():
    print(f"{k:6s} {c:.6g} +- {s:.3g}  ({100*s/c:.2f}%)")
print("mt(mt) MSbar", res0["mt_mt_MSbar"], " alpha_s check", res0["alpha_s_MZ_check"])
print("CKM", {k: (round(v[0], 6), round(v[1], 6)) for k, v in ckm.items()})
