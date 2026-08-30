# V48 fixed-order source operator and cross-wall Wilson audit

Status: `V48_FIXED_ORDER_SOURCE_PORTAL_BASIS_COMPLETE__FINITE_SELF_ADJOINT_COLLAR_MAP_EXACT__FULL_FOUR_SPINOR_CROSS_WALL_WILSON_KERNEL_MATCHED__NO_FINITE_SELECTOR_REQUIRED_FOR_DECLARED_WILSONIAN_EFT__ALL_ORDER_UV_COEFFICIENT_PREDICTION_AND_PHYSICAL_GATES_OPEN`

## Verdict

The retained V47 source wall now has a complete **scoped fixed-order
Wilsonian** definition for the renormalizable action and the first
two-bulk-trace portal order.  In the 4D-normalized boundary-trace scheme there are
16 raw holomorphic structures through
degree three including the constant, or
14 nonconstant
coefficients after the allowed affine `S` shift.  The complete leading
two-bulk-trace degree-four portal sector has 12 independent
SO(10) contractions.  Leading localized kinetic, neutral-source kinetic,
210-kinetic, two independent U(1)F FI data, gauge-kinetic and
normal-derivative responses are also declared.

This is not an all-order or regulator-independent dimension-five basis claim.
The matching action is defined at `Lambda`, modulo IBP, leading equations of
motion and the `S` shift.  Pure-source quartics belong to the G3 vacuum
functional; two-bulk-trace degree-five terms are the next portal remainder.

## Complete renormalizable source-wall basis

| Degree | Operator | SO(10) contraction | qF |
|---:|---|---|---:|
| 0 | `W0` | `1` | 0 |
| 1 | `f1 S` | `1` | 0 |
| 2 | `f2 S^2/2` | `1` | 0 |
| 2 | `muTheta ThetaPlus ThetaMinus` | `1` | 0 |
| 2 | `m Phi^2/2` | `210x210->1` | 0 |
| 2 | `M Sigma barSigma` | `126xbar126->1` | 0 |
| 3 | `f3 S^3/3` | `1` | 0 |
| 3 | `kappa S ThetaPlus ThetaMinus` | `1` | 0 |
| 3 | `m1 S Phi^2/2` | `210x210->1` | 0 |
| 3 | `M1 S Sigma barSigma` | `126xbar126->1` | 0 |
| 3 | `lambda Phi^3/3` | `210^3->1` | 0 |
| 3 | `eta Phi Sigma barSigma` | `210x126xbar126->1` | 0 |
| 3 | `tL ThetaPlus A B` | `16xbar16->1` | 0 |
| 3 | `tR ThetaMinus C D` | `16xbar16->1` | 0 |
| 3 | `s16 barSigma A C` | `16x16->126` | 0 |
| 3 | `sbar16 Sigma B D` | `bar16xbar16->bar126` | 0 |

When `kappa!=0`, `S -> S-muTheta/kappa` removes the displayed quadratic
`ThetaPlus ThetaMinus` coefficient and redefines the other neutral
coefficients.  It is a coordinate choice, not a selection rule.

## Leading two-bulk-trace portal basis

| Operator | SO(10) channel | qF |
|---|---|---:|
| `S ThetaPlus (A B)_1` | `1` | 0 |
| `ThetaPlus Phi (A B)_210` | `210` | 0 |
| `S ThetaMinus (C D)_1` | `1` | 0 |
| `ThetaMinus Phi (C D)_210` | `210` | 0 |
| `S barSigma (A C)_126` | `126` | 0 |
| `Phi barSigma (A C)_10` | `10` | 0 |
| `Phi barSigma (A C)_120` | `120` | 0 |
| `Phi barSigma (A C)_126` | `126` | 0 |
| `S Sigma (B D)_bar126` | `bar126` | 0 |
| `Phi Sigma (B D)_10` | `10` | 0 |
| `Phi Sigma (B D)_120` | `120` | 0 |
| `Phi Sigma (B D)_bar126` | `bar126` | 0 |

The three `Phi barSigma A C` and three conjugate contractions are distinct:
`16 x 16 = 10_s + 120_a + 126_s`.  Since `A,C` and `B,D` are distinct
hypermultiplets, the 120 channels do not vanish.

## Why no new finite selector is needed

At fixed order every displayed coefficient is ordinary matching data.  The
V47 zero theorem needs only finite nonzero Theta even-even blocks and is valid
for arbitrary finite Sigma mixing, so this audit does not set an allowed
coefficient unnaturally to zero.

An all-order sparse action is impossible in the declared field content:
`ThetaPlus ThetaMinus`, `S`, `Phi^2` and `Sigma barSigma` are neutral and can
dress allowed portals indefinitely.  A finite symmetry labels operators; it
does not calculate their coefficients.  Any later need for a small coefficient
must be justified by UV matching, locality or a new symmetry.

## Resolved collar and induced terms

For a Hermitian Nambu source matrix `A`, choose a square collar of width
`epsilon` with

`epsilon G=[[0,epsilon m I],[A-epsilon m I,0]]`.

