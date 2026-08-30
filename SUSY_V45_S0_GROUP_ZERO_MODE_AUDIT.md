# SUSY V45 S0 group and zero-mode audit

Status: `V45_S0_CONNECTED_SM_INTERSECTION_CERTIFIED__V44_NAKED_PS_DOUBLETS_GLOBALLY_INVALID__MINIMAL_SPINORIAL_CORE_HAS_ZERO_INTEGRATED_ANOMALY_ROWS__Z2M_REMAINS_AND_Z9F_REQUIRES_UNIT_LINE_LATTICE__S0_FAIL_CLOSED`

Core SHA-256: `1329d333fee4d06ed7ac4ba47c613525ebf5e8593d9d797c96d070507933b732`

## Fail-closed verdict

The proposed **orbifold/boundary breaking pattern is group-theoretically viable**, but the
V44 field manifest is not.  The exact connected intersection is

`(SU(3)_C x SU(2)_L x U(1)_Y)/Z6`,

with 12 vector multiplets and rank four.  However, a Spin(10) parent fixes the PS wall
group to `(SU(4)xSU(2)LxSU(2)R)/Z2_diag`.  V44's isolated `(1,2,1)` and `(1,1,2)`
anomalons are not representations of this quotient.  The displayed spinorial repair fixes
that exact defect and preserves the integrated anomaly rows, but localized anomalies,
boundary-Higgs mass rank, and cross-wall matching remain uncomputed.  Therefore S0 is
**not closed**, and no G1--G8 gate is promoted.

There is one further precision point: for the explicit trivial bulk quotient and unit
Wilson-line lattice chosen here,
the full residual gauge group is

`[(SU(3)_C x SU(2)_L x U(1)_Y)/Z6] x Z2_M x Z9_F`.

Thus the result is exactly the connected SM global form plus the deliberately retained
matter parity and flavour selector.  It is not literally the SM with no finite extension.
All displayed local core charges have gcd three, however, so those local particles see
only a faithful `Z3`; the stronger `Z9` is a genuine global line-operator input rather
than a conclusion from the minimal particle list.

## Exact intersection certificate

Use the standard `D5` roots `±e_i±e_j`.  The PS roots are `D3` on coordinates
1--3 plus `D2` on coordinates 4--5; the SU(5) roots are `e_i-e_j` for all five
coordinates.  Their common roots are six `A2` roots on 1--3 and two `A1` roots
on 4--5.  The SU(5) Cartan has rank four, so one commuting Cartan direction
remains in addition to `A2+A1`:

- intersection roots: 8;
- semisimple rank: 3;
- total rank: 4;
- dimension: 12;
- primitive Abelian generator: `6Y=(-2,-2,-2,3,3)`.

The connected subgroup is `S(U(3)xU(2))`.  The map
`(A,B,z) -> diag(z^-2 A,z^3 B)` has a six-element kernel, proving the global
form `(SU(3)xSU(2)xU(1))/Z6`, not merely its Lie algebra.

## Orbifold and supersymmetry projection

Take `M4 x [0,L]`, with `L=pi R/2`, and choose the bulk group
`Spin(10)xU(1)_F` (trivial `Gamma`) for this witness.  At `y=0` use
`P0=diag(-1,-1,-1,+1,+1) tensor I2`; at `y=L` use `PL=I10`.

| sector | dim | P0 | PL | constant zero modes before brane VEVs |
|---|---:|:---:|:---:|---:|
| Spin10 vector V_PS | 21 | + | + | 21 |
| Spin10 vector V_coset (6,2,2) | 24 | - | + | 0 |
| adjoint chiral Phi_PS | 21 | - | - | 0 |
| adjoint chiral Phi_coset | 24 | + | - | 0 |
| U1F vector V_F | 1 | + | + | 1 |
| U1F adjoint chiral Phi_F | 1 | - | - | 0 |

Only `(++)` fields have constant zero modes.  Opposite parities for the adjoint
chiral field remove its zero mode, reducing the eight-supercharge 5D theory to
4D `N=1`.  The inner orbifold keeps the PS rank.  The aligned
`126+bar126` singlet VEV at the full-Spin(10) wall then lifts the nine
`PS/SM` vector modes through a boundary mass/Robin condition.  For finite VEV
these modes are lifted rather than deleted by parity.

## The 126 global stabilizer

`126` and `bar126` contain `SU(5)xU(1)_chi` singlets `1_-10` and `1_+10`.
An equal-norm conjugate pair can be D-flat and has connected stabilizer SU(5).
Globally the relevant maximal subgroup is `(SU(5)xU(1)_chi)/Z5`; the charge-ten
VEV gives `(SU(5)xZ10)/Z5`, which has two components.
Because 126 is tensorial, the central element `c^2` in the Spin(10) centre acts
trivially on the VEV while acting as `-1` on a 16.  The exact stabilizer is
therefore `SU(5)xZ2_M`.  This is the usual surviving matter parity.  A complete
superpotential that selects this orbit and gives every uneaten 126 mode a mass
has not been supplied.

## Global-representation defect in V44

The kernel element `(-I4,-I2,-I2)` must act trivially.  Equivalently,
`SU4 n-ality + 2j_L + 2j_R` must be even.

| field class | PS representation | kernel phase | honest? |
|---|---|:---:|:---:|
| Q/Psi | `(4,2,1)` | +1 | yes |
| Qc/PsiC | `(bar4,1,2)` | +1 | yes |
| H | `(1,2,2)` | +1 | yes |
| V44_L0/Lminus9 | `(1,2,1)` | -1 | NO |
| V44_R0/Rplus9 | `(1,1,2)` | -1 | NO |
| repair_L | `(4 or bar4,2,1)` | +1 | yes |
| repair_R | `(4 or bar4,1,2)` | +1 | yes |

