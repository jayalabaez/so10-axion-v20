# V89 C8, localized quantum and compact-globalization audit

Status: `V89_C8_LOCALIZED_BV_COMPACT_GLOBALIZATION_AUDIT__V70_V87_V88_CORES_BOUND__C8_EXPONENT_PROJECTIONS_ENUMERATED_FOR_FROZEN_V88_NONC8_LIFTS__EVERY_SURVIVING_EXPONENT_IS_EVEN__NO_PRIMITIVE_K_IN_C8_FACTOR_PROJECTION_FOR_FROZEN_V88_NONC8_LIFTS__INDEPENDENT_EXTERNAL_C8_KERNEL_PARITY_COMPATIBLE__NEW_Z00_SPLIT_U5_LOCAL_PHASE_CANDIDATE_EXACT__WALL_QUOTIENT_OPEN__COMPONENT_CHARACTERS_AND_PLACEMENT_NEW__CONTINUOUS_SP3_CARTAN_U1_GAUGING_REJECTED_BY_GRAVITY_COUNT_AND_THREE_EXACT_GS_EQUATIONS__CHARGED_FERMION_GAUGE_LOG_TWIST_COMPONENT_ZERO__FULL_CHARACTER_INPUTS_UNDERSPECIFIED_AND_COMMON_BV_REGULATOR_OPEN__COMPACT_TORSOR_BLOWUPS_GLOBAL_PROJECTIVE_AND_CREPANT__GENERIC_COMPACT_SMOOTH_MEMBER_EXISTS__NO_FROZEN_MEMBER_OR_REES_SATURATION__NATURAL_ORDER4_ROOT_REJECTED__LITERAL_GLOBAL_ORDER4_ACTION_AND_DIAGONAL_ORBIBUNDLE_OPEN__NO_ACCEPTED_PARENT__G1_TO_G8_OPEN`

Core: `afece33b67225eb97b4813a643914fe979a744cea5d233e4886c80be59fbf3e7`

## Exact result

With the non-C8 parts of the V88 lifts frozen, the order-eight exponent projection has a complete finite answer.  The translation equations leave `[[0, 0], [0, 4], [2, 2], [2, 6], [4, 0], [4, 4], [6, 2], [6, 6]]`.  Restoring the V70 projectors reduces these to `[[2, 2], [2, 6], [6, 2], [6, 6]]`, while the rotation exponent is `0` or `4`.  All eight necessary exponent triples use only even powers of `k`; the C8-factor projection of the selected full cocycle is `[0, 2, 4, 6]`, namely `<k^2> = C4`.  The other triples are not promoted to fully correlated Gammahat cocycles.  Under the frozen V88 lift, no element projects to primitive `k` in the C8 factor.

A primitive `k` can nevertheless be adjoined as an independent internal C8 generator.  Every assigned central character obeys `c+q8=0 mod 2`, and the audited bulk Spin(11) representations descend through `(z,k^4)`.  For localized U5 fields this proves kernel-parity compatibility only: the global wall quotient and its induced representations are not frozen.  This is not a quantum gauging or a geometric lift.

V89 also supplies one explicit new local-phase choice: put three split local U5 families (10_-1+5bar_3+1_-5), X, Xbar and 5_0+5bar_4 at z00.  The `10` and `5bar+1` use independent local U5 intrinsic characters; this is not one scalar character on an irreducible Spin(11) `16`, nor a completed representation of an unfrozen global wall quotient.  With `zeta=exp(i*pi/4)`, every displayed gauge-times-intrinsic phase is one, every fourth power matches the assigned center parity, and every assigned character annihilates `(z,k^4)`.  The `X,Xbar` VEVs are invariant under this orbifold isotropy but break primitive `k` to the gauge-diagonal subgroup.  These action data were not fixed by V70 or V88.  Moving the same ordinary-anomaly-free family content from `z00` to `z11` only demonstrates that placement is not frozen; it does not compute a nonzero difference of eta characters.  A common BV regulator and Dai--Freed/WCS trivialization remain absent.

The connected six-dimensional Spin(11) polynomial is exactly `-1/16 (trR2-trF2)(trR2+2trF2)`.  For the signed Sp(3) Cartan, the charged-hyper dimension-weighted moments are `(q^2,q^4)=(88,352)`.  Gauging adds a vector, changing `(H,V,T)` to `[299, 56, 1]` and leaving an irreducible gravitational mismatch of `-1`; one added neutral hyper repairs only that count.  Independently, the Abelian GS equations force `c=['-92/9', '26/9']` from the first two conditions, giving `c^2=-4784/81` instead of `352/3`.  Thus continuous `U(1)_T` cannot be gauged with the current spectrum and lattice.  This does not reject the finite subgroup.  The charged-fermion gauge/log-twist wall component vanishes, while the gravity/tensor/neutral/normal-bundle Gysin terms remain absent.

