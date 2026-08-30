# V47 coupled source completion and route audit

Status: V47_COUPLED_NEUTRAL_SOURCE_BRANCH_AND_GENERIC_PHYSICAL_RANK_PROVED__PARAMETER_NEUTRAL_DISCRETE_SEQUESTERING_NO_GO__210_ROUTE_RETAINED_BY_EXACT_RANK_CERTIFICATE__45_PLUS_54_HAS_BETTER_INDEX_WINDOW_BUT_FULL_HESSIAN_REPLAY_OPEN__NO_G_GATE_PROMOTED

## Result

The neutral-210 source branch survives the unavoidable renormalizable Theta/GUT cross couplings and remains generically full physical rank. A 45+54 replacement has an exact SU5 branch and a materially better one-loop index budget, but it is not promoted without a complete independent Hessian replay.

The coupled source contains 465
chiral components.  Spin(10) to SU(5) and U(1)F to Z3F eat
22; the remaining
443 are
generically massive.

## Unavoidable cross couplings are harmless to local rank

After shifting the neutral singlet, the relevant general form is

W=W_GUT(m0+m1 STheta,M0+M1 STheta,lambda,eta)+kappa STheta ThetaPlus ThetaMinus+f0+f1 STheta+f2 STheta^2/2+f3 STheta^3/3.

Set STheta=0 and use the already-certified SU(5) GUT branch.  F_STheta fixes
ThetaPlus ThetaMinus, while every other F equation reduces exactly to the
isolated V46 equation.  On the gauge-fixed physical space the Hessian is

[[H,0,c],[0,0,a],[cT,a,d]],

whose determinant is -a^2 det(H).  It is nonzero whenever the V46 GUT Hessian
is nonzero and the Theta VEV/coupling is nonzero.  Thus including STheta Phi^2
and STheta Sigma barSigma does not create a physical flat direction.

The determinant follows by one cofactor expansion along the Theta-radial row;
the executable exact-rational witnesses also pass in dimensions 1 through 4.

No parameter-neutral ordinary or R-type discrete symmetry can forbid those
cross terms while retaining the standard mass, cubic and driver terms.
Charged coefficients would be new spurion fields and a different model.

## 45+54 comparison

The alternative source superpotential has an exact SU(5) branch

a2=E=0, a1=sqrt(10)m2/lambda6,
Sigma barSigma=10 m4 m2/lambda6^2.

The executable rescaled witness has all branch residuals zero:
{'F_Delta_divided_by_V': '0', 'F_A1_rescaled': '0', 'F_A2': '0', 'F_E': '0'}.

Its complete physical Hessian is not replayed here, so it is not promoted.
The published general mass matrices make it a concrete priority alternative.

At alpha inverse 25, the source-sector-only one-loop index proxy gives:

- 210 route: sum T=126, b=102,
  naive vector-included Landau ratio=4.665.
- 45+54 route: sum T=90, b=66,
  naive vector-included Landau ratio=10.805.

The exact comparison is sum T=90 versus 126.  The displayed pole ratios omit
common matter/light fields and are only proxy values; they are neither complete
4D beta functions nor the required 5D threshold calculation.

## Decision

Retain the neutral 210 route because its full source-Higgs rank has an
executable certificate.  Include all gauge-allowed neutral cross couplings.
Keep 45+54 as the leading lower-index alternative until its complete Hessian
is independently replayed.

No full G gate is promoted.

## Remaining obligations

1. specialize and replay every 45+54+126+bar126 mass block on the exact SU5 branch before considering a route switch
2. perform the actual 5D brane-plus-bulk threshold and NDA cutoff calculation for the retained 210 route
3. couple the source solution to the enlarged four-spinor KK operator and the relative eta problem
4. solve Kahler, radion, SUSY-breaking and cosmological branch selection

Core SHA-256: 15ebb7f8e763c98784c65a709d1d753d4327cf28d6029e6a635a8198c6ce2881
