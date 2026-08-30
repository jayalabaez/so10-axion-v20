#!/usr/bin/env python3
"""Fail-closed stress audit of the prospective V40 U(1)_F -> Z9 route.

This is deliberately a *negative-control/architecture* certificate, not a
V40 model source.  It verifies the useful pieces of the proposed charge
assignment (the exact pure-Q^4 ring block and ordinary U(1)_F anomaly
arithmetic), then proves why the stated N_D sector cannot be a Majorana
type-I seesaw while the Z9 selector remains exact.

No microscopic U(1)_X x U(1)_H lift, R/PQ charge table, vacuum, or pole
spectrum is inferred here.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
OUTPUT_JSON = ROOT / "SUSY_V40_Z9_U1F_STRESS_AUDIT.json"
OUTPUT_MD = ROOT / "SUSY_V40_Z9_U1F_STRESS_AUDIT.md"
TEST = ROOT / "test_susy_v40_z9_u1f_stress_audit.py"

STATUS = (
    "V40_U1F_TO_Z9_PURE_Q4_RING_PROTECTION_AND_ORDINARY_PARENT_ANOMALIES_"
    "VALIDATED__EXACT_MAJORANA_SEESAW_NO_GO__NOT_A_COMPLETE_V40_SOURCE"
)

N = 9

# Physical Weyl-component dimensions.  The PS doubled Dynkin factors already
# include family and spectator multiplicities, exactly as in the V39 audit.
VISIBLE: dict[str, dict[str, int]] = {
    "H": {"dim": 4, "f": 0},
    "Q": {"dim": 24, "f": 3},
    "Qc": {"dim": 24, "f": -3},
    "X": {"dim": 1, "f": 0},
    "Zp": {"dim": 1, "f": 0},
    "Sc": {"dim": 8, "f": 0},
    "Sbc": {"dim": 8, "f": 0},
    "SigC": {"dim": 6, "f": 0},
    "SigBc": {"dim": 6, "f": 0},
    "PsiBar": {"dim": 8, "f": -3},
    "Psi": {"dim": 8, "f": 3},
    "PsiC": {"dim": 8, "f": -3},
    "PsiCBar": {"dim": 8, "f": 3},
    "P": {"dim": 1, "f": 0},
    "Pb": {"dim": 1, "f": 0},
    "A2": {"dim": 1, "f": 3},
    "A32": {"dim": 1, "f": -3},
    "A15": {"dim": 1, "f": 0},
    "A17": {"dim": 1, "f": 0},
    "A16": {"dim": 1, "f": 0},
    # Three light sterile fields, one per family, are required for the
    # displayed Q H Sc N_D operator.
    "ND": {"dim": 3, "f": -3},
}

PS_DOUBLED_DYNKIN: dict[str, dict[str, int]] = {
    "SU4": {
        "Q": 6,
        "Qc": 6,
        "Sc": 2,
        "Sbc": 2,
        "SigC": 2,
        "SigBc": 2,
        "PsiBar": 2,
        "Psi": 2,
        "PsiC": 2,
        "PsiCBar": 2,
    },
    "SU2L": {"Q": 12, "H": 2, "PsiBar": 4, "Psi": 4},
    "SU2R": {"Qc": 12, "H": 2, "Sc": 4, "Sbc": 4, "PsiC": 4, "PsiCBar": 4},
}

# A multiplicity row represents copies of a PS representation.  Its ``dim``
# is the physical component dimension per copy and its PS index is the
# doubled Dynkin index per copy.
EXOTICS: tuple[dict[str, Any], ...] = (
    {"name": "ThetaPlus", "copies": 1, "dim": 1, "f": 9, "indices": {}},
    {"name": "ThetaMinus", "copies": 1, "dim": 1, "f": -9, "indices": {}},
    {"name": "L0", "copies": 4, "dim": 2, "f": 0, "indices": {"SU2L": 1}},
    {"name": "Lminus9", "copies": 4, "dim": 2, "f": -9, "indices": {"SU2L": 1}},
    {"name": "R0", "copies": 4, "dim": 2, "f": 0, "indices": {"SU2R": 1}},
    {"name": "Rplus9", "copies": 4, "dim": 2, "f": 9, "indices": {"SU2R": 1}},
    {"name": "S4", "copies": 1, "dim": 1, "f": 4, "indices": {}},
    {"name": "S5", "copies": 1, "dim": 1, "f": 5, "indices": {}},
    {"name": "S3", "copies": 1, "dim": 1, "f": 3, "indices": {}},
    {"name": "S6", "copies": 1, "dim": 1, "f": 6, "indices": {}},
    {"name": "Sminus2", "copies": 1, "dim": 1, "f": -2, "indices": {}},
    {"name": "Sminus7", "copies": 1, "dim": 1, "f": -7, "indices": {}},
)

# The representative V37 U(1)_X/Z66 and U(1)_H/Z85 lifts.  These are used
# only to expose missing mixed-parent data, not to claim a unique continuous
# lift of Z5610.
V37_PARENT_REPRESENTATIVES = {
    # These are the primitive continuous lifts declared in
    # susy_v38_g1_uv_completion_audit.py, not merely residues.  ``dim`` is
    # the physical component multiplicity used in ordinary Abelian triangles.
    "PsiBar": {"dim": 8, "f": -3, "x": -2, "h": 0},
    "PsiCBar": {"dim": 8, "f": 3, "x": -2, "h": 0},
    "A2": {"dim": 1, "f": 3, "x": -29, "h": 1},
    "A32": {"dim": 1, "f": -3, "x": 31, "h": -1},
}


def canonical_sha(payload: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(payload))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def u1f_anomalies() -> dict[str, Any]:
    visible_ps = {
        group: sum(
            PS_DOUBLED_DYNKIN[group].get(name, 0) * row["f"]
            for name, row in VISIBLE.items()
        )
        for group in PS_DOUBLED_DYNKIN
    }
    exotic_ps = {
        group: sum(
            row["copies"] * row["indices"].get(group, 0) * row["f"]
            for row in EXOTICS
        )
        for group in PS_DOUBLED_DYNKIN
    }
    visible_gravity = sum(row["dim"] * row["f"] for row in VISIBLE.values())
    exotic_gravity = sum(row["copies"] * row["dim"] * row["f"] for row in EXOTICS)
    visible_cubic = sum(row["dim"] * row["f"] ** 3 for row in VISIBLE.values())
    exotic_cubic = sum(row["copies"] * row["dim"] * row["f"] ** 3 for row in EXOTICS)
    total_ps = {group: visible_ps[group] + exotic_ps[group] for group in PS_DOUBLED_DYNKIN}
    return {
        "convention": "PS rows use 2T(R) times all other multiplicities; gravity/cubic rows use physical Weyl-component multiplicities.",
        "visible_PS_squared_U1F_doubled": visible_ps,
        "exotic_PS_squared_U1F_doubled": exotic_ps,
        "total_PS_squared_U1F_doubled": total_ps,
        "visible_gravity_squared_U1F": visible_gravity,
        "exotic_gravity_squared_U1F": exotic_gravity,
        "total_gravity_squared_U1F": visible_gravity + exotic_gravity,
        "visible_U1F_cubed": visible_cubic,
        "exotic_U1F_cubed": exotic_cubic,
        "total_U1F_cubed": visible_cubic + exotic_cubic,
        "all_listed_ordinary_parent_anomalies_cancel_exactly": (
            all(value == 0 for value in total_ps.values())
            and visible_gravity + exotic_gravity == 0
            and visible_cubic + exotic_cubic == 0
        ),
        "massability_of_the_completion_rows": {
            "doublet_pairs": [
                "ThetaPlus L0 Lminus9",
                "ThetaMinus R0 Rplus9",
            ],
            "singlet_pairs": [
                "ThetaMinus S4 S5",
                "ThetaMinus S3 S6",
                "ThetaPlus Sminus2 Sminus7",
            ],
            "qualification": "These U(1)_F-invariant cubic mass couplings become heavy thresholds only if the displayed Theta branch is actually stabilized.",
        },
    }


def residual_z9_checks() -> dict[str, Any]:
    rows = list(VISIBLE.values()) + [
        {"dim": row["copies"] * row["dim"], "f": row["f"]}
        for row in EXOTICS
    ]
    linear = sum(row["dim"] * row["f"] for row in rows)
    cubic = sum(row["dim"] * row["f"] ** 3 for row in rows)
    low_energy = list(VISIBLE.values())
    low_linear = sum(row["dim"] * row["f"] for row in low_energy)
    low_cubic = sum(row["dim"] * row["f"] ** 3 for row in low_energy)
    coefficient = N * N + 3 * N + 2
    return {
        "Higgsing": {
            "parent": "gauged U(1)_F",
            "Theta_charges": [9, -9],
            "unbroken_group": "Z9",
            "necessary_branch_condition": "Every field with a nonzero VEV has U(1)_F charge in 9 Z; in particular Sc, Sbc, P, Pb, X, Zp and all exotic/singlet completion fields must have zero VEV.",
        },
        "full_chiral_Hsieh_Dai_Freed_style_arithmetic": {
            "Delta_s1": linear,
            "Delta_s3": cubic,
            "2Delta_s1_mod_9": (2 * linear) % N,
            "(n2+3n+2)Delta_s3_mod_6n": (coefficient * cubic) % (6 * N),
        },
        "low_energy_after_Theta_mass_thresholds": {
            "Delta_s1": low_linear,
            "Delta_s3": low_cubic,
            "2Delta_s1_mod_9": (2 * low_linear) % N,
            "(n2+3n+2)Delta_s3_mod_6n": (coefficient * low_cubic) % (6 * N),
        },
        "qualification": "These are necessary finite-arithmetic checks; they do not compute the full Spin x G_PS x Z9 bordism invariant.",
    }


def pure_q4_ring_proof() -> dict[str, Any]:
    q = VISIBLE["Q"]["f"]
    qc = VISIBLE["Qc"]["f"]
    drivers = {name: VISIBLE[name]["f"] for name in ("X", "Zp")}

    rows = []
    for driver, dcharge in drivers.items():
        for label, matter_charge in (("Q", q), ("Qc", qc)):
            total = dcharge + 4 * matter_charge
            residue = total % N
            rows.append(
                {
                    "operator_class": f"{driver} {label}^4 times arbitrary canonical VEV insertions",
                    "U1F_charge_before_Theta_insertions": total,
                    "Z9_residue": residue,
                    "Diophantine_equation_for_Theta_insertions": f"{total} + 9 k = 0",
                    "integer_solution_exists": total % N == 0,
                    "forbidden": total % N != 0,
                }
            )
    explicit_qc = -12
    return {
        "assumptions": [
            "q_F(X)=q_F(Zp)=0, q_F(Q)=+3 and q_F(Qc)=-3",
            "all canonical PS/PQ/driving VEVs and every other VEV have q_F in 9 Z",
            "the only U(1)_F-breaking insertions are ThetaPlus/ThetaMinus of charges plus/minus 9",
        ],
        "four_pure_operator_classes": rows,
        "canonical_PSVev_counterexample_retested": {
            "V39_counterexample": "X [epsilon_SU2R delta_SU4 (Qc Sbc)]^4 / M^6",
            "U1F_charge": explicit_qc,
            "Z9_residue": explicit_qc % N,
            "Theta_dressed_equation": "-12 + 9 k = 0",
            "integer_solution_exists": False,
            "conclusion": "The V39 degree-nine Qc^4 dressing is forbidden in this Z9 route, provided <Sbc> is Z9 neutral.",
        },
        "proof": (
            "Gauge contractions cannot change U(1)_F charge.  Canonical VEVs and arbitrary Theta powers shift it only by 9 Z, while each pure driver-dressed Q^4 or Qc^4 class has residue +3 or -3 modulo 9."
        ),
        "scope_limit": (
            "This proves only the requested pure Q^4 and Qc^4 holomorphic classes.  In particular X Q^2 Qc^2 is F-neutral and must receive its own PS-component, flavour, SUSY-dressing and hadronic analysis before any full proton-stability statement."
        ),
    }


def seesaw_no_go() -> dict[str, Any]:
    c = VISIBLE["Qc"]["f"]
    nd = VISIBLE["ND"]["f"]
    q = VISIBLE["Q"]["f"]
    return {
        "stated_neutrino_source": {
            "operator": "Q H Sc ND / M",
            "U1F_charge": q + VISIBLE["H"]["f"] + VISIBLE["Sc"]["f"] + nd,
            "after_Sc_VEV": "a Dirac neutrino Yukawa source",
        },
        "explicit_ND_Majorana_test": {
            "operator": "ND ND times arbitrary ThetaPlus/ThetaMinus and canonical-VEV insertions",
            "U1F_equation": f"2({nd}) + 9 k = 0",
            "Z9_residue": (2 * nd) % N,
            "integer_solution_exists": False,
        },
        "type_I_general_theorem": {
            "assumptions": [
                "<Sbc> and every other high-scale VEV preserve the residual selector, so their charges vanish modulo N",
                "the standard Pati-Salam type-I source Sbc Qc N is allowed",
                "a Majorana N N mass is allowed after those VEV insertions",
            ],
            "deduction": [
                "q_N = -q_Qc modulo N from Sbc Qc N",
                "2 q_N = 0 modulo N from the Majorana mass",
                "therefore 2 q_Qc = 0 and hence 4 q_Qc = 0 modulo N",
            ],
            "contradiction": "Exact protection of Qc^4 requires 4 q_Qc != 0 modulo N.  Therefore an unbroken additive residual cannot simultaneously furnish this standard type-I seesaw and protect the full pure Qc^4 ring.",
        },
        "light_Majorana_operator_test": {
            "operator": "(Q H Sc)^2 times residual-neutral VEV insertions",
            "Z9_charge": (2 * (q + VISIBLE["H"]["f"] + VISIBLE["Sc"]["f"])) % N,
            "conclusion": "The exact Z9 also forbids the low-energy Majorana Weinberg class in the stated assignment.",
        },
        "allowed_interpretation": (
            "The stated assignment is a Dirac-neutrino route.  A Dirac seesaw can be designed only by adding specified vectorlike sterile mediators and a neutral small-mixing sector; that is a material new V40 neutrino architecture, not the retained V39 type-I seesaw."
        ),
    }


def parent_cross_boundary() -> dict[str, Any]:
    rows = list(V37_PARENT_REPRESENTATIVES.values())
    values = {
        "F_X_squared": sum(row["dim"] * row["f"] * row["x"] ** 2 for row in rows),
        "F_squared_X": sum(row["dim"] * row["f"] ** 2 * row["x"] for row in rows),
        "F_H_squared": sum(row["dim"] * row["f"] * row["h"] ** 2 for row in rows),
        "F_squared_H": sum(row["dim"] * row["f"] ** 2 * row["h"] for row in rows),
        "F_X_H": sum(row["dim"] * row["f"] * row["x"] * row["h"] for row in rows),
        "F_squared_X_H": sum(row["dim"] * row["f"] ** 2 * row["x"] * row["h"] for row in rows),
    }
    return {
        "input_scope": "The primitive continuous U(1)_X and U(1)_H lifts declared in susy_v38_g1_uv_completion_audit.py, for the F-charged PsiBar, PsiCBar, A2 and A32 rows only.",
        "raw_representative_cross_sums": values,
        "selected_residues": {
            "F_X_squared_mod66": values["F_X_squared"] % 66,
            "F_squared_X_mod66": values["F_squared_X"] % 66,
            "F_H_squared_mod85": values["F_H_squared"] % 85,
            "F_squared_H_mod85": values["F_squared_H"] % 85,
        },
        "conclusion": (
            "The listed U(1)_F exotics are neutral under the old parent representatives, so they do not by themselves supply a U(1)_F x U(1)_X x U(1)_H anomaly completion.  A continuous-parent lift, extra charged UV states, or a quantized Green--Schwarz/Wess--Zumino sector must be specified before calling the combined selector gauge-derived."
        ),
        "qualification": "Representative charges are not a unique continuous lift; nonzero rows are an unresolved necessary UV-completion condition, not a standalone anomaly theorem.",
    }


def pq_r_boundary() -> dict[str, Any]:
    return {
        "missing_data": [
            "Z5610/PQ charges of Theta, all doublet pairs and all singlet pairs",
            "external discrete-R charges and every new superpotential/Kahler term",
            "F/D equations proving no non-9-multiple charged field gains a VEV",
        ],
        "non-worsening_assignment_that_must_be_checked_in_a_real_source": {
            "ThetaPlus_ThetaMinus": "Z5610=PQ=0, R=0",
            "F_breaking_driver": "Z5610=PQ=0, R=2",
            "mass-paired_exotics": "Z5610=PQ=0 and R charges summing to 2 (for example 1+1)",
            "reason": "Those signatures already occur in the V39 (Z5610, R, PQ) lattice, so they do not automatically create a lower charge-lattice PQ-breaking monomial.  A fresh V40 enumeration is still mandatory.",
        },
        "result": "PQ quality is unverified, not inherited.",
    }


def build_report() -> dict[str, Any]:
    report: dict[str, Any] = {
        "status": STATUS,
        "candidate_scope": "prospective 4D gauged U(1)_F Higgsed by charges plus/minus 9 to Z9; not an active V40 SARAH source",
        "input_charge_table": {name: row["f"] for name, row in VISIBLE.items()},
        "completion_exotics": list(EXOTICS),
        "ordinary_U1F_anomaly_audit": u1f_anomalies(),
        "residual_Z9_necessary_audit": residual_z9_checks(),
        "pure_Q4_Qc4_holomorphic_ring": pure_q4_ring_proof(),
        "Majorana_seesaw_no_go": seesaw_no_go(),
        "old_parent_cross_anomaly_boundary": parent_cross_boundary(),
        "PQ_R_vacuum_boundary": pq_r_boundary(),
        "decision": {
            "pure_driver_dressed_Q4_and_Qc4_ring_blocked_conditional_on_neutral_VEV_branch": True,
            "ordinary_listed_U1F_parent_anomalies_cancel": True,
            "retained_V39_type_I_Majorana_seesaw_survives": False,
            "complete_V40_candidate": False,
            "gates_promoted": [],
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(data: Mapping[str, Any]) -> str:
    anomaly = data["ordinary_U1F_anomaly_audit"]
    ring = data["pure_Q4_Qc4_holomorphic_ring"]
    seesaw = data["Majorana_seesaw_no_go"]
    cross = data["old_parent_cross_anomaly_boundary"]
    return f"""# V40 U(1)F to Z9 selector stress audit

