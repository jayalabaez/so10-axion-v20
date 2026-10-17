"""K5 continuation: (A) the Vec3 = 16(-6)+16bar(10) ("C") sector as a possible second long-lived relic (K0 flagged it
with tau ~ 1e15-1e16 s from dim-10 operators; the K5 feasibility verifier listed X-only operators that are not SO(10)
invariant).  Here: the lowest-dimension operators connecting C to the other sectors, with SO(10) invariance checked by
hand against the tensor products 16x16 = 10+120+126 (pairs with 10, 120, 126bar scalars), 16barx16bar = 10+120+126bar
(pairs with 10, 120, 126), 16x16bar = 1+45+210 (pairs with singlets, 45, 210), and X neutrality.  Scalars: Phi210 (0),
Delta = 126bar (-2), H10 (-2), S (4), Phi17 (17) and conjugates.  Mixing masses and lifetimes in the two orderings
m_C > m_A and m_C < m_A (A = Vec1 = 16(0)+16bar(4), which decays promptly through F Abar S^3 Phi17*/M_P^3, K0/K5).
(B) T_RH thresholds for a relic that must be a tiny fraction of the DM (late decays), reusing the K5 Boltzmann solver
with the vector-like-16 production parameters (g_X = 64, k = 10), and the R-odd thresholds at M = 6e12.
(C) Leptogenesis cross-link with K2's provisional RH-neutrino spectrum M_R = (5.9e12, 7.4e11, 6.4e10) GeV.
(D) Graviton-mediated UV freeze-in estimate (EST) at the window edge.
All EST unless stated.  Writes k5_second_relic.json.
"""
from __future__ import annotations
import json, sys, time, math
import numpy as np

HERE = r"C:\Users\jayal\AppData\Local\Temp\claude\c--Users-jayal-Downloads-So10Theory2-So10Theory\d4b271a0-faef-4f94-bc1d-6399a3649e86\scratchpad\wfV21\K5-cosmology-relics"
sys.path.insert(0, HERE)
from k5_relic_reheating import run, threshold, MP, GSTAR  # noqa: E402

OUT = HERE + r"\k5_second_relic.json"
hbar = 6.582e-25  # GeV s

# ---------------------------------------------------------------- (A) operator table for the C sector
vS, vR, vPhi, vEW = 4.0e13, 3.0e13, 1.0e17, 174.0
# each entry: name, bilinear type, X check, SO(10) check (by the product rules above), dimension, vev monomial / M_P^(d-4)
ops = []
def add(name, dim, mixing_mass, so10_ok, x_sum, note):
    ops.append(dict(operator=name, dim=dim, mixing_mass_GeV=mixing_mass, SO10_invariant=so10_ok, X_sum=x_sum, note=note))
