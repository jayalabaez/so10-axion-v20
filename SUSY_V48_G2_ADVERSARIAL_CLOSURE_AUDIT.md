# V48 adversarial G2 closure audit

Status: `V48_G2_ADVERSARIAL_REVIEW__RESOLVED_COLLAR_C2_PASS__PARITY_RESOLVED_OPERATOR_AND_COUNTERTERM_CENSUS_INCOMPLETE__REPRESENTATIVE_WILSON_IDENTITY_NOT_FULL_COMPONENT_MATCH__G2_OPEN`

## Verdict

**The combined V48 artifacts do not close G2.**  The resolved source collar is
a genuine C2 advance, and the operator artifact correctly adds the two
complementary-even-`Hc` PS cubics and improves the Green-function identity.
Only `1` of the
seven clauses now passes completely.  The retained-order parity-resolved
operator basis, full positive norm/counterterm scheme, and physical component
Wilson-current match are still incomplete.

This is not a demand for a fundamental UV completion.  The smallest legitimate
closure is a one-sided interval Wilsonian EFT, with no new propagating fields,
defined and matched through `O(Lambda^-1)` with a declared
`O(E^2/Lambda^2)` plus loop-order remainder.

## G2 scope

G2 is the Wilsonian microscopic boundary-action and source/portal-matching gate for the retained V47 interval architecture at a declared EFT order.

G2 should not absorb global vacuum selection (G3), the complete numerical KK
threshold/RG problem (G6), baryon-decay matching and likelihoods (G7), or the
flavour/neutrino fit (G8).  Its closure predicate is exactly

`G2_closed iff C1 and C2 and C3 and C4 and C5 and C6 and C7`.

## Mandatory clauses

| ID | Clause | V47 state | Closure pass |
|---|---|---|---|
| C1 | scope_power_counting_and_operator_completeness | partial | fail |
| C2 | regulator_or_fundamental_interval_prescription | open | fail |
| C3 | variational_domain_and_self_adjointness | conditional | fail |
| C4 | positive_kinetic_form | open | fail |
| C5 | counterterm_and_renormalization_scheme | open | fail |
| C6 | symmetry_and_naturalness_policy | partial | fail |
| C7 | action_to_Wilson_matching | open | fail |

### C1 — scope_power_counting_and_operator_completeness

Required: Declare Lambda, matching scale, loop order and an expansion order; enumerate an independent bulk/PS-wall/source-wall operator basis through that order modulo integration by parts, supersymmetric field redefinitions and leading equations of motion.

V47: The renormalizable source superpotential and four holomorphic spinor portals are included, but the boundary Kahler, gauge-kinetic, normal-derivative and wrong-chirality basis is not enumerated and no truncation error is declared.

### C2 — regulator_or_fundamental_interval_prescription

Required: Either retain a finite-width/deconstructed wall, or define a one-sided interval action with normalized boundary traces and a named thin-defect subtraction scheme; derive the renormalized boundary kernel from that action.

V47: V47 treats B as a finite renormalized extension parameter and explicitly declines to map the bare delta coefficients to B.

### C3 — variational_domain_and_self_adjointness

Required: Derive every boundary condition by varying the retained regulated action and prove that the complete, possibly generalized, KK operator is self-adjoint on that domain.

V47: For an externally supplied constant Hermitian B, V47 proves cancellation of the boundary form and reality of signed eigenvalues.  It does not derive that B or the domain from a microscopic boundary action with induced operators.

### C4 — positive_kinetic_form

Required: Give the bulk plus boundary quadratic norm, including boundary kinetic mixing and any retained boundary fields, and certify positivity throughout the declared EFT domain.

V47: No boundary Kahler/kinetic matrices or generalized norm are present; the no-tachyon theorem explicitly excludes negative boundary kinetic norms.

### C5 — counterterm_and_renormalization_scheme

Required: Name the regulator and subtraction prescription, list every counterterm at the retained order, give renormalization conditions at mu_star and show regulator/scale independence up to the declared remainder.

V47: V47 normalizes same-domain spectral products but leaves absolute and cross-boundary constants to an unspecified brane regulator and local counterterm scheme.

### C6 — symmetry_and_naturalness_policy

