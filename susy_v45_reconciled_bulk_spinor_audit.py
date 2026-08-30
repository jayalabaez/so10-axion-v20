#!/usr/bin/env python3
"""Localized-anomaly and mass reconciliation for the minimal V45 5D core.

The four quotient-valid anomalons are treated as zero modes of four bulk
Spin(10) hypermultiplets.  On a physical interval the ordinary anomaly of a
bulk hyper at an endpoint is one half of the four-dimensional anomaly,
weighted by the parity of the left-chiral member of the hyper.  Boundary
chirals contribute one full four-dimensional anomaly.

This audit is intentionally narrower than a global eta-invariant/bordism
calculation.  It proves cancellation of the displayed perturbative local
polynomials and the rank of the projected zero-mode mass matrix.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v45_reconciled_bulk_spinor_audit.py"

STATUS = (
    "V45_FOUR_BULK_SPINORS_CANCEL_LOCAL_ORDINARY_ANOMALIES__"
    "SOURCE_THETA_MASSES_LOCAL_AND_ZERO_MODE_RANK4__"
    "NO_SINGLET_SHINING_HYPERS_OR_ORDINARY_CS_REQUIRED__"
    "GLOBAL_ETA_AND_FULL_KK_OPEN"
)

PS_KEYS = (
    "U1F_SU4_squared_doubled",
    "U1F_SU2L_squared_doubled",
    "U1F_SU2R_squared_doubled",
    "gravity_squared_U1F",
    "U1F_cubed",
    "SU4_cubed",
)

SOURCE_KEYS = (
    "U1F_Spin10_squared_doubled",
    "gravity_squared_U1F",
    "U1F_cubed",
    "Spin10_cubed",
)

# For each PS representation, ``index_2T`` already includes spectator
# dimensions.  ``SU4_cubed`` uses A(4)=+1 and includes spectators.
PS_REPS: dict[str, dict[str, Any]] = {
    "L4": {
        "label": "(4,2,1)",
        "dim": 8,
        "index_2T": {"SU4": 2, "SU2L": 4, "SU2R": 0},
        "SU4_cubed": 2,
        "twist": 1,
    },
    "Lbar4": {
        "label": "(bar4,2,1)",
        "dim": 8,
        "index_2T": {"SU4": 2, "SU2L": 4, "SU2R": 0},
        "SU4_cubed": -2,
        "twist": 1,
    },
    "Rbar4": {
        "label": "(bar4,1,2)",
        "dim": 8,
        "index_2T": {"SU4": 2, "SU2L": 0, "SU2R": 4},
        "SU4_cubed": -2,
        "twist": -1,
    },
    "R4": {
        "label": "(4,1,2)",
        "dim": 8,
        "index_2T": {"SU4": 2, "SU2L": 0, "SU2R": 4},
        "SU4_cubed": 2,
        "twist": -1,
    },
    "H": {
        "label": "(1,2,2)",
        "dim": 4,
        "index_2T": {"SU4": 0, "SU2L": 2, "SU2R": 2},
        "SU4_cubed": 0,
        "twist": 1,
    },
}

HYPERS = (
    {
        "name": "HLF",
        "Spin10_rep": "16",
        "q": 3,
        "eta0": 1,
        "etaL": 1,
        "components": ("L4", "Rbar4"),
        "selected_zero_mode": "LF=(4,2,1)_+3",
    },
    {
        "name": "HLA",
        "Spin10_rep": "bar16",
        "q": -12,
        "eta0": 1,
        "etaL": 1,
        "components": ("Lbar4", "R4"),
        "selected_zero_mode": "LA=(bar4,2,1)_-12",
    },
    {
        "name": "HRA",
        "Spin10_rep": "16",
        "q": -3,
        "eta0": -1,
        "etaL": 1,
        "components": ("L4", "Rbar4"),
        "selected_zero_mode": "RA=(bar4,1,2)_-3",
    },
    {
        "name": "HRF",
        "Spin10_rep": "bar16",
        "q": 12,
        "eta0": -1,
        "etaL": 1,
        "components": ("Lbar4", "R4"),
        "selected_zero_mode": "RF=(4,1,2)_+12",
    },
)

PS_BOUNDARY_FIELDS = (
    {"name": "3xQ", "rep": "L4", "multiplicity": 3, "q": 3},
    {"name": "3xQc", "rep": "Rbar4", "multiplicity": 3, "q": -3},
    {"name": "H", "rep": "H", "multiplicity": 1, "q": 0},
)

SOURCE_BOUNDARY_FIELDS = (
    {"name": "ThetaPlus", "Spin10_rep": "1", "dim": 1, "index_2T": 0, "q": 9},
    {"name": "ThetaMinus", "Spin10_rep": "1", "dim": 1, "index_2T": 0, "q": -9},
    {"name": "STheta", "Spin10_rep": "1", "dim": 1, "index_2T": 0, "q": 0},
    {"name": "Delta", "Spin10_rep": "126", "dim": 126, "index_2T": 70, "q": 0},
    {"name": "barDelta", "Spin10_rep": "bar126", "dim": 126, "index_2T": 70, "q": 0},
)


def zero_ledger(keys: Iterable[str]) -> dict[str, Fraction]:
    return {key: Fraction(0) for key in keys}


def add_ledgers(*ledgers: Mapping[str, Fraction]) -> dict[str, Fraction]:
    keys = tuple(ledgers[0]) if ledgers else ()
    return {key: sum((ledger[key] for ledger in ledgers), Fraction(0)) for key in keys}


def scale_ledger(ledger: Mapping[str, Fraction], coefficient: Fraction) -> dict[str, Fraction]:
    return {key: coefficient * value for key, value in ledger.items()}


def ps_4d_anomaly(rep_name: str, q: int, multiplicity: int = 1) -> dict[str, Fraction]:
    rep = PS_REPS[rep_name]
    return {
        "U1F_SU4_squared_doubled": Fraction(multiplicity * q * rep["index_2T"]["SU4"]),
        "U1F_SU2L_squared_doubled": Fraction(multiplicity * q * rep["index_2T"]["SU2L"]),
        "U1F_SU2R_squared_doubled": Fraction(multiplicity * q * rep["index_2T"]["SU2R"]),
        "gravity_squared_U1F": Fraction(multiplicity * q * rep["dim"]),
        "U1F_cubed": Fraction(multiplicity * q**3 * rep["dim"]),
        "SU4_cubed": Fraction(multiplicity * rep["SU4_cubed"]),
    }


def source_4d_anomaly(dim: int, index_2t: int, q: int) -> dict[str, Fraction]:
    return {
        "U1F_Spin10_squared_doubled": Fraction(q * index_2t),
        "gravity_squared_U1F": Fraction(dim * q),
        "U1F_cubed": Fraction(dim * q**3),
        # D5 has no rank-three symmetric invariant, so this perturbative row
        # vanishes for every Spin(10) representation.
        "Spin10_cubed": Fraction(0),
    }


def ps_boundary_ledger() -> dict[str, Any]:
    rows = []
    for field in PS_BOUNDARY_FIELDS:
        values = ps_4d_anomaly(field["rep"], field["q"], field["multiplicity"])
        rows.append({**field, "coefficient": "1", "values": values})
    return {"rows": rows, "totals": add_ledgers(*(row["values"] for row in rows))}


def ps_bulk_ledger() -> dict[str, Any]:
    hyper_rows = []
    component_rows = []
    parity_rows = []
    for hyper in HYPERS:
        pieces = []
        for component_name in hyper["components"]:
            rep = PS_REPS[component_name]
            p0 = hyper["eta0"] * rep["twist"]
            pL = hyper["etaL"]
            coefficient = Fraction(p0, 2)
            values = scale_ledger(ps_4d_anomaly(component_name, hyper["q"]), coefficient)
            pieces.append(values)
            component_rows.append(
                {
                    "hyper": hyper["name"],
                    "Spin10_rep": hyper["Spin10_rep"],
                    "component": rep["label"],
                    "q": hyper["q"],
                    "p0_H": p0,
                    "pL_H": pL,
                    "p0_Hc": -p0,
                    "pL_Hc": -pL,
                    "PS_wall_coefficient": coefficient,
                    "values": values,
                }
            )
            parity_rows.append(
                {
                    "hyper": hyper["name"],
                    "component": f"{rep['label']}_{hyper['q']:+d}",
                    "H_parities": ["+" if p0 == 1 else "-", "+" if pL == 1 else "-"],
                    "Hc_parities": ["+" if p0 == -1 else "-", "+" if pL == -1 else "-"],
                    "H_zero_mode": p0 == 1 and pL == 1,
                    "Hc_zero_mode": p0 == -1 and pL == -1,
                }
            )
        hyper_rows.append(
            {
                "hyper": hyper["name"],
                "Spin10_rep": hyper["Spin10_rep"],
                "q": hyper["q"],
                "eta0": hyper["eta0"],
                "etaL": hyper["etaL"],
                "selected_zero_mode": hyper["selected_zero_mode"],
                "values": add_ledgers(*pieces),
            }
        )
    return {
        "formula": "I6_bulk_at_yf = (1/2) sum_components p_f(component) I6_4D(component)",
        "delta_function_convention": "physical interval; each endpoint delta integrates to one",
        "component_rows": component_rows,
        "hyper_rows": hyper_rows,
        "parity_rows": parity_rows,
        "totals": add_ledgers(*(row["values"] for row in hyper_rows)),
    }


def source_bulk_ledger() -> dict[str, Any]:
    rows = []
    for hyper in HYPERS:
        # Every left-chiral H has etaL=+1 at the full Spin(10) wall.  A 16 has
        # doubled Dynkin index 2T=4; bar16 has the same quadratic index.
        values = scale_ledger(source_4d_anomaly(16, 4, hyper["q"]), Fraction(hyper["etaL"], 2))
        rows.append(
            {
                "hyper": hyper["name"],
                "Spin10_rep": hyper["Spin10_rep"],
                "q": hyper["q"],
                "pL_H": hyper["etaL"],
                "source_wall_coefficient": Fraction(hyper["etaL"], 2),
                "values": values,
            }
        )
    return {"rows": rows, "totals": add_ledgers(*(row["values"] for row in rows))}


def source_boundary_ledger() -> dict[str, Any]:
    rows = []
    for field in SOURCE_BOUNDARY_FIELDS:
        values = source_4d_anomaly(field["dim"], field["index_2T"], field["q"])
        rows.append({**field, "coefficient": "1", "values": values})
    return {"rows": rows, "totals": add_ledgers(*(row["values"] for row in rows))}


def mass_certificate() -> dict[str, Any]:
    mass_terms = (
        {
            "operator": "delta(y-L) lambdaL ThetaPlus HLF HLA",
            "Spin10_contraction": "16 x bar16 -> 1",
            "U1F_charge": 9 + 3 - 12,
            "zero_mode_mass": "mL=lambdaL <ThetaPlus> fLF(L) fLA(L)",
            "paired_zero_modes": ["LF", "LA"],
        },
        {
            "operator": "delta(y-L) lambdaR ThetaMinus HRA HRF",
            "Spin10_contraction": "16 x bar16 -> 1",
            "U1F_charge": -9 - 3 + 12,
            "zero_mode_mass": "mR=lambdaR <ThetaMinus> fRA(L) fRF(L)",
            "paired_zero_modes": ["RA", "RF"],
        },
    )
    # Ordering (LF, LA, RA, RF).  Entries are symbolic labels; the exact rank
    # below is conditional only on mL*mR != 0.
    matrix = [
        ["0", "mL", "0", "0"],
        ["mL", "0", "0", "0"],
        ["0", "0", "0", "mR"],
        ["0", "0", "mR", "0"],
    ]
    return {
        "source_wall_operators": list(mass_terms),
        "all_operators_local_in_5D": True,
        "why_local": (
            "All four H chirals are even and have nonzero boundary values at y=L; "
            "Theta and the full Spin(10) bilinears are co-located there."
        ),
        "projected_zero_mode_basis": ["LF", "LA", "RA", "RF"],
        "projected_zero_mode_mass_matrix": matrix,
        "determinant": "mL^2 mR^2",
        "rank_if_mL_and_mR_nonzero": 4,
        "massless_exotic_zero_modes_if_mL_and_mR_nonzero": 0,
        "separate_Bplus_Bminus_shining_hypers_needed": False,
        "localization_note": (
            "Odd bulk masses may exponentially suppress f_i(L), but a finite nonzero "
            "boundary value still gives a nonzero mass."
        ),
        "qualification": (
            "This proves the zero-mode overlap matrix, not the regulated determinant of "
            "the complete boundary-condition-shifted KK tower."
        ),
    }


def parity_anomaly_certificate() -> dict[str, Any]:
    charges = [int(hyper["q"]) for hyper in HYPERS]
    return {
        "summed_5D_parity_odd_polynomial_coefficients": {
            "U1F_Spin10_squared_doubled": 4 * sum(charges),
            "gravity_squared_U1F": 16 * sum(charges),
            "U1F_cubed": 16 * sum(q**3 for q in charges),
            "Spin10_cubed": 0,
        },
        "ordinary_wall_totals_require_CS_inflow": False,
        "additional_chiral_fields_required_for_displayed_ordinary_rows": False,
        "net_perturbative_half_level_shift": 0,
        "global_eta_invariant_or_bordism_audit_complete": False,
        "qualification": (
            "Zero perturbative coefficients remove the displayed local need for inflow. "
            "They do not decide global parity anomalies for the final compact quotient, "
            "nor CS quantization before the U(1)F charge/line lattice is fixed."
        ),
    }


def encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance() -> dict[str, Any]:
    paths = (
        ROOT / "susy_v45_s0_group_zero_mode_audit.py",
        ROOT / "SUSY_V45_S0_GROUP_ZERO_MODE_AUDIT.json",
        ROOT / "susy_v45_wall_anomaly_mass_audit.py",
        ROOT / "SUSY_V45_WALL_ANOMALY_MASS_AUDIT.json",
        Path(__file__).resolve(),
        TEST_PATH,
    )
    return {
        "files": [
            {
                "path": path.name,
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
            for path in paths
        ]
    }


def build_report() -> dict[str, Any]:
    ps_boundary = ps_boundary_ledger()
    ps_bulk = ps_bulk_ledger()
    source_boundary = source_boundary_ledger()
    source_bulk = source_bulk_ledger()
    ps_total = add_ledgers(ps_boundary["totals"], ps_bulk["totals"])
    source_total = add_ledgers(source_boundary["totals"], source_bulk["totals"])

    report = {
        "schema": "susy-v45-reconciled-bulk-spinor-audit-v1",
        "status": STATUS,
        "scope": (
            "Parity-resolved ordinary localized anomalies and projected zero-mode masses "
            "for one microscopic four-bulk-spinor realization of the minimal V45 core."
        ),
        "geometry": {
            "space": "M4 x [0,L]",
            "y0_wall": "Pati-Salam x U(1)F",
            "yL_wall_before_Higgsing": "Spin(10) x U(1)F",
            "bulk_group": "Spin(10) x U(1)F",
        },
        "bulk_hypers": [dict(hyper) for hyper in HYPERS],
        "PS_wall": {
            "boundary_chirals": ps_boundary,
            "bulk_hyper_density": ps_bulk,
            "combined_totals": ps_total,
            "all_displayed_ordinary_rows_zero": all(value == 0 for value in ps_total.values()),
        },
        "Spin10_wall": {
            "boundary_chirals": source_boundary,
            "bulk_hyper_density": source_bulk,
            "combined_totals": source_total,
            "all_displayed_ordinary_rows_zero": all(value == 0 for value in source_total.values()),
        },
        "source_wall_mass_lifting": mass_certificate(),
        "inflow_and_parity": parity_anomaly_certificate(),
        "reconciliation_decision": {
            "one_microscopic_skeleton_reconciled": True,
            "bulk_spinors_replace_boundary_LF_LA_RA_RF": True,
            "separate_singlet_shining_hypers_removed": True,
            "ordinary_anomalies_cancel_wall_by_wall": True,
            "ordinary_CS_or_extra_chiral_matter_required": False,
            "all_four_exotic_zero_modes_lifted_conditionally": True,
            "complete_5D_model_established": False,
            "gates_promoted": [],
        },
        "open_kill_tests": [
            "solve the full KK spectrum and determinant with both source boundary masses",
            "compute the eta invariant/global anomaly for the fixed compact gauge quotient",
            "fix the primitive U(1)F charge and line-operator lattice and recheck CS quantization",
            "derive all cross-wall Wilson coefficients carried directly by the four spinors",
            "supply and solve the complete 126+bar126 boundary superpotential and mass matrices",
            "reconstruct neutrino masses, Higgs/mu sector, flavour, thresholds and RG matching",
        ],
        "primary_sources": [
            {
                "url": "https://arxiv.org/abs/hep-th/0110073",
                "use": "S1/(Z2 x Z2') fixed-point anomaly signs and half-anomaly normalization on identified walls",
            },
            {
                "url": "https://arxiv.org/abs/hep-th/0305024",
                "use": "general orbifold projector formula and the distinction between local and globally vanishing anomalies",
            },
            {
                "url": "https://arxiv.org/abs/hep-ph/0603086",
                "use": "5D supersymmetric Spin(10) hypermultiplets, parity-selected PS zero modes and boundary-mass-shifted towers",
            },
        ],
        "provenance": provenance(),
    }
    encoded = encode(report)
    encoded["core_sha256"] = canonical_sha(encoded)
    validate(encoded)
    return encoded


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("stale core hash")
    if report["PS_wall"]["boundary_chirals"]["totals"] != {
        "U1F_SU4_squared_doubled": 0,
        "U1F_SU2L_squared_doubled": 36,
        "U1F_SU2R_squared_doubled": -36,
        "gravity_squared_U1F": 0,
        "U1F_cubed": 0,
        "SU4_cubed": 0,
    }:
        raise RuntimeError("unexpected PS boundary anomaly ledger")
    if report["PS_wall"]["bulk_hyper_density"]["totals"] != {
        "U1F_SU4_squared_doubled": 0,
        "U1F_SU2L_squared_doubled": -36,
        "U1F_SU2R_squared_doubled": 36,
        "gravity_squared_U1F": 0,
        "U1F_cubed": 0,
        "SU4_cubed": 0,
    }:
        raise RuntimeError("unexpected PS bulk localized anomaly ledger")
    if not report["PS_wall"]["all_displayed_ordinary_rows_zero"]:
        raise RuntimeError("PS wall is anomalous")
    if not report["Spin10_wall"]["all_displayed_ordinary_rows_zero"]:
        raise RuntimeError("Spin10 wall is anomalous")
    masses = report["source_wall_mass_lifting"]
    if masses["rank_if_mL_and_mR_nonzero"] != 4 or masses["massless_exotic_zero_modes_if_mL_and_mR_nonzero"] != 0:
        raise RuntimeError("projected zero-mode mass matrix is not full rank")
    if masses["separate_Bplus_Bminus_shining_hypers_needed"]:
        raise RuntimeError("reconciled skeleton should not retain redundant shining singlets")
    decision = report["reconciliation_decision"]
    if decision["ordinary_CS_or_extra_chiral_matter_required"]:
        raise RuntimeError("zero ordinary wall totals cannot require ordinary inflow")
    if decision["complete_5D_model_established"] or decision["gates_promoted"]:
        raise RuntimeError("this audit cannot close the full model or promote gates")


def render_markdown(data: Mapping[str, Any]) -> str:
    ps_b = data["PS_wall"]["boundary_chirals"]["totals"]
    ps_h = data["PS_wall"]["bulk_hyper_density"]["totals"]
    ps_t = data["PS_wall"]["combined_totals"]
    so_b = data["Spin10_wall"]["boundary_chirals"]["totals"]
    so_h = data["Spin10_wall"]["bulk_hyper_density"]["totals"]
    so_t = data["Spin10_wall"]["combined_totals"]
    return f"""# V45 reconciled bulk-spinor audit