Writing its exact transfer as `[[D,U],[C,D]]`, the inner boundary condition is

`g+B_epsilon(m)f=0`, `B_epsilon=D^-1 C`.

The exact zero-energy map and derivative expansion are

`B_epsilon(0)=A`,

`B_epsilon=A-epsilon m(I+A^2/3)+epsilon^2 m^2(2A/3+2A^3/15)+...`.

Thus the regulator supplies the kinetic/wrong-chirality response that a bare
delta coefficient alone does not define.  The complete collar is
self-adjoint; poles of `D` are retained as wall states rather than divided
away.

The renormalization conditions are imposed at `mu=Lambda` on `B_R(0)`, its
first momentum derivative, both wall metrics, both FI coefficients and all
boundary gauge couplings.  The declared NDA domain is `Lambda L>>1`,
`Lambda epsilon>=1`, `p/Lambda<1`, source backgrounds below `Lambda`, positive
Kähler/gauge metrics and `g5^2 Lambda/(24 pi^3)<1`.  The benchmark uses
`Lambda L=20`, `epsilon=1/Lambda` and `p_max/Lambda=0.4`.

## Complete PS-wall current census

The earlier 17-term zero-mode census is not the complete boundary-trace
census.  The conjugate hypermultiplet traces even at the PS wall also allow

`HRAc_L H HLFc_R` and `HRFc_L H HLAc_R`.

The fixed-order PS superpotential therefore has 19 coefficients: nine local
`Q_i H Qc_j`, six one-bulk current vertices, `LF H RA`, `LA H RF`, and the two
complementary-trace cubics.  Its Kähler action contains arbitrary positive
Hermitian 4x4 matrices for `(Q_i,LF)` and `(Qc_i,RA)`, explicitly including
`Q_i^dagger LF` and `Qc_i^dagger RA`.  The four complementary even traces
`HLFc_R`, `HLAc_R`, `HRAc_L`, and `HRFc_L` each have an independent positive
boundary metric.  Constant PS gauge kinetic terms, the PS-wall U1F FI datum
and the allowed broken-generator `Tr Zhat^2` term are declared as independent
matching coefficients.

## Exact cross-wall Wilson matching

For the full four-spinor V47 matrix, introduce both allowed initial data

`f(0)=Ea-Ob`, `g(0)=Oa+Eb`,

so that `f(L)=Ra+Pb`, `g(L)=Qa+Tb`.  The undivided resolved-wall matrices are

`K_reg=CR+DQ`, `N_reg=CP+DT`.

The source wall has no independent operator linear in one bulk spinor, so a
formal source current is not the actual matching problem.  Instead the PS wall
sets

`b=J_0+V_0(H)a`,

where `J_A=H sum_j Y_4j Qc_j`, `J_C=H sum_i Y_i4 Q_i`, and `V_0`
contains all four two-bulk Higgs vertices, including the complementary traces.
The exact physical host kernel is

`G_00=(K_reg+N_reg V_0)^-1 N_reg`,

and

`W_eff=-1/2 J_0^T G_00 J_0`.

For a source fluctuation `X` entering the four Theta/Sigma projectors, the
matched coefficient is

`delta_X W_eff=-1/2 J_0^T (partial_X G_00) J_0`.

The executable eight-coordinate left/right representative includes
`(A_L,B_L,Cc_L,Dc_L | Ac_R,Bc_R,C_R,D_R)`, all four Higgs vertices and all
four source projectors.  The other seven internal pairs follow by the stated
PS Clebsch contractions; the `H=0` V47 characteristic is unchanged.

For reference, the inner thin-wall characteristic is

`K(m)=(-mS+B F)E+(G+m B S)O`,

but every resolved result uses `K_reg`, not a divided `B_epsilon`.  Because
`K_reg^-1=adj(K_reg)/det(K_reg)`, every Wilson pole is a root of the complete
resolved signed KK characteristic; the matching introduces no spurious pole.

For Euclidean `m=ip`, the executable witness verifies exponential suppression
with momentum and wall separation.  It also verifies fixed-off-shell
decoupling as an invertible boundary matrix is scaled large.  That limit is
not uniform at a physical pole or at the distinct infinite-boundary spectral
flow endpoint.

## G2 decision

The fixed-order source/portal EFT subgate is **closed in the declared collar
scheme**: field content, operator coefficients, regulator, induced response
and the actual source-dependent PS-to-PS tree kernel are explicit and
replayable.  Unqualified G2 is left fail-closed until the integration audit
freezes that scoped Wilsonian definition.  If G2 instead demands a UV
prediction of the infinite neutral-dressing tower or a regulator-independent
distributional dimension-five basis, it remains open.  No claim about G3--G8
is promoted by this calculation.

Primary formal anchors are
[Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Nath--Syed](https://arxiv.org/abs/hep-th/0109116),
[Chen--Zhang--Bai](https://arxiv.org/abs/1707.00580),
[del Aguila--Perez-Victoria--Santiago](https://arxiv.org/abs/hep-th/0302023),
and [Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `9e036d222727fa114c986175d0866f2e530e13304c52bb7d9d1a9de9ecdd2d12`
