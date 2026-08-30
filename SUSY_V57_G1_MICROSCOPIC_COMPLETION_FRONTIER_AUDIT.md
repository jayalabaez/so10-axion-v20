# V57 G1 microscopic-completion frontier audit

Status: `V57_G1_MICROSCOPIC_COMPLETION_FRONTIER__SPIN10_T1_U_LATTICE_BULK_GS_CLOSED__ALL_CONTINUOUS_FIXED_POINT_GAUGE_ANOMALIES_ZERO__TRADITIONAL_GLOBAL_CHECKS_PASS__Z4R_CLASSICAL_AUTOMORPHISM_ONLY__DISCRETE_GAUGE_ORIGIN_LOCAL_DISCRETE_INFLOW_AND_NEUTRAL_ORBIFOLD_SECTOR_OPEN__G1_NOT_CLOSED__HETEROTIC_SPIN_LIFT_REDESIGN_SELECTED__ZERO_GATE_PROMOTIONS__COMPLETE_THEORY_FALSE`

## Result

**G1 remains OPEN. No G1--G8 gate is promoted.**

V57 nevertheless closes two substantial subsectors exactly:

1. the integrated six-dimensional `Spin(10)` bulk anomaly and quantized
   Green--Schwarz sector; and
2. every perturbative continuous gauge anomaly, plus the traditional Witten
   checks, at all four orbifold fixed points.

The remaining obstruction is not another ordinary anomaly sum. The declared
`Z4R` is a consistent classical automorphism, but no faithful microscopic
discrete-gauge realization, pointwise discrete/local-Lorentz anomaly ledger,
or quantized localized inflow action has been constructed. The required 269
neutral hypermultiplet dimensions also have no declared orbifold parities.

## Exact 6D bulk completion

With `tr=tr_10`, two same-chirality `10` hypermultiplets and the `45` vector give

```text
B_adj - 2 B_10 = 2 - 2 = 0
a.b = (2/6)(8 - 2) = 2
b^2 = -(4/3)(3 - 0) = -4
```

The minimal tensor choice is `T=1`. The complete
integrated chiral count is

```text
H = 20 charged + 269 neutral = 289
H - V + 29 T = 273 = 273
```

Choose the even unimodular hyperbolic plane

```text
Omega = [[0,1],[1,0]]       det(Omega) = -1
a = [-2, -2]                    a^2 = 8
b = [-2, 1]                     a.b = 2, b^2 = -4
j = (2,1/4)                 j^2 = 1, j.b = 3/2
```

`a` is characteristic because for every `x=(m,n)`, `x^2=2mn` and
`a.x=-2(m+n)` are equal modulo two. The factorized polynomial is

```text
I8 = (tr R^2 + 2 tr F^2)(tr R^2 - tr F^2)
   = (tr R^2)^2 + tr R^2 tr F^2 - 2 (tr F^2)^2.
```

This passes the declared `Spin(10)` global-form quantization and
`Omega_7^Spin(BSpin(10))=0`. Literal `SO(10)` needs an even `b` on the odd
unimodular `I_(1,1)` repair lattice, but it cannot carry the localized `16`
families and is therefore not the V57 global group.

## Continuous fixed-point ledger

| Fixed point | Compact local group | Continuous anomaly | Traditional global check |
|---|---|---:|---|
| O_SO10 | Spin(10) | ZERO | pi4(Spin(10))=0 |
| O_GG | (SU(5) x U(1)_X)/Z5 | ZERO | pi4(SU(5))=0; finite Z5 quotient adds no Witten test here |
| O_fl | (SU(5)' x U(1)'_X)/Z5 | ZERO | pi4(SU(5))=0 |
| O_PS | (SU(4)_C x SU(2)_L x SU(2)_R)/Z2 | ZERO | each (1,2,2) gives two doublets and (6,2,2) gives twelve; both SU(2) Witten counts are even |

At `O_GG`, the two bulk tens contribute opposite coefficient vectors
`(2,2,80,20)` and `(-2,-2,-80,-20)` for
`(SU5^3, SU5^2-X, X^3, grav^2-X)`. Each localized
`10_-1 + 5bar_3 + 1_-5` family is separately anomaly-free, and
`X_10 + Xbar_-10` is vectorlike.

## Why the discrete sector blocks G1

The low-energy necessary gauge residues are

```text
(A3^R, A2^R, 5 A1^R) = (3, 1, -3)
                         = (1,1,1) mod eta=2.
```

This is the universal Green--Schwarz pattern, not zero anomaly. For the stated
visible plus `X`, `Xbar`, `S`, and `U(1)_X` ledger,

```text
A_grav^R = -13 = 1 mod 2,
24 rho   = 24 = 0 mod 2.
```

An explicit dilaton/axion GS multiplet can repair the odd mismatch through its
axino, but V56 did not contain that microscopic field and did not quantize its
shift or local couplings. Also, with matter superfield charge one,
`r^2=(-1)^F` times matter parity; the symmetry is generically ordinary
`Spin x Z4`, not automatically `Spin^Z4`.

## Strict G1 matrix

