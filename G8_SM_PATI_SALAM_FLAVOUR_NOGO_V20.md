# G8 flavour no-go on the SM Pati-Salam G3 witness branch (Route C, v20)

- Status: `G8_SM_PATI_SALAM_WITNESS_FLAVOUR_NOGO__ROUTE_C_RECORDED__G8_OPEN`
- Overall state: `WITNESS_BRANCH_FLAVOUR_EXCLUDED_AT_RENORMALIZABLE_TREE_LEVEL`; G8: **OPEN**
- Checks: 103/103 pass

## Verdict

On the SM Pati-Salam G3 witness branch (renormalizable 27-parameter benchmark family, H-linear portals zero) the light Higgs doublet is exactly the 10_H direction Re H_6..9 and, with the contract's renormalizable Yukawas, M_u = c_u Y, M_d = c_d Y, M_e = c_e Y^T, M_D = c_nu Y^T with |c_u| = |c_d|: CKM = 1, m_t = m_b, m_d = m_e, m_s = m_mu, M_D = M_u, and the 126bar enters only M_R.  The tan-beta-independent tests are excluded by at least 13.2 sigma (experimental errors) and 8.9 sigma (with a 10% theory term) across 1e9-2e16 GeV.  The O28 portal alone (the largest direct 10_H-(15,2,2) portal, other portals zero) gives theta = |c| r0^2 sqrt(R(r0)) <= 2.40e-05 at the anchor r0 with |c| <= 4 pi for the witness doublet (<= 3.39e-05 for any tan beta); its admixture is purely up-type, so it cannot split b from tau at all, and repairing the t-b split needs ||Y_F|| >= 5786 at every repository r0 inside the colour-stable range (Mirsky; Y_F the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2)).  With all five H-linear portals on at q0, the full H block (colour triplets included) gives the second-order colour-stable region: |c_O15| <= 0.791 at every repository r0 (the H triplets couple to the 126bar (6,1,1) through <Phi> at O(1); beyond it q0 has GUT-scale (3,1)_|Y|=1/3 tachyons), |c_O28| <= rho_O28(r0) ~ 1/r0 (4.54 at candidate_PS_content_with_2HDM_below_M_I, 14.1 at anchor_content_local_chain, 17 at candidate_PS_content_with_1HDM_below_M_I, 230 at candidate_content_with_1HDM_and_sub_M_I_remnants; below 4 pi at candidate_PS_content_with_2HDM_below_M_I), O38 and O45 colour-stable in the box; raising O06 cures only the doublet saddle (it lifts triplets and doublets alike and the doublet must stay light); inside it O45_B02_Phi2_Hdag_Sigma_210_1050 still moves tan beta past m_t/m_b (O15 only beyond its colour radius), so the O28-alone t-b bound does not survive the portal set.  But every portal-induced 126bar (15,2,2) vev is purely up-type (exact: the induced 16.16 couplings are only Q u^c and L nu^c at every repository r0), so M_e = phase x M_d^T survives every portal combination at any coefficient and the portal-immune tests (m_s/m_d)/(m_mu/m_e) and (m_b/m_s)/(m_tau/m_mu) stay excluded by >= 34.8 sigma (10.0 sigma with the theory term): no in-contract H-linear portal repair of the flavour sector survives at any repository r0.  Every doublet-coupled portal c != 0 turns the certified witness into a saddle (SOS27 needs portal = 0), so any repair needs a new G3 certificate (Route A).  If M_D = M_u(data) (the generic SO(10) premise, not the witness's own M_D), the seesaw needs a non-perturbative Y_126 for generic textures (a tuned texture can evade this, so it is not load-bearing).  Route C is recorded; G8 stays OPEN; the G3-G5 certificates and the SO(10) contract are not falsified.

## (1) The light doublet is pure 10_H (exact)

- H-linear directions: O15_B01_Phi_Hdag_Sigma, O28_B01_unique_Hdag_Sigma2_Sigmadag, O38_B01_Phi_Hdag_Sigmadag, O45_B01_Phi2_Hdag_Sigma_210_1050, O45_B02_Phi2_Hdag_Sigma_210_1050 (all re/im parameters zero).
- Nonzero H-quadratic parameters: lambda::O06_B01_Hdag_H_norm, lambda::O46_B01_Phi2_HdagH_channels, lambda::O46_B03_Phi2_HdagH_channels, re::O12_B01_Hdag_Hdag_pair.

| r0 | gradient 0 | H block decoupled | H block = exact formula | Re H_6..9 null |
|---|---|---|---|---|
| 1/5 | True | True | True | True |
| 1/20 | True | True | True | True |
| 1/100 | True | True | True | True |
| 51544138/809635808795 | True | True | True | True |

## (2) Clebsches, contract couplings and flavour relations (exact)

- Clebsches at v = a e8 + b e9: d[+--] = -I*a + b, d[-+-] = I*a - b, d[--+] = -I*a + b, e[+++] = I*a - b, nu[+++] = I*a + b, u[+--] = -I*a - b, u[-+-] = I*a + b, u[--+] = -I*a - b.
- Moduli: all equal to a^2 + b^2 (tan beta = 1). sigma_std bilinear: [['nuc[---]', 'nuc[---]', [0, 32]]].
- (15,2,2) relative lepton/quark Clebsch: -3, -3.
- H10 Yukawas allowed: H10.F.F, H10.F.P, H10.F.R, H10.P.P, H10.P.R, H10.R.R; 126bar Yukawas: Delta126bar.F.F, Delta126bar.F.P, Delta126bar.F.R, Delta126bar.P.P, Delta126bar.P.R, Delta126bar.R.R; 16.16.conj[H10]: none.
- Allowed but undeclared renormalizable couplings: Delta126bar.F.P, Delta126bar.F.R, Delta126bar.P.P, Delta126bar.P.R, Delta126bar.R.R, H10.P.P, H10.P.R, H10.R.R, Phi17.F.Rbar, Phi17.P.Rbar, conj[Delta126bar].Pbar.Rbar, conj[H10].Pbar.Rbar, conj[Phi17].F.Pbar, conj[Phi17].R.Pbar, conj[S].P.Qbar, conj[S].R.Qbar.
- Predictions: {"(m_b/m_s)/(m_tau/m_mu)": "1", "(m_c/m_u)/(m_s/m_d)": "1", "(m_s/m_d)/(m_mu/m_e)": "1", "(m_t/m_c)/(m_b/m_s)": "1", "M_D": "M_u (up to rephasing)", "M_R": "Y_126 v_R", "V_CKM": "1 (diagonal phases)", "m_d/m_e = m_s/m_mu = m_b/m_tau": "1", "m_u/m_d = m_c/m_s = m_t/m_b": "1"}

