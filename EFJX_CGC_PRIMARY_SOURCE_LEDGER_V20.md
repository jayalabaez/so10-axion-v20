# Direct `Phi H Sigmabar S` tensor-source ledger — v20

## Correct physical question

For the non-supersymmetric scalar invariant

\[
V\supset \frac{\lambda_4}{4!}\,S\,H_i\Phi_{jklm}
\overline{\Sigma}_{ijklm}+\text{h.c.},
\]

derive the canonically normalized scalar bilinear generated after
`S` and the `210` singlets acquire VEVs.  This is a `10 x 126` scalar
mass-squared map.  It is not an E/F/J/X gaugino-mass response.

## Primary-source correction

### Aulakh and Girdhar, hep-ph/0405074

- Eq. (1) contains the superpotential coupling
  `H_i Phi_jklm (gamma Sigma_ijklm + gamma_bar Sigmabar_ijklm) / 4!`.
- Eq. (3) gives the tensor kinetic terms.  The self-dual `126/126bar`
  has the extra factor `1/2`, so a canonical five-form state has raw
  component norm `sqrt(2)`.
- Section 3.3 is explicitly titled **Mixed Chiral-Gauge**.
- The Appendix-A E/F/J/X bases explicitly contain `lambda`, the SO(10)
  gaugino field.
- The symbol `g` in Eqs. (87)-(90) is the SO(10) gauge coupling entering
  super-Higgs chiral-fermion/gaugino mixing.  It is not `gamma`.

Therefore the former repository operation

```text
replace Aulakh g by gamma, scan E/F/J/X, infer gamma_eff/lambda4
```

was a category error.  The associated `8.8e29` Clebsch bound is withdrawn.

## Executed replacement

`direct_phi_h_sigmabar_tensor_v20.py` now:

1. represents `210` as a real four-form on `R^10`;
2. constructs a canonical kinetic-orthonormal `126bar` basis in the
   `-i` Hodge eigenspace;
3. constructs the full canonical `(p,a,omega)` singlet basis;
4. evaluates the direct contraction
   `C_i = Phi_jklm Sigmabar_ijklm`;
5. verifies SO(10) equivariance;
6. derives the closed singular-value spectrum independently of the
   numerical SVD.

For real canonical singlet coefficients `(p,a,omega)`, the four branches are

\[
\begin{aligned}
s^2_{T+}&=\left(p+\frac{a}{\sqrt3}\right)^2+
          \frac{4\omega^2}{3}, &&\text{multiplicity }3,\\
s^2_{T-}&=\left(p-\frac{a}{\sqrt3}\right)^2,
          &&\text{multiplicity }3,\\
s^2_{D+}&=\left(a+\frac{\omega}{\sqrt2}\right)^2,
          &&\text{multiplicity }2,\\
s^2_{D-}&=\left(a-\frac{\omega}{\sqrt2}\right)^2,
          &&\text{multiplicity }2.
\end{aligned}
\]

The `3+3` degeneracies are the two color-triplet branches of
`10_H -> (6,1,1)`.  The `2+2` degeneracies are the two electroweak-doublet
branches of `10_H -> (1,2,2)`.

After `S=v_S`, the direct off-diagonal scalar mass-squared singular values are

\[
|\lambda_4 v_S|\,s_{T\pm,D\pm}.
\]

## Independent cross-check routes

1. **Direct Cartesian forms — executed.**
   Numerical `10 x 126` construction, Hodge duality, kinetic Gram matrix,
   gauge orbit and SO(10) equivariance.
2. **Closed analytic reconstruction — executed.**
   Diagonalize `T_Phi T_Phi^dagger` into the `3+3+2+2` branches above and
   compare to the numerical SVD.
3. **Published state-table dictionary — still open.**
   Chen-Zhang-Bai and Fukuyama et al. can independently map phases and labels
   between Cartesian, SU(5), and G422 conventions.  This is now a convention
   cross-check, not the producer of the tensor map.

## What remains open

- map the repository's historical numerical `p,a,omega` parameters to these
  canonical Cartesian coefficients without reusing proxy normalizations;
- insert the direct block into the complete non-supersymmetric scalar
  mass-squared matrix;
- enumerate the complete allowed scalar invariant ring;
- solve stationarity, boundedness, competing extrema and the full Hessian.

The direct tensor contraction is solved.  The complete scalar theory is not.
