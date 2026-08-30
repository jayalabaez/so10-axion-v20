# V47 G1 closure and exact frontier

Status: V47_G1_MICROSCOPIC_GAUGE_AND_GLOBAL_ANOMALY_CONSISTENCY_CLOSED__COUPLED_NEUTRAL_210_SOURCE_BRANCH_FULL_PHYSICAL_RANK__FOUR_SPINOR_MIXED_KK_ZERO_MODE_THEOREM_PROVED__REGULATOR_VACUUM_THRESHOLDS_AND_PHENOMENOLOGY_OPEN__ONE_OF_EIGHT_FULL_GATES_CLOSED

## Scientific verdict

V47 closes G1: the exact ordinary-Spin Pati-Salam quotient AHSS has no degree-five torsion, the Spin10/P relative degree-six group vanishes, and the already-certified local/free and residual-Z6 anomaly data are compatible. It also proves a coupled full-rank source branch and the exact four-spinor mixed KK zero theorem.  The brane regulator, stabilized vacuum, thresholds and physical reconstruction remain open, so the theory is not complete.

**Full gates closed: 1 / 8 — G1 only.**

This is a mathematical consistency advance, not empirical validation and not a
complete theory.

## Why G1 closes

For `P=(SU4 x SU2L x SU2R)/Z2_diag` with an independent spacetime Spin
structure, the exact low-degree AHSS gives

`Omega5^Spin(BP)=Omega5^Spin(B(P x U1F))=0`.

The non-liftable candidate `x Sq1(x)` and the mixed `x c1(U1F)` direction are
killed by explicit `d2` differentials.  The free degree-six map from the
Pati--Salam endpoint to `Spin(10) x U1F` hits all three bulk generators
primitively, so the standard interval relative group is also zero.  Together
with the exact wall-local anomaly cancellation, quantized parity levels and
residual-Z6 pullback, the gauge/global-anomaly obstruction vanishes.

The absolute APS determinant phase is not assigned a number.  It depends on a
regulator and local counterterm convention, but its gauge-invariant value is
not an anomaly and does not reopen G1.

## Coupled source branch

After shifting the neutral singlet coordinate, all relevant neutral
renormalizable cross couplings can be retained.  At `STheta=0`, the V46 SU5
branch remains exact and `F_STheta` fixes `ThetaPlus ThetaMinus`.  On the gauge
quotient the physical Hessian has block form

`[[H,0,c],[0,0,a],[cT,a,d]]`,

with determinant `-a^2 det(H)`.  The coupled sector has 465 chiral components,
22 eaten directions and 443 generic massive physical components, with no
physical zero.  This closes the source-superpotential existence subproblem,
not full G3: Kahler/radion stabilization and branch selection remain absent.

## Four-spinor mixed KK theorem

The exact characteristic is

`K(m)=(-mS+BF)E+(G+mBS)(1-E)`, `C(m)=det K(m)`,

and `D(z)=C(sqrt(z))C(-sqrt(z))`.  At zero mass,

`det K(0)=det G_O det(B_EE) det F_E`.

Therefore `n_zero=n_even-rank(B_EE)`.  Both finite nonzero Theta blocks make
`B_EE` full rank in all 16 component directions; the allowed Sigma entries are
even--odd on the SU5 singlet and cannot restore a zero.  A Hermitian extension
has real signed eigenvalues and no supersymmetric tachyon.  Large finite Sigma
mixing can nevertheless produce a parametrically light pole, so the regulator
and complete threshold spectrum remain part of G6.

## V47 exact results

| ID | Result | Exact statement |
|---|---|---|
| E15 | ordinary-Spin quotient bordism | Every total-degree-five AHSS term dies for BP and B(PxU1F), including non-liftable bundles. |
| E16 | relative interval anomaly | The degree-six map is integrally surjective and the standard interval relative group is zero. |
| E17 | G1 promoted | Local polynomials, quantized parity levels, quotient torsion, the relative obstruction and the residual Z6 pullback all cancel. |
| E18 | coupled neutral source branch | The unavoidable neutral cross couplings preserve an exact F/D-flat branch with 443 generic massive physical chirals and no physical zero. |
| E19 | source Hessian cofactor theorem | On the gauge quotient, det(Mphys)=-a^2 det(H), independent of the cross vector and singlet diagonal entry. |
| E20 | four-spinor mixed KK theorem | The zero-mode kernel is exactly ker(B_EE); both finite nonzero Theta blocks remove all exact zero modes for arbitrary finite Sigma mixing. |
| E21 | finite strong-mixing warning | Large finite Sigma mixing need not create a zero but can create a parametrically light pole, so thresholds require the full characteristic. |
| E22 | source-route comparison | 45+54 has a lower source index and an exact SU5 branch, but 210 remains selected because only it has a replayed full physical Hessian. |

