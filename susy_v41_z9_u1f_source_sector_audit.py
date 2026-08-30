#!/usr/bin/env python3
"""Fail-closed V41 source-sector audit for the V40 U(1)_F -> Z9 route.

The V40 selector supplied only the charge arithmetic.  This script makes the
smallest corresponding renormalizable Higgs/stabilizer and anomalon threshold
sector explicit, then checks one canonical supersymmetric F/D-flat branch.

It is deliberately narrower than a complete Pati--Salam source: it neither
solves the pre-existing PS/PQ driver vacuum nor assumes that an arbitrary
Kahler potential, soft sector, product-symmetry UV completion, flavour fit,
or proton calculation has been supplied.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
OUTPUT_JSON = ROOT / "SUSY_V41_Z9_U1F_SOURCE_SECTOR_AUDIT.json"
OUTPUT_MD = ROOT / "SUSY_V41_Z9_U1F_SOURCE_SECTOR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v41_z9_u1f_source_sector_audit.py"

ORDER = 9
STATUS = (
    "V41_U1F_TO_Z9_RENORMALIZABLE_SOURCE_BRANCH_AND_ANOMALON_MASSABILITY_"
    "CERTIFIED_ON_A_CANONICAL_SUSY_BRANCH__EMBEDDING_KAEHLER_SOFT_AND_FULL_"
    "THEORY_GATES_FAIL_CLOSED"
)


# The new-source charges are deliberately compatible with the charge table in
# susy_v40_all_ring_selector.py.  ``multiplicity`` counts copies of a PS
# representation, rather than its gauge-component dimension.
FIELDS: dict[str, dict[str, Any]] = {
    "STheta": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": 0, "r4": 2, "z5610": 0, "pq": 0,
        "role": "U(1)_F-breaking stabilizer",
    },
    "ThetaPlus": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": 9, "r4": 0, "z5610": 0, "pq": 0,
        "role": "positive-charge U(1)_F Higgs",
    },
    "ThetaMinus": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": -9, "r4": 0, "z5610": 0, "pq": 0,
        "role": "negative-charge U(1)_F Higgs",
    },
    "L0": {
        "representation": "(1,2,1)", "multiplicity": 4,
        "u1f": 0, "r4": 1, "z5610": 0, "pq": 0,
        "role": "SU(2)_L anomalon",
    },
    "Lminus9": {
        "representation": "(1,2,1)", "multiplicity": 4,
        "u1f": -9, "r4": 1, "z5610": 0, "pq": 0,
        "role": "SU(2)_L anomalon",
    },
    "R0": {
        "representation": "(1,1,2)", "multiplicity": 4,
        "u1f": 0, "r4": 1, "z5610": 0, "pq": 0,
        "role": "SU(2)_R anomalon",
    },
    "Rplus9": {
        "representation": "(1,1,2)", "multiplicity": 4,
        "u1f": 9, "r4": 1, "z5610": 0, "pq": 0,
        "role": "SU(2)_R anomalon",
    },
    "E4": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": 4, "r4": 1, "z5610": 0, "pq": 0,
        "role": "singlet anomalon",
    },
    "E5": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": 5, "r4": 1, "z5610": 0, "pq": 0,
        "role": "singlet anomalon",
    },
    "E3": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": 3, "r4": 1, "z5610": 0, "pq": 0,
        "role": "singlet anomalon",
    },
    "E6": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": 6, "r4": 1, "z5610": 0, "pq": 0,
        "role": "singlet anomalon",
    },
    "Eminus2": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": -2, "r4": 1, "z5610": 0, "pq": 0,
        "role": "singlet anomalon",
    },
    "Eminus7": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": -7, "r4": 1, "z5610": 0, "pq": 0,
        "role": "singlet anomalon",
    },
    # This vectorlike PS pair is a concrete tree-level completion of V40's
    # otherwise effective Dirac-neutrino operator.  It cancels internally in
    # every ordinary U(1)_F anomaly row and is not part of the anomalon repair.
    "F": {
        "representation": "(4,1,2)", "multiplicity": 1,
        "u1f": 3, "r4": 1, "z5610": 0, "pq": 0,
        "role": "Dirac-neutrino messenger",
    },
    "Fc": {
        "representation": "(bar4,1,2)", "multiplicity": 1,
        "u1f": -3, "r4": 1, "z5610": 0, "pq": 0,
        "role": "Dirac-neutrino messenger",
    },
    # Existing V40 fields needed only to audit the messenger interface and
    # the unavoidable neutral-driver mixing boundary.
    "Q": {
        "representation": "(4,2,1)", "multiplicity": 3,
        "u1f": 3, "r4": 1, "z5610": 0, "pq": 0,
        "role": "V40 host matter",
    },
    "H": {
        "representation": "(1,2,2)", "multiplicity": 1,
        "u1f": 0, "r4": 0, "z5610": 0, "pq": 0,
        "role": "V40 host Higgs",
    },
    "Sc": {
        "representation": "(bar4,1,2)", "multiplicity": 1,
        "u1f": 0, "r4": 0, "z5610": 0, "pq": 0,
        "role": "V40 PS-breaking host field",
    },
    "NDirac": {
        "representation": "(1,1,1)", "multiplicity": 3,
        "u1f": -3, "r4": 1, "z5610": 0, "pq": 0,
        "role": "V40 sterile Dirac-neutrino field",
    },
    "X": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": 0, "r4": 2, "z5610": 0, "pq": 0,
        "role": "existing V40 driver",
    },
    "Zp": {
        "representation": "(1,1,1)", "multiplicity": 1,
        "u1f": 0, "r4": 2, "z5610": 0, "pq": 0,
        "role": "existing V40 driver",
    },
}


# Coupling parameters and the dimension-two constant mu_F^2 are symmetry
# neutral.  Repeated L/R labels denote full-rank 4 by 4 flavour matrices.
SUPERPOTENTIAL: tuple[dict[str, Any], ...] = (
    {
        "label": "stabilizer_linear",
        "fields": ("STheta",),
        "expression": "-kappa mu_F^2 STheta",
        "gauge_invariant": True,
    },
    {
        "label": "stabilizer_higgs",
        "fields": ("STheta", "ThetaPlus", "ThetaMinus"),
        "expression": "kappa STheta ThetaPlus ThetaMinus",
        "gauge_invariant": True,
    },
    {
        "label": "L_anomalon_mass",
        "fields": ("ThetaPlus", "L0", "Lminus9"),
        "expression": "ThetaPlus epsilon_2 L0^a lambdaL_ab Lminus9^b",
        "gauge_invariant": True,
    },
    {
        "label": "R_anomalon_mass",
        "fields": ("ThetaMinus", "R0", "Rplus9"),
        "expression": "ThetaMinus epsilon_2 R0^a lambdaR_ab Rplus9^b",
        "gauge_invariant": True,
    },
    {
        "label": "E45_anomalon_mass",
        "fields": ("ThetaMinus", "E4", "E5"),
        "expression": "lambda45 ThetaMinus E4 E5",
        "gauge_invariant": True,
    },
    {
        "label": "E36_anomalon_mass",
        "fields": ("ThetaMinus", "E3", "E6"),
        "expression": "lambda36 ThetaMinus E3 E6",
        "gauge_invariant": True,
    },
    {
        "label": "Eminus2minus7_anomalon_mass",
        "fields": ("ThetaPlus", "Eminus2", "Eminus7"),
        "expression": "lambdaMinus27 ThetaPlus Eminus2 Eminus7",
        "gauge_invariant": True,
    },
    {
        "label": "Dirac_messenger_yukawa_left",
        "fields": ("Q", "H", "Fc"),
        "expression": "y1 Q H Fc",
        "gauge_invariant": True,
    },
    {
        "label": "Dirac_messenger_yukawa_right",
        "fields": ("F", "Sc", "NDirac"),
        "expression": "y2 F Sc NDirac",
        "gauge_invariant": True,
    },
    {
        "label": "Dirac_messenger_mass",
        "fields": ("F", "Fc"),
        "expression": "M_F F Fc",
        "gauge_invariant": True,
    },
)


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def charge(fields: Iterable[str], key: str, modulus: int | None = None) -> int:
    value = sum(int(FIELDS[field][key]) for field in fields)
    return value if modulus is None else value % modulus


def term_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for term in SUPERPOTENTIAL:
        fields = tuple(term["fields"])
        rows.append({
            "label": term["label"],
            "expression": term["expression"],
            "fields": list(fields),
            "gauge_invariant_by_declared_PS_representations": term["gauge_invariant"],
            "U1F": charge(fields, "u1f"),
            "Z9": charge(fields, "u1f", ORDER),
            "Z4R": charge(fields, "r4", 4),
            "Z5610": charge(fields, "z5610", 5610),
            "PQ_numerator_over_170": charge(fields, "pq"),
        })
    return {
        "declared_renormalizable_superpotential": {
            "formula": (
                "W_F = kappa STheta(ThetaPlus ThetaMinus-mu_F^2) + "
                "ThetaPlus[L0 lambdaL Lminus9 + lambdaMinus27 Eminus2 Eminus7] + "
                "ThetaMinus[R0 lambdaR Rplus9 + lambda45 E4 E5 + lambda36 E3 E6] + "
                "y1 Q H Fc + y2 F Sc NDirac + M_F F Fc"
            ),
            "scope": "The epsilon_2 contractions and flavour indices on L/R are suppressed in the displayed formula.",
        },
        "rows": rows,
        "all_U1F_neutral": all(row["U1F"] == 0 for row in rows),
        "all_Z9_neutral": all(row["Z9"] == 0 for row in rows),
        "all_Z4R_charge_two": all(row["Z4R"] == 2 for row in rows),
        "all_Z5610_neutral": all(row["Z5610"] == 0 for row in rows),
        "all_PQ_neutral": all(row["PQ_numerator_over_170"] == 0 for row in rows),
        "all_declared_PS_invariants": all(row["gauge_invariant_by_declared_PS_representations"] for row in rows),
    }


def fd_flat_branch() -> dict[str, Any]:
    # In the stated D convention the FI coefficient xi carries the same
    # dimension as |Theta|^2.  The formula includes xi=0 as a special case.
    return {
        "canonical_assumptions": [
            "global N=1 SUSY with canonical positive Kahler metric for the displayed source fields",
            "kappa != 0, mu_F^2 != 0, M_F != 0, and the listed anomalon couplings have the stated ranks",
            "all anomalons and messenger fields have zero expectation values on the branch",
            "the displayed branch is isolated from the unsolved host PS/PQ driver sector",
        ],
        "F_equations": {
            "F_STheta": "kappa(ThetaPlus ThetaMinus-mu_F^2)",
            "F_ThetaPlus": "kappa STheta ThetaMinus + L0 lambdaL Lminus9 + lambdaMinus27 Eminus2 Eminus7",
            "F_ThetaMinus": "kappa STheta ThetaPlus + R0 lambdaR Rplus9 + lambda45 E4 E5 + lambda36 E3 E6",
            "F_anomalons": "ThetaPlus/ThetaMinus times the appropriate full-rank mass matrix times its partner",
            "F_F": "y2 Sc NDirac + M_F Fc",
            "F_Fc": "y1 Q H + M_F F",
        },
        "branch": {
            "STheta": 0,
            "ThetaPlus_times_ThetaMinus": "mu_F^2",
            "all_anomalons": 0,
            "F": 0,
            "Fc": 0,
            "host_fields_for_the_isolated_source_test": 0,
            "zero_F": True,
        },
        "D_equation_convention": "D_F = 9(|ThetaPlus|^2-|ThetaMinus|^2) + sum_i q_i |phi_i|^2 + xi_F",
        "FI_deformed_solution": {
            "definitions": "v_F^4 = |mu_F^2|^2 and d = -xi_F/9",
            "absolute_values": {
                "|ThetaPlus|^2": "(d + sqrt(d^2+4 v_F^4))/2",
                "|ThetaMinus|^2": "(-d + sqrt(d^2+4 v_F^4))/2",
            },
            "both_nonzero_for_finite_xi_F_and_mu_F": True,
            "xi_F_zero_special_case": "|ThetaPlus|=|ThetaMinus|=v_F",
            "zero_D": True,
        },
        "unbroken_gauge_subgroup": {
            "VEV_charges": [9, -9],
            "gcd_of_nonzero_VEV_charges": math.gcd(9, 9),
            "result": "Z9",
            "every_nonzero_branch_VEV_is_zero_mod_9": True,
        },
        "canonical_branch_exists": True,
        "full_host_vacuum_solved": False,
    }


def massability_audit() -> dict[str, Any]:
    identity4 = [[1 if row == col else 0 for col in range(4)] for row in range(4)]
    return {
        "rank_witness": {
            "lambdaL": identity4,
            "lambdaR": identity4,
            "lambda45": 1,
            "lambda36": 1,
            "lambdaMinus27": 1,
            "kappa": 1,
            "M_F_over_v_F": 1,
        },
        "anomalon_thresholds": [
            {
                "sector": "four L0/Lminus9 SU(2)_L pairs",
                "mass_matrix": "v_F lambdaL",
                "full_rank_requirement": 4,
                "rank_of_witness": 4,
                "all_chiral_pairs_massable": True,
            },
            {
                "sector": "four R0/Rplus9 SU(2)_R pairs",
                "mass_matrix": "v_F lambdaR",
                "full_rank_requirement": 4,
                "rank_of_witness": 4,
                "all_chiral_pairs_massable": True,
            },
            {
                "sector": "E4/E5, E3/E6, Eminus2/Eminus7 singlet pairs",
                "mass_matrices": ["lambda45 v_F", "lambda36 v_F", "lambdaMinus27 v_F"],
                "nonzero_coupling_requirement": True,
                "all_chiral_pairs_massable": True,
            },
        ],
        "Higgs_stabilizer_and_vector": {
            "at_xi_F_zero": {
                "STheta_and_radial_chiral_combination": "mass scale sqrt(2)|kappa| v_F in canonical normalization",
                "relative_Theta_chiral_combination": "eaten by the U(1)_F vector multiplet",
                "vector_mass_scale": "proportional to 9 g_F v_F; convention-dependent normalization omitted",
            },
            "physical_massless_source_chiral_multiplet_on_canonical_branch": False,
        },
        "Dirac_neutrino_messenger": {
            "mass": "M_F != 0",
            "F_flat_value": "F=Fc=0 when host backgrounds Q,H,Sc,NDirac vanish",
            "tree_level_elimination": {
                "Fc_solution": "-(y2/M_F) Sc NDirac",
                "F_solution": "-(y1/M_F) Q H",
                "effective_operator": "-(y1 y2/M_F) Q H Sc NDirac",
            },
            "vectorlike_under_PS_and_U1F": True,
            "full_flavour_completion_or_fit": False,
        },
        "all_required_U1F_breaking_and_anomalon_fields_massable_on_witness": True,
        "pole_spectrum_or_threshold_matching_computed": False,
    }


def anomaly_recheck() -> dict[str, Any]:
    # These are the ordinary U(1)_F triangles in the same doubled-Dynkin and
    # physical-Weyl conventions as the V40 stress audit.  The baseline is the
    # V40 visible field content before its completion fields are added.
    visible = {"SU4": 0, "SU2L": 36, "SU2R": -36, "gravity": -9, "cubic": -81}
    theta = {"SU4": 0, "SU2L": 0, "SU2R": 0, "gravity": 0, "cubic": 0}
    l_pairs = {"SU4": 0, "SU2L": -36, "SU2R": 0, "gravity": -72, "cubic": -5832}
    r_pairs = {"SU4": 0, "SU2L": 0, "SU2R": 36, "gravity": 72, "cubic": 5832}
    singlets = {"SU4": 0, "SU2L": 0, "SU2R": 0, "gravity": 9, "cubic": 81}
    messenger = {"SU4": 0, "SU2L": 0, "SU2R": 0, "gravity": 0, "cubic": 0}
    rows = {
        "visible_before_completion": visible,
        "ThetaPlus_ThetaMinus": theta,
        "four_L_pairs": l_pairs,
        "four_R_pairs": r_pairs,
        "three_singlet_pairs": singlets,
        "F_Fc_vectorlike_messenger": messenger,
    }
    totals = {key: sum(row[key] for row in rows.values()) for key in visible}
    return {
        "convention": "PS rows use 2T(R) including spectator/family multiplicities; gravity and cubic rows use physical Weyl-component multiplicities.",
        "rows": rows,
        "totals": totals,
        "all_listed_ordinary_PS_times_U1F_anomalies_cancel": all(value == 0 for value in totals.values()),
        "scope_limit": "This rechecks only ordinary local PS times U(1)_F rows. Product anomalies involving the old Z5610/Z4R parents and global bordism data remain outside this source audit.",
    }


def embedding_boundary() -> dict[str, Any]:
    # STheta, X and Zp have exactly the same listed source-level signatures.
    signatures = {
        name: {
            key: FIELDS[name][key]
            for key in ("representation", "u1f", "r4", "z5610", "pq")
        }
        for name in ("STheta", "X", "Zp")
    }
    cross_terms = []
    for label, fields in (
        ("X_ThetaPlus_ThetaMinus", ("X", "ThetaPlus", "ThetaMinus")),
        ("Zp_ThetaPlus_ThetaMinus", ("Zp", "ThetaPlus", "ThetaMinus")),
        ("X_STheta_STheta", ("X", "STheta", "STheta")),
        ("Zp_STheta_STheta", ("Zp", "STheta", "STheta")),
        ("STheta_X_X", ("STheta", "X", "X")),
        ("STheta_X_Zp", ("STheta", "X", "Zp")),
        ("STheta_Zp_Zp", ("STheta", "Zp", "Zp")),
    ):
        cross_terms.append({
            "label": label,
            "fields": list(fields),
            "U1F": charge(fields, "u1f"),
            "Z4R": charge(fields, "r4", 4),
            "Z5610": charge(fields, "z5610", 5610),
            "PQ_numerator_over_170": charge(fields, "pq"),
            "allowed_by_listed_product_symmetries": (
                charge(fields, "u1f") == 0
                and charge(fields, "r4", 4) == 2
                and charge(fields, "z5610", 5610) == 0
                and charge(fields, "pq") == 0
            ),
        })
    return {
        "identical_declared_signatures": signatures,
        "all_three_signatures_identical": len({tuple(row.items()) for row in signatures.values()}) == 1,
        "representative_allowed_cross_terms": cross_terms,
        "consequence": (
            "The isolated source superpotential is an existence construction, not a symmetry-protected separation from the existing X/Zp driver sector.  A full V41 source must either solve the coupled F equations or provide an additional UV/sequestering mechanism and audit every resulting operator."
        ),
        "embedding_is_complete": False,
    }


def kahler_soft_boundary() -> dict[str, Any]:
    return {
        "canonical_result": (
            "With canonical positive Kahler metric and vanishing soft terms, the reported F/D-flat branch is exact and every nontrivial residual-Z9 field is at the origin except ThetaPlus/ThetaMinus, whose charges are multiples of nine."
        ),
        "Kahler_requirements_not_yet_supplied": [
            "positive-definite full Kahler metric after coupling to all host fields",
            "the complete U(1)_F moment map, including any kinetic mixing and any allowed FI datum",
            "absence of a lower-energy minimum with an anomalon or messenger VEV",
            "a derivation that the source/driver sequestering assumed above survives the UV theory",
        ],
        "soft_terms_that_require_a_real_vacuum_analysis": [
            "m^2_ThetaPlus, m^2_ThetaMinus, m^2_STheta and the allowed STheta tadpole/B/A terms",
            "soft scalar masses and A terms for every L, R and E anomalon pair",
            "soft masses and B term for F/Fc, plus U(1)_F D-term shifts",
            "soft terms and mixings inherited from X/Zp and the PS/PQ host sector",
        ],
        "local_noncondensation_test_for_each_mass_pair": {
            "definition": "A_i=|M_i|^2+m_i^2+q_i g_F<D_F>, B_i=|M_i|^2+m_partner^2+q_partner g_F<D_F>",
            "condition": "A_i>0, B_i>0, and A_i B_i>|b_i|^2 for the scalar pair mass matrix with holomorphic mixing b_i",
            "interpretation": "This sufficient local condition keeps all anomalon/messenger VEVs zero. If it fails, a field with nonzero charge modulo nine can condense and destroy the claimed Z9 branch.",
        },
        "Z9_survival_statement": (
            "The residual gauge Z9 remains exact only on branches where every field with U(1)_F charge not in 9 Z has zero VEV. Gauge invariance alone does not choose that branch once arbitrary Kahler/soft data are admitted."
        ),
        "full_Kahler_soft_global_vacuum_or_thermal_selection_computed": False,
    }


def source_manifest() -> list[dict[str, Any]]:
    paths = (ROOT / "susy_v41_z9_u1f_source_sector_audit.py", TEST_PATH)
    return [
        {
            "path": path.name,
            "exists": path.exists(),
            "sha256": sha256_file(path) if path.exists() else None,
        }
        for path in paths
    ]


def build_report() -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "susy-v41-z9-u1f-source-sector-audit-v1",
        "status": STATUS,
        "scope": (
            "A concrete canonical-SUSY source-sector existence proof for U(1)_F -> Z9, anomalon massability, and a tree-level Dirac messenger. It is not an integrated V41 Pati--Salam model."
        ),
        "field_table": FIELDS,
        "superpotential_charge_audit": term_audit(),
        "canonical_F_D_flat_branch": fd_flat_branch(),
        "massability_audit": massability_audit(),
        "ordinary_anomaly_recheck": anomaly_recheck(),
        "host_embedding_boundary": embedding_boundary(),
        "Kahler_soft_boundary": kahler_soft_boundary(),
        "decision": {
            "isolated_renormalizable_source_branch_exists": True,
            "exact_Z9_is_preserved_on_that_branch": True,
            "all_listed_anomalon_and_U1F_breaking_fields_massable_on_a_rank_witness": True,
            "tree_level_Dirac_messenger_completion_exists": True,
            "full_coupled_PS_PQ_U1F_source_exists": False,
            "full_Kahler_soft_vacuum_exists": False,
            "full_product_symmetry_UV_completion_exists": False,
            "full_gate_closed": [],
        },
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    terms = report["superpotential_charge_audit"]
    branch = report["canonical_F_D_flat_branch"]
    mass = report["massability_audit"]
    anomaly = report["ordinary_anomaly_recheck"]
    embedding = report["host_embedding_boundary"]
    return f"""# V41 U(1)F-to-Z9 source-sector audit

