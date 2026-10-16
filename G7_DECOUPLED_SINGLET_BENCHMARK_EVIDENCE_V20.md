# G7 evidence on the decoupled-singlet benchmark BM-DA1 (v20)

**Status:** `G7_DECOUPLED_SINGLET_BENCHMARK_BM_DA1__TWO_LOOP_PASS__THREE_LOOP_WITHIN_TWO_CODE_ROOT_UNCERTAINTY__RG_IMPROVED_QUALITY_FAIL_CONDITIONAL__G7_BLOCKED`
**Overall state:** `BM_DA1_TWO_LOOP_PASS__THREE_LOOP_GAUGE_ONLY_FAIL_U1_ROOT_MARGINAL_PASS_U2_ROOT__RG_IMPROVED_QUALITY_FAIL_CONDITIONAL__G7_BLOCKED`
**G7 status:** `BLOCKED` (evidence only; this module never changes a gate status)
**Checks:** 46/46 passed

G7 is not closed on BM-DA1. It passes the reduced-Planck Landau criterion at two loops (alpha = 1 at 3.72e18 GeV on the U1 root, 3.88e18 GeV on the second-code U2 root). At three loops (gauge-only; P,Q,R at x0 p) it fails on the U1 root (2.34e18 GeV < 2.435e18 GeV, -3.8%) and passes marginally on the U2 root (2.438e18 GeV, +0.14%), so the BM-DA1 three-loop outcome lies within the two-code root uncertainty (and below the neglected two-loop GUT thresholds and Yukawa terms). With the RG-improved remnant masses (CONDITIONAL: anti-SOS region points, committed GUT scalar spectrum) the rho = 1e3 root moves to v_R = 8.56e9 GeV, <S> = 2.85e13 GeV at y_s = 0.30 and fails both axion-quality bounds; doubling the GUT scalar masses removes that failure (research scheme variant: v_R = 1.96e9 GeV, NDA 1.6e-11, Z17 4.3e-17), while U2 and the other scheme variants keep it. BM-E passes at two loops only (P,Q,R at x0 p; on both roots). Every flavour-capable SO(10)-phase addition fails the criterion at three loops at BM-DA1 (a 120_H, a second 126bar and vectorlike pairs already at two loops), as does the contract content itself on the U1 root. The SO(10)-phase running is gauge + matter only at every order and the rho windows that pass are conditional (anti-SOS remnant masses; G6 not closed; the NDA window is convention-dependent); a Planck gauge-kinetic term would move the alpha = 1 scale by more than the three-loop margins (EST). G7 stays BLOCKED.

Labels: `CONDITIONAL` holds only under the stated conditions; `EST` order-of-magnitude arithmetic, never load-bearing for a check; `EXACT` Fraction or sympy identity; `LIT` a paper that was read (transcription recorded with sha256); `NUM` float, recomputed in this module; `RESEARCH_RECORD` not re-derived; sha256 provenance of the scratch output; `RESEARCH_RECORD_INPUT` a research value used as an input of a recomputation.

## Flags

- `evidence_recorded`: `True`
- `bm_da1_two_loop_pass_both_roots`: `True`
- `bm_da1_three_loop_fail_on_U1_root`: `True`
- `bm_da1_three_loop_marginal_pass_on_U2_root`: `True`
- `bm_da1_rg_improved_quality_fail_conditional`: `True`
- `bm_e_three_loop_fail_both_roots`: `True`
- `integrators_agree`: `True`
- `G7_closed`: `False`
- `gate_status_changed`: `False`
- `wired_into_gate_ledger`: `False`
- `report_closes_G7_by_itself`: `False`
- `benchmark_adopted`: `False`
- `three_loop_includes_yukawa_quartic`: `False`
- `planck_kinetic_term_computed`: `False`
- `G6_closed_assumed_true`: `False`

## (A) coefficients (EXACT)

t = ln(mu/GeV); dg/dt = b1 g^3/(16 pi^2) + b2 g^5/(16 pi^2)^2 + b3 g^7/(16 pi^2)^3, i.e. d alpha^-1/dt = -b1/(2 pi) - b2 alpha/(8 pi^2) - b3 alpha^2/(32 pi^3); Weyl fermions, real scalars (a complex scalar = 2 real), T(10) = 1, C_G = C2(45) = 8; SO(10) phase from mu_G = M_X with 3 x 16 + 5 x (16 + 16bar) + 210 (real) + 126bar + 10 (complex), P,Q,R (+ bars) = 3 x (16 + 16bar) above x0 p; 1L: b2 = b3 = 0; 2L: b3 = 0; 3L_gauge_only: gauge + matter three-loop term; the SO(10)-phase running is gauge + matter only at EVERY order (the two-loop Yukawa terms of 16.16.10_H, 16.16.126bar_H and y_s S 16_s 16bar_s and the three-loop Yukawa and quartic terms are omitted; the Yukawa terms enter d alpha^-1/dt with a positive sign and would raise the alpha = 1 scale, so their omission is not conservative for a fail statement); U(1)_X feedback neglected

| rep | dim | T | C2 |
| --- | --- | --- | --- |
| 10 | 10 | 1 | 9/2 |
| 16 | 16 | 2 | 45/8 |
| 16bar | 16 | 2 | 45/8 |
| 45 | 45 | 8 | 8 |
| 54 | 54 | 12 | 10 |
| 120 | 120 | 28 | 21/2 |
| 126 | 126 | 35 | 25/2 |
| 126bar | 126 | 35 | 25/2 |
| 210 | 210 | 56 | 12 |

