# V88 B-neutral Gammahat and Cartan-anomaly correction audit

Status: `V88_B_NEUTRAL_GAMMAHAT_CARTAN_ANOMALY_CORRECTION_AUDIT__V70_V84_V85_V86_V87_CORES_BOUND__REDUCED_FLAVOR_CENTRALIZER_SP2_TIMES_SP1_EXACT__CONTINUOUS_CARTAN_CENTRALIZER_U2_TIMES_SP1_EXACT__SELECTED_UVRS_ZERO_GAMMAHAT_COCYCLE_EXACT_MOD_KROT_KSPIN__NO_PURE_SPIN11_CENTER__ALL_FOUR_STRATA_AND_ALL_V70_A_B_C_PROJECTORS_RESTORED_FOR_SMOOTH_CHARGED_HYPERS__V87_DISCRETE_ZERO_MODE_RESIDUES_RETAINED__V87_TENSOR_DIVIDED_BY_FOUR_NOT_A_CONTINUOUS_6D_GS_FACTORIZATION__ONE_MINIMAL_INTEGER_LIFT_CHANGES_TRF_AND_TRF3__AW4_UNIQUE_ONLY_IN_RESTRICTED_SW_SUBRING__DISPLAYED_WITNESS_NEEDS_NO_AW4_TERM__T2_COHOMOLOGICAL_COMPONENT_HAS_FOUR_CANDIDATE_LABELS__WCS_ADMISSIBILITY_OPEN__RELATIVE_PROJECTIVE_CREPANT_BISECTION_RESOLUTION_OVER_S_AND_CENTER_COSET_EXACT__COMPACT_GLOBAL_GEOMETRY_OPEN__V85_MIXED_ACTION_CBAR45C_RETRACTION_BOUND__C8_NEUTRAL_DRIVER_B0_PARITY_AND_VECTORLIKE_5PAIR_RESIDUE_SCREEN_EXACT__C8_FULL_DAIFREED_AND_GM_SPURION_OPEN__FULL_SIGNED_6D_ANOMALY_WCS_DAIFREED_AND_LOCALIZED_REGULATOR_OPEN__OPERATOR_CLOSURE_COMPACT_RESOLUTION_AND_SAME_ACTION_PARENT_OPEN__G1_TO_G8_OPEN`

Core: `d8172ac25c3336ae622b250cf29b8a48089be4f15455c0163562a86a49b55033`

## Exact result

The copy-dependent involution `H_AC=diag(-,+,-,-,+,-)` reduces the identical-hyper flavor group from `Sp(3)` to `Sp(2)_AC x Sp(1)_B`. Its signed continuous interpolation has charges `[2, 0, 2, -2, 0, -2]` and centralizer `U(2)_AC x Sp(1)_B`.

For the selected lift class `(u,v,r,s)=(0,0,0,0)`, `A=(qhat,A3,1)`, `U=(what,H_AC,j)` and `V=(what,H_AC,j)`. The four space-group defects are `{'A4': [1, 1, 1, 1, 1, 0], 'UVUinvVinv': [0, 0, 0, 0, 0, 0], 'AUAinvVinv': [0, 0, 0, 0, 0, 0], 'AVAinvU': [0, 1, 0, 0, 0, 1]}` and all lie in `K_F=<krot,kspin>`. The kernel contains no pure Spin(11) center. Every A/B/C projector at all four strata now reproduces V70 exactly.

The relative bisection model over the gauge divisor is resolved by blowing up the two disjoint curves `C_+` and `C_-` and then the residual weak transform of `D0`. Both discrepancies vanish. The final chart Jacobian bases are unit ideals, while the bisection intersects affine-D6 node `alpha3` with degree `2`. Its inverse-Cartan column differs integrally from V86 node one, so both represent the same nontrivial Spin(11) center coset and geometrically realize `j^2=z`. This is a relative certificate over `S`, not compact-global smoothness.

V88 also corrects V87's anomaly scope. The displayed discrete zero-mode residues still vanish, but dividing their integer tensor by four does **not** construct a continuous six-dimensional U(1) anomaly polynomial or quantized GS/WCS coefficient. One explicitly scoped minimal integer lift of the four-dimensional table is `{'A3': 12, 'A2': 16, 'FY6_squared': 432, 'FX_squared': 672, 'TrF': 60, 'TrF_cubed': 96, 'F_squared_Y6': 0, 'F_squared_X': 0, 'FY6X': 48}`; it is not a canonical continuous-U(1) anomaly tensor. Inside the stated restricted Stiefel--Whitney polynomial subring, the ordinary degree-five reduction leaves `a*w4(V)`, and the displayed witness needs no such term. The `t^2` cohomological component has `4` candidate lattice labels before WCS admissibility constraints. The full characteristic ring, bordism character, bulk anomaly and fixed-wall Dai--Freed computation are absent.

