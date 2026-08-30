#!/usr/bin/env python3
"""Fail-closed discrete-R audit for the reduced V45 five-dimensional core.

This is a conventional integrated four-dimensional anomaly screen plus an
exact congruence no-go.  It is deliberately not a localized orbifold-anomaly
or Spin^Z_N bordism certificate.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V45_DISCRETE_R_AUDIT.json"
MD_PATH = ROOT / "SUSY_V45_DISCRETE_R_AUDIT.md"
STATUS = (
    "V45_INTEGRATED_DISCRETE_R_CANDIDATES_EXIST__EQUAL_LEVEL_PS_UNIVERSALITY_"
    "FORCES_THE_DEGREE20_ORIENTED_W_OPERATOR__NO_SYMMETRY_PRESERVING_MASSIVE_"
    "PACKET_REPAIR__LOCALIZED_GLOBAL_COMPLETION_OPEN"
)


def eta(order: int) -> int:
    return order if order % 2 else order // 2


def canonical_sha(payload: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(payload))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def charges_for(order: int, q: int, qc: int, t: int = 0) -> dict[str, int]:
    """A reproducible representative of every required-term congruence class."""

    h = (2 - q - qc) % order
    a = q % order
    b = (2 - t - a) % order
    c = qc % order
    d = (2 + t - c) % order
    return {
        "Q": q % order,
        "Qc": qc % order,
        "H": h,
        "A16_plus3": a,
        "Bbar16_minus12": b,
        "C16_minus3": c,
        "Dbar16_plus12": d,
        "ThetaPlus": t % order,
        "ThetaMinus": (-t) % order,
        "STheta": 2 % order,
        "Delta126": 0,
        "DeltaBar126": 0,
        "SDelta": 2 % order,
    }


def term_charge(order: int, charges: Mapping[str, int], names: tuple[str, ...]) -> int:
    return sum(charges[name] for name in names) % order


REQUIRED_TERMS: dict[str, tuple[str, ...]] = {
    "Q_H_Qc": ("Q", "H", "Qc"),
    "STheta_constant_spurion": ("STheta",),
    "STheta_ThetaPlus_ThetaMinus": ("STheta", "ThetaPlus", "ThetaMinus"),
    "ThetaPlus_A16_Bbar16": ("ThetaPlus", "A16_plus3", "Bbar16_minus12"),
    "ThetaMinus_C16_Dbar16": ("ThetaMinus", "C16_minus3", "Dbar16_plus12"),
    "SDelta_constant_spurion": ("SDelta",),
    "SDelta_Delta126_DeltaBar126": ("SDelta", "Delta126", "DeltaBar126"),
}


def required_term_audit(order: int, charges: Mapping[str, int]) -> dict[str, Any]:
    rows = {
        name: term_charge(order, charges, fields)
        for name, fields in REQUIRED_TERMS.items()
    }
    return {
        "W_target": 2 % order,
        "charges": rows,
        "all_allowed": all(value == 2 % order for value in rows.values()),
        "mu_HH_charge": 2 * charges["H"] % order,
        "mu_HH_forbidden": 2 * charges["H"] % order != 2 % order,
    }


def anomaly_rows(order: int, charges: Mapping[str, int]) -> dict[str, Any]:
    """Conventional integrated 4D anomaly coefficients.

    The non-Abelian rows are doubled, so 2T(fundamental)=1.  The 126 and
    bar126 each have doubled index 70 for every equal-level PS factor.  The
    gravitational row contains the 4D gravitino (-21), the 21 PS plus one
    U(1)_F gauginos, and the displayed chiral fermions.  It does not contain
    an unspecified radion/gravity/Kaluza--Klein regulator sector.
    """

    r = charges
    common_126 = 70 * ((r["Delta126"] - 1) + (r["DeltaBar126"] - 1))
    a4 = (
        8
        + 6 * (r["Q"] - 1)
        + 6 * (r["Qc"] - 1)
        + 2
        * sum(
            r[name] - 1
            for name in ("A16_plus3", "Bbar16_minus12", "C16_minus3", "Dbar16_plus12")
        )
        + common_126
    )
    al = (
        4
        + 12 * (r["Q"] - 1)
        + 2 * (r["H"] - 1)
        + 4 * ((r["A16_plus3"] - 1) + (r["Bbar16_minus12"] - 1))
        + common_126
    )
    ar = (
        4
        + 12 * (r["Qc"] - 1)
        + 2 * (r["H"] - 1)
        + 4 * ((r["C16_minus3"] - 1) + (r["Dbar16_plus12"] - 1))
        + common_126
    )

    chiral_dims = {
        "Q": 24,
        "Qc": 24,
        "H": 4,
        "A16_plus3": 8,
        "Bbar16_minus12": 8,
        "C16_minus3": 8,
        "Dbar16_plus12": 8,
        "ThetaPlus": 1,
        "ThetaMinus": 1,
        "STheta": 1,
        "Delta126": 126,
        "DeltaBar126": 126,
        "SDelta": 1,
    }
    agrav = -21 + 22 + sum(chiral_dims[name] * (r[name] - 1) for name in chiral_dims)
    modulus = eta(order)
    doubled_modulus = 2 * modulus
    return {
        "normalization": "Atilde_G=2 A_G with 2T(fund)=1; standard eta=N for odd N and N/2 for even N.",
        "eta": modulus,
        "doubled_modulus": doubled_modulus,
        "common_126_shift_doubled": common_126,
        "doubled_nonabelian": {"SU4": a4, "SU2L": al, "SU2R": ar},
        "standard_nonabelian": {"SU4": a4 // 2, "SU2L": al // 2, "SU2R": ar // 2},
        "standard_residues_mod_eta": {
            "SU4": (a4 // 2) % modulus,
            "SU2L": (al // 2) % modulus,
            "SU2R": (ar // 2) % modulus,
        },
        "mixed_equal_level_universal": (a4 - al) % doubled_modulus == 0
        and (a4 - ar) % doubled_modulus == 0,
        "mixed_exact_no_GS": all(value % doubled_modulus == 0 for value in (a4, al, ar)),
        "gravity": agrav,
        "gravity_residue_mod_eta": agrav % modulus,
        "gravity_exact_screen": agrav % modulus == 0,
        "gravity_universal_GS_screen": (agrav - 12 * a4) % modulus == 0,
    }


def scan_integrated_candidates(max_order: int = 96) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for order in range(3, max_order + 1):
        witnesses: list[dict[str, Any]] = []
        for q in range(order):
            for qc in range(order):
                charges = charges_for(order, q, qc, t=0)
                terms = required_term_audit(order, charges)
                anomaly = anomaly_rows(order, charges)
                if not terms["all_allowed"] or not terms["mu_HH_forbidden"]:
                    continue
                if not anomaly["mixed_exact_no_GS"] or not anomaly["gravity_exact_screen"]:
                    continue
                witnesses.append(
                    {
                        "Q": q,
                        "Qc": qc,
                        "H": charges["H"],
                        "A16": charges["A16_plus3"],
                        "Bbar16": charges["Bbar16_minus12"],
                        "C16": charges["C16_minus3"],
                        "Dbar16": charges["Dbar16_plus12"],
                    }
                )
        if witnesses:
            rows.append(
                {
                    "order": order,
                    "eta": eta(order),
                    "number_of_charge_representatives": len(witnesses),
                    "first_representative": witnesses[0],
                }
            )
    return {
        "range": [3, max_order],
        "assumptions": [
            "ThetaPlus and ThetaMinus are R-neutral, so their nonzero VEVs preserve the full Z_N^R.",
            "Delta126 and DeltaBar126 are R-neutral and SDelta has charge two.",
            "The displayed four-dimensional zero-mode/brane spectrum is used; localized KK and gravity sectors are omitted.",
            "The mu bilinear H H is required to be absent.",
        ],
        "orders_passing_the_conventional_exact_integrated_screen": [row["order"] for row in rows],
        "rows": rows,
        "qualification": "Every candidate still allows the forced degree-20 oriented W operator and is not a 5D anomaly certificate.",
    }


def epsilon4_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def explicit_quartic_value() -> int:
    """Evaluate eps4 eps2 eps2 Q1 Q1 Q2 Q2 on one explicit field point."""

    q1 = [[int((a == 0 and i == 0) or (a == 1 and i == 1)) for i in range(2)] for a in range(4)]
    q2 = [[int((a == 2 and i == 0) or (a == 3 and i == 1)) for i in range(2)] for a in range(4)]
    eps2 = {(0, 1): 1, (1, 0): -1}
    value = 0
    for perm in itertools.permutations(range(4)):
        for (i, j), e1 in eps2.items():
            for (k, ell), e2 in eps2.items():
                value += (
                    epsilon4_sign(perm)
                    * e1
                    * e2
                    * q1[perm[0]][i]
                    * q1[perm[1]][j]
                    * q2[perm[2]][k]
                    * q2[perm[3]][ell]
                )
    return value


def forcing_theorem() -> dict[str, Any]:
    return {
        "assumptions": [
            "The three Q families have one charge q and the three Qc families one charge qc. A generic 3x3 Q_i H Qc_j matrix enforces this family universality.",
            "Q H Qc, ThetaPlus A16 Bbar16, and ThetaMinus C16 Dbar16 are allowed W terms.",
            "r(ThetaPlus)=t and r(ThetaMinus)=-t; no value of r(H)=h is assumed.",
            "The three PS factors have equal level and one universal GS residue, so A4=A2L=A2R mod eta.",
            "Any 126/bar126 or other complete-Spin10 threshold contributes the same common shift C to all three mixed rows.",
        ],
        "required_congruences_mod_N": [
            "q+qc+h=2",
            "a+b+t=2",
            "c+d-t=2",
        ],
        "doubled_rows_mod_2eta": {
            "A4": "8-6h+C",
            "A2L": "12q+2h-10-4t+C",
            "A2R": "12qc+2h-10+4t+C",
        },
        "difference_equations_mod_2eta": [
            "A4-A2L = 18-8h-12q+4t = 0",
            "A4-A2R = -6+4h+12q-4t = 0 after qc=2-h-q",
        ],
        "deduction": [
            "Adding the two differences gives 12-4h=0 mod 2eta.",
            "Substitution gives 12q+6-4t=0 mod 2eta and therefore mod N.",
            "The conjugate equation is 12qc+6+4t=0 mod N.",
        ],
        "plus_witness": {
            "operator": "[eps4 eps2 eps2 Q1 Q1 Q2 Q2]^3 [delta4 eps2 LF LA]^4",
            "degree": 20,
            "orientation": 12,
            "U1F": 12 * 3 + 4 * (3 - 12),
            "R_charge": "12q+4(a+b)=12q+8-4t=2 mod N",
            "explicit_nonzero_quartic_evaluation": explicit_quartic_value(),
        },
        "minus_witness": {
            "operator": "[eps4 eps2 eps2 Qc1 Qc1 Qc2 Qc2]^3 [delta4 eps2 RA RF]^4",
            "degree": 20,
            "orientation": -12,
            "U1F": 12 * (-3) + 4 * (-3 + 12),
            "R_charge": "12qc+4(c+d)=12qc+8+4t=2 mod N",
        },
        "conclusion": "No Z_N^R satisfying these equal-level universal mixed-anomaly conditions can forbid both first oriented degree-20 local invariants.",
        "escape_routes_not_solutions": [
            "family-nonuniversal R charges together with a rebuilt flavour/Yukawa texture",
            "nonuniversal localized GS axions or boundary counterterms with explicit quantized couplings",
            "a changed light chiral spectrum or changed required mass/Yukawa couplings",
            "an R-breaking rather than exact-R mass threshold",
        ],
    }


def massive_packet_statement() -> dict[str, Any]:
    return {
        "claim": "An ordinary symmetry-preserving massive vectorlike PS packet cannot repair the congruence no-go.",
        "complex_pair_proof": "For X in R and Xbar in barR, an invariant nondegenerate mass requires rX+rXbar=2 mod N. Its mixed contribution is T(R)[(rX-1)+(rXbar-1)]=0 mod eta.",
        "real_or_pseudoreal_qualification": "A permitted Majorana/Pfaffian block obeys the analogous mass-determinant condition; its perturbative mixed anomaly shift is trivial modulo eta. A nontrivial gapped topological sector would be new microscopic input, not an ordinary massive matter packet.",
        "smallest_honest_rep_comment": "A (1,2,2) is honest under the PS diagonal Z2 and can change SU2L/R rows only if it remains R-chiral. If its exact-R mass is allowed, its anomaly shift is trivial; if not, it is an added light field or needs R breaking.",
        "valid_massive_repair_found": False,
    }


def benchmark_rows() -> dict[str, Any]:
    z4 = charges_for(4, 1, 1)
    z5 = charges_for(5, 2, 2)
    z6 = charges_for(6, 1, 1)
    return {
        "inherited_Z4R": {
            "charges": z4,
            "terms": required_term_audit(4, z4),
            "anomalies": anomaly_rows(4, z4),
            "verdict": "Required terms pass, but the mixed PS residues are nonuniversal; this is not an exact/one-axion-GS completion.",
        },
        "Z5R_integrated_screen": {
            "charges": z5,
            "terms": required_term_audit(5, z5),
            "anomalies": anomaly_rows(5, z5),
            "dangerous_126_portal_charges": {
                "A16_C16_DeltaBar126": term_charge(5, z5, ("A16_plus3", "C16_minus3", "DeltaBar126")),
                "Bbar16_Dbar16_Delta126": term_charge(5, z5, ("Bbar16_minus12", "Dbar16_plus12", "Delta126")),
            },
            "degree20_plus_R_charge": (12 * z5["Q"] + 4 * (z5["A16_plus3"] + z5["Bbar16_minus12"])) % 5,
            "verdict": "A clean conventional integrated no-GS screen, not a 5D completion; the degree-20 oriented W witness is allowed.",
        },
        "Z6R_integrated_screen": {
            "charges": z6,
            "terms": required_term_audit(6, z6),
            "anomalies": anomaly_rows(6, z6),
            "contains_matter_parity_pattern": True,
            "degree20_plus_R_charge": (12 * z6["Q"] + 4 * (z6["A16_plus3"] + z6["Bbar16_minus12"])) % 6,
            "verdict": "The minimal even integrated screen passes and contains the usual odd-spinor/even-H pattern, but it allows both 126-spinor portals and the degree-20 oriented W witness.",
        },
    }


def build_report() -> dict[str, Any]:
    report: dict[str, Any] = {
        "status": STATUS,
        "scope": "Family-universal discrete-R charge search for the reconciled minimal V45 core; conventional integrated anomaly screen and exact orientation theorem only.",
        "conventions": {
            "superpotential_charge": 2,
            "eta": "N for odd N; N/2 for even N",
            "mixed_anomaly": "A_G=sum T(R_i)(r_i-1)+T(adj); calculations store Atilde_G=2A_G",
            "universal_GS": "equal PS levels and one residue rho: A4=A2L=A2R=rho mod eta; A_grav=24rho mod eta",
        },
        "benchmarks": benchmark_rows(),
        "finite_integrated_search": scan_integrated_candidates(96),
        "degree20_forcing_theorem": forcing_theorem(),
        "massive_packet_no_go": massive_packet_statement(),
        "fail_closed_boundary": {
            "localized_bulk_and_boundary_discrete_anomalies_computed": False,
            "KK_eta_and_quantized_inflow_computed": False,
            "Spin_ZNR_bordism_for_actual_global_quotient_computed": False,
            "complete_5D_gravity_radion_regulator_spectrum_computed": False,
            "candidate_promoted_to_exact_5D_symmetry": False,
            "gates_promoted": [],
            "reason": "Integrated residues are necessary arithmetic only. Bulk hypermultiplets, orbifold parities, boundary gauginos, heavy KK thresholds, the gravity/radion sector, and the actual Spin^Z_N global structure can change or obstruct the localized/global answer.",
        },
        "primary_sources": [
            {
                "title": "Lee et al., Discrete R symmetries for the MSSM and its singlet extensions",
                "url": "https://arxiv.org/abs/1102.3595",
                "supports": "standard discrete-R anomaly coefficients, eta convention, and anomaly universality",
            },
            {
                "title": "Dine and Monteux, Discrete R Symmetries and Anomalies",
                "url": "https://arxiv.org/abs/1212.4371",
                "supports": "dependence of low-energy anomaly claims on microscopic GS fields and heavy thresholds",
            },
            {
                "title": "von Gersdorff and Quiros, Localized anomalies in orbifold gauge theories",
                "url": "https://arxiv.org/abs/hep-th/0305024",
                "supports": "localized orbifold anomaly and inflow constraints",
            },
            {
                "title": "Witten and Yonekura, Anomaly Inflow and the eta-Invariant",
                "url": "https://arxiv.org/abs/1909.08775",
                "supports": "global anomaly/inflow information beyond local anomaly polynomials",
            },
        ],
        "decision": {
            "inherited_Z4R_retained_as_exact": False,
            "some_integrated_exact_candidates_exist": True,
            "any_candidate_forbids_first_oriented_local_W_invariant": False,
            "ordinary_exact_R_massive_packet_repair_exists": False,
            "discrete_R_sector_complete": False,
            "G1_closed": False,
            "G7_closed": False,
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def markdown(data: Mapping[str, Any]) -> str:
    z4 = data["benchmarks"]["inherited_Z4R"]
    z5 = data["benchmarks"]["Z5R_integrated_screen"]
    z6 = data["benchmarks"]["Z6R_integrated_screen"]
    scan = data["finite_integrated_search"]
    return f"""# V45 discrete-R audit