## Data comparison (float)

| test | prediction | data | pull (raw) | pull (10% theory) |
|---|---|---|---|---|
| |V_us| | 0 (V_CKM = 1, preserved by SM running) | 0.2243 | 280.4 | 9.994 |
| |V_cb| | 0 (V_CKM = 1, preserved by SM running) | 0.0411 | 34.25 | 9.599 |
| |V_ub| | 0 (V_CKM = 1, preserved by SM running) | 0.00382 | 19.1 | 8.859 |
| (m_c/m_u)/(m_s/m_d) = (m_c/m_s)(m_d/m_u) | 1 | 25.31 | 62.5 | 28.7 |
| (m_s/m_d)/(m_mu/m_e) | 1 | 0.09647 | 68.02 | 22.12 |

| scale | (m_t/m_c)/(m_b/m_s) | (m_b/m_s)/(m_tau/m_mu) | m_t/m_b | m_b/m_tau |
|---|---|---|---|---|
| 1e+09 GeV | 6.123 (10.69 sigma) | 2.908 (10.22 sigma) | 69.73 | 0.829 |
| 1e+10 GeV | 6.216 (10.78 sigma) | 2.886 (10.15 sigma) | 70.62 | 0.7865 |
| 1e+11 GeV | 6.303 (10.86 sigma) | 2.866 (10.08 sigma) | 71.44 | 0.7502 |
| 1e+12 GeV | 6.384 (10.94 sigma) | 2.848 (10.02 sigma) | 72.18 | 0.7189 |
| 1e+13 GeV | 6.46 (11.01 sigma) | 2.831 (9.965 sigma) | 72.85 | 0.6916 |
| 2e+16 GeV | 6.68 (11.21 sigma) | 2.784 (9.804 sigma) | 74.66 | 0.6227 |
| M_I[anchor_content_local_chain] | 6.368 (10.92 sigma) | 2.851 (10.03 sigma) | 72.03 | 0.7248 |
| M_I[candidate_PS_content_with_1HDM_below_M_I] | 6.365 (10.92 sigma) | 2.852 (10.04 sigma) | 72.01 | 0.7259 |
| M_I[candidate_PS_content_with_2HDM_below_M_I] | 6.385 (10.94 sigma) | 2.847 (10.02 sigma) | 72.19 | 0.7182 |
| M_I[candidate_content_with_1HDM_and_sub_M_I_remnants] | 6.294 (10.85 sigma) | 2.868 (10.09 sigma) | 71.35 | 0.7539 |

Minimum load-bearing pull: 13.2 sigma (raw), 8.9 sigma (10% theory).

## (3) The O28 portal alone (exact / parametric)

- O28 alone (the other H-linear portals zero): O28 is the largest direct 10_H-(15,2,2) portal.  The portal-set analysis (all five directions on the full H block, the colour-stable region and the tan beta freedom from O45_B02) is section H_linear_portals.
- theta = |c| r0^2 sqrt(R(r0)), R(r) = 7962624 (13 r^2 + 6)^2/(13 r^4 + 12 r^2 + 36)^2, theta -> 192 sqrt(6) |c| r0^2 = 470.30 |c| r0^2 (r0 -> 0) for the witness light doublet Re H_6..9 (tan beta = 1); for a light doublet with t = |5|/|5bar| the admixture is sqrt(2 t^2/(1 + t^2)) times this (<= sqrt(2) times, exact Gram structure of section H_linear_portals); c = the compiler's re:: or im:: O28 coefficient (complex c: theta^2 = |c|^2 r0^4 R, the re/im admixtures are orthogonal).
- |c| <= 4 pi is applied to the compiler coefficient, whose operator has lattice entry 192 in the H-Sigma block: this is generous and overestimates theta, which is conservative for the no-go.  The colour-stable range is smaller where the colour radius rho_O28(r0) (~ 1/r0) is below 4 pi.
- Closed form derived: R(r) = 7962624*(13*r**2 + 6)**2/(13*r**4 + 12*r**2 + 36)**2; light-doublet shift = c^2 r^4 x -663552*(13*r**2 + 6)/(13*r**4 + 12*r**2 + 36).

| r0 | theta/(c r0^2) | shift/(c^2 r0^4) | saddle for c != 0 |
|---|---|---|---|
| 1/5 | 504.0496 | -118528 | True |
| 1/20 | 472.4547 | -111098 | True |
| 1/100 | 470.3882 | -110612 | True |
| 51544138/809635808795 | 470.3020 | -110592 | True |
| 48406501/760350994483 | 470.3020 | -110592 | True |
| 29753684/565180975619 | 470.3020 | -110592 | True |
| 24281534/123126730703 | 470.3021 | -110592 | True |
| 2152851/552262714325 | 470.3020 | -110592 | True |

