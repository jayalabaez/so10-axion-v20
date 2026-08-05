# Next executable calculation: full non-SUSY scalar potential and Hessian

## Source correction

The former E/F/J/X Clebsch-normalization plan is retired.

Aulakh Appendix E/F/J/X are mixed chiral-gauge fermion/gaugino matrices. Their `g` is the SO(10) gauge coupling, not the superpotential `gamma` coupling. They cannot be used to define a non-supersymmetric scalar `lambda4` normalization or threshold.

The obsolete targets are forbidden:

- no E/F/J/X slot matching for scalar closure;
- no `gamma_eff/lambda4` extraction from E/F/J/X;
- no resurrection of the withdrawn `8.8e29` bound;
- no `EFJX_CGC_NORMALIZATION_INPUT_V20.json` closure artifact.

## Completed direct tensor work

The direct scalar invariant

`lambda4 S H_i Phi_jklm Sigmabar_ijklm / 4! + h.c.`

has been implemented as a canonically normalized `10 x 126` tensor map using the complete `(P,A,W)` singlet basis.

Its analytic singular branches are:

1. `sqrt((P+A/sqrt(3))^2+4 W^2/3)`, multiplicity 3;
2. `abs(P-A/sqrt(3))`, multiplicity 3;
3. `abs(A+W/sqrt(2))`, multiplicity 2;
4. `abs(A-W/sqrt(2))`, multiplicity 2.

The independent Aulakh VEV dictionary is

`P=p`, `A=sqrt(3)a`, `W=sqrt(6)omega`,

and the direct spectrum matches the genuine `gamma`-dependent chiral triplet/doublet Clebsch magnitudes.

## Correct next goal

Build the complete physical non-supersymmetric scalar mass-squared matrix and solve the global `hEW=174 GeV` vacuum.

## Executable sequence

1. **Complete invariant ring**
   - Enumerate every charge-allowed independent scalar operator through the declared engineering dimension.
   - Prove linear independence and record Hermitian-conjugation conventions.

2. **Full component projection**
   - Project every invariant into canonical Pati-Salam and Standard Model component fields.
   - Insert the direct `lambda4 vS T_Phi` off-diagonal block.
   - Do not import SUSY fermion/gaugino matrices as scalar masses.

3. **Stationarity and hierarchy**
   - Solve all stationarity equations with `hEW=174 GeV`.
   - Trace every numerical VEV and coupling to the canonical `(P,A,W)` convention.
   - Demonstrate a technically stable hierarchy mechanism.

4. **Gauge-projected component Hessian**
   - Construct the complete real scalar `M^2` matrix.
   - Remove exactly 33 gauge Goldstones.
   - Require every remaining eigenvalue to be positive.

5. **Global vacuum and boundedness**
   - Check all enumerated competing extrema.
   - Prove the target vacuum is lower.
   - Apply a boundedness certificate to the complete potential.

6. **Physical thresholds and downstream predictions**
   - Emit physical triplet, doublet and singlet masses with multiplicities and SM quantum numbers.
   - Only then run full two-loop threshold evolution and calculate proton decay.

## Required closure artifacts

- `FULL_MIXED_REP_INVARIANT_RING_V20.json`
- `FULL_TENSOR_PROJECTED_POTENTIAL_V20.json`
- `FULL_NONSUSY_VACUUM_HESSIAN_V20.json`

The direct tensor problem is solved. The complete scalar theory remains open.
