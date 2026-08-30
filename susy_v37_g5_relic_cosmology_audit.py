#!/usr/bin/env python3
"""Fail-closed G5 audit for the V37 residual-discrete relic problem.

This is deliberately not a cosmological promotion.  It proves the exact
residual-charge obstruction in the published V37 spectrum and records the
smallest *charge-class* completion found here that lets every anomalon block
decay without weakening the V37 selector or its polynomial PQ-quality bound.
The remaining mass spectrum, mediation and Boltzmann evolution are explicit
inputs, rather than being silently assumed away.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import susy_v37_new_physics_routes as v37


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V37_G5_RELIC_COSMOLOGY_AUDIT.json"
MD_PATH = ROOT / "SUSY_V37_G5_RELIC_COSMOLOGY_AUDIT.md"

N66 = 66
N85 = 85
N5610 = N66 * N85
NRES = 170
FPQ_GEV = 5.0e11
MRED_GEV = 2.4e18

# (q66, Z4R superfield charge, h85, optimized PQ numerator / 170).
# The candidate has three inverse-charge dark pairs, one for each inequivalent
# residual charge class.  A bar is a field name, not a complex conjugation.
# The pre-existing driver X is the neutral mediator.  Reusing it avoids adding
# a new neutral field with an unconstrained linear superpotential tadpole.
EXTENSION_FIELDS: dict[str, tuple[int, int, int, int]] = {
    "D2": (29, 0, 84, 23),
    "Db2": (37, 2, 1, -23),
    "D17": (65, 2, 69, 113),
    "Db17": (1, 0, 16, -113),
    "D16": (1, 0, 0, 85),
    "Db16": (65, 2, 0, -85),
}

FIELDS = {**v37.ALL_CHIRAL_FIELDS, **EXTENSION_FIELDS}

# Each displayed monomial has exact q66=h85=0, Z4R charge 2, and PQ charge 0.
DECAY_COMPLETION_TERMS: dict[str, tuple[str, ...]] = {
    "mu2_D2_Db2": ("D2", "Db2"),
    "mu17_D17_Db17": ("D17", "Db17"),
    "mu16_D16_Db16": ("D16", "Db16"),
    "decay_A2": ("X", "A2", "D2"),
    "decay_A32": ("Pbar", "X", "A32", "Db2"),
    "decay_A17": ("X", "A17", "D17"),
    "decay_A15": ("P", "X", "A15", "Db17"),
    "decay_A16": ("X", "A16", "D16"),
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_sha(value: dict[str, Any]) -> str:
    body = copy.deepcopy(value)
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def q5610(q66: int, h85: int) -> int:
    return v37.combined_charge(q66, h85)


def residual_charge(name: str) -> int:
    q66, _r4, h85, _pq = FIELDS[name]
    return q5610(q66, h85) % NRES


def term_audit(term: Iterable[str]) -> dict[str, int | bool]:
    names = tuple(term)
    q66_sum = sum(FIELDS[name][0] for name in names) % N66
    r_sum = sum(FIELDS[name][1] for name in names) % 4
    h_sum = sum(FIELDS[name][2] for name in names) % N85
    pq_sum = sum(FIELDS[name][3] for name in names)
    return {
        "q66_mod66": q66_sum,
        "Z4R_mod4": r_sum,
        "h85_mod85": h_sum,
        "PQ_numerator_over_170": pq_sum,
        "selector_and_PQ_invariant": q66_sum == 0 and r_sum == 2 and h_sum == 0 and pq_sum == 0,
    }


def charge_class(charge: int) -> tuple[int, int]:
    return tuple(sorted((charge % NRES, (-charge) % NRES)))


def hsieh_rows() -> list[dict[str, int | str]]:
    base = [
        ("PsiBar", 8, 64, 0),
        ("PsiCBar", 8, 64, 0),
        ("P", 1, 2, 0),
        ("Pbar", 1, 64, 0),
        ("A2", 1, 37, 1),
        ("A32", 1, 31, 84),
        ("A15", 1, 63, 69),
        ("A17", 1, 1, 16),
        ("A16", 1, 65, 0),
    ]
    rows: list[dict[str, int | str]] = [
        {"field": name, "multiplicity": mult, "charge": q5610(q66, h85)}
        for name, mult, q66, h85 in base
    ]
    rows.extend(
        {
            "field": name,
            "multiplicity": 1,
            "charge": q5610(q66, h85),
        }
        for name, (q66, _r4, h85, _pq) in EXTENSION_FIELDS.items()
    )
    return rows


def extension_mixed_r_h2() -> int:
    # Use signed representatives so the pairwise cancellation is transparent.
    signed_h = {"D2": -1, "Db2": 1, "D17": 69, "Db17": -69, "D16": 0, "Db16": 0}
    return sum((EXTENSION_FIELDS[name][1] - 1) * h * h for name, h in signed_h.items())


def quality_congruence_residues() -> dict[str, int]:
    return {
        name: (pq - (N85 * q66 + 2442 * h85)) % N5610
        for name, (q66, _r4, h85, pq) in EXTENSION_FIELDS.items()
    }


def suppressed_decay_width(mass_gev: float, kappa: float) -> dict[str, float]:
    """Two-body width estimate for a P/M-suppressed decay, with phase space set to 1."""

    epsilon = FPQ_GEV / (math.sqrt(2.0) * MRED_GEV)
    width = kappa * kappa * epsilon * epsilon * mass_gev / (16.0 * math.pi)
    return {
        "epsilon_fPQ_over_sqrt2Mred": epsilon,
        "mass_GeV": mass_gev,
        "kappa": kappa,
        "width_GeV": width,
        "lifetime_seconds": 6.582119569e-25 / width,
    }


def report() -> dict[str, Any]:
    core_residual = {
        name: residual_charge(name)
        for name in v37.ALL_CHIRAL_FIELDS
        if residual_charge(name) != 0
    }
    anomalon_class_tuples = {
        "A2_A32": charge_class(residual_charge("A2")),
        "A15_A17": charge_class(residual_charge("A15")),
        "A16": charge_class(residual_charge("A16")),
    }
    # Use JSON-native lists in the report so --check can compare a reloaded
    # certificate structurally rather than relying on tuple serialization.
    anomalon_classes = {
        name: list(values) for name, values in anomalon_class_tuples.items()
    }
    extended_w = v37._state_space_first_breaking(False, 33, FIELDS)
    extended_k = v37._state_space_first_breaking(True, 33, FIELDS)
    rows = hsieh_rows()
    hsieh = v37.hsieh_audit(N5610, rows)  # type: ignore[arg-type]
    decay_terms = {name: term_audit(term) for name, term in DECAY_COMPLETION_TERMS.items()}
    suppressed = suppressed_decay_width(1.0e3, 1.0)

    data: dict[str, Any] = {
        "schema": "susy-v37-g5-relic-cosmology-audit-v1",
        "scope": "Exact residual-relic obstruction plus a conditional symmetry-preserving decay/dark-sector construction; not a full cosmology.",
        "residual_relic_theorem": {
            "PQ_breaking_charges": {"P": q5610(2, 0), "Pbar": q5610(64, 0)},
            "unbroken_group": "Z_gcd(5610,170)=Z170 ~= Z2 x Z85",
            "unbroken_order": math.gcd(N5610, q5610(2, 0)),
            "nontrivially_charged_core_fields": core_residual,
            "all_non_anomalon_core_fields_neutral": set(core_residual) == {"A2", "A32", "A15", "A17", "A16"},
            "inverse_charge_classes": anomalon_classes,
            "inequivalent_charge_class_count": len(set(anomalon_class_tuples.values())),
            "exact_consequence": (
                "No state with a nonzero Z170 charge can decay solely to the V37 core fields outside "
                "the anomalon sector.  Hence at least one stable residual-charge relic exists in the "
                "unextended EFT; if it was thermal and m >> 3.4e5 GeV, standard thermal freeze-out is excluded by partial-wave unitarity."
            ),
            "proof_boundary": (
                "The statement is charge conservation only.  It does not assume a particular mass ordering, "
                "nor does it claim every anomalon is absolutely stable against multi-anomalon final states."
            ),
        },
        "conditional_decay_dark_extension": {
            "new_chiral_field_count": len(EXTENSION_FIELDS),
            "new_fields": {
                name: {
                    "q66": values[0],
                    "Z4R": values[1],
                    "h85": values[2],
                    "PQ_numerator_over_170": values[3],
                    "q5610": q5610(values[0], values[2]),
                    "residual_Z170": residual_charge(name),
                }
                for name, values in EXTENSION_FIELDS.items()
            },
            "construction_logic": (
                "D2, D17 and D16 carry the inverse residual charges of one representative of each "
                "inequivalent anomalon block.  Their vectorlike partners make the selector anomaly-safe; "
                "the pre-existing neutral driver X mediates the visible decay operators.  This is a sufficient "
                "six-field construction, not a proof of global minimality among all UV completions."
            ),
            "superpotential_terms": {name: list(term) for name, term in DECAY_COMPLETION_TERMS.items()},
            "term_audits": decay_terms,
            "all_terms_exactly_invariant": all(item["selector_and_PQ_invariant"] for item in decay_terms.values()),
            "selector_PQ_congruence_residues": quality_congruence_residues(),
            "all_new_fields_obey_selector_PQ_congruence": not any(quality_congruence_residues().values()),
            "full_Z5610_Hsieh_Dai_Freed": hsieh,
            "extension_increment_mixed_Z4R_Z85_squared": extension_mixed_r_h2(),
            "quality_lattice": {
                "superpotential_first_breaking_degree": extended_w["first_breaking_degree"],
                "superpotential_witness": extended_w["witness_multiplicities"],
                "Kahler_first_breaking_degree": extended_k["first_breaking_degree"],
                "Kahler_witness": extended_k["witness_multiplicities"],
                "quality_preserved_relative_to_V37": (
                    extended_w["first_breaking_degree"] == 33 and extended_k["first_breaking_degree"] == 32
                ),
            },
            "BBN_decay_scale_example": {
                "description": "The two P/Mred operators after <P>=<Pbar>=fPQ/sqrt2 have this phase-space-one estimate.",
                **suppressed,
                "before_one_second_for_kappa_one_and_mass_one_TeV": suppressed["lifetime_seconds"] < 1.0,
            },
        },
        "soft_vacuum_and_cosmology_boundary": {
            "vacuum_status": (
                "No generic added-sector vacuum lemma is claimed.  X has selector-allowed linear and cubic "
                "terms, and the D-sector scalar potential depends on the unprovided Kahler and mediation data."
            ),
            "why_this_is_not_an_actual_matching_result": (
                "V37 specifies no mediation sector or complete Kahler potential, and electroweak H vevs, A/B terms, "
                "and Planck-suppressed coefficients have not been matched.  The displayed decay estimate is a conditional "
                "kinematic check, not a derived cosmological boundary condition."
            ),
            "thermal_relic_limit_GeV": 3.4e5,
            "thermal_relic_source": "Griest--Kamionkowski partial-wave unitarity bound for an elementary thermal relic",
            "observed_DM_target_Omega_h2": 0.120,
            "observed_DM_source": "Planck 2018 cosmological parameters",
            "viable_histories_not_yet_computed": [
                "a secluded multi-component WIMP calculation using the X/H portal and the full scalar/fermion spectrum",
                "or a low-reheat/nonthermal history with explicit inflaton branching fractions",
                "PQ restoration, isocurvature, domain-wall, and entropy-dilution evolution",
                "late-decay, BBN, CMB, direct-detection, and dark-radiation likelihoods",
            ],
        },
        "promotion": {
            "G5_closed": False,
            "reason": (
                "The candidate moves the unavoidable residual charge into dark carriers, but their masses, mediation, "
                "Boltzmann evolution, and full vacuum have not been supplied.  A real G5 promotion would require those "
                "calculations at one explicit parameter point."
            ),
            "defensible_result": "V37 core alone is cosmologically incomplete; the displayed extension is a symmetry- and quality-safe route, not a completed theory.",
        },
    }
    data["core_sha256"] = canonical_sha(data)
    return data


def markdown(data: dict[str, Any]) -> str:
    theorem = data["residual_relic_theorem"]
    candidate = data["conditional_decay_dark_extension"]
    boundary = data["soft_vacuum_and_cosmology_boundary"]
    return f"""# SUSY V37 G5 residual-relic and cosmology audit

