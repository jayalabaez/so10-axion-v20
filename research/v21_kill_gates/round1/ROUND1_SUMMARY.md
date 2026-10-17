# v21 kill gates, round 1: summary (2026-10-16)

Workflow wf_7f291be0-2ee. All structured gate and skeptic results are in ROUND1_RESULTS.json (same folder). Each gate
folder has a REPORT.txt plus scripts. The judge, critic, final adjudicator, K4 continuation, K1b re-solve and the K0b/K3
skeptics did NOT run (usage-credit failure). Labels: EXACT, NUM, EST, CONJ, LIT.

## Configuration under test ("v21-F17-G3221", now with the B63 fermion sector)
- Gauge SO(10) x U(1)_X; scalar potential of v20 verbatim (51 parameters, models/SO10Z17AxionV20.m, including the
  kappaH H10.H10.S row; the K0 draft model file models/SO10Z17AxionV21.m wrongly DROPPED that row - any new model file
  must restore it).
- Scalars: Phi210 (X=0), Delta126bar (-2), H10 complex (-2), S (4), Phi17 (17).
- Vacuum: one-step G3221 at M_U ~ 2-3e16 (210 orientation D-odd, p*a < 0: "Am45"), Delta_R (1,1,3) at v_R, <S>, <Phi17>.

## K0 contract: original F17 FAIL (skeptics upheld), K0b variant B63 PASS (NOT skeptic-verified)
- F17 dies on axion quality: PQ-violating closures with K = 12 Planck powers (skeptic correction: dtheta ~ 10^-1..10^0.6
  instead of 10^1.1; still >= 8.5 orders above 1e-10). Some closures labelled EXACT were zero by B-L (net Delta_R
  power must vanish); valid K = 9/10 closures remain.
- K0b: v21-F17-B63 (K0b-charge-variants/candB63*.json, REPORT.txt): 3x16_F(1); conj[S]-mass pairs 16(-35)+16bar(39),
  16(-28)+16bar(32), 16(34)+16bar(-30), 2x10(+2); Phi17 pair 16(-35)+16bar(18); singlets 1(-63)+1(59), 1(-58)+1(54)
  [S], 1(-57)+1(61) [conj S], 2x1(-2) [S Majorana]. 12 renormalizable fermion structures (listed in the K0b result).
  T_S = 14, T_Phi = 4, N = 34, E/N = 8/3, N_DW = 1 mod gauge, b_X = 101203 (g_X(M_U) <= 0.013). Dual-LP certificate
  K_min >= 17 (attained by a 4-loop UV-dominated closure, 10^-11.8 below tree) -> dtheta = 2.1e-11 at <S> = 3e13,
  1.0e-10 at 3.29e13 (margin x5). y_s window at M_s = 1e13: [0.304, 0.368]; <S> = 2.7-3.29e13; m_a = 2.09-2.52 ueV.
  Relics: exactly stable R-odd state; long-lived colour-neutral 16-sector state (tau >~ 1e8 s EST).
  Alternative A48 (|X| <= 48) also passes but adds a 4th family-like 16 with O(0.1) mixings.

## K1 unification (G7): UNDECIDED (skeptics agree) - but computed for a light content that is NOT realisable
- For T2/T3 contents: two-loop robust for M_s >~ 7e12; three-loop +5% knife edge at M_s = 1e13; 2L/1L = 1.9 at M_U.
- Skeptic additions: the heavy-vector MS-bar matching constant (S_V = (5,6,6,8)/(12 pi)) moves Lambda_3L by +-6-8%
  (larger than the margin; sign convention to fix from primary literature).
- Skeptic two-loop runs with K3-allowed contents (K1-g7-unification/verify-*/vf_k3_contents.*):
  bidoublet + Delta_R only -> v_R = 2.9e9, M_U = 1.8e16 (no 1e13 seesaw scale);
  T2 minus (8,2,2) -> v_R = 8.0e12, M_U = 2.3e15, tau_p = 2.1e33 yr < Super-K 2.4e34 (killed);
  T2 minus (8,3,1)+(1,3,1) -> no perturbative unification; bidoublet + Delta_R + (8,1,1) -> v_R = 1.1e8.
  NOT computed: bidoublet + (8,3,1)_0 + Delta_R, and two bidoublets + (8,3,1)_0 + Delta_R (with B63 fermions).
