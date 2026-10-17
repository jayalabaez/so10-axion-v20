"""Second-pass verifier: semi-analytic (non-ODE) re-derivation of the R-odd relic yield from the plasma
during perturbative reheating, written independently of the three Boltzmann codes already in the folder.

Background (Gamma << H_I, inflaton = matter): with x = a_I/a,
   H(x) = H_I x^{3/2}  (inflaton dominated until H ~ Gamma),
   rho_R(x) = (2/5) Gamma rho_I/H_I [x^{3/2} - x^4]   (exact solution of d(rho_R a^4)/dt = Gamma rho_phi a^4)
   -> T_max = 0.805 g_*^{-1/8} (T_RH^2 H_I M_P)^{1/4} with M_P reduced and Gamma = sqrt(pi^2 g_*/90) T_RH^2/M_P.
Freeze-in (no back-reaction, valid when Omega << 1 ... we only need the overclosure line):
   d(n_X a^3)/dt = <sv> n_eq(T)^2 a^3  ->  n_X a^3 |_end = int <sv> n_eq^2 a^3 dt,  dt = -dx/(x H(x)).
Dilution: entropy at the end of reheating.  Rather than tracking a^3 to T_RH analytically (the late phase is not
matter-dominated any more), use the conserved quantity rho_R a^4 proxy: in the inflaton-dominated phase
rho_R a^4 grows as a^{5/2}; at the end (a_RH) rho_R(a_RH) = 3 M_P^2 Gamma^2 (H = Gamma).  We take the standard
approximation a_RH from H(a_RH) = Gamma with H = H_I x^{3/2}, i.e. x_RH = (Gamma/H_I)^{2/3}, and
T(a_RH) from rho_R = (2/5) Gamma rho_I/H_I x_RH^{3/2} = (2/5) * 3 M_P^2 H_I Gamma * (Gamma/H_I) = (6/5) M_P^2 Gamma^2
(close to the exact 3 M_P^2 Gamma^2; the factor 5/2 in rho_R is an O(1) uncertainty of the matching ->
T uncertainty (5/2)^{1/4} = 1.26 -> Y uncertainty factor 2; we quote both choices).
Y = n_X / s at a_RH, then conserved.  Omega h^2 = 2.74e8 (M/GeV) Y.
"""
import json, numpy as np
from scipy.special import kve
from scipy.integrate import quad

MP = 2.435e18
GS = 106.75
OUT = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics\verify-feasibility\vf2_relic_semianalytic.json"


def neq(M, T, g=40.0):
    z = M / T
    if z > 650:
        return 0.0
    return g * M * M * T * kve(2, z) * np.exp(-z) / (2 * np.pi ** 2)


def yield_semianalytic(M, TRH, HI, k=1.0, alpha=0.03, g=40.0, match="exact_rho"):
    Gam = np.sqrt(np.pi ** 2 * GS / 90.0) * TRH ** 2 / MP
    sv = k * np.pi * alpha ** 2 / M ** 2
    rhoI = 3 * MP ** 2 * HI ** 2
    A = 0.4 * Gam * rhoI / HI          # rho_R = A (x^{3/2} - x^4)

    def T_of_x(x):
        rr = A * max(x ** 1.5 - x ** 4, 0.0)
        return (30 * rr / (np.pi ** 2 * GS)) ** 0.25

    x_RH = (Gam / HI) ** (2.0 / 3.0)
    # integrand in ln x: n_X a^3 = a_I^3 int sv n_eq^2 x^{-3} dt ; dt = -dx/(x H) = -dx/(x H_I x^{3/2})
    # -> n_X(a_RH) a_RH^3/a_I^3 = int_{x_RH}^{1} sv n_eq(T(x))^2 x^{-3} /(H_I x^{5/2}) dx
    def integrand(lx):
        x = np.exp(lx)
        T = T_of_x(x)
        ne = neq(M, T, g)
        return sv * ne * ne * x ** (-3) / (HI * x ** 1.5)  # dx/x = dlx : x^{-5/2} * x = x^{-3/2}
    # find T_max location
    xs = np.exp(np.linspace(np.log(x_RH), 0.0, 4000))
    Ts = np.array([T_of_x(x) for x in xs])
    Tmax = Ts.max()
    # integrate in pieces around the peak for accuracy
    lo, hi = np.log(x_RH), 0.0
    val, err = quad(integrand, lo, hi, limit=400, points=[np.log(xs[Ts.argmax()])])
    nX_a3_over_aI3 = val
    nX_RH = nX_a3_over_aI3 * x_RH ** 3
    if match == "exact_rho":
        rr_RH = 3 * MP ** 2 * Gam ** 2
    else:
        rr_RH = A * x_RH ** 1.5
    T_RH_eff = (30 * rr_RH / (np.pi ** 2 * GS)) ** 0.25
    s = 2 * np.pi ** 2 / 45 * GS * T_RH_eff ** 3
    Y = nX_RH / s
    return dict(M=M, TRH=TRH, HI=HI, Tmax=Tmax, Tmax_formula=0.805 * GS ** (-1 / 8) * (TRH ** 2 * HI * MP) ** 0.25,
                M_over_Tmax=M / Tmax, T_RH_eff=T_RH_eff, Y=Y, Omega_h2=2.74e8 * M * Y, quad_err=err)


def threshold(M, HI, target=0.12, match="exact_rho"):
    lo, hi = 1e9, 1e13
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        if yield_semianalytic(M, mid, HI, match=match)["Omega_h2"] <= target:
            lo = mid
        else:
            hi = mid
        if hi / lo < 1.01:
            break
    return np.sqrt(lo * hi)


if __name__ == "__main__":
    out = {"points": [], "thresholds": []}
    for (M, TRH, HI) in ((1e13, 1.08e11, 3e7), (1e13, 1e11, 3e7), (3e12, 1.38e10, 3e7), (1e13, 4.05e11, 1e6), (1e13, 1.62e11, 1e7)):
        for match in ("exact_rho", "matter_rho"):
            r = yield_semianalytic(M, TRH, HI, match=match)
            r["match"] = match
            out["points"].append(r)
            print(json.dumps({k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in r.items()}))
    for (M, HI) in ((1e13, 3e7), (3e12, 3e7), (1e13, 1e7), (1e13, 1e6), (6e12, 3e7), (6e12, 1e7)):
        th1 = threshold(M, HI, match="exact_rho")
        th2 = threshold(M, HI, match="matter_rho")
        r1 = yield_semianalytic(M, th1, HI)
        out["thresholds"].append(dict(M=M, HI=HI, TRH_max_exact_rho=th1, TRH_max_matter_rho=th2, M_over_Tmax_at_th=r1["M_over_Tmax"]))
        print(f"threshold M={M:.0e} HI={HI:.0e}: TRH_max = {th1:.3e} (exact-rho matching) / {th2:.3e} (matter matching); M/Tmax at threshold = {r1['M_over_Tmax']:.1f}")
    json.dump(out, open(OUT, "w"), indent=1, default=float)
