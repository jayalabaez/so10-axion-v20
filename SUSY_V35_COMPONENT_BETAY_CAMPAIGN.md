# SUSY V35 component BetaY campaign

- Status: `V35_COMPONENT_BETAY_RECONSTRUCTION_COMPLETE__FROZEN_V33_BETAY_PROJECTION_IMPOSSIBLE__LIVE_YIJK_BASIS_111_BY_42_RANK42__ONE_AND_TWO_LOOP_COMPONENT_BETAS_PROJECTED__GAUGE_YUKAWA_MN_LINEAR_ENGINE_COMPLETE__PHYSICAL_BOUNDARY_STILL_MISSING__ESTABLISHED_FULL_GATES_ZERO_OF_EIGHT__NO_COMPLETE_THEORY`
- Core: `96e895f90bd750d55045d820a1cc9aed55e4ac2b2ae8646bd4cafa67503ae392`
- Materially updated frontier: **G6**
- Established full predictive gates: **0/8**

## Decision

V35 completes the next executable G6 derivation.  It reconstructs the full
ordered superpotential tensor with **111 chiral components**, **42 independent
complex trilinear-coupling components**, and **2,719 nonzero ordered tensor
entries**.  The exact invariant Gram matrix has rank 42 and condition number
24.0.  The standard N=1 SUSY anomalous-dimension
formula then supplies every one- and two-loop trilinear beta component.  The
same tensors now also supply the two-loop gauge feedback, all six independent
complex `MN` betas, the linear `xi_X` beta, and a callable 45-component
dimensionless gauge--Yukawa ODE.

This is real progress, but not a complete theory.  The source still has no
derived Pati--Salam-scale values for the 42 complex couplings, no mediation or
soft boundary, and no physical heavy-threshold matching.  Those missing inputs
prevent a unique coupled RGE trajectory and keep the strict gate count at 0/8.

## Why the old frozen BetaY rows are rejected

The V33 strings contain 447
unresolved epsilon tensors at one loop and
9416 at two loops.  Live
`PrepareRGEs` expands them to 42 equations but still leaves
32945 epsilon tensors.  The
flattened 18-row list also duplicates `kappaPS` across trilinear and linear
sectors.

More decisively, mandatory one-loop Casimir monomials are absent for:
`lambdaPX, lambdaPQ, lambdaPcX, lambdaPcQ, YXX, YXQ, YQX, YQQ, yNX, yNQ, lambdaSb, lambdaS, kappaPS`.  A linear projector cannot create a gauge monomial absent from
the component beta tensor.  `lambdaH` and `lambdaS/lambdaSb` also have wrong
preprojection normalizations.  Therefore the frozen string payload is lossy;
it cannot be repaired by choosing epsilon values.

## Literal component derivation

With `Cbar_i=sum_a g_a^2 C_a(i)`, V35 implements

```text
gamma1_i^j = 1/2 conj(Y_iMN) Y_jMN - 2 delta_i^j Cbar_i

gamma2_i^j = -1/2 conj(Y_iwx) Y_xyz conj(Y_yzr) Y_wrj
             + conj(Y_iyz) Y_jyz (2 Cbar_y - Cbar_i)
             + delta_i^j [2 sum_a g_a^4 C_a(i)(S_a-3C(G_a))
                            + 4 Cbar_i^2]

betaY_ijk = Y_ijn gamma_nk + Y_ink gamma_nj + Y_njk gamma_ni
beta_p    = (G^-1)_pq sum_ijk conj(T_q,ijk) betaY_ijk

beta_g,a^(2) = g_a^3 [sum_b B_ab g_b^2
                       - sum_ijk |Y_ijk|^2 C_a(k)/dim(G_a)]
beta_M,ij    = M_in gamma_nj + M_jn gamma_ni
beta_L,i     = L_n gamma_ni
```

Here `T_p=dY/dc_p`.  The component Casimirs independently reconstruct
`S=(13,11,15)`.  The exact one-loop gauge coefficients and two-loop pure-gauge
polynomials for all 42 components are frozen in
`SUSY_V35_G6_COMPONENT_BETAY_CLOSURE.json`.

The exact singlet anchor passes:

```text
beta_kappaX^(1) = 3 kappaX (2|kappaX|^2 + 3|lambdaSigma|^2
                            + 8|kappaPS|^2 + 2|lambdaH|^2)
beta_kappaX^(2) = -24 kappaX |kappaX|^4    [kappaX-only]
```

At a deterministic complex, nonphysical audit point, the maximum projection
residuals are 2.776e-16 at one loop and
3.887e-16 at two loops.  Both beta tensors
are symmetric and both anomalous dimensions are Hermitian to numerical
precision.  The 42 projected beta values are stored explicitly so the result
is replayable without inventing a phenomenological boundary.

## Completed downstream RGE layer

The component Yukawa norms independently reproduce every V34 gauge-row
subtraction vector.  At the audit point, their coefficient replay residual is
`5.551e-17`.  The
dimensionful projection contains 6
independent symmetric `MN` components and one `xi_X`; all one- and two-loop
beta support outside those declared tensors is exactly zero.

A fixed-step RK4 audit evolves all 3 real gauges and 42 complex trilinears over
a scale ratio of 10.  Forward integration followed
by the inverse interval returns the complete state with maximum residual
`4.119e-14`.  This proves the
coupled dimensionless engine is executable.  Its starting values are an
explicitly nonphysical audit point, so it is not promoted to a prediction.

## Strict result and next boundary

The component gauge, trilinear, `MN`, and linear RGE algebra is complete.  G6
itself remains open until a source-derived boundary, soft mediation, physical
matching, and uncertainty-propagated piecewise integration exist.  G1--G5 and
G7--G8 retain their V34/V33 fail-closed states.  No new fundamental law is
claimed.

## Primary references

- [N=1 SUSY two-loop beta functions](https://arxiv.org/abs/hep-ph/0203027)
- [Pati--Salam/SO(10) RGE framework](https://arxiv.org/abs/hep-ph/0206118)
- [SARAH](https://arxiv.org/abs/0806.0538)

## Replay

```bash
python -B susy_v35_component_betay_campaign.py --check
python -m pytest -q test_susy_v35_component_betay_campaign.py
```

To regenerate the live tensor evidence:

```bash
wolframscript -file tools/probe-susy-v35-betay.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3 --output SUSY_V35_SARAH_BETAY_FEASIBILITY_PROBE.json
wolframscript -file tools/derive-susy-v35-yijk-basis.wls --repo-root . --sarah-root ../../external-tools/SARAH-4.15.3 --output SUSY_V35_SARAH_YIJK_COMPONENT_BASIS.json
```