## Exact result

The `P,Pbar` VEV leaves `Z170 ~= Z2 x Z85`.  Every core field except
`A2,A32,A15,A17,A16` is neutral under it.  Their inverse-charge classes are
`{theorem['inverse_charge_classes']}`; there are therefore three inequivalent
anomalon charge classes.  A nonzero-charge state cannot decay only to the rest
of the V37 core.  This proves an extension-free stable-relic obstruction, but
does not assert that every anomalon is separately stable for every mass order.

## Conditional extension

The six-field `D2,Db2,D17,Db17,D16,Db16` construction reuses the existing `X`
driver to give a decay route for each class.  All listed terms pass the exact `Z66`, `Z85`, `Z4R`, and
optimized-PQ checks; the full finite Hsieh/Dai--Freed audit remains true.  The
all-chiral lattice first breaks PQ at W degree
`{candidate['quality_lattice']['superpotential_first_breaking_degree']}` and
Kahler degree `{candidate['quality_lattice']['Kahler_first_breaking_degree']}`.
The P/M-suppressed decay benchmark has lifetime
`{candidate['BBN_decay_scale_example']['lifetime_seconds']:.3e}` s for a
1-TeV parent and unit coefficient, far before BBN.

## Fail-closed boundary

This is not a G5 closure.  The candidate leaves stable dark carriers and needs
a spectrum, soft mediation, global vacuum calculation, and a numerical
Boltzmann/reheating history.  A standard thermal relic much heavier than
`{boundary['thermal_relic_limit_GeV']:.1e}` GeV cannot be rescued by ordinary
elementary-particle freeze-out alone.  The observed target used for a future
calculation is `Omega_c h^2={boundary['observed_DM_target_Omega_h2']}`.

Sources: [Griest--Kamionkowski thermal-relic unitarity bound](https://ntrs.nasa.gov/citations/19900004848);
[Planck 2018 cosmological parameters](https://arxiv.org/abs/1807.06209).

Core SHA-256: `{data['core_sha256']}`
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = report()
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    if args.write:
        JSON_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MD_PATH.write_text(markdown(data), encoding="utf-8")
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise SystemExit("generated G5 certificate is missing; run with --write")
        on_disk = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        if on_disk != data:
            raise SystemExit("generated G5 JSON is stale; run with --write")
        if MD_PATH.read_text(encoding="utf-8") != markdown(data):
            raise SystemExit("generated G5 Markdown is stale; run with --write")
        print("SUSY V37 G5 relic-cosmology audit: PASS")
        return
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
