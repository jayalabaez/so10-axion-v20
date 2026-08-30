# V48 G2 frontier integration audit

Status: `V48_G2_MAJOR_REGULATOR_AND_WILSON_ADVANCE__EXACT_POSITIVE_HYPERMULTIPLET_COLLAR_MAP_AND_POLE_SAFE_CHARACTERISTIC__SCOPED_SOURCE_PORTAL_AND_PS_SCHUR_KERNEL_REPLAYED__FULL_RETAINED_ACTION_DOMAIN_AND_COMPONENT_MATCHING_INCOMPLETE__G2_FAIL_CLOSED__ONE_OF_EIGHT_FULL_GATES_CLOSED`

## Scientific verdict

V48 solves the fixed-background H/Hc regulator subproblem and derives an exact restricted full-tower source-dependent Schur kernel.  It does not close G2 because the retained action, positive generalized domain and component Wilson kernel are not yet the same complete object. G1 remains the only closed full gate.

**Full gates closed: 1 / 8 — G1 only.  G2 remains open.**

This is a real regulator and matching advance, not a complete theory, UV
completion or empirical validation.

## What V48 genuinely solved

For a Hermitian Nambu source matrix `A`, a finite square collar gives

`delta=m epsilon`, `X=delta(A-delta I)`,

`D=cosh(sqrt X)`, `C=(A-delta I) sinhc(sqrt X)`,

and, where `D` is invertible,

`B_epsilon(m)=D^-1 C`.

The exact derivative expansion begins

`B_epsilon=A-m epsilon(I+A^2/3)+...`,

so the induced H/Hc boundary kinetic matrix
`Z_b=epsilon(I+A^2/3)` is strictly positive.  The undivided characteristic

`K_reg=(CF-mDS)E+(mCS+DG)O`

retains collar poles and tends to the V47 characteristic in the thin-wall
limit.

For both host boundary data, the corrected tree response is

`K_reg=CR+DQ`, `N_reg=CP+DT`,

`G_00=(K_reg+N_reg V_0)^-1 N_reg`.

This is the right Schur structure.  The executable representative contains all
four H/Hc Higgs bilinears, sees all four Theta/Sigma projectors, replays three
regulated poles and one residue, and has exponential Euclidean locality.

## Frozen G2 contract

A fixed-order tree-level Wilsonian source/portal boundary EFT in one declared regulator scheme, with a complete retained-order local action, an action-derived positive self-adjoint domain, and a component-resolved full-tower kernel for that same action.

`G2_closed iff C1 through C7 all pass for the same retained action`.

It does not demand an all-order UV prediction, and it does not absorb the
vacuum, numerical-threshold, B/L-rate or flavor-fit work owned by G3, G6, G7
and G8.

## C1--C7 decision

| Clause | Requirement | Status | Landed | Remaining blocker |
|---|---|---|---|---|
| C1 | fixed_order_action_completeness | fail | The complete renormalizable neutral source superpotential, four leading source-spinor portals, twelve next two-bulk-trace contractions, the corrected nineteen PS Yukawa structures, FI data and boundary gauge terms are catalogued. | The allowed PS mu_H H H term, pure-source quartics at the same 1/Lambda order, source-collar Hc/mixed portals and the normal-derivative/EOM-reduced basis are not all included in one retained-order action. |
| C2 | explicit_regulator | pass | A finite square H/Hc collar of width epsilon is an explicit regulator and gives the exact undivided transfer matrices C,D and the map B_epsilon=D^-1 C. | none for the fixed-background H/Hc regulator subproblem |
| C3 | variational_domain_and_self_adjointness | partial | The canonical H/Hc collar with Hermitian Nambu source matrix is J-unitary and self-adjoint on its parity/continuity domain. | The declared wall kinetic, normal-derivative and source-field terms have not been varied together to derive one complete self-adjoint generalized domain. |
| C4 | positive_full_kinetic_form | partial | The H/Hc slab induces Z_b=epsilon(I+A^2/3)>0 and the declared wall metrics can be chosen positive. | The full source, Zhat, Kähler-mixing and derivative Schur complements are not assembled.  The proposed source-collar y-stiffness changes Kähler normalization but does not prove a gapped transverse source spectrum. |
| C5 | counterterm_and_matching_scheme | partial | The square-collar matching scale, minimal quadratic renormalization conditions and NDA domain are explicit. | There is no complete retained-order counterterm catalogue or profile-rematching calculation for the source, PS kinetic and normal-derivative sectors. |
| C6 | selector_and_naturalness_policy | partial | V48 correctly rejects an all-order finite selector, treats allowed coefficients as matching data and declares a sub-cutoff NDA expansion. | Because the retained-order basis is incomplete, the claim that every allowed coefficient at that order is admitted is not yet true. |
| C7 | action_to_full_tower_Wilson_matching | partial | The undivided matrices K_reg=CR+DQ and N_reg=CP+DT give the exact restricted tree kernel G_00=(K_reg+N_reg V_0)^-1 N_reg; poles, a residue, locality and off-shell decoupling replay numerically. | The kernel omits the declared wall Kähler/derivative operators and is represented by an eight-coordinate witness rather than a complete component-Clebsch current map for the same retained action. |

