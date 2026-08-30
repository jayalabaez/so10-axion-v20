# SUSY V26 G1 dynamical Green--Schwarz completion attempt

- Status: `V26_G1_DYNAMICAL_GS_EFT_CONSTRUCTED__MODULUS_STABILIZED__HIDDEN_ANOMALIES_MATCH__MICROSCOPIC_UV_AND_WILSON_MATCHING_OPEN__FULL_G1_NOT_CLOSED`
- Core: `7dd049d43e1ce6cb6e9ca3385ecb2895521443a80f5af1363260d4ea637ba59d`
- Full G1 closed: **no**.
- Qualified dynamical GS EFT subgate closed: **true**.

## New result

A dynamical four-dimensional completion of the previously topological-only GS term now exists at a precise EFT scope. With `theta_GS` of period one, the `Z4R` and `Z11` shifts generate the elementary quotient translation `1/22`. A superpotential exponential `exp(-2*pi*n*T)` is covariant only for `n=11 mod 22`; the first three choices are `11, 33, 55`.

Three hidden pure-SYM groups realize those exponents in the declared condensation convention: `SU(2)_h` at level 22, `SU(3)_h` at level 99, and `SU(5)_h` at level 275. Every hidden `Z4R` and `Z11` mixed anomaly congruence matches the same GS shifts. Their R-gravitational contribution is 35; including the R-neutral chiral modulus's charge-minus-one modulino gives `20+35-1=54`, so the visible + hidden + modulus congruence remains matched. The condensates break `Z4R` only to the same residual `Z2` matter parity.

The exact racetrack is

`W_GS=M^3[2 exp(-22*pi*T)-16 exp(-66*pi*T)+32 exp(-110*pi*T)]`.

At `T0=log(2)/(22*pi)` its three terms are exactly `(1,-2,1) M^3`, so `W=0` and `W_T=0`, while `W_TT=3872*pi^2 M^3`. With `K=-log(T+Tdag)`, this is a supersymmetric Minkowski point and both canonically normalized real modulus components have strictly positive mass squared.

## Why full G1 still does not close

This construction is a consistent 4D dynamical GS/racetrack EFT, not a microscopic UV realization. No compactification or other fundamental source has been supplied that derives the integer levels, the condensate threshold prefactors `(2,-16,32)`, or the quotient of all `2*3*5=30` pure-SYM branches. Those quantities are inputs here.

The all-order PS tensor grammar is now stated constructively using the `SU(4)` delta/epsilon tensors, the antisymmetric realization of the 6, and the two `SU(2)` epsilon tensors, followed by the exact `Z4R x Z11` filters. But an independent normalized all-order basis and syzygy reducer is not implemented, and the Wilson, Kahler, gauge-kinetic, and soft coefficients are not UV matched. The pure-discrete/cubic anomaly is likewise UV-sensitive and has no microscopic counterterm audit. The V25 arbitrary driver function therefore remains genuine input data.

## Decision

The plausible dynamical route was executed and passes every internal check, but it does not satisfy the repository's microscopic-UV G1 definition. Full G1 remains open. Closing it would require an explicit UV source reproducing the spectrum, levels, selectors, stabilized moduli, branch quotient, and all-order matching; inventing those data would not be a physics solution.

Primary references: [Kawamura--Raby PS model](https://arxiv.org/abs/2009.04582), [discrete R anomalies and GS cancellation](https://arxiv.org/abs/1212.4371), [field-dependent gaugino condensation](https://arxiv.org/abs/hep-th/9505171), and [supersymmetric racetrack stabilization](https://arxiv.org/abs/hep-th/0511042).

Finite quotient regression: first exponents `[11, 33, 55]`. Hidden raw branch count: `30`.