| repository scale | r0 | colour radius | abs c max (colour-stable) | theta (abs c = 4 pi, tan beta = 1) | theta max (colour-stable, any tan beta) | tan beta max | Y_F needed (t-b) | admixture up-type only |
|---|---|---|---|---|---|---|---|---|
| anchor_content_local_chain | 6.366e-05 | 14.05 | 12.57 | 2.395e-05 | 3.388e-05 | 1.152 | 2.05e+04 | True |
| candidate_PS_content_with_1HDM_below_M_I | 5.264e-05 | 17 | 12.57 | 1.638e-05 | 2.316e-05 | 1.101 | 3.07e+04 | True |
| candidate_PS_content_with_2HDM_below_M_I | 1.972e-04 | 4.537 | 4.537 | 2.298e-04 | 1.174e-04 | 1.193 | 5.79e+03 | True |
| candidate_content_with_1HDM_and_sub_M_I_remnants | 3.898e-06 | 229.5 | 12.57 | 8.981e-08 | 1.270e-07 | 1.001 | 6.07e+06 | True |

Findings: {"b_tau_repairable_by_O28": false, "colour_radius_below_4pi_at": ["candidate_PS_content_with_2HDM_below_M_I"], "second_order_Re_Im_H_mixing_present": true}

Y_F denotes the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2); it differs from the contract's declared Y126 and from the seesaw Y_R by unfixed Clebsch normalisations (the t-b bound is far above 4 pi, so the O(1) normalisation does not matter).  The O28 admixture of the light doublet is purely up-type (exact selection rule of section H_linear_portals: O28 acts only on the Y = +1/2 doublet component and its induced 126bar vev couples only Q u^c and L nu^c), so alpha_d = 0: M_d and M_e keep only their 10_H parts, M_e = phase x M_d^T, and the b-tau split is not generated at any ||Y_F|| (the earlier alpha_d-free b-tau estimate is withdrawn).  M_u - t e^{i phi} M_d = sin(theta(t)) Y_F v with t = |c_u/c_d| of the 10_H part and theta(t) = sqrt(2 t^2/(1 + t^2)) theta_Re.  With O28 on, the doublet Schur complement M0 - |c|^2 S (O(c^2)) mixes Re H and Im H, so t is computed from its lightest eigenvector (float, maximised over the phase of c), and |c| is restricted to the colour-stable range min(4 pi, rho_O28(r0)).  Mirsky: max_i |sigma_i(A) - sigma_i(B)| <= ||A - B||_2, so ||Y_F|| >= |m_t - t m_b|/(theta(t) v) at M_I (v = 174.1 GeV; running masses from section E).

q0 stays stationary with V_c(q0) = V0 (O28 vanishes at H = 0, its gradient is zero), but for every c != 0 the doublet Schur complement of the positive-definite heavy block is O(c^2), exactly -c^2 r0^4 663552 (13 r0^2 + 6)/(13 r0^4 + 12 r0^2 + 36) < 0 on the light doublet: q0 is a saddle and V + c O28 < V0 nearby, so the SOS27 lower bound V >= V0 fails at the certified member.  Raising O06 by that shift restores the doublet sector, but for |c| > rho_O28(r0) O28 also drives the (3,1)_|Y|=1/3 sector tachyonic, which O06 cannot cure (it lifts the H triplets and doublets together and the doublet must stay light); and the certified SOS27 identity does not contain the H-odd O28 term, so a light doublet with the O28 portal on needs a new G3 certificate (Route A).  Portal = 0 is load-bearing.

## (3b) All five H-linear portals at q0 on the full H block

