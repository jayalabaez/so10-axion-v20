# V46 bulk-spinor KK determinant audit

Status: `V46_SELF_ADJOINT_KK_CHARACTERISTICS_DERIVED__FINITE_NONZERO_FULL_RANK_BOUNDARY_EXTENSION_LIFTS_ALL_ZERO_MODES__NO_TACHYONS_IN_THE_SUPERSYMMETRIC_DOMAIN__PROJECTED_RANK_AND_FULL_TOWER_DETERMINANTS_SEPARATED__BARE_DELTA_TO_EXTENSION_MATCHING_AND_GLOBAL_GATES_OPEN`

## Verdict

For each of the two V45 conjugate Spin(10) hypermultiplet pairs, a **finite,
nonzero, full-rank self-adjoint source-wall mixing parameter** removes every
exact KK zero mode.  There is no tachyonic root for real odd bulk masses and a
Hermitian supersymmetric boundary condition.  This closes the idealized
two-hyper KK mass subproblem, not a G gate and not the complete 5D theory.

The qualification about the boundary parameter is essential.  The bare symbol
`mu=lambda<Theta>` multiplying an endpoint delta function does not define a
unique spectrum until the delta convention or resolved-brane regulator is
specified.  This audit chooses the one-sided interval prescription and calls
the resulting renormalized extension parameter `b>=0`; in that convention
`b=|mu|`.  All exact equations below are equations in `b`.  Other prescriptions
can change the map `b=|B_R(mu)|` and hence finite-coupling KK phases.

## Retained V45 pairs and parities

The source wall is `y=L`, the PS wall is `y=0`, and `L=pi R/2`.

- `ThetaPlus 16_+3 bar16_-12` pairs `LF=(4,2,1)_+3` with
  `LA=(bar4,2,1)_-12`.
- `ThetaMinus 16_-3 bar16_+12` pairs `RA=(bar4,1,2)_-3` with
  `RF=(4,1,2)_+12`.

For either Spin(10) pair, the selected PS halves have `H=(+,+)` and the other
eight components have `H=(-,+)`.  The conjugate chiral `Hc` always has the
opposite parities.  Because both `H` fields are even at the full-Spin(10) wall,
the source superpotential pairs the complete representations.  Per conjugate
Spin(10) pair the full characteristic factor is

`[D_++(z) D_-+(z)]^8`, with `z=m_4^2`.

## Declared self-adjoint boundary problem

On `0<y<L`, use the Marti--Pomarol hypermultiplet convention

`int d2theta H_i^c (partial_y+M_i) H_i + h.c.`

with real odd kink mass `M_i epsilon(y)`.  The mode equations are

`(partial_y+M_i)f_i=m g_i`,  `(-partial_y+M_i)g_i=m f_i`.

After rephasing the holomorphic mass, the source boundary condition is

`g(L)+b sigma_1 f(L)=0`,  `b>=0`.

It is self-adjoint because `b sigma_1` is Hermitian.  For cross-boundary
determinant comparisons the two boundary rows are normalized by
`sqrt(1+b^2)`; otherwise an arbitrary rescaling of a boundary equation would
spuriously rescale the functional determinant.

Define the entire functions

`S_i(z)=sin(k_i L)/k_i`,  `F_i(z)=cos(k_i L)-M_i S_i(z)`,
`G_i(z)=cos(k_i L)+M_i S_i(z)`,  `k_i^2=z-M_i^2`.

For imaginary `k_i`, the trigonometric functions are analytically continued to
hyperbolic functions.  At zero,

`S_i(0)=sinh(M_i L)/M_i`, `F_i(0)=exp(-M_i L)`, and
`G_i(0)=exp(+M_i L)`.

## Exact KK eigenvalue conditions

For the selected `(+,+)` halves, `g_i(0)=0`.  The source-wall coefficient
matrix is

`[[-m S_1, b F_2], [b F_1, -m S_2]]`,

so the exact full-tower condition is

`D_++(z) = z S_1(z)S_2(z) - b^2 F_1(z)F_2(z) = 0`.

For the unselected `(-,+)` halves, `f_i(0)=0`.  Multiplying the two source rows
by `m` gives

`[[G_1, m b S_2], [m b S_1, G_2]]`,

and therefore

`D_-+(z) = G_1(z)G_2(z) - z b^2 S_1(z)S_2(z) = 0`.

These are entire in `z`; no division by `m`, `k_i`, or a trigonometric
function is used in the root test, so threshold roots are not lost.

`D` counts nonnegative Dirac/Takagi singular masses.  At `b=0`, the two
selected chiral zero modes of one conjugate PS pair make one zero singular mass
per gauge component, so `D_++` has one factor of `z`; the determinant of the
signed `2x2` chiral mass matrix contains the corresponding square.

For `M_1=M_2=0`, writing `alpha=atan(b)`, the selected masses are

`(n pi+alpha)/L` and `((n+1)pi-alpha)/L`,

while the unselected masses are

`(n pi+pi/2-alpha)/L` and `((n+1)pi-pi/2+alpha)/L`.

## Zero modes, tachyons, and strong-boundary spectral flow

At `z=0`,

`D_++(0)=-b^2 exp[-(M_1+M_2)L]`,

`D_-+(0)= exp[+(M_1+M_2)L]`.