Status: `{data['status']}`

This certificate audits a prospective gauged `U(1)_F -> Z9` selector.  It is
not a V40 model source and closes no G gate.

## What survives the stress test

With `q_F(Q,Qc,X,Zp)=(3,-3,0,0)` and every canonical VEV in `9 Z`, each
pure driver-dressed class has residual charge `+3` or `-3` modulo nine.
Theta insertions shift charges only by `9 k`, so none can repair it.  The
former V39 witness `X(Qc Sbc)^4/M^6` has charge `-12 = 6 mod 9` and is also
forbidden.

The listed ordinary-parent anomaly totals are
`PS={anomaly['total_PS_squared_U1F_doubled']}`, gravity
`{anomaly['total_gravity_squared_U1F']}`, and cubic
`{anomaly['total_U1F_cubed']}`: all vanish exactly.

## Decisive neutrino limitation

The proposed `Q H Sc ND/M` source is neutral but creates a **Dirac** Yukawa
after PS breaking.  A Majorana `ND ND` term would require
`{seesaw['explicit_ND_Majorana_test']['U1F_equation']}`, which has no integer
solution.  More generally, a standard type-I source plus a residual-neutral
Majorana mass implies `2 q(Qc)=0`, hence `4 q(Qc)=0`; that contradicts the
same all-ring `Qc^4` protection being sought.  This route cannot retain the
V39 Majorana/type-I seesaw while `Z9` stays exact.