# C(-6).A(0): 16.16 -> needs 10/120/126bar scalar
add("C A H10^dag S / M_P", 5, vEW * vS / MP, True, -6 + 0 + 2 + 4, "16.16.10 ok; H10^dag is a 10; EW-vev mixing (3e-3 GeV) AND a C-A-h Yukawa vertex y_eff = <S>/M_P")
add("C A Delta S^2 / M_P^2", 6, vR * vS ** 2 / MP ** 2, True, -6 + 0 - 2 + 8, "16.16.126bar ok; <Delta_R> = v_R in the nu^c nu^c direction: singlet-singlet mixing")
add("C A Delta^dag S / M_P  (verifier/K0 'Vec1 Vec3 Delta^ S')", 5, None, False, -6 + 0 + 2 + 4, "16.16.126 has no singlet: NOT SO(10) invariant (X-only candidate)")
# C(-6).F(1)
add("C F H10^dag S^5 Phi17^dag / M_P^6", 10, vEW * vS ** 5 * vPhi / MP ** 6, True, -6 + 1 + 2 + 20 - 17, "direct C-F; negligible")
add("C F Delta^dag ... ", 10, None, False, None, "16.16.126 not invariant; the invariant partner needs Delta (X=-2): C F Delta S^6 Phi17^dag is dim 11")
# Cbar(10).Abar(4): 16bar.16bar -> 10/120/126 scalar
add("Cbar Abar H10 S^dag^3 / M_P^4", 7, vEW * vS ** 3 / MP ** 4, True, 10 + 4 - 2 - 12, "16bar.16bar.10 ok; negligible")
add("Cbar Abar Delta^dag S^dag^4 / M_P^5", 8, vR * vS ** 4 / MP ** 5, True, 10 + 4 + 2 - 16, "16bar.16bar.126 ok; negligible")
# C(-6).Bbar(7) : 16.16bar -> singlet/45/210
add("C Bbar S^4 Phi17^dag / M_P^5", 8, vS ** 4 * vPhi / MP ** 5, True, -6 + 7 + 16 - 17, "negligible")
# C(-6).Abar(4): X=-2 -> 4a+17c = 2 -> S^dag^8 Phi17^2 : dim 13
add("C Abar S^dag^8 Phi17^2 / M_P^10", 13, vS ** 8 * vPhi ** 2 / MP ** 10, True, -6 + 4 - 32 + 34, "negligible")
# C(-6).B(-3): X=-9 -> with H10^dag: -7 -> S^6 Phi17^dag (dim 11)
add("C B H10^dag S^6 Phi17^dag / M_P^7", 11, vEW * vS ** 6 * vPhi / MP ** 7, True, -6 - 3 + 2 + 24 - 17, "negligible")
# Cbar(10).P(-9): 16bar.16 : X = 1 -> S^4 Phi17^dag : dim 8
add("Cbar P S^4 Phi17^dag / M_P^5", 8, vS ** 4 * vPhi / MP ** 5, True, 10 - 9 + 16 - 17, "mixing with the 1e17 Phi-sector; negligible")
add("Cbar Pbar H10 (renormalizable)", 4, None, True, 10 - 8 - 2, "P-sector (1e17) decays promptly into Cbar + h; keeps the C-sector number")
add("C Cbar S^dag (renormalizable mass)", 4, None, True, -6 + 10 - 4, "M_C = y_C <S>")

# lifetimes (EST): sector A decays promptly: theta_AF = m_AF / M with m_AF = vS^3 vPhi / MP^3 (dim 7, K0/K5), Gamma ~ theta^2 Y^2 M/(16 pi)
M = 1.0e13
Y = 0.5
m_AF = vS ** 3 * vPhi / MP ** 3
theta_AF = m_AF / M
Gamma_A = theta_AF ** 2 * Y ** 2 * M / (16 * math.pi)
tau_A = hbar / Gamma_A
y_eff5 = vS / MP          # C-A-h vertex from the dim-5 operator (times the H10 fraction of the SM Higgs, taken 1)
# branch 1: m_C > m_A + m_h : C -> A h at tree level
Gamma_C_to_Ah = y_eff5 ** 2 * M / (16 * math.pi)
tau_C_branch1 = hbar / Gamma_C_to_Ah
# branch 2: m_C < m_A : C is the lightest of the (A,C) complex; its nu^c-like member mixes with A's through the dim-6
# operator (m_CA6 = vR vS^2/MP^2) and A mixes with F (theta_AF).  Effective F admixture theta_CA * theta_AF.
m_CA6 = vR * vS ** 2 / MP ** 2
m_CA5 = vEW * vS / MP
branch2 = []
for dM in (1e11, 3e11, 1e12, 3e12):
    th_CA = max(m_CA6, m_CA5) / dM
    th_eff = th_CA * theta_AF
    G = th_eff ** 2 * Y ** 2 * M / (16 * math.pi)
    branch2.append(dict(dM=dM, theta_CA=th_CA, theta_eff=th_eff, Gamma_GeV=G, tau_s=hbar / G))