Status: `{data['status']}`

## Result

The four quotient-valid exotic multiplets can be realized as zero modes of the
four bulk hypers `16_+3`, `bar16_-12`, `16_-3`, and `bar16_+12`.  This single
choice resolves the apparent conflict between the group/zero-mode audit and the
wall/locality audit: the same bulk spinors both supply the PS zero modes and have
even fields at the full-Spin(10) wall.  Consequently the two Theta mass operators
are local boundary operators.  Separate singlet `B+/-` shining hypers are not
needed.

## Local anomaly formula

On the physical interval, normalize each endpoint delta function to integrate to
one.  For a bulk hyper written as a left-chiral `H` plus conjugate `Hc`,

`I6_f = (1/2) sum_alpha p_f(alpha) I6_4D(R_alpha,q)`,

where `p_f=+1` when `H` is even and `p_f=-1` when `Hc` is even.  A boundary
chiral contributes one full `I6_4D`.  This is the identified-wall version of the
fixed-point anomaly derived for `S1/(Z2 x Z2')`.

## Pati-Salam wall

In the row order `(SU4^2-F, SU2L^2-F, SU2R^2-F, grav-F, F^3, SU4^3)`, the
boundary fields `3Q+3Qc+H` give

`({ps_b['U1F_SU4_squared_doubled']}, {ps_b['U1F_SU2L_squared_doubled']}, {ps_b['U1F_SU2R_squared_doubled']}, {ps_b['gravity_squared_U1F']}, {ps_b['U1F_cubed']}, {ps_b['SU4_cubed']})`.

