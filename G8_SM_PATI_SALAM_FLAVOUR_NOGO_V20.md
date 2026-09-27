# G8 flavour no-go on the SM Pati-Salam G3 witness branch (Route C, v20)

- Status: `G8_SM_PATI_SALAM_WITNESS_FLAVOUR_NOGO__ROUTE_C_RECORDED__G8_OPEN`
- Overall state: `WITNESS_BRANCH_FLAVOUR_EXCLUDED_AT_RENORMALIZABLE_TREE_LEVEL`; G8: **OPEN**
- Checks: 157/157 pass

## Verdict

On the SM Pati-Salam G3 witness branch (renormalizable 27-parameter benchmark family, H-linear portals zero) the light Higgs doublet is exactly the 10_H direction Re H_6..9 and, with the contract's renormalizable Yukawas, M_u = c_u Y, M_d = c_d Y, M_e = c_e Y^T, M_D = c_nu Y^T with |c_u| = |c_d|: CKM = 1, m_t = m_b, m_d = m_e, m_s = m_mu, M_D = M_u, and the 126bar enters only M_R.  The tan-beta-independent tests are excluded by at least 13.2 sigma (experimental errors) and 8.9 sigma (with a 10% theory term) across 1e9-2e16 GeV.  The O28 portal alone (the largest direct 10_H-(15,2,2) portal, other portals zero) gives theta = |c| r0^2 sqrt(R(r0)) <= 2.40e-05 at the anchor r0 with |c| <= 4 pi for the witness doublet (<= 3.39e-05 for any tan beta); its admixture is purely up-type, so it cannot split b from tau at all, and repairing the t-b split needs ||Y_F|| >= 5786 at every repository r0 inside the colour-stable range (Mirsky; Y_F the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2)).  With all five H-linear portals on at q0, the full H block (colour triplets included) gives the second-order colour-stable region: |c_O15| <= 0.791 at every repository r0 (the H triplets couple to the 126bar (6,1,1) through <Phi> at O(1); beyond it q0 has GUT-scale (3,1)_|Y|=1/3 tachyons), |c_O28| <= rho_O28(r0) ~ 1/r0 (4.54 at candidate_PS_content_with_2HDM_below_M_I, 14.1 at anchor_content_local_chain, 17 at candidate_PS_content_with_1HDM_below_M_I, 230 at candidate_content_with_1HDM_and_sub_M_I_remnants; below 4 pi at candidate_PS_content_with_2HDM_below_M_I), O38 and O45 colour-stable in the box; raising O06 cures only the doublet saddle (it lifts triplets and doublets alike and the doublet must stay light); inside it O45_B02_Phi2_Hdag_Sigma_210_1050 still moves tan beta past m_t/m_b (O15 only beyond its colour radius), so the O28-alone t-b bound does not survive the portal set.  But every portal-induced 126bar (15,2,2) vev is purely up-type (exact: the induced 16.16 couplings are only Q u^c and L nu^c at every repository r0), so M_e = phase x M_d^T survives every portal combination at any coefficient and the portal-immune tests (m_s/m_d)/(m_mu/m_e) and (m_b/m_s)/(m_tau/m_mu) stay excluded by >= 34.8 sigma (10.0 sigma with the theory term): no in-contract H-linear portal repair of the flavour sector survives at any repository r0.  Every doublet-coupled portal c != 0 turns the certified witness into a saddle (SOS27 needs portal = 0), so any repair needs a new G3 certificate (Route A).  If M_D = M_u(data) (the generic SO(10) premise, not the witness's own M_D), the seesaw needs a non-perturbative Y_126 for generic textures (a tuned texture can evade this, so it is not load-bearing).  Route C is recorded; G8 stays OPEN; the G3-G5 certificates and the SO(10) contract are not falsified.  Status-neutral v2 lemmas (exact): every (1,2,2) Yukawa source has lepton/quark Clebsch +1 (T15-free), so a second 10_H or F.F.H10^*.S^* cannot split d from e: among the analysed candidate extensions only a 120_H can (a second 126bar_H, a new B-L-breaking scalar vev and vectorlike matter were not analysed); for SU(5)-equivariant mixing the up-type-only rule follows from the SU(5) Casimir (10_H doublets 12/5, the 126bar down-type doublet 32/5); the light doublet stays pure 10_H with tan beta = 1 for every |S|; Dirac Yukawas are Sigma-balanced at every dimension (the census of single-Higgs light-16 monomials is exhaustive to dimension 12), so the PS-invariant part of the operators linear in H10 or H10^* keeps M_e = phase x M_d and, at tan beta = 1, M_d = phase x M_u; one light G3221 bidoublet forces s = 1 (CKM = 1; dimension four, G3221-equivariant composition, <Sigma>-mediated SU(2)_R breaking not analysed, no G3221 vacuum claimed); the pure 10 + 120 inequality B1a is proved.  G8 stays OPEN and the contract is not falsified.

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

## (5) Status-neutral v2 lemmas (exact)

No lemma changes a status: G8 stays OPEN.  They are no-go statements about this witness branch and the declared contract; a 120_H extension, a Route A branch and the extensions not analysed here (a second 126bar_H, a new B-L-breaking scalar vev, vectorlike matter) remain logically open.

### L1. The (1,2,2) Clebsch is +1 via T15 (`lemma_122_clebsch`, 7/7 checks pass)

