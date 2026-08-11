# Global real Phi self-zero classification

Status:
`EXACT_GLOBAL_REAL_PHI_SELF_ZERO_IS_SIGNED_KAEHLER_CONE__G3_OPEN`.

Let

```text
omega = e01+e23+e45+e67+e89,
F     = (1/2) omega wedge omega,
||F||^2 = 10.
```

The exact global result is

```text
{real Phi : q54(Phi)=q4125(Phi)=0}
 = {0}
   union {r g.F    : r>0, g in SO(10)}
   union {r g.(-F) : r>0, g in SO(10)}.
```

In particular, on `||Phi||^2=10`, the common zero locus is exactly

```text
SO(10).F union SO(10).(-F).
```

The two sheets are distinct: the exact cubic invariant is `+60` on `F` and
`-60` on `-F`.

## Algebraic reduction

Write

```text
N = ||Phi||^2,
D = (9/5)N^2 - ||*(Phi wedge Phi)||^2,
G = O_Phi^T O_Phi,
S = tr[G(G-(6/5)NI)^2],
C = 5 I3^2 - 18 N^3.
```

On `q54=q4125=0`:

1. The exact degree-eight conductor identity gives `D=0`.
2. The exact cubic Cauchy bridge gives `C<=0`.
3. The exact sextic syzygy gives `C=(35/1536)S`.
4. For real `Phi`, `G` is positive semidefinite, hence `S>=0`.

Therefore `C=S=0`.

If `N=0`, reality gives `Phi=0`.  If `N>0`, every eigenvalue of `G` is
either `0` or `6N/5`.  Since `tr G=24N`, exactly 20 eigenvalues are nonzero:

```text
spec G = {0^25, (6N/5)^20}.
```

Thus the identity component of the SO(10) stabilizer has dimension 25.

## Stabilizer rigidity

The final structural input is Dynkin's classification of connected maximal
proper subgroups of the classical groups.  The high-dimensional possibilities
in SO(10) are the standard blocks, U(5), and the listed absolutely
irreducible cases.

- Blocks SO(3)xSO(7), SO(4)xSO(6), and SO(5)xSO(5) have dimensions at most
  24.
- In SO(2)xSO(8), the kernel of a 25-dimensional subgroup's projection to
  SO(2) would have dimension at least 24, but a proper connected subgroup of
  SO(8) has dimension at most 21.
- The full SO(9) maximal list leaves only SO(8) above dimension 24; a proper
  25-dimensional subgroup inside SO(8) is again impossible.
- The remaining proper simple absolutely irreducible entries have no faithful
  real ten-dimensional representation at dimension at least 25.

Hence the stabilizer is conjugate to U(5).  Complexifying
`R^10=C^5` decomposes four-forms by bidegree `(p,q)`.  The U(1) center forces
`p=q=2`; Schur's lemma on the irreducible `Lambda^2(C^5)` leaves one fixed
line.  It is exactly `R*(omega^2/2)`.  Norm then fixes
`Phi=+sqrt(N/10)g.F` or `-sqrt(N/10)g.F`.

The external classification reference is E. B. Dynkin, *Maximal subgroups of
the classical groups*, Trudy Moskov. Mat. Obshch. 1 (1952), 39–166; English
translation, AMS Translations Series 2, vol. 6 (1957), 245–378.

## Converse and physical zero boundary

The frozen exact SU(4) formulas give `q54=q4125=0` at both signed
representatives.  Equivariance and homogeneity give the complete signed
cones.  The already frozen full-126 physical subtraction theorem is safe on
both signed orbits, so this classification identifies every nonzero Phi
self-zero point with that certified boundary.

## Why G3 remains open

This classification is qualitative, not a quantitative error bound.  The
frozen linearized source has a 30-dimensional common projector kernel on the
unit sphere: 20 orbit directions plus ten transverse directions.  Including
the radial cone direction gives a 31-dimensional quadratic kernel versus a
21-dimensional signed-orbit-cone tangent.  Thus the zero is not Morse–Bott;
the ten conductor directions first appear quartically.

Still missing is an explicit global inequality of the form needed to push a
small projector residual into the existing signed-orbit strong-operator
tube, together with exact control on the compact complement.  Accordingly,
this theorem leaves both G3 and G4 false/open.

Certificate core SHA-256:
`db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc`.