- all five H-linear directions at the certified vacuum q0 on the full H block (colour triplets Re/Im H_0..5 and doublets Re/Im H_6..9) and every non-H block they couple to (Phi, Sigma; S and Phi17 are not reached).  The Hessian of V + sum c_k O_k at q0 is exactly [[H_HH, B(c)^T], [B(c), A]] (the portals have only H x non-H blocks there and A does not depend on c), so its Schur complement on the H block, H_HH - sum c_k c_l G[k, l], is O(c^2) (exactly quadratic in c) and decides the second-order stability of q0 by Haynsworth inertia additivity; the light eigenvalues and the heavy admixture agree with it to O(c^2) (first order in c for the admixture).  |c_d| <= 4 pi for the complex coefficient of each direction (|c_d|^2 = c_re^2 + c_im^2); the combined admixture obeys the triangle inequality theta <= sum_d |c_d| theta_d.
- Lattice binding: each H-linear operator is linear in (H, H^dag), so at H = 0 its Hessian has only H x (non-H) blocks (checked: the H x H and non-H x non-H blocks vanish).  Doublet columns: O28 (H^dag Sigma^2 Sigma^dag) to Sigma with <Sigma>^2 ~ r0^2; O15 (Phi H^dag Sigma) and O45_B02 (Phi^2 H^dag Sigma) to Phi with <Sigma> ~ r0 (times <Phi> for O45); O38 (Phi H^dag Sigma^dag S^dag) to Phi with <Sigma^dag><S^dag> ~ r0^2; O45_B01 none (the PS-singlet p cannot connect (1,2,2)_10 to (15,2,2)_126bar).  Colour-triplet columns: O15 to Sigma with <Phi> = p ~ 1 (the 126bar (6,1,1)) and to Phi with ~ r0; O38 to Sigma with <Phi><S^dag> ~ r0 and to Phi with ~ r0^2; O28 to Sigma with ~ r0^2; O45_B01 and O45_B02 to Phi with ~ r0.  O15, O28 and O45_B02 act on the Y = +1/2 ('5') component of the doublets and annihilate the Y = -1/2 ('5bar') one; O38 acts on the Y = -1/2 component only.
- Selection rule: exact at the physical member and at every repository r0: the doublet columns of O15, O28 and O45_B02 annihilate the Y = -1/2 (5bar) component of the 10_H doublets and those of O38 the Y = +1/2 (5) component (integer lattice); the Sigma admixture Gram is 2 theta_Re^2 times the projector onto the coupled component, so theta(tan beta) = sqrt(2 t^2/(1 + t^2)) theta_Re (O15, O28, O45_B02) or sqrt(2/(1 + t^2)) theta_Re (O38) with t = |5|/|5bar| (theta <= sqrt(2) theta_Re for every tan beta); and for every portal parameter and every doublet column the induced 126bar vev couples only the up-type structures Q u^c and L nu^c (entries u u^c, d u^c, nu nu^c, e nu^c; lepton/quark modulus 3), never Q d^c or L e^c (exact Gaussian-rational 16.16 bilinears; the same machinery couples sigma_std only to nu^c nu^c).  So M_d and M_e keep only their 10_H parts, M_e = phase x M_d^T, for every combination of the five portals at any coefficient (first order in v, tree level).
- Colour-stable region, per direction: the colour-triplet Schur block is H_TT - |c_d|^2 G_d (phase independent, exact); q0 has no colour-triplet negative mode iff |c_d| <= rho_d, rho_d = 1/sqrt(lambda_max(H_TT^-1/2 G_d H_TT^-1/2)), bracketed exactly by the inertia of H_TT - t G_d at t = (1 -+ 1e-6) rho_d^2.
- Any combination (sufficient): sum_d |c_d|/rho_d <= 1 implies H_TT - Q_T(c) >= 0 (Minkowski: ||A^-1/2 B_T(c) v|| <= sum_d |c_d| ||A^-1/2 B_T,d v|| <= (sum_d |c_d|/rho_d) sqrt(v^T H_TT v)).
- Any combination (necessary): if H_HH(eps) - Q(c) >= 0 then for every triplet vector v and heavy vector z, (z^T B(c) v)^2 <= (z^T A z)(v^T H_HH v); with z = A^-1 B_d(phi_d) v (the response of direction d at the phase of c_d) this gives |c_d| m <= sqrt(m h) + 4 pi sum_{d' != d} X_d', m = v^T G_d v, X_d' = sqrt(sum_{a, b in re, im} (v^T G[(d, a), (d', b)] v)^2), h = v^T H_HH(eps_max) v, v the top generalised eigenvector of (G_d, H_TT) and eps_max the largest O06 compensation that keeps the doublet light anywhere in the box (Minkowski bound over the directions); valid for any combination with the other directions in the |c| <= 4 pi box.
- Compensation: raising O06 by eps shifts every H level (triplets and doublets) by eps.  eps = the doublet Schur shift (O(c^2 r0^2), at most eps_max_O06_compensation_in_box) restores the doublet sector and keeps the doublet light; it enlarges each colour radius by at most sqrt(1 + eps) (H_TT(eps) <= (1 + eps) H_TT(0)), so O06 cannot remove a colour tachyon: any larger eps makes the doublet GUT-heavy.  Beyond rho_d the H-triplet level (from O46, (3/5) I_1 - I_54, relative to the doublet) or the heavy (3,1)_1/3 levels must be raised by the factor (|c_d|/rho_d)^2, which changes the certified benchmark coefficient map.  Either way (and for every portal c != 0, which makes q0 a saddle of V + c O) the SOS27 identity no longer certifies the vacuum: a new G3 certificate is required (Route A).

| direction | doublet block (r0 power) | triplet blocks (r0 power) | doublet source | theta_(15,2,2)/(c r0^2) (physical r0, tan beta = 1) | shift/(c^2 r0^2) | induced 16.16 pairs | colour radius (physical r0) | saddle for c != 0 |
|---|---|---|---|---|---|---|---|---|
| O15_B01_Phi_Hdag_Sigma | Phi210 (1) | Phi210 (1), Sigma126bar (0) | + | 1.633 | -0.6667 | d-uc, e-nuc, nu-nuc, u-uc | 0.7906 | True |
| O28_B01_unique_Hdag_Sigma2_Sigmadag | Sigma126bar (2) | Sigma126bar (2) | + | 470.3 | -0.0004482 | d-uc, e-nuc, nu-nuc, u-uc | 14.05 | True |
| O38_B01_Phi_Hdag_Sigmadag | Phi210 (2) | Phi210 (2), Sigma126bar (1) | - | 0.000104 | -2.702e-09 | d-uc, e-nuc, nu-nuc, u-uc | 1.242e+04 | True |
| O45_B01_Phi2_Hdag_Sigma_210_1050 | none | Phi210 (1) | none | 0 | 0 | none | 7854 | False |
| O45_B02_Phi2_Hdag_Sigma_210_1050 | Phi210 (1) | Phi210 (1) | + | 3.266 | -2.667 | d-uc, e-nuc, nu-nuc, u-uc | 7854 | True |

| repository scale | r0 | colour radius: O15 / O28 / O38 / O45_B01 / O45_B02 | outer bound O15 / O28 | theta up-type: box / colour-stable | portal-immune pull (raw / theory) | tan beta max colour-stable: O15 / O28 / O38 / O45_B02 | reaches m_t/m_b (box; smallest grid abs c, step 4 pi/48) | reaches m_t/m_b (colour-stable; smallest grid abs c, step 4 pi/48) | fix excluded |
|---|---|---|---|---|---|---|---|---|---|
| anchor_content_local_chain | 6.366e-05 | 0.7906 / 14.05 / 1.242e+04 / 7854 / 7854 | 0.7909 / 14.06 | 3.423e-05 / 3.412e-05 | 34.83 / 10.03 | 2.14 / 1.15 / 1 / 1.68e+03 | O15 (abs c >= 5.24), O45_B02 (abs c >= 2.62) | O45_B02 (abs c >= 2.62) | True |
| candidate_PS_content_with_1HDM_below_M_I | 5.264e-05 | 0.7906 / 17 / 1.502e+04 / 9498 / 9498 | 0.7908 / 17 | 2.341e-05 / 2.333e-05 | 34.84 / 10.04 | 2.14 / 1.1 / 1 / 1.68e+03 | O15 (abs c >= 5.24), O45_B02 (abs c >= 2.62) | O45_B02 (abs c >= 2.62) | True |
| candidate_PS_content_with_2HDM_below_M_I | 1.972e-04 | 0.7906 / 4.537 / 4009 / 2535 / 2535 | 0.7915 / 4.538 | 3.284e-04 / 1.197e-04 | 34.78 / 10.02 | 2.14 / 1.19 / 1 / 1.68e+03 | O15 (abs c >= 5.24), O45_B02 (abs c >= 2.62) | O45_B02 (abs c >= 2.62) | True |
| candidate_content_with_1HDM_and_sub_M_I_remnants | 3.898e-06 | 0.7906 / 229.5 / 2.028e+05 / 1.283e+05 / 1.283e+05 | 0.7906 / 229.5 | 1.283e-07 / 1.279e-07 | 35.02 / 10.09 | 2.14 / 1 / 1 / 1.68e+03 | O15 (abs c >= 5.24), O45_B02 (abs c >= 2.62) | O45_B02 (abs c >= 2.62) | True |

