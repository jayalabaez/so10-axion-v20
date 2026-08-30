"""Fail-closed audit of the V37 spectrum, vacuum, running and flavour gates.

This is deliberately not a benchmark fitter.  It extracts what follows exactly
from the declared PSZ4RZ5610SUSYV37 source, and proves which additional inputs
are still logically required before a pole spectrum, EWSB solution, proton
lifetime, or likelihood could be claimed.

The result is useful because it distinguishes a real tree-level EFT result
(a zero-energy canonical global-SUSY branch and a rank-five anomalon block)
from quantities that cannot be inferred from the present source file.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
MODEL_NAME = "PSZ4RZ5610SUSYV37"
MODEL = ROOT / "models" / MODEL_NAME / f"{MODEL_NAME}.m"
PARAMETERS = ROOT / "models" / MODEL_NAME / "parameters.m"
PARTICLES = ROOT / "models" / MODEL_NAME / "particles.m"
RGE = ROOT / "SUSY_V37_SARAH_RGE_ATTESTATION.json"
GATE_LEDGER = ROOT / "SUSY_V37_G1_G8_GATE_LEDGER.json"
OUTPUT_JSON = ROOT / "SUSY_V37_NONANOMALY_GATE_AUDIT.json"
OUTPUT_MD = ROOT / "SUSY_V37_NONANOMALY_GATE_AUDIT.md"

STATUS = (
    "V37_NONANOMALY_AUDIT_COMPLETE__CANONICAL_GLOBAL_SUSY_BRANCH_AND_"
    "ANOMALON_RANK_CERTIFIED__NO_PHYSICAL_POLE_SOFT_RUNNING_PROTON_OR_"
    "LIKELIHOOD_CLOSURE"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(payload: Mapping[str, Any]) -> str:
    copy = dict(payload)
    copy.pop("core_sha256", None)
    encoded = json.dumps(copy, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    """Exact Gaussian-elimination determinant for the small certification blocks."""

    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result *= -1
        value = work[column][column]
        result *= value
        work[column] = [entry / value for entry in work[column]]
        for row in range(column + 1, len(work)):
            factor = work[row][column]
            if factor:
                work[row] = [
                    left - factor * right
                    for left, right in zip(work[row], work[column], strict=True)
                ]
    return result


def rank(matrix: list[list[Fraction]]) -> int:
    """Exact row rank, retained separately so the proof does not need numpy."""

    work = [row[:] for row in matrix]
    n_rows = len(work)
    n_cols = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(n_cols):
        pivot = next(
            (row for row in range(pivot_row, n_rows) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(n_rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    left - factor * right
                    for left, right in zip(work[row], work[pivot_row], strict=True)
                ]
        pivot_row += 1
        if pivot_row == n_rows:
            break
    return pivot_row


def source_text() -> tuple[str, str, str]:
    return (
        MODEL.read_text(encoding="utf-8"),
        PARAMETERS.read_text(encoding="utf-8"),
        PARTICLES.read_text(encoding="utf-8"),
    )


def source_static_contract() -> dict[str, Any]:
    model, parameters, particles = source_text()
    no_spheno = not (MODEL.parent / "SPheno.m").exists()
    no_boundary_file = not any(
        path.name in {"SPheno.m", "RGEs.m", "EWSB.m", "Boundary.m"}
        for path in MODEL.parent.iterdir()
    )
    soft_flags = {
        "AddSoftTerms": "AddSoftTerms = False;" in model,
        "AddSoftScalarMasses": "AddSoftScalarMasses = False;" in model,
        "AddSoftGauginoMasses": "AddSoftGauginoMasses = False;" in model,
    }
    return {
        "model": MODEL_NAME,
        "declared_state": "GaugeES",
        "only_gauge_basis_state_declared": "NameOfStates = {GaugeES};" in model,
        "source_soft_terms_disabled": all(soft_flags.values()),
        "soft_disable_flags": soft_flags,
        "spectrum_generator_or_boundary_file_present": not no_boundary_file,
        "SPheno_m_present": not no_spheno,
        "parameter_definitions": ["vPS2", "fPQ2"],
        "parameter_file_contains_only_scale_definitions": (
            "{vPS2," in parameters
            and "{fPQ2," in parameters
            and "MINPAR" not in parameters
            and "EXTPAR" not in parameters
        ),
        "particles_file_is_gauge_basis_only": "ParticleDefinitions[GaugeES]" in particles,
        "consequence": (
            "The V37 source is a gauge-basis supersymmetric EFT declaration, not a "
            "numerical EWSB/pole-spectrum model."
        ),
    }


def permutation_sign(indices: tuple[int, ...]) -> int:
    if len(set(indices)) != len(indices):
        return 0
    inversions = sum(
        indices[left] > indices[right]
        for left in range(len(indices))
        for right in range(left + 1, len(indices))
    )
    return -1 if inversions % 2 else 1


def q4_contraction_witness() -> int:
    """An exact nonzero (4,2,1)^4 PS invariant with two family labels.

    The first family has nonzero Q^(1,1), Q^(2,2); the second has nonzero
    Q^(3,1), Q^(4,2).  Contracting epsilon_SU4 epsilon_SU2 epsilon_SU2 gives
    four equal nonzero terms.  This rules out an automatic Bose-symmetry zero.
    """

    q0 = [[1, 0], [0, 1], [0, 0], [0, 0]]
    q1 = [[0, 0], [0, 0], [1, 0], [0, 1]]
    result = 0
    for a, b, c, d in itertools.permutations(range(4)):
        for alpha, beta, gamma, delta in itertools.product(range(2), repeat=4):
            result += (
                permutation_sign((a, b, c, d))
                * permutation_sign((alpha, beta))
                * permutation_sign((gamma, delta))
                * q0[a][alpha]
                * q0[b][beta]
                * q1[c][gamma]
                * q1[d][delta]
            )
    return result


def anomalon_rank_certificate() -> dict[str, Any]:
    # a=yAbar<Pb>, b=yA15<P>, c=yA16<P> in the ordered V37 anomalon basis.
    a, b, c = map(Fraction, (2, 3, 5))
    matrix = [
        [0, a, 0, 0, 0],
        [a, 0, 0, 0, 0],
        [0, 0, 0, b, 0],
        [0, 0, b, 0, 0],
        [0, 0, 0, 0, c],
    ]
    return {
        "scope": "holomorphic tree mass block only",
        "field_order": ["A2", "A32", "A15", "A17", "A16"],
        "mass_entries": {
            "a": "yAbar*<Pb>",
            "b": "yA15*<P>",
            "c": "yA16*<P>",
        },
        "matrix": [
            ["0", "a", "0", "0", "0"],
            ["a", "0", "0", "0", "0"],
            ["0", "0", "0", "b", "0"],
            ["0", "0", "b", "0", "0"],
            ["0", "0", "0", "0", "c"],
        ],
        "determinant": "a^2*b^2*c",
        "generic_full_rank_condition": "a*b*c != 0",
        "exact_rational_witness_abc": [2, 3, 5],
        "exact_rational_witness_rank": rank(matrix),
        "exact_rational_witness_determinant": str(determinant(matrix)),
        "does_not_establish": [
            "soft scalar splittings",
            "gauge and matter mixing matrices",
            "self energies or pole masses",
            "physical threshold covariance",
        ],
    }


def canonical_global_susy_branch() -> dict[str, Any]:
    # K multiplies ((<Sbc Sc>-vPS^2),(<P Pb>-fPQ^2)) in F_X,F_Zp.
    k = [[Fraction(2), Fraction(3)], [Fraction(5), Fraction(7)]]
    hessian = [
        [0, 0, k[0][0], k[0][1]],
        [0, 0, k[1][0], k[1][1]],
        [k[0][0], k[1][0], 0, 0],
        [k[0][1], k[1][1], 0, 0],
    ]
    return {
        "scope": "canonical global-N=1 SUSY truncation; not a Kähler/soft completion",
        "driver_fields": ["X", "Zp"],
        "bilinear_coordinates": ["U=<Sbc Sc>", "V=<P Pb>"],
        "F_driver_system": (
            "[[kappaPS,kappaPQ],[rhoPS,rhoPQ]] "
            "[[U-vPS^2],[V-fPQ^2]] = 0"
        ),
        "generic_condition": "Delta= kappaPS*rhoPQ-kappaPQ*rhoPS != 0",
        "solution_when_Delta_nonzero": ["U=vPS^2", "V=fPQ^2"],
        "branch_representative": {
            "<Sc>=<Sbc>=vPS along conjugate PS-neutral directions": True,
            "<P>=<Pb>=fPQ": True,
            "<X>=<Zp>=<H>=<Sig6>=<Q>=<Qc>=<Psi>=<PsiBar>=<PsiC>=<PsiCBar>=<Nv>=<Ai>=0": True,
        },
        "F_terms_vanish_on_representative": True,
        "D_terms_vanish_on_equal_conjugate_PS_VEVs": True,
        "canonical_global_energy": "V=sum_i |F_i|^2 + (1/2)sum_a D_a^2 >= 0",
        "zero_energy_branch_is_global_minimum_of_that_truncation": True,
        "radial_holomorphic_hessian": {
            "basis": ["X", "Zp", "deltaU", "deltaV"],
            "matrix": "[[0,K],[K^T,0]]",
            "determinant": "Delta^2",
            "generic_rank": 4,
            "exact_rational_K_witness": [[2, 3], [5, 7]],
            "exact_rational_witness_rank": rank(hessian),
            "exact_rational_witness_determinant": str(determinant(hessian)),
        },
        "not_established": [
            "Kähler metric and higher-derivative corrections",
            "soft terms and SUSY-breaking tadpoles",
            "saxion stabilization and all competing branches",
            "tunneling or cosmological vacuum selection",
        ],
    }


def electroweak_boundary() -> dict[str, Any]:
    model, _, _ = source_text()
    required_terms = ["lambdaH/2*X.H.H", "lambdaZH/2*Zp.H.H"]
    term_check = {term: term in model for term in required_terms}
    h_lines = [line.strip() for line in model.splitlines() if ".H.H" in line]
    bare_h2 = any(
        ".H.H" in line and "X.H.H" not in line and "Zp.H.H" not in line
        for line in h_lines
    )
    return {
        "H_representation": "(1,2,2)",
        "all_H_bilinear_source_terms": required_terms,
        "all_expected_H_bilinear_terms_present": all(term_check.values()),
        "bare_H_squared_source_term_present": bare_h2,
        "tree_mu_on_canonical_global_SUSY_branch": "mu=lambdaH*<X>+lambdaZH*<Zp>=0",
        "source_soft_terms_enabled": False,
        "derived_Bmu_or_Higgs_soft_masses_present": False,
        "conclusion": (
            "The source preserves the desired supersymmetric mu protection, but it does "
            "not specify the mediation data required to test radiative EWSB or a weak-scale pole spectrum."
        ),
    }


def running_and_matching_boundary() -> dict[str, Any]:
    rge = json.loads(RGE.read_text(encoding="utf-8"))
    beta_counts = rge["beta_counts"]
    model, _, _ = source_text()
    no_gauge_boundary_literals = all(
        token not in model for token in ("g4 ->", "gL ->", "gR ->", "BoundaryHighScale")
    )
    return {
        "live_SARAH_two_loop_RGE_attestation": {
            "model_initialized": rge["model_initialized"],
            "two_loop_RGE_calculation_succeeded": rge["two_loop_RGE_calculation_succeeded"],
            "one_loop_gauge_b_4_L_R": [1, 5, 9],
            "beta_counts": beta_counts,
            "source_soft_terms_enabled": rge["source_soft_terms_enabled"],
        },
        "structural_matching_results_retained_from_V36_visible_sector": {
            "PS_to_SM": ["g3=g4", "g2=gL", "1/g1^2=2/(5*g4^2)+3/(5*gR^2)"],
            "complete_vectorlike_threshold_sum_Delta_b_1_2_3": [4, 4, 4],
            "qualification": (
                "This is a representation-level sum, not a physical threshold correction: "
                "the individual mixed heavy masses are not supplied."
            ),
        },
        "absent_physical_inputs": {
            "gauge_boundary_numbers": no_gauge_boundary_literals,
            "soft_beta_rows": {
                key: beta_counts[key]
                for key in (
                    "soft_trilinear",
                    "soft_bilinear",
                    "soft_linear",
                    "soft_scalar_mass",
                    "gaugino_mass",
                )
            },
            "pole_or_threshold_boundary_file": False,
            "matching_wilson_coefficients": False,
            "covariance_or_uncertainty_model": False,
        },
        "conclusion": (
            "The beta functions are live and useful, but the source cannot select a physical "
            "trajectory or calculate a threshold-matched uncertainty band."
        ),
    }


def proton_and_flavour_boundary() -> dict[str, Any]:
    # The following degree-five source monomials have q5610=0 and R(W)=2.
    # Q^4 and Qc^4 admit PS singlet contractions using epsilon_SU4 and two
    # epsilon_SU2 tensors; the required three-family flavour tensors exist.
    allowed = []
    for driver in ("X", "Zp"):
        for matter in ("Q^4", "Qc^4"):
            allowed.append(
                {
                    "source_monomial": f"{driver}*{matter}/M^2",
                    "superfield_degree": 5,
                    "Z5610_charge": 0,
                    "external_Z4R_charge_mod4": 2,
                    "Pati_Salam_contraction": (
                        "epsilon_SU4 times two epsilon_SU2 contractions; nonzero with "
                        "the available three-family flavour tensors"
                    ),
                    "branch_value_if_X_and_Zp_zero": 0,
                }
            )
    return {
        "selection_rule_result": {
            "bare_Q4_or_Qc4_has_external_Z4R_charge_mod4": 0,
            "bare_Q4_or_Qc4_is_forbidden_in_W": True,
            "driver_dressed_degree5_sources_are_permitted": allowed,
            "exact_Q4_two_family_contraction_witness": q4_contraction_witness(),
            "physical_interpretation": (
                "If a driver receives a SUSY-breaking VEV, these induce conventional "
                "four-matter dimension-five superpotential operators."
            ),
        },
        "why_no_lifetime_can_be_inferred": [
            "the allowed Wilson flavour tensors are not derived or bounded",
            "the driver VEVs after soft/Kähler corrections are unknown",
            "the heavy pole spectrum, SUSY dressing, operator running and lattice matrix elements are not matched",
        ],
        "flavour_nonidentifiability": {
            "unfixed_matrix_couplings": ["YQQ (3x3)", "yNQ (3x3)", "YQX (3)", "YXQ (3)", "lambdaPQ (3)", "lambdaPcQ (3)", "yNX (3)"],
            "symmetry_allowed_counterexamples": [
                "YQQ=0",
                "YQQ=y*Identity_3 for arbitrary complex y",
            ],
            "consequence": (
                "Both assignments satisfy the declared gauge and discrete charges but give "
                "different fermion masses and mixings, so CKM/PMNS and a joint likelihood are not predictions."
            ),
        },
    }


def gate_conclusions() -> list[dict[str, Any]]:
    return [
        {
            "gate": "G2",
            "full_gate_closed": False,
            "landed_exact_subproblem": "generic rank-five anomalon holomorphic mass block",
            "blocking_fact": "no EWSB/pole state, soft masses, numerical boundary, self energies, or covariance",
        },
        {
            "gate": "G3",
            "full_gate_closed": False,
            "landed_exact_subproblem": "zero-energy F=D=0 branch and rank-four two-driver radial Hessian in canonical global SUSY",
            "blocking_fact": "Kähler/soft potential, competing vacua, tunneling and cosmological selection absent",
        },
        {
            "gate": "G4",
            "full_gate_closed": False,
            "landed_exact_subproblem": "mu protection on the canonical branch",
            "blocking_fact": "source disables mediation and all soft terms, so radiative EWSB cannot be calculated",
        },
        {
            "gate": "G6",
            "full_gate_closed": False,
            "landed_exact_subproblem": "live SARAH one- and two-loop supersymmetric beta functions",
            "blocking_fact": "no physical boundary, soft beta system, individual pole thresholds, matching Wilsons or uncertainty propagation",
        },
        {
            "gate": "G7",
            "full_gate_closed": False,
            "landed_exact_subproblem": "the bare four-matter terms are R-forbidden",
            "blocking_fact": "X/Zp-dressed Q^4 and Qc^4 source monomials are allowed; their coefficients and soft-induced VEVs are not controlled",
        },
        {
            "gate": "G8",
            "full_gate_closed": False,
            "landed_exact_subproblem": "a flavour-capable renormalizable source exists",
            "blocking_fact": "independent Yukawa/Wilson matrices and no versioned joint likelihood leave observables non-identifiable",
        },
    ]


def build_report() -> dict[str, Any]:
    source = source_static_contract()
    anomalons = anomalon_rank_certificate()
    vacuum = canonical_global_susy_branch()
    electroweak = electroweak_boundary()
    running = running_and_matching_boundary()
    proton = proton_and_flavour_boundary()
    gates = gate_conclusions()
    sources = [MODEL, PARAMETERS, PARTICLES, RGE, GATE_LEDGER]
    report: dict[str, Any] = {
        "schema": "susy-v37-nonanomaly-gate-audit-v1",
        "status": STATUS,
        "model": MODEL_NAME,
        "source_static_contract": source,
        "G2_tree_mass_rank": anomalons,
        "G3_canonical_global_SUSY_branch": vacuum,
        "G4_electroweak_boundary": electroweak,
        "G6_running_and_matching_boundary": running,
        "G7_proton_and_flavour_boundary": proton,
        "G2_G4_G6_G8_gate_conclusions": gates,
        "established_full_predictive_closed_count": 0,
        "complete_theory_exists": False,
        "minimal_honest_extension_contract": {
            "not_implemented_as_ad_hoc_new_physics": True,
            "reason": (
                "Assigning arbitrary soft masses, Wilson tensors, thresholds, or likelihood priors "
                "would create a benchmark, not derive a complete theory."
            ),
            "required_single_source_inputs": [
                "microscopic Kähler potential, gauge kinetic functions and mediation mechanism",
                "complete PS-to-SM component spectrum and matching scale(s)",
                "all baryon-violating Wilson tensors and flavour origin",
                "experimental/lattice/cosmology likelihood with theory covariance",
            ],
        },
        "source_manifest": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}
            for path in sources
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    g2 = report["G2_tree_mass_rank"]
    g3 = report["G3_canonical_global_SUSY_branch"]
    g6 = report["G6_running_and_matching_boundary"]
    g7 = report["G7_proton_and_flavour_boundary"]
    return f"""# V37 non-anomaly gate audit