SO(10) phase (PGJ): without P,Q,R b = (28/3, 22283/6, 132706057/864); with P,Q,R b = (52/3, 25013/6, 109873879/864). MV cross-check (two_loop_thresholds_v20): (28/3, 22283/6) and (52/3, 25013/6).

QCD with general Casimirs (b + beta at 1, 2, 3 loops): 0, 0, 0; n_f = 5, 6: b3 = -9769/54, 65/2.

MSS arXiv:1201.5868 eq. (5) as polynomials in n_G (residuals) and the SM values at n_G = 3:

| group | residuals 1L, 2L, 3L | b1, b2, b3 at n_G = 3 |
| --- | --- | --- |
| U1_Y | 0, 0, 0 | 41/10, 199/50, -388613/24000 |
| SU2_L | 0, 0, 0 | -19/6, 35/6, 324953/1728 |
| SU3_C | 0, 0, 0 | -7, -26, 65/2 |

Chain segments (U1 record = exact re-derivation):

| segment | b | b_ij |
| --- | --- | --- |
| SM_1HDM | 41/10, -19/6, -7 | 199/50, 27/10, 44/5; 9/10, 35/6, 12; 11/10, 9/2, -26 |
| SM_1HDM+all_remnants | 53/6, -19/6, -25/6 | 10477/150, 27/10, 2084/15; 9/10, 35/6, 12; 521/30, 9/2, 289/3 |
| SM_1HDM+all_remnants+5pairs | 133/6, 61/6, 55/6 | 12377/150, 87/10, 2524/15; 29/10, 1015/6, 52; 631/30, 39/2, 1049/3 |
| PS_witness | -23/3, -3, 11/3 | 643/6, 9/2, 153/2; 45/2, 8, 3; 765/2, 3, 584/3 |
| PS_witness+5pairs | 17/3, 31/3, 17 | 2693/6, 39/2, 183/2; 195/2, 514/3, 3; 915/2, 3, 358 |
| PS_spectators_only_delta | 40/3, 40/3, 40/3 | 1025/3, 15, 15; 75, 490/3, 0; 75, 0, 490/3 |
| PS_anchor_with_(15,2,2) | -7/3, 2, 26/3 | 2435/6, 105/2, 249/2; 525/2, 73, 48; 1245/2, 48, 779/3 |
| SO10_no_spect | -4 | 5911/2 |
| SO10_5pairs | 28/3 | 22283/6 |
| SO10_5pairs+PQR | 52/3 | 25013/6 |

## (B) running (NUM)

I1: fixed-step RK4 in t = ln(mu/GeV), h = 0.001 (<= 0.002), threshold at the P,Q,R scale, alpha = 1 located by 80 bisections of the last step. I2: scipy solve_ivp DOP853, rtol = atol = 1e-12, terminal event alpha^-1 = 1. Max |I1/I2 - 1| = 6.39e-08 over 151 scales.

| benchmark | P,Q,R | 1L (GeV) | 2L (GeV) | 3L_gauge_only (GeV) | 2L pass | 3L pass |
| --- | --- | --- | --- | --- | --- | --- |
| BM-DA1 | PQR_at_x0p | 1.24858e+21 | 3.72351e+18 | 2.34352e+18 | yes | no |
| BM-DA1 | PQR_at_max_x0p_MPlred | 1.54577e+21 | 4.14231e+18 | 2.4556e+18 | yes | yes |
| BM-E | PQR_at_x0p | 1.56039e+21 | 3.584e+18 | 2.26665e+18 | yes | no |
| BM-E | PQR_at_max_x0p_MPlred | 2.33484e+21 | 4.4292e+18 | 2.57871e+18 | yes | yes |
| D_rho1e3 | PQR_at_x0p | 5.79855e+21 | 7.45006e+18 | 4.69074e+18 | yes | yes |
| D_rho1e3 | PQR_at_max_x0p_MPlred | 9.43175e+21 | 9.96588e+18 | 5.98823e+18 | yes | yes |

Second-code (U2) roots, P,Q,R at x0 p with x0/p = 10.0831 (U1 BM-DA1): the SO(10) phase run from the second-code (U2) roots with the same x0/p as the U1 BM-DA1 root (P,Q,R at x0 p); p = sqrt2 M_X/g_U equals U2's recorded chart scale.

| benchmark | v_R (GeV) | M_X (GeV) | alpha_U^-1 | x0 p (GeV) | 1L (GeV) | 2L (GeV) | 3L_gauge_only (GeV) | 3L margin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BM-DA1 | 1.22391e+09 | 8.35852e+16 | 23.7839 | 1.63974e+18 | 1.27516e+21 | 3.87714e+18 | 2.43844e+18 | 0.00141171 |
| BM-E | 5.57361e+09 | 5.33475e+16 | 25.6008 | 1.08579e+18 | 1.59942e+21 | 3.73499e+18 | 2.36189e+18 | -0.0300264 |
| D_rho1e3 | 8.359e+09 | 4.111e+16 | 29.8594 | 9.03635e+17 | 5.97909e+21 | 7.77469e+18 | 4.8961e+18 | 1.01072 |

Benchmark roots (RESEARCH_RECORD_INPUT, code U1):