Only `C2` passes completely.  The
conjunction is therefore false and G2 cannot be promoted.

## Exact defects preventing closure

| ID | Defect | Why it matters |
|---|---|---|
| D1 | missing_PS_Higgs_mass | After the exact Z4R selector was withdrawn, the local PS invariant mu_H epsilon_L epsilon_R H H is allowed and must be declared even though the small-mu mechanism belongs to G4. |
| D2 | same_order_pure_source_quartics | Pure-source chiral quartics are O(1/Lambda), the same Wilsonian order as the retained degree-four portals.  G3 owns their vacuum solution, but G2 must still parameterize their invariant coefficient space. |
| D3 | source_collar_wrong_chirality_basis | A finite collar makes Hc nonzero.  The four conjugate HcHc source portals and source-dependent HcH/mixed-Kähler terms require inclusion or a proved symmetric-profile/Dirichlet power-counting reduction. |
| D4 | PS_normal_derivative_basis | Gauge-covariant normal-derivative operators, including Q_i nabla5(HLFc) and Qc_i nabla5(HRAc), are not explicitly reduced by IBP/EOM/field redefinitions or propagated into the boundary pencil. |
| D5 | source_profile_spectrum_unproved | The rho epsilon^2 |D_y X|^2 D-term is a mode-dependent Kähler metric, not by itself a supersymmetric transverse mass.  A constrained single profile, finite deconstruction or proper first-order 5D source multiplets are needed. |
| D6 | same_action_positivity_and_counterterms | The source, boundary Kähler, Zhat, derivative and counterterm blocks must be assembled in one positive generalized norm and rematched in the chosen scheme. |
| D7 | component_resolved_matching | The exact Schur structure is established, but all physical PS Clebsches, projectors and currents for the complete retained operator set have not been published. |

The source-collar problem is especially important.  A positive
`d4theta epsilon^2 |D_y X|^2` term is a Kähler normalization, not a proof that
nonconstant source profiles are gapped.  The source must instead be a
constrained single profile, a finite deconstruction, or a proper first-order
5D multiplet before its spectrum and norm can support G2.

## V48 exact results

| ID | Result | Exact statement |
|---|---|---|
| E23 | exact finite-collar map | For delta=m epsilon and X=delta(A-delta I), D=cosh(sqrt X), C=(A-delta I)sinhc(sqrt X), and B_epsilon=D^-1 C wherever D is invertible. |
| E24 | positive induced kinetic term | B_epsilon=A-m epsilon(I+A^2/3)+... and Z_b=epsilon(I+A^2/3) is strictly positive. |
| E25 | pole-safe resolved characteristic | K_reg=(CF-mDS)E+(mCS+DG)O retains every collar state, tends to V47 in the thin-wall limit and preserves zero nullity at the certificate point. |
| E26 | scoped operator census | The renormalizable source action has 16 raw structures including W0, the next two-bulk-trace portal sector has 12 SO(10) contractions, and the corrected PS Yukawa census has 19 coefficients before the missing Higgs mass term is added. |
| E27 | restricted exact full-tower Schur kernel | For the encoded tree action, K_reg=CR+DQ, N_reg=CP+DT and G_00=(K_reg+N_reg V_0)^-1 N_reg.  The witness sees every Theta/Sigma projector. |
| E28 | regulated pole and locality witness | Three representative positive signed roots, the first-pole residue, exponential Euclidean locality and off-shell large-source decoupling replay. |
| E29 | G2 fail-closed decision | Only C2 passes completely.  The exact collar and Schur formula are genuine advances, but the same-action C1--C7 conjunction is false, so G2 is not promoted. |

## Research stages