| Criterion | Status | Evidence |
|---|---|---|
| compact_global_gauge_group_and_quotients | PASS | Spin(10) with (SU5xU1)/Z5 and PS/Z2 fixed-point global forms |
| integral_unimodular_string_charge_lattice | PASS_FOR_INTEGRATED_BULK | U lattice with characteristic a=(-2,-2), b=(-2,1) |
| complete_6D_chiral_supergravity_spectrum | PASS_FOR_INTEGRATED_BULK_ONLY | gravity + T=1 + Spin10 vector + 2x10 + 269 neutral hyper dimensions |
| all_integrated_6D_perturbative_anomalies | PASS | irreducible terms vanish and I8 factorizes on the quantized U lattice |
| connected_6D_global_gauge_gravity_anomaly | PASS_UNDER_DECLARED_ASSUMPTIONS | Omega_7^Spin(BSpin10)=0 plus unimodular lattice and characteristic a |
| continuous_fixed_point_gauge_and_traditional_global_anomalies | PASS | 4/4 fixed points pass exactly |
| orbifold_projection_of_complete_parent_spectrum | OPEN | 269 neutral hyper parities and localized tensor boundary conditions are unspecified |
| globally_gauged_Z4R_and_gravitational_residue | FAIL_OPEN | classical automorphism only; low-energy A_grav=-13 fails the required congruence without an explicit GS axino/dilatino |
| pointwise_discrete_R_local_Lorentz_and_quantized_inflow | OPEN | no four-fixed-point coefficient matrix or localized axion/tensor inflow action |
| torsion_global_anomaly_for_actual_Spin_x_Z4_group | OPEN | Dai-Freed/bordism invariant not computed |
| same_action_G1_closure | OPEN | every strict row must pass in one versioned action; three rows remain open and one fails/open |

## Redesign decision

| Route | Decision | Exact role |
|---|---|---|
| R1_MINIMAL_SPIN10_T1_U_GS_PARENT | ACCEPTED_EXACT_BULK_SUBSECTOR | closes irreducible, reducible, gravitational, lattice, and connected global 6D bulk anomalies |
| R2_LITERAL_SO10_I11_PARENT | REJECTED_FOR_V56 | mathematically repairs the stronger SO(10) cocharacter quantization condition |
| R3_BOTTOM_UP_GAUGED_U1R_TO_Z4R | NOT_SELECTED | requires a substantially new gauged 6D R-supergravity spectrum, vacuum, flux, and anomaly lattice |
| R4_HETEROTIC_SPIN_LIFT_MIXED_Z4R | SELECTED_UV_REDESIGN_TARGET_NOT_YET_CONSTRUCTED | derive Z4R from the spin lift of a T2/Z2 orbifold plane mixed with space-group and gauge symmetries; retain the universal dilaton GS multiplet |

The selected redesign target is a heterotic spin-lift/mixed-symmetry origin for
`Z4R`, including the universal dilaton GS multiplet. Published string vacua
show that this mechanism can exist, but they are not the V56 action. The cited
semi-realistic witness also retains an extra `Z2` and rank-two down/lepton
Yukawas. It is therefore a target to construct, not a closure certificate that
can be imported.

## Terminal decision

V57 makes the maximum exact same-line advance presently supported: the bulk Green--Schwarz parent and every continuous fixed-point gauge anomaly are closed. G1 itself remains open because the proposed Z4R is only a classical automorphism, its necessary gravitational residue fails without an explicit GS multiplet, and no quantized pointwise discrete/local-Lorentz inflow or complete neutral orbifold spectrum exists. A heterotic spin-lift embedding is a viable redesign, but importing a published different string vacuum would violate the one-action rule.

- New physics created: **yes**, an exact quantized 6D bulk parent layer.
- Integrated 6D bulk G1 subsector closed: **yes**.
- Continuous fixed-point gauge anomaly subsector closed: **yes**.
- Full same-action G1 closed: **no**.
- Complete theory: **no**.
- Empirical discovery: **no**.

## Primary sources

- [Anomaly Constraints and String/F-theory Geometry in 6D Quantum Gravity](https://arxiv.org/abs/1008.1062): 6D anomaly equations, group constants, and kinetic chamber
- [Quantization of anomaly coefficients in 6D N=(1,0) supergravity](https://arxiv.org/abs/1711.04777): integral string-charge and global-form quantization
- [Remarks on the Green-Schwarz terms of six-dimensional supergravity theories](https://arxiv.org/abs/1808.01334): unimodular lattice, characteristic a, and global GS conditions
- [Some comments on 6D global gauge anomalies](https://arxiv.org/abs/2012.11622): Spin/SO bordism computation
- [SO(10) Unified Theories in Six Dimensions](https://arxiv.org/abs/hep-ph/0108071): two-10 orbifold spectrum and parity architecture
- [Anomaly cancellation in six dimensions](https://arxiv.org/abs/hep-ph/0209144): parity-weighted localized anomaly formula
- [Localized anomalies in orbifold gauge theories](https://arxiv.org/abs/hep-th/0612212): localized gauge and internal-Lorentz anomaly obligations
- [A unique Z4R symmetry for the MSSM](https://arxiv.org/abs/1009.0905): discrete residues, GS axino repair, and string spin-lift existence witness
- [On the Anomaly of the Electromagnetic Duality of the Maxwell Theory](https://arxiv.org/abs/1808.02881): ordinary Z4 versus Spin-Z4 global-symmetry distinction
- [Supersymmetric Standard Model from the Heterotic String (II)](https://arxiv.org/abs/hep-th/0606187): explicit modular-invariant local-SO10 heterotic redesign precedent

Core SHA-256: `0896cc21d84d6395d6ba9d5c0b6414c3aec14c18981708d2e06b548a4fc21302`
