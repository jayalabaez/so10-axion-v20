# Exact global sextic syzygy for the Phi-self zero problem

Status: `EXACT_GLOBAL_PHI_ZERO_SEXTIC_SYZYGY__CLASSIFICATION_OPEN`.

For a real four-form `Phi` define

```text
N = ||Phi||^2,
B = *(Phi wedge Phi),
D = (9/5)N^2-||B||^2,
G = O_Phi^T O_Phi,
S = tr[G(G-(6/5)N I)^2],
C = 5 I3(Phi)^2-18N^3.
```

Here `O_Phi` is the `210 x 45` infinitesimal-orbit matrix and
`I3=tr(A_Phi^3)`. The verifier proves the exact global polynomial identity

```text
C = sum_i c_i X_i + (1405/64) N D + (35/1536) S,            (1)
```

where every one of the fifteen displayed `X_i=tr(q_r q_a q_b)` contains
one live residual `q_r`, with `r=54` or `4125`. The source records every
rational coefficient `c_i` and the exact channel labels.

Consequently, on the common live-projector zero set,

```text
5 I3^2-18N^3 = (1405/64) N D + (35/1536) S.                 (2)
```

The proof is finite and exact:

- a D5 Racah--Speiser weight calculation gives
  `mult_1 Sym^6(210)=18`;
- the fifteen ideal contractions together with `ND`, `S`, and `N^3`
  form an 18-element invariant basis, certified by rank `18` on an
  `18 x 18` integral evaluation matrix modulo every certificate prime;
- the proposed identity has zero residual on those 18 samples modulo
  18 distinct primes;
- after clearing all projector, relation, and fifth denominators, the
  product of those primes exceeds twice an explicit absolute integer
  height bound for every sampled residual.

Thus each sampled residual is exactly zero over the rationals. Since the
evaluation set is unisolvent for the complete 18-dimensional invariant
space, (1) is a global polynomial identity.

For real `Phi`, `G` is positive semidefinite, so `S>=0`. If `S=0`, its
spectrum is contained in `{0,6N/5}`; together with `tr G=24N`, this gives
`rank G=20` for `N>0`. This is the desired orbit-Gram rigidity mechanism.

Scope is strict. The theorem does not prove a sign for `D`, a sharp cubic
inequality, `D=S=0` on the common zero set, or the global signed-Kahler
classification. G3 and G4 remain open pending that final real-radical or
spinor-normalization step.
