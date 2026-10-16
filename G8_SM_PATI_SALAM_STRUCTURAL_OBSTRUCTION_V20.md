# G8 structural obstruction: the SOS-certified witness family is flavour-dead (v20, evidence only)

- Status: `G8_SM_PATI_SALAM_STRUCTURAL_OBSTRUCTION__SOS_CERTIFIED_FAMILY_FLAVOUR_DEAD__RECORDED__NO_GATE_CHANGE`
- Overall state: `CERTIFIED_WITNESS_FAMILY_FLAVOUR_DEAD_EXACT__OFF_ORIENTATION_SPLITTERS_RESEARCH_RECORDED`
- Checks: 78/78 pass (expected 78)
- No gate status changes; not wired into the gate ledger.

## Verdict

EXACT: every vacuum in the degree-2-SOS-certified witness family (the committed witness, the r_S family and the O36 lambda_H member, certified by g3_sm_pati_salam_higgs_quartic_member_v20) is flavour-dead: M_e = phase x M_d^T and CKM = 1 (tan beta = 1) at the level of the light (dimension-4) Yukawa matrices.  The Weyl element g_de (pi-rotation in the (3,5) plane, lift Gamma_3 Gamma_5) fixes every charged-sector vev bilinear and maps d[+--] to e[+++]; sigma_std couples only nu^c nu^c; so spec(M_d) = spec(M_e) for any 16/16bar content (L1).  g_cust (the (7,9) plane) gives spec(M_u) = spec(M_d) exactly and CKM = 1 at the dimension-4 level at tan beta = 1 (L2); with 16bar content the charged current of full mass eigenstates is (phases)(1 - K), K = U_d^dag P_{16bar SU(2)_L-singlet} U_d = O(v^2/M_V^2) (dimension-6 non-unitarity; exactly 0 without 16bar states).  This holds for any H-linear portal (L1 is portal-robust; every doublet-coupled portal (O15, O28, O38, O45_B02) makes q0 a saddle, O45_B01 has no doublet coupling (flavour-inert), and any portal != 0 is outside the SOS27 certificate), for vectorlike 16s on contract scalars and P/Q/R promotion (the contract's 74 couplings have no X-neutral 16bar.16 pair), and for a 120_H added as SOS squares with a GUT-scale (15,2,2)_120 (M15 ~ M_GUT): the d/e split then enters only through a (15,2,2)_120 admixture of O((v_R/M15)^2) = O(r0^2) (X-parity bounds the PS-breaking H/T entries at O(r0^2): Sigma number even through degree 11, the first odd-Sigma monomial at degree 12); a tuned-light (15,2,2)_120, which SOS squares allow, gives O(1) splitting (research selection120 C4_tuned_15) and is excluded only numerically (no perturbative two-loop root, research).  The 126bar's (15,2,2) (not the 120's) has m^2 = p^2/2 + O(r0^2) across the family.  Off q0 every H-linear portal's down-type 126bar source needs a (15,1,1) or (15,1,3) Phi vev, i.e. it leaves the certified orientation.  RESEARCH_RECORD (not re-derived): the 45 scalar portal, vectorlike matter with a reoriented 210 and the off-witness ERT channel also split d from e, but all sit off the certified orientation; a second 126bar is Landau-excluded at BM-DA1 (8.1e17 GeV, two loops).  G8 is not closed, the contract and the G3-G5 certificates are not falsified, and no gate status changes.

## (A) Weyl-element lemmas [EXACT]

| element | lift | covariant | monomial | flipped weight slots |
|---|---|---|---|---|
| g_cust | Gamma_7 Gamma_9 | True | True | [3, 4] |
| g_de | Gamma_3 Gamma_5 | True | True | [1, 2] |

| vev | g_de | g_cust |
|---|---|---|
| 10_doublet_e6 | +1 (fixed) | +1 (fixed) |
| 10_doublet_e7 | +1 (fixed) | -1 (odd) |
| 10_doublet_e8 | +1 (fixed) | +1 (fixed) |
| 10_doublet_e9 | +1 (fixed) | -1 (odd) |
| 126bar_sigma_std | moved | moved |
| 210_(15,1,1)_B-L | moved | +1 (fixed) |
| 210_PS_singlet_p | +1 (fixed) | +1 (fixed) |
| 45_B-L | moved | +1 (fixed) |
| 45_T3L | +1 (fixed) | -1 (odd) |
| 45_T3R | +1 (fixed) | -1 (odd) |

State maps on the 16: g_de d[+--] -> e[+++], d[-+-] -> d[--+], d[--+] -> d[-+-], dc[++-] -> dc[+-+], dc[+-+] -> dc[++-], dc[-++] -> ec[---], e[+++] -> d[+--], ec[---] -> dc[-++], nu[+++] -> u[+--], nuc[---] -> uc[-++], u[+--] -> nu[+++], u[-+-] -> u[--+], u[--+] -> u[-+-], uc[++-] -> uc[+-+], uc[+-+] -> uc[++-], uc[-++] -> nuc[---].

g_cust d[+--] -> u[+--], d[-+-] -> u[-+-], d[--+] -> u[--+], dc[++-] -> uc[++-], dc[+-+] -> uc[+-+], dc[-++] -> uc[-++], e[+++] -> nu[+++], ec[---] -> nuc[---], nu[+++] -> e[+++], nuc[---] -> ec[---], u[+--] -> d[+--], u[-+-] -> d[-+-], u[--+] -> d[--+], uc[++-] -> dc[++-], uc[+-+] -> dc[+-+], uc[-++] -> dc[-++].

- sigma_std 16.16 entries: [['nuc[---]', 'nuc[---]', [0, 32]]].
- Torus reduction: {'determinant': '1', 'doublet_image': ['sqrt(a**2 + b**2)', '0'], 'fixes_p': True, 'reduces_real_doublet_to_e8': True, 'sigma_std_phase_unit': True, 'z5_phase': '(a + I*b)/sqrt(a**2 + b**2)'}.
- L1: For any content of 16/16bar Weyl fermions coupled only to the witness vevs (singlets S, Phi17 and bare masses, p, H in span(e6..e9), sigma_std): the charged blocks (Q = -1/3, -1) see no sigma_std (it couples only neutral states), every other vev bilinear is exactly S_de-invariant, and S_de maps the colour-(+--) Q = -1/3 sector onto the Q = -1 sector in both chiralities; so M_e = S_de^T M_d S_de up to unit phases and spec(M_d) = spec(M_e), light and heavy, colour by colour (the charged-sector vevs are SO(6)-invariant).
- L2: At tan beta = 1 (a real neutral doublet, reduced to e8 by the (8,9) torus element): S_cust fixes the bilinears of the singlets, p and e8 exactly, sigma_std stays in the neutral sector, and S_cust maps every up-quark sector onto the down-quark sector of the same colour and acts on every SU(2)_L doublet state as the W_L partner map: spec(M_u) = spec(M_d) exactly and U_u = S U_d, so CKM = 1 exactly at the level of the light (dimension-4) Yukawa matrices (and for purely chiral 16 content); with 16bar content the W_L current does not act on the 16bar SU(2)_L-singlet components, so the charged-current matrix of full mass eigenstates is (phases)(1 - K), K = U_d^dag P_{16bar SU(2)_L-singlet} U_d = O(v^2/M_V^2) (dimension-6 non-unitarity; exactly 0 without 16bar states).

## (B) Corollaries [EXACT]

- Every renormalizable fermion-scalar coupling of the contract (26 field-level, 74 generation-expanded) uses a 10_H, a 126bar or an SO(10)-singlet vev; no 16bar.16 pair is X-neutral (Z17 = X mod 17 for every field, so the X census is complete), so no 210 or bare 16bar.16 mass exists.  Promoting P, Q, R changes no vev bilinear, and a vectorlike 16 + 16bar pair coupled to contract scalars adds only 16bar_V.16.Phi210 at p, bare masses and 10_H / 126bar / singlet couplings: all their bilinears are the L1/L2-invariant ones (or neutral-only for sigma_std), so L1 and L2 hold for any such content.
- Scalars used: Delta126bar, H10, Phi17, S, conj[Delta126bar], conj[H10], conj[Phi17], conj[S]; generation-expanded couplings: 74.
- Vectorlike pair: new couplings Delta126bar.F.Vv, Delta126bar.P.Vv, Delta126bar.R.Vv, Delta126bar.Vv.Vv, H10.F.Vv, H10.P.Vv, H10.Qbar.Vvbar, H10.R.Vv, H10.Vv.Vv, Phi17.Rbar.Vv, Phi210.F.Vvbar, Phi210.P.Vvbar, Phi210.R.Vvbar, Phi210.Vv.Vvbar, conj[Delta126bar].Vvbar.Vvbar, conj[H10].Vvbar.Vvbar, conj[Phi17].Pbar.Vv, conj[S].Qbar.Vv.

## (C) X-parity of an added 120_H [EXACT]

| total degree <= D | Sigma numbers |
|---|---|
| 2 | [0] |
| 3 | [0] |
| 4 | [0, 2] |
| 5 | [0, 2] |
| 6 | [0, 2, 4] |
| 7 | [0, 2, 4] |
| 8 | [0, 2, 4, 6] |
| 9 | [0, 2, 4, 6] |
| 10 | [0, 2, 4, 6, 8] |
| 11 | [0, 2, 4, 6, 8] |
| 12 | [0, 1, 2, 4, 6, 8, 10] |
| 13 | [0, 1, 2, 3, 4, 6, 8, 10] |

- Minimal odd-Sigma degree: 12; examples: H* H* Sigma* S^7 Phi17*^2; H* T* Sigma* S^7 Phi17*^2; T* T* Sigma* S^7 Phi17*^2; H H Sigma S*^7 Phi17^2.
- SM-Cartan kernel on the 120: {'controls_annihilated': True, 'dimension': 120, 'kernel_zero': True, 'rank_GFp': 120}.
- T-linear covariants (nonzero components): {'(Sigma0 Sigma0* Sigma0*)_3': 0, '(Sigma0 p p)_3': 0, '(Sigma0* Sigma0 Sigma0)_3': 0, '(Sigma0* p p)_3': 0, '(Sigma0*.p)_3': 0, '(Sigma0.p)_3': 0}.
- p-only operators: 2496 (1,2,2) <-> (15,2,2) matrix elements, max |value| 0; controls 6, 12.
- At the witness the only PS-breaking vev is Sigma = r0 sigma_std; p, S and Phi17 are PS singlets.  Every X-neutral H/T bilinear operator through total degree 11 carries an even Sigma number, and its p-only (PS-invariant) part has zero (1,2,2) <-> (15,2,2) matrix elements, so every PS-breaking H/T bilinear entry is O(r0^2) (two Sigma insertions).  The 120 has no SM-Cartan-neutral vector, so every T-linear term vanishes at q0 (checked explicitly for six covariants) and 120 squares that vanish at q0 keep q0 an exact SOS minimum (research construction sos120 E3).  Z17 = X mod 17 for every field, so Z17 removes nothing further.

## (D) s-structure and the real-type lemma [EXACT]

- s(G3221) - 1 = -e*(alpha*alphabar - beta*betabar)/(alpha*(alphabar*e + betabar*d)).
- s at the claimed points: ['1', '1', '1', '1', '1']; control (tan beta = 2, e != 0): 1/2.
- so(4) commutant dimension 1; invariant two-copy forms 3.
- For a G3221 composition (d_u = d_d, e_u = e_d) s - 1 = -e (|alpha|^2 - |beta|^2)/(alpha (d conj(beta) + e conj(alpha))): s = 1 iff e = 0 (no conjugate mixing) or tan beta = 1.  The so(4) commutant on the real (2,2) is R, so every G3221-invariant real quadratic form on m copies is A (x) I_4, its eigenvectors are a (x) v with v a real (2,2) vector, and ||P_+ v|| = ||P_- v|| (P_- = conj(P_+)): one tuning of a G3221-invariant mass form gives tan beta = 1 for the 10 and |v_u^126| = |v_d^126|, hence s = 1 and CKM = 1 (G8 v2 lemma_s1_g3221).

## (E) Off-q0 selection polynomials [EXACT by lattice binding]

- live compiler adapter functions (portal.base_derivative for O15 and O38 with the S^dag dressing, the exact phi2_bilinear source with the 210/1050 chiral projectors for O45); H x Sigma block at H = 0, Sigma = r0 sigma_std; O15 and O45 blocks do not depend on (r0, rS), O38's is linear in rS (census S^dag degree 1): evaluated at r0 = rS = 1.
- Compiler binding: {'max_abs_deviation': 7.1054273576e-15, 'point_p_a_w': [3, 1, 2], 'r0': '1', 'rS': '1/2'}.

| source | Yukawa type | f(p, a, w) (integer forms) |
|---|---|---|
| O15 H+ | up | `a + w` |
| O15 H- | down | `a - w` |
| O38 H+ | down | `a - w` |
| O38 H- | up | `a + w` |
| O45_B01 H+ | up | `a**2 + 2*a*w + p*w + 2*w**2` |
| O45_B01 H- | down | `-a**2 + 2*a*w + p*w - 2*w**2` |
| O45_B02 H+ | up | `-a**2 - 2*a*w + 2*p*w + w**2` |
| O45_B02 H- | down | `a**2 - 2*a*w + 2*p*w - w**2` |

- O28 pair types at the generic point: {'im': {'+': ['d-uc', 'e-nuc', 'nu-nuc', 'u-uc'], '-': []}, 're': {'+': ['d-uc', 'e-nuc', 'nu-nuc', 'u-uc'], '-': []}}.
- Research a3 consistency (NUM): {'compared': 8, 'consistent': True, 'max_relative_deviation': 2.30787646882e-07}.
- Every H-linear portal's doublet -> Sigma response is a polynomial f(p, a, w) times a fixed Sigma vector (rank one per doublet vector), with no pure-p term: at a = w = 0 (the certified orientation) it vanishes, so no down-type 126bar source exists there (O28, Phi-independent, is up-type only).  O15 and O45 feed up-type from the Y = +1/2 doublet and down-type from Y = -1/2 (O15: a + w and a - w); O38 is conjugate (Y = +1/2 -> down-type with a - w, Y = -1/2 -> up-type with a + w).  A down-type source needs a != 0 or w != 0, i.e. a (15,1,1) or (15,1,3) Phi vev, which leaves the certified orientation.

## (F) m^2((15,2,2) of 126bar) [EXACT]

| G6 factor | multiplicity | roots at r0 = 0 |
|---|---|---|
| lam - (1/2) | 12 | ['1/2'] |
| lam - (1/2 + 1/96*r0^2) | 44 | ['1/2'] |
| lam - (1/2 + 37/576*r0^2) | 48 | ['1/2'] |
| lam - (1/2 + 353/3360*r0^2) | 12 | ['1/2'] |
| lam^2 - (2 + 10/3*r0^2)*lam + (3/4 + 1/4*r0^2 + 13/48*r0^4) | 4 | ['1/2', '3/2'] |

- The 126bar (15,2,2) levels of the committed G6 tree spectrum are 1/2, 1/2 + r0^2/96, 1/2 + 37 r0^2/576, 1/2 + 353 r0^2/3360 and the 1/2-branch of lam^2 - (2 + 10 r0^2/3) lam + (3/4 + r0^2/4 + 13 r0^4/48): 120 real states with m^2 = p^2/2 + O(r0^2) (M_GUT^2, |p| = 1 chart unit).  r_S enters only the O12, O04 and O23 units (H and S blocks), and the O36 units are empty at H = 0, so the Phi/Sigma/Phi17 blocks (hence these levels) are the same for the r_S family and the O36 lambda_H member.

## (G) Headline [EXACT, composed]

- Every vacuum in the degree-2-SOS-certified witness family (the committed witness, the r_S family and the O36 lambda_H member, whose certificate is g3_sm_pati_salam_higgs_quartic_member_v20; they share the Phi/Sigma/Phi17 blocks and the charged-sector vev set) is flavour-dead: M_e = phase x M_d^T and CKM = 1 (tan beta = 1) at the level of the light (dimension-4) Yukawa matrices, for (i) any H-linear portal (L1 keeps M_e = phase x M_d^T at any coefficient; every doublet-coupled portal (O15, O28, O38, O45_B02) makes q0 a saddle, O45_B01 has no doublet coupling (flavour-inert), and any portal != 0 is outside the SOS27 certificate, G8 v2), (ii) vectorlike 16s on contract scalars, (iii) P/Q/R promotion and (iv) a 120 added as SOS squares with a GUT-scale (15,2,2)_120 (M15 ~ M_GUT), up to an O(r0^2) = O((v_R/M15)^2) (15,2,2)_120 admixture.  With 16bar content ((ii), (iii) and the contract's own Pbar, Qbar, Rbar) the charged current of full mass eigenstates is non-unitary at O(v^2/M_V^2) (dimension 6); a tuned-light (15,2,2)_120 is outside (iv) (O(1) splitting, research selection120 C4_tuned_15; excluded only numerically, no perturbative two-loop root, research).
- Caveat: RESEARCH_RECORD (portal_ckm_caveat): with the up-type portal on, CKM != 1 is possible in a toy at unphysical portal size; G8 v2 bounds theta < 1e-3 and a portal != 0 is outside the certified family; L1 (d = e) is portal-robust.

## (H) Research record (not re-derived)

- scratch research outputs of 2026-09-27 (wfRESCUE rescue study); not in the repository; hashes recorded for audit only; the source files are not in the repository and were hashed at generation time (the session scratch area that held them was wiped afterwards), so the sha256 values are a record of the inputs and are not re-verified at runtime.
- the 45 scalar portal H^*.126bar.45.45 (X, Z17, PQ neutral) with the 45.45.210 cubic: a 126bar vev along H^(A^A) couples Q d^c and L e^c with |lepton/quark| = 3 (forty_five_scalar_portal).
- one vectorlike 16 + 16bar (X = +-1) plus the contract's own 210 with (15,1,1)/(15,1,3) vevs ((c')): splits d/e and u/d, CKM != 1 at tan beta = 1; two-loop Landau at BM-DA1 with 1 VL at mu_G 2.694e18 GeV (v1_independent_spinor, vectorlike_reoriented_210_landau).
- the off-witness ERT channel H.126bar^*.Phi210 at a != omega, a - omega ~ mu eta v_R^2 (1/M_a^2 - 1/M_omega^2) (off_witness_ERT_channel).
- a second 126bar_H: Landau-excluded at BM-DA1, two-loop alpha = 1 at 8.1e17 GeV (second_126bar_landau); no mixed Phi-Sigma single-step portal, so no first-order d/e split at the quartic level (second_126bar_portal_census).
- pure 10 + 120 fits: chi2 = 38.5 at v_R = 1.27e9 GeV and 43.3 at 1e13 GeV (pure_10_120_fit_*).
- the one-vectorlike-family c/s inequality at tan beta = 1: violated by a factor 3.65 (one_vectorlike_family_cs_inequality).
- a tuned-light (15,2,2)_120 (allowed by SOS squares) gives O(1) d/e splitting, 0.65 at M15 = 1.2 v_R (selection120_tuned_light_1522), and is excluded only numerically: no perturbative two-loop root (light_1522_no_perturbative_two_loop_root, light_1522_root_lost_to_strong_coupling).

| file | sha256 |
|---|---|
| A/a1_selection_offq0.json | `236d57400052c7420995b76a0303241cf2a9c70ed72026a40a5ed606b57b967c` |
| A/a2_s_structure.json | `138cde03a608ad8d48e2dd90d9b5e176678f77d14b29f019a6b0c874f66bf1c3` |
| A/a3_portal_polynomials.json | `78300c431e63d976a3bc6f7a1c5a7f3dbfd8d0cf637bebdcf0f9e20ab71cc359` |
| B/fitB_pure10_120_1.27e+09_21.json | `c3def7c804fcaa8a2240bef012869af916d902ae6022a9ef5e7f1c7425a60a15` |
| B/fitB_pure10_120_1e+13_22.json | `868b822b0497782c1a3bce914accee6d45ea37d9fb58ffe3fd4a5fd832ccea85` |
| B/selection120.json | `3362628b29e5078a716221bebe6413e7cf935bd12624d58c3a74e81b6787621c` |
| B/sos120.json | `526d4551a529c3e7ceb3de61411374de9d89f749092ec44847fe81f7839378f9` |
| B/verify-feasibility/xparity.json | `aa4b4c4cd5dfbc9f520a3027db955d6b2aa6d70e9be180fa00fcfddb7d1e48fd` |
| C/c1_spinor.py | `5fd049bbdcafb843dfd870bf28eac6328ed5b10d6a18ff0ae1ffe11c58919b9d` |
| C/c2_weyl_lemmas.json | `0004d434d35daddfbcfd8e09b1a0e01bc2a86011afc4305fe9bacfaa2857d3a0` |
| C/c2_weyl_lemmas.py | `3c2f838e6ee4513027bbef97e56ef25fba7f53818e0bfa461188e39c9b7c1473` |
| C/c6_landau_cost.json | `78cc4eb01879dae36a6aeeee96339ec1772c7409621ba237479fa4464afbb1a4` |
| C/c8_second126_portals.json | `294d5c0552ee5fae3f5b5f1efa8ac1938a23d2374d0566cac8cdc11dd0a24a1f` |
| C/verify-feasibility/v3_45_scalar_portal.json | `f19529928b77c65194f648efd8646731a5d0bddcece16602dfc90b64a54024f8` |
| C/verify-physics/v1_spinor_indep.json | `9316dc7d66d37f01d7a11eca7645cf0f19930d85bfa07c2b14cf384b95e3d0bb` |
| critic/c1_f17_light1522_scan.json | `4481ba5df0ee232dec1a04c39439fcfda59a423312d9b84239bb52488b139d3d` |
| routes_and_verdicts.json | `c20dff1098e95288b4b66a7060e3571dce3ed4f5eb56fd62c7cb938fe22f6434` |

## Scope

**claimed**
- (A) Weyl-element lemmas L1 (d <-> e) and L2 (u <-> d: spec(M_u) = spec(M_d) and CKM = 1 at the level of the light (dimension-4) Yukawa matrices at tan beta = 1) in G8 v2's exact Clifford algebra
- (B) contract census (26 field-level / 74 generation-expanded couplings, no X-neutral 16bar.16 pair, Z17 = X mod 17) and the P/Q/R and vectorlike corollaries
- (C) X-parity census of an added 120_H (Sigma number even through degree 11, first odd at 12), no SM-Cartan-neutral vector in the 120, T-linear covariants zero, p-only operators with zero (1,2,2) <-> (15,2,2) matrix elements
- (D) s-structure closed form, s = 1 iff e = 0 or tan beta = 1, so(4) commutant dimension 1, A (x) I_4 forms, equal Y projections of a real (2,2) vector
- (E) off-q0 H-doublet -> Sigma selection polynomials of O15, O38, O45 (exact by lattice binding; bound to the live compiler at a generic point), O28 Phi-independent and up-type only
- (F) m^2((15,2,2) of 126bar) = p^2/2 + O(r0^2) bound to the committed G6 tree spectrum; r_S and lambda_H independence of the Phi/Sigma/Phi17 blocks
- (G) the headline composition with G8 v2 (committed, 157 checks), the committed r_S family and the committed O36 lambda_H member (g3_sm_pati_salam_higgs_quartic_member_v20, read fail-closed)

**float_or_research**
- (E) the rational-point verification compares float evaluations with the exact polynomials (<= 1e-12 relative)
- (E) the research a3 least-squares coefficients are compared (NUM, relative 1e-5) with the exact factors
- (H) every research record: float spectra of the Weyl lemmas, the off-orientation splitters, Landau numbers, fits, the admixture slope

**not_claimed**
- no statement off the certified orientation beyond the research record: the 45 scalar portal, vectorlike matter with a reoriented 210 and the off-witness ERT channel are research-recorded, not re-derived here
- no loop-level flavour (threshold corrections, radiative PS breaking)
- the Phi-sector-only degree-2 SOS no-go for G3221/G3211 orientations is a research NUM statement, not proved here
- no exclusion of the SO(10) contract and no statement about the G3-G5 scalar-vacuum certificates (they stand)
- the 120 statement holds for a GUT-scale (15,2,2)_120 (M15 ~ M_GUT): the d/e split enters only through a (15,2,2)_120 admixture of O((v_R/M15)^2) = O(r0^2); a tuned-light (15,2,2)_120, which SOS squares allow (sos120 E4 leaves 44 massless (15,2,2)_120 components and the W1 mass M is free), gives O(1) splitting (research selection120 C4_tuned_15) and is excluded only numerically (no perturbative two-loop root, research); it is not analysed exactly here
- CKM = 1 is exact only at the level of the light (dimension-4) Yukawa matrices (or for purely chiral 16 content); with 16bar content the charged current of full mass eigenstates is (phases)(1 - K), K = O(v^2/M_V^2) (dimension-6 non-unitarity), not computed here
- with a portal switched on, CKM != 1 is not excluded (research toy caveat); such a point is outside the certified family
- G8 is not closed and no gate status changes; the module is not wired into the gate ledger

## Flags

- `G8_closed`: False
- `L1_portal_robust`: True
- `certified_family_flavour_dead_exact`: True
- `evidence_only`: True
- `falsifies_G3_G5_certificates`: False
- `falsifies_so10_contract`: False
- `gate_status_changed`: False
- `loop_level_flavour_analysed`: False
- `off_orientation_splitters_rederived_here`: False
- `off_orientation_splitters_research_recorded`: True
- `report_closes_G8_by_itself`: False
- `route_B_reduced_to_120H_among_all_extensions`: False
- `wired_into_gate_ledger`: False

## Checks

- PASS `corollaries.PQR_present_and_coupled_only_through_contract_scalars`
- PASS `corollaries.Z17_equals_X_mod_17_for_every_field`
- PASS `corollaries.contract_couplings_26_field_level_74_generation_expanded`
- PASS `corollaries.contract_couplings_use_only_H10_126bar_and_singlet_vevs`
- PASS `corollaries.corollaries_follow_from_L1_and_L2`
- PASS `corollaries.no_X_neutral_16bar_16_pair_in_contract`
- PASS `corollaries.vectorlike_pair_adds_only_contract_scalar_p_and_bare_couplings`
- PASS `fifteen_two_two_mass.O36_units_empty_at_H_zero_lambda_H_independent`
- PASS `fifteen_two_two_mass.chart_units_p_squared_one`
- PASS `fifteen_two_two_mass.fifteen_two_two_levels_bound_to_committed_g6_factors`
- PASS `fifteen_two_two_mass.fifteen_two_two_levels_tend_to_one_half_as_r0_to_0`
- PASS `fifteen_two_two_mass.fifteen_two_two_real_dimension_120_on_the_one_half_branch`
- PASS `fifteen_two_two_mass.g6_tree_spectrum_committed_status`
- PASS `fifteen_two_two_mass.phi_sigma_phi17_hessian_blocks_identical_at_witness_and_rS_1_member`
- PASS `fifteen_two_two_mass.rS_dependence_confined_to_O12_O04_O23_units_in_H_S_blocks`
- PASS `headline.family_committed_status_77_checks_0_failed`
- PASS `headline.flavour_capable_sources_require_leaving_the_certified_orientation`
- PASS `headline.g8_v2_committed_status_157_checks_0_failed`
- PASS `headline.g8_v2_portal_rules_and_S_independence_exact`
- PASS `headline.g8_v2_route_b_text_corrected`
- PASS `headline.headline_certified_family_flavour_dead`
- PASS `headline.o36_quartic_member_committed_certified_0_failed`
- PASS `offq0_selection.O28_phi_independent_and_up_type_only_at_generic_point`
- PASS `offq0_selection.direct_blocks_equal_live_compiler_rows_at_generic_point`
- PASS `offq0_selection.doublet_to_sigma_response_vanishes_at_a_w_zero`
- PASS `offq0_selection.each_doublet_source_feeds_one_pinned_yukawa_type`
- PASS `offq0_selection.lattice_bound_at_every_integer_point_margin_0_49`
- PASS `offq0_selection.polynomial_identity_verified_at_extra_points`
- PASS `offq0_selection.portal_phi_degrees_from_committed_census_representatives`
- PASS `offq0_selection.research_a3_coefficients_consistent_NUM`
- PASS `offq0_selection.responses_rank_one_with_pinned_O15_O38_factors_no_p2_in_O45`
- PASS `research_record.research_entries_labelled_with_provenance`
- PASS `research_record.research_files_digest_pinned`
- PASS `research_record.research_off_orientation_splitters_recorded_with_sources`
- PASS `s_structure.conjugate_mixing_with_tan_beta_2_gives_s_one_half`
- PASS `s_structure.invariant_forms_on_two_copies_are_A_tensor_I4`
- PASS `s_structure.real_22_vector_has_equal_Y_projections_tan_beta_one`
- PASS `s_structure.s_equals_one_iff_e_zero_or_tan_beta_one_symbolic`
- PASS `s_structure.s_equals_one_on_the_claimed_point_set`
- PASS `s_structure.s_minus_1_closed_form_G3221_exact`
- PASS `s_structure.so4_commutant_on_real_22_is_one_dimensional`
- PASS `scope.status_neutral_never_true_flags_false`
- PASS `weyl_lemmas.L1_composed_spec_Md_equals_spec_Me`
- PASS `weyl_lemmas.L2_composed_tan_beta_one_spec_Mu_equals_spec_Md_and_dim4_CKM_one`
- PASS `weyl_lemmas.charged_sector_vevs_so6_invariant_colour_by_colour`
- PASS `weyl_lemmas.g_cust_fixes_singlet_p_e8_bilinears_exactly`
- PASS `weyl_lemmas.g_cust_is_the_su2L_partner_map_on_every_doublet_state`
- PASS `weyl_lemmas.g_cust_lift_monomial_flips_only_w3_w4`
- PASS `weyl_lemmas.g_cust_lift_squares_to_minus_one`
- PASS `weyl_lemmas.g_cust_maps_u_d_uc_dc_e_nu_ec_nuc_colour_preserved`
- PASS `weyl_lemmas.g_cust_maps_up_quark_sectors_onto_down_quark_sectors`
- PASS `weyl_lemmas.g_cust_moves_e9_and_45_T3R_controls`
- PASS `weyl_lemmas.g_cust_spinor_lift_covariant_exact`
- PASS `weyl_lemmas.g_de_fixes_every_charged_sector_vev_bilinear_exactly`
- PASS `weyl_lemmas.g_de_flips_only_colour_weights_w1_w2`
- PASS `weyl_lemmas.g_de_lift_monomial_with_unit_phases_on_32_states`
- PASS `weyl_lemmas.g_de_lift_squares_to_minus_one`
- PASS `weyl_lemmas.g_de_maps_d_to_e_dc_to_ec_u_to_nu_uc_to_nuc`
- PASS `weyl_lemmas.g_de_maps_down_sector_onto_charged_lepton_sector_both_chiralities`
- PASS `weyl_lemmas.g_de_moves_45_BL_and_210_15_1_1_controls`
- PASS `weyl_lemmas.g_de_spinor_lift_covariant_exact`
- PASS `weyl_lemmas.sigma_and_conjugate_bilinears_touch_only_neutral_states`
- PASS `weyl_lemmas.sigma_std_16x16_bilinear_is_nuc_nuc_32i_only`
- PASS `weyl_lemmas.sigma_std_16x16bar_bilinear_zero`
- PASS `weyl_lemmas.torus_element_reduces_real_doublet_to_e8_fixing_p`
- PASS `weyl_lemmas.vev_table_matches_research_c2_exactly`
- PASS `xparity_120.F_F_120_allowed_only_for_X_minus_2_Z17_15`
- PASS `xparity_120.T_linear_covariants_of_the_vevs_vanish_exactly`
- PASS `xparity_120.Z17_equals_X_mod_17_for_T`
- PASS `xparity_120.minimal_odd_sigma_degree_is_12`
- PASS `xparity_120.p_only_O15_map_vanishes_on_10_doublets_iota15_nonzero`
- PASS `xparity_120.p_only_operator_controls_nonzero`
- PASS `xparity_120.p_only_operators_zero_122_to_1522_matrix_elements`
- PASS `xparity_120.research_xparity_sets_reproduced`
- PASS `xparity_120.sigma_number_even_through_degree_11`
- PASS `xparity_120.sigma_numbers_pinned_degrees_4_to_8`
- PASS `xparity_120.sm_cartan_control_p_A_W_annihilated`
- PASS `xparity_120.three_forms_have_no_SM_Cartan_neutral_vector`