The separate signed-C8 scout promotes `B0` to charge four. It forbids odd driver powers only when their coefficients are C8-neutral and retains the required even mass term; the proposed charge-four GM spurion can compensate an odd power, so no unconditional all-order selector is claimed. A proposed localized gauge-vectorlike `5_0 + 5bar_4` changes the displayed anomaly tensor to `{'A3': 64, 'A2': 80, 'FY6_squared': 2208, 'FX_squared': 2208, 'TrF': 312, 'TrF_cubed': 7824, 'F_squared_Y6': 96, 'F_squared_X': 544, 'FY6X': 192}`, which is zero modulo eight componentwise. Its mass operator is allowed, not constructed. VEV-assisted Higgs mixing and decay portals depend on the unresolved R assignment. The full order-eight Gammahat lift, localized regulator, GM realization and simultaneous decay/Higgs/proton certificate are absent.

This removes the smooth charged-hyper projector blocker and solves the relative bisection singularities over `S`. It does not construct localized isotropy, the common regulator, full operator closure, compact-global geometry or a complete theory. All eight SUSY gates remain open.

## Gates

- G1: OPEN: the B-neutral smooth charged-hyper Gammahat cocycle, all V70 A/B/C projectors and the relative crepant bisection resolution over S are exact, but localized isotropy, quantum trivialization, compact-global completion and one accepted same-action parent remain absent.
- G2: OPEN: the rank-one light Higgs pair survives V88, but no accepted supersymmetry-breaking sector, soft spectrum or complete thresholds exist.
- G3: OPEN: the selected smooth-bulk lift is exact, while localized families, rank-VEV profiles, BV/regulator representations and the global line/endpoint form remain unconstructed.
- G4: OPEN: V88 corrects the continuous-GS overinterpretation and, within a restricted ordinary SW-polynomial subring, reduces the degree-five candidate to a*w4; the displayed witness needs no such term, but the full bordism character, six-dimensional polynomial, fixed-wall logarithmic twist terms and Dai-Freed/WCS trivialization are uncomputed.
- G5: OPEN: no common gauge-fixed KK determinant, regulator, Pfaffian orientation, self-dual polarization or defect cap/junction complex exists.
- G6: OPEN: no accepted V88 spectrum has been propagated through complete two-loop running and compact thresholds.
- G7: OPEN: V85 proves Cbar-45-C was a retracted mixed-action row and the C8 scout forbids odd B0 powers with neutral coefficients, but a charge-four spurion can compensate them; the GM realization, compensator decay/mixing/proton screen, all-order operator closure, cosmology and quantitative phenomenology remain unresolved.
- G8: OPEN: the resolution is only relative over S; compact geometry, a literal global order-four action, the diagonal orbifold bundle, anomaly theory and empirical likelihood are not one UV-complete action.

## Open obligations

- construct every localized-family, rank-VEV, ghost, antifield and regulator representation of the selected Gammahat lift
- compute the signed six-dimensional anomaly polynomial and every fixed-stratum logarithmic twist/Gysin term
- evaluate the full Dai-Freed eta character and construct any differential GS/WCS trivialization
- construct the full order-eight Gammahat action and test the C8 selector with localized isotropy and a common regulator
- construct the charge-four SUSY-breaking/GM spurion and prove compensator decay plus proton safety
- finish compact smoothness away from S, Cox saturation, the global order-four automorphism and diagonal resolved orbibundle
- derive SUSY breaking, thresholds, unification, cosmology and likelihood from the same action

## Primary sources

- [vonGersdorff2006](https://arxiv.org/abs/hep-th/0612212): six-dimensional orbifold projector and fixed-point anomaly dependence on the full internal twist
- [Hsieh2018](https://arxiv.org/abs/1808.02881): Dai-Freed discrete anomalies and distinction from continuous-U1 embedding conditions
- [MonnierMoore2018](https://arxiv.org/abs/1808.01334): global six-dimensional Green-Schwarz/Wu-Chern-Simons quantization and finite-group residual anomalies