Findings: {"O15_frees_tan_beta_only_beyond_its_colour_radius": true, "colour_radius_below_4pi": {"anchor_content_local_chain": ["O15_B01_Phi_Hdag_Sigma"], "candidate_PS_content_with_1HDM_below_M_I": ["O15_B01_Phi_Hdag_Sigma"], "candidate_PS_content_with_2HDM_below_M_I": ["O15_B01_Phi_Hdag_Sigma", "O28_B01_unique_Hdag_Sigma2_Sigmadag"], "candidate_content_with_1HDM_and_sub_M_I_remnants": ["O15_B01_Phi_Hdag_Sigma"]}, "down_type_and_charged_lepton_masses_untouched_by_every_portal_combination": true, "portal_fix_excluded_at_anchor_chain_r0": true, "portal_fix_excluded_at_every_repository_r0": true, "portal_fix_not_excluded_at": [], "t_b_bound_survives_portal_set_at_every_repository_r0": false, "tan_beta_reaches_m_t_over_m_b_colour_stable_with": {"anchor_content_local_chain": ["O45_B02_Phi2_Hdag_Sigma_210_1050"], "candidate_PS_content_with_1HDM_below_M_I": ["O45_B02_Phi2_Hdag_Sigma_210_1050"], "candidate_PS_content_with_2HDM_below_M_I": ["O45_B02_Phi2_Hdag_Sigma_210_1050"], "candidate_content_with_1HDM_and_sub_M_I_remnants": ["O45_B02_Phi2_Hdag_Sigma_210_1050"]}, "tan_beta_reaches_m_t_over_m_b_in_box_with": {"anchor_content_local_chain": ["O15_B01_Phi_Hdag_Sigma", "O45_B02_Phi2_Hdag_Sigma_210_1050"], "candidate_PS_content_with_1HDM_below_M_I": ["O15_B01_Phi_Hdag_Sigma", "O45_B02_Phi2_Hdag_Sigma_210_1050"], "candidate_PS_content_with_2HDM_below_M_I": ["O15_B01_Phi_Hdag_Sigma", "O45_B02_Phi2_Hdag_Sigma_210_1050"], "candidate_content_with_1HDM_and_sub_M_I_remnants": ["O15_B01_Phi_Hdag_Sigma", "O45_B02_Phi2_Hdag_Sigma_210_1050"]}}

The full H block changes the picture of the doublet-only analysis in two ways.  (i) Colour: O15 couples the H triplets to the 126bar (6,1,1) through <Phi> = p at O(1), so q0 acquires GUT-scale (3,1)_|Y|=1/3 tachyons for |c_O15| > rho_O15 ~ 0.79 (r0-independent), well before O15 can move tan beta to m_t/m_b; O28 is colour-limited to |c| <= rho_O28 ~ 1/r0 (below 4 pi at the 2HDM-content r0); O38 and O45 are colour-stable in the box.  O45_B02 still moves tan beta past m_t/m_b inside the colour-stable region (the doublet saddle it creates is cured by O06), so the O28-alone t-b bound does not survive the portal set.  (ii) Flavour: every portal-induced 126bar (15,2,2) vev is purely up-type (exact selection rule), so M_e = phase x M_d^T survives every portal combination and the tan-beta-independent (m_s/m_d)/(m_mu/m_e) and (m_b/m_s)/(m_tau/m_mu) exclusions stand: no in-contract H-linear portal repair survives at any repository r0 at q0.  Any doublet-coupled portal makes q0 a saddle, so a flavour-repairing branch would need a new G3 certificate in any case (Route A).

## (4) Seesaw (float, not load-bearing)

type-I only (the type-II-capable H-Sigma quartics O35 and the 5/5bar-splitting O31 vanish in the benchmark); v_R = M_I; M_D = M_u = diag(m_u, m_c, m_t)(v_R) in the common flavour basis (M_e, M_d, M_u, M_D aligned on the witness); only the nu^c of the three light families (nu^c-vectorlike mixing through the S and Phi17 vevs is neglected); m_nu = -M_D^T M_R^-1 M_D, so M_R = -M_D m_nu^-1 M_D^T; oscillation data NuFIT 5.2, sum m_nu < 0.12 eV; the RG running of m_nu below v_R (a factor ~1.2-1.4) is ignored; Y_R = sigma_max(M_R)/v_R.  M_D = M_u(data) is the generic SO(10) premise, not a prediction of the witness: on the witness M_D = phase M_u^T and M_u has the singular values of M_e = M_d (tan beta = 1), for which the generic Y_R ~ m_tau^2/(sqrt(dm31^2) v_R) ~ 0.06 at 1e12 GeV (column generic_Y_R_if_MD_has_charged_lepton_singular_values)