This is a fatal contradiction for the **original manifest**, not for the 5D
architecture: boundary-localized fields cannot be assigned projective gauge
representations and still define the stated Spin(10) gauge theory.

## Globally honest spinorial repair

Replace the four-copy naked-doublet rows by four bulk hypermultiplets whose
orbifold zero modes are:

| Spin(10) hyper | selected PS zero mode | intrinsic `(eta0,etaL)` |
|---|---|:---:|
| `16_+3` | `(4,2,1)_+3` | (+,+) |
| `bar16_-12` | `(bar4,2,1)_-12` | (+,+) |
| `16_-3` | `(bar4,1,2)_-3` | (-,+) |
| `bar16_+12` | `(4,1,2)_+12` | (-,+) |

Here `16=(4,2,1)+(bar4,1,2)` and
`bar16=(bar4,2,1)+(4,1,2)`; opposite PS twist eigenvalues select one half of
each hyper, while the conjugate 4D chiral `Hc` has no zero mode.  On the
Spin(10) wall the terms

- `ThetaPlus(+9) 16_L(+3) bar16_L(-12)`, and
- `ThetaMinus(-9) 16_R(-3) bar16_R(+12)`

are Spin(10) singlets and U(1)_F neutral.  They can pair all four selected zero
modes after the Theta VEVs.  Their fundamental/antifundamental charges remain
`+3/-3 mod 9`.

| integrated anomaly row | old naked doublets | repaired spinorial modes |
|---|---:|---:|
| SU4_squared_U1F_doubled | 0 | 0 |
| SU2L_squared_U1F_doubled | -36 | -36 |
| SU2R_squared_U1F_doubled | 36 | 36 |
| gravity_squared_U1F | 0 | 0 |
| U1F_cubed | 0 | 0 |
| SU4_cubed | 0 | 0 |
| SU2L_Witten_doublet_count_mod2 | 0 | 0 |
| SU2R_Witten_doublet_count_mod2 | 0 | 0 |

The equality is exact for the combined anomalon packet.  It does **not** prove
wall-by-wall anomaly cancellation: charged bulk spinors have parity anomalies
and also reopen nonlocal propagation between the walls.

## Minimal V45 core, not the V40 packet

The repaired candidate keeps only three `Q_+3` families, three `Qc_-3`
families, `H_0`, and the four spinorial zero modes on/through the PS wall.  The
source wall keeps `STheta`, `ThetaPlus/ThetaMinus`, and the neutral
`126+bar126`.  The old `X/Zp/PQ/A/Psi/E/NDirac/Sc` sectors are deleted at this
core stage.  The full displayed core has the exact integrated anomaly ledger

`{'SU4_squared_U1F_doubled': 0, 'SU2L_squared_U1F_doubled': 0, 'SU2R_squared_U1F_doubled': 0, 'gravity_squared_U1F': 0, 'U1F_cubed': 0, 'SU4_cubed': 0, 'SU2L_Witten_doublet_count_mod2': 0, 'SU2R_Witten_doublet_count_mod2': 0}`,

so every listed perturbative mixed/cubic/gravitational row and both SU(2)
Witten parities vanish.  This is an integrated statement only; the anomaly
density at each wall remains the next kill test.

## Why S0 remains open

- The complete 126+bar126 boundary superpotential and all physical mass matrices are absent.
- Localized perturbative, parity, discrete and global anomalies of the four proposed bulk hypers are uncomputed.
- The bulk-hyper repair creates cross-wall propagation, so all dangerous nonlocal Wilson coefficients must be recomputed.
- The finite residual global group is SM_connected x Z2_M x Z9_F, not literally the connected SM alone.
- The minimal local field charges have gcd three; a genuine Z9 rather than faithful-local Z3 requires an explicit unit Wilson-line/charge lattice.
- Gauge-unification and KK-threshold viability of SO(10)-wall Higgs breaking are not established.

The next kill test is: Build the complete localized-anomaly polynomial for the vector multiplets and the four charged 16/bar16 hypers with the displayed parities.  Reject the repair if no quantized inflow and boundary spectrum cancel both wall distributions while retaining the two source-wall masses.

## Primary-source anchors

- [Dermisek and Mafi, SO(10) grand unification in five dimensions](https://arxiv.org/abs/hep-ph/0108139) — S1/(Z2 x Z2') parity construction, PS gauge zero modes, 4D N=1 projection, and SU5/PS intersection precedent.
- [Alciati and Lin, Gauge coupling Unification and SO(10) in 5D](https://arxiv.org/abs/hep-ph/0506130) — rank-preserving orbifold plus rank-reducing brane Higgs mechanism and the warning that SO10-wall Higgs breaking is disfavored for unification.
- [Alciati et al., Fermion masses and proton decay in a minimal five-dimensional SO(10) model](https://arxiv.org/abs/hep-ph/0603086) — bulk 16 hypermultiplets, doubled zero-mode constructions, PS decomposition of a 16, and boundary-mass-shifted KK towers.
- [Chen, Zhang and Bai, Couplings in Renormalizable Supersymmetric SO(10) Models](https://arxiv.org/abs/1707.00580) — the 126 and bar126 contain SU5 singlets of U1X charges -10 and +10.
- [Goh et al., Proton Decay in a Minimal SUSY SO(10) Model for Neutrino Mixings](https://arxiv.org/abs/hep-ph/0311330) — 126 breaking preserves automatic R/matter parity.