## Research stages

| Stage | Status | Passed | Missing |
|---|---|---|---|
| S0 | OPEN_WITH_COUPLED_SOURCE_BRANCH_AND_RANK_CERTIFIED | all relevant neutral renormalizable source terms included; exact coupled branch; 443 massive physical chirals | resolved boundary regulator, complete Kahler action, radion stabilization and dynamical branch selection |
| S1 | CLOSED | local polynomials, free parity lattice, exact quotient Omega5, relative Omega6 and residual Z6 pullback | none for gauge/global-anomaly consistency in the declared ordinary-Spin boundary-condition model |
| S2 | OPEN_WITH_FOUR_SPINOR_ZERO_THEOREM_CERTIFIED | exact C(m), D(z), ker(B_EE) theorem and no-zero/no-SUSY-tachyon result for finite Hermitian B | bare-to-renormalized brane map, induced kinetic/derivative terms, numerical roots and thresholds |
| S3 | OPEN_WITH_OPERATOR_FRONTIER_RETAINED | faithful Z3F and matter parity survive; prior degree-20 orientation frontier retained | 210-completed operator ring, full-tower Wilson matching and decay-rate limits |
| S4 | OPEN | no phenomenological claim imported from a microscopic subcheck | unification, RG spectrum, flavor, neutrinos, light Higgs, SUSY breaking, dark sector and cosmology |

## G1--G8 ledger

| Gate | Status | Advance | Remaining blocker |
|---|---|---|---|
| G1 | closed | Exact ordinary-Spin AHSS and relative-pair calculations remove the non-liftable, mixed-U1F and residual-Z6 anomaly obstructions. | none within the declared model; gauging the orbifold reflection would define a different equivariant/Pin problem |
| G2 | open | All relevant renormalizable neutral cross terms and both Sigma-spinor portals are now included algebraically and in the idealized boundary matrix. | The resolved-brane map, induced boundary operators, higher-dimensional selector/naturalness structure and Wilson matching are absent. |
| G3 | open | An exact coupled F/D-flat neutral-210 branch has 443 generic massive physical chirals and an executable full-rank Hessian theorem. | The Kahler/radion/soft potential, global vacuum selection and controlled 5D branch are not solved. |
| G4 | open | No inconsistent soft sector was imported. | Radion stabilization, SUSY breaking, mu/Bmu, EWSB and the complete scalar vacuum are absent. |
| G5 | open | The excluded V39 dark benchmark remains removed. | No dark-sector Lagrangian, relic calculation or cosmological history is specified. |
| G6 | open | The exact four-spinor characteristic, zero-mode theorem and Hermitian no-tachyon result include both Theta and Sigma mixings. | Regulator matching, boundary kinetics, numerical thresholds, 5D unification, RG running and the pole spectrum are missing. |
| G7 | open | The anomaly-free faithful Z3F and matter parity coexist with the retained high-degree orientation frontier. | The 210-completed operator ring, shifted-tower Wilson coefficients and proton/multinucleon rates are absent. |
| G8 | open | The PS-wall Yukawa architecture remains compatible with the retained route. | There is no neutrino completion, three-family fit, uncertainty propagation or withheld prediction. |

## Next terminal calculations

1. Resolve the source wall and derive the matrix-valued bare-to-renormalized B_R map, including induced kinetic, derivative and wrong-chirality operators.
2. Choose a controlled 5D parameter point and compute every root of the complete four-spinor/gauge/source characteristic, thresholds, NDA cutoff and unification fit.
3. Specify the Kahler, radion and SUSY-breaking sectors and prove global vacuum selection, EWSB and absence of dangerous scalar directions.
4. Recompute the 210-completed invariant/operator ring, full-tower Wilson coefficients and proton or multinucleon decay likelihoods.
5. Build and fit the light-Higgs, flavor, neutrino, dark-sector and cosmological completion with uncertainty propagation and withheld predictions.

Core SHA-256: 916c3f3f90aacb691a8232fd58c8ddc2ae422be2f86706c7f91af05fcfe8fbe4
