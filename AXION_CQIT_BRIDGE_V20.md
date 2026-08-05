# SO(10) axion × CQIT receiver bridge — v20

## Scientific scope

This bridge combines the **37 GHz experimental target** from `so10-axion-v20`
with the **receiver/null-test accounting** developed in the CQIT repository.
It does not merge the falsified circumference-redshift hypothesis into the
axion model and it does not introduce a new axion interaction.

The v20 model supplies a benchmark source hypothesis:

- axion mass near 153.5 µeV;
- photon frequency near 37.11 GHz;
- target coupling near 2.335×10⁻¹⁴ GeV⁻¹;
- Galactic halo linewidth of order ν/Q with Q≈10⁶.

CQIT supplies a disciplined receiver decomposition:

\[
  x(\nu)=\mathcal D_{\rm receiver}\circ\mathcal L_{\eta}
  [s_a(\nu;m_a,g_{a\gamma\gamma},{\cal H})]+n(\nu).
\]

Here `s_a` is the axion-conversion spectrum, `L_eta` represents calibrated
receiver loss, `D_receiver` represents template capture and readout response,
and `n` is measured noise.

## Crucial boundary

Galactic axions do not emit 37 GHz photons across cosmological distances. The
photon is produced **inside the haloscope** by axion-to-photon conversion.
Therefore the cosmological CQIT redshift map is the identity for this signal:

\[
 z_{\rm laboratory}=0.
\]

Redshift cannot explain, enhance, or validate the predicted axion line.

## Added tests

The bridge adds executable checks for:

1. local mode identity at z=0;
2. exact matched-template capture;
3. loss of capture from a frequency/template offset;
4. halo linewidth and coherence time;
5. receiver-efficiency and excess-noise SNR penalties;
6. coupling bias when lost signal power is not calibrated;
7. repeatability requirements;
8. instrumental vetoes;
9. explicit no-discovery/no-validation claims.

The coherence convention used is

\[
 \Delta\nu=\nu_a/Q_a,\qquad
 \tau_c=\frac{1}{\pi\Delta\nu}.
\]

At 37.11 GHz and Q=10⁶ this gives Δν≈37.11 kHz and τc≈8.58 µs.

## Receiver bias

Because haloscope power scales approximately as

\[
 P_a\propto g_{a\gamma\gamma}^2,
\]

an unmodelled signal-power fraction `f = efficiency × template_capture` biases
the inferred coupling by

\[
 g_{\rm inferred}/g_{\rm true}=\sqrt f.
\]

This is an analysis systematic, not new physics.

## Candidate triage

A software candidate must pass all of the following before external review:

- SNR threshold;
- frequency inside 36.6–37.6 GHz;
- linewidth compatible with the halo template;
- at least two independent repeats;
- instrumental/environmental vetoes clear.

Even a passing candidate is **not a discovery**. A physical rescan, independent
hardware or collaboration, trials correction, and source-systematics review are
still required.

## Provenance

The receiver concepts were adapted from
`jayalabaez/path-dependent-optical-expansion`, CQIT v6 main commit
`2b07685cbd4518f1f3154f58e2925cf9923684db`.

The bridge is intentionally self-contained so that the SO(10) release does not
depend on another repository at runtime.

## Honest verdict

- CQIT does not rescue or alter the SO(10) field-theory gaps.
- CQIT does improve the 37 GHz receiver and falsification accounting.
- Passing the bridge tests proves software consistency only.
- Only a real, independently reproduced haloscope excess can test nature.
