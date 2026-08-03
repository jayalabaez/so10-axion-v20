# FCNC channel-rate conventions — v20

## Interaction convention

The code uses

\[
\mathcal L_{\partial a}=\frac{\partial_\mu a}{f_a}
\left(\bar f_L K_L\gamma^\mu f_L+\bar f_RK_R\gamma^\mu f_R\right).
\]

The matrices are dimensionless and are rotated into the fermion mass basis.
This normalization matches the lepton convention of arXiv:1908.00008 after
identifying its left/right matrices with `K_L,K_R`.

## Muon decay

For \(\mu\to e a\), equations of motion give

\[
A_L=m_\mu K_R-m_eK_L,\qquad
A_R=m_\mu K_L-m_eK_R.
\]

The exact spin-averaged two-body rate implemented in
`channel_fcnc_rates_v20.py` includes finite \(m_e\) and \(m_a\). In the
\(m_e\to0\) limit it reduces to

\[
\Gamma(\mu\to ea)=\frac{m_\mu^3}{32\pi f_a^2}
\left(|K_L|^2+|K_R|^2\right)
\left(1-\frac{m_a^2}{m_\mu^2}\right)^2,
\]

which is the two-body normalization in arXiv:1908.00008.

## Kaon decay

For \(K^+\to\pi^+a\), the pseudoscalar-to-pseudoscalar axial-current matrix
element vanishes by parity. With the convention above, the vector-current
coefficient is therefore controlled by \(K_L+K_R\). The rate implemented is

\[
\Gamma(K^+\to\pi^+a)=\frac{m_K^3}{64\pi f_a^2}
|K_L^{ds}+K_R^{ds}|^2 f_0(m_a^2)^2
\lambda_{\pi a}^{1/2}
\left(1-\frac{m_\pi^2}{m_K^2}\right)^2,
\]

using the normalization of arXiv:1901.02031. At the v20 mass,
\(m_a^2\) is effectively zero on the hadronic scale, so the current diagnostic
uses the lattice result

\[
f_0(0)=f_+(0)=0.9704(32)
\]

from arXiv:1312.1228.

## Experimental comparison scope

The current code stores conservative TWIST and NA62 comparison scales. These
are not pointwise digitized likelihoods and are not used to claim unconditional
exclusion or finite-model FCNC absence.

## Remaining UV work

The left/right rotations are conditional on a common family-space current for
the components of one SO(10) `16`. Full closure requires component-specific
currents after Pati-Salam and electroweak threshold matching, propagation of the
portal-Yukawa posterior, form-factor covariance, and the pointwise experimental
likelihoods.
