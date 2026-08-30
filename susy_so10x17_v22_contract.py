#!/usr/bin/env python3
"""Source-exact candidate contract for the V22 SUSY continuation.

This is a design/audit artifact.  It does not close canonical V21 G4 or G5.
It establishes the smallest anomaly-vectorlike N=1 field/charge scaffold used
for the subsequent exact superpotential, vacuum, spectrum and soft-EWSB work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from fractions import Fraction
from typing import Any


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models/SO10X17SUSYV22/SO10X17SUSYV22.m"
OUT_JSON = ROOT / "SUSY_SO10X17_V22_CONTRACT.json"
OUT_MD = ROOT / "SUSY_SO10X17_V22_CONTRACT.md"
SCHEMA = "susy_so10x17_v22_candidate_contract_v1"

INDEX = {1: 0, 10: 1, 16: 2, 120: 28, 126: 35, 210: 56}


def q(value: int | Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def field(name: str, multiplicity: int, dim: int, x: int, mp: int | Fraction, role: str) -> dict[str, Any]:
    return {"name": name, "multiplicity": multiplicity, "SO10_dimension": dim,
            "SO10_Dynkin_index": INDEX[abs(dim)], "X": x, "Z17": x % 17,
            "MP": q(mp), "role": role}


FIELDS = (
    field("F", 3, 16, 1, Fraction(-1, 2), "matter"), field("P", 1, 16, 1, Fraction(-1, 2), "matter"),
    field("R", 1, 16, 1, Fraction(-1, 2), "matter"), field("SpecS", 5, 16, 2, Fraction(-1, 2), "matter"),
    field("SpecB", 5, -16, -6, Fraction(-1, 2), "matter"), field("Q", 1, 16, 14, Fraction(-1, 2), "matter"),
    field("Pbar", 1, -16, 16, Fraction(-1, 2), "matter"), field("Qbar", 1, -16, 3, Fraction(-1, 2), "matter"),
    field("Rbar", 1, -16, -18, Fraction(-1, 2), "matter"),
    field("Phi210", 1, 210, 0, 0, "heavy_Higgs"),
    field("DeltaB", 1, -126, -2, -1, "heavy_Higgs"), field("Delta", 1, 126, 2, -1, "heavy_Higgs"),
    field("DeltaB2", 1, -126, -2, -1, "heavy_Higgs"), field("Delta2", 1, 126, 2, -1, "heavy_Higgs"),
    field("H10m", 1, 10, -2, 1, "light_Higgs"), field("H10p", 1, 10, 2, 1, "light_Higgs"),
    field("T120m", 1, 120, -2, 1, "light_Higgs"), field("T120p", 1, 120, 2, 1, "light_Higgs"),
    field("Splus", 1, 1, 4, 1, "Higgs"), field("Sminus", 1, 1, -4, 1, "Higgs"),
    field("Phi17p", 1, 1, 17, 1, "Higgs"), field("Phi17m", 1, 1, -17, 1, "Higgs"),
    field("NX", 1, 1, 0, -2, "driving"), field("NS", 1, 1, 0, -2, "driving"),
    field("XMP", 1, 1, 0, 2, "missing_partner_spurion"),
    field("C16", 1, 16, 0, Fraction(3, 2), "rank_breaking_Higgs"),
    field("C16bar", 1, -16, 0, Fraction(-3, 2), "rank_breaking_Higgs"),
    field("Nphi", 1, 1, 0, 0, "driving"),
    field("Z0", 1, 1, 0, 0, "discrete_R_anomaly_spectator"),
    field("NC", 1, 1, 0, 0, "driving"),
    field("NMP", 1, 1, 0, 0, "driving"),
    field("Z1", 1, 1, 0, 0, "discrete_R_anomaly_spectator"),
    field("Z2", 1, 1, 0, 0, "discrete_R_anomaly_spectator"),
)

R4 = {
    "F": 1, "P": 1, "R": 1, "SpecS": 1, "SpecB": 1, "Q": 1,
    "Pbar": 1, "Qbar": 1, "Rbar": 1,
    "Phi210": 0, "DeltaB": 0, "Delta": 2, "DeltaB2": 2, "Delta2": 0,
    "H10m": 0, "H10p": 0, "T120m": 0, "T120p": 0,
    "Splus": 0, "Sminus": 0, "Phi17p": 0, "Phi17m": 0,
    "NX": 2, "NS": 2, "XMP": 0, "C16": 0, "C16bar": 0,
    "Nphi": 2, "Z0": 0, "NC": 2, "NMP": 2, "Z1": 0, "Z2": 0,
}
for _field in FIELDS:
    _field["R4"] = R4[_field["name"]]

TERMS = {
    "kappaPhi": ("Nphi", "Phi210", "Phi210"),
    "zetaPhi": ("Nphi", "Phi210", "Phi210", "Phi210"),
    "kappaC": ("NC", "C16bar", "C16"),
    "xiC": ("NC", "C16bar", "Phi210", "C16"),
    "kappaMP": ("NMP", "XMP", "XMP"),
    "rho1": ("XMP", "DeltaB", "Delta"), "rho2": ("XMP", "DeltaB2", "Delta2"),
    "gammaH": ("Phi210", "H10m", "Delta"),
    "gammaHb2": ("Phi210", "H10p", "DeltaB2"),
    "gammaT": ("Phi210", "T120m", "Delta"),
    "gammaTb2": ("Phi210", "T120p", "DeltaB2"),
    "kappaX": ("NX", "Phi17p", "Phi17m"), "kappaS": ("NS", "Splus", "Sminus"),
    "Y10": ("F", "F", "H10m"), "Y126eff": ("XMP", "F", "F", "DeltaB"),
    "Y120": ("F", "F", "T120m"), "yP": ("Phi17m", "P", "Pbar"),
    "yQ": ("Phi17m", "Q", "Qbar"), "yR": ("Phi17p", "R", "Rbar"),
    "ys": ("Splus", "SpecS", "SpecB"), "lambdaP": ("P", "F", "H10m"),
    "lambdaR": ("R", "F", "H10m"), "lambdaQB": ("Sminus", "Qbar", "F"),
    "lambdaQR": ("Splus", "Q", "Rbar"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha(value: Any) -> str:
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def anomalies(fields: tuple[dict[str, Any], ...] = FIELDS) -> dict[str, int]:
    return {
        "SO10_squared_U1X": sum(f["multiplicity"] * f["SO10_Dynkin_index"] * f["X"] for f in fields),
        "gravity_squared_U1X": sum(f["multiplicity"] * abs(f["SO10_dimension"]) * f["X"] for f in fields),
        "U1X_cubed": sum(f["multiplicity"] * abs(f["SO10_dimension"]) * f["X"] ** 3 for f in fields),
    }


def term_audit() -> dict[str, dict[str, Any]]:
    by_name = {f["name"]: f for f in FIELDS}
    out = {}
    for coupling, names in TERMS.items():
        x = sum(by_name[name]["X"] for name in names)
        z = sum(by_name[name]["Z17"] for name in names) % 17
        mp = sum(Fraction(by_name[name]["MP"]) for name in names)
        r4 = sum(by_name[name]["R4"] for name in names) % 4
        out[coupling] = {"fields": list(names), "X_sum": x, "Z17_sum_mod_17": z,
                         "MP_sum": q(mp), "R4_sum_mod_4": r4,
                         "source_symmetry_allowed": x == z == 0 and r4 == 2,
                         "literature_MP_grading_neutral": mp == 0}
    return out


def build_report() -> dict[str, Any]:
    model = MODEL_PATH.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    model_text = model.decode("utf-8")
    compact_model = "".join(model_text.split())
    anomaly = anomalies()
    terms = term_audit()
    pairs = (("DeltaB", "Delta"), ("DeltaB2", "Delta2"), ("H10m", "H10p"), ("T120m", "T120p"), ("C16bar", "C16"),
             ("Splus", "Sminus"), ("Phi17p", "Phi17m"))
    by_name = {f["name"]: f for f in FIELDS}
    pair_checks = {
        f"{a}__{b}": by_name[a]["SO10_dimension"] in {by_name[b]["SO10_dimension"], -by_name[b]["SO10_dimension"]}
        and by_name[a]["X"] == -by_name[b]["X"] and (by_name[a]["Z17"] + by_name[b]["Z17"]) % 17 == 0
        for a, b in pairs
    }
    checks = {
        "model_declares_N1_superfields": "SuperFields[[33]]" in model_text,
        "model_declares_Z4R_as_the_only_continuous_R_global_slot": "Global[[3]] = {U[1], RSymmetry};" in model_text and "Global[[4]]" not in model_text,
        "every_audited_coupling_is_landed_in_the_model_catalogue": all(name in model_text for name in TERMS),
        "independent_driver_constraints_are_landed_verbatim": all(token in model_text for token in (
            "Nphi.(Phi210.Phi210 - vPhi2)", "NC.(C16bar.C16 - vC2)",
            "NMP.(XMP.XMP - vMP2)", "NX.(Phi17p.Phi17m - vX2)",
            "NS.(Splus.Sminus - vS2)")),
        "missing_partner_mass_and_mixing_terms_are_landed_with_exact_field_order": all(token in compact_model for token in (
            "rho1XMP.DeltaB.Delta", "rho2XMP.DeltaB2.Delta2",
            "gammaHPhi210.H10m.Delta", "gammaHb2Phi210.H10p.DeltaB2",
            "gammaTPhi210.T120m.Delta", "gammaTb2Phi210.T120p.DeltaB2")),
        "all_continuous_anomalies_cancel_exactly": anomaly == {"SO10_squared_U1X": 0, "gravity_squared_U1X": 0, "U1X_cubed": 0},
        "all_charged_Higgsino_sectors_are_vectorlike": all(pair_checks.values()),
        "every_superpotential_term_is_U1X_Z17_and_R_allowed": all(row["source_symmetry_allowed"] for row in terms.values()),
        "only_the_spurion_phase_fixing_term_breaks_the_nonphysical_MP_grading": [name for name, row in terms.items() if not row["literature_MP_grading_neutral"]] == ["kappaMP"],
        "matter_Yukawas_include_10_effective_126bar_and_120": all(key in terms for key in ("Y10", "Y126eff", "Y120")),
        "U1X_breaking_pair_has_charge_17": by_name["Phi17p"]["X"] == 17 and by_name["Phi17m"]["X"] == -17,
        "residual_Z17_is_X_mod_17_for_every_field": all(f["Z17"] == f["X"] % 17 for f in FIELDS),
        "missing_partner_light_fields_have_MP_plus_one": all(Fraction(by_name[name]["MP"]) == 1 for name in ("H10m", "H10p", "T120m", "T120p")),
        "missing_partner_heavy_126_fields_have_MP_minus_one": all(Fraction(by_name[name]["MP"]) == -1 for name in ("DeltaB", "Delta", "DeltaB2", "Delta2")),
        "separate_rank_breaking_16_pair_has_published_MP_charges": Fraction(by_name["C16"]["MP"]) == Fraction(3, 2) and Fraction(by_name["C16bar"]["MP"]) == Fraction(-3, 2),
        "literature_missing_partner_grading_marks_light_bilinears_nonzero": Fraction(by_name["H10m"]["MP"]) + Fraction(by_name["H10p"]["MP"]) == 2 and Fraction(by_name["T120m"]["MP"]) + Fraction(by_name["T120p"]["MP"]) == 2,
        "all_required_superpotential_terms_have_R4_charge_two": all(row["R4_sum_mod_4"] == 2 for row in terms.values()),
        "all_nonzero_VEV_design_fields_have_R4_zero": all(by_name[name]["R4"] == 0 for name in ("Phi210", "C16", "C16bar", "XMP", "Splus", "Sminus", "Phi17p", "Phi17m")),
        "missing_partner_spurion_phase_is_fixed_to_a_discrete_pair": terms["kappaMP"]["fields"] == ["NMP", "XMP", "XMP"],
        "independent_GUT_and_missing_partner_VEV_constraints_have_distinct_R2_drivers": all(by_name[name]["R4"] == 2 for name in ("Nphi", "NC", "NMP")),
        "every_light_Higgs_bilinear_has_R4_zero": all((by_name[a]["R4"] + by_name[b]["R4"]) % 4 == 0 for a in ("H10m", "H10p", "T120m", "T120p") for b in ("H10m", "H10p", "T120m", "T120p")),
        "V21_G3_not_claimed_as_V22_vacuum_proof": True,
        "canonical_G4_G5_not_prematurely_closed": True,
    }
    failures = [name for name, passed in checks.items() if passed is not True]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "model_contract_id": "susy_so10x17_v22_candidate",
        "status": "V22_SUSY_FIELD_CHARGE_AND_ANOMALY_CONTRACT_CLOSED__VACUUM_AND_G4_G5_OPEN" if not failures else "V22_CONTRACT_AUDIT_FAILED",
        "model_source": {"path": str(MODEL_PATH.relative_to(ROOT)).replace("\\", "/"), "mode": "portable-lf", "sha256": sha(model)},
        "fields": list(FIELDS),
        "continuous_anomalies": anomaly,
        "vectorlike_Higgs_pairs": pair_checks,
        "superpotential_charge_audit": terms,
        "protection_logic": {
            "mechanism": "N=1 supersymmetry above a declared soft-breaking scale",
            "exact_limit": "boson/fermion supertrace cancellation forbids additive quadratic scalar-mass sensitivity",
            "soft_limit_requirement": "all SUSY-breaking operators must be soft and the complete RG-evolved spectrum must remain non-tachyonic",
            "missing_partner_grading": "the published U(1)_MP charges are retained only as a term-by-term architecture grading; no continuous U(1)_MP is declared, so its spurion VEV creates no extra Goldstone",
            "all_order_selection_rule": "source-landed Z4R: W has charge 2, every light bilinear and every nonzero-VEV field has charge 0, and every charge-2 Higgs/driving field is required to have zero VEV",
            "rank_breaking_sector": "C16+C16bar and Phi210 break SO(10), while every missing-partner 126/126bar is required to have zero VEV",
            "not_yet_proved": ["source-exact component Clebsch realization of the 10/13 rank witnesses", "all-order higher-dimensional operator protection with zero missing-partner-126 VEVs", "soft boundary/RGE bridge to the exact v=174 GeV endpoint", "full RGE perturbativity", "global F+D+soft vacuum"],
        },
        "continuity_with_V21": {
            "V21_G1_G2_G3_remain_valid_for_their_frozen_nonSUSY_contract": True,
            "V21_G3_can_be_inherited_as_the_V22_vacuum": False,
            "reason": "V22 adds chiral partners, 120 pairs, F/D terms and soft breaking; its scalar potential and field space differ",
            "required_use": "V21 G3 is a regression/reference theorem only until V22 G1-G3 are independently closed",
        },
        "literature_basis": [
            {"title": "The minimal supersymmetric grand unified theory", "arXiv": "hep-ph/0306242", "scope": "210+126+126bar+10 baseline"},
            {"title": "The New Minimal Supersymmetric GUT: Spectra, RG analysis and fitting formulae", "arXiv": "hep-ph/0612021", "scope": "adds 120 and complete spectrum/RG framework"},
            {"title": "Missing Partner Mechanism in SO(10) Grand Unification", "arXiv": "hep-ph/0612315", "scope": "all-order protected doublet-triplet splitting"},
        ],
        "checks": checks, "n_checks": len(checks), "n_failed": len(failures), "failures": failures,
        "claim_boundary": {"V22_candidate_contract_closed": not failures, "V22_G1_G2_G3_closed": False,
                           "canonical_G4_closed": False, "canonical_G5_closed": False},
    }
    body = dict(report)
    report["core_sha256"] = canonical_sha(body)
    return report


def markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# SUSY SO(10) x U(1)_X V22 candidate contract", "",
        f"- Status: `{report['status']}`", f"- Core: `{report['core_sha256']}`",
        f"- Model source: `{report['model_source']['sha256']}`", "",
        "The exact field/charge catalogue, residual Z17 relation, continuous anomaly cancellation and declared-term superpotential charge ledger are closed.",
        "The declared catalogue is not a complete operator ring. Its selection-rule repair, component projections, global F+D+soft vacuum, protected 174 GeV branch and cal-G/spectrum revalidation remain open.", "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(markdown(report), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.check:
        if json.loads(OUT_JSON.read_text(encoding="utf-8")) != report or OUT_MD.read_text(encoding="utf-8") != markdown(report):
            raise ArithmeticError("V22 contract outputs drifted")
    print(report["status"]); print(report["core_sha256"])
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
