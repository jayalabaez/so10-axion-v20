# V45 reconciled bulk-spinor audit

Status: `V45_FOUR_BULK_SPINORS_CANCEL_LOCAL_ORDINARY_ANOMALIES__SOURCE_THETA_MASSES_LOCAL_AND_ZERO_MODE_RANK4__NO_SINGLET_SHINING_HYPERS_OR_ORDINARY_CS_REQUIRED__GLOBAL_ETA_AND_FULL_KK_OPEN`

## Result

The four quotient-valid exotic multiplets can be realized as zero modes of the
four bulk hypers `16_+3`, `bar16_-12`, `16_-3`, and `bar16_+12`.  This single
choice resolves the apparent conflict between the group/zero-mode audit and the
wall/locality audit: the same bulk spinors both supply the PS zero modes and have
even fields at the full-Spin(10) wall.  Consequently the two Theta mass operators
are local boundary operators.  Separate singlet `B+/-` shining hypers are not
needed.

## Local anomaly formula

On the physical interval, normalize each endpoint delta function to integrate to
one.  For a bulk hyper written as a left-chiral `H` plus conjugate `Hc`,

`I6_f = (1/2) sum_alpha p_f(alpha) I6_4D(R_alpha,q)`,

where `p_f=+1` when `H` is even and `p_f=-1` when `Hc` is even.  A boundary
chiral contributes one full `I6_4D`.  This is the identified-wall version of the
fixed-point anomaly derived for `S1/(Z2 x Z2')`.

## Pati-Salam wall

In the row order `(SU4^2-F, SU2L^2-F, SU2R^2-F, grav-F, F^3, SU4^3)`, the
boundary fields `3Q+3Qc+H` give

`(0, 36, -36, 0, 0, 0)`.

The parity-weighted four bulk hypers give

`(0, -36, 36, 0, 0, 0)`.

Their wall-local sum is exactly

`(0, 0, 0, 0, 0, 0)`.

The cancellation is not merely integrated over the fifth dimension; it occurs at
the PS endpoint.

## Full-Spin(10) wall

All four `H` chirals have positive source-wall parity.  Each therefore deposits
one half of its full-representation anomaly there.  In the row order
`(Spin10^2-F, grav-F, F^3, Spin10^3)`, their total is

`(0, 0, 0, 0)`.

`ThetaPlus+ThetaMinus+STheta+126+bar126` contributes

`(0, 0, 0, 0)`,

so the source-wall total is

`(0, 0, 0, 0)`.

Thus no ordinary Chern-Simons inflow or extra chiral matter is required for the
displayed perturbative rows.

## Local source masses and zero-mode rank

The allowed source operators are

- `delta(y-L) lambdaL ThetaPlus HLF HLA`, and
- `delta(y-L) lambdaR ThetaMinus HRA HRF`.

After the Theta VEVs they induce `mL LF LA + mR RA RF`, with
`mL=lambdaL <ThetaPlus> fLF(L)fLA(L)` and similarly for `mR`.  In the basis
`(LF,LA,RA,RF)` the symmetric chiral mass matrix has two off-diagonal `2x2`
blocks, determinant `mL^2 mR^2`, and rank four whenever both overlaps are
nonzero.  Hence all four exotic zero modes are lifted.  Bulk localization may
make these masses exponentially small, but it does not make them vanish at
finite localization.

## What remains open

This closes the ordinary localized-anomaly ledger and the projected zero-mode
mass rank, not S0 or any G gate.  The full boundary-condition-shifted KK
determinant, eta/global anomaly, compact charge lattice and CS quantization,
cross-wall Wilson coefficients, and complete `126+bar126` vacuum/mass problem
remain kill tests.

Primary formulas and precedents: [Scrucca et al.](https://arxiv.org/abs/hep-th/0110073),
[von Gersdorff and Quiros](https://arxiv.org/abs/hep-th/0305024), and
[Alciati et al.](https://arxiv.org/abs/hep-ph/0603086).

Core SHA-256: `2d1e67bff06482fbb6b6e26b3153f8c49e6cd802d07f38e6de2a3505003888d7`