Status: `{data['status']}`

## Result

The inherited assignment (all spinorial superfields charge one, `H=0`,
`Theta+=Theta-=0`) is **not** a completed `Z4R`: its conventional mixed
Pati--Salam residues are
`{z4['anomalies']['standard_residues_mod_eta']}` at `eta=2`, so they are not
universal.

Alternative integrated candidates do exist.  With neutral Theta and 126
VEVs, an `SDelta` charge-two driver, a forbidden bare `H H`, and the displayed
four-dimensional spectrum, the exact no-GS scan through order 96 finds
orders `{scan['orders_passing_the_conventional_exact_integrated_screen']}`.
For example, `Z5R` with

`Q=Qc=A16=C16=2`, `H=3`, `Bbar16=Dbar16=0`

has mixed rows `{z5['anomalies']['standard_nonabelian']}` and gravity row
`{z5['anomalies']['gravity']}`, all zero modulo `eta=5`.  The minimal even
screen is the `Z6R` odd-spinor/even-H pattern, with residues
`{z6['anomalies']['standard_residues_mod_eta']}`.  These are necessary
integrated screens, not five-dimensional anomaly certificates.

## Exact degree-20 no-go

Let the family-universal charges be `q,qc,h`, let `t=r(ThetaPlus)` and
`r(ThetaMinus)=-t`, and write the four bulk-spinor charges as `a,b,c,d`.
The required terms imply, modulo `N`,

