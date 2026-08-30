# V45 wall-local anomaly and exotic-mass audit

Status: `V45_5D_WALL_ANOMALIES_ZERO_AT_THE_DECLARED_FIELD_LEVEL__V44_LONE_DOUBLETS_INVALID_FOR_PS_DIAGONAL_Z2_QUOTIENT__THETA_MASSES_NONLOCAL__QUOTIENT_VALID_BULK_MEDIATOR_REPAIR_PREREGISTERED__ZERO_GATES_PROMOTED`

## Exact result

At the Lie-algebra level, the displayed V44 boundary spectrum is locally
anomaly-free.  In the V40 doubled-index convention, the PS-wall totals are

`U1F-SU4^2=0`,
`U1F-SU2L^2=0`,
`U1F-SU2R^2=0`,
`U1F-gravity=0`, and
`U1F^3=0`.

The source-wall totals are `U1F-Spin10^2=0`,
`U1F-gravity=0`, and `U1F^3=0`.
The source `126+bar126` is neutral and vectorlike.  The PS pure-gauge result is
`SU4^3=0`; the SU(2)
Witten doublet counts are
`(30,
30)`, both even.

## Decisive global-group failure

The arithmetic pass is not enough.  V44 declares
`(SU4 x SU2L x SU2R)/Z2_diag`, whose identified center element is
`(-I4,-I2L,-I2R)`.  A lone `(1,2,1)` or `(1,1,2)` has character `-1` under
that element and is not a representation of the quotient.  Therefore
`L0, Lminus9, R0, Rplus9` make the provisional partition globally ill-defined.  This is a
fatal defect of the partition *as written*, not a no-go theorem for 5D
Spin(10).

## Loss of the heavy anomalon thresholds

All five V40 mass structures place Theta and its anomalon pair on opposite
walls.  They are absent from a local 5D action.  Neutral PS-wall VEVs cannot
repair their charge mismatch, and the old intended mass matrices have rank
zero.  Optional local `L0 L0` and `R0 R0` antisymmetric masses and the rank-one
`NDirac E3` mixing still leave at least thirteen anomalon multiplets without a
high-scale mass.  Inflow cannot generate those masses.

## Quotient-valid repair packet

Replace the invalid lone doublets by

- `(4,2,1)_+3 + (bar4,2,1)_-12`, and
- `(bar4,1,2)_-3 + (4,1,2)_+12`.

Every new representation descends to the quotient.  The replacement totals
remain `U1F-SU4^2=0`,
`U1F-SU2L^2=0`,
`U1F-SU2R^2=0`,
`gravity=0`, `cubic=0`;
`SU4^3=0` and the Witten counts remain `(30,30)`.

More generally, charges `(a,-9-a)` and `(c,9-c)` preserve the mixed and
gravity rows.  Cubic cancellation requires
`(a+c)(c-a-9)=0`; the displayed packet takes `a=3,c=-3`.  Modulo nine,
every fundamental is still `+3` and every antifundamental is `-3`, so the
residual orientation congruence survives.  This is not the stronger V44
all-order theorem: the first exact charge-and-center solution with nonzero
orientation occurs at degree 20, and the explicit PS invariant
`[epsilon4 epsilon2 epsilon2 Q1 Q2 Q3 LF]^3
[delta4 epsilon2 LA LF]^4` realizes it.  Thus the preferred packet protects
this arithmetic only through degree 19 unless another local selector is
added.  The anomaly-free `0/+-9` first attempt is rejected because its
nontrivial SU(4) fields would be residual-neutral and permit lower-degree
oriented classes.

## Selected reduced V45 core

The coherent field-level successor now discards the entire old host/PQ/E/lone
doublet structure.  Its PS wall contains only three-family
`Q(4,2,1)_+3`, `Qc(bar4,1,2)_-3`, `H(1,2,2)_0`, and
`LF(4,2,1)_+3 + LA(bar4,2,1)_-12 +
RA(bar4,1,2)_-3 + RF(4,1,2)_+12`.  The source wall retains only
`STheta,ThetaPlus,ThetaMinus` and the neutral `126+bar126` pair.

For this reduced core every displayed mixed, gravitational and cubic U(1)F
row is zero; `SU4^3=0`; the Witten counts are `(22,22)`; and every PS field
descends to the diagonal-Z2 quotient.  It is therefore promoted as the one
field-level V45 core to instantiate.  It is not yet a 5D model: its two heavy
exotic masses remain cross-wall operators, the neutrino Majorana sector was
dropped, and the boundary Higgs, KK, global-anomaly and physical matching
packets do not exist.

There is also a normalization correction.  Every displayed nonzero U(1)F
charge, including the proposed bulk transport charges, has gcd three.  In
primitive displayed units the charges are
`Q=LF=+1`, `Qc=RA=-1`, `LA=-4`, `RF=+4`, and `ThetaPlus/Minus=+/-3`.
Thus the faithfully acting residual selector on the displayed fields is Z3,
not Z9; it still forbids `Q^4`.  A genuine Z9 requires a specified compact
character/line lattice containing unit charge in the old normalization.  V44
did not provide that global datum.

Two Spin(10)-singlet bulk hypers of charges `+9` and `-9`, with opposite
chirals even on opposite walls, can in principle transmit both Theta VEVs.
In the standard half-anomaly convention their localized linear and cubic
rows cancel pairwise on each wall, so no CS inflow is required for this
specific transport pair.  The boundary Green function, parities, KK
determinants, eta/global anomaly and generated nonlocal baryon operators are
still missing.  Consequently this is a concrete next candidate, not a gate
closure.

Core SHA-256: `3b7294a7ae0ff89234890020a754d7447ebb507fc5f40190fc686eb664a2c21a`