Status: `{report['status']}`

This is a source-level existence calculation for the V40 `U(1)_F -> Z9`
selector, not a complete Pati--Salam theory or a full G-gate closure.

## Concrete renormalizable source

The declared source is

`W_F = kappa STheta(ThetaPlus ThetaMinus-mu_F^2)`

`+ ThetaPlus[L0 lambdaL Lminus9 + lambdaMinus27 Eminus2 Eminus7]`

`+ ThetaMinus[R0 lambdaR Rplus9 + lambda45 E4 E5 + lambda36 E3 E6]`

`+ y1 Q H Fc + y2 F Sc NDirac + M_F F Fc`.

All {len(terms['rows'])} listed terms are neutral under `U(1)_F`, `Z9`,
`Z5610`, and the supplied PQ charge, and carry superpotential `Z4R` charge
two.  The `F/Fc` pair is a vectorlike tree-level messenger: eliminating it
gives `-(y1 y2/M_F) Q H Sc NDirac`.

## Canonical F/D-flat branch

At zero host backgrounds and zero anomalon/messenger VEVs, choose
`<STheta>=0` and `<ThetaPlus><ThetaMinus>=mu_F^2`.  The canonical D equation
has a solution even with a finite FI datum; at `xi_F=0`,
`|ThetaPlus|=|ThetaMinus|=v_F`.  The nonzero VEV charges are `+9,-9`, whose
gcd is `{branch['unbroken_gauge_subgroup']['gcd_of_nonzero_VEV_charges']}`;
the unbroken gauge group is exactly `Z9`.