| benchmark | variant | log10 rho | v_R (GeV) | M_X = mu_G (GeV) | alpha_U^-1 | x0 p (GeV) |
| --- | --- | --- | --- | --- | --- | --- |
| BM-DA1 | G6 | 3.00 | 1.26655e+09 | 7.79373e+16 | 23.9153 | 1.53316e+18 |
| BM-E | D | 2.50 | 5.74547e+09 | 4.98505e+16 | 25.7169 | 1.01691e+18 |
| D_rho1e3 | D | 3.00 | 8.56043e+09 | 3.85511e+16 | 29.9502 | 8.48675e+17 |

## (C) landau_cost (NUM; BM-DA1 root held fixed, P,Q,R at x0 p)

| option | b below P,Q,R (1L, 2L, 3L) | 2L (GeV) | 3L_gauge_only (GeV) | 2L pass | 3L pass | role |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 28/3, 22283/6, 132706057/864 | 3.72351e+18 | 2.34352e+18 | yes | no | the contract content (no flavour repair) |
| +real 45 | 32/3, 23179/6, 128249017/864 | 3.03202e+18 | 1.99232e+18 | yes | no | B-L-breaking 45_H: the 45 scalar portal (splits d from e off the certified orientation) |
| +real 45 +1VL | 40/3, 24089/6, 120626611/864 | 2.26196e+18 | 1.55437e+18 | no | no | 45_H plus one vectorlike 16 + 16bar |
| +complex 45 | 12, 8025/2, 4562891/32 | 2.518e+18 | 1.71337e+18 | yes | no | complex 45_H (X != 0) |
| +second 126bar | 21, 11301/2, 3765131/32 | 8.12403e+17 | 6.66726e+17 | no | no | a second 126bar_H |
| +10_F | 10, 7499/2, 14556977/96 | 3.41978e+18 | 2.18972e+18 | yes | no | one Weyl 10 (vectorlike 10 matter) |
| +2VL | 44/3, 24103/6, 117998269/864 | 2.0452e+18 | 1.41561e+18 | no | no | two vectorlike 16 + 16bar pairs |
| +120_H | 56/3, 30235/6, 100917097/864 | 1.08331e+18 | 8.49554e+17 | no | no | a 120_H (among the analysed candidates the only d/e splitter on the certified orientation, through a (15,2,2)_120 admixture of O((v_R/M15)^2)) |
| +120_H +real 45 | 20, 10377/2, 10182673/96 | 9.64681e+17 | 7.84033e+17 | no | no | a 120_H plus a real 45_H |

## (D) quality (NUM)

<S> = rho v_R / y_s (canonical), v_S = sqrt2 <S>, M_s = rho v_R = y_s <S>; NDA-conservative dtheta = 2 Lambda^16/(chi M_Pl,red^12) with Lambda = max(M_s, <S>) = <S> (every mass and scalar insertion <= Lambda), more conservative by y_s^-16 (2.3e8 at y_s = 0.30) than the manuscript's eq. (qualitybound), which uses Lambda = M_s; the eq. (qualitybound) value dtheta_NDA_Ms = 2 M_s^16/(chi M_Pl,red^12) is recorded alongside; Z17-EFT dtheta = 6.47e-37 (v_S/6.31e11)^17 (manuscript eq. scalarquality, c17 = 1); chi = (0.0755 GeV)^4; requirement dtheta < 1e-10; the hard-coded e2 flags NDA_quality_ok(vR<=2.2e9) / Z17_quality_ok(vR<=4.6e9) are thresholds for rho = 1e3 only and are NOT used

| point | y_s | v_R (GeV) | <S> (GeV) | dtheta NDA | dtheta Z17 | NDA ok | Z17 ok |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BM-DA1 (G6 masses) | 0.30 | 1.26655e+09 | 4.22182e+12 | 1.44297e-14 | 2.52734e-20 | yes | yes |
| BM-DA1 (G6 masses) | 0.34 | 1.26655e+09 | 3.72514e+12 | 1.94776e-15 | 3.01011e-21 | yes | yes |
| rho = 1e3, RG-improved | 0.30 | 8.56043e+09 | 2.85348e+13 | 0.273679 | 3.23983e-06 | no | no |
| rho = 1e3, RG-improved | 0.34 | 8.56043e+09 | 2.51777e+13 | 0.0369419 | 3.85871e-07 | no | no |
| BM-E | 0.30 | 5.74547e+09 | 6.05626e+12 | 4.64004e-12 | 1.16582e-17 | yes | yes |
| BM-E | 0.34 | 5.74547e+09 | 5.34376e+12 | 6.26325e-13 | 1.38852e-18 | yes | yes |

RG-improved rho = 1e3 root (NUM, CONDITIONAL): conditional on the RG-improved remnant masses come from anti-SOS region points (G6 is not closed); the committed GUT scalar spectrum (non-perturbative normalisation; GUT thresholds uncontrolled): the GUT scalar masses x2 scheme variant removes the failure.

Scheme variants of that root (NUM (inputs RESEARCH_RECORD_INPUT: e5 U1 scheme variants and the U2 root)): doubling the GUT scalar masses removes the RG-improved quality failure (three loops and both bounds pass); U2 and every other scheme variant keep the Z17 failure (and the NDA failure with Lambda = <S>; with Lambda = M_s the mu_G = 2 M_X variant passes NDA but still fails Z17).

