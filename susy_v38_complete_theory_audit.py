#!/usr/bin/env python3
"""Executable, fail-closed master audit for the V37/V38 theory program.

This program deliberately does not turn missing Kähler data, cosmology, flavour
tensors, or UV topological data into benchmark assumptions.  It instead joins
the independently reproducible V37 and V38 certificates, proves one additional
selection-rule obstruction for G7, and writes the exact evidence needed for a
future promotion of each of the eight gates.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
REPORT_JSON = ROOT / "SUSY_V38_COMPLETE_THEORY_AUDIT.json"
REPORT_MD = ROOT / "SUSY_V38_COMPLETE_THEORY_AUDIT.md"
MODEL_SOURCE = ROOT / "models/PSZ4RZ5610SUSYV37/PSZ4RZ5610SUSYV37.m"

INPUT_PATHS = {
    "v37_gate_ledger": ROOT / "SUSY_V37_G1_G8_GATE_LEDGER.json",
    "v37_quality": ROOT / "SUSY_V37_G5_QUALITY_CERTIFICATE.json",
    "v37_routes": ROOT / "SUSY_V37_NEW_PHYSICS_ROUTES.json",
    "v37_nonanomaly": ROOT / "SUSY_V37_NONANOMALY_GATE_AUDIT.json",
    "v37_relic": ROOT / "SUSY_V37_G5_RELIC_COSMOLOGY_AUDIT.json",
    "v38_uv": ROOT / "SUSY_V38_G1_UV_COMPLETION_AUDIT.json",
}

SOURCE_FILES = (
    "susy_v38_complete_theory_audit.py",
    "test_susy_v38_complete_theory_audit.py",
    "susy_v38_g1_uv_completion_audit.py",
    "susy_v37_g5_relic_cosmology_audit.py",
    "susy_v37_nonanomaly_gate_audit.py",
    "susy_v37_new_physics_routes.py",
    "models/PSZ4RZ5610SUSYV37/PSZ4RZ5610SUSYV37.m",
    ".github/workflows/susy-v38-complete-theory-audit.yml",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_manifest() -> list[dict[str, Any]]:
    return [
        {
            "path": name,
            "exists": (ROOT / name).is_file(),
            "sha256": sha256_file(ROOT / name) if (ROOT / name).is_file() else None,
        }
        for name in SOURCE_FILES
    ]


def load_inputs() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for key, path in INPUT_PATHS.items():
        if not path.is_file():
            raise RuntimeError(f"required input is missing: {path.name}")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise RuntimeError(f"input is not an object: {path.name}")
        if "core_sha256" in loaded and canonical_sha(loaded) != loaded["core_sha256"]:
            raise RuntimeError(f"input checksum does not verify: {path.name}")
        result[key] = loaded
    return result


def vector_sum(*terms: tuple[int, Mapping[str, int]]) -> dict[str, int]:
    """Return an integer linear combination of symbolic charge equations."""

    result: dict[str, int] = {}
    for coefficient, equation in terms:
        for variable, value in equation.items():
            result[variable] = result.get(variable, 0) + coefficient * value
    return {variable: value for variable, value in result.items() if value}


def g7_additive_selection_no_go() -> dict[str, Any]:
    """Prove the driver-dressed Q^4 no-go in any additive abelian symmetry.

    The proof is in an arbitrary abelian charge group.  Every displayed
    relation is therefore valid for ordinary U(1)/Z_N symmetries and, with W
    retained as a formal charge, for additive R symmetries too.  It assumes
    unspurioned couplings: an alleged exact shaping symmetry must preserve the
    listed renormalizable V37 terms rather than assign charges to constants.
    """

    source = MODEL_SOURCE.read_text(encoding="utf-8")
    required_terms = {
        "linear_X": "*X",
        "X_cubic": "kappaX/3*X.X.X",
        "X_H_H": "lambdaH/2*X.H.H",
        "X_Sbc_Sc": "kappaPS*X.Sbc.Sc",
        "Sc_Sc_Sig6": "lambdaS/2*Sc.Sc.Sig6",
        "Sbc_Sbc_Sig6": "lambdaSb/2*Sbc.Sbc.Sig6",
        "Sbc_Qc_Nv": "yNQ*Sbc.Qc.Nv",
        "Nv_Nv": "MN/2*Nv.Nv",
        "Q_H_Qc": "YQQ*Q.H.Qc",
    }
    present = {name: text in source for name, text in required_terms.items()}

    # Ordinary (non-R) charges.  Each equation equals zero when the indicated
    # renormalizable monomial is invariant.
    ordinary = {
        "linear_X": {"X": 1},
        "X_H_H": {"X": 1, "H": 2},
        "X_Sbc_Sc": {"X": 1, "Sbc": 1, "Sc": 1},
        "Sc_Sc_Sig6": {"Sc": 2, "Sig6": 1},
        "Sbc_Sbc_Sig6": {"Sbc": 2, "Sig6": 1},
        "Sbc_Qc_Nv": {"Sbc": 1, "Qc": 1, "Nv": 1},
        "Nv_Nv": {"Nv": 2},
        "Q_H_Qc": {"Q": 1, "H": 1, "Qc": 1},
    }
    ordinary_q_combo = vector_sum(
        (4, ordinary["Q_H_Qc"]),
        (-4, ordinary["Sbc_Qc_Nv"]),
        (-2, ordinary["X_H_H"]),
        (2, ordinary["X_Sbc_Sc"]),
        (-1, ordinary["Sc_Sc_Sig6"]),
        (1, ordinary["Sbc_Sbc_Sig6"]),
        (2, ordinary["Nv_Nv"]),
    )
    ordinary_qc_combo = vector_sum(
        (4, ordinary["Sbc_Qc_Nv"]),
        (-2, ordinary["X_Sbc_Sc"]),
        (2, ordinary["linear_X"]),
        (1, ordinary["Sc_Sc_Sig6"]),
        (-1, ordinary["Sbc_Sbc_Sig6"]),
        (-2, ordinary["Nv_Nv"]),
    )

    # For an additive R symmetry, a superpotential monomial has formal charge
    # W.  Keeping W explicit avoids choosing a normalization such as W=2.
    r_equations = {
        "linear_X": {"X": 1, "W": -1},
        "X_cubic": {"X": 3, "W": -1},
        "X_H_H": {"X": 1, "H": 2, "W": -1},
        "X_Sbc_Sc": {"X": 1, "Sbc": 1, "Sc": 1, "W": -1},
        "Sc_Sc_Sig6": {"Sc": 2, "Sig6": 1, "W": -1},
        "Sbc_Sbc_Sig6": {"Sbc": 2, "Sig6": 1, "W": -1},
        "Sbc_Qc_Nv": {"Sbc": 1, "Qc": 1, "Nv": 1, "W": -1},
        "Nv_Nv": {"Nv": 2, "W": -1},
        "Q_H_Qc": {"Q": 1, "H": 1, "Qc": 1, "W": -1},
    }
    r_q_combo = vector_sum(
        (4, r_equations["Q_H_Qc"]),
        (-4, r_equations["Sbc_Qc_Nv"]),
        (-2, r_equations["X_H_H"]),
        (2, r_equations["X_Sbc_Sc"]),
        (-1, r_equations["Sc_Sc_Sig6"]),
        (1, r_equations["Sbc_Sbc_Sig6"]),
        (2, r_equations["Nv_Nv"]),
        (1, r_equations["X_cubic"]),
        (-3, r_equations["linear_X"]),
    )
    r_qc_combo = vector_sum(
        (4, r_equations["Sbc_Qc_Nv"]),
        (-2, r_equations["X_Sbc_Sc"]),
        (2, r_equations["linear_X"]),
        (1, r_equations["Sc_Sc_Sig6"]),
        (-1, r_equations["Sbc_Sbc_Sig6"]),
        (-2, r_equations["Nv_Nv"]),
        (1, r_equations["X_cubic"]),
        (-3, r_equations["linear_X"]),
    )

    expected_q = {"Q": 4}
    expected_qc = {"Qc": 4}
    return {
        "assumption": (
            "An added ordinary or R-type additive Abelian symmetry preserves every listed V37 "
            "renormalizable monomial with uncharged numerical couplings."
        ),
        "source_term_presence": present,
        "ordinary_non_R": {
            "four_Q_linear_combination": {
                "Q_H_Qc": 4,
                "Sbc_Qc_Nv": -4,
                "X_H_H": -2,
                "X_Sbc_Sc": 2,
                "Sc_Sc_Sig6": -1,
                "Sbc_Sbc_Sig6": 1,
                "Nv_Nv": 2,
            },
            "four_Qc_linear_combination": {
                "Sbc_Qc_Nv": 4,
                "X_Sbc_Sc": -2,
                "linear_X": 2,
                "Sc_Sc_Sig6": 1,
                "Sbc_Sbc_Sig6": -1,
                "Nv_Nv": -2,
            },
            "derived_charge_vectors": {
                "4qQ": ordinary_q_combo,
                "4qQc": ordinary_qc_combo,
            },
            "conclusion": (
                "The combinations give 4q(Q)=4q(Qc)=0; the linear X term gives q(X)=0, "
                "so X Q^4 and X Qc^4 are allowed."
            ),
        },
        "additive_R": {
            "four_Q_linear_combination": {
                "Q_H_Qc": 4,
                "Sbc_Qc_Nv": -4,
                "X_H_H": -2,
                "X_Sbc_Sc": 2,
                "Sc_Sc_Sig6": -1,
                "Sbc_Sbc_Sig6": 1,
                "Nv_Nv": 2,
                "X_cubic": 1,
                "linear_X": -3,
            },
            "four_Qc_linear_combination": {
                "Sbc_Qc_Nv": 4,
                "X_Sbc_Sc": -2,
                "linear_X": -1,
                "Sc_Sc_Sig6": 1,
                "Sbc_Sbc_Sig6": -1,
                "Nv_Nv": -2,
                "X_cubic": 1,
            },
            "derived_charge_vectors": {
                "4rQ": r_q_combo,
                "4rQc": r_qc_combo,
            },
            "conclusion": (
                "The combinations give 4r(Q)=4r(Qc)=0.  The linear X term gives r(X)=r(W), "
                "so X Q^4 and X Qc^4 have the superpotential charge and are allowed."
            ),
        },
        "verified": (
            all(present.values())
            and ordinary_q_combo == expected_q
            and ordinary_qc_combo == expected_qc
            and r_q_combo == expected_q
            and r_qc_combo == expected_qc
        ),
        "scope": (
            "This excludes only a simple additive-Abelian selector repair that leaves the full V37 "
            "renormalizable driver/cubic/Majorana/PS-breaking architecture intact.  It does not exclude "
            "non-Abelian flavour, locality/sequestering, spurion dynamics, or an architecture change."
        ),
    }


def gate_rows(inputs: Mapping[str, Mapping[str, Any]], g7_no_go: Mapping[str, Any]) -> list[dict[str, Any]]:
    ledger = inputs["v37_gate_ledger"]
    ledger_by_gate = {row["gate"]: row for row in ledger["gates"]}
    nonanomaly = inputs["v37_nonanomaly"]
    g2_to_g8 = {
        row["gate"]: row
        for row in nonanomaly["G2_G4_G6_G8_gate_conclusions"]
    }
    uv = inputs["v38_uv"]
    relic = inputs["v37_relic"]
    quality = inputs["v37_quality"]
    return [
        {
            "gate": "G1",
            "closed": False,
            "locked_result": (
                "Z5610 finite congruences pass; V38 proves the ordinary 4D Higgsed-U(1)X heavy-threshold "
                "route impossible under its stated assumptions and supplies a locally anomaly-balanced 5D interval EFT."
            ),
            "blocker": "; ".join(uv["required_for_a_genuine_G1_promotion"]),
            "frozen_ledger_state": ledger_by_gate["G1"]["state"],
        },
        {
            "gate": "G2",
            "closed": False,
            "locked_result": nonanomaly["G2_tree_mass_rank"]["scope"],
            "blocker": g2_to_g8["G2"]["blocking_fact"],
            "frozen_ledger_state": ledger_by_gate["G2"]["state"],
        },
        {
            "gate": "G3",
            "closed": False,
            "locked_result": nonanomaly["G3_canonical_global_SUSY_branch"]["scope"],
            "blocker": g2_to_g8["G3"]["blocking_fact"],
            "frozen_ledger_state": ledger_by_gate["G3"]["state"],
        },
        {
            "gate": "G4",
            "closed": False,
            "locked_result": nonanomaly["G4_electroweak_boundary"]["conclusion"],
            "blocker": g2_to_g8["G4"]["blocking_fact"],
            "frozen_ledger_state": ledger_by_gate["G4"]["state"],
        },
        {
            "gate": "G5",
            "closed": False,
            "locked_result": (
                "All-chiral quality stays at W degree %s / Kähler degree %s; the six-field D cascade "
                "passes selector and finite-anomaly checks but leaves stable dark carriers."
                % (
                    relic["conditional_decay_dark_extension"]["quality_lattice"]["superpotential_first_breaking_degree"],
                    relic["conditional_decay_dark_extension"]["quality_lattice"]["Kahler_first_breaking_degree"],
                )
            ),
            "blocker": (
                "An unbroken Z170 forces a lightest charged remnant; a spectrum, mediation, Boltzmann/reheat, "
                "PQ isocurvature/domain-wall, BBN/CMB, and direct-detection calculation is still absent."
            ),
            "frozen_ledger_state": ledger_by_gate["G5"]["state"],
            "quality_selector_congruence": quality["all_chiral_charge_lattice_lower_bound"]["analytic_PQ_congruence"],
        },
        {
            "gate": "G6",
            "closed": False,
            "locked_result": nonanomaly["G6_running_and_matching_boundary"]["conclusion"],
            "blocker": g2_to_g8["G6"]["blocking_fact"],
            "frozen_ledger_state": ledger_by_gate["G6"]["state"],
        },
        {
            "gate": "G7",
            "closed": False,
            "locked_result": (
                "Bare Q^4/Qc^4 are R-forbidden, but their driver-dressed degree-five versions are selector-allowed; "
                "the added-Abelian-shaping-symmetry no-go is symbolically verified."
            ),
            "blocker": (
                g2_to_g8["G7"]["blocking_fact"]
                + ". A simple additional additive Abelian symmetry cannot forbid the class without changing the V37 architecture."
            ),
            "frozen_ledger_state": ledger_by_gate["G7"]["state"],
            "additive_abelian_no_go_verified": g7_no_go["verified"],
        },
        {
            "gate": "G8",
            "closed": False,
            "locked_result": g2_to_g8["G8"]["landed_exact_subproblem"],
            "blocker": g2_to_g8["G8"]["blocking_fact"],
            "frozen_ledger_state": ledger_by_gate["G8"]["state"],
        },
    ]


def report() -> dict[str, Any]:
    inputs = load_inputs()
    g7_no_go = g7_additive_selection_no_go()
    gates = gate_rows(inputs, g7_no_go)
    closed_count = sum(bool(row["closed"]) for row in gates)
    v37_ledger = inputs["v37_gate_ledger"]
    uv = inputs["v38_uv"]
    relic = inputs["v37_relic"]

    integrity_checks = {
        "all_required_inputs_present": len(inputs) == len(INPUT_PATHS),
        "all_input_cores_verify": True,
        "frozen_v37_ledger_has_zero_closed_gates": v37_ledger["established_full_predictive_closed_count"] == 0,
        "v38_ordinary_4D_U1X_no_go_verified": uv["gate_decision"]["ordinary_4D_Higgsed_U1X_solution_exists_under_theorem_assumptions"] is False,
        "v38_5D_anomaly_EFT_verified": uv["gate_decision"]["local_5D_continuous_anomaly_EFT_packet_exists"] is True,
        "g5_residual_relic_obstruction_verified": relic["residual_relic_theorem"]["unbroken_order"] == 170,
        "g7_additive_abelian_no_go_verified": g7_no_go["verified"],
        "no_full_gate_is_promoted": closed_count == 0,
    }

    data: dict[str, Any] = {
        "schema": "susy-v38-complete-theory-audit-v1",
        "status": "V38_EXHAUSTIVE_COMPLETION_AUDIT__ALL_COMPUTABLE_SUBPROBLEMS_REPLAYED__ZERO_OF_EIGHT_FULL_GATES_CLOSED",
        "complete_theory_exists": False,
        "established_full_predictive_closed_count": closed_count,
        "integrity_checks": integrity_checks,
        "gate_ledger": gates,
        "g7_additive_abelian_selector_no_go": g7_no_go,
        "new_physics_decisions": {
            "not_adopted_as_a_complete_theory": [
                "The ordinary 4D Higgsed-U(1)X repair is excluded by V38 under its explicit threshold assumptions.",
                "The 5D eta-inflow construction is a local anomaly-EFT scaffold, not a microscopic UV completion.",
                "The six-field D cascade preserves selector/quality arithmetic but only transfers the unavoidable Z170 charge into dark carriers.",
                "No soft spectrum, Wilson tensors, covariance, likelihood, or reheating history has been inserted as an arbitrary benchmark."
            ],
            "genuine_architecture_choices_remaining": [
                "Complete the 5D/topological route with a gapped mirror wall, global-form bordism, and UV-to-EFT matching.",
                "Redesign the driver/cubic/Majorana sector, or derive non-Abelian flavour/locality sequestering, to control driver-dressed baryon violation.",
                "Supply a microscopic mediation and cosmology sector that predicts a safe Z170-charged dark abundance, or break Z170 and re-audit quality."
            ],
        },
        "promotion_contract": {
            "G1": uv["required_for_a_genuine_G1_promotion"],
            "G2": [
                "A complete broken-phase component Lagrangian, numerical pole solution, self energies, mixings, and covariance matrix."
            ],
            "G3": [
                "Microscopic Kähler and gauge-kinetic functions, SUSY-breaking terms, all competing vacua, bounce actions, and cosmological vacuum selection."
            ],
            "G4": [
                "A mediation mechanism with soft boundary conditions, threshold-matched running, radiative EWSB, collider likelihood, and uncertainty propagation."
            ],
            "G5": [
                "One explicit mass/interaction point with a Boltzmann solution or a fully specified nonthermal reheating history, plus PQ restoration/isocurvature/domain-wall and late-decay likelihoods."
            ],
            "G6": [
                "Measured or UV-derived gauge/Yukawa/soft boundaries, individual pole thresholds, matching Wilson coefficients, and a covariance model."
            ],
            "G7": [
                "A derived baryon-protection mechanism, flavour Wilson tensors, heavy spectrum, SUSY dressing, operator running, and lattice matrix-element covariance."
            ],
            "G8": [
                "A predictive flavour origin and a versioned out-of-sample joint likelihood with experimentally defined inputs and theory covariance."
            ],
        },
        "literature_backed_architecture_forks_not_merged": [
            {
                "reference": "https://arxiv.org/abs/2412.21157",
                "route": "SO(10) x U(1)_a high-quality-axion construction",
                "reason_not_merged": "Its anomaly-free non-SUSY field content and scalar sector are a different theory; it does not provide the V37 soft/pole/flavour/relic completion."
            },
            {
                "reference": "https://arxiv.org/abs/2508.21813",
                "route": "Exact SUSY chiral-dynamics composite axion with an SO(10) extension",
                "reason_not_merged": "It is a distinct composite SU(14) architecture with extra assumed GUT breaking and its own cosmological matching problem."
            },
            {
                "reference": "https://arxiv.org/abs/2510.18306",
                "route": "Anomalous U(1)_X / Green--Schwarz high-quality-axion models",
                "reason_not_merged": "It motivates a quantized GS architecture, but does not furnish the full V37 Pati--Salam, R-symmetry, soft, and likelihood completion."
            },
        ],
        "primary_sources": [
            "https://arxiv.org/abs/1808.02881",
            "https://arxiv.org/abs/hep-ph/9210211",
            "https://arxiv.org/abs/1909.08775",
            "https://arxiv.org/abs/hep-th/0305024",
            "https://arxiv.org/abs/2211.02054",
            "https://ntrs.nasa.gov/citations/19900004848",
            "https://arxiv.org/abs/1807.06209",
            "https://arxiv.org/abs/2412.21157",
            "https://arxiv.org/abs/2508.21813",
            "https://arxiv.org/abs/2510.18306",
        ],
        "source_manifest": source_manifest(),
    }
    data["core_sha256"] = canonical_sha(data)
    return data


def markdown(data: Mapping[str, Any]) -> str:
    lines = [
        "# SUSY V38 exhaustive complete-theory audit",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Full predictive gates closed: **{data['established_full_predictive_closed_count']} / 8**.",
        "",
        "## What this resolves exactly",
        "",
        "- V38 proves that the ordinary 4D `U(1)_X -> Z66` heavy-threshold repair cannot work under its stated symmetry-preserving assumptions; it records an explicit anomaly-balanced 5D eta-inflow EFT instead.",
        "- The `P,Pbar` VEV leaves exact `Z170`; a lightest charged remnant is unavoidable. The six-field D cascade is selector/quality-safe but remains a dark-sector proposal until its abundance is calculated.",
        "- The full V37 driver/cubic/Majorana/PS-breaking superpotential implies a new no-go: no additional ordinary or R-type additive Abelian symmetry can forbid `X Q^4/M^2` and `X Qc^4/M^2` while preserving that architecture.",
        "",
        "## Gate ledger",
        "",
    ]
    for gate in data["gate_ledger"]:
        lines.extend(
            [
                f"### {gate['gate']} — open",
                "",
                f"Locked result: {gate['locked_result']}",
                "",
                f"Blocking evidence: {gate['blocker']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Honest next architecture choices",
            "",
            "- Finish a microscopic 5D/topological completion, including a gapped mirror wall, global-form bordism, and numerical UV-to-EFT matching.",
            "- Redesign the driver/cubic/Majorana sector or derive non-Abelian flavour/locality sequestering before making a proton-lifetime prediction.",
            "- Derive the mediation, spectrum, and reheating sector and solve the dark/Boltzmann history at a specified parameter point.",
            "",
            "The report intentionally does not turn any missing item into an invented benchmark. The V37/V38 program is now a stronger, reproducible research EFT with clear no-go theorems, not an established complete theory.",
            "",
            "## References used to choose the remaining forks",
            "",
            "- [Hsieh, discrete gauge anomalies](https://arxiv.org/abs/1808.02881)",
            "- [Witten--Yonekura, eta-inflow](https://arxiv.org/abs/1909.08775)",
            "- [Dutka--Gargalionis, Pati--Salam dimension-five baryon violation](https://arxiv.org/abs/2211.02054)",
            "- [Griest--Kamionkowski thermal-relic unitarity bound](https://ntrs.nasa.gov/citations/19900004848)",
            "- [Babu--Dutta--Mohapatra, anomaly-free SO(10) x U(1)_a high-quality axion](https://arxiv.org/abs/2412.21157)",
            "- [Gherghetta et al., exact SUSY chiral dynamics](https://arxiv.org/abs/2508.21813)",
            "",
            f"Core SHA-256: `{data['core_sha256']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    data = report()
    if args.write:
        REPORT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT_MD.write_text(markdown(data), encoding="utf-8")
    if args.check:
        if not REPORT_JSON.is_file() or not REPORT_MD.is_file():
            raise SystemExit("generated V38 report is missing; run with --write")
        on_disk = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        if on_disk != data:
            raise SystemExit("generated V38 JSON is stale; run with --write")
        if REPORT_MD.read_text(encoding="utf-8") != markdown(data):
            raise SystemExit("generated V38 Markdown is stale; run with --write")
        print("SUSY V38 complete-theory audit: PASS")
        return
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
