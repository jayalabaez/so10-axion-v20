# V77 equivariant parent anomaly-line audit

Status: `V77_EQUIVARIANT_PARENT_ANOMALY_LINE_AUDIT__V70_V71_AND_V76_CORES_BOUND__T2_Z4_SPACE_GROUP_ABELIANIZATION_Z4_X_Z2_EXACT__EIGHT_FLAT_CHARACTERS_ENUMERATED__SMOOTH_AND_ORDER2_DATA_DO_NOT_FIX_ORDER4_TRACES_EXACT__V71_STANDARD_LIFT_EQUAL_CORNER_RESIDUE_REPRODUCED__TEN_NEUTRAL_CHIRAL_COMPACTIFICATION_ZERO_MODES_EXACT__SCALAR_PARENT_DETERMINANT_NOT_DEFINED__BRST_GHOST_SELF_DUAL_CAP_REGULATOR_AND_ZERO_MODE_TRIVIALIZATIONS_ABSENT__NAIVE_SMOOTH_GS_CLASS_FAILS_ALL_ORDINARY_ORBIFOLD_ISOTROPY_DIVISIBILITY_TESTS__UNCHANGED_TENSOR_LATTICE_TWIST_FORCED_IDENTITY__STANDARD_INDUCED_Z2_RAW_BRANCH_HAS_CONDITIONAL_SU2R_POLYNOMIAL__F76_TARGET_REFINED_TO_EQUIVARIANT_ANOMALY_LINE_PLUS_WUCS_TRIVIALIZATION__SELECTED_OPEN__G1_TO_G8_OPEN`

Core SHA-256: `fa54bc8ad2ed0991bb7923d6ef7d2da80505e27673d32d22c814369df7c152bb`

## Exact correction to the V76 target

V71 proves at least **10 neutral chiral
compactification zero modes** for its bound internal witness.  The internal KK
product therefore vanishes at zero external momentum, but this does not assert
that the six-dimensional determinant vanishes on every external background.
No external operator, zero-mode measure or mass has been fixed.  With chiral
and self-dual fields the correct quantum object is the combined anomaly line with
its Green--Schwarz/Wu--Chern--Simons anomaly theory and a trivialization.

## Parent-action scenario freeze

The selected V70 branch is `integer_m301_dynamical_reduction`.  No accepted full
parent action exists.  Applying V71's provisional F71 normal lifts to the
inherited V70 `X`, `Xbar`, and `S0` fields and the bound V71 bulk/neutral profile gives
`[-28, -20]`
at z00 and
`[-24, -24]`
at z11 in the `(nu^3,nu p1)` numerator over 192.  The corresponding provisional
mixed normal-gauge vectors are
`{'z00': ['-1/4', '-60'], 'z11': ['-1/4', '40']}`.
Only the complete F71 local perturbative ledger restores equal corners, and F71
is both unaccepted and not a same-action completion.  Thus the equal-corner
V76 theorem remains exact for its bound F71 profile, not for unmodified V70.

## Space-group character theorem

The square-torus space group has presentation `A^4=1; [U,V]=1; A U A^-1=V; A V A^-1=U^-1`.
Its abelianization is exactly **Z4 x Z2**, giving
**8** flat one-dimensional characters.  The two
order-four corners use `A` and `UA`.  A translation sign can therefore change a
same-sign profile into an opposite-sign profile, while the real `m=2` character
flips both order-four traces without changing the identity or actual `UA^2` Z2 trace.

This is an identifiability theorem, not a list of accepted supergravity lifts.
Reality, preserved supersymmetry, BRST and global-bundle consistency must select
the physical row field by field.

## What remains exact from V71-V76

The V71 component blocks over 192 are
`{'charged_gaugino_plus_three_11_hypers': [44, 4], 'gauge_fixed_gravitino_plus_tensorino': [42, -18], 'neutral_266_at_Delta_minus10': [-110, -10]}`.  Their standard untwisted sum is
`[-24, -24]`, namely
`-(1/8) nu (nu^2+p1(T4))` at each order-four corner.
Thus the V75-V76 equal-corner odd-quarter theorem is reproduced and is **not
retracted**.  A future different raw lift would define a changed profile and
would require the complete ledger to be recomputed.

## Parent quantum input contract

Present inputs: `D1, D2, D3, D4`.

Missing inputs: `D5, D6, D7, D8, D9, D10, D11, D12, D13, D14, D15`.