- One-loop b's: K5's exact Fraction recount for T2 + F17 is b = (47/6, 12, 29/3, 89/6); K2 used wrong b's.

## K2 flavour: T2 FAIL (EXACT obstruction found by both skeptics); two-bidoublet basin chi2 ~ 220
- EXACT: X forbids F.F.H10^* (X = 4), so ONE light complex G3221 bidoublet Phi_L = alpha Phi_10 + beta Phi_126 gives one
  matrix Y_L for both H_u and H_d: Yu = (v_u/v_d) Yd, CKM = 1 up to O((v_R/M_U)^2) ~ 1e-6 (repo G8 v2 lemma "one light
  G3221 bidoublet forces s = 1"). Pulls: s12 -331 sigma, s23 -52, s13 -35. This kills the T2 content AND K3's realisable
  content (one bidoublet). Escape: TWO light bidoublets with different 10/126bar compositions (or an O(1) (15,1,3) vev,
  i.e. G3211, which K3 found is not a local minimum).
- Two-bidoublet (free-composition) fits: K2 chi2 = 218 (unconverged); skeptic independent fit chi2 = 222.8 (DE 1e6
  evaluations x 2 seeds + LM + ~170 basin hops), same basin as Ohlsson-Pernow 2019 (r ~ -66, s ~ 0.39-0.48);
  tensions sin^2 theta23 pull -12, sin^2 theta13 -4.5..-7, delta_CKM +5..+6. Literature claim of chi2 ~ 15-25 (dof 1) is
  not reproduced. K2 had a composition-normalisation bug (light doublet is ~59% 126bar (15,2,2) up-type, not 99.98% 10).

## K3 vacuum / G6 / Higgs: FAIL for T2/T3 (NUM, converged convex LPs at 4 orientations)
- Realisable at a one-step G3221 point: ONE complex bidoublet (pure H10 or up to 75% Sigma(15,2,2)) + (8,3,1)_0 +
  Delta_R (1,1,3). Not light: (8,2,2)_0, (1,3,1)_0 (fails SM-singlet-subspace minimality), (8,1,1), PS partners of
  Delta_R. A SECOND LIGHT BIDOUBLET WAS NOT TESTED DIRECTLY ("excluded a fortiori" only as part of T3).
- Explicit point P831 (bidoublet + (8,3,1)_0 + Delta_R, Am45): 35 zero / 0 negative / 36 light / 415 heavy, a0 <= 0.49,
  tree lambda_eff dialable (required ~ -0.04 after a ~ +0.03 one-loop threshold). Tunings: 3 mass cancellations at
  ~1e-6, 2-4 cubic suppressions at ~1e-5, one quartic tuning 1/6000, plus EW. One-loop CW curvature of tuned states is
  1e5-1e7 x tree (tunings must be redone at one loop).
- GLOBAL MINIMALITY FAILS at both explicit points: full-486-chart Newton descents reach a deeper region
  (V - V* = -26.6 box units, |Sigma| ~ 4|Phi|, |H| ~ 1.8|Phi|, positive quartic along the ray; driven by O27_B02,
  Im O31, O06, O20). O27 >= 0 is LP-infeasible; |O31|, |O28| <= 0.05 is LP-feasible (t = 0.00342) but untested by
  descents. Tools: K3-vacuum-g6-higgs/k3_lp4.py, k3_verify.py, k3_descend.py, k3_bisect.py, k3_cw_lambda.py, rows npz.

## K4 certification method: UNDECIDED (partial; agent died)
- EXACT: orbit-space method unusable (165-dim orbit space); degree-2 SOS impossible at every D-odd G3221 point
  (179 flat modes vs a PD 180-dim normal Hessian).
- NUM: complete symmetry-adapted degree-3 multiplier SOS for a 210-only prototype is infeasible (residual 2.5e-4;
  numerical Farkas ray, exact verification unfinished). Degree 4 not attempted. So no exact G3 certificate method is
  known for the G3221 vacuum; at best "numerical global search + exact local Hessian" (relaxation U2a).

## K5 cosmology: PASS (both skeptics)
- Pre-inflation PQ; H_I <= 3-4e7; T_RH window [1e10, 1.1e11] at M = 1e13; m_a avoids ADMX; relics OK with a
  singlet-LRP refinement (y_1 >~ y_10 or y_h <~ 1e-5).