## Remaining boundaries

- Mixed `Q^2 Qc^2` classes are selector-neutral and still need a physical
  operator-ring calculation.
- Representative cross rows with the old `U(1)_X x U(1)_H` parent are nonzero:
  `{cross['raw_representative_cross_sums']}`.  A UV completion or GS/WZ data
  are required.
- New R/PQ charges and the F/D vacuum have not been supplied, so PQ quality
  is unverified.

Core SHA-256: `{data['core_sha256']}`
"""


def validate(data: Mapping[str, Any]) -> None:
    if data.get("status") != STATUS:
        raise RuntimeError("unexpected status")
    if canonical_sha(data) != data.get("core_sha256"):
        raise RuntimeError("stale core hash")
    if not data["ordinary_U1F_anomaly_audit"]["all_listed_ordinary_parent_anomalies_cancel_exactly"]:
        raise RuntimeError("ordinary U(1)_F anomaly arithmetic failed")
    if not all(row["forbidden"] for row in data["pure_Q4_Qc4_holomorphic_ring"]["four_pure_operator_classes"]):
        raise RuntimeError("a pure driver-dressed Q^4 class is allowed")
    if data["pure_Q4_Qc4_holomorphic_ring"]["canonical_PSVev_counterexample_retested"]["integer_solution_exists"]:
        raise RuntimeError("the V39 Qc^4 dressing was not blocked")
    if data["Majorana_seesaw_no_go"]["explicit_ND_Majorana_test"]["integer_solution_exists"]:
        raise RuntimeError("incorrect Majorana no-go")
    if data["decision"]["retained_V39_type_I_Majorana_seesaw_survives"]:
        raise RuntimeError("a no-go cannot claim retained type-I seesaw")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_report()
    validate(data)
    markdown = render_markdown(data)
    if args.write:
        OUTPUT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUTPUT_MD.write_text(markdown, encoding="utf-8")
        print("SUSY V40 Z9 U1F stress audit: wrote certificates")
    if args.check:
        if not OUTPUT_JSON.exists() or not OUTPUT_MD.exists():
            raise SystemExit("generated V40 Z9 U1F certificates are missing; run with --write")
        if OUTPUT_JSON.read_text(encoding="utf-8") != json.dumps(data, indent=2, sort_keys=True) + "\n":
            raise SystemExit("generated V40 Z9 U1F JSON is stale; run with --write")
        if OUTPUT_MD.read_text(encoding="utf-8") != markdown:
            raise SystemExit("generated V40 Z9 U1F Markdown is stale; run with --write")
        print("SUSY V40 Z9 U1F stress audit: PASS")


if __name__ == "__main__":
    main()