Thus every finite `b!=0` removes both selected chiral zero modes (the one
vectorlike singular pair) and cannot create an unselected zero mode.  More
generally, if `n_1+n_2` selected chirals are coupled by a boundary matrix of
rank `r`, the exact residual chiral nullity is `n_1+n_2-2r`, since finite kink
profiles are nonzero at the source.  The exceptions are `b=0`, deficient flavor
rank, a parity/locality mistake, extra boundary fields, or the distinct endpoint
`b=infinity`.  A nonzero *bare* `mu` is not by itself a proof unless the chosen
UV prescription establishes `B_R(mu)!=0`.

There are no tachyons in the declared problem.  For `z=-kappa^2`, define
`rho_i=sqrt(kappa^2+M_i^2)>|M_i|`.  Then `S_i`, `F_i`, and `G_i` are positive,
so

`D_++=-kappa^2 S_1S_2-b^2F_1F_2<0`,

`D_-+=G_1G_2+kappa^2b^2S_1S_2>0`.

There is nevertheless an important non-uniform limit.  As `b->infinity`, the
lowest unselected state becomes light:

`m_light,-+^2 = exp[(M_1+M_2)L]/[b^2 S_1(0)S_2(0)] + O(b^-4)`.

At exactly infinite `b`, the endpoint is a different self-adjoint extension and
this mode is massless.  “Larger boundary mass” therefore does not mean that the
whole Spin(10) tower becomes monotonically heavier.

## Regulated determinants

The regulator-independent spectral objects at fixed `b` are the convergent
genus-zero Hadamard products

`P_++(z;b)=D_++(z;b)/D_++(0;b)` for `b!=0`,

`P'_++(z;0)=D_++(z;0)/[z partial_z D_++(0;0)]` with its zero removed, and

`P_-+(z;b)=D_-+(z;b)/D_-+(0;b)`.

Each equals `product_n(1-z/m_n^2)`.  For the declared unit-normalized boundary
rows, the cross-domain zeta ratios are

`det_zeta O_++,b / det'_zeta O_++,0`
`= b^2 exp[-(M_1+M_2)L]/[(1+b^2)S_1(0)S_2(0)]`,

`det_zeta O_-+,b / det_zeta O_-+,0 = 1/(1+b^2)`.

The `1/(1+b^2)` factors are required: a raw characteristic determinant has
high-Euclidean-momentum normalization `1+b^2`.  In the flat case a direct
Hurwitz-zeta product gives `b^2/[L^2(1+b^2)]` and `1/(1+b^2)`, respectively.
Absolute determinant constants remain adjustable by local boundary
counterterms; the roots and the same-domain products above do not.

## Projected 4D rank is not the full tower

The unperturbed normalized zero profile is

`f_i^0(y)=N_i exp(-M_i y)`,

`N_i^-2=(1-exp(-2M_iL))/(2M_i)=exp(-M_iL)S_i(0)`.

Projection gives

`m_proj=b N_1N_2 exp[-(M_1+M_2)L]`.

It is the leading small-`b` pole, `m_light^2=m_proj^2+O(b^4)`, not an exact
finite-`b` eigenvalue.  In the flat example, `m_proj=b/L` whereas the exact
selected light mass is `atan(b)/L`.  Both V45 boundary blocks nonzero therefore
give exact projected multiplet rank four and no exact finite-`b` KK zero, but
rank alone neither fixes the spectrum nor excludes the strong-`b` light
unselected state.

## Executable certificate

For `L=1.0`, `M_1=0.7`, `M_2=-0.4`, `b=0.3`:

- `D_++(0)=-0.06667363986135` and `D_-+(0)=1.349858807576`;
- first selected mass `0.23841488904706`;
- first unselected mass `1.23013736275942`;
- projected mass `0.24477346101275`.

At the flat check point `b=0.3`, the exact lowest masses are
`0.29145679447787` and `1.27933953231703` and both
characteristics vanish to the recorded numerical precision.

Run:

`python susy_v46_spinor_kk_determinant_audit.py --check`

`python -m pytest -q test_susy_v46_spinor_kk_determinant_audit.py`

## Fail-closed boundary

No G gate is promoted.  The next mandatory step is to specify a resolved
source-wall UV action, derive `B_R(mu)` (including any induced boundary kinetic
terms), then redo this transfer matrix with the separately allowed source terms
`barSigma HLF HRA` and `Sigma HLA HRF`.  Those terms mix the nominal left and
right spinor pairs with source-even KK states, so the factorized determinant in
this audit is not the final source-wall determinant.  They must be included in
one enlarged coupled transfer matrix or forbidden by an exact selector before
S2 can close.  Threshold matching and cross-wall Wilson coefficients must use
the shifted full tower.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230),
[Alciati et al.](https://arxiv.org/abs/hep-ph/0603086),
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852), and
[Falco--Fedorenko--Gruzberg](https://arxiv.org/abs/1703.07329).

V45 input SHA-256:

- `SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json`: `dd982bd79da39f8d59870fdcd3d3da74515a527ac14415d510dab65136e5e2a5`
- `SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json`: `92dc538c67d1e455d8eab36a1d3a1cd7ccb254f1a131cb9af30f4eb45ab35a38`

V46 core SHA-256: `9b814b32381d2b476f4368054e8f27eedb1423740ac829755ab7570d862d71e8`
