# E/F/J/X Clebsch-normalization source ledger — v20

## Exact question

Derive the convention map

\[
\gamma_{\rm eff}=c_{\rm norm}\,\lambda_4
\]

for the non-supersymmetric invariant

\[
\Phi(210)\,H(10)\,\overline{\Sigma}(\overline{126})\,S,
\]

using canonically normalized fields and the physical electroweak branch.

## Primary sources

1. **Chen, Zhang and Bai, arXiv:1707.00580**
   - Supplies normalized 10, 126/126bar and 210 states in an SU(5) basis.
   - Defines the general renormalizable invariant containing `H Phi Delta` and `H Phi Deltabar`.
   - Table 6 records the conversion between historical invariant couplings and order-one normalized couplings.
   - Its F- and D-flatness equations and physical SUSY mass spectrum are not imported into the non-supersymmetric model.

2. **Fukuyama, Ilakovac, Kikuchi, Meljanac and Okada, arXiv:hep-ph/0405300**
   - Supplies an independent G422 component-state and Clebsch table.
   - Used only as a representation-theory cross-check.

3. **Aulakh-sector E/F/J/X matrices already transcribed in `mixed_210_126_10_cw_v20.py`**
   - These matrices determine the exact linear response to the Aulakh `gamma` convention.
   - They do not determine how the repository's reduced radial `lambda4` proxy maps onto `gamma`.

## Why the old ratio is not physical

`lam4_potential_efjx_decoupling_v20.py` obtains its selected `lambda4` from
`charge_allowed_potential_minimize_v20.py`, whose target point sets the effective
radial 10_H magnitude to the intermediate scale. The canonical physical audit
instead requires the electroweak 10_H VEV to be 174 GeV and finds the historical
point tachyonic. Therefore `gamma_crit/lambda4_selected` is only a diagnostic of
that reduced proxy and cannot be quoted as a physical SO(10) Clebsch coefficient.

## Required direct calculation

1. Write the exact antisymmetric-index contraction, including factorials and the
   126bar duality convention.
2. Insert normalized 210 singlet states for the selected `(p,a,omega)` direction,
   the normalized 126bar and 10 component states, and the normalized singlet S.
3. Reconstruct every gamma-dependent E/F/J/X matrix slot directly.
4. Match the result to the Aulakh gamma convention and extract `c_norm`.
5. Insert the derived mapping into the complete non-supersymmetric component
   potential and re-minimize on the physical `h=174 GeV` branch.
6. Accept the result only after an independent reconstruction agrees slot by slot.

The accompanying JSON example is intentionally non-closing until all six steps
have evidence.