| Stage | Status | Passed | Missing |
|---|---|---|---|
| S0 | OPEN_WITH_COUPLED_SOURCE_RANK_RETAINED | exact coupled neutral-210 branch and 443 generic massive physical source chirals | spectrally healthy source-field regulator, complete Kähler/FI functional, radion dynamics and branch selection |
| S1 | CLOSED | V47 local, quotient, relative and residual-discrete gauge/global anomaly certificate | none within the declared ordinary-Spin boundary-condition model |
| S2 | OPEN_WITH_EXACT_HYPERMULTIPLET_COLLAR | exact B_epsilon, positive induced H/Hc norm, pole-safe K_reg and representative roots/residue | one complete action-derived generalized domain, healthy source realization, full pole tower and thresholds |
| S3 | OPEN_WITH_RESTRICTED_SCHUR_KERNEL | leading source portals, corrected PS H/Hc Yukawas and exact restricted full-tower kernel | complete retained-order operator basis, component Clebsches, B/L ring, physical Wilson coefficients and rates |
| S4 | OPEN | no empirical claim imported from the exact microscopic subchecks | unification, RG spectrum, flavor, neutrinos, light Higgs, SUSY breaking, dark sector and cosmology |

## G1--G8 ledger

| Gate | Status | Advance | Remaining blocker |
|---|---|---|---|
| G1 | closed | V47 exact ordinary-Spin quotient and relative anomaly calculations remain intact. | none within the declared ordinary-Spin model |
| G2 | open | An explicit H/Hc square collar gives exact B_epsilon and K_reg; the leading source/portal census, corrected PS traces and a restricted tree full-tower Schur kernel are executable. | The source realization is not spectrally certified, the retained-order action omits allowed mu_H/source-quartic/Hc/normal-derivative terms, and all declared kinetic terms are not matched in one component-resolved positive kernel. |
| G3 | open | The exact coupled F/D-flat branch and generic physical-rank theorem remain valid at renormalizable order. | Pure-source higher operators, FI/Kähler/radion/soft terms, global vacuum selection and the controlled 5D branch are unsolved. |
| G4 | open | The missing PS mu_H term is now identified as an allowed input rather than silently forbidden. | The mu/Bmu mechanism, SUSY breaking, radion stabilization, EWSB and complete scalar vacuum are absent. |
| G5 | open | No excluded dark benchmark is reintroduced. | No dark-sector Lagrangian, relic calculation or cosmological history is specified. |
| G6 | open | The regulator map is exact and three representative regulated poles plus one residue replay. | A complete controlled parameter point, every pole, thresholds, NDA cutoff, unification and RG running are absent. |
| G7 | open | The source-dependent restricted Schur kernel supplies the correct structural starting point for full-tower matching. | The 210-completed B/L ring, component Wilson coefficients, dressing/running and proton or multinucleon rates are absent. |
| G8 | open | The PS census now includes complementary Hc Higgs cubics and the allowed family/bulk Kähler mixings. | There is no complete component Clebsch map, neutrino completion, family fit, uncertainty propagation or withheld prediction. |

## Smallest next G2 closure patch

1. Replace the dynamical source collar by a constrained single 4D profile, finite deconstruction, or proper first-order 5D source multiplets and prove that no extra light source tower appears.
2. Freeze the full retained-order source/PS action, adding mu_H H H, an abstract complete invariant basis for pure-source quartics, the Hc/mixed terms and an explicit normal-derivative IBP/EOM reduction.
3. Insert every retained Kähler, derivative and counterterm block into generalized K_reg,N_reg; prove self-adjointness and positivity of the complete norm.
4. Publish the component Clebsch/projector current map and verify that its poles, residues and low-energy coefficients reproduce the complete retained action.

The neutral-210 route remains viable.  It should be continued, but the result
must stay at **1/8 closed gates** until the repaired source regulator and the
same-action component kernel pass together.

## Primary sources

- [Marti--Pomarol: 5D supersymmetry in N=1 superfields](https://arxiv.org/abs/hep-th/0106256)
- [Hebecker: gauge-covariant brane operators](https://arxiv.org/abs/hep-ph/0112230)
- [von Gersdorff et al.: interval boundary action principle](https://arxiv.org/abs/hep-th/0411133)
- [del Aguila--Perez-Victoria--Santiago: thin-defect EFT](https://arxiv.org/abs/hep-ph/0601222)
- [Nath--Syed: SO(10) spinor contraction channels](https://arxiv.org/abs/hep-th/0109116)
- [Barcelo--Mitra--Moreau: finite-width brane/KK limit ordering](https://arxiv.org/abs/1408.1852)

Core SHA-256: `011ed9c18b48a0bed359e998cde1eb3d04525294f29e03cc8e950e4e7b2c8950`
