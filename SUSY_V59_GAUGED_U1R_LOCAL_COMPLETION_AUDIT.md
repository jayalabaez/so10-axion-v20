# V59 gauged-U(1)R local-completion audit

Status: `V59_GAUGED_U1R_LOCAL_COMPLETION__V56_V57_CORES_BOUND__V58_INTEGRATED_SPIN10_X_U1R_SEED_RECONSTRUCTED_EXACTLY__270_SINGLET_PARITIES_HAVE_AN_EXPLICIT_VEV_COMPATIBLE_SOLUTION__CONVENTIONAL_QTHETA1_LIFT_HAS_NONUNIVERSAL_MIXED_U1R_GFP2_ANOMALIES_AT_GG_FLIPPED_AND_PS__EXISTING_BULK_SPIN10_GS_INVARIANT_CANNOT_CANCEL_THEM__LOCALIZED_LEVELS_NORMAL_BUNDLE_DYONIC_STRING_AND_RESIDUAL_NORMALIZATION_DATA_OPEN__SAME_ACTION_MICROSCOPIC_COMPLETION_FALSE__G1_OPEN__ZERO_GATE_PROMOTIONS`

## Result

**The existing route-C action cannot be completed by its bulk Green--Schwarz
sector. G1 remains OPEN, and no gate is promoted.**

V59 does solve the previously unspecified 270-singlet parity problem: an exact
assignment supports one neutral and one charge-four constant coordinate and
pairs every other spectator so its parity-weighted moments cancel pointwise.
The obstruction instead comes from fields that the four-weak-mode topology
fixes: the Spin(10) gaugino and the two charged bulk tens.

## Reconstructed integrated seed

```text
T=1, V=46, H=290,       H-V+29T = 273
S2=926, S4=8054, q_av=1
P = u^2 - 150 u f + u t + 5336 f^2 - 24 f t - 2 t^2
  = 1/2[(3u/2-104f)^2-(u/2-12f-2t)^2]
Omega = [[1, 0], [0, -1]]
a=[3, 1], b10=[0, -2], bar_bR=[26, 3]
```

The lattice is integral and unimodular, `a` is characteristic, the polynomial
factorization is exact, and the positive chamber `j=(5/3,4/3)` exists. These
remain integrated-bulk results only.

The formal moment-map seed is

```text
150 |z4|^2 + 146 |z0|^2 = 2,
|z4|^2=1/150, |z0|^2=1/146.
```

Its unrescaled tangent weights `(148,144)` have gcd four. Because the scalar
derivative is `Dphi=dphi-2 A T phi`, while the anomaly spectrum uses minimal
hyperfermion charge one, this gcd is not yet a faithful `q(theta)=1` residual
group calculation.

## Exact singlet parity solution

Parity keys are `(base,t1,t2)`. The nonzero counts are

```text
q=0: +++ x1, +-+ x80, --+ x80
q=1:          +-+ x2,  --+ x2
q=2:          +-+ x5,  --+ x5
q=3:          +-+ x47, --+ x47
q=4: +++ x1
```

The two paired character vectors are negatives at every fixed point. Hence

```text
sum sign       = [2, 2, 2, 2]
sum q sign     = [4, 4, 4, 4]
sum q^3 sign   = [64, 64, 64, 64].
```

This is a feasibility witness, not local anomaly cancellation.

## Fixed-point mixed-anomaly certificate

Indices use `A(fund)=1`; raw `X` charges are the V56 convention. A common
orbifold normalization cancels from every proportionality minor.