For full-rank `lambdaL`, `lambdaR`, and nonzero singlet couplings, all listed
anomalon pairs acquire masses proportional to `v_F`.  The stabilizer/radial
mode is massive, the relative Theta mode is eaten by the massive `U(1)_F`
vector multiplet, and the `F/Fc` messenger has mass `M_F`.

The ordinary anomaly recheck totals are `{anomaly['totals']}`.

## What is still open

`STheta`, `X`, and `Zp` have the same listed PS, `U(1)_F`, `Z4R`, `Z5610`,
and PQ signatures.  Therefore the existing product symmetries allow terms
such as `X ThetaPlus ThetaMinus`; the isolated source is not a protected
separation from the host driver sector.  Its consequence is:

> {embedding['consequence']}

An arbitrary Kahler/soft sector can also destabilize an anomalon direction.
The branch preserves `Z9` only while every field whose `U(1)_F` charge is not
a multiple of nine remains at zero.  No full Kahler/soft global vacuum,
product-anomaly completion, pole spectrum, flavour fit, or G gate is claimed.

Core SHA-256: `{report['core_sha256']}`
"""


def validate(report: Mapping[str, Any]) -> None:
    if report.get("status") != STATUS:
        raise RuntimeError("unexpected V41 source-sector status")
    if canonical_sha(report) != report.get("core_sha256"):
        raise RuntimeError("stale V41 source-sector core hash")
    terms = report["superpotential_charge_audit"]
    if not all(terms[key] for key in (
        "all_U1F_neutral", "all_Z9_neutral", "all_Z4R_charge_two",
        "all_Z5610_neutral", "all_PQ_neutral", "all_declared_PS_invariants",
    )):
        raise RuntimeError("declared source superpotential violates its own charge table")
    branch = report["canonical_F_D_flat_branch"]
    if not branch["canonical_branch_exists"] or not branch["branch"]["zero_F"] or not branch["FI_deformed_solution"]["zero_D"]:
        raise RuntimeError("canonical F/D branch is not established")
    if branch["unbroken_gauge_subgroup"]["result"] != "Z9":
        raise RuntimeError("the declared U(1)_F branch does not retain Z9")
    mass = report["massability_audit"]
    if not mass["all_required_U1F_breaking_and_anomalon_fields_massable_on_witness"]:
        raise RuntimeError("a required anomalon/source field lacks a mass witness")
    if not report["ordinary_anomaly_recheck"]["all_listed_ordinary_PS_times_U1F_anomalies_cancel"]:
        raise RuntimeError("ordinary U(1)_F anomaly completion arithmetic failed")
    embedding = report["host_embedding_boundary"]
    if not embedding["all_three_signatures_identical"]:
        raise RuntimeError("expected STheta/X/Zp embedding warning disappeared")
    if not all(row["allowed_by_listed_product_symmetries"] for row in embedding["representative_allowed_cross_terms"]):
        raise RuntimeError("cross-coupling boundary has inconsistent charge arithmetic")
    decision = report["decision"]
    if decision["full_coupled_PS_PQ_U1F_source_exists"] or decision["full_Kahler_soft_vacuum_exists"]:
        raise RuntimeError("a conditional source audit cannot claim a full V41 vacuum")
    if decision["full_gate_closed"]:
        raise RuntimeError("this source sub-audit must not close a full gate")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    markdown = render_markdown(report)
    if args.write:
        OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUTPUT_MD.write_text(markdown, encoding="utf-8")
        print("SUSY V41 Z9 U1F source-sector audit: wrote certificates")
    if args.check:
        expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if not OUTPUT_JSON.exists() or not OUTPUT_MD.exists():
            raise SystemExit("generated V41 source-sector certificates are missing; run with --write")
        if OUTPUT_JSON.read_text(encoding="utf-8") != expected_json:
            raise SystemExit("generated V41 source-sector JSON is stale; run with --write")
        if OUTPUT_MD.read_text(encoding="utf-8") != markdown:
            raise SystemExit("generated V41 source-sector Markdown is stale; run with --write")
        print("SUSY V41 Z9 U1F source-sector audit: PASS")


if __name__ == "__main__":
    main()