Required: For every omitted allowed operator through the retained order, provide a symmetry/EOM reason; for every retained coefficient give a renormalized input or matching value and an NDA-sized domain.  Zero is not a symmetry argument.

V47: V47 correctly proves that neutral discrete sequestering cannot remove STheta Phi^2 and STheta Sigma barSigma, but it supplies no fixed-order policy for the infinite neutral dressings.

### C7 — action_to_Wilson_matching

Required: Integrate the regulated boundary layer and the four hypermultiplets with all declared wall currents, publish the matrix Schur-complement/Green-function Wilson kernel, and verify its low-energy expansion and remainder in the same scheme.

V47: The exact homogeneous characteristic C(m) is known, but no inhomogeneous Green function, current map, Wilson coefficient or regulator-matching comparison is supplied.

## Post-V48 clause review

| ID | State | Adversarial finding |
|---|---|---|
| C1 | fail | The parity-resolved fixed-order basis is incomplete: mu_H HH and PS normal-derivative operators are absent; the finite collar does not census Hc-dependent responses; and pure-source quartics at the same 1/Lambda order are assigned to G3 rather than parameterized. |
| C2 | pass | The finite positive square collar is retained as the fundamental problem, has normalized source modes, and uses the pole-free characteristic rather than discarding D-block poles. |
| C3 | partial | Self-adjointness is proved for the quadratic source collar, but not for the complete PS/source action after all allowed derivative and kinetic operators are included and varied. |
| C4 | partial | The collar and named matter metrics are positive, but no full Schur-complement/no-ghost test includes source-field Kahler responses, PS derivative mixing and the Zhat boundary term. |
| C5 | partial | A tree-level matching scale and one quadratic collar scheme are declared, but the complete retained-order counterterm basis, subtraction conditions and profile-rematching check are absent. |
| C6 | partial | The finite-order/no-selector policy is sound, but allowed omitted coefficients and the Hc profile zeros lack a symmetry, matching condition or demonstrated remainder assignment. |
| C7 | partial | G00=(Kreg+Nreg V0)^-1 Nreg and its source-projector derivatives are a useful structural advance, but the executable witness uses representative matrices.  It does not publish the physical component Clebsches/projectors and current matrices for all 19 PS vertices plus the derivative/Hc operators, so it is not a complete Wilson coefficient match. |

## Parity-resolved omissions

At the PS wall the eight non-derivative even bulk traces are the four selected
`H` traces and the four complementary `Hc` traces.  The 19 spinor cubic terms
in the operator artifact are the correct exhaustive cubic count.  They are not
the complete renormalizable PS superpotential: `mu_H epsilon_L epsilon_R H H`
is allowed by PS, `U(1)F`, and matter parity after V47 explicitly withdrew the
inherited `Z4R` selector.

The PS action must also include or explicitly reduce the covariant
normal-derivative `O7/O8` structures and the allowed brane--bulk mixings such
as `Q_i (nabla5 HLFc)_L` and `Qc_i (nabla5 HRAc)_R`.  The source collar does
not replace independent PS-wall counterterms.

The finite collar makes `Hc` nonzero in its interior.  Exact symmetries allow
the conjugate portals

- `ThetaMinus HLFc HLAc`
- `ThetaPlus HRAc HRFc`
- `Sigma HLFc HRAc`
- `barSigma HLAc HRFc`

For a nonsingular symmetric profile and outer Dirichlet condition these
`Hc Hc` terms begin at `O(epsilon^2 E^2)` and can consistently enter the
declared remainder, but that scaling and the profile symmetry must be part of
the action contract.  A merely one-sided slab does not by itself forbid
localized/source-dependent `Hc H` and mixed `H--Hc` Kähler responses, which
can enter already at `O(epsilon E)`.

## Exact all-order sparsity no-go

The current symmetries do not select a finite boundary action at all orders.
The explicit neutral Kähler invariant

`Y = ThetaPlus^dagger exp(2 q_Theta V_F) ThetaPlus`, with
`q_F(Y)=-3+3=0` and zero R charge,

dresses every allowed D-term by arbitrary powers.  The holomorphic
`X=ThetaPlus ThetaMinus` supplies additional F-term dressings whenever its R
charge permits.  Neutral contractions of `Phi210`, `Sigma barSigma` and
`STheta` give further towers.  Therefore an
all-order finite catalogue cannot be required or claimed without a UV
completion.  The scientifically meaningful non-UV gate is a finite-order
Wilsonian basis with an explicit truncation error.