# K0-type direct dim-10 route for comparison (F Vec3 Delta^dag S^5 Phi17^dag is NOT invariant; the invariant dim-10 C F H10^dag S^5 Phi17^dag has the EW vev):
m_CF10 = vEW * vS ** 5 * vPhi / MP ** 6
G10 = (m_CF10 / M) ** 2 * Y ** 2 * M / (16 * math.pi)
# three-body via the dim-5 vertex with an off-shell A (branch 2, m_C < m_A): C -> h + A* -> h + h' + F, Gamma ~ y_eff5^2 theta_AF^2 Y^2 M/(192 pi^3) x (M/dM)^2 (phase space EST)
three_body = []
for dM in (1e11, 3e11, 1e12, 3e12):
    G3 = y_eff5 ** 2 * theta_AF ** 2 * Y ** 2 * M / (192 * math.pi ** 3) * (M / dM) ** 2
    three_body.append(dict(dM=dM, Gamma_GeV=G3, tau_s=hbar / G3))

partA = dict(vevs=dict(vS=vS, vR=vR, vPhi=vPhi, vEW=vEW), M=M, Yukawa_assumed=Y, operators=ops,
             A_sector=dict(m_AF_GeV=m_AF, theta_AF=theta_AF, Gamma_GeV=Gamma_A, tau_s=tau_A),
             C_branch1_mC_gt_mA=dict(y_eff5=y_eff5, Gamma_GeV=Gamma_C_to_Ah, tau_s=tau_C_branch1),
             C_branch2_mC_lt_mA=dict(m_CA6_GeV=m_CA6, m_CA5_GeV=m_CA5, two_step_mixing=branch2, three_body_offshell_A=three_body,
                                     direct_dim10=dict(m_CF10_GeV=m_CF10, Gamma_GeV=G10, tau_s=hbar / G10)),
             conclusion="EST: branch 1 prompt (1e-20 s). Branch 2: tau ~ 1e-4 ... 10 s for dM = 1e11..3e12 (two-step mixing), "
                        "i.e. around or before BBN onset; K0's 1e15-1e16 s (dim-10 only) is superseded by the dim-5/6 C-A operators. "
                        "Residual: Planck coefficients and dM unknown -> tau uncertain by >= 2 orders; the late-decay bounds below cover the worst case.")

# ---------------------------------------------------------------- (B) thresholds for late-decay fractions, vector-like-16 production
t0 = time.time()
partB = []
def thr(M_, HI_, key, target, k, gX, label):
    # threshold() in k5_relic_reheating uses run(M, TRH, HI, k, alpha); gX is a kwarg of run -> wrap
    import k5_relic_reheating as R
    orig = R.run
    def run_g(Mx, TRHx, HIx, kx=1.0, alphax=0.03, gXx=gX):
        return orig(Mx, TRHx, HIx, kx, alphax, gXx)
    R.run = run_g
    try:
        th, note = R.threshold(M_, HI_, key, target, k=k)
    finally:
        R.run = orig
    row = dict(M=M_, HI=HI_, criterion=label, k=k, gX=gX, TRH_max=th, note=note, M_over_TRH=(M_ / th if th else None))
    print(row, flush=True)
    return row

for M_ in (3e12, 1e13):
    for HI_ in (1e6, 1e7, 3e7):
        for target, label in ((0.12, "Omega_C = Omega_DM"), (1.2e-5, "Omega_C = 1e-4 Omega_DM"), (1.2e-7, "Omega_C = 1e-6 Omega_DM"), (1.2e-9, "Omega_C = 1e-8 Omega_DM")):
            partB.append(thr(M_, HI_, "Omega_h2", target, k=10.0, gX=64.0, label=label + " [VL16: k=10, gX=64]"))
# R-odd thresholds at M = 6e12 (standard parameters k=1, gX=40) for the leptogenesis cross-link
partB6 = []
for HI_ in (1e5, 1e6, 1e7, 3e7):
    partB6.append(thr(6e12, HI_, "Omega_h2", 0.12, k=1.0, gX=40.0, label="Omega_X = Omega_DM [R-odd: k=1, gX=40]"))
    partB6.append(thr(6e12, HI_, "Omega_h2", 1.2e-4, k=1.0, gX=40.0, label="Omega_X = 1e-3 Omega_DM [R-odd: k=1, gX=40]"))

