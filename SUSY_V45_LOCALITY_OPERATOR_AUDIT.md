# V45 reduced-core locality and operator audit

Status: `V45_REDUCED_SPINORIAL_CORE_LOCALITY_AUDITED__DEGREE20_ORIENTED_INVARIANT_CONFIRMED_BUT_Z4R_EXCLUDES_IT_FROM_W__FIRST_LOCAL_ORIENTED_W_DEGREE23__PURE_LIGHT_NONLOCAL_CHARGE_FLOW_REQUIRES_FOUR_SOURCE_UNITS__G7_OPEN`

## Authoritative verdict

The reduced V45 core uses the four bulk Spin(10) spinor hypers themselves to
carry the anomalons to the source wall.  Separate `Bplus/Bminus` singlet
shining hypers are unnecessary and are rejected.  The authoritative field
content is only three `Q/Qc` families, `H`, and

`LF(4,2,1)_3 + LA(bar4,2,1)_-12 +
 RA(bar4,1,2)_-3 + RF(4,1,2)_12`.

This audit proves a real orientation bound, but closes **0/8** full gates.

## Exact local orientation frontier

Write every oriented charge as `q_F=3s+9t`, with `s=+1` on a 4 and `s=-1`
on a bar4.  A PS invariant has `Delta=n4-nbar4=4k`; U1F neutrality gives

`12k+9T=0`, hence `k=3 ell`.

The first nonzero orientation is therefore 12.  Exhaustive aggregate integer
search finds no PS/U1F invariant through degree
19; the first occurs at degree
20.

Define

- `A = epsilon4 epsilon2 epsilon2 Q1 Q2 Q3 LF`, with charge +12;
- `B = delta4 epsilon2 LA LF`, with charge -9.

Then `A^3 B^4` is a nonzero degree-20 local
PS/U1F invariant with net orientation +12; the barred construction gives -12.
This independently confirms the wall audit's degree-20 witness.

There is an important correction: all 20 spinorial factors have `Z4R=1`, so
the invariant has `Z4R=0`, **not** the superpotential value 2.  It is not a W
term if Z4R is exact.  The first local oriented W solution occurs at degree
23; an explicit witness is
`A^3 B^4 (Q1 H Qc1)`.

## Complete renormalizable PS-wall W

There are 17 family-resolved terms and no linear or quadratic
terms:

| Operator | U1F | Z4R |
|---|---:|---:|
| `Q1 Qc1 H` | 0 | 2 |
| `Q1 Qc2 H` | 0 | 2 |
| `Q1 Qc3 H` | 0 | 2 |
| `Q1 H RA` | 0 | 2 |
| `Q2 Qc1 H` | 0 | 2 |
| `Q2 Qc2 H` | 0 | 2 |
| `Q2 Qc3 H` | 0 | 2 |
| `Q2 H RA` | 0 | 2 |
| `Q3 Qc1 H` | 0 | 2 |
| `Q3 Qc2 H` | 0 | 2 |
| `Q3 Qc3 H` | 0 | 2 |
| `Q3 H RA` | 0 | 2 |
| `Qc1 H LF` | 0 | 2 |
| `Qc2 H LF` | 0 | 2 |
| `Qc3 H LF` | 0 | 2 |
| `H LF RA` | 0 | 2 |
| `H LA RF` | 0 | 2 |

Equivalently, the wall contains a generic `4x4` Yukawa
`Y_AB L_A H R_B`, where
`L_A=(Q1,Q2,Q3,LF)` and `R_B=(Qc1,Qc2,Qc3,RA)`, plus `LA H RF`.
Fourth/mirror mixing is therefore allowed already at dimension three.  The
source-wall masses select the bulk pairs, but the resulting three-family
Yukawa must be obtained from the KK reduction rather than by naming fields.

There is no neutral R-charge-two driver on the PS wall.  `H H` has `Z4R=0`,
so this core does not yet generate a mu term.

## Source masses without singlet shining hypers

The required full-Spin10 source terms are

- `ThetaPlus 16_(+3) bar16_(-12)`;
- `ThetaMinus 16_(-3) bar16_(+12)`.

They contain `ThetaPlus LF LA` and `ThetaMinus RA RF` for the selected zero
modes.  Because these fields already propagate in the bulk, no additional
singlet transporter is needed.

This simplification creates a sharper open calculation, not a closure.  The
source also permits, at the gauge/U1F level,
`16_(+3)16_(-3)bar126` and
`bar16_(-12)bar16_(+12)126`.  Their Z4R status, Clebsches and effect of the
aligned 126 VEV cannot be decided until the boundary-Higgs R assignments and
parities are supplied.  The full parity-resolved KK mass determinant is absent.

## Four-source-unit theorem is not an exponential theorem

For a pure-light nonlocal oriented class the source supplies charge only in
units of nine.  Thus `12k+9m=0` gives the minimum
`|Delta|=12`, `|m|=4`.  Schematically the first charge-compatible class is
`ThetaMinus^4 (epsilon Q^4)^3 (Q H Qc)` and its conjugate.

This is a charge-flow/insertion lower bound.  It does **not** prove four
independent factors of `exp(-ML)`: integrating out bulk spinors whose masses
are proportional to Theta can produce inverse powers of Theta, and a KK Green
function can correlate insertions.  Only regulated matching can determine the
coefficient.

All displayed charges have gcd three, so local particles faithfully see Z3
after the charge-nine VEV.  A genuine Z9 additionally requires the unit-charge
line lattice specified by the S0 construction; the orientation arithmetic is
unchanged.

## Why the redundant B option is rejected

Adding separate charge-nine singlet hypers would allow the lower local W
classes `Bminus^3 (epsilon Q^4)^3 (LF LA)` at degree 17 and
`Bminus^4 (epsilon Q^4)^3 (Q H Qc)` at degree 19, plus conjugates.  Since the
spinorial anomalons already propagate across the interval, those hypers add
operator hazards without solving a missing transport problem.

## G7 remains open

The positive result is exact: the reduced local matter ring has no nonzero
orientation invariant through degree 19, and Z4R postpones its first local W
term to degree 23.  This does not classify orientation-zero B/L operators,
Kähler terms, broken-gauge/KK exchange, global selection rules, or physical
proton and multinucleon Wilson bounds.  The nonlocal four-unit bound also lacks
a coefficient.  Therefore G7 is not closed.

## Next required outputs

1. Parity-resolved localized anomaly polynomial for every component of the four bulk spinor hypers.
2. Full source-boundary 126/Theta/spinor superpotential, R charges, Clebsches and coupled F/D solution.
3. KK-plus-boundary determinant proving LF/LA and RA/RF are lifted with no extra zero mode.
4. Three-family Yukawa matching after integrating the fourth/mirror bulk spinors.
5. Complete orientation-zero B/L ring and regulated local/nonlocal/gauge/KK Wilson coefficients.

Primary formal anchors are the 5D N=1-superfield construction of
[Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256), explicit generation of
nonlocal interactions by bulk fields
([Scrucca--Serone--Silvestrini](https://arxiv.org/abs/hep-ph/0304220)), and the
localized-anomaly constraints of
[von Gersdorff--Quiros](https://arxiv.org/abs/hep-th/0305024).

Core SHA-256: `02b0d8a6c9fba5b6acb15b9de85dcf4383948b325c6ebcb727c525290795325b`
