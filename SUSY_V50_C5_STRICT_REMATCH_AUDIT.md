# V50 strict C5 second-profile rematch audit

Status: `V50_C5_STRICT_TREE_QUADRATIC_PROFILE_REMATCH_COMPLETE__FULL_SP_COUNTERTERMS_REALIZED_IN_LOCAL_A_XI_C_ACTION__FIXED_TRANSFER_JET_RENORMALIZATION_REMOVES_HOMOGENEOUS_QUADRATIC_PROFILE_AMBIGUITY_THROUGH_O_LAMBDA_MINUS1__LOOP_DIVERGENCE_MIXING_THRESHOLD_SUBTRACTION_AND_SCALE_CANCELLATION_UNCOMPUTED__C5_REMAINS_PARTIAL__G2_OPEN`

## Verdict

The independent-profile test now **passes for the complete quadratic tree
collar through `O(Lambda^-1)`**.  The regulator-profile difference is an exact
symplectic transfer.  Its leading correction and first spectral jet are
Hamiltonian and decompose into the already retained local `A`, `Xi`, and `C`
blocks.  Holding the full renormalized transfer and its first spectral jet
fixed removes the homogeneous quadratic and fixed-endpoint-current ambiguity;
no new operator is needed for that tested sector.  Distributed collar
currents and source-functional jets are not silently included in this claim.

**Strict C5 nevertheless remains partial and G2 remains open.**  The frozen
C5 criterion also demands the retained-order subtraction calculation and
scale independence.  No one-loop divergent mixing matrix, finite local-chain
threshold subtraction, beta functions, or component projection of those
divergences has been computed.  That conjunct cannot be replaced by the
tree-level profile rematch.

## Exact tree rematch

Let `x=m epsilon=m/Lambda` and let `T_star(x)` and `T_p(x)` be the two
independently integrated same-action collar transfers.  Although every
individual profile has the same zeroth moment, their noncommuting ordered
moments differ.  Before rematching,

```text
||T_star(0)-T_p(0)|| = 0.0020859161,
last/first raw Wilson mismatch = 1.0298504.
```

Define

```text
C_exact(x) = T_star(x) T_p(x)^-1,
H0 = principal_log C_exact(0),
H1 = C_exact'(0) C_exact(0)^-1,
C_CT(x) = exp(x H1) exp(H0).
```

Because both transfers are symplectic, `H0,H1 in sp(2n)`.  In the deterministic
four-channel calculation their Hamiltonian residuals are
`0.000e+00` and
`0.000e+00`.  Their reconstruction from
`[[C,Xi],[-A,-C^T]]` has residuals
`0.000e+00`
and `0.000e+00`.
Thus the correction is inside the declared local action, not an abstract
unmapped boundary matrix.

The leading layer reproduces `C_exact(0)` to
`1.742e-15`.  The weak layer corresponds
to the symmetric spectral counterterm `Z_CT=-J0 H1`; the total representative
Kahler metric remains positive with minimum eigenvalue
`0.319186`.

For successive halvings of `x`, the corrected transfer errors are
`[4.247179917971649e-06, 1.0620940380096428e-06, 2.6556004889136953e-07, 6.63945284386993e-08, 1.659919393070568e-08]` and their ratios are
`[0.2500704134325615, 0.25003440315796077, 0.2500170063828342, 0.25000846185738596]`.  They scale as `x^2`.

After composing the unchanged bulk transfer and enlarged endpoint pencils,
the physical Wilson-response errors at widths `[0.08, 0.04, 0.02, 0.01]` are
`[2.9958064117495156e-06, 7.377923046715414e-07, 1.8313551434457866e-07, 4.562547008378616e-08]` with ratios
`[0.24627502691026, 0.2482209602689052, 0.2491350202994464]`.  They scale as `epsilon^2`, whereas
the unrematched errors approach a nonzero thin-wall value.

## Fixed tree renormalization conditions

At `mu_star=Lambda`, use the principal-log outer-layer chart and hold fixed:

1. the entire renormalized transfer `T_R(0)=T_star(0)`;
2. the left spectral jet `(dT_R/dx)T_R^-1|_0`;
3. the enlarged Hermitian endpoint pencils and their undivided auxiliary
   determinant factors.

These conditions determine profile-dependent **bare** `H0,H1` shifts while
keeping the tested renormalized response fixed.  Therefore the old inference
that an unmapped homogeneous-quadratic coefficient necessarily survives is
rejected; the affine distributed-current sector remains an explicit missing
calculation.

## Why strict C5 still fails

The unchanged C5 criterion is: name the regulator and subtraction
prescription, list every retained-order counterterm, give renormalization
conditions, and prove regulator/scale independence to the declared remainder.
The finite local deconstruction regulator is named, and the tree quadratic
conditions above are complete.  The following required data remain absent:

1. the one-loop divergent 1PI boundary functional in the finite local deconstruction regulator
2. the anomalous-dimension/operator-mixing matrix for every V49 retained invariant direction
3. finite thresholds of the transport pairs, gauge-link sector, and any linear-link radial completion
4. bare-to-DRbar maps for A,Xi,C,R7,R8,Kahler,FI,gauge,source-quartic and portal coefficients
5. a beta-function proof that the full physical Wilson array is mu_star independent through O(Lambda^-1)
6. an affine/distributed-current and source-functional profile rematch for every retained portal and derivative-current direction
7. normalized component tensors needed to project the loop divergences into every retained SO(10)->PS direction

Consequently `C5=PARTIAL_NOT_CLOSED`.  The precise obstruction is now the
missing loop/threshold mixing and scale-cancellation calculation—not an
unrealizable tree-level symplectic counterterm.

Core SHA-256: `2cce92e6890fedaedfa51aba425849b4ac0254486a42195565b89ada9301fa1f`