The V71 virtual Rarita--Weyl index is sufficient for its perturbative polynomial
but not for the individual kinetic operators, ghost determinants, zero-mode
measure, tensor quadratic refinement, caps or regulator.

## Exact ordinary GS obstruction

The smooth string-charge lattice is
`U with Omega=[[0,1],[1,0]]` with
`a=[2, 2]` and
`b=[2, -1]`.  Their determinant is
**-6**, so an unchanged-action
lattice automorphism fixing both is forced to be the identity.  The ordinary
class has `2Y=(3,2)` at each Z4 corner and `2Y=(1,1)` at the Z2 orbit; every row
fails divisibility by two.  A regulator cannot supply the missing integral
class.  A newly constructed combined-H refinement remains possible, not proven.

## New order-two SU(2)R obligation

V71's statement that the Z2 normal polynomial vanishes remains exact in the
`nu^3, nu p1` basis.  It is not a full-background vanishing statement.  Under
the standard induced Rarita/ghost/tensor branch, retaining the SU(2)R Cartan
root gives
`rho (4 rho^2+21 nu^2-25 p1(T4))/96` on the single Z2 orbit.  Its coefficient
vector over 96 is
`[4, 21, -25]`.
This is a conditional exact equivariant index density: the global BRST/BV lift and
H_Gamma orbibundle that would promote it to a parent result are still absent.
Its scope is: gauge and flavor curvatures are set to zero; this is only the (nu,rho,p1) projection, not the complete parent polynomial.
The same branch gives the Z4 cross-check
`(-24 nu^3-24 nu p1-196 rho^3-23 rho p1+303 rho nu^2-132 rho^2 nu)/192` at either
order-four corner.  Setting `rho=0` recovers the bound V71 result exactly; the
`rho^2 nu` term is equivalently `+(11/16) nu c2(R)`.  This Z4 projection excludes
inherited V70 and new F71 localized fields as well as gauge/flavor curvature.

## Completion equation

On a closed seven-manifold the required phase shadow is
`A_bare(U) * WCS^s_(Lambda,checkY_H)(U) * A_cap_defect(U) = 1`.  The actual target is
`a specified natural symmetric-monoidal isomorphism A_bare tensor WCS^s_(Lambda,checkY_H) tensor A_cap_defect ~= 1` on
a to-be-defined equivariant/stratified H_Gamma bordism category: six-dimensional objects and seven-dimensional bordisms with caps, junctions and differential cocycles, compatibly with cutting and gluing.  It must respect cutting and gluing.  The
smooth bounding-manifold cancellation formula is known, but it does not supply
the missing orbifold `checkY_H`, cap states, or zero-mode trivialization.
Here `nu` is the normal first Chern root, not the degree-four Wu class.

## Route adjudication

- `F77A_V71_POLYNOMIAL_AS_FULL_DETERMINANT` — **REJECTED_CATEGORY_ERROR**: a local curvature polynomial is not a determinant-line section or its trivialization
- `F77B_UNPRIMED_NUMERIC_PARENT_DETERMINANT` — **REJECTED_EXACT_ZERO_MODES**: the bound internal operator has ten zero eigenvalues at zero external momentum, while no external background, zero-mode measure or mass is fixed
- `F77C_ASSUME_STANDARD_UNTWISTED_RAW_CHARACTERS` — **CONDITIONAL_SCAFFOLD_ONLY**: reproduces V71 but omits field-by-field BRST, cap and global-H proof
- `F77D_FLAT_CHARACTER_REPAIR` — **DIAGNOSTIC_NOT_A_COMPLETION**: character twists expose sensitivity but are not accepted supersymmetric actions
- `F77E_EQUIVARIANT_ANOMALY_LINE_WUCS_TRIVIALIZATION` — **SELECTED_OPEN**: correct quantum object, but its BRST, zero-mode, tensor, cap and cocycle inputs are absent


## Fail-closed decision