## Smallest construction that can close G2

Use a genuine interval action with one-sided boundary traces.  Keep the V47
bulk and source fields and its four source spinor superpotential portals.  At
the source and PS walls, add the complete independent boundary basis through
dimension five:

- the two U(1)F Fayet-Iliopoulos coefficients (or an exact symmetry/renormalization condition fixing them), because local anomaly cancellation does not by itself forbid a finite FI term
- all marginal gauge terms: independent W^alpha W_alpha coefficients for every unbroken factor and, on the PS wall, the allowed Z_hat Z_hat term for the broken (6,2,2) gauge multiplet
- all dimension-five gauge-kinetic functions, including STheta Tr(W10^2)/Lambda, STheta W_F^2/Lambda and the allowed Phi210 W10 W10/Lambda contraction
- all symmetry-allowed boundary Kahler matrices for traces of bulk hypers and source/PS fields
- the half-integer-dimension PS-wall kinetic mixings Q_i^dagger HLF/sqrt(Lambda) and Qc_i^dagger HRA/sqrt(Lambda), or the explicit field redefinition that removes them and the induced shifts of every Yukawa/current coefficient
- covariant normal-derivative and wrong-chirality hypermultiplet operators modulo EOM and field redefinitions
- all source-field dressings and mixed kinetic terms allowed at dimension five

Boundary dimension four alone is not enough for an `O(Lambda^-2)` claim: the
localized kinetic and normal-derivative operators built from 5D hypermultiplet
traces first occur at dimension five and are `O(Lambda^-1)`.

Vary this action rather than inserting an orbifold delta by convention.  At LO
the Nambu boundary condition is `g+B_N f=0`, with `B_N=B_N^dagger`.  At NLO,
use the positive generalized norm

`<Psi,Psi> = integral Psi^dagger Z_bulk Psi + boundary/Lambda`,

and either prove the energy-dependent boundary pencil self-adjoint in that norm
or retain the finite regulator states.  A smooth slab with
`epsilon=Lambda^-1`, finite supersymmetric deconstruction, or a declared
thin-brane analytical subtraction scheme is sufficient; string or other UV
completion is not required.

The matching output is the matrix Schur complement

`Gamma_eff(p)=Gamma_LL(p)-Gamma_LH(p) Gamma_HH(p)^(-1) Gamma_HL(p)`.

It must pass:

- all poles of Gamma_HH^-1 match the retained regulated characteristic
- the p=0 mass kernel reproduces the V47 ker(B_EE) theorem
- the low-energy coefficients are invariant under allowed field redefinitions
- the difference between exact and truncated kernels obeys the declared remainder bound

## Promotion decision

Current promotion: **REJECT**.

The resolved collar closes C2 and the operator artifact improves the PS/source response, but the parity-resolved NLO action, complete positive norm/counterterms and physical component Wilson-current match remain incomplete.

Promotion remains possible once one explicit V48 interval/slab artifact makes
all C1--C7 true.  It would close only G2; it would not establish a stabilized
vacuum, a full threshold/unification solution, proton stability, flavour or
phenomenological validity.

## Primary sources

- [5D N=1 superfield bulk action](https://arxiv.org/abs/hep-th/0106256)
- [systematic gauge-covariant brane operator basis including normal derivatives](https://arxiv.org/abs/hep-ph/0112230)
- [interval variational boundary actions uniquely determine boundary conditions](https://arxiv.org/abs/hep-th/0411133)
- [thin-brane classical renormalization and fixed-order EFT](https://arxiv.org/abs/hep-ph/0601222)
- [brane kinetic terms, gauge identities and unitarity](https://arxiv.org/abs/hep-ph/0411258)
- [supersymmetric boundary Fayet-Iliopoulos operators in 5D](https://arxiv.org/abs/hep-ph/0205034)
- [noncommuting thin-wall and infinite-tower limits](https://arxiv.org/abs/1408.1852)

Core SHA-256: `76825263d4d397182568168d33134c369b40261e2f3d96c51541acfca4cbd3d1`