| variant | v_R (GeV) | 3L margin | <S> (0.30) | NDA (<S>) | NDA (M_s) | Z17 | NDA ok | Z17 ok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1:base | 8.56043e+09 | 0.926383 | 2.85348e+13 | 0.273679 | 1.1781e-09 | 3.23983e-06 | no | no |
| U1:cV=0 | 8.0622e+09 | 0.753036 | 2.6874e+13 | 0.10485 | 4.51345e-10 | 1.16898e-06 | no | no |
| U1:gut_mass_x0.5 | 3.12304e+10 | 0.76749 | 1.04101e+14 | 2.69491e+08 | 1.16007 | 11638.7 | no | no |
| U1:gut_mass_x2 | 1.961e+09 | 0.986375 | 6.53666e+12 | 1.57379e-11 | 6.77465e-20 | 4.26784e-17 | yes | yes |
| U1:muG=2MX | 6.03762e+09 | 0.312176 | 2.01254e+13 | 0.00102606 | 4.41684e-12 | 8.56686e-09 | no | no |
| U1:muR=2vR | 9.65208e+09 | 1.02527 | 3.21736e+13 | 1.86744 | 8.0387e-09 | 2.49259e-05 | no | no |
| U1:pdg_inputs | 8.06969e+09 | 0.911642 | 2.6899e+13 | 0.106419 | 4.581e-10 | 1.18757e-06 | no | no |
| U1:ys=0.3_2loop | 8.56408e+09 | 0.93403 | 2.85469e+13 | 0.275551 | 1.18616e-09 | 3.26338e-06 | no | no |
| U2 | 8.359e+09 | 1.01072 | 2.78633e+13 | 0.186975 | 8.04866e-10 | 2.16133e-06 | no | no |

## (E) windows (NUM, CONDITIONAL)

Conditional on: the RG-improved remnant masses come from anti-SOS region points (G6 is not closed); the GUT-scale thresholds are uncontrolled (witness a0 ~ 21.6 normalisation); the Yukawa terms (two and three loops) and the three-loop quartic terms are missing.

| variant | log10 rho | v_R (GeV) | alpha_U^-1 | 2L (x0 p) | 3L (x0 p) | 3L (P,Q,R at max(x0 p, M_Pl,red)) | NDA (0.30) | Z17 (0.30) | 3L/2L term ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G6 | 3.00 | 1.26655e+09 | 23.9153 | 3.72351e+18 | 2.34352e+18 | 2.4556e+18 | 1.44297e-14 | 2.52734e-20 | 0.319863 |
| D | 2.00 | 1.87434e+08 | 9.42707 | 7.28594e+17 | 5.62182e+17 | 5.62182e+17 | 7.63658e-44 | 1.97939e-51 | - |
| D | 2.00 | 2.56018e+09 | 19.867 | 1.57071e+18 | 9.14154e+17 | 9.14154e+17 | 1.12108e-25 | 3.96908e-32 | - |
| D | 2.25 | 4.21144e+09 | 23.1613 | 2.43135e+18 | 1.52205e+18 | 1.55304e+18 | 3.22255e-18 | 3.33744e-24 | - |
| D | 2.30 | 4.5254e+09 | 23.711 | 2.63332e+18 | 1.65544e+18 | 1.72042e+18 | 6.42429e-17 | 8.0217e-23 | 0.758176 |
| D | 2.35 | 4.83559e+09 | 24.2386 | 2.84837e+18 | 1.79542e+18 | 1.90466e+18 | 1.17088e-15 | 1.75285e-21 | 0.539826 |
| D | 2.40 | 5.14225e+09 | 24.7472 | 3.07769e+18 | 1.94327e+18 | 2.10757e+18 | 1.97593e-14 | 3.52947e-20 | 0.439224 |
| D | 2.45 | 5.44552e+09 | 25.2393 | 3.32248e+18 | 2.10003e+18 | 2.33115e+18 | 3.11849e-13 | 6.61863e-19 | 0.37841 |
| D | 2.50 | 5.74547e+09 | 25.7169 | 3.584e+18 | 2.26665e+18 | 2.57871e+18 | 4.64004e-12 | 1.16582e-17 | 0.336621 |
| D | 2.55 | 6.04213e+09 | 26.1815 | 3.86356e+18 | 2.44404e+18 | 2.83187e+18 | 6.55178e-11 | 1.94238e-16 | 0.30565 |
| D | 2.60 | 6.33552e+09 | 26.6346 | 4.16253e+18 | 2.63312e+18 | 3.09715e+18 | 8.82729e-10 | 3.07889e-15 | 0.281517 |
| D | 2.65 | 6.6256e+09 | 27.0773 | 4.48237e+18 | 2.83483e+18 | 3.37869e+18 | 1.14004e-08 | 4.66584e-14 | 0.262029 |
| D | 2.75 | 7.19575e+09 | 27.935 | 5.19099e+18 | 3.28016e+18 | 4.00009e+18 | 1.70031e-06 | 9.51455e-12 | 0.232176 |
| D | 3.00 | 8.56043e+09 | 29.9502 | 7.45006e+18 | 4.69074e+18 | 5.98823e+18 | 0.273679 | 3.23983e-06 | 0.185645 |
| D | 3.25 | 9.83346e+09 | 31.8271 | 1.0634e+19 | 6.66532e+18 | 8.8236e+18 | 25154.5 | 0.608285 | 0.15784 |
| D_best | 2.25 | 6.35112e+09 | 24.5543 | 2.75619e+18 | 1.73929e+18 | 1.87015e+18 | 2.3063e-15 | 3.60205e-21 | 0.607335 |
| D_best | 2.50 | 8.22186e+09 | 26.9038 | 4.01723e+18 | 2.54092e+18 | 3.04303e+18 | 1.43495e-09 | 5.15931e-15 | 0.292356 |
| D_best | 2.75 | 9.98739e+09 | 29.0021 | 5.78513e+18 | 3.64942e+18 | 4.63345e+18 | 0.000322514 | 2.50487e-09 | 0.215186 |
| D_best | 3.00 | 1.16411e+10 | 30.9371 | 8.27439e+18 | 5.19792e+18 | 6.88715e+18 | 37.4317 | 0.000602585 | 0.176183 |
| D_sq | 2.50 | 1.90735e+09 | 22.1155 | 2.45856e+18 | 1.51322e+18 | 1.51188e+18 | 1.00976e-19 | 8.42234e-26 | 1.68226 |
| D_sq | 3.00 | 3.53525e+09 | 27.2042 | 5.34875e+18 | 3.38245e+18 | 3.95022e+18 | 1.95904e-07 | 9.5774e-13 | 0.227133 |
| D_x2 | 2.00 | 2.34114e+10 | 27.1382 | 3.34656e+18 | 2.11641e+18 | 2.60737e+18 | 2.68006e-10 | 8.67672e-16 | 0.373808 |
| D_x2 | 2.50 | 3.26666e+10 | 31.1181 | 6.8685e+18 | 4.31284e+18 | 6.01177e+18 | 5.53313 | 7.90421e-05 | 0.193945 |
| D_x2 | 3.00 | 4.06108e+10 | 34.6397 | 1.38672e+19 | 8.62484e+18 | 1.29079e+19 | 1.8013e+10 | 1.01161e+06 | 0.142975 |