V77 closes the scalar-determinant shortcut and replaces it with the correct anomaly-line problem.  The square-torus Z4 space group has abelianization Z4 x Z2 and eight flat characters; therefore smooth and order-two data alone cannot identify the order-four fixed-point traces or the relative two-corner profile.  For the complete but unaccepted F71 local ledger, V71's standard untwisted lift reproduces the V75-V76 equal-corner residue exactly, so their odd-quarter no-go remains valid for that bound profile.  It is not the unmodified V70 action: V71's provisional qL lifts on the inherited V70 X/Xbar/S0 fields shift the provisional z00 normal-gravity vector to (-28,-20)/192 while z11 remains (-24,-24)/192, and their mixed normal-gauge vector also stays uncanceled.  No accepted action scenario supplies all raw BRST characters or a global H-orbibundle.  In addition, the internal KK product has ten neutral zero eigenvalues at zero external momentum; this does not assert a zero determinant on every external background.  The self-dual sector needs a quadratic refinement and WuCS data.  More sharply, the ordinary smooth GS class fails the integral restriction test at both Z4 corners and the Z2 orbit, while a,b rigidly forbid a nontrivial unchanged-action tensor-lattice twist.  A combined H-cocycle is still possible but unconstructed.  On the standard induced raw branch, retaining the SU2R root also yields the conditional Z2 polynomial rho(4 rho^2+21 nu^2-25 p1)/96; V71's normal-only Z2 zero remains correct, but is not the full parent answer.  The present action remains rejected; the research program remains viable through an explicit equivariant anomaly-line plus GS/WuCS trivialization.

Remaining obligations:

- select and construct one accepted same-action parent field, VEV and localized profile, explicitly deciding whether the F71 compensators and provisional qL lifts exist
- write the field-by-field Spin-SU2R-gauge-flavor space-group lift, including translation characters and every BRST ghost
- construct the global Spin-SU2R-Sp266-Spin11 H-orbibundle and its fixed-stratum restrictions
- derive or reject the conditional rho(4 rho^2+21 nu^2-25 p1)/96 order-two polynomial from the complete BRST/BV lift
- choose gauge-fixing operators and elliptic boundary domains for gravitino, Yang--Mills, tensor and ghost complexes
- supply a zero-mode measure or honest supersymmetric mass/stabilization operator for the ten neutral chiral modes
- construct the self-dual quadratic refinement, tensor polarization and equivariant GS/WuCS differential cocycle
- cancel the self-dual-string charge/tadpole with a worldsheet anomaly-inflow sector, or explicitly restrict the bordism domain to source-free [Y]=0 backgrounds
- pin caps, APS projectors, regulator and reference eta invariant, then compute curvature and holonomy of the combined anomaly line
- only if that line is canonically trivialized, recompute the localized residue and reapply the V74-V76 repair classification

G1-G8 remain OPEN.

## Primary sources

- [Eta-Invariants and Determinant Lines](https://arxiv.org/abs/hep-th/9405012) — eta invariants with boundary are determinant-line elements; variation, holonomy and gluing
- [Anomalies on Six Dimensional Orbifolds](https://arxiv.org/abs/hep-th/0612212) — bulk-fermion contributions to fixed-point anomalies on six-dimensional Zn orbifolds
- [Perturbative Anomaly Inflow on Orbifolds](https://arxiv.org/abs/2608.23326) — equivariant APS fixed-point density as an orbifold anomaly polynomial
- [Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0305024) — path-integral localized anomalies with Scherk--Schwarz boundary data and GS inflow
- [The global gravitational anomaly of the self-dual field theory](https://arxiv.org/abs/1110.4639) — self-dual partition/anomaly line and its quadratic-refinement data
- [The global anomaly of the self-dual field in general backgrounds](https://arxiv.org/abs/1309.6642) — self-dual anomaly line in backgrounds with gauge fields and Wu-class refinements
- [Topological field theories on manifolds with Wu structures](https://arxiv.org/abs/1607.01396) — seven-dimensional Wu--Chern--Simons anomaly theories and quadratic refinements
- [Remarks on the Green-Schwarz terms of six-dimensional supergravity theories](https://arxiv.org/abs/1808.01334) — smooth-spin six-dimensional GS/WuCS construction, charge lattice and characteristic element; not an orbifold theorem
- [Anomaly Inflow and the eta-Invariant](https://arxiv.org/abs/1909.08775) — regulated fermion phases as eta-invariant anomaly inflow
- [Anomaly Cancellation in Six Dimensions](https://arxiv.org/abs/hep-th/9304104) — smooth six-dimensional multiplet anomaly polynomial and H-V+29T relation
- [Gravitational Anomalies](https://doi.org/10.1016/0550-3213(84)90066-X) — gauge-fixed Rarita complex, reality normalization and chiral gravitational anomaly indices
- [All couplings of minimal six-dimensional supergravity](https://arxiv.org/abs/hep-th/0101074) — six-dimensional (1,0) gravity, tensor, vector and hypermultiplet field content
