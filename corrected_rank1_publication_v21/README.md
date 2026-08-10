# Corrected rank-one SU(4) positive-Gram publication v21

This isolated bundle certifies the fixed endpoint

`H = h_- = (e0 - i e1)/sqrt(2), Sigma = q/4`

for arbitrary real `Phi`.  It proves

`p(t,Phi) = A(t,Phi) - 3 t^4/200 > 0`

away from the homogeneous origin.  Consequently, at `t=1`,
`A(Phi) > 3/200` for every real `Phi`, and the fixed-endpoint `p`-zero set is
empty.

The theorem does not vary `H` or `Sigma`.  It does not prove a global-Sigma,
general-H, full-H, full-Hessian, or G3 statement.  `G3_closed` is false in
every public claim boundary.

## Exact chain

- The complete positive-carrier decomposition has real dimension
  `22366 = 211*212/2`, 35 complex isotypic types, 824 irreducible copies, and
  22 real/Hermitian Gram blocks.  Its standard Schur coordinate census is
  `(1,4,90,1414,18085)`, totaling 19,594.
- All 19,594 coefficient-map columns are reconstructed from carrier APIs.  The
  four grade-01 columns use the corrected `linear_column/16` normalization.
  The exact map is `6585x19594`, denominator 256, 138,550 nonzeros, SHA-256
  `1834c8439fa3e44459f7ba871420a4351cd0b4de194dec6f5c4a84c1f39d3a16`.
- All 6,057 quartic RHS rows are reconstructed from the ordered spectral
  operator with Python-integer physical contractions.  The complete RHS has
  denominator 576,000 and SHA-256
  `14debcfaf02d4b8c20d1d43a2e1f82d6a7390e28428fc63dd21a9c5f90aec0cf`.
  The first quartic pivot is `27776/1125`; the rejected raw-Schur value is
  `129568/3375`.
- The exact rational primal has coordinate SHA-256
  `7a36b579821e135fb7283d02e696153cc78907048e73ca5dce0dd260abdc3147`.
  An independent Fraction/Bareiss verifier checks all 6,585 affine
  equalities and 824 strictly positive pivots across all 22 blocks.  The pivot
  SHA-256 is
  `bc8626c201d626aa33a97f707bfa963ae887fe9abb64a0fab728343825a430c2`.
- A direct live SU(3) regression evaluates the primal as actual positive
  carrier norms grade by grade.  It records raw `A`, subtracts `3/200` only
  from grade zero, and obtains exact target/carrier total
  `15742745821207/3000000000000000`.
- Separate arithmetic hardening traverses all seven ordered pair-Casimir
  powers with Python integers.  The coarse and sharp scalar contractions are
  respectively 68 and 108 bits, both beyond signed int64.  This overflow
  audit hardens the evaluation path; it is not a premise of positivity.

## Fast runtime checks

Ordinary validation uses only byte-pinned files in this directory and never
rebuilds the large map or RHS:

```text
python -B exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py --check
python -B verify_exact_gauged_u1x_g3_rank1_su4_corrected_positive_gram_primal_v21.py
python -B verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py
python -B -m unittest -v test_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py
python -B freeze_exact_gauged_u1x_g3_rank1_su4_corrected_publication_v21.py --check
```

The runtime theorem path is relocatable.  A fresh-copy/shadow-path regression
is part of the fast test suite.  A manual isolated check is:

```text
python -B -I verify_exact_gauged_u1x_g3_rank1_su4_corrected_fixed_endpoint_theorem_v21.py
```

## Explicit heavy reconstruction

The two reconstruction builders and the live/overflow evaluators are
generation-time evidence.  They require the explicitly byte-pinned structural
API tree through `SO10_PUBLISHED_API_ROOT`; they are not part of the relocated
runtime dependency graph.  Run the full map/RHS reconstruction exactly once
in the dedicated heavy job:

```text
SO10_PUBLISHED_API_ROOT=/path/to/pinned/api python -B heavy_regenerate_exact_gauged_u1x_g3_rank1_su4_corrected_system_v21.py --check
```

`reconstruct_system()` performs one complete 19,594-column reconstruction and
one embedded 6,057-row RHS reconstruction.  Unit-test discovery never invokes
it.  This keeps the ordinary workflow fast and leaves a single explicit heavy
step within the GitHub-hosted 360-minute ceiling.

## Inventory boundary

`EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json`
byte-pins every other file in this directory.  The freezer rejects missing,
extra, or changed files.  `__pycache__` is not permitted in a frozen bundle.
The release repository is not modified by this isolated bundle.