| v_R | generic Y_R (M_D = M_u data) | generic Y_R (M_D with charged-lepton values) | median Y_R (NO) | min Y_R found (NO) | min Y_R found (IO) |
|---|---|---|---|---|---|
| 1e+10 GeV | 1.99e+04 | 6.46 | 1.08e+05 | 49.3 | 1.47e+04 |
| 1e+11 GeV | 1.83e+03 | 0.638 | 9.9e+03 | 4.87 | 1.36e+03 |
| 1e+12 GeV | 170 | 0.063 | 930 | 0.379 | 126 |
| M_I[anchor_content_local_chain] | 273 | 0.1 | 1.44e+03 | 0.608 | 202 |
| M_I[candidate_PS_content_with_1HDM_below_M_I] | 298 | 0.109 | 1.69e+03 | 0.796 | 221 |
| M_I[candidate_PS_content_with_2HDM_below_M_I] | 160 | 0.0597 | 857 | 0.382 | 119 |
| M_I[candidate_content_with_1HDM_and_sub_M_I_remnants] | 2.38e+03 | 0.822 | 1.27e+04 | 3.07 | 1.76e+03 |

If M_D = M_u(data), a generic Y_126 needs Y_R = O(10^2 - 10^4) (non-perturbative) across the band; a textured Y_126 with (m_nu^-1)_tautau ~ 0 lowers the requirement, and where the scan finds perturbative minima the seesaw alone is not a no-go.  With the witness's own M_D (charged-lepton singular values) the generic Y_R is perturbative.  So 'the seesaw needs Y_126 ~ 10^2-10^3' is a statement about the M_D = M_u premise, not about the witness.  The no-go of this certificate rests on the charged sector (sections B-E), not on the seesaw.

## (5) Scope and routes

**cited_or_hand_argued**
- electroweak breaking proceeds along the light doublet Re H_6..9 (the only light scalar with doublet quantum numbers; the certified eps >= 0 family itself leaves SU(2)_L x U(1)_Y unbroken)
- the light-state lemma: 16bar components are heavy (generic rank 8 certified; rank 8 at the physical couplings assumed: exactly three light families), heavy-light corrections O(v^2/M_V^2) are dimension >= 6
- no induced (10,3,1) (Delta_L) vev from EW breaking at tree level: the heavy-doublet part is proved (V even in H), the integer-isospin (10,3,1) part rests on the vanishing H-Sigma quartics O31/O35 (checked)
- SM running preserves Yukawa alignment (one-loop form Y g(Y^dag Y); U(1)^3 family symmetry to all orders)
- Mirsky's singular-value inequality; Haynsworth inertia additivity (the Schur complement on the H block decides the second-order stability of q0); the Minkowski and Cauchy-Schwarz inequalities of the combination certificates
- with portals on, the induced heavy vevs are the first-order (in v) response -A^-1 B(c) h v of the light doublet h; O(v^3/M^2) corrections are dimension >= 6
- Y_F (the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2)), the contract's declared Y126 and the seesaw Y_R differ by unfixed Clebsch normalisations; the O28-alone t-b bound is far above 4 pi, so this O(1) ambiguity does not matter

**float_diagnostics**
- data comparison: PDG/FLAG/XZZ inputs, one-loop SM running, pulls (raw and with a 10% theory term)
- O28 bounds at the repository r0 values: theta at |c| = 4 pi and in the colour-stable range, tan beta of the lightest eigenvector of the O(c^2) doublet Schur complement (eigh, phase scan), and the Mirsky t-b requirement
- colour radii rho_d (eigvalsh of the exact triplet Grams; bracketed exactly), the O06-compensated upper radius, and the outer bound on each |c_d| for any combination (Cauchy-Schwarz with the others in the box)
- portal-set bounds: up-type theta_(15,2,2) <= sum_d |c_d| sqrt(2) theta_d (box and colour-stable), the portal-immune data pulls, and tan beta scans per direction over |c| in (0, 4 pi] and over the colour-stable range, and the phase of c
- seesaw: generic Y_R and a scan (random + Nelder-Mead) of textured Y_126
- the O28 and portal lattice bindings compare the compiler's float64 Hessian with the (1/6)-integer patterns

**not_claimed**
- no statement about the G3-G5 scalar-vacuum certificates or the SO(10) contract: they stand
- no loop-level flavour analysis (threshold corrections from 126bar remnants below M_I are O(Y_126^2/16 pi^2))
- the seesaw section is not a no-go (textured Y_126 can lower the requirement), and its non-perturbative generic Y_R assumes M_D = M_u(data), not the witness's own M_D
- the colour-stable region is the second-order (Hessian) region at q0 with the certified couplings; global minimality with any portal on is not certified (a new G3 certificate would be needed); tan beta is freed inside it by O45_B02, so the O28-alone t-b bound is not a statement about the portal set
- no analysis away from q0 (a vacuum with a light or down-type-mixing (15,2,2) is Route A)
- G8 is not closed; Route A or B is required to reach it