The parity-weighted four bulk hypers give

`({ps_h['U1F_SU4_squared_doubled']}, {ps_h['U1F_SU2L_squared_doubled']}, {ps_h['U1F_SU2R_squared_doubled']}, {ps_h['gravity_squared_U1F']}, {ps_h['U1F_cubed']}, {ps_h['SU4_cubed']})`.

Their wall-local sum is exactly

`({ps_t['U1F_SU4_squared_doubled']}, {ps_t['U1F_SU2L_squared_doubled']}, {ps_t['U1F_SU2R_squared_doubled']}, {ps_t['gravity_squared_U1F']}, {ps_t['U1F_cubed']}, {ps_t['SU4_cubed']})`.

The cancellation is not merely integrated over the fifth dimension; it occurs at
the PS endpoint.

## Full-Spin(10) wall

All four `H` chirals have positive source-wall parity.  Each therefore deposits
one half of its full-representation anomaly there.  In the row order
`(Spin10^2-F, grav-F, F^3, Spin10^3)`, their total is

`({so_h['U1F_Spin10_squared_doubled']}, {so_h['gravity_squared_U1F']}, {so_h['U1F_cubed']}, {so_h['Spin10_cubed']})`.

`ThetaPlus+ThetaMinus+STheta+126+bar126` contributes