| Fixed point | Local U(1)R-Gf^2 vector | restriction of tr10 F^2 | minors | verdict |
|---|---|---|---|---|
| O_SO10 | [6] | [1] | n/a | NO_RATIO_OBSTRUCTION_AT_THIS_POINT |
| O_GG | [4, -320] | [2, 40] | {'SU5_squared__X_squared': 800} | FAIL_EXISTING_BULK_GS_DIRECTION |
| O_flipped | [4, -320] | [2, 40] | {'SU5prime_squared__Xprime_squared': 800} | FAIL_EXISTING_BULK_GS_DIRECTION |
| O_PS | [4, -12, -12] | [2, 2, 2] | {'SU4_squared__SU2L_squared': 32, 'SU4_squared__SU2R_squared': 32, 'SU2L_squared__SU2R_squared': 0} | FAIL_EXISTING_BULK_GS_DIRECTION |

At `O_PS`, for example,

```text
45 gaugino:  (0,-8,-8)
two 10s:     (4,-4,-4)
total:       (4,-12,-12)
bulk tr10:   (2, 2, 2).
```

The nonzero minors are invariant under any overall tensor-inflow coefficient.
At `O_GG`, the exact bulk vector `(4,-320)` is not proportional to the
Spin(10) restriction `(2,40)`; its minor is `800`. The brane `X_10` and
`Xbar_-10` fermions have the raw 4D contribution `(0,-200)` because their
superfields have R charge zero and their fermions charge minus one. If the
relative corner delta normalization is any positive `c_brane`, the minor is
`800+400 c_brane`, so this localized pair cannot rescue the mismatch.

Two bulk tensors do not repair these ratios: they can alter the local overall
coefficient but both couple to the same restricted Spin(10) invariant. New
subgroup-specific localized levels or non-singlet localized matter would be a
new action and require fresh quantization, Bianchi, supersymmetry, and anomaly
checks.

## Remaining local/global data deficits

The resolved spin-half numerators are

```text
grav^2-U(1)R: [30, 10, 10, 6]
U(1)R^3:      [90, 70, 70, 66].
```

They deliberately exclude the gravitino/tensorino fixed-point lift and do not
pretend to be a complete local polynomial. The normal-bundle `SO(2)` anomaly,
localized tensor transformations, effective dyonic-string cone, string
worldsheet anomaly/central-charge tests, and orbifold action on strings remain
unspecified. The connected bulk bordism result does not cover these defects or
the residual discrete R group.

## Fail-closed decision

Route C advances beyond integrated I8 and is rejected for the existing action by an exact fixed-point invariant-ratio certificate.  The result is stronger than a mere missing-data verdict, while the normal-bundle, string-worldsheet, and faithful residual-Z4R sectors remain explicit data deficits rather than assumed passes.

The smallest repair is not a coupling retuning: add explicitly quantized
localized subgroup-specific GS data or anomaly-canceling non-singlet matter,
then recompute the complete integrated and local theory. Alternatively change
the Higgs parity topology and restart the bulk spectrum/lattice problem.

## Primary sources

- [Bulk and Brane Anomalies in Six Dimensions](https://arxiv.org/abs/hep-ph/0209144): four-fixed-point parity trace formula and the SO(10) projector
- [Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0305024): conditions and restricted tensor mechanisms for localized inflow
- [Anomalies on Six Dimensional Orbifolds](https://arxiv.org/abs/hep-th/0612212): fixed-point gauge and normal-bundle/local-Lorentz anomaly obligations
- [Diagonally gauged anomaly-free 6D supergravities and their vacua](https://arxiv.org/abs/2607.21311): U(1)_R+ anomaly polynomial, lattice normalization, action, and moment-map vacua
- [Quantization of anomaly coefficients in 6D N=(1,0) supergravity](https://arxiv.org/abs/1711.04777): string-charge lattice and global-form quantization
- [Global anomalies in 6D gauged supergravities](https://arxiv.org/abs/2507.22127): connected-group bordism and gauged-R global consistency
- [On the consistency of a class of R-symmetry gauged 6D N=(1,0) supergravities](https://arxiv.org/abs/2002.04619): dyonic-string existence and worldsheet-inflow caveats for gauged R symmetry

Core SHA-256: `27b4e032ff10065b534c1c62c2adf88f677b07c228f243b5376227fdb307ac8d`
