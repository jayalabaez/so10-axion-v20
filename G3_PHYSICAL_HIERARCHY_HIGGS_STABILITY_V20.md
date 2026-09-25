# Higgs-vacuum stability in an SM + singlet EFT at the repository scales -- v20

**Status:** `G3_SM_SINGLET_EFT_HIGGS_STABILITY__TUNED_POINT_TREE_SADDLE_FOR_GUT_OR_M_I_MATCHING__EW_VACUUM_METASTABLE_AT_BUTTAZZO_CENTRAL_INPUTS__G3_OPEN`

Within an SM + complex-singlet EFT (not the repository's 2HDM + Pati-Salam anchor chain, and not realized by any current repository vacuum, whose Delta_R is not the SM singlet): two-loop SM running from the Buttazzo et al. inputs puts the MSbar instability scale at 4.76e+09 GeV, a factor 133 below M_I, with lambda_SM(M_I) = -0.00854 and lambda_SM(M_GUT) = -0.01511 (one loop: -0.0335). With the H-S portal threshold at M_I, positive-portal windows keep lambda_H > 0 up to M_GUT for every scanned lambda_S. Copositivity is not the tree-level local-minimum condition (the single-stage point is copositive too). At the tuned point of the tree potential the condition is lambda_eff = lambda_H - lambda_HS^2/(4 lambda_S) >= 0 (g3_tuned_target_portal_threshold_v20). With the S threshold at M_I, lambda_eff(M_I) = lambda_SM(M_I) = -0.0085 < 0, so the M_I threshold does not remove the tree-level saddle; at the GUT coefficients lambda_eff is -0.073 for the O36 = O23 = 1 benchmark and negative at 4 of 5 window middles. Metastability is the RG-improved statement. In the RG-improved potential the EW vacuum is still not the global minimum at central inputs, because the SM segment [Lambda_I, M_I] has lambda_SM < 0; the bounce estimate S ~ 3082 far exceeds the ~500 needed, so it is metastable and long-lived (estimate). At tree level with the S vev the EW/S point is a local (and then global) minimum iff lambda_SM(threshold) >= 0, so at central inputs it is the tree-level saddle stated above. Absolute stability with the threshold at M_I needs M_t < 171.96 GeV (2L) / 172.07 GeV (3L) with the MSbar criterion. With PDG 2024 M_h and alpha_s this becomes 171.95 GeV, 2.0 sigma below the measured 172.57 +- 0.29 GeV; with the Landau-gauge effective-potential zero it is ~172.36 GeV (0.7 sigma). The alternative is a radial mode below Lambda_I, i.e. lambda_S <~ 1.4e-05, far from the certified O23 = 1 (RG-improved: lambda_eff(m_rho) > 0 there, but lambda_eff at the GUT coefficients is negative at every scanned window point). Keeping O36 = O23 = 1 needs O34 = lambda_HS(M_GUT) = 2.072 (RG-improved metastable; a tree-level saddle, since O34 > 2 at O36 = O23 = 1). Single-stage GUT matching needs lambda_eff(M_GUT) = -0.0151 at two loops (negative at every loop order), so that tuned point is not a tree-level local minimum either. The RG-improved M_I-threshold conclusions are marginal: they depend on M_t (1-2 sigma), on the MSbar versus effective-potential instability criterion, and on the omitted states listed in the scope. This is an RG-improved EFT statement, not an exact lower witness of the 486-field tree potential: G3 stays open and the model is neither validated nor excluded.

## SM running (Buttazzo et al. 1307.3536 v3/v4 inputs, mu0 = M_t = 173.34 GeV)

| run | Lambda_I [GeV] | lambda(M_I) | lambda(M_GUT) | lambda(M_Pl) | lambda_min |
|---|---|---|---|---|---|
| 1L_superseded_5f25846_mu0_173.10 | 9.149e+07 | -0.024830 | -0.033536 | -0.033701 | -0.034083 |
| 1L | 9.162e+07 | -0.024828 | -0.033535 | -0.033701 | -0.034083 |
| 2L | 4.765e+09 | -0.008539 | -0.015112 | -0.015079 | -0.015454 |
| 3L+4QCD | 6.19e+09 | -0.007881 | -0.014393 | -0.014361 | -0.014732 |

| M_t [GeV] | loops | Lambda_I [GeV] | lambda(M_I) | lambda(M_GUT) | lambda(M_Pl) |
|---|---|---|---|---|---|
| 172.34 | 2L | 1.123e+11 | -0.002320 | -0.008542 | -0.008611 |
| 173.34 | 2L | 4.765e+09 | -0.008539 | -0.015112 | -0.015079 |
| 174.34 | 2L | 5.662e+08 | -0.014909 | -0.021785 | -0.021602 |
| 172.34 | 3L+4QCD | 1.732e+11 | -0.001675 | -0.007834 | -0.007900 |
| 173.34 | 3L+4QCD | 6.190e+09 | -0.007881 | -0.014393 | -0.014361 |
| 174.34 | 3L+4QCD | 6.798e+08 | -0.014237 | -0.021056 | -0.020878 |

## Top-mass bound and metastability (threshold at M_I)

- Absolute stability needs Lambda_I >= M_I: M_t < `171.961` GeV (2L), `172.066` GeV (3L+4QCD); with M_h = 125.20, alpha_s = 0.1180: `171.841` / `171.946` GeV (matching theory error +-0.12 GeV).
- With the Landau-gauge effective-potential zero (~6.5 x the MSbar zero) instead: `172.480` GeV (3L), `172.363` GeV (3L, PDG 2024 M_h, alpha_s); an estimate.
- Measured M_t = 172.57 +- 0.29 GeV: 2.0 sigma above the 3L MSbar bound, 0.7 sigma above the effective-potential estimate.
- PDG 2024 central inputs (3L): MSbar zero `4.5e+10` GeV, effective-potential zero ~`2.92e+11` GeV, both below M_I; lambda_SM(M_I) = `-0.00384`.
- Window [Lambda_I, M_I]: lambda_min = `-0.00854`, bounce action S ~ `3082` vs ~494 needed; max log10 p ~ `-1124` (estimate).

## Portal windows at M_I (lambda_H > 0 and |lambda| < 4 pi up to M_GUT)

| lambda_S(M_I) | lambda_HS min | lambda_HS max | delta min | (lambda_H, lambda_S, lambda_HS)(M_GUT) at middle | tree lambda_eff(M_GUT) at middle | class |
|---|---|---|---|---|---|---|
| 0.01 | 0.02519 | 0.2085 | 0.01586 | (0.1350, 0.0108, 0.0799) | -0.0123 | METASTABLE_LONG_LIVED_ESTIMATE |
| 0.05 | 0.05604 | 0.4340 | 0.01570 | (0.1233, 0.0569, 0.1782) | -0.0163 | METASTABLE_LONG_LIVED_ESTIMATE |
| 0.1 | 0.07873 | 0.5922 | 0.01549 | (0.1184, 0.1217, 0.2570) | -0.0173 | METASTABLE_LONG_LIVED_ESTIMATE |
| 0.2 | 0.10975 | 0.7985 | 0.01506 | (0.1132, 0.2834, 0.3826) | -0.0159 | METASTABLE_LONG_LIVED_ESTIMATE |
| 0.5 | 0.16417 | 1.0942 | 0.01348 | (0.1012, 1.4015, 0.7520) | +0.0003 | METASTABLE_LONG_LIVED_ESTIMATE |

- Tree level: lambda_eff(M_I) = lambda_SM(M_I) = `-0.00854` for every M_I solution, so the M_I-matched tuned point is a tree-level saddle; the classes above are RG-improved. Metastable grid rows with lambda_eff(M_GUT) >= 0: 2 of 14.
- Certified benchmark (1, 1, 0) at M_GUT: lambda(M_t) = `0.2468`, m_h(tree) = `173.0` GeV (two loops).
- Keeping O36 = O23 = 1: lambda_S(M_I) = `0.3623`, lambda_HS(M_I) = `0.7616`, O34 = lambda_HS(M_GUT) = `2.0719`; class `METASTABLE_LONG_LIVED_ESTIMATE` (RG-improved); tree-level lambda_eff(M_GUT) = `-0.0732`, a saddle.
- Radial-mode threshold m_rho = 2 sqrt(lambda_S) M_I is below Lambda_I iff lambda_S < `1.42e-05`:
  - lambda_S = 1e-06: m_rho = 1.26e+09 GeV, below Lambda_I: True; lambda_HS in [0.000251, 0.00191]; class ABSOLUTELY_STABLE_TO_M_GUT; tree lambda_eff(m_rho) = +0.0033, lambda_eff(M_GUT) at middle = -0.0024 (class RG-improved)
  - lambda_S = 1e-05: m_rho = 3.99e+09 GeV, below Lambda_I: True; lambda_HS in [0.000796, 0.00601]; class ABSOLUTELY_STABLE_TO_M_GUT; tree lambda_eff(m_rho) = +0.0004, lambda_eff(M_GUT) at middle = -0.0043 (class RG-improved)
  - lambda_S = 0.0001: m_rho = 1.26e+10 GeV, below Lambda_I: False; lambda_HS in [0.00252, 0.0189]; class METASTABLE_LONG_LIVED_ESTIMATE; tree lambda_eff(m_rho) = -0.0021, lambda_eff(M_GUT) at middle = -0.0062 (class RG-improved)
  - lambda_S = 0.01: m_rho = 1.26e+11 GeV, below Lambda_I: False; lambda_HS in [0.0252, 0.187]; class METASTABLE_LONG_LIVED_ESTIMATE; tree lambda_eff(m_rho) = -0.0062, lambda_eff(M_GUT) at middle = -0.0127 (class RG-improved)

## Single-stage matching at M_GUT (portal module; the 1L mu0 = 173.10 row reproduces the superseded commit-5f25846 value)

- lambda_eff(M_GUT) required: 1L (mu0 173.10) `-0.0335`, 2L `-0.0151`, 3L `-0.0144`: negative, so the tuned point is not a tree-level local minimum.
- lambda_eff(M_GUT) = 0 would give m_h(tree) = `128.2` GeV (scaled `129.8` GeV) at two loops; lambda_SM(M_GUT) >= 0 needs M_t < `171.02` GeV (2L).

Checks: 25/25 passed. G3: `OPEN`; whole model: neither validated nor excluded.

## Scope

- Only the complex singlet S is kept between M_I and M_GUT. Other states near M_I are omitted: any colour-triplet partner (the F-branch formula extrapolated to M_I gives sqrt(beta) M_I ~ 1.4e11 GeV, but no such state has been constructed) and light Sigma_126bar components.
- The axion-sector vector-like fermion Yukawas (y S Q Qbar), which drive lambda_S through -6 y^4 and 12 y^2 lambda_S, are omitted, as are right-handed-neutrino Yukawas.
- Threshold matching is tree level at mu = M_I (or at m_rho in the radial-mode scan). One-loop threshold corrections and the log of m_rho/M_I are omitted.
- Portal running is one loop; the singlet-only two-loop pieces from SMASH App. A enter only as a sensitivity estimate. SM running below M_I is two loop (three loop + four-loop QCD as a cross-check).
- Stability is judged on the RG-improved tree potential, with lambda evaluated at mu ~ field value. The MSbar zero Lambda_I is not the Landau-gauge effective-potential zero, which is ~6.5x higher (Buttazzo et al.). Both sit below M_I at the Buttazzo and PDG 2024 central inputs. The top-mass bound moves by ~0.4 GeV between the two definitions, and it is quoted for both.
- The vacuum-decay numbers use the tree-level Fubini bounce, with no quantum, gravitational or thermal corrections. They are estimates.
- Tree-level local minimality at the tuned point (lambda_eff >= 0) is evaluated on the (H, S) block only, at M_I and at the running GUT values; it is a necessary condition, not a 486-field Hessian test.
- Identifying the GUT-scale light-field quartics with the tree-level coefficients O36_B02, O23 and O34 assumes no heavy-exchange shifts at M_GUT for S and HS; only the H shift was shown to vanish.
- This is not an exact lower witness of the 486-field tree potential; the G3 gate stays open.
- EFT mismatch: the repository's M_I/M_GUT anchor (two_loop_thresholds_v20 chain) runs a 2HDM below M_I and Pati-Salam above it, while this module runs the one-doublet SM below M_I and SM + singlet above. In a 2HDM the stability conditions differ (lambda3, lambda4 raise beta_lambda1,2), so the no-absolute-stability conclusions hold only if the low-energy EFT is exactly the SM.
- No current repository vacuum realizes this EFT: the certified Delta_R (direct.delta_r) is the T3R = 0, Y = -1 component of the 126bar triplet, not the SM singlet (g3_sigma_hypercharge_audit_v20).
- Above M_N ~ f M_I, SO(10) Dirac neutrino Yukawas y_nu ~ y_t add -2 y_nu^4 to beta_lambda_H; the dynamical Delta_R and its portals give further thresholds (a matrix over the S and Delta_R radial modes) and make lambda_HS = 0 non-RG-invariant at one loop.
- For lambda_S << lambda_HS the relevant scale is the valley end h_c ~ sqrt2 (lambda_S/delta)^(1/4) M_I rather than m_rho; the radial-mode scan treats the threshold at m_rho and is optimistic there.
- The Fubini bounce at 1/R ~ M_I has a central field above the threshold; the action is used as a conservative lower bound (V >= lambda_SM(M_I) |H|^4 at tree level). Inflationary and thermal Higgs fluctuations are not addressed.
- With PDG 2024 inputs, the effective-potential criterion and matching at m_rho, absolute stability is allowed for small lambda_S; the 'metastable at central inputs' status refers to the Buttazzo 2013 central values and the MSbar criterion.
