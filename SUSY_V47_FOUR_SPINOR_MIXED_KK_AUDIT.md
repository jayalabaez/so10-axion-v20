# V47 four-spinor mixed KK audit

Status: `V47_FOUR_SPINOR_TRANSFER_CHARACTERISTIC_DERIVED__ZERO_NULLITY_CONTROLLED_ONLY_BY_SOURCE_EVEN_EVEN_BLOCK__THETA_PLUS_AND_MINUS_REMOVE_ALL_ZERO_MODES_WHILE_SIGMA_CROSS_BLOCKS_ONLY_SHIFT_TOWERS__HERMITIAN_EXTENSION_HAS_NO_TACHYONS__REGULATOR_THRESHOLDS_AND_GLOBAL_GATES_OPEN`

## Verdict

The exact four-hypermultiplet boundary problem can be solved without truncating
the KK tower.  For every finite, self-adjoint renormalized source matrix `B`,
the massless spectrum depends **only** on the block `B_EE=E B E` connecting
fields even at the PS wall.  Even--odd and odd--odd source masses can alter the
wavefunctions and every nonzero KK pole, but they cannot lift an exact chiral
zero mode.

Applied to V46/V47, the two Theta masses make `B_EE` full rank in all 16
Spin(10) component directions.  The allowed `barSigma HLF HRA` and
`Sigma HLA HRF` entries act only on the SU(5)-singlet component and are
even--odd there.  Consequently they create no additional zero and remove no
zero that would remain if a Theta block vanished.  With both Theta parameters
finite and nonzero, the enlarged idealized system has **zero exact KK zero
modes**.  This does not close S2 because the bare-brane matching and numerical
threshold spectrum remain open.

## Exact component projectors

The faithful primitive `U(1)F` charges are

`HLF,HLA,HRA,HRF,ThetaPlus,ThetaMinus = +1,-4,-1,+4,+3,-3`.

All four retained source operators are neutral in this normalization.  The
older labels `(+3,-12,-3,+12; +/-9)` are only a common-factor-three convention
and are not used in this V47 contract.

Use the internal spinor ordering

`(Q[6], L[2] | uC[3], dC[3], eC | nuC)`.

Then

`P_L=diag(1^8,0^8)`, `P_R=diag(0^8,1^8)`, and
`P_1=diag(0^15,1)`.

Separately, under `SU(5) x U(1)chi`, the SO(10) spinor decomposition is
`16=10_(chi=-1)+bar5_(chi=+3)+1_(chi=-5)`.  These subscripts are `U(1)chi`,
not `U(1)F`.  The final `nuC` entry is the `chi=-5` singlet and lies in the
PS-right half, so `P_1 P_R=P_1` and `rank(P_1)=1`.  The SU(5)-singlet 126 or
bar126 VEV therefore projects

- `barSigma HLF HRA` onto the `HLF_nuC--HRA_nuC` entry, and
- `Sigma HLA HRF` onto its conjugate `HLA_nuC--HRF_nuC` entry.

It vanishes on the other fifteen internal components.  This is stronger than
saying the direct selected-zero-mode projection vanishes: it specifies the
complete component operator that must enter the KK determinant.

## Renormalized boundary matrix

In channel order `(HLF,HLA,HRA,HRF)`, the Hermitian extension matrix is

```text
B = [[0,    tL,       s16 P1,       0],
     [tL*,  0,        0,       sbar16 P1],
     [s16*, 0,        0,            tR],
     [0,    sbar16*,  tR*,           0]] .
```

The four entries are renormalized boundary-extension parameters, not bare
delta coefficients.  In the real singlet component

`det B=(tL tR-s16 sbar16)^2`.

This determinant is **not** the zero-mode test when the PS-wall parities are
mixed.

## General transfer-matrix characteristic

Let `E` project H fields even at `y=0`, `O=1-E`, and let the real diagonal odd
bulk masses on `0<y<L` be `M_i`.  Define

`S_i=sin(k_iL)/k_i`, `F_i=cos(k_iL)-M_iS_i`,
`G_i=cos(k_iL)+M_iS_i`, with `k_i^2=m^2-M_i^2`.

The exact one-channel transfer matrix is

```text
[f_i(L)]   [ F_i    m S_i ] [f_i(0)]
[g_i(L)] = [-m S_i  G_i  ] [g_i(0)].
```

The parity data can be written `f(0)=E a`, `g(0)=O a`.  Imposing
`g(L)+B f(L)=0` gives the finite characteristic matrix

`K(m)=(-mS+BF)E+(G+mBS)O`,

and the exact signed eigenvalue equation is

`C(m)=det K(m)=0`.

Because mixed even--odd masses need not make `C` even, the complete
mass-squared characteristic is

`D(z)=C(sqrt(z)) C(-sqrt(z))`.

It is entire in `z`.  The complete four-spinor result is

`C_full=C_L^8 C_R,non-singlet^7 C_R,singlet`.

