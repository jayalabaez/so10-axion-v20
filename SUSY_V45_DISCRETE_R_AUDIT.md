# V45 discrete-R audit

Status: `V45_INTEGRATED_DISCRETE_R_CANDIDATES_EXIST__EQUAL_LEVEL_PS_UNIVERSALITY_FORCES_THE_DEGREE20_ORIENTED_W_OPERATOR__NO_SYMMETRY_PRESERVING_MASSIVE_PACKET_REPAIR__LOCALIZED_GLOBAL_COMPLETION_OPEN`

## Result

The inherited assignment (all spinorial superfields charge one, `H=0`,
`Theta+=Theta-=0`) is **not** a completed `Z4R`: its conventional mixed
Pati--Salam residues are
`{'SU4': 0, 'SU2L': 1, 'SU2R': 1}` at `eta=2`, so they are not
universal.

Alternative integrated candidates do exist.  With neutral Theta and 126
VEVs, an `SDelta` charge-two driver, a forbidden bare `H H`, and the displayed
four-dimensional spectrum, the exact no-GS scan through order 96 finds
orders `[3, 5, 6, 10, 15, 30]`.
For example, `Z5R` with

`Q=Qc=A16=C16=2`, `H=3`, `Bbar16=Dbar16=0`

has mixed rows `{'SU4': -60, 'SU2L': -60, 'SU2R': -60}` and gravity row
`-195`, all zero modulo `eta=5`.  The minimal even
screen is the `Z6R` odd-spinor/even-H pattern, with residues
`{'SU4': 0, 'SU2L': 0, 'SU2R': 0}`.  These are necessary
integrated screens, not five-dimensional anomaly certificates.

## Exact degree-20 no-go

Let the family-universal charges be `q,qc,h`, let `t=r(ThetaPlus)` and
`r(ThetaMinus)=-t`, and write the four bulk-spinor charges as `a,b,c,d`.
The required terms imply, modulo `N`,

`q+qc+h=2`, `a+b+t=2`, `c+d-t=2`.

In doubled-index normalization, up to any common complete-Spin(10) shift
`C`,

`A4=8-6h+C`,
`A2L=12q+2h-10-4t+C`,
`A2R=12qc+2h-10+4t+C`.

Equal-level anomaly universality is imposed modulo `2 eta`.  The two
differences give

`18-8h-12q+4t=0`,
`-6+4h+12q-4t=0`.

Their sum gives `12-4h=0`; substitution then gives

`12q+6-4t=0 mod 2 eta`, and therefore modulo `N`.

Now define the nonzero quartic

`P_Q = eps4 eps2 eps2 Q1 Q1 Q2 Q2`.

It evaluates to `4`
on the explicit unit-column field point stored in the audit.  Therefore

`O+ = P_Q^3 (LF LA)^4`

is a nonzero local PS singlet of degree 20, exact `U(1)_F` charge zero and
orientation `+12`.  Its R charge is forced to

`12q+4(a+b)=12q+8-4t=2 mod N`.

The conjugate `O- = P_Qc^3 (RA RF)^4` is forced in the same way.  This proof
does **not** assume `h=0`, and a neutral 126 pair cannot change it because its
mixed-anomaly shift is common to all three PS factors.

Thus no family-universal, equal-level, single-residue `Z_N^R` on the current
field core can both satisfy the required terms and forbid the first oriented
degree-20 local superpotential invariant.

## Why a massive matter patch does not fix it

For a complex vectorlike pair, an exact-R mass requires
`r_X+r_Xbar=2 mod N`.  Its mixed anomaly is then
`T(R)[(r_X-1)+(r_Xbar-1)]=0 mod eta`.  The analogous determinant statement
holds for real or pseudoreal mass blocks.  Consequently, an ordinary
symmetry-preserving massive PS packet cannot alter the congruence responsible
for the no-go.  A chiral light packet, an R-breaking threshold, or a
nonuniversal localized GS/topological sector would be new physics, but none is
an instantiated solution here.

## Fail-closed boundary

No candidate is promoted to an exact 5D symmetry.  The parity-resolved local
anomaly density, quantized inflow/KK eta invariant, full gravity/radion
spectrum, and `Spin^Z_N` bordism class for the actual PS quotient remain
uncomputed.  No G1 or G7 gate is closed.

Conventions and microscopic caveats follow
[Lee et al.](https://arxiv.org/abs/1102.3595),
[Dine--Monteux](https://arxiv.org/abs/1212.4371), localized-orbifold anomaly
constraints follow [von Gersdorff--Quiros](https://arxiv.org/abs/hep-th/0305024),
and the global inflow caveat follows
[Witten--Yonekura](https://arxiv.org/abs/1909.08775).

Core SHA-256: `4a214e7f34ae2d9fc6b8d16b5aefd990ee6a886b26aaac380e421500171f83e1`