**proved_exactly**
- the H-linear directions of the 44-direction contract are exactly O15, O28, O38, O45_B01, O45_B02 (census orbit keys) and all ten re/im parameters vanish in the benchmark map for every r0, x0 (sympy)
- exact Hessian (Fraction binding units) at r0 = 1/5, 1/20, 1/100 and the anchor r0: zero gradient, H block decoupled and equal to diag(2, 2 + 2 r0^2 | 0, 2 r0^2) (u coords), Re H_6..9 exact null vectors: the light doublet is pure 10_H with zero 126bar (15,2,2) and zero 210 admixture
- V is even in H on the witness (live H-degrees {0, 1, 2, 4}, H-linear parameters zero), so no heavy doublet (126bar (15,2,2), 210 doublets) gets an induced vev at any order in v at tree level (the SU(2)_L centre -1 composed with H -> -H fixes q0 + h and acts as -1 on every heavy doublet)
- the allowed 16bar x 16 coupling pattern has generic rank 8 (exact rank at deterministic integer couplings; kernel of dimension 3 in span{F, P, Q, R}): exactly three light families for generic couplings
- Gaussian-integer Clifford algebra: 16x16 = 10 + 120 + 126, 16x16bar = 1 + 45 + 210; the 16.16.10 Clebsches at the real neutral vev a e8 + b e9 have |c_f|^2 = a^2 + b^2 for u, d, e, nu (tan beta = 1), constant phases nu/u and e/d; sigma_std couples only nu^c nu^c; the (15,2,2) lepton/quark Clebsch is -3
- contract enumeration from the SARAH model file: no 16.16.10_H^* coupling, H10/126bar Yukawas only on the X = 1 sixteens, 16.16bar masses only from SO(10) singlets, no 120_H
- flavour structure (sympy): M_u M_u^dag = M_d M_d^dag, M_e = phase M_d^T, M_D = phase M_u^T
- O28 alone: lattice-bound H-Sigma block (+-192 r0^2), exact first-order admixture theta^2 = c^2 r0^4 R(r0) with R = 7962624 (13 r^2+6)^2/(13 r^4+12 r^2+36)^2 (derived from 3 exact points, re-checked at 2, and matched exactly by the first-order solve at 8 r0 values including the anchor and the 4 repository r0), O(c^2) (exactly quadratic) negative doublet Schur complement (saddle) for every c != 0
- all five H-linear portals on the full H block (colour triplets and doublets): all twenty H columns bound to the (1/6) Z lattice with pinned blocks and r0 powers, exact heavy responses, exact Schur Grams (the triplet and doublet blocks decouple, both are phase independent) at the physical member and the 4 repository r0; every doublet-coupled portal makes q0 a saddle for c != 0; O45_B01 has no doublet coupling but, like every portal, couples the colour triplets
- colour-stable radii: H_TT - t G_d has no negative eigenvalue at t = (1 - 1e-6) rho_d^2 and one at (1 + 1e-6) rho_d^2 (exact inertia, per direction and r0)
- selection rule: O15, O28, O45_B02 act only on the Y = +1/2 doublet component, O38 only on Y = -1/2 (integer lattice); the Sigma admixture Gram is 2 theta_Re^2 times the coupled-component projector (theta(tan beta) exact up to the float t); and every portal-induced 126bar vev couples only Q u^c and L nu^c (exact 16.16 bilinears), so M_e = phase x M_d^T for every portal combination at any coefficient