`q+qc+h=2`, `a+b+t=2`, `c+d-t=2`.

In doubled-index normalization, up to any common complete-Spin(10) shift
`C`,

`A4=8-6h+C`,
`A2L=12q+2h-10-4t+C`,
`A2R=12qc+2h-10+4t+C`.

Equal-level anomaly universality is imposed modulo `2 eta`.  The two
differences give

`18-8h-12q+4t=0`,
`-6+4h+12q-4t=0`.

Their sum gives `12-4h=0`; substitution then gives

`12q+6-4t=0 mod 2 eta`, and therefore modulo `N`.

Now define the nonzero quartic

`P_Q = eps4 eps2 eps2 Q1 Q1 Q2 Q2`.

It evaluates to `{data['degree20_forcing_theorem']['plus_witness']['explicit_nonzero_quartic_evaluation']}`
on the explicit unit-column field point stored in the audit.  Therefore

`O+ = P_Q^3 (LF LA)^4`

is a nonzero local PS singlet of degree 20, exact `U(1)_F` charge zero and
orientation `+12`.  Its R charge is forced to

`12q+4(a+b)=12q+8-4t=2 mod N`.

The conjugate `O- = P_Qc^3 (RA RF)^4` is forced in the same way.  This proof
does **not** assume `h=0`, and a neutral 126 pair cannot change it because its
mixed-anomaly shift is common to all three PS factors.

