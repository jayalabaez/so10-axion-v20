# REJECTED: PSZ4RZ5610Z5SUSYV39 negative-control source

This directory records an exploratory `Z5` charge assignment that was
**rejected**. Its standard mixed Pati--Salam--`Z5` doubled-Dynkin residues are
`A_SU2L=3 mod 5` and `A_SU2R=2 mod 5`; it is not an anomaly-clean selector
candidate and must not be used in a V39 source manifest or gate claim. The
active candidate is `PSZ4RZ5610Z3SUSYV39`.

The rejected experiment was a narrow G7 architecture repair on top of V37. It replaces the one
Pati--Salam `Sig6` with two chiral sixes:

`Sc^2 SigC + Sbc^2 SigBc`, with `Z5(SigC,SigBc)=(3,2)`.

The complete extra `Z5` has `Z5(Q,Qc)=(4,1)` and keeps the V37 `Z5610`,
external `Z4R`, Yukawa, vectorlike-mixing, and seesaw structure.  Therefore
the source-level monomials `X Q^4`, `X Qc^4`, `Zp Q^4`, and `Zp Qc^4` carry
nonzero `Z5` charge and are absent.

The equal-conjugate Pati--Salam branch retains `Sc*Sbc=vPS^2`,
`P*Pb=fPQ^2`, `X=Zp=SigC=SigBc=0` in the canonical global-SUSY truncation.
The same V37 `Z5610`/PQ assignments are retained, so this replacement cannot
lower the V37 charge-lattice quality bounds by itself.

It does not establish any completion, and is retained solely so the failed
`Z5` route is auditable rather than silently reused.