- Route A: New in-contract G3 branch: a vacuum in which a DOWN-type doublet from the 126bar (15,2,2) has a nonzero admixture theta_d in the light doublet, large enough that theta_d ||Y_F|| v reaches the required d-e / s-mu / b-tau splittings (theta_d ||Y_F|| ~ 1e-4 at M_I for s-mu; far below O(1) for perturbative Y_F).  At the certified q0 this is impossible at every repository r0 (sections F and F'): theta_d = 0 exactly, because every H-linear portal (O15, O28, O38, O45) feeds only the up-type (15,2,2) (exact Yukawa selection rule), so M_e = phase x M_d^T survives any portal combination; the portals are also colour-limited (|c_O15| <= ~0.79 at every r0, |c_O28| <= rho_O28(r0) ~ 1/r0, 4.5 at the 2HDM-content r0) and every doublet-coupled portal makes q0 a saddle (SOS27 needs portal = 0; O06 cures only the doublet saddle).  A Route A branch must therefore leave q0 (other vevs, or a (15,2,2) near M_I with a down-type mixing channel), keep the colour triplets non-tachyonic, and needs new exact G3/G4/G5 certificates; it may not exist and reopens the 2HDM proton-decay and high-v_R Higgs-matching risks.
- Route B: Extension beyond the declared contract: a 120_H, a second 10_H, or a UV completion that generates F.F.H10^*.S^* (U(1)_X allows it at dimension five).  Changes models/SO10Z17AxionV20.m; G1-G5 restart.
- Route C: Record this no-go (this artifact) and leave G8 OPEN on the current witness branch.

## Checks

- PASS `H_linear_portals.admixture_uniform_over_doublet_and_re_im_every_direction`
- PASS `H_linear_portals.colour_radii_exactly_bracketed`
- PASS `H_linear_portals.every_H_linear_portal_theta_below_1e-3_at_every_repository_r0`
- PASS `H_linear_portals.every_direction_couples_the_colour_triplets`
- PASS `H_linear_portals.every_direction_lattice_bound_with_pinned_blocks_powers_and_hypercharge_source`
- PASS `H_linear_portals.general_solver_reproduces_O28_alone_exactly`
- PASS `H_linear_portals.gram_symmetric_every_direction`
- PASS `H_linear_portals.heavy_blocks_positive_definite_every_direction`
- PASS `H_linear_portals.heavy_components_avoid_the_H_block`
- PASS `H_linear_portals.heavy_systems_nonsingular_every_direction`
- PASS `H_linear_portals.induced_126bar_vev_up_type_only_every_direction_every_r0`
- PASS `H_linear_portals.only_O45_B01_lacks_a_doublet_coupling`
- PASS `H_linear_portals.portal_immune_tests_excluded_at_every_repository_r0`
- PASS `H_linear_portals.re_im_admixtures_orthogonal_every_direction`
- PASS `H_linear_portals.repository_scales_present`
- PASS `H_linear_portals.saddle_for_every_nonzero_c_every_doublet_coupled_direction`
- PASS `H_linear_portals.schur_complements_phase_independent_exactly`
- PASS `H_linear_portals.sigma_admixture_gram_is_2_theta2_times_source_projector`
- PASS `H_linear_portals.triplet_and_doublet_schur_blocks_decouple_exactly`
- PASS `H_linear_portals.yukawa_machinery_reproduces_sigma_std_nuc_nuc`
- PASS `O28_fix.O28_lattice_bound_to_plus_minus_192`
- PASS `O28_fix.R_at_zero_is_221184`
- PASS `O28_fix.admixture_uniform_over_doublet_and_re_im`
- PASS `O28_fix.admixture_up_type_only_at_every_repository_r0`
- PASS `O28_fix.closed_form_derived_and_matches_pinned`
- PASS `O28_fix.exact_rows_match_closed_form`
- PASS `O28_fix.heavy_blocks_positive_definite`
- PASS `O28_fix.re_im_admixtures_orthogonal`
- PASS `O28_fix.repository_scales_present`
- PASS `O28_fix.saddle_for_every_nonzero_c_at_every_r0`
- PASS `O28_fix.second_order_gram_symmetric`
- PASS `O28_fix.t_b_repair_nonperturbative_at_every_repository_r0`
- PASS `O28_fix.theta_max_small_at_every_repository_r0`
- PASS `contract.Delta126bar_yukawas_only_on_X1_sixteens`
- PASS `contract.H10_yukawas_only_on_X1_sixteens`
- PASS `contract.Q_and_spectators_have_no_16_16_scalar_coupling`
- PASS `contract.allowed_set_Z17_consistent`
- PASS `contract.declared_terms_U1X_neutral`
- PASS `contract.declared_terms_Z17_neutral`
- PASS `contract.declared_terms_parsed`
- PASS `contract.declared_yukawas_SO10_singlets`
- PASS `contract.declared_yukawas_subset_of_allowed`
- PASS `contract.every_16bar_has_a_singlet_mass_partner`
- PASS `contract.model_fields_parsed`
- PASS `contract.net_chirality_three_families`
- PASS `contract.no_120_scalar_in_contract`
- PASS `contract.no_16_16_10H_conjugate_coupling`
- PASS `contract.no_16_16bar_210_coupling`
- PASS `contract.no_bare_vectorlike_mass`
- PASS `contract.sixteen_sixteen_scalars_only_H10_and_Delta126bar`
- PASS `contract.sixteenbar_pair_couplings_involve_only_16bars`
- PASS `contract.vectorlike_masses_only_SO10_singlet_vevs`
- PASS `contract.vectorlike_pattern_generic_rank_8`
- PASS `data.every_load_bearing_test_excluded_conservative_at_threshold`
- PASS `data.every_load_bearing_test_excluded_raw_at_threshold`
- PASS `data.m_t_over_m_b_far_from_one_across_band`
- PASS `data.repository_M_I_rows_present`
- PASS `data.running_reproduces_published_high_scale_top_mass_roughly`
- PASS `flavour_structure.MD_equals_constant_phase_times_Mu_transpose`
- PASS `flavour_structure.Me_equals_constant_phase_times_Md_transpose`
- PASS `flavour_structure.MuMu_dagger_commutes_with_MdMd_dagger`
- PASS `flavour_structure.MuMu_dagger_equals_MdMd_dagger`
- PASS `flavour_structure.clebsch_available`
- PASS `light_doublet.H_Sigma_quadratic_O31_O35_zero_in_benchmark`
- PASS `light_doublet.H_block_decoupled_at_every_r0`
- PASS `light_doublet.H_block_equals_exact_formula_at_every_r0`
- PASS `light_doublet.H_linear_directions_are_exactly_O15_O28_O38_O45`
- PASS `light_doublet.H_linear_parameters_are_the_candidate_portal_list_plus_im`
- PASS `light_doublet.H_linear_parameters_zero_for_all_r0_x0_symbolic`
- PASS `light_doublet.H_linear_parameters_zero_in_benchmark`
- PASS `light_doublet.Re_H_6_9_exact_null_vectors_at_every_r0`
- PASS `light_doublet.binding_unit_coverage_complete_at_every_r0`
- PASS `light_doublet.census_has_44_live_directions`
- PASS `light_doublet.exact_gradient_zero_at_every_r0`
- PASS `light_doublet.my_exact_hessian_reproduces_certified_benchmark_hessian`
- PASS `light_doublet.no_H_degree_3_live_direction`
- PASS `light_doublet.nonzero_H_quadratic_parameters_are_O06_O12_O46`
- PASS `light_doublet.potential_even_in_H_on_the_witness`
- PASS `spinor.Q_em_equals_T3L_plus_Y_on_spinor`
- PASS `spinor.all_charged_and_dirac_clebsch_moduli_equal`
- PASS `spinor.cartan_generators_diagonal_with_spinor_weights`
- PASS `spinor.charge_conjugation_intertwines_so10`
- PASS `spinor.clebsch_moduli_equal_a2_plus_b2`
- PASS `spinor.clifford_relations_exact`
- PASS `spinor.conjugate_sigma_std_decouples_from_16x16`
- PASS `spinor.equal_5_5bar_components_tan_beta_one`
- PASS `spinor.fifteen_two_two_relative_lepton_clebsch_minus_3`
- PASS `spinor.neutral_vev_plane_is_e8_e9`
- PASS `spinor.nu_over_u_and_e_over_d_constant_unimodular`
- PASS `spinor.sigma_std_couples_only_nuc_nuc`
- PASS `spinor.sixteen_bar_has_conjugate_spectrum`
- PASS `spinor.sixteen_has_one_family_hypercharge_spectrum`
- PASS `spinor.ten_bilinear_at_e8_e9_only_dirac_pairs`
- PASS `spinor.ten_bilinear_symmetric_on_16`
- PASS `spinor.tensor_products_16x16_and_16x16bar_proved`
- PASS `spinor.z5_has_hypercharge_plus_half`
- PASS `upstream.candidate_H_linear_portals_are_zero`
- PASS `upstream.candidate_kernel_symmetry_plus_light_doublet_float`
- PASS `upstream.candidate_light_doublet_equal_5_5bar`
- PASS `upstream.candidate_r0_physical_matches`
- PASS `upstream.candidate_status_and_zero_failures`
- PASS `upstream.exact_hessian_certified`
- PASS `upstream.exact_hessian_kernel_orbit_plus_doublet`