Thus no family-universal, equal-level, single-residue `Z_N^R` on the current
field core can both satisfy the required terms and forbid the first oriented
degree-20 local superpotential invariant.

## Why a massive matter patch does not fix it

For a complex vectorlike pair, an exact-R mass requires
`r_X+r_Xbar=2 mod N`.  Its mixed anomaly is then
`T(R)[(r_X-1)+(r_Xbar-1)]=0 mod eta`.  The analogous determinant statement
holds for real or pseudoreal mass blocks.  Consequently, an ordinary
symmetry-preserving massive PS packet cannot alter the congruence responsible
for the no-go.  A chiral light packet, an R-breaking threshold, or a
nonuniversal localized GS/topological sector would be new physics, but none is
an instantiated solution here.

## Fail-closed boundary

No candidate is promoted to an exact 5D symmetry.  The parity-resolved local
anomaly density, quantized inflow/KK eta invariant, full gravity/radion
spectrum, and `Spin^Z_N` bordism class for the actual PS quotient remain
uncomputed.  No G1 or G7 gate is closed.

Conventions and microscopic caveats follow
[Lee et al.](https://arxiv.org/abs/1102.3595),
[Dine--Monteux](https://arxiv.org/abs/1212.4371), localized-orbifold anomaly
constraints follow [von Gersdorff--Quiros](https://arxiv.org/abs/hep-th/0305024),
and the global inflow caveat follows
[Witten--Yonekura](https://arxiv.org/abs/1909.08775).

Core SHA-256: `{data['core_sha256']}`
"""


def validate(data: Mapping[str, Any]) -> None:
    if data.get("status") != STATUS or canonical_sha(data) != data.get("core_sha256"):
        raise RuntimeError("stale discrete-R report")
    if explicit_quartic_value() == 0:
        raise RuntimeError("degree-four epsilon witness vanished")
    z4 = data["benchmarks"]["inherited_Z4R"]
    if z4["anomalies"]["mixed_equal_level_universal"]:
        raise RuntimeError("inherited Z4R unexpectedly universal")
    for name in ("Z5R_integrated_screen", "Z6R_integrated_screen"):
        row = data["benchmarks"][name]
        if not row["terms"]["all_allowed"] or not row["terms"]["mu_HH_forbidden"]:
            raise RuntimeError(f"{name} term regression")
        if not row["anomalies"]["mixed_exact_no_GS"] or not row["anomalies"]["gravity_exact_screen"]:
            raise RuntimeError(f"{name} integrated anomaly regression")
        if row["degree20_plus_R_charge"] != 2 % int(name[1 : name.index('R')]):
            raise RuntimeError(f"{name} lost forced witness")
    if data["finite_integrated_search"]["orders_passing_the_conventional_exact_integrated_screen"] != [3, 5, 6, 10, 15, 30]:
        raise RuntimeError("integrated candidate scan regression")
    theorem = data["degree20_forcing_theorem"]
    if theorem["plus_witness"]["U1F"] or theorem["minus_witness"]["U1F"]:
        raise RuntimeError("degree-20 witness is not U1F neutral")
    if data["massive_packet_no_go"]["valid_massive_repair_found"]:
        raise RuntimeError("unsupported massive repair promoted")
    if data["decision"]["G1_closed"] or data["decision"]["G7_closed"]:
        raise RuntimeError("gate promoted by a necessary screen")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_report()
    validate(data)
    json_text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    md_text = markdown(data)
    if args.write:
        JSON_PATH.write_text(json_text, encoding="utf-8")
        MD_PATH.write_text(md_text, encoding="utf-8")
        print("SUSY V45 discrete-R audit: wrote certificates")
    if args.check:
        if not JSON_PATH.exists() or not MD_PATH.exists():
            raise SystemExit("generated certificates missing; run --write")
        if JSON_PATH.read_text(encoding="utf-8") != json_text or MD_PATH.read_text(encoding="utf-8") != md_text:
            raise SystemExit("generated certificates stale; run --write")
        print("SUSY V45 discrete-R audit: PASS")


if __name__ == "__main__":
    main()
