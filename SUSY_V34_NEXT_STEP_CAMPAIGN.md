# SUSY V34 next-step campaign

- Status: `V34_NEXT_STEPS_COMPLETE__BARE_Z33_DAI_FREED_ANOMALY_PROVED__MIXED_PRODUCT_FALSE_OBSTRUCTION_RETIRED__CHARGED_FLUX_Z33_INCOMPATIBILITY_PROVED__GAUGE_TWO_LOOP_COEFFICIENTS_RECONSTRUCTED__THRESHOLD_BRIDGE_EXISTS_CONDITIONALLY__ESTABLISHED_FULL_GATES_ZERO_OF_EIGHT__NO_COMPLETE_THEORY`
- Core: `053572fbf94c2583311de52beaa0ac9ab376b2c7ee5dab4751b890ebab65e1bb`
- Materially updated frontiers: **3/8** (`G1`, `G5`, `G6`)
- Established full predictive gates: **0/8**

## Decision

V34 executed the next calculations instead of adding another fitted axiom.  It
finds useful, reproducible physics, but **not** a complete theory.  The bare
visible `Z33` is globally anomalous, the charged-flux ansatz is incompatible
with the `P^33` quality selector, and G6 still lacks boundary data even though
all its two-loop gauge-row coefficients now match an independent invariant-norm
reference.

## G1: exact anomaly result

Only `PsiBar`, `PsiCBar`, and `P` carry `Z33`.  Their Weyl sums are
`Delta s1=-15` and `Delta s3=-15`.  The exact
residues are `84 mod 99` and
`18 mod 33`; the Dai--Freed phases
are `28/33` and
`1/11`.  They do
not vanish.  A correctly quantized pure finite-background GS/topological
coupling or a compensating UV-fermion sector is required; the conventional
mixed gauge/gravity GS term alone is insufficient.

The conventional equal-level gauge/gravity GS congruence does pass
conditionally.  Because `gcd(4,33)=1`, `Z4 x Z33` is cyclic; the two V33
mixed-product sums are not independent finite anomalies and their combined
cross contribution is exactly a multiple of 396.  This correction retires a
false blocker, but it does not supply the missing pure finite counterclass.

An exhaustive singlet search finds that at least three new `Z33`-chiral,
Pati--Salam-singlet Weyl fermions are needed for the bare subgroup; the unique
minimal charge witness is
`[20, 29, 32]`.
Its `Z4R` charges, masses, hidden dynamics, and full product anomaly are not
solved, so it remains a candidate rather than an adopted model.

## G1/G5: charged-flux incompatibility

For `K=22027` and `x=1/K`, the retained instanton terms have relative
magnitudes `1:2:1` and `Kx=1`.  If a next coefficient scales as `K^3`, it is
unsuppressed; without an all-harmonic prefactor bound, uniform truncation
control is not established.

The coefficient spurions leave only the elements `[[0, 0], [2, 0]]`,
namely the residual `Z2`, and allow `C2^2 C3^4 P`.
The first undressed pure-P monomial remains `P^33`, but after the charged
coefficient spurions acquire values, lower visible-P powers are allowed and
the protection is lost.  No cited compactification supplies a flux orbit that
repairs this.

## G6: exact reconstructed gauge-row coefficients

Independent group theory gives `S=(13,11,15)`,
`b=[1, 5, 9]` and

`B=[[108, 15, 21], [75, 53, 3], [105, 3, 81]]`.

The pure-gauge coefficients match the frozen V33 SARAH output entry by entry.
Applying its calibrated normalized invariant projector and independently
reconstructing the invariant norms yield the same nonnegative
Yukawa-subtraction vectors:

```text
{
  "YQQ": [
    8,
    16,
    16
  ],
  "YQX": [
    8,
    16,
    16
  ],
  "YXQ": [
    8,
    16,
    16
  ],
  "YXX": [
    8,
    16,
    16
  ],
  "kappaPS": [
    4,
    0,
    8
  ],
  "kappaX": [
    0,
    0,
    0
  ],
  "lambdaH": [
    0,
    2,
    2
  ],
  "lambdaPQ": [
    4,
    8,
    0
  ],
  "lambdaPX": [
    4,
    8,
    0
  ],
  "lambdaPcQ": [
    4,
    0,
    8
  ],
  "lambdaPcX": [
    4,
    0,
    8
  ],
  "lambdaS": [
    5,
    0,
    6
  ],
  "lambdaSb": [
    5,
    0,
    6
  ],
  "lambdaSigma": [
    2,
    0,
    0
  ],
  "yNQ": [
    4,
    0,
    8
  ],
  "yNX": [
    4,
    0,
    8
  ]
}
```

This closes the gauge-row coefficient/reference subproblem.  It is a replay of
frozen V33 SARAH output, not a new live V34 call or literal component Gram
projection.  It does not project the raw `BetaY` tensors or create the absent
16-coupling PS boundary.
The only fitted Dirac matrix has `Tr(YdagY)=`
`0.16789741344867715`;
identifying it with `YQQ` is not source-derived.

## Conditional new threshold physics

Six new chirals arranged as anomaly-neutral pairs in `(6,1,1)`, `(1,3,1)`,
and `(1,1,3)` reproduce the chosen minimum-zero-sum diagnostic correction at
conditional one-loop leading-log order.  Their mass ratios to `Mstar` are
`[0.554466811697, 1.487905480652, 0.902582437007]`
and the spread is only `2.683489`.  The
corrected inverse couplings are `[18.9419255747675, 18.9419255747675, 18.9419255747675]`.

This target is not source-derived, and the six-chiral construction is not
minimal: a four-chiral two-pair witness exists if the zero-sum convention is
released.  It is an existence witness, not an adopted completion; its
split-SO(10) embedding, decay symmetry, physical finite matching, and coupled
running have not been derived.

## Strict result

The honest gate count remains **0/8**.  V34 makes G1 and G6 much sharper and
uncovers a real G5 incompatibility; it does not invent unsupported microscopic
data.  The next executable G6 task is invariant-basis projection of every
`BetaY` tensor, followed by a piecewise coupled integration once boundary data
exist.

## Primary sources

- [Discrete gauge anomalies revisited](https://arxiv.org/abs/1808.02881)
- [Dai--Freed anomalies in particle physics](https://arxiv.org/abs/1808.00009)
- [Discrete R symmetries and GS universality](https://arxiv.org/abs/1102.3595)
- [N=1 supergraph two-loop beta methods](https://arxiv.org/abs/hep-ph/0203027)
- [Global F-theory Pati--Salam models](https://arxiv.org/abs/1503.02068)
- [Fluxed E3 instantons](https://arxiv.org/abs/1105.3193)

## Replay

```bash
python -B susy_v34_next_step_campaign.py --check
python -m pytest -q test_susy_v34_next_step_campaign.py
```