This accounts for all 64 bulk-H chiral component channels.  No division by
`m`, `S`, `F`, or `G` is made, so the formula remains valid at zero and at
bulk thresholds.

## Exact zero theorem

At `m=0`,

`K(0)=B F(0)E+G(0)O`.

Ordering odd rows/columns before even ones makes this block triangular:

`det K(0)=det G_O(0) det(B_EE) det F_E(0)`.

Both profile determinants are products of finite exponentials and cannot
vanish.  Therefore

`n_zero,chiral = n_even-rank(B_EE)`.

For a vector in `ker(B_EE)`, the odd-channel admixture is fixed by

`a_O=-G_O(0)^(-1) OBE F_E(0) a_E`.

This explicitly proves that the even--odd block changes the zero-mode profile
but cannot change its existence.  For a general complex symmetric holomorphic
mass `mu`, the same statement follows after the Hermitian Nambu lift
`B_N=[[0,mu^dagger],[mu,0]]`, and reduces to `ker(mu_EE)` in complex chiral
counting.

## V46 Theta+Sigma count

For the eight PS-left components, `E=diag(1,1,0,0)` and

`B_EE=[[0,tL],[tL*,0]]`.

For all eight PS-right components, including the single SU(5) singlet,
`E=diag(0,0,1,1)` and

`B_EE=[[0,tR],[tR*,0]]`.

The Sigma entries are outside both displayed even--even blocks.  The exact
chiral-component counts are:

- both Theta blocks nonzero: `0`;
- `tL=0`: `16`;
- `tR=0`: `16`;
- both zero: `32`.

Two useful counterexamples prevent a false rank argument:

1. `det B` can vanish at `tL tR=s16 sbar16` while `B_EE` is full rank and
   there is no zero mode.
2. With `tR=0` and nonzero Sigma entries, the full singlet `B` can be
   invertible while `B_EE=0` and two right-component chiral zero modes remain.

## Self-adjointness and tachyons

The first-order boundary form is

`[-f_psi^dagger g_phi+g_psi^dagger f_phi]_0^L`.

The parity condition at `y=0` is isotropic.  At the source, `g=-Bf` cancels
the form exactly when `B=B^dagger`; arbitrary complex superpotential masses
must be handled by the Hermitian Nambu lift.  The resulting first-order KK
operator has real signed eigenvalues.  Unbroken 4D N=1 supersymmetry then gives
nonnegative scalar masses squared.  Thus the declared problem has no
tachyonic or complex roots.

This proof does not cover non-Hermitian matching, negative boundary kinetic
norms, scalar-only SUSY-breaking masses, or an energy-dependent boundary kernel
whose additional boundary states have been integrated out incorrectly.

## Regulated determinant and strong-coupling warning

When `C(0)!=0`, the same-domain spectral determinant is

`P_B(z)=C(sqrt(z))C(-sqrt(z))/C(0)^2=product_a(1-z/m_a^2)`.

If `C(m)=c_q m^q+...`, remove the zeros by dividing the numerator by
`(-1)^q c_q^2 z^q`.  Unit-normalized Hermitian boundary rows are
`(I+B^2)^(-1/2)(g+Bf)=0`.  Same-domain products are independent of boundary-row
rescaling, while absolute and cross-`B` constants still require a brane
regulator and local counterterm scheme.

No exact zero appears at finite `B` while `B_EE` is full rank, but large
boundary singular values can create parametrically light states.  At the flat
certificate point, increasing the two Sigma entries from zero to
`(12.0,9.0)`
changes the lightest singlet absolute signed mass from
`0.5404195002706` to `0.00551446886439`.  If an invertible `B` is
scaled to infinity, the source condition tends to `f(L)=0` and `n_odd`
parity-flow zero modes appear at the limiting self-adjoint endpoint.

Projected rank, `det B`, and the phrase “large boundary mass” therefore do not
determine thresholds.  The actual 5D threshold calculation must use every root
of `C_full`.

## Fail-closed decision

The idealized four-spinor zero-mode question is closed: finite Hermitian `B`
with `tL,tR!=0` has no exact zero.  S2 and every G gate remain open.  Required
next steps are:

1. derive the matrix map from the four bare Theta/Sigma brane coefficients to
   `B` in one resolved source-wall regulator;
2. include induced kinetic, derivative and wrong-chirality terms;
3. fix `M_i,L` and source couplings and calculate the complete shifted
   thresholds, perturbativity and cross-wall Wilson coefficients;
4. finish the eta/global-anomaly, selector, flavor, neutrino, Higgs and
   SUSY-breaking audits.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230),
[Syed](https://arxiv.org/abs/hep-ph/0508153),
[Alciati et al.](https://arxiv.org/abs/hep-ph/0603086), and
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `f4e474c487da680d6da3400d6bb1d093070f6ad8e0628a49319ad09916ba6985`
