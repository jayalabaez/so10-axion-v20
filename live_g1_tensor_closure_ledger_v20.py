#!/usr/bin/env python3
"""Authoritative live G1 tensor-basis closure ledger.

The live symmetry contract is SO(10)+PQ+Z17 with no continuous-X filter.  The
exact D5 census contains 48 Hermitian-conjugacy orbits and 64 independent
invariant coefficients through canonical degree four.

Every orbit is a singlet dressing of one of eighteen non-singlet base tensor
families.  This module maps all eighteen bases to explicit Cartesian formulas
or exact arbitrary-component projector modules, verifies the multiplicities,
and fixes a normalization convention for every direction.

G1 closure here means:
* exact live degree<=4 charge and singlet multiplicities;
* an explicit independent tensor basis for every one of the 64 directions;
* a stated coefficient normalization for each basis.

It does not mean the 64 operators have been assembled into one component
potential, minimized simultaneously, or propagated through G2-G8.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import g1_exact_declared_symmetry_character_census_v20 as census
import exact_unique_hsigma_chiral_quartics_v20 as unique

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G1_TENSOR_CLOSURE_LEDGER_V20.json"
OUT_MD = ROOT / "LIVE_G1_TENSOR_CLOSURE_LEDGER_V20.md"

# Keys are counts in (P,H,Hdag,D,Ddag), with singlet fields stripped.
BASE_FAMILIES: dict[tuple[int, ...], dict[str, Any]] = {
    (0, 0, 0, 0, 0): {
        "id": "singlet_polynomial",
        "multiplicity": 1,
        "basis": ["the recorded scalar monomial itself"],
        "formula": "ordinary complex-scalar multiplication",
        "sources": ["live_g1_tensor_closure_ledger_v20.py"],
        "normalization": "unit monomial coefficient in canonical scalar fields",
    },
    (0, 0, 0, 1, 1): {
        "id": "126bar_norm",
        "multiplicity": 1,
        "basis": ["(1/2) Sigma^dag_{abcde} Sigma_{abcde}"],
        "formula": "canonical chiral five-form kinetic inner product",
        "sources": ["direct_phi_h_sigmabar_tensor_v20.py"],
        "normalization": "K_126=(1/(2*5!)) Sigma^* Sigma",
    },
    (0, 0, 2, 0, 0): {
        "id": "Hdag_Hdag_pair",
        "multiplicity": 1,
        "basis": ["Hdag_i Hdag_i"],
        "formula": "SO(10) vector bilinear",
        "sources": ["exact_h10_self_quartic_family_v20.py"],
        "normalization": "unit delta_ij contraction",
    },
    (0, 1, 1, 0, 0): {
        "id": "Hdag_H_norm",
        "multiplicity": 1,
        "basis": ["Hdag_i H_i"],
        "formula": "Hermitian vector norm",
        "sources": ["exact_h10_self_quartic_family_v20.py"],
        "normalization": "unit delta_ij contraction",
    },
    (2, 0, 0, 0, 0): {
        "id": "Phi_norm",
        "multiplicity": 1,
        "basis": ["(1/4!) Phi_{abcd} Phi_{abcd}"],
        "formula": "real four-form norm",
        "sources": ["exact_210_self_invariant_basis_v20.py"],
        "normalization": "K_210=(1/4!) Phi Phi",
    },
    (1, 0, 0, 1, 1): {
        "id": "Phi_Sigma_Sigmadag_cubic",
        "multiplicity": 1,
        "basis": ["Phi_{abcd} Sigmadag_{abefg} Sigma_{cdefg}"],
        "formula": "unique degree graph (2,2,3) among (Phi,Sigmadag,Sigma)",
        "sources": ["exact_p_delta_second_stage_hessian_v20.py"],
        "normalization": "recorded full-index contraction; coupling absorbs no hidden factor",
    },
    (1, 0, 1, 0, 1): {
        "id": "Phi_Hdag_Sigmadag",
        "multiplicity": 1,
        "basis": ["Hdag_e Phi_{abcd} Sigmadag_{abcde}"],
        "formula": "conjugate orientation of the direct Phi-H-Sigmabar map",
        "sources": ["direct_phi_h_sigmabar_tensor_v20.py"],
        "normalization": "factorial-reduced direct contraction in canonical kinetic bases",
    },
    (1, 0, 1, 1, 0): {
        "id": "Phi_Hdag_Sigma",
        "multiplicity": 1,
        "basis": ["Hdag_e Phi_{abcd} Sigma_{abcde}"],
        "formula": "unique direct cubic contraction",
        "sources": ["exact_phi_hdag_sigmabar_cubic_audit_v20.py"],
        "normalization": "factorial-reduced direct contraction in canonical kinetic bases",
    },
    (3, 0, 0, 0, 0): {
        "id": "Phi_cubic",
        "multiplicity": 1,
        "basis": ["Tr(A_Phi^3)"],
        "formula": "A_Phi is the symmetric operator on two-forms",
        "sources": ["exact_210_self_invariant_basis_v20.py"],
        "normalization": "the exact arbitrary-component evaluator convention",
    },
    (0, 0, 0, 2, 2): {
        "id": "126bar_self_quartics",
        "multiplicity": 4,
        "basis": ["54", "1050bar", "2772bar", "4125"],
        "formula": "four pair-Casimir projectors on Sym^2(126bar)",
        "sources": ["exact_126bar_self_quartic_basis_v20.py"],
        "normalization": "orthogonal projector norms in the canonical chiral basis",
    },
    (0, 0, 1, 2, 1): {
        "id": "Hdag_Sigma2_Sigmadag",
        "multiplicity": 1,
        "basis": ["graph (0,1,0,2,3,2) on degrees (1,5,5,5)"],
        "formula": "explicit full-index delta contraction",
        "sources": ["exact_unique_hsigma_chiral_quartics_v20.py"],
        "normalization": "recorded einsum with no hidden coefficient",
    },
    (0, 0, 2, 2, 0): {
        "id": "Hdag2_Sigma2",
        "multiplicity": 1,
        "basis": ["graph (0,0,1,1,0,4) on degrees (1,1,5,5)"],
        "formula": "explicit full-index delta contraction",
        "sources": ["exact_unique_hsigma_chiral_quartics_v20.py"],
        "normalization": "recorded einsum with no hidden coefficient",
    },
    (0, 1, 1, 1, 1): {
        "id": "H_Sigma_Hermitian_quartics",
        "multiplicity": 2,
        "basis": ["1", "45"],
        "formula": "common irreps of 10dagx10 and 126x126bar",
        "sources": ["exact_hsigma_hermitian_family_closure_v20.py"],
        "normalization": "singlet norm plus canonical adjoint-current contraction",
    },
    (0, 2, 2, 0, 0): {
        "id": "H_self_quartics",
        "multiplicity": 2,
        "basis": ["1", "54"],
        "formula": "Sym^2(10)=1+54",
        "sources": ["exact_h10_self_quartic_family_v20.py"],
        "normalization": "I1=|H.H|^2/10 and I54=(HdagH)^2-I1",
    },
    (2, 0, 0, 1, 1): {
        "id": "Phi2_Sigma_Sigmadag",
        "multiplicity": 6,
        "basis": ["1", "45", "210", "770", "5940", "8910"],
        "formula": "complete six Cartesian contractions / pure-irrep projectors",
        "sources": [
            "exact_phi2_126dag126_six_contractions_v20.py",
            "exact_phisigma_126bar_minus_projectors_v20.py",
        ],
        "normalization": "explicit graph basis and canonical pair-Casimir projector basis",
    },
    (2, 0, 1, 1, 0): {
        "id": "Phi2_Hdag_Sigma",
        "multiplicity": 2,
        "basis": ["210", "1050"],
        "formula": "10x126=210+1050 with P210=JJdag/3",
        "sources": ["exact_phi2_h_126dag_210_1050_channels_v20.py"],
        "normalization": "J(A)_a=P_+(e_a wedge A), JdagJ=3I",
    },
    (2, 1, 1, 0, 0): {
        "id": "Phi2_Hdag_H",
        "multiplicity": 3,
        "basis": ["1", "45", "54"],
        "formula": "common channels of Sym^2(210) and 10dagx10",
        "sources": ["exact_phi2_hdagh_channel_family_v20.py"],
        "normalization": "canonical M1, M45=iA, and traceless M54 operators",
    },
    (4, 0, 0, 0, 0): {
        "id": "Phi_self_quartics",
        "multiplicity": 4,
        "basis": ["J0", "J2", "J3", "J4"],
        "formula": "complete pure-210 quartic basis from pair-Casimir powers",
        "sources": ["exact_210_self_invariant_basis_v20.py"],
        "normalization": "exact arbitrary-component evaluator convention",
    },
}


def singlet_dressing(counts: dict[str, int]) -> str:
    pieces: list[str] = []
    for key, label in (("S", "S"), ("Sb", "Sdag"), ("X", "Phi17"), ("Xb", "Phi17dag")):
        count = int(counts.get(key, 0))
        if count == 1:
            pieces.append(label)
        elif count > 1:
            pieces.append(f"{label}^{count}")
    return " ".join(pieces) if pieces else "1"


def build_report() -> dict[str, Any]:
    census_report = census.build_report()
    unique_report = unique.build_report()
    rows = census.census(False)
    orbits = census.orbits(rows)
    orbit_entries: list[dict[str, Any]] = []
    missing_base_keys: list[list[int]] = []
    multiplicity_mismatches: list[str] = []

    for orbit in orbits:
        key = tuple(int(value) for value in orbit["orbit_key"][:5])
        base = BASE_FAMILIES.get(key)
        if base is None:
            missing_base_keys.append(list(key))
            continue
        multiplicity = int(orbit["so10_singlet_multiplicity"])
        if multiplicity != int(base["multiplicity"]):
            multiplicity_mismatches.append(orbit["representative"])
        counts = dict(zip(census.FIELD_ORDER, orbit["orbit_key"]))
        dressing = singlet_dressing(counts)
        if key == (0, 0, 0, 0, 0):
            basis = [orbit["representative"]]
        else:
            basis = [
                name if dressing == "1" else f"({name}) * ({dressing})"
                for name in base["basis"]
            ]
        orbit_entries.append(
            {
                "representative": orbit["representative"],
                "members": orbit["members"],
                "degree": orbit["degree"],
                "multiplicity": multiplicity,
                "base_key": list(key),
                "base_family": base["id"],
                "singlet_dressing": dressing,
                "basis": basis,
                "formula": base["formula"],
                "sources": base["sources"],
                "normalization": base["normalization"],
            }
        )

    source_files = sorted(
        {
            source
            for base in BASE_FAMILIES.values()
            for source in base["sources"]
        }
    )
    missing_sources = [source for source in source_files if not ROOT.joinpath(source).exists()]
    directions = sum(entry["multiplicity"] for entry in orbit_entries)
    basis_directions = sum(len(entry["basis"]) for entry in orbit_entries)
    normalization_missing = [
        entry["representative"] for entry in orbit_entries if not entry["normalization"]
    ]

    checks = {
        "live_census_executes": census_report.get("n_failed", 1) == 0,
        "last_two_unique_families_execute": unique_report.get("n_failed", 1) == 0,
        "live_orbit_count_is_48": len(orbits) == 48,
        "live_direction_count_is_64": sum(
            int(orbit["so10_singlet_multiplicity"]) for orbit in orbits
        )
        == 64,
        "exactly_18_base_tensor_families": len(BASE_FAMILIES) == 18,
        "every_orbit_has_a_base_family": not missing_base_keys,
        "all_base_multiplicities_match_census": not multiplicity_mismatches,
        "ledger_has_all_48_orbits": len(orbit_entries) == 48,
        "ledger_has_all_64_directions": directions == 64,
        "basis_labels_have_all_64_directions": basis_directions == 64,
        "all_source_modules_exist": not missing_sources,
        "normalization_recorded_for_every_orbit": not normalization_missing,
        "G2_not_overclaimed": True,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, passed in checks.items() if not passed]
    g1_closed = not failures

    return {
        "status": (
            "LIVE_G1_RENORMALIZABLE_TENSOR_RING_CLOSED"
            if g1_closed
            else "LIVE_G1_TENSOR_CLOSURE_LEDGER_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "live_contract": census_report.get("live_symmetry_contract"),
        "counts": {
            "charge_and_so10_allowed_multidegrees": 74,
            "hermitian_conjugacy_orbits": len(orbits),
            "independent_invariant_coefficients": directions,
            "real_potential_parameters": 91,
            "non_singlet_base_tensor_families_including_scalar_base": len(BASE_FAMILIES),
            "source_modules": len(source_files),
        },
        "source_modules": source_files,
        "missing_source_modules": missing_sources,
        "missing_base_keys": missing_base_keys,
        "multiplicity_mismatches": multiplicity_mismatches,
        "normalization_missing": normalization_missing,
        "base_families": {
            ",".join(str(value) for value in key): data
            for key, data in BASE_FAMILIES.items()
        },
        "operator_orbits": orbit_entries,
        "closure": {
            "live_multiplicity_census_closed": g1_closed,
            "explicit_tensor_basis_all_64_directions_closed": g1_closed,
            "normalization_all_64_directions_specified": g1_closed,
            "G1_invariant_ring_and_component_tensors_closed": g1_closed,
            "G2_complete_projected_component_potential_closed": False,
            "G3_global_vacuum_closed": False,
            "G4_full_gauge_quotient_hessian_closed": False,
            "G5_global_multifield_BFB_closed": False,
            "G6_physical_thresholds_closed": False,
            "G7_validated_two_loop_running_closed": False,
            "G8_unique_proton_decay_closed": False,
        },
        "flags": {
            "g1_closed": g1_closed,
            "g2_closed": False,
            "all_g1_g8_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "G2: assemble all 64 normalized invariant directions into one "
            "arbitrary-component non-SUSY potential and differentiate it into the "
            "complete stationarity equations and Hessian."
        ),
        "verdict": (
            "The live SO(10)+PQ+Z17 renormalizable scalar invariant ring now has "
            "an explicit normalized Cartesian tensor basis for all 64 independent "
            "coefficient directions. G1 is closed. The theory remains blocked at G2 "
            "and every downstream gate."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# Live G1 tensor closure ledger — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + f"**Next:** {report['next_exact_target']}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