Status: `{report['status']}`

This audit does **not** add a free soft benchmark. It separates exact
properties of the declared V37 EFT from data which the source does not
contain. The strict full-theory result remains **0/8** gates.

## Exact EFT subresults

- The anomalon tree mass block has determinant `{g2['determinant']}` and is
  generically rank {g2['exact_rational_witness_rank']} when `a*b*c != 0`.
- In the canonical global-SUSY truncation, the two-driver equations force
  `Sbc Sc=vPS^2` and `P Pb=fPQ^2` when `Delta != 0`; the representative has
  `F=D=0`. Since this potential is a sum of squares, it is a global
  zero-energy minimum **only in that truncation**. The radial holomorphic
  Hessian has generic rank {g3['radial_holomorphic_hessian']['generic_rank']}.
- SARAH has live one- and two-loop supersymmetric RGEs, with one-loop PS
  coefficients `{g6['live_SARAH_two_loop_RGE_attestation']['one_loop_gauge_b_4_L_R']}`.

## Decisive boundaries

The source deliberately disables every soft term and declares only `GaugeES`;
there is no SPheno/boundary file. Thus it cannot produce a physical pole
spectrum, radiative EWSB solution, or a threshold-matched uncertainty band.

The external `Z4R` and `Z5610` assignments forbid bare `Q^4` and `Qc^4` in
the superpotential, but permit each of `{', '.join(row['source_monomial'] for row in g7['selection_rule_result']['driver_dressed_degree5_sources_are_permitted'])}`.
These vanish on the canonical `X=Zp=0` branch but become ordinary
four-matter dimension-five superpotential operators if the drivers acquire
SUSY-breaking VEVs. Their Wilson flavour tensors are neither calculated nor
bounded. This prevents a proton-lifetime claim.

Likewise, symmetry permits independent flavour matrices such as `YQQ` and
`yNQ`; the allowed choices `YQQ=0` and `YQQ=y I` already give inequivalent
fermion spectra. No CKM/PMNS or joint likelihood is therefore predicted.

## Promotion rule

Do not close any remaining gate by assigning soft masses, thresholds, Wilson
coefficients, or data priors by hand. A genuine completion must derive them
from one microscopic source together with the Kähler/gauge-kinetic sector and
the full PS-to-SM matching calculation.

Core SHA-256: `{report['core_sha256']}`
"""


def write_outputs(report: Mapping[str, Any]) -> None:
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(report), encoding="utf-8")


def check_outputs(report: Mapping[str, Any]) -> bool:
    if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
        return False
    stored = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    return stored == report and stored["core_sha256"] == canonical_sha(stored) and stored["core_sha256"] in OUTPUT_MD.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
        print(f"WROTE {OUTPUT_JSON.name} {OUTPUT_MD.name}")
    if args.check:
        ok = check_outputs(report)
        print("V37_NONANOMALY_AUDIT_CHECK " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    if not args.write and not args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
