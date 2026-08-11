# Exact cubic Cauchy bridge for the Phi-zero problem

Status: `EXACT_PHI_ZERO_CUBIC_CAUCHY_BRIDGE__D_ZERO_OPEN`.

Let `A_Phi` be the four-form operator on two-forms and define

```text
I3 = tr(A_Phi^3),
U  = (1/3) grad I3.
```

The exact verifier proves globally

```text
<Phi,U> = I3,
||U||^2 = 90 p210.
```

The second identity is certified in the complete four-dimensional quartic
invariant space: four integral samples have a nonzero exact evaluation
determinant, and every exact sample gives zero residual. Cauchy--Schwarz
therefore gives

```text
I3^2 <= 90 N p210.
```

Coefficientwise in the same complete quartic basis, the verifier proves

```text
p210 = N^2/25 + D/15 + (44/15)p54 - (4/5)p4125,
D = (9/5)N^2-||*(Phi wedge Phi)||^2.
```

Hence on the common live-projector zero set,

```text
I3^2 <= (18/5)N^3 + 6ND.                              (1)
```

This closes the post-conductor scalar step. If a separate exact theorem
establishes `D=0`, then (1) says `5I3^2-18N^3<=0`, while the frozen global
sextic syzygy says

```text
5I3^2-18N^3 = (35/1536)S >= 0.
```

Thus `D=0` would force the sharp cubic equality and `S=0` immediately.

Scope is strict: this theorem does not establish the degree-eight conductor
`D=0`, the global signed-Kahler zero-locus classification, G3, or G4.