Windows (log10 rho sets):

| variant | y_s | 2L | 3L | NDA (<S>) | Z17 | 3L and Z17 | 3L and NDA (<S>) | NDA (M_s) | 3L and NDA (M_s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G6 | 0.30 | 3.00 | none | 3.00 | 3.00 | none | none | 3.00 | none |
| G6 | 0.34 | 3.00 | none | 3.00 | 3.00 | none | none | 3.00 | none |
| D | 0.30 | 2.30, 2.35, 2.40, 2.45, 2.50, 2.55, 2.60, 2.65, 2.75, 3.00, 3.25 | 2.55, 2.60, 2.65, 2.75, 3.00, 3.25 | 2.00, 2.25, 2.30, 2.35, 2.40, 2.45, 2.50, 2.55 | 2.00, 2.25, 2.30, 2.35, 2.40, 2.45, 2.50, 2.55, 2.60, 2.65, 2.75 | 2.55, 2.60, 2.65, 2.75 | 2.55 | 2.00, 2.25, 2.30, 2.35, 2.40, 2.45, 2.50, 2.55, 2.60, 2.65, 2.75 | 2.55, 2.60, 2.65, 2.75 |
| D | 0.34 | 2.30, 2.35, 2.40, 2.45, 2.50, 2.55, 2.60, 2.65, 2.75, 3.00, 3.25 | 2.55, 2.60, 2.65, 2.75, 3.00, 3.25 | 2.00, 2.25, 2.30, 2.35, 2.40, 2.45, 2.50, 2.55 | 2.00, 2.25, 2.30, 2.35, 2.40, 2.45, 2.50, 2.55, 2.60, 2.65, 2.75 | 2.55, 2.60, 2.65, 2.75 | 2.55 | 2.00, 2.25, 2.30, 2.35, 2.40, 2.45, 2.50, 2.55, 2.60, 2.65, 2.75 | 2.55, 2.60, 2.65, 2.75 |
| D_best | 0.30 | 2.25, 2.50, 2.75, 3.00 | 2.50, 2.75, 3.00 | 2.25 | 2.25, 2.50 | 2.50 | none | 2.25, 2.50, 2.75 | 2.50, 2.75 |
| D_best | 0.34 | 2.25, 2.50, 2.75, 3.00 | 2.50, 2.75, 3.00 | 2.25 | 2.25, 2.50 | 2.50 | none | 2.25, 2.50, 2.75 | 2.50, 2.75 |
| D_sq | 0.30 | 2.50, 3.00 | 3.00 | 2.50 | 2.50, 3.00 | 3.00 | none | 2.50, 3.00 | 3.00 |
| D_sq | 0.34 | 2.50, 3.00 | 3.00 | 2.50 | 2.50, 3.00 | 3.00 | none | 2.50, 3.00 | 3.00 |
| D_x2 | 0.30 | 2.00, 2.50, 3.00 | 2.50, 3.00 | none | 2.00 | none | none | 2.00 | none |
| D_x2 | 0.34 | 2.00, 2.50, 3.00 | 2.50, 3.00 | 2.00 | 2.00 | none | none | 2.00 | none |

Knife edge D log10 rho = 2.55: 3L = 2.44404e+18 GeV (margin 0.00371), NDA = 6.55e-11.

## (F) uncertainty (NUM)

| benchmark | Lambda_2L/Lambda_3L | 3L/2L term ratio at M_Pl,red |
| --- | --- | --- |
| BM-DA1 | 1.58886 | 0.319863 |
| BM-E | 1.58119 | 0.336621 |
| D_rho1e3 | 1.58825 | 0.185645 |

Term-ratio range over the 21 window rows whose two-loop alpha stays below 1 up to M_Pl,red (NUM): 0.143 to 1.682; values near or above 1 occur where the two-loop alpha approaches 1 at M_Pl,red. Research quote (RESEARCH_RECORD only): about 0.23-0.32 (VERIFY_feasibility.md); not a computed range.

b3 sensitivity at BM-DA1 (3L alpha = 1 scale): x0.5: 2.89871e+18, x0.75: 2.59766e+18, x1.25: 2.12513e+18.

## (G) planck_kinetic (EST)

delta alpha_i^-1 ~ c (M_X/M_Pl,red) alpha_U^-1 (group factors O(1) omitted); per unit c: BM-DA1 0.7655, BM-E 0.5265, D_rho1e3 0.4742. d ln Lambda/d alpha_U^-1 (NUM): 2L 0.2199, 3L_gauge_only 0.2271. per unit c the alpha = 1 scale moves by about 15-20% [EST], more than the three-loop margins at BM-DA1 (-3.8% on the U1 root, +0.14% on the U2 root): the three-loop verdict is convention- and threshold-limited. The FINAL '0.23c' is for M_U = 2.07e16 GeV (the G3221 lead), not BM-DA1.

## (H) research_record (not re-derived)

scratch research outputs of 2026-09-27 (wfRESCUE rescue study); not in the repository; hashes recorded for audit only; the source files are not in the repository and were hashed at generation time (the session scratch area that held them was wiped afterwards), so the sha256 values are a record of the inputs and are not re-verified at runtime. paths are relative to the session scratchpad; wfRESCUE/* is the 2026-09-27 rescue study, wfGNG/U1/* the D-C workstream U1 code (2026-09-26) that the rescue study drove read-only, wfREC/verify-M2/* the record PR's independent verifier (MSS 2012 text, PyR@TE 3 runs).

| entry | label | source | sha256 |
| --- | --- | --- | --- |
| c1_route_b_engine_root | RESEARCH_RECORD | wfRESCUE/critic/c1_f17_light1522_scan.json | 4481ba5df0ee232d... |
| c5_witness_chain_3loop | RESEARCH_RECORD | wfRESCUE/critic/c5_witness_chain_3loop.json | 8cd545b154edb641... |
| c6_landau_cost | RESEARCH_RECORD | wfRESCUE/C-other-extensions/c6_landau_cost.json | 78cc4eb01879dae3... |
| e4_so10_3loop | RESEARCH_RECORD | wfRESCUE/E-G7-completion/e4_so10_3loop.json | 19a85330788e9f75... |
| e5_u1_scheme_variants_rho1e3 | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/e5_crosscheck.json | 7244bc65daa5c754... |
| e6_summary_rows | RESEARCH_RECORD | wfRESCUE/E-G7-completion/e6_summary.json | ea19c9031175b03a... |
| j1f_planck_kinetic | RESEARCH_RECORD | wfRESCUE/final/j1_adjudication_checks.json | cd4b85a0983688cc... |
| mss2012_pgj_agreement | LIT | wfREC/verify-M2/mss2012.txt | 2b0df369fd026bfc... |
| mss_eq5 | LIT | wfRESCUE/E-G7-completion/verify-physics/mss.txt | 5430459c261b5572... |
| pgj_eqs_28_33 | LIT | wfRESCUE/E-G7-completion/verify-physics/pgj.txt | e3de10df9895c665... |
| pyrate3_so10_b3.no_PQR | RESEARCH_RECORD | wfREC/verify-M2/pyrate_out/VSO10noPQR/PythonOutput/RGEs.py | 9763855e8753873f... |
| pyrate3_so10_b3.with_PQR | RESEARCH_RECORD | wfREC/verify-M2/pyrate_out/VSO10PQR/PythonOutput/RGEs.py | 7a316a60eba04148... |
| remnant_masses_over_vR | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/e2_unif_D_ys0.0_3.0.json | d30403a2631e7edc... |
| u1_betas | RESEARCH_RECORD | wfGNG/U1/betas.json | 79328ca11341b563... |
| u1_chain_content | RESEARCH_RECORD | wfGNG/U1/rge.py | 04bb4ad527c05477... |
| u2_roots | RESEARCH_RECORD | wfRESCUE/E-G7-completion/e5_crosscheck.json | 7244bc65daa5c754... |
| v1_threeloop_coefficients | RESEARCH_RECORD | wfRESCUE/E-G7-completion/verify-physics/v1_threeloop.json | 38cd9b2f9033eaad... |
| v1_threeloop_landau | RESEARCH_RECORD | wfRESCUE/E-G7-completion/verify-physics/v1_threeloop.json | 38cd9b2f9033eaad... |
| verify_feasibility_quotes | RESEARCH_RECORD | wfRESCUE/E-G7-completion/VERIFY_feasibility.md | 770aa7ca8197e606... |
| window_roots.roots_e2_D_best | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/verify-feasibility/e2_unif_D_best_ys0.0_2.25_2.5_2.75_3.0.json | b7c55aca8bb7bf80... |
| window_roots.roots_e2_D_rho1e3 | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/e2_unif_D_ys0.0_3.0.json | d30403a2631e7edc... |
| window_roots.roots_e2_D_scan_a | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/e2_unif_D_ys0.0_1.5_1.75_2.0_2.25_2.5_2.75_3.25.json | 63a9a490c7a0217d... |
| window_roots.roots_e2_D_scan_b | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/e2_unif_D_ys0.0_2.3_2.35_2.4_2.45_2.55_2.6_2.65.json | ea935ae57b44a385... |
| window_roots.roots_e2_D_sq | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/e2_unif_D_sq_ys0.0_2.0_2.5_3.0.json | 2a40ba7d06d16b09... |
| window_roots.roots_e2_D_x2 | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/e2_unif_D_x2_ys0.0_2.0_2.5_3.0.json | 6035d598d04005df... |
| window_roots.roots_e2_G6_rho1e3 | RESEARCH_RECORD_INPUT | wfRESCUE/E-G7-completion/e2_unif_G6_ys0.0_3.0.json | 15265343e05ef9cf... |

## Scope

**claimed**

- EXACT: SO(10) representation data from the Weyl dimension formula; the PGJ single-group b1, b2, b3 of the SO(10) phase with and without P,Q,R (gauge + matter terms); PGJ = QCD with general Casimirs and = MSS eq. (5) as polynomials in n_G for U(1)_Y, SU(2)_L, SU(3)_C; b1, b2 = the repository's Machacek-Vaughn routine; every chain segment of code U1 re-derived as exact Fractions
- NUM: alpha_10 = 1 scales at 1L, 2L and 3L_gauge_only from the research-recorded roots of codes U1 and U2 with two integrators (<= 1e-6 agreement); BM-DA1 passes the reduced-Planck Landau criterion at two loops on both roots; at three loops (gauge-only) it fails on the U1 root (-3.8%) and passes marginally on the U2 root (+0.14%), so its three-loop outcome lies within the two-code root uncertainty; BM-E passes at two loops and fails at three loops on both roots
- NUM: every analysed SO(10)-phase addition at mu_G fails at three loops at BM-DA1 (root held fixed: a lower bound on the damage); a 120_H, a second 126bar and vectorlike pairs fail already at two loops
- NUM: axion quality (NDA with Lambda = <S> and with Lambda = M_s, Z17-EFT) at every recorded root; BM-DA1 with the G6 masses passes
- NUM, CONDITIONAL: the rho = 1e3 root with the RG-improved remnant masses (anti-SOS region points, committed GUT scalar spectrum) fails both bounds; the GUT scalar masses x2 scheme variant removes the failure, U2 and the other six scheme variants keep the Z17 failure
- NUM, CONDITIONAL: the rho windows of the recorded scan

**not_claimed**

- the two-loop unification roots are research-recorded (codes U1 and U2; one-loop MS-bar thresholds at v_R and M_X), not re-derived here
- the SO(10)-phase running is gauge + matter only at every order: the two-loop Yukawa terms (16.16.10_H, 16.16.126bar_H, y_s S 16_s 16bar_s) and the three-loop Yukawa and quartic terms are omitted; the Yukawa terms enter d alpha^-1/dt with a positive sign and would raise the alpha = 1 scale, so their omission is not conservative for a fail statement
- the 3L_gauge_only SO(10) segment sits on a two-loop root with one-loop thresholds: the unknown two-loop GUT thresholds are of the same formal order as the three-loop term, so the BM-DA1 three-loop margins (-3.8% on the U1 root, +0.14% on the U2 root) are below the neglected effects
- U(1)_X feedback on the SO(10) running is neglected; the SO(10) phase is a single coupling
- the GUT-scale thresholds are uncontrolled: BM-DA1 uses the committed spectrum, whose normalisation is non-perturbative (a0 ~ 21.6, g3_sm_pati_salam_witness_unitarity_v20); on the perturbative x1/50 member every scalar tree mass (the six remnants below v_R and the GUT scalars) scales by 1/sqrt50 and the root, Landau and quality numbers are not recomputed here; the GUT scalar masses x0.5 and x2 scheme variants alone move the rho = 1e3 root from v_R = 3.1e10 to 1.96e9 GeV (a factor 16; the rescue synthesis quotes up to x30)
- the Planck gauge-kinetic term c Phi210 F F/M is not computed (EST only); it moves the alpha = 1 scale by more than the three-loop margins (-3.8% on the U1 root, +0.14% on the U2 root), so the three-loop verdict is convention- and threshold-limited
- the RG-improved remnant masses come from anti-SOS region points: G6 is not closed and is not assumed closed
- no benchmark is adopted; the windows are conditional evidence, not a G7 closure
- no gate status changes; nothing is wired into the gate ledger; G7 stays BLOCKED

## Disclosures

- `critic_engine_not_independent`: the critic's Route-B engine reproduces the U1 root and scales bit for bit: a reproduction, not an independent code; the independent checks are U2 (roots) and v1 (scales)
- `e2_hard_coded_quality_flags`: the e2 JSON flags are thresholds for rho = 1e3; at BM-E they say False where both bounds pass
- `e6_duplicated_landau_columns`: e6 keys its Landau columns by (variant, log10 rho): both D log10 rho = 2.00 roots carry the second root's values; they are excluded from the record comparison
- `nda_convention`: the NDA bound uses Lambda = max(M_s, <S>) = <S> = M_s/y_s, more conservative by y_s^-16 (2.3e8 at y_s = 0.30) than the manuscript's eq. (qualitybound) with Lambda = M_s; the windows are recorded under both (3L and NDA: {2.55} with Lambda = <S>, {2.55, 2.60, 2.65, 2.75} with Lambda = M_s for the D variant); the rho = 1e3 RG-improved failure holds under both (NDA with Lambda = M_s 1.2e-9 > 1e-10; Z17 3.2e-6)
- `normalisation_nonperturbative`: BM-DA1 uses the committed spectrum, whose normalisation is non-perturbative (singlet-channel a0 ~ 21.6, g3_sm_pati_salam_witness_unitarity_v20); on the perturbative x1/50 member every scalar tree mass (the remnants below v_R and the GUT scalars) scales by 1/sqrt50 and the root, Landau and quality numbers are not recomputed; the GUT scalar masses alone move the rho = 1e3 root by a factor 16 across the x0.5/x2 scheme variants (the rescue synthesis quotes up to x30)
- `planck_kinetic`: per unit c the alpha = 1 scale moves by about 15-20% [EST], more than the three-loop margins at BM-DA1 (-3.8% on the U1 root, +0.14% on the U2 root): the three-loop verdict is convention- and threshold-limited
- `pqr_placement`: with P,Q,R at M_Pl,red instead of x0 p BM-DA1 passes three loops marginally (+0.8%) and BM-E passes (+5.9%), but that places U(1)_X breaking at the cutoff, where the EFT and the certified renormalisable vacuum lose meaning; the recorded verdict uses P,Q,R at x0 p
- `rg_improved_quality_scheme_dependence`: doubling the GUT scalar masses removes the RG-improved quality failure (three loops and both bounds pass); U2 and every other scheme variant keep the Z17 failure (and the NDA failure with Lambda = <S>; with Lambda = M_s the mu_G = 2 M_X variant passes NDA but still fails Z17)
- `so10_phase_yukawa_terms_omitted`: the SO(10)-phase running is gauge + matter only at every order: the two-loop Yukawa terms (16.16.10_H, 16.16.126bar_H, y_s S 16_s 16bar_s) are omitted as well as the three-loop Yukawa and quartic terms; they enter d alpha^-1/dt with a positive sign and would raise the alpha = 1 scale, so the omission is not conservative for the fail statements
- `term_ratio_quote`: the research quote '3L/2L ~ 0.23-0.32' is research-recorded only; the module states its own per-root values and range (uncertainty.term_ratio_3L_over_2L_at_MPlred)
- `three_loop_on_two_loop_root`: the 3L_gauge_only SO(10) segment is run from a two-loop root with one-loop MS-bar thresholds; the unknown two-loop GUT thresholds are of the same formal order as the three-loop term, so the three-loop margins are below the neglected effects
- `two_code_root_uncertainty`: run through this module's integrators, the U1 BM-DA1 root fails three loops by -3.8% and the second-code U2 root passes by +0.14%: the gap between the two codes' three-loop scales exceeds the U1 miss, so the BM-DA1 three-loop outcome lies within the two-code root uncertainty (a two-loop pass is the robust statement)
- `windows_conditional`: the rho windows that pass three loops and a quality bound use the RG-improved remnant masses of anti-SOS region points (G6 not closed), uncontrolled GUT thresholds and gauge-only three loops: conditional evidence only, not a benchmark

## Checks

- PASS `coefficients.chain_segments_match_u1_record`
- PASS `coefficients.landau_option_coefficients_exact`
- PASS `coefficients.mv_two_loop_reproduces_pgj_b1_b2`
- PASS `coefficients.pgj_matches_mss_as_nG_polynomials`
- PASS `coefficients.pgj_mss_values_at_nG_3`
- PASS `coefficients.pgj_reproduces_qcd_general_casimirs`
- PASS `coefficients.remnant_delta_b_match_u1_record`
- PASS `coefficients.so10_index_casimir_relation`
- PASS `coefficients.so10_phase_coefficients_pinned`
- PASS `coefficients.so10_rep_data_from_weyl_formula`
- PASS `coefficients.so10_segments_match_u1_record`
- PASS `coefficients.two_loop_module_provenance`
- PASS `landau_cost.every_option_fails_three_loop`
- PASS `landau_cost.scales_match_research_records`
- PASS `landau_cost.scales_pinned`
- PASS `landau_cost.two_loop_pass_fail_split`
- PASS `planck_kinetic.dlnLambda_daU_inv`
- PASS `planck_kinetic.estimate_arithmetic_matches_j1f_record`
- PASS `quality.bm_da1_g6_masses_pass_both_bounds`
- PASS `quality.e2_hard_coded_flags_disagree_at_bm_e`
- PASS `quality.matches_e6_record`
- PASS `quality.rg_improved_failure_scheme_dependence_pinned`
- PASS `quality.rg_improved_remnants_fail_both_bounds`
- PASS `research_record.entries_labelled_with_provenance`
- PASS `research_record.files_digest_pinned`
- PASS `research_record.remnant_masses_consistent`
- PASS `research_record.two_code_roots_and_reproduction`
- PASS `running.bm_da1_matches_research_records`
- PASS `running.bm_da1_pqr_at_planck_three_loop_marginal`
- PASS `running.bm_da1_scales_pinned`
- PASS `running.bm_da1_two_loop_pass_three_loop_fail_on_U1_root`
- PASS `running.bm_e_matches_research_records`
- PASS `running.bm_e_two_loop_pass_three_loop_fail`
- PASS `running.d_remnant_rho1e3_landau_pass_and_matches_records`
- PASS `running.integrators_agree`
- PASS `running.u2_roots_pinned_bm_da1_two_loop_pass_three_loop_marginal_pass`
- PASS `scope.g7_blocked_and_status_neutral`
- PASS `uncertainty.b3_sensitivity_matches_record`
- PASS `uncertainty.three_to_two_loop_term_ratios`
- PASS `uncertainty.two_to_three_loop_scale_ratios`
- PASS `verdict.physics_flags_from_numbers`
- PASS `windows.d_best_windows_pinned`
- PASS `windows.d_variant_windows_pinned`
- PASS `windows.knife_edge_point`
- PASS `windows.rows_complete_and_match_records`
- PASS `windows.y_s_034_windows_same`