- Statement: On the 16, T15 = 3(B-L) (the repository Cartan B-L generator) is 1 on the quarks and -3 on the leptons of (4,2,1) (-1, +3 on (4bar,1,2)) and traceless on every SU(4) multiplet.  For every component e_a (a = 6..9) of the (1,2,2) of the 10: the 10 channel C Gamma_a is symmetric and the 120-like (1,2,2) channel C Gamma_{iota_{e_a} p} (the dimension-five F.F.H.Phi210 at <Phi210> = p) antisymmetric, their ratio on every oriented (particle-row) entry is one constant for all a, so every (1,2,2) Yukawa source has the lepton/quark Clebsch of the 10 (+1); the 126bar (15,2,2) image omega6 ^ iota_{e_a} p equals K T15 times the 10 on oriented entries with one K for all a (lepton/quark -3 on the up- and the down-type doublet alike), and so does the (15,2,2) component omega6 ^ e_a of a hypothetical 120_H (with K').
- T15 on the 16: d = 1, dc = -1, e = -3, ec = 3, nu = -3, nuc = 3, u = 1, uc = -1.
- Oriented ratios: (1,2,2)_120-like / 10 = -1; 126bar (15,2,2) / (T15 x 10) = -I; hypothetical 120_H (15,2,2) / (T15 x 10) = I.
- Scope: group theory of (1,2,2) Yukawa sources of any dimension (the Yukawa couplings of the 10_H, of a second 10_H of any X charge, a 10_H^* Yukawa, F.F.H10^*.S^* and every Pati-Salam-singlet dressing such as F.F.H10.Phi210 at <Phi210> = p); it covers the Yukawa sources only (not the scalar portals of a second 10_H), says nothing about vevs, and does not exclude a 120_H (whose (15,2,2) component is T15-type).

### L2. The SU(5)-Casimir selection rule (12/5 against 32/5) (`lemma_su5_casimir`, 7/7 checks pass)

- Statement: With the SU(5) of the repository complex structure (z_k = e_{2k-2} + i e_{2k-1}) and C normalised to 12/5 on the 5: C = 12/5 on every z_k and zbar_k, in particular on both 10_H neutral doublet components z5 (Y = +1/2) and zbar5 (Y = -1/2); C(sigma_std) = 0 (SU(5) singlet); in the 126bar the Q = 0 colour-singlet doublet space with Y = +1/2 and the one with Y = -1/2 are each one-dimensional (the 2 P_{-i} span of the six zero-colour-weight monomials has rank 3); the Y = +1/2 one, w_u = 2 P_{-i}(z5 ^ J ^ J), has C = 12/5 and only up-type 16.16 pairs (u u^c, nu nu^c); the Y = -1/2 one, w_d = 2 P_{-i}(omega6 ^ iota_{zbar5} p), has C = 32/5 and only down-type pairs (d d^c, e e^c); and 2 P_{-i}(zbar5 ^ J ^ J) = 0 (the 5bar has no image in the 126bar).  Corollary (Schur, cited): an SU(5)-equivariant (linear or antilinear) mixing of the 10_H doublets into Sigma can only produce the Casimir-12/5 Sigma doublet, hence only up-type (Q u^c, L nu^c) Sigma Yukawas; the down-type Sigma doublet (Casimir 32/5) is unreachable.
- Casimir: 126_part_of_omega6_iota_zbar5_p = 12/5, 126_part_of_zbar5_J_J = 12/5, sigma_std = 0, w_d = 32/5, w_u = 12/5, z_k = 12/5, zbar_k = 12/5.
- 126bar neutral doublet spaces (2 P_{-i} span rank, colour-singlet dimension): Y=+1/2: [3, 1], Y=-1/2: [3, 1]; 16.16 pairs: w_u nu-nuc, u-uc; w_d d-dc, e-ec; p is an SU(5) singlet: False.
- Scope: representation theory of SU(5)-equivariant maps: it explains the up-type-only rule for mixings built from the SU(5)-singlet vevs sigma_std, S and Phi17 (e.g. O28 = H^dag Sigma^2 Sigma^dag).  The witness 210 vev p is NOT an SU(5) singlet (p_is_su5_singlet = False), so the p-mediated portal paths (O15, O38, O45 through <Phi210> = p and the p-dependent heavy Hessian) rest on the exact per-r0 Schur computation (H_linear_portals.induced_126bar_vev_up_type_only_every_direction_every_r0), not on this lemma.

### L3. tan beta = 1 and the pure-10_H doublet for every |S| = r_S (`lemma_S_independence`, 8/8 checks pass)

- Statement: On the witness family q(s) = (p, 0, r0 sigma_std, S = s, x0), s any complex number (the D-A decoupling changes only the S sector O04, O23 and the O06 retune), with the benchmark operator set (H-linear parameters zero, O31 = O35 = 0): no binding unit couples S to another block and only O04, O23 carry S-S entries (the O12 unit is H-H only), and the only nonzero S-dependent directions are O04, O23 and O12, so the heavy Phi/Sigma/Phi17 Hessian does not depend on s; among the H-linear directions only O38 contains S (S-degree 1); the O06 + O12 block of one complex H component is Matrix([[2 c06 + 4 c12 s_r, -4 c12 s_i], [-4 c12 s_i, 2 c06 - 4 c12 s_r]]) (equal to the binding units at s = r0), with eigenvectors (cos theta/2, -sin theta/2) and (sin theta/2, cos theta/2) for s = r e^{i theta} and every r, i.e. exactly Re H_6..9 and Im H_6..9 for real s; with O06 retuned to 2|kappa| r_S the exact H block at q(r_S) is diag(2, 2 + 2 r0 r_S | 0, 2 r0 r_S); every phase-rotated real doublet has |v_up| = |v_down| (tan beta = 1); and O38 (the 10 x 210 -> 126 contraction <conj(H) ^ Phi, conj(Sigma)> times conj(S)) has no H x S block at q0 (exact forms: e_a ^ p pairs to zero with sigma_std, its conjugate and its Hodge dual for every H direction e_a, a = 0..9) and its doublet columns reach only Phi (e_a ^ p = 0 for a = 6..9), so its columns at q(s) are conj(s)/r0 times those at q0 and the up-type-only portal selection rule and O38's Y = -1/2 source do not depend on |S|.
- S-S binding units: O04 |S|^2, O23 |S|^4; units coupling S to other blocks: none; S-dependent nonzero directions: O04_B01_singlet_polynomial, O12_B01_Hdag_Hdag_pair, O23_B01_singlet_polynomial; S-dependent H-linear directions: O38_B01_Phi_Hdag_Sigmadag.
- O06 + O12 block per complex H component: Matrix([[2*c06 + 4*c12*s_r, -4*c12*s_i], [-4*c12*s_i, 2*c06 - 4*c12*s_r]]); retuned H block diag(2, 2 + 2 r0 r_S | 0, 2 r0 r_S) at r0 = 1/5, 1/20, 1/100, 51544138/809635808795 and r_S/r0 = 1, 10, 1000.
- O38 blocks at q0 (exact forms): H_by_S_block_zero_for_every_H_direction True, doublet_H_by_Sigma_block_zero_e_a_wedge_p_vanishes True, doublet_columns_reach_Phi True, triplet_H_by_Sigma_block_nonzero True; the compiler's lattice-bound O38 pattern agrees (corroboration, not a check): True.
- Scope: tree level, the portal-free witness family (plus the |S| scaling of O38's columns, which follows from its S-degree 1).  Check (vii) models O38 by the unique 10 x 210 -> 126 contraction (cited: 10 x 210 = 120 + 126 + 126bar + 1728 contains the 126 once, the 5-form v ^ Phi) and is exact on forms; the compiler's lattice-bound O38 pattern (float64 bound to (1/6) Z, H_linear_portals) is recorded as a corroboration only.  Not claimed: that q(r_S) with r_S != r0 is a global minimum (G3 at r_S != r0 is not certified), anything about D-A unification, or O31/O35 (Sigma-dependent, |S|-independent, zero in the benchmark).  The 'no induced heavy-doublet vev' lemma (V even in H) holds for every s unchanged.

### L4. (B-L, T3R) Sigma balance, the census to dimension 12 and the PS-invariant remainder (`lemma_eft_census`, 19/19 checks pass)

- Statement: (a) Charges are derived, not typed: <Sigma> = sigma_std has (B-L, T3R) = (-2, +1) (Cartan derivations; minus the charge of nu^c nu^c, the only pair it couples); p, S and Phi17 are neutral; the 10_H doublet components are (0, +1/2) (z5) and (0, -1/2) (zbar5); every Dirac pair (f, f^c) has B-L = 0 and T3R = -1/2 (u, nu) or +1/2 (d, e).  (b) All-orders grading: a Dirac entry needs spurion charge in {(0, -1), (0, 0), (0, +1)} and the spurion B-L is -2 (n_Sigma - n_Sigmabar), so n_Sigma = n_Sigmabar and T3R = 0: every Dirac Yukawa monomial is Sigma-balanced at every dimension (with extra H10/H10^* insertions, all B-L-neutral, n_Sigma = n_Sigmabar still follows from B-L alone), and (with the witness spurions p, S, Phi17, Sigma) every Pati-Salam-breaking Dirac entry carries at least one Sigma Sigma^dag pair, i.e. is O(|<Sigma>|^2/Lambda^2) relative to the PS-invariant part for any operator scale Lambda.  (c) The explicit census of necessary conditions (U(1)_X, Z17, (B-L, T3R)) over the single-Higgs (or Higgs-free) monomials psi_1 psi_2 h s_1 ... s_n of two light 16s (F, P, Q, R), at most one h in {H10, H10^*} and witness spurions s_i in {p, S, S^*, Phi17, Phi17^*, Sigma, Sigma^*} (with multiplicity) is exhaustive to mass dimension 12 for that class.  (d) For generic PS-invariant Yukawas of the operators linear in H10 or H10^* (symmetric 10-type and antisymmetric 120-like channels, on v and on conj(v), any number of PS-singlet spurions) and any v = alpha z5 + beta zbar5: M_e = kappa M_d and M_D = kappa' M_u (kappa = +-1 per colour, no transpose); at |alpha| = |beta| (tan beta = 1, the witness for every |S| by lemma_S_independence) M_d = phase x M_u identically, so CKM = 1 and m_t = m_b; for |alpha| != |beta| the H-tilde terms make the ratio Yukawa-dependent.
- Spurion (B-L, T3R): Phi (0, 0), Phi17 (0, 0), Phi17* (0, 0), S (0, 0), S* (0, 0), Sigma (-2, 1), Sigma* (2, -1); Dirac targets (0, -1), (0, 0), (0, 1); Majorana target (-2, 1).
- Census to dimension 12: 4657 X-neutral monomials, 1460 Dirac-admissible, 800 Majorana-admissible; Dirac dimension histogram {4: 6, 5: 15, 6: 36, 7: 64, 8: 110, 9: 167, 10: 248, 11: 344, 12: 470}; minimal PS-breaking Dirac dimension 6, minimal H-tilde Dirac dimension 5; net Phi17 numbers of Dirac monomials -2, -1, 0: recorded as data only: no PQ-neutrality claim (Dirac monomials with net Phi17 number -1, -2 exist).
- PS-invariant remainder: kappa(e/d) = d[+--]: -1, d[-+-]: 1, d[--+]: -1; kappa(nu/u) = u[+--]: -1, u[-+-]: 1, u[--+]: -1; at tan beta = 1: d[+--]/u[+--] = exp(I*(-theta1 + theta2)), d[-+-]/u[-+-] = exp(I*(-theta1 + theta2)), d[--+]/u[--+] = exp(I*(-theta1 + theta2)).
- Orientation: M_f[i][j] is the coefficient of f_i f^c_j (particle row, conjugate column; Weyl bilinears are symmetric under exchange, so M_f = B[f, f^c] Y + B[f^c, f] Y^T per channel).  For generic PS-invariant Yukawas (symmetric and antisymmetric parts, on v and on conj(v)) the exact relation is M_e = kappa M_d and M_D = kappa' M_u with no transpose (kappa = +-1 per colour); M_e = kappa M_d^T holds only when the antisymmetric parts vanish (the symmetric dimension-four contract Yukawa, flavour_structure).  The mass relations m_d = m_e, m_s = m_mu, m_b = m_tau do not depend on the orientation.
- Cutoff (exact): the grading (every Dirac Yukawa monomial Sigma-balanced, with any number of B-L-neutral Higgs insertions; PS breaking only through Sigma Sigma^dag pairs) holds at every dimension and for every operator scale Lambda; the PS-invariant remainder (M_e = kappa M_d, M_D = kappa' M_u; M_d = phase x M_u at tan beta = 1) holds at every dimension for the operators linear in H10 or H10^* (any number of PS-singlet spurions; multi-Higgs composites only hand-argued); the explicit census is exhaustive to mass dimension 12 among the single-Higgs (or Higgs-free) monomials of two light 16s (F, P, Q, R) and the witness spurions (multi-Higgs monomials and operators with 16bar or heavy fields are not enumerated).  Cutoff (float): NDA only, not a check: the Sigma-bearing entries, bounded by 4 pi (v_R/Lambda)^2, can reach the observed SU(4)-breaking splittings only if Lambda <= v_R sqrt(4 pi/|y_mu - y_s|) (s-mu) and Lambda <= v_R sqrt(4 pi/|y_tau - y_b|) (b-tau); float_diagnostics.nda_Lambda_max_over_v_R per scale of the data band.
- Scope: exact at every dimension and for every Lambda: the grading (b) (it needs only B-L, so it also covers extra B-L-neutral H10/H10^* insertions) and the PS-invariant remainder (d) for operators linear in H10 or H10^* (any number of PS-singlet spurions); exhaustive to mass dimension 12: the census (c) of single-Higgs (or Higgs-free) monomials of two light 16s (F, P, Q, R) and the witness spurions (necessary conditions X, Z17, (B-L, T3R); SO(10) contraction coefficients are not computed, which is conservative for a no-go).  Multi-Higgs operators (extra H H^dag dressings, e.g. F.F.H10.(H10^dag H10) at dimension 6, X- and Z17-neutral) are B-L-neutral, so the grading (b) still applies to them, but they are EW-vev-suppressed and not enumerated; for their PS-invariant part M_e = kappa M_d follows from lemma_122_clebsch, while M_d = phase x M_u at tan beta = 1 rests on a hand-argued SU(2)_L x SU(2)_R covariance argument (cited_or_hand_argued), not on a check.  Operators with 16bar or heavy fields are covered only through the cited light-state lemma.  It assumes the witness spurion set (p, S, Phi17, Sigma): a B-L-breaking 210 vev ((15,1,1) or (15,1,3), Route A) is (B-L, T3R)-neutral and PS-breaking and evades the grading.  The net Phi17 numbers of the Dirac monomials are recorded as data only; no PQ-neutrality claim is made.  Radiative (loop-level) Pati-Salam breaking is not analysed.

### L5. One light G3221 bidoublet forces s = 1 (CKM = 1) (`lemma_s1_g3221`, 9/9 checks pass)

- Statement: Definition: s = (v_u^126/v_u^10)/(v_d^126/v_d^10), the ratio of the 126bar-to-10 composition of the up-type (Y = +1/2) and the down-type (Y = -1/2) component of the light bidoublet, with each 126bar vev measured in units of the equivariant image iota15 of the corresponding 10 component; then M_d = H + F and M_u = r (H + s F) with H, F the 10 and 126bar contributions to M_d and r = v_u^10/v_d^10, and s = 1 (an SU(2)_R-symmetric composition) gives M_u = r M_d.  (i) iota15(v) = omega6 ^ iota_v p is G3221-equivariant (the six so(4) generators on e6..e9 and the nine u(3) colour generators); (ii) the Y = +-1/2 neutral colour-singlet doublet spaces of the 126bar are one-dimensional (lemma_su5_casimir), so every G3221-equivariant complex-linear map (1,2,2)_10 -> 126bar is a multiple of P_{-i} iota15 (Schur, cited); (iii) the contract's O15 mixing map v -> 2 P_{-i}(v ^ F) is exactly i x 2 P_{-i} iota15(v) at the G3221 direction F = a = omega6 ^ omega6/2 (SU(2)_R-symmetric), has relative sign -1 between z5 (+i) and zbar5 (-i) at the G3211 direction F = omega = omega6 ^ J_R (SU(2)_R-breaking), and vanishes on the doublets at F = p (the witness); (iv) with one light bidoublet L = c Phi10 + d Phi126, Phi126 = iota15(Phi10), symmetric Y10, Y126 and any v = alpha z5 + beta zbar5 (any tan beta), M_u = (alpha/beta) M_d colour by colour with a Yukawa-free ratio, so M_u M_u^dag is proportional to M_d M_d^dag and CKM = 1 (s = 1); M_e is not proportional to M_d (the theorem is about CKM); this is exact for a G3221-equivariant composition, and v_R-scale SU(2)_R breaking through <Sigma> (e.g. O28 with <Sigma>^2, or the <Sigma>-proportional O15 H-Phi block), whose size is not computed, is a further possible source of s != 1 and CKM != 1; (v) escapes: conjugate (antilinear) mixing Phi126 = iota15(conj Phi10) has coefficient determinant c d (alpha alphabar - beta betabar) x const, so proportionality holds iff tan beta = 1; two independent light bidoublets give (alpha1 beta2 - alpha2 beta1) x const.
- O15 mixing / (2 P_{-i} iota15): at a e6 I, e7 I, e8 I, e9 I; at omega e8 none, e9 none, z4 I, z5 I, zbar4 -I, zbar5 -I; at p 0.
- One light bidoublet: u[+--]/d[+--] = alpha/beta, u[-+-]/d[-+-] = alpha/beta, u[--+]/d[--+] = alpha/beta; conjugate mixing determinant 16*I*c*d*(alpha*alphabar - beta*betabar); two-bidoublet determinant 16*I*(alpha1*beta2 - alpha2*beta1).
- Scope: dimension-four Yukawas; the light bidoublet's 10/126bar composition map is G3221-equivariant (true for the <Phi>-mediated O15 H-Sigma block at a (15,1,1) vev, check (iii); <Sigma>-mediated mixings, which break SU(2)_R at v_R, are not analysed).  Not claimed: existence or certifiability of any G3221 vacuum of the contract, the size of s - 1 from v_R-scale SU(2)_R breaking through <Sigma>, the size of conjugate mixing (O38 with <S>), or anything about unification or the seesaw scale on such chains.  At the witness itself (p only) the mixing vanishes (check iii), so the lemma scopes Route A and does not add to Route C.

### L6. The pure 10 + 120 inequality B1a (proved) (`lemma_b1a`, 4/4 checks pass)

- Statement: For complex symmetric S, complex antisymmetric A = [a]_x (3 x 3) and complex x_d, x_e, with M_f = S + x_f A: | ||M_e||_F^2 - ||M_d||_F^2 | <= 2 (||adj M_e||_F + ||adj M_d||_F), where ||M||_F^2 = sum m_i^2 and ||adj M||_F^2 = sum_{i<j} m_i^2 m_j^2 (singular values).  By lemma_122_clebsch this is the form of the down-quark and charged-lepton matrices in a pure 10 + 120 extension (the 10 and the (1,2,2) of the 120 share the lepton/quark Clebsch +1; the (15,2,2) of the 120 has -3), up to the colour sign.
- Proof: (1) Tr(A^dag S) = 0 for S symmetric and A antisymmetric, so ||M_f||_F^2 = ||S||_F^2 + |x_f|^2 ||A||_F^2 and the left side equals ||x_e|^2 - |x_d|^2| ||A||_F^2.  (2) adj(S + x A) = adj S + x C1 + x^2 a a^T with adj S symmetric and C1 antisymmetric (adj(M)^T = adj(M^T), M(x)^T = M(-x)); symmetric and antisymmetric matrices are Frobenius-orthogonal, so ||adj M_f||_F >= ||adj S + x_f^2 a a^T||_F >= | |x_f|^2 ||a||^2 - ||adj S||_F | (reverse triangle inequality, ||a a^T||_F = ||a||^2).  (3) With ||A||_F^2 = 2 ||a||^2 and K = 2 ||adj S||_F: 2 ||adj M_f||_F >= | |x_f|^2 ||A||_F^2 - K |, and |u - w| <= |u - K| + |w - K| gives the claim.  (4) ||adj M||_F^2 = e2(M^dag M) = sum_{i<j} m_i^2 m_j^2 (Cauchy-Binet).  Sharp: at S = 0, x_d = 0 both sides equal 2 |x_e|^2 ||a||^2 (adj(x A) = x^2 a a^T).
- Sharp case: S = 0, x_d = 0.
- Scope: a necessary condition for the hypothetical pure 10 + 120 extension (a Route B sub-branch), proved exactly (sympy identities with independent symbols for entries and conjugates; the triangle inequalities are cited).  Not claimed: its data consequence (not load-bearing, not recorded), any exclusion of a 120_H, or any 10 + 126bar (+ 120) fit.

## (6) Scope and routes

**cited_or_hand_argued**
- electroweak breaking proceeds along the light doublet Re H_6..9 (the only light scalar with doublet quantum numbers; the certified eps >= 0 family itself leaves SU(2)_L x U(1)_Y unbroken)
- the light-state lemma: 16bar components are heavy (generic rank 8 certified; rank 8 at the physical couplings assumed: exactly three light families), heavy-light corrections O(v^2/M_V^2) are dimension >= 6
- no induced (10,3,1) (Delta_L) vev from EW breaking at tree level: the heavy-doublet part is proved (V even in H), the integer-isospin (10,3,1) part rests on the vanishing H-Sigma quartics O31/O35 (checked)
- SM running preserves Yukawa alignment (one-loop form Y g(Y^dag Y); U(1)^3 family symmetry to all orders)
- Mirsky's singular-value inequality; Haynsworth inertia additivity (the Schur complement on the H block decides the second-order stability of q0); the Minkowski and Cauchy-Schwarz inequalities of the combination certificates
- with portals on, the induced heavy vevs are the first-order (in v) response -A^-1 B(c) h v of the light doublet h; O(v^3/M^2) corrections are dimension >= 6
- Y_F (the Yukawa of the canonically normalised (1,2,2) inside the (15,2,2)), the contract's declared Y126 and the seesaw Y_R differ by unfixed Clebsch normalisations; the O28-alone t-b bound is far above 4 pi, so this O(1) ambiguity does not matter
- Schur's lemma: uniqueness of the G3221-equivariant bidoublet map (lemma_s1_g3221) and the SU(5) isotypic corollary of lemma_su5_casimir
- B1a: Frobenius orthogonality of symmetric and antisymmetric matrices and the (reverse) triangle inequality (the identities they act on are checked in sympy)
- the |S| scaling of O38's columns follows from its homogeneity in S^dag (S-degree 1, checked from the census orbit key)
- lemma_S_independence (vii) models O38 by the 10 x 210 -> 126 contraction <conj(H) ^ Phi, conj(Sigma)> conj(S): 10 x 210 = 120 + 126 + 126bar + 1728 contains the 126 once (the 5-form v ^ Phi), so the compiler's O38 is a multiple of it
- multi-Higgs PS-invariant composites (e.g. the (1,2,2) projection of H H H^dag in F.F.H.H.H^dag.S^n): at |alpha| = |beta| the neutral bidoublet vev is r U with U in U(2); writing U = e^{i phi} U' with U' in SU(2), SU(2)_L x SU(2)_R covariance F(L Phi R^dag) = L F(Phi) R^dag gives F(r U) = U' F(r e^{i phi} 1), and F(r e^{i phi} 1) commutes with the diagonal SU(2), so it is a multiple of 1 (Schur): every covariant composite is proportional to U, keeps tan beta = 1 and hence M_d = phase x M_u; M_e = kappa M_d for such composites follows from lemma_122_clebsch (every (1,2,2) source has lepton/quark Clebsch +1).  Hand-argued, not checked
- a second 10_H with H10's (X, Z17) = (-2, 15) or H10^*'s (2, 2) adds H'-linear portals that are, term by term, the witness H portals under H' -> H or H' -> conj(H); the up-type-only selection rule of H_linear_portals is checked on every doublet column Re/Im H_6..9 (hence for every light-doublet direction), so it covers them (not recomputed)
- lemma_eft_census rests on the light-state lemma (light 16s in span{F, P, Q, R}) and on the light doublet being pure 10_H; the (1,2,2) content of 16 x 16 is one symmetric (10) and one antisymmetric (120) channel, which the PS-invariant remainder covers on v and on conj(v)
- Weyl bilinears are symmetric under exchange: M_f[i][j] (the coefficient of f_i f^c_j) = B[f, f^c] Y + B[f^c, f] Y^T per channel

**float_diagnostics**
- data comparison: PDG/FLAG/XZZ inputs, one-loop SM running, pulls (raw and with a 10% theory term)
- O28 bounds at the repository r0 values: theta at |c| = 4 pi and in the colour-stable range, tan beta of the lightest eigenvector of the O(c^2) doublet Schur complement (eigh, phase scan), and the Mirsky t-b requirement
- colour radii rho_d (eigvalsh of the exact triplet Grams; bracketed exactly), the O06-compensated upper radius, and the outer bound on each |c_d| for any combination (Cauchy-Schwarz with the others in the box)
- portal-set bounds: up-type theta_(15,2,2) <= sum_d |c_d| sqrt(2) theta_d (box and colour-stable), the portal-immune data pulls, and tan beta scans per direction over |c| in (0, 4 pi] and over the colour-stable range, and the phase of c
- seesaw: generic Y_R and a scan (random + Nelder-Mead) of textured Y_126
- the O28 and portal lattice bindings compare the compiler's float64 Hessian with the (1/6)-integer patterns
- lemma_eft_census.float_diagnostics: the NDA cutoff Lambda_max/v_R = sqrt(4 pi/|y_l - y_q|) (s-mu, b-tau) below which Sigma-bearing operators could reach the observed SU(4)-breaking splittings (not a check)
- lemma_S_independence.O38_compiler_pattern_corroboration_not_a_check reads the H_linear_portals lattice binding of the compiler's O38 (float64 bound to the (1/6) Z lattice); it corroborates the exact form check (vii) and is not a check

**not_claimed**
- no statement about the G3-G5 scalar-vacuum certificates or the SO(10) contract: they stand
- no loop-level flavour analysis (threshold corrections from 126bar remnants below M_I are O(Y_126^2/16 pi^2))
- the seesaw section is not a no-go (textured Y_126 can lower the requirement), and its non-perturbative generic Y_R assumes M_D = M_u(data), not the witness's own M_D
- the colour-stable region is the second-order (Hessian) region at q0 with the certified couplings; global minimality with any portal on is not certified (a new G3 certificate would be needed); tan beta is freed inside it by O45_B02, so the O28-alone t-b bound is not a statement about the portal set
- no analysis away from q0 (a vacuum with a light or down-type-mixing (15,2,2) is Route A)
- G8 is not closed; Route A or B is required to reach it
- the v2 lemmas are no-go statements about this witness branch and the declared contract's operator content; they do not falsify the contract: a 120_H extension, a Route A branch and the extensions not analysed here remain logically open
- Route B is not reduced to a 120_H among all extensions: among the analysed candidate extensions (a second 10_H, a 10_H^* Yukawa, F.F.H10^*.S^*, PS-singlet dressings of the 10_H, a 120_H) only a 120_H can split d from e; extensions that add a second 126bar_H, a new B-L-breaking scalar vev (e.g. a 45_H (15,1,1) vev) or vectorlike matter were not analysed
- a second 10_H with charges other than H10's or H10^*'s (X, Z17) is covered only at the level of its Yukawa source (its scalar portals are not analysed); a UV completion that adds further PS-breaking operators near v_R is not analysed (only the operator F.F.H10^*.S^* is)
- lemma_122_clebsch says nothing about vevs and does not exclude a 120_H (its (15,2,2) is T15-type); a second 126bar_H was not analysed
- lemma_su5_casimir does not cover the p-mediated portal paths (p is not an SU(5) singlet): those rest on the exact per-r0 Schur computation of H_linear_portals
- lemma_S_independence does not certify q(r_S) with r_S != r0 as a global minimum (G3 there is not certified) and says nothing about D-A unification or O31/O35
- lemma_eft_census: no PQ-neutrality claim (Dirac monomials with net Phi17 number -1, -2 exist); the census checks necessary conditions only (SO(10) contraction coefficients are not computed); it assumes the witness spurion set (a B-L-breaking 210 vev, Route A, evades it); M_e = phase x M_d^T is not claimed for generic Yukawas
- lemma_eft_census: the census covers single-Higgs (or Higgs-free) monomials of two light 16s and the witness spurions only; multi-Higgs monomials (e.g. F.F.H10.(H10^dag H10)) and operators with 16bar or heavy fields are not enumerated, and M_d = phase x M_u at tan beta = 1 is checked for the operators linear in H10 or H10^* only (multi-Higgs PS-invariant composites: hand-argued)
- radiative (loop-level) Pati-Salam breaking is not analysed
- lemma_s1_g3221: no existence or certifiability of a G3221 vacuum of the contract is claimed, nor the size of s - 1 from v_R-scale SU(2)_R breaking through <Sigma> (e.g. O28, or the <Sigma>-proportional O15 H-Phi block) or of conjugate (O38 with <S>) mixing; its list of escapes is exhaustive only for G3221-equivariant compositions
- lemma_b1a: its data consequence is not load-bearing and not recorded; it excludes neither a 120_H nor a 10 + 126bar (+ 120) fit

**proved_exactly**
- the H-linear directions of the 44-direction contract are exactly O15, O28, O38, O45_B01, O45_B02 (census orbit keys) and all ten re/im parameters vanish in the benchmark map for every r0, x0 (sympy)
- exact Hessian (Fraction binding units) at r0 = 1/5, 1/20, 1/100 and the anchor r0: zero gradient, H block decoupled and equal to diag(2, 2 + 2 r0^2 | 0, 2 r0^2) (u coords), Re H_6..9 exact null vectors: the light doublet is pure 10_H with zero 126bar (15,2,2) and zero 210 admixture
- V is even in H on the witness (live H-degrees {0, 1, 2, 4}, H-linear parameters zero), so no heavy doublet (126bar (15,2,2), 210 doublets) gets an induced vev at any order in v at tree level (the SU(2)_L centre -1 composed with H -> -H fixes q0 + h and acts as -1 on every heavy doublet)
- the allowed 16bar x 16 coupling pattern has generic rank 8 (exact rank at deterministic integer couplings; kernel of dimension 3 in span{F, P, Q, R}): exactly three light families for generic couplings
- Gaussian-integer Clifford algebra: 16x16 = 10 + 120 + 126, 16x16bar = 1 + 45 + 210; the 16.16.10 Clebsches at the real neutral vev a e8 + b e9 have |c_f|^2 = a^2 + b^2 for u, d, e, nu (tan beta = 1), constant phases nu/u and e/d; sigma_std couples only nu^c nu^c; the (15,2,2) lepton/quark Clebsch is -3
- contract enumeration from the SARAH model file: no 16.16.10_H^* coupling, H10/126bar Yukawas only on the X = 1 sixteens, 16.16bar masses only from SO(10) singlets, no 120_H
- flavour structure (sympy): M_u M_u^dag = M_d M_d^dag, M_e = phase M_d^T, M_D = phase M_u^T (symmetric dimension-four Y; see lemma_eft_census for generic Y)
- O28 alone: lattice-bound H-Sigma block (+-192 r0^2), exact first-order admixture theta^2 = c^2 r0^4 R(r0) with R = 7962624 (13 r^2+6)^2/(13 r^4+12 r^2+36)^2 (derived from 3 exact points, re-checked at 2, and matched exactly by the first-order solve at 8 r0 values including the anchor and the 4 repository r0), O(c^2) (exactly quadratic) negative doublet Schur complement (saddle) for every c != 0
- all five H-linear portals on the full H block (colour triplets and doublets): all twenty H columns bound to the (1/6) Z lattice with pinned blocks and r0 powers, exact heavy responses, exact Schur Grams (the triplet and doublet blocks decouple, both are phase independent) at the physical member and the 4 repository r0; every doublet-coupled portal makes q0 a saddle for c != 0; O45_B01 has no doublet coupling but, like every portal, couples the colour triplets
- colour-stable radii: H_TT - t G_d has no negative eigenvalue at t = (1 - 1e-6) rho_d^2 and one at (1 + 1e-6) rho_d^2 (exact inertia, per direction and r0)
- selection rule: O15, O28, O45_B02 act only on the Y = +1/2 doublet component, O38 only on Y = -1/2 (integer lattice); the Sigma admixture Gram is 2 theta_Re^2 times the coupled-component projector (theta(tan beta) exact up to the float t); and every portal-induced 126bar vev couples only Q u^c and L nu^c (exact 16.16 bilinears), so M_e = phase x M_d^T for every portal combination at any coefficient
- lemma_122_clebsch (v2): T15 = 3(B-L) on the 16; every (1,2,2) Yukawa source (the 10, a second 10_H, a 10_H^* Yukawa, F.F.H10^*.S^*, F.F.H10.Phi210 at <Phi210> = p) has the lepton/quark Clebsch of the 10 (+1), exactly (oriented Gaussian-integer bilinears); the 126bar (15,2,2) and a hypothetical 120_H (15,2,2) are K T15 times the 10 (lepton/quark -3 on the up- and down-type doublet alike)
- lemma_su5_casimir (v2): SU(5) Casimir 12/5 on both 10_H doublets and on the up-type 126bar doublet, 32/5 on the down-type 126bar doublet (the one coupling d d^c and e e^c); the neutral colour-singlet doublet spaces of the 126bar are one-dimensional; the 5bar has no 126bar image (representation-theoretic scope: SU(5)-equivariant mixings only; p is not an SU(5) singlet)
- lemma_S_independence (v2): S enters the nonzero benchmark only through O04, O23 (S sector) and O12 (H sector); the doublet eigenvectors are Re/Im H_6..9 for every r_S and the retuned H block is diag(2, 2 + 2 r0 r_S | 0, 2 r0 r_S) (Fractions, r_S/r0 = 1, 10, 1000 at four r0), so the light doublet stays pure 10_H with tan beta = 1 for every |S|; O38 (the only S-dependent H-linear direction) has no H x S block and its doublet columns reach only Phi (exact forms of the 10 x 210 -> 126 contraction: e_a ^ p pairs to zero with sigma_std, its conjugate and its Hodge dual, and vanishes for a = 6..9)
- lemma_eft_census (v2): (B-L, T3R) charges derived from the vev forms; every Dirac Yukawa monomial is Sigma-balanced at every dimension (grading; B-L alone, so also with any number of B-L-neutral Higgs insertions) and the census of X-, Z17- and (B-L, T3R)-admissible single-Higgs (or Higgs-free) monomials of two light 16s (F, P, Q, R) and the witness spurions is exhaustive to mass dimension 12 (4657 / 1460 Dirac / 800 Majorana; PS-breaking Dirac entries from dimension 6, H-tilde from 5); for generic PS-invariant Yukawas of the operators linear in H10 or H10^* (any number of PS-singlet spurions) M_e = kappa M_d and M_D = kappa' M_u (no transpose), and at tan beta = 1 M_d = phase x M_u (sympy)
- lemma_s1_g3221 (v2): iota15 = omega6 ^ iota_v p is G3221-equivariant and (with the one-dimensional doublet spaces) the unique bidoublet intertwiner up to scale; the <Phi>-mediated O15 H-Sigma map at the (15,1,1) direction a is i x iota15, at omega it has relative sign -1, at p it vanishes; with a G3221-equivariant composition one light bidoublet gives s = 1, i.e. M_u = (alpha/beta) M_d for any tan beta (CKM = 1); conjugate mixing needs tan beta != 1 and two light bidoublets break it (sympy)
- lemma_b1a (v2): the pure 10 + 120 inequality | ||M_e||_F^2 - ||M_d||_F^2 | <= 2 (||adj M_e||_F + ||adj M_d||_F) (sympy identities: Tr(A^dag S) = 0, the parity split of the adjugate, the norm identities, Cauchy-Binet; the triangle inequalities cited)

- Route A: New in-contract G3 branch: a vacuum in which a DOWN-type doublet from the 126bar (15,2,2) has a nonzero admixture theta_d in the light doublet, large enough that theta_d ||Y_F|| v reaches the required d-e / s-mu / b-tau splittings (theta_d ||Y_F|| ~ 1e-4 at M_I for s-mu; far below O(1) for perturbative Y_F).  At the certified q0 this is impossible at every repository r0 (sections F and F'): theta_d = 0 exactly, because every H-linear portal (O15, O28, O38, O45) feeds only the up-type (15,2,2) (exact Yukawa selection rule), so M_e = phase x M_d^T survives any portal combination; the portals are also colour-limited (|c_O15| <= ~0.79 at every r0, |c_O28| <= rho_O28(r0) ~ 1/r0, 4.5 at the 2HDM-content r0) and every doublet-coupled portal makes q0 a saddle (SOS27 needs portal = 0; O06 cures only the doublet saddle).  A Route A branch must therefore leave q0 (other vevs, or a (15,2,2) near M_I with a down-type mixing channel), keep the colour triplets non-tachyonic, and needs new exact G3/G4/G5 certificates; it may not exist and reopens the 2HDM proton-decay and high-v_R Higgs-matching risks.  At a G3221 point (a (15,1,1) vev, no (15,1,3)) the <Phi>-mediated O15 H-Sigma mixing is SU(2)_R-symmetric, so with a G3221-equivariant composition one light bidoublet still gives M_u proportional to M_d and CKM = 1 (lemma_s1_g3221, exact at dimension four).  The escapes that lemma leaves open are two light bidoublets, an SU(2)_R-breaking (15,1,3) component, conjugate (H.Sigma.S-type) mixing with tan beta != 1, and v_R-scale SU(2)_R breaking through <Sigma> in the bidoublet mixing (e.g. O28 with <Sigma>^2, or the <Sigma>-proportional O15 H-Phi block), whose size is not analysed.
- Route B: Extension beyond the declared contract.  Among the analysed candidate extensions (a second 10_H, a 10_H^* Yukawa, the operator F.F.H10^*.S^*, Pati-Salam-singlet dressings of the 10_H, a 120_H) only a 120_H can split d from e: with X = -2 (Z17 phase 15) F.F.120_H is allowed, and its (15,2,2) component carries the T15 Clebsch (lepton/quark -3) on the down-type doublet as well (lemma_122_clebsch.hypothetical_120_fifteen_component_is_T15_type).  A second 10_H, a 10_H^* Yukawa and the operator F.F.H10^*.S^* (whatever completion generates it), as well as any other Pati-Salam-singlet dressing of the 10_H (e.g. F.F.H10.Phi210 at <Phi210> = p), are excluded as flavour repairs at the level of their Yukawa sources: each is a (1,2,2) source with lepton/quark Clebsch +1 (lemma_122_clebsch), so M_e = phase x M_d and M_D = phase x M_u for generic non-symmetric Yukawas and independent vevs (lemma_eft_census) and the portal-immune tests stay excluded; for F.F.H10^*.S^* on the witness, tan beta = 1 for every |S| (lemma_S_independence) also keeps M_d = phase x M_u (CKM = 1).  A second 10_H is covered at the level of its Yukawa source; its own H'-linear portals are, term by term, the witness portals under H' -> H or H' -> conj(H), so the existing up-type-only selection rule covers them only if it carries H10's (X, Z17) = (-2, 15) or H10^*'s (2, 2) (hand-argued, not recomputed).  Not analysed: a second 10_H with other charges beyond its Yukawa source, a UV completion that adds further PS-breaking operators near v_R, a second 126bar_H, a new B-L-breaking scalar vev (e.g. a 45_H with a (15,1,1) vev, whose F.F.H10.45_H can carry a Georgi-Jarlskog-type T15 Clebsch) and vectorlike matter; so Route B is not reduced to a 120_H among all extensions.  A 120_H is not shown to repair G8: only its (15,2,2) component can split d from e, so the light doublet needs a (15,2,2)_120 admixture whose size is not analysed here, and the pure 10 + 120 limit obeys the exact inequality of lemma_b1a.  The other in-contract option, a B-L-breaking 210 orientation ((15,1,1) or (15,1,3) components), is Route A, not Route B (lemma_s1_g3221).  Changes models/SO10Z17AxionV20.m; G1-G5 restart.
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
- PASS `lemma_122_clebsch.T15_is_three_B_minus_L_on_the_16`
- PASS `lemma_122_clebsch.fifteen_two_two_126bar_is_K_T15_times_ten`
- PASS `lemma_122_clebsch.hypothetical_120_fifteen_component_is_T15_type`
- PASS `lemma_122_clebsch.one_two_two_120_clebsch_equals_ten_clebsch`
- PASS `lemma_122_clebsch.one_two_two_channels_symmetric_10_antisymmetric_120`
- PASS `lemma_122_clebsch.one_two_two_supports_inside_ten_support`
- PASS `lemma_122_clebsch.p_is_the_repository_ps_singlet_e6789`
- PASS `lemma_S_independence.O12_block_symbolic_in_S_matches_binding_unit`
- PASS `lemma_S_independence.O38_H_columns_have_no_S_block`
- PASS `lemma_S_independence.S_block_decoupled_in_every_binding_unit`
- PASS `lemma_S_independence.doublet_eigenvectors_independent_of_S_modulus`
- PASS `lemma_S_independence.only_O12_is_S_dependent_among_nonzero_H_quadratics`
- PASS `lemma_S_independence.only_O38_is_S_dependent_among_H_linear_directions`
- PASS `lemma_S_independence.retuned_H_block_exact_at_every_tested_r_S`
- PASS `lemma_S_independence.tan_beta_one_for_every_phase_rotated_real_doublet`
- PASS `lemma_b1a.adjugate_norm_is_e2_of_singular_values`
- PASS `lemma_b1a.adjugate_parity_decomposition`
- PASS `lemma_b1a.frobenius_pythagoras_TrAdagS_zero`
- PASS `lemma_b1a.norm_identities_aaT_and_A`
- PASS `lemma_eft_census.census_counts_to_dimension_12_pinned`
- PASS `lemma_eft_census.every_dirac_monomial_sigma_balanced_to_dimension_12`
- PASS `lemma_eft_census.every_ps_breaking_dirac_monomial_carries_a_sigma_pair`
- PASS `lemma_eft_census.generic_tan_beta_Md_not_proportional_to_Mu_with_Htilde`
- PASS `lemma_eft_census.grading_forces_sigma_balance_at_every_dimension`
- PASS `lemma_eft_census.light_sixteens_are_the_rank_certificate_kernel`
- PASS `lemma_eft_census.majorana_monomials_carry_net_one_sigma`
- PASS `lemma_eft_census.min_dimension_Htilde_dirac_is_5`
- PASS `lemma_eft_census.min_dimension_ps_breaking_dirac_is_6`
- PASS `lemma_eft_census.no_T3R_mismatched_dirac_monomial`
- PASS `lemma_eft_census.no_single_sigma_dirac_monomial`
- PASS `lemma_eft_census.p_S_Phi17_vevs_carry_zero_charge`
- PASS `lemma_eft_census.ps_invariant_MD_equals_kappa_Mu_for_generic_Y`
- PASS `lemma_eft_census.ps_invariant_Me_equals_kappa_Md_for_generic_Y`
- PASS `lemma_eft_census.sigma_vev_charge_is_minus2_plus1`
- PASS `lemma_eft_census.tan_beta_one_gives_Md_equal_phase_Mu_with_Htilde_and_120_channel`
- PASS `lemma_eft_census.ten_doublet_and_dirac_pair_charges`
- PASS `lemma_eft_census.transposed_relation_holds_only_for_symmetric_Y`
- PASS `lemma_eft_census.z17_automatic_for_every_X_neutral_monomial`
- PASS `lemma_s1_g3221.O15_at_G3211_direction_omega_has_relative_sign_minus_one`
- PASS `lemma_s1_g3221.O15_at_G3221_direction_a_equals_i_iota15`
- PASS `lemma_s1_g3221.O15_at_ps_singlet_p_vanishes_on_the_doublets`
- PASS `lemma_s1_g3221.conjugate_mixing_proportional_iff_tan_beta_one`
- PASS `lemma_s1_g3221.g3221_bidoublet_intertwiner_unique_up_to_scale`
- PASS `lemma_s1_g3221.iota15_is_G3221_equivariant`
- PASS `lemma_s1_g3221.one_light_bidoublet_Me_not_proportional_Md`
- PASS `lemma_s1_g3221.one_light_bidoublet_Mu_proportional_Md_for_any_tan_beta`
- PASS `lemma_s1_g3221.two_independent_light_bidoublets_break_proportionality`
- PASS `lemma_su5_casimir.casimir_12_over_5_on_every_z_and_zbar`
- PASS `lemma_su5_casimir.fivebar_doublet_has_no_image_in_126bar`
- PASS `lemma_su5_casimir.neutral_colour_singlet_doublet_spaces_of_126bar_are_one_dimensional`
- PASS `lemma_su5_casimir.sigma_down_doublet_casimir_32_over_5_down_type_only`
- PASS `lemma_su5_casimir.sigma_std_is_su5_singlet`
- PASS `lemma_su5_casimir.sigma_up_doublet_casimir_12_over_5_up_type_only`
- PASS `lemma_su5_casimir.u5_generators_in_so10_and_commute_with_J`
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