# ---------------------------------------------------------------- (C) leptogenesis cross-link with K2's provisional spectrum
MR = (5.9e12, 7.4e11, 6.4e10)
m_atm = 0.05e-9  # GeV
v = 174.0
M1 = MR[2]
eps1_DI = 3 * M1 * m_atm / (16 * math.pi * v ** 2)
# eta_B ~ 1e-2 eps_1 kappa  (standard; eta_B = 6.1e-10)
kappa_needed = 6.1e-10 / (1e-2 * eps1_DI)
# windows: need T_RH >= M1 (zero initial abundance, weak washout) or >= M1/5 (strong washout, EST)
prev = json.load(open(HERE + r"\k5_relic_reheating.json", encoding="utf-8"))
def trh_max(M_, HI_, crit="Omega_X = Omega_DM"):
    for r in prev["thresholds"]:
        if r["M"] == M_ and r["HI"] == HI_ and r["criterion"] == crit:
            return r["TRH_max"]
    for r in partB6:
        if r["M"] == M_ and r["HI"] == HI_ and r["criterion"].startswith(crit):
            return r["TRH_max"]
    return None
windows = []
for M_ in (3e12, 6e12, 1e13):
    for HI_ in (1e5, 1e6, 1e7, 3e7):
        tmax = trh_max(M_, HI_)
        windows.append(dict(M_lightest_Rodd=M_, HI=HI_, TRH_max_OmegaDM=tmax,
                            window_TRH_ge_M1=(tmax is not None and tmax >= M1), window_TRH_ge_M1_over_5=(tmax is not None and tmax >= M1 / 5),
                            window_TRH_ge_1e9=(tmax is not None and tmax >= 1e9)))
partC = dict(K2_M_R_GeV=list(MR), M1=M1, eps1_DI_max=eps1_DI, kappa_efficiency_needed=kappa_needed, windows=windows,
             note="K2's point is a non-converged best fit (chi2 = 218); M_1 = 6.4e10 is provisional. Thermal N_1 leptogenesis needs "
                  "T_RH >~ M_1 (zero initial abundance) or >~ M_1/5 (strong washout, EST); DI bound M_1 > ~1e9 (LIT-abstract).")

# ---------------------------------------------------------------- (D) graviton-mediated UV freeze-in (EST)
# gamma ~ a_grav T^8/M_P^4 with a_grav ~ 1e-3 (fermion pair from the full SM bath, order of magnitude);
# Y ~ a_grav (45/(2 pi^2 1.66 g*^{3/2})) T_RH^3/(3 M_P^3) x exp(-2M/T_RH) (Boltzmann factor for M > T_RH; crude)
def Y_grav(M_, TRH, a_grav=1e-3):
    pref = a_grav * 45.0 / (2 * math.pi ** 2 * 1.66 * GSTAR ** 1.5) * TRH ** 3 / (3 * MP ** 3)
    return pref * math.exp(-2 * M_ / TRH) if M_ > TRH else pref
partD = []
for M_ in (3e12, 1e13):
    for TRH in (1e11, 3e11, 1e12):
        Yg = Y_grav(M_, TRH)
        partD.append(dict(M=M_, TRH=TRH, Y_grav=Yg, Omega_h2=2.74e8 * M_ * Yg, Omega_over_DM=2.74e8 * M_ * Yg / 0.12))

res = dict(partA=partA, partB_late_decay_thresholds=partB, partB_Rodd_6e12=partB6, partC_leptogenesis=partC, partD_graviton_freeze_in=partD,
           runtime_s=time.time() - t0)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1, default=float)
print(json.dumps(partA, indent=1, default=float))
print(json.dumps(partC, indent=1, default=float))
print(json.dumps(partD, indent=1, default=float))
print("done", res["runtime_s"])
