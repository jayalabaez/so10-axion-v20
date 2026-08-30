#!/usr/bin/env python3
"""Exact discrete Z4^R anomaly audit for the V22 protection design."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import susy_so10x17_v22_contract as contract
import susy_v22_all_order_r_protection as rdesign


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SUSY_V22_Z4R_ANOMALY.json"
OUT_MD = ROOT / "SUSY_V22_Z4R_ANOMALY.md"


def csha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_report() -> dict[str, Any]:
    c = contract.build_report()
    rows = []
    for field in c["fields"]:
        name = field["name"]
        if name not in rdesign.R:
            raise ArithmeticError(f"missing R charge for {name}")
        fermion_r = rdesign.R[name] - 1
        rows.append({
            "name": name,
            "multiplicity": field["multiplicity"],
            "dimension": abs(field["SO10_dimension"]),
            "T_SO10": field["SO10_Dynkin_index"],
            "X": field["X"],
            "superfield_R_mod4": rdesign.R[name] % 4,
            "fermion_R_mod4": fermion_r % 4,
            "A_SO10": field["multiplicity"] * field["SO10_Dynkin_index"] * fermion_r,
            "A_X2": field["multiplicity"] * abs(field["SO10_dimension"]) * field["X"] ** 2 * fermion_r,
            "A_X_R2": field["multiplicity"] * abs(field["SO10_dimension"]) * field["X"] * fermion_r ** 2,
            "A_gravity": field["multiplicity"] * abs(field["SO10_dimension"]) * fermion_r,
        })
    a_so10 = 8 + sum(row["A_SO10"] for row in rows)  # SO(10) gaugino
    a_x2 = sum(row["A_X2"] for row in rows)
    a_xr2 = sum(row["A_X_R2"] for row in rows)
    # gravitino -21, SO(10)+U(1)_X gauginos 45+1
    a_grav = -21 + 46 + sum(row["A_gravity"] for row in rows)
    eta = 2  # for even N=4 discrete R symmetry
    checks = {
        "all_contract_fields_have_R_assignments": len(rows) == len(c["fields"]),
        "mixed_SO10_squared_Z4R_vanishes_mod_eta": a_so10 % eta == 0,
        "mixed_U1X_squared_Z4R_vanishes_mod_eta": a_x2 % eta == 0,
        "mixed_U1X_Z4R_squared_vanishes_exactly": a_xr2 == 0,
        "gravitational_Z4R_anomaly_vanishes_mod_eta_with_complete_source_spectrum": a_grav % eta == 0,
        "removing_one_R0_anomaly_partner_flips_gravitational_parity": (a_grav + 1) % eta != 0,
        "discrete_anomaly_check_does_not_replace_full_vacuum_or_operator_audit": True,
    }
    failures = [name for name, ok in checks.items() if ok is not True]
    out: dict[str, Any] = {
        "schema": "susy_v22_z4r_anomaly_v1",
        "status": "EXACT_SOURCE_BOUND_Z4R_MIXED_ANOMALIES_CANCEL_MOD_ETA__VACUUM_PRESERVATION_OPEN" if not failures else "Z4R_ANOMALY_AUDIT_FAILED",
        "N": 4, "eta": eta,
        "conventions": {
            "chiral_fermion_charge": "r_superfield-1",
            "A_SO10": "T(adj)+sum T(R_i)(r_i-1)",
            "A_gravity": "-21+dim(SO10)+dim(U1X)+sum dim(R_i)(r_i-1)",
        },
        "field_rows": rows,
        "anomalies": {"SO10_squared_Z4R": a_so10, "U1X_squared_Z4R": a_x2,
                      "U1X_Z4R_squared": a_xr2, "gravity_squared_Z4R": a_grav},
        "source_landing": {"complete": not failures, "contract_core_sha256": c["core_sha256"], "model_source": c["model_source"]},
        "checks": checks, "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
        "claim_boundary": {"Z4R_mixed_anomaly_arithmetic_closed": not failures,
                           "Z4R_source_bound": not failures,
                           "Z4R_vacuum_and_soft_sector_preserved": False,
                           "canonical_G4_closed": False, "canonical_G5_closed": False},
    }
    body = dict(out); out["core_sha256"] = csha(body)
    return out


def markdown(r: dict[str, Any]) -> str:
    return "\n".join(["# SUSY V22 Z4R anomaly audit", "", f"- Status: `{r['status']}`", f"- Core: `{r['core_sha256']}`",
        f"- Anomalies: `{r['anomalies']}`", "", "All required mixed anomalies vanish under the stated modulo-eta convention in the source-bound spectrum. Preservation by the full vacuum and soft sector remains open.", ""])


def write_outputs(r: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(r), encoding="utf-8", newline="\n")


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--write",action="store_true"); p.add_argument("--check",action="store_true"); a=p.parse_args(); r=build_report()
    if a.write: write_outputs(r)
    if a.check and (json.loads(OUT_JSON.read_text(encoding="utf-8")) != r or OUT_MD.read_text(encoding="utf-8") != markdown(r)):
        raise ArithmeticError("Z4R anomaly report drift")
    print(r["status"]); print(r["core_sha256"]); return 0 if r["n_failed"] == 0 else 1


if __name__ == "__main__": raise SystemExit(main())