On the geometry side, the centers `C_+`, `C_-` and the weak transform of `D0` globalize on the compact `P(1,1,2)` torsor.  Their discrepancies are `[0, 0, 0]`, and the strict transform remains anticanonical.  The exact F4 section counts are `{'h0_S_plus_12F': 22, 'h0_2S_plus_12F': 27, 'h0_3S_plus_12F': 28}`.  The moving directions cover the locus `(U,V) != (0,0)`; at the weighted singular section the fixed term `F0=W^2` is nonzero.  Thus the full span is basepoint-free away from `S`, and Bertini plus the V88 charts over `S` proves that a nonempty Zariski-open family of smooth compact resolved members exists.  No explicit member or Rees/Jacobian saturation is frozen.

The manifest deck action is only `W -> -W`.  Its natural proposed order-four root `(U,V,W)->(V,-U,iW)` fails because `W^2` changes sign while `(U^2-V^2)^2` does not, and the boundary quartic is not an eigenvector.  Other automorphisms are not classified.  A literal global order-four action and diagonal resolved Gammahat orbibundle remain open.

This is real progress, but it is not a completed parent action: all eight gates remain open.

## Gates

- G1: OPEN: V89 constructs external-C8 kernel parity plus bulk descent and a new z00 split-U5 phase candidate, and globalizes the compact crepant blowups with generic smooth existence; localized wall-group descent, a primitive geometric C8 and a quantum same-action parent remain absent.
- G2: OPEN: the V88 rank-one light Higgs pair is retained, but the external C8/compensator sector has no accepted SUSY-breaking action, soft spectrum or complete thresholds.
- G3: OPEN: one z00 split-U5 isotropy candidate is explicit, but its component characters and placement are new, its rank VEVs break primitive C8, and the full fixed-wall/neutral sector plus one common BV/regulator complex are not constructed.
- G4: OPEN: the charged-fermion gauge/log-twist component vanishes, but placement, wall-group, gravity/tensor/neutral, normal-bundle and regulator inputs for the full character are not frozen, and no Dai-Freed/WCS trivialization exists.
- G5: OPEN: charge-conjugate regulator representations are algebraically available, but no common elliptic gauge-fixed KK complex, stratified boundary conditions, Pfaffian orientation or determinant exists.
- G6: OPEN: no accepted spectrum from a same-action quantum parent has been propagated through two-loop running and compact thresholds.
- G7: OPEN: the signed C8 selector survives as an external classical candidate, but its U1_8/GM origin, nonzero compensator mass, decay/Higgs/proton certificate, cosmology and likelihood remain absent.
- G8: OPEN: a global crepant resolution and generic smooth compact member now exist, but no explicit frozen member/Rees saturation, literal order-four action, diagonal orbibundle, anomaly theory or UV-complete same action exists.

## Open obligations

- choose and derive, from one action, either an external U1_8/C8 gauge sector or a different geometric primitive-C8 compactification
- if a continuous parent is retained, add charged matter and/or tensor/GS data that solve all Abelian six-dimensional anomaly equations
- freeze the localized placement and every intrinsic phase, including neutral, tensor, gravity, ghost, antifield and regulator sectors
- construct one elliptic BV/BRST/Pauli-Villars complex and compute every fixed-wall logarithmic twist/Gysin contribution
- evaluate the full Dai-Freed eta character and construct a quantized differential GS/WCS trivialization
- freeze explicit rational compact coefficients and compute the resolved Rees/Jacobian saturation
- construct or globally rule out an equivariant order-four action and glue the diagonal Gammahat orbibundle
- construct the U1_8 breaking, charge-four GM spurion, compensator mass/decay and proton-safe Higgs sector
- only after a same-action quantum parent exists, compute thresholds, unification, cosmology and likelihood

## Primary sources

- [vonGersdorff2006](https://arxiv.org/abs/hep-th/0612212): localized six-dimensional orbifold anomalies depend on the full fixed-point twist
- [Hsieh2018](https://arxiv.org/abs/1808.02881): Dai-Freed classification of four-dimensional discrete fermion anomalies and symmetry extensions
- [MonnierMoore2018](https://arxiv.org/abs/1808.01334): global six-dimensional Green-Schwarz/Wu-Chern-Simons quantization and residual finite-group anomalies
- [GrootNibbelinkHillenbach2006](https://arxiv.org/abs/hep-th/0602155): orbifold-compatible supersymmetric bulk and fixed-point quantum structures
- [BraunMorrison2014](https://arxiv.org/abs/1401.7844): genus-one fibrations, Tate-Shafarevich data and F-theory without a section
- [Park2011](https://arxiv.org/abs/1111.2351): six-dimensional nonabelian and abelian anomaly/Green-Schwarz equations
- [WittenYonekura2019](https://arxiv.org/abs/1909.08775): nonperturbative anomaly inflow and eta-invariant formulation