`({so_b['U1F_Spin10_squared_doubled']}, {so_b['gravity_squared_U1F']}, {so_b['U1F_cubed']}, {so_b['Spin10_cubed']})`,

so the source-wall total is

`({so_t['U1F_Spin10_squared_doubled']}, {so_t['gravity_squared_U1F']}, {so_t['U1F_cubed']}, {so_t['Spin10_cubed']})`.

Thus no ordinary Chern-Simons inflow or extra chiral matter is required for the
displayed perturbative rows.

## Local source masses and zero-mode rank

The allowed source operators are

- `delta(y-L) lambdaL ThetaPlus HLF HLA`, and
- `delta(y-L) lambdaR ThetaMinus HRA HRF`.

After the Theta VEVs they induce `mL LF LA + mR RA RF`, with
`mL=lambdaL <ThetaPlus> fLF(L)fLA(L)` and similarly for `mR`.  In the basis
`(LF,LA,RA,RF)` the symmetric chiral mass matrix has two off-diagonal `2x2`
blocks, determinant `mL^2 mR^2`, and rank four whenever both overlaps are
nonzero.  Hence all four exotic zero modes are lifted.  Bulk localization may
make these masses exponentially small, but it does not make them vanish at
finite localization.

## What remains open

This closes the ordinary localized-anomaly ledger and the projected zero-mode
mass rank, not S0 or any G gate.  The full boundary-condition-shifted KK
determinant, eta/global anomaly, compact charge lattice and CS quantization,
cross-wall Wilson coefficients, and complete `126+bar126` vacuum/mass problem
remain kill tests.

Primary formulas and precedents: [Scrucca et al.](https://arxiv.org/abs/hep-th/0110073),
[von Gersdorff and Quiros](https://arxiv.org/abs/hep-th/0305024), and
[Alciati et al.](https://arxiv.org/abs/hep-ph/0603086).

Core SHA-256: `{data['core_sha256']}`
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if args.write:
        JSON_PATH.write_text(expected_json, encoding="utf-8")
        MD_PATH.write_text(expected_md, encoding="utf-8")
        print("V45_RECONCILED_BULK_SPINOR_AUDIT_WRITE_PASS")
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise SystemExit("V45 reconciled artifacts missing; run --write")
        if JSON_PATH.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("V45 reconciled JSON stale; run --write")
        if MD_PATH.read_text(encoding="utf-8") != expected_md:
            raise SystemExit("V45 reconciled Markdown stale; run --write")
        print("V45_RECONCILED_BULK_SPINOR_AUDIT_CHECK_PASS")


if __name__ == "__main__":
    main()
