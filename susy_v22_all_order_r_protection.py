#!/usr/bin/env python3
"""Exact holomorphic R-charge design for all-order V22 light-block protection.

The published U(1)_MP charges are retained as an architecture grading, not as
a declared continuous symmetry: spontaneously breaking such a U(1) would add
an unwanted Goldstone multiplet.  The actual source-landed all-order
selection rule is the N=1 R symmetry audited here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import susy_so10x17_v22_contract as contract


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_ALL_ORDER_R_PROTECTION.json"
OUT_MD = ROOT / "SUSY_V22_ALL_ORDER_R_PROTECTION.md"

R = {
    # matter and light Higgs
    "F": 1, "P": 1, "R": 1, "SpecS": 1, "SpecB": 1, "Q": 1,
    "Pbar": 1, "Qbar": 1, "Rbar": 1,
    "H10m": 0, "H10p": 0, "T120m": 0, "T120p": 0,
    # VEV fields have R=0
    "Phi210": 0, "C16": 0, "C16bar": 0, "XMP": 0,
    "Splus": 0, "Sminus": 0, "Phi17p": 0, "Phi17m": 0,
    # missing-partner pairs alternate 0/2; every member is required VEVless
    "DeltaB": 0, "Delta": 2, "DeltaB2": 2, "Delta2": 0,
    # driving fields have R=2 and zero VEV
    "NX": 2, "NS": 2, "Nphi": 2, "NC": 2, "NMP": 2,
    # anomaly-balancing neutral spectator (R=0); its VEV is not required
    "Z0": 0, "Z1": 0, "Z2": 0,
}

TERMS = {
    "Nphi_Phi2": ("Nphi", "Phi210", "Phi210"),
    "NC_CbarC": ("NC", "C16bar", "C16"),
    "NMP_XMP_square": ("NMP", "XMP", "XMP"),
    "rho1": ("XMP", "DeltaB", "Delta"),
    "rho2": ("XMP", "DeltaB2", "Delta2"),
    "gammaH": ("Phi210", "H10m", "Delta"),
    "gammaHb2": ("Phi210", "H10p", "DeltaB2"),
    "gammaT": ("Phi210", "T120m", "Delta"),
    "gammaTb2": ("Phi210", "T120p", "DeltaB2"),
    "kappaX": ("NX", "Phi17p", "Phi17m"),
    "kappaS": ("NS", "Splus", "Sminus"),
    "Y10": ("F", "F", "H10m"),
    "Y120": ("F", "F", "T120m"),
    "Y126eff": ("XMP", "F", "F", "DeltaB"),
    "yP": ("Phi17m", "P", "Pbar"),
    "yQ": ("Phi17m", "Q", "Qbar"),
    "yR": ("Phi17p", "R", "Rbar"),
    "ys": ("Splus", "SpecS", "SpecB"),
    "lambdaP": ("P", "F", "H10m"),
    "lambdaR": ("R", "F", "H10m"),
    "lambdaQB": ("Sminus", "Qbar", "F"),
    "lambdaQR": ("Splus", "Q", "Rbar"),
}

LIGHT = ("H10m", "H10p", "T120m", "T120p")
NONZERO_VEV = ("Phi210", "C16", "C16bar", "XMP", "Splus", "Sminus", "Phi17p", "Phi17m")
ZERO_VEV = ("DeltaB", "Delta", "DeltaB2", "Delta2", "NX", "NS", "Nphi", "NC", "NMP")


def csha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_report() -> dict[str, Any]:
    source_contract = contract.build_report()
    term_rows = {name: {"fields": list(fields), "R_sum": sum(R[f] for f in fields), "allowed_in_W": sum(R[f] for f in fields) == 2}
                 for name, fields in TERMS.items()}
    light_pairs = {f"{a}.{b}": (R[a] + R[b]) for i, a in enumerate(LIGHT) for b in LIGHT[i:]}
    checks = {
        "all_required_superpotential_terms_have_R_two": all(row["allowed_in_W"] for row in term_rows.values()),
        "every_light_bilinear_has_R_zero": all(value == 0 for value in light_pairs.values()),
        "every_declared_nonzero_VEV_has_R_zero": all(R[name] == 0 for name in NONZERO_VEV),
        "every_R_two_nonmatter_field_is_declared_zero_VEV": all(name in ZERO_VEV for name, value in R.items() if value == 2),
        "arbitrary_nonzero_VEV_monomial_cannot_turn_light_bilinear_into_W_term": all(value == 0 for value in light_pairs.values()) and all(R[name] == 0 for name in NONZERO_VEV),
        "opposite_hypercharge_mixings_use_R_two_heavy_fields": R["Delta"] == R["DeltaB2"] == 2,
        "missing_partner_U1_is_grading_not_a_spontaneously_broken_continuous_symmetry": "MissingPartner" not in contract.MODEL_PATH.read_text(encoding="utf-8").split("RpM =", 1)[0],
        "discrete_R_anomaly_and_nonperturbative_audit_still_required": True,
        "R_selection_rule_is_landed_in_the_model_source": source_contract["n_failed"] == 0 and contract.R4 == R,
    }
    failures = [name for name, ok in checks.items() if ok is not True]
    out: dict[str, Any] = {
        "schema": "susy_v22_all_order_r_protection_v1",
        "status": "EXACT_HOLOMORPHIC_R_SELECTION_RULE_SOURCE_LANDED__FULL_VACUUM_AND_KAHLER_OPEN" if not failures else "R_PROTECTION_AUDIT_FAILED",
        "model_source": source_contract["model_source"],
        "contract_core_sha256": source_contract["core_sha256"],
        "superpotential_R_charge": 2,
        "field_R_charges": R,
        "required_terms": term_rows,
        "light_bilinear_R_charges": light_pairs,
        "vacuum_partition": {"nonzero_VEV_R0": list(NONZERO_VEV), "required_zero_VEV": list(ZERO_VEV)},
        "all_order_argument": "a light bilinear has R=0; every arbitrary holomorphic monomial made only from nonzero-VEV fields also has R=0; their product can never have superpotential R=2. Any R=2 insertion is a field whose VEV is required to vanish.",
        "soft_mu_boundary": "R breaking by a source-bound soft/SUGRA spurion may generate mu only at the soft scale; this must be computed in the RG/threshold bridge",
        "remaining_requirements": [
            "prove the complete F/D solution has precisely the declared VEV partition",
            "prove the source-landed anomaly-free discrete R subgroup is preserved by the full vacuum and soft sector",
            "audit Kähler and soft operators and compute the generated mu/Bmu terms",
        ],
        "checks": checks, "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
        "claim_boundary": {"holomorphic_charge_theorem_closed": not failures, "holomorphic_charge_theorem_source_landed": not failures,
                           "source_bound_all_order_protection_closed": False,
                           "canonical_G4_closed": False, "canonical_G5_closed": False},
    }
    body = dict(out); out["core_sha256"] = csha(body)
    return out


def markdown(r: dict[str, Any]) -> str:
    return "\n".join(["# SUSY V22 all-order R-protection design", "", f"- Status: `{r['status']}`", f"- Core: `{r['core_sha256']}`", "",
        r["all_order_argument"], "", "The charge theorem is exact. Canonical G4 remains open until the rule is source-landed, its discrete anomaly is canceled, and the full vacuum proves the required zero-VEV partition.", ""])


def write_outputs(r: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(r), encoding="utf-8", newline="\n")


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args(); r=build_report()
    if a.write: write_outputs(r)
    if a.check and (json.loads(OUT_JSON.read_text(encoding="utf-8")) != r or OUT_MD.read_text(encoding="utf-8") != markdown(r)):
        raise ArithmeticError("R-protection report drift")
    print(r["status"]); print(r["core_sha256"]); return 0 if r["n_failed"] == 0 else 1


if __name__ == "__main__": raise SystemExit(main())
