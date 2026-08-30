# SUSY V24 minimal Pati--Salam Z11 vacuum/RG frontier

- Status: `V24_PS_Z11_RP2_VACUUM_RG_FRONTIER_LANDED__P_ONLY_AXION_ARITHMETIC__GS_INCLUSIVE_WALL_OPEN__FULL_G1_G8_OPEN`
- Core: `9f47db6cb3bb97b10b4554b8b3f51f146c09820bd202d7b6dcb429891fece780`
- Gauge/vacuum source and published Z5 control: [Kawamura--Raby, arXiv:2009.04582](https://arxiv.org/abs/2009.04582); the selected Z11 selector is a V24 derivation.
- Exact PS coefficients: `b=[1, 5, 9]`, `B=[[108, 15, 21], [75, 53, 3], [105, 3, 81]]`.
- Published-control `fPQ=1e10 GeV`: the complete vectorlike `Delta b=(4,4,4)` threshold lowers `alpha_G^-1` from `24` to `15.204772813447`. Gauge-only inverse-coupling endpoints are `[13.860611822824, 10.985373107419, 7.747434876886]` at the source cutoff `10^18 GeV` (`mu/vPS=100`) and `[13.580318662923, 10.154174281965, 6.252345458625]` at reduced Planck `2.435e18 GeV` (`mu/vPS=243.5`).
- Selected Z11 witness `fPQ=1.76e+11 GeV`: `alpha_PS^-1(vPS)=17.030533960`. Its coupled gauge-only inverse-coupling endpoints are `[15.760581116, 12.877672032, 9.686379301]` at `10^18 GeV` and `[15.501027745, 12.063693017, 8.23108108]` at reduced Planck; both remain finite, while precision thresholds/Yukawas are open.
- Exact global-SUSY witness: `F=D=0`, zero energy; colored rank `2/2`, PQ exotic rank `2/2`.
- Published Z5 control anomalies: `Z4R mod 2=[1, 1, 1]`, `Z5 mod 5=[3, 3, 3]`. The selected Z11 residues are `[9, 9, 9]`; both selectors are universal but nonzero, so the GS completion is open.
- Axion: source `N_DW=4`, `E/N=8/3`, leading `P^10` quality. The `fPQ=4e10 GeV` scan point conditionally passes the quality/timing inequalities, but `gcd(4,10)=2` leaves an unremoved degeneracy, so it is not promoted to a domain-wall solution.
- Conditional P-only EFT arithmetic: `Z4R x Z11`, `rP=2`, leading `P^11`, and the formal integer `gcd(11,4)=1`. For unit coefficient and generic phase the P-only inequalities give `1.74031e+11 < fPQ < 1.78713e+11 GeV`; the `1.76e+11 GeV` row gives `Delta theta=8.45e-11` and `Tdec~0.00106 GeV`. This is not a physical wall-window claim.
- GS wall boundary: the Z11 mixed anomalies are universal but nonzero. A shifting GS axion is required, and the P-only QCD cosine is not by itself the complete discrete-gauge potential. The GS-inclusive vacuum lattice, residual degeneracy, physical bias, and wall collapse are all uncomputed/open.
- Conditional P-only 37-GHz diagnostic: `fPQ=1.5e+11 GeV`, `fa=3.75e+10 GeV`, `ma~152 micro-eV`, `nu~36.7 GHz`, worst-phase `Delta theta~1.46e-11`, and P-only radiation-era `tdec~3.26 s`. This row is phase/gap-factor dependent, overlaps BBN, and is neither a GS-inclusive wall result nor a closed relic calculation.
- Seesaw: `M_R=1e+14 GeV`; the normal-ordering mass witness needs perturbative Dirac singular values `[0.057471264368, 0.169633333153, 0.40695095319]`.

This is the selected V24 research frontier, not a complete G1--G8 theory. The Z11 candidate supplies only conditional P-only EFT arithmetic; it does not supply a consistent discrete-gauge wall witness without the dynamical Green--Schwarz axion and quotient. The complete discrete operator/GS sector, radiative PQ and soft/Kahler stabilization, physical stage thresholds, wall-network and relic evolution, full flavour fit, and proton Wilson matching are not landed. All eight full gates remain open.
