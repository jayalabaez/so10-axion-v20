#!/usr/bin/env python3
"""Fail-closed V40 completion contract for the non-UV G1--G8 gates.

V39 established several useful *negative* results.  In particular, its
gauge-only 5D boundary leaves every exact singlet unlifted, while its isolated
``lambda_D`` secluded-freeze-out illustration reaches a Landau pole below the
PQ scale.  Neither defect can be repaired by choosing another point in the
same input table.

This module does not manufacture a spectrum.  It records the smallest
microscopic-data contract a successor theory must satisfy in order for G2--G6
and G8 to be promotable.  It also gives a quantitative, deliberately
conditional alternative to the V39 pure-Yukawa dark mechanism: a Higgsed
vectorlike U(1)_D portal.  The vector portal is a perturbativity feasibility
witness only; its charges, vacuum, portal matching, and cosmology must still
be derived by a V40 source and checked alongside the UV/G1 construction.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V40_NONUV_COMPLETION_CONTRACT.json"
MD_PATH = ROOT / "SUSY_V40_NONUV_COMPLETION_CONTRACT.md"
V39_AUDIT_PATH = ROOT / "SUSY_V39_COMPLETE_THEORY_AUDIT.json"

STATUS = (
    "V40_NONUV_COMPLETION_CONTRACT_DEFINED__V39_PURE_YUKAWA_G5_SCALE_NO_GO_"
    "QUANTIFIED__VECTOR_PORTAL_FEASIBILITY_ONLY__ZERO_GATES_PROMOTED"
)

# The numerical values below are deliberately copied from the *failed* V39
# secluded-freeze-out screen wherever possible.  They are not V40 inputs.
FPQ_GEV = 5.0e11
MCHI_GEV = 2.0e3
OMEGA_V39 = 0.1188
LAMBDA_D_V39 = 1.563065
LAMBDA_BETA_COEFFICIENT = 3.0
SIGMA_V39_TARGET_CM3_S = 4.128e-26
GEV2_TO_CM3_S = 1.167e-17
MPL_REDUCED_GEV = 2.4e18
MPL_GEV = 1.22089e19

# A *conditional* minimal vector-portal feasibility point.  A vectorlike
# Dirac carrier and a unit-charge complex dark Higgs give b_D = 4/3 + 1/3.
# If V40 retains the V39 cascade, the portal scalar is required to be neutral
# under its exact Z170.  A genuine selector rebuild may instead have a new
# stabilizing remnant; that remnant must be stated and audited afresh.
MVD_GEV = 5.0e2
BD_MINIMAL_U1D = 5.0 / 3.0
EPSILON_KINETIC = 1.0e-5
ALPHA_EM = 1.0 / 137.035999084
GSTAR = 106.75
HBAR_GEV_S = 6.582119569e-25

V39_GAUGE_ONLY_UNLIFTED_SINGLET_SET = (
    "X",
    "P",
    "Nv",
    "Pbar",
    "Zp",
    "A2",
    "A32",
    "A15",
    "A17",
    "A16",
    "D2",
    "Db2",
    "D17",
    "Db17",
    "D16",
    "Db16",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def v39_context() -> dict[str, Any]:
    """Read, but do not rely on, the prior fail-closed classification."""

    if not V39_AUDIT_PATH.is_file():
        return {"available": False, "reason": "V39 master audit is missing"}
    payload = json.loads(V39_AUDIT_PATH.read_text(encoding="utf-8"))
    gate_states = {
        row["gate"]: {"closed": row["closed"], "blocker": row["blocker"]}
        for row in payload.get("gate_ledger", [])
    }
    return {
        "available": True,
        "audit_core_sha256": payload.get("core_sha256"),
        "complete_theory_exists": payload.get("complete_theory_exists"),
        "closed_gate_count": payload.get("established_full_predictive_closed_count"),
        "selected_gate_states": {key: gate_states.get(key) for key in ("G2", "G3", "G4", "G5", "G6", "G8")},
    }


def pure_yukawa_scale_no_go() -> dict[str, Any]:
    """Integrate the V39 one-loop lambda_D beta function exactly.

    This is a no-go only for the stated isolated mechanism: beta_lambda =
    3 lambda^3/(16 pi^2) and the V39 proxy annihilation scaling sigma v
    proportional to lambda^4.  New thresholds or new interactions are outside
    that theorem and are precisely why V40 needs a new source-level sector.
    """

    log_interval = math.log(FPQ_GEV / MCHI_GEV)
    lambda_max = math.sqrt(8.0 * math.pi**2 / (LAMBDA_BETA_COEFFICIENT * log_interval))
    log_pole_over_mchi = 8.0 * math.pi**2 / (LAMBDA_BETA_COEFFICIENT * LAMBDA_D_V39**2)
    lambda_pole_gev = MCHI_GEV * math.exp(log_pole_over_mchi)
    allowed_cross_section_fraction = (lambda_max / LAMBDA_D_V39) ** 4
    minimal_proxy_omega = OMEGA_V39 / allowed_cross_section_fraction
    return {
        "assumptions": {
            "beta_function": "d lambda_D/d ln(mu) = 3 lambda_D^3/(16 pi^2)",
            "annihilation_scaling": "<sigma v> proportional to lambda_D^4 at fixed component spectrum",
            "thresholds_or_new_gauge_dynamics_below_fPQ": False,
            "renormalization_start_scale_GeV": MCHI_GEV,
            "required_PQ_scale_GeV": FPQ_GEV,
        },
        "integrated_solution": "1/lambda_D(mu)^2 = 1/lambda_D(mu0)^2 - 3 ln(mu/mu0)/(8 pi^2)",
        "V39_fitted_lambda_D": LAMBDA_D_V39,
        "V39_lambda_pole_GeV": lambda_pole_gev,
        "V39_pole_below_fPQ": lambda_pole_gev < FPQ_GEV,
        "lambda_D_max_without_a_pole_below_fPQ": lambda_max,
        "fitted_lambda_exceeds_PQ_safe_bound": LAMBDA_D_V39 > lambda_max,
        "maximum_proxy_annihilation_fraction_if_PQ_safe": allowed_cross_section_fraction,
        "minimum_proxy_Omega_h2_if_PQ_safe": minimal_proxy_omega,
        "V39_target_Omega_h2": OMEGA_V39,
        "conditional_conclusion": (
            "Within the isolated V39 pure-Yukawa beta function and fixed-spectrum annihilation proxy, "
            "a thermal relic matching the fitted target cannot remain perturbative to fPQ.  This does not "
            "exclude a new threshold, coannihilation, resonance, nonthermal history, or a new gauge force."
        ),
    }


def vector_portal_feasibility() -> dict[str, Any]:
    """A perturbativity screen for a possible V40 dark gauge sector.

    The tree-level Dirac result used here is the standard massive-vector
    approximation.  It is intentionally *not* a relic calculation: the
    component spectrum, Sommerfeld effects, portal thermalization, dark-Higgs
    decays, and nuclear matching are V40 deliverables.
    """

    r = (MVD_GEV / MCHI_GEV) ** 2
    phase = (1.0 - r) ** 1.5 / (1.0 - r / 2.0) ** 2
    target_gev_minus2 = SIGMA_V39_TARGET_CM3_S / GEV2_TO_CM3_S
    alpha_d = math.sqrt(target_gev_minus2 * MCHI_GEV**2 / (math.pi * phase))
    g_d = math.sqrt(4.0 * math.pi * alpha_d)
    log_to_planck = math.log(MPL_REDUCED_GEV / MCHI_GEV)
    g_max_to_planck = math.sqrt(8.0 * math.pi**2 / (BD_MINIMAL_U1D * log_to_planck))
    log_pole_over_mchi = 8.0 * math.pi**2 / (BD_MINIMAL_U1D * g_d**2)
    u1d_pole_gev = MCHI_GEV * math.exp(log_pole_over_mchi)

    # A conservative single e+e- partial-width lower proxy; all open charged
    # SM species increase it.  It only demonstrates that a decay window can
    # exist, not that the UV theory gives this epsilon or permits the portal.
    gamma_ee_proxy = ALPHA_EM * EPSILON_KINETIC**2 * MVD_GEV / 3.0
    lifetime_ee_proxy_s = HBAR_GEV_S / gamma_ee_proxy
    mu_nucleon_gev = 0.939
    sigma_si_proxy_cm2 = (
        16.0
        * math.pi
        * alpha_d
        * ALPHA_EM
        * EPSILON_KINETIC**2
        * mu_nucleon_gev**2
        / MVD_GEV**4
        * 0.389379e-27
    )
    gamma_over_h_proxy_at_mchi = (
        EPSILON_KINETIC**2
        * ALPHA_EM
        * alpha_d
        * MPL_GEV
        / (1.66 * math.sqrt(GSTAR) * MCHI_GEV)
    )
    return {
        "candidate_structure_not_yet_a_V40_model": {
            "gauge_factor": "U(1)_D",
            "minimal_light_content_for_beta_screen": "one vectorlike unit-charge Dirac carrier plus one unit-charge complex dark Higgs",
            "visible_remnant_requirement": (
                "Every U(1)_D-Higgs/portal VEV is neutral under the exact stabilizing remnant "
                "(Z170 if the V39 cascade is retained)."
            ),
            "new_G1_obligations": [
                "all U(1)_D, mixed, gravitational, discrete, and global anomalies cancel in the full microscopic spectrum",
                "kinetic mixing and any Stueckelberg/Green--Schwarz terms have quantized UV matching",
                "the added fields preserve the V40 selector, PQ-quality theorem, and baryon-operator protection",
            ],
        },
        "tree_level_screen": {
            "annihilation_formula": "sigma v(chi chibar -> V_D V_D) = pi alpha_D^2/m_chi^2 * (1-r)^(3/2)/(1-r/2)^2, r=m_VD^2/m_chi^2",
            "gauge_beta": "d g_D/d ln(mu) = b_D g_D^3/(16 pi^2)",
            "gauge_running_solution": "1/g_D(mu)^2 = 1/g_D(mu0)^2 - b_D ln(mu/mu0)/(8 pi^2)",
            "m_chi_GeV": MCHI_GEV,
            "m_VD_GeV": MVD_GEV,
            "r": r,
            "phase_space_factor": phase,
            "target_sigma_v_cm3_s": SIGMA_V39_TARGET_CM3_S,
            "target_sigma_v_GeV_minus2": target_gev_minus2,
            "alpha_D_needed_in_tree_proxy": alpha_d,
            "g_D_needed_in_tree_proxy": g_d,
            "minimal_b_D": BD_MINIMAL_U1D,
            "g_D_max_for_perturbativity_to_reduced_Planck": g_max_to_planck,
            "one_loop_U1D_pole_GeV": u1d_pole_gev,
            "one_loop_pole_above_reduced_Planck": u1d_pole_gev > MPL_REDUCED_GEV,
            "g_D_below_Planck_safe_bound": g_d < g_max_to_planck,
        },
        "portal_window_proxies": {
            "kinetic_mixing_epsilon": EPSILON_KINETIC,
            "Gamma_VD_to_ee_proxy_GeV": gamma_ee_proxy,
            "tau_VD_to_ee_proxy_seconds": lifetime_ee_proxy_s,
            "tau_proxy_below_0p1_seconds": lifetime_ee_proxy_s < 0.1,
            "sigma_chi_nucleon_SI_proxy_cm2": sigma_si_proxy_cm2,
            "Gamma_over_H_proxy_at_T_equals_mchi": gamma_over_h_proxy_at_mchi,
            "qualification": (
                "These are tree/proxy quantities only.  A full acceptance test requires all open V_D and dark-Higgs "
                "widths, component amplitudes, thermal masses, Boltzmann equations, current direct/indirect/collider "
                "likelihoods, and nucleon matching."
            ),
        },
        "feasibility_conclusion": (
            "Unlike the isolated lambda_D point, the displayed minimal-U(1)_D running has wide one-loop scale headroom. "
            "It is therefore a coherent route worth constructing, not a derived solution or a promoted G5 gate."
        ),
    }


def hidden_mediation_contract() -> dict[str, Any]:
    return {
        "V39_obstruction": {
            "gauge_only_boundary_left_unlifted": list(V39_GAUGE_ONLY_UNLIFTED_SINGLET_SET),
            "number_of_unlifted_exact_singlets": len(V39_GAUGE_ONLY_UNLIFTED_SINGLET_SET),
            "consequence": "Gauge-only gaugino mediation cannot select the driver/PQ/anomalon/dark vacuum or its component poles.",
        },
        "minimal_microscopic_input_set": [
            "complete hidden gauge group, all chiral/vector multiplets, representations, and V40 selector/PQ/R charges",
            "a cutoff-complete W_hidden and visible-hidden messenger superpotential, including every allowed relevant and marginal term",
            "K(visible, hidden) and the visible wavefunction matrix Z_i{}^j through the order that generates every soft term",
            "holomorphic gauge-kinetic matrix f_AB, including U(1) kinetic mixing and any moduli dependence",
            "a specified supergravity or global-SUSY decoupling limit, Planck-suppressed operators, and the cosmological constant prescription",
            "a solved hidden stationary point with F^m, D^A, messenger eigenmasses, phases, and no messenger tachyon",
            "matching scale(s), regulator/scheme, and a covariance/prior for microscopic couplings rather than fitted weak-scale soft terms",
        ],
        "required_matching_equations": [
            "V_F = exp(K/M_Pl^2) [K^{A Bbar} D_A W D_Bbar Wbar - 3 |W|^2/M_Pl^2]",
            "V_D = (Re f)^(-1)_ab D^a D^b / 2",
            "M_a = (Re f_a)^(-1) F^m partial_m f_a / 2",
            "m_i^2 = m_3/2^2 + V_0 - F^m F^nbar partial_m partial_nbar ln Z_i  (in a diagonal visible metric basis)",
            "A_ijk = F^m partial_m ln[exp(K/M_Pl^2) Y_ijk/(Z_i Z_j Z_k)]  (with conventions declared)",
            "mu and Bmu must follow from the displayed W/K operators and the same F/D solution; neither may be inserted as an IR boundary number",
        ],
        "acceptance_conditions": [
            "all 16 formerly unlifted singlet scalar/fermion directions receive a calculated component mass matrix; any protected massless mode is identified and phenomenologically acceptable",
            "all messenger and hidden-sector scalar mass-squared eigenvalues are nonnegative at the selected vacuum",
            "the hidden-to-visible matching computes m^2, A, B, tadpoles, gaugino masses, mu/Bmu, and CP phases in one convention",
            "the source proves that each visible-hidden operator is permitted and that omitted allowed operators are absent by a microscopic symmetry, not by declaration",
            "flavour alignment or a derived flavour symmetry controls off-diagonal soft matrices before flavour data are used",
        ],
        "fail_closed_rule": "A list of soft masses, a universal boundary ansatz, or a spurion without W_hidden/K/f and a solved hidden vacuum leaves G3, G4, and G6 open.",
    }


def vacuum_and_pole_contract() -> dict[str, Any]:
    return {
        "potential_to_be_evaluated": [
            "V_eff(phi,T=0) = V_F + V_D + V_soft + V_CW + counterterms in a declared gauge and tadpole scheme",
            "V_eff(phi,T) = V_eff(phi,0) + Delta V_T + daisy/resummation prescription for the actual particle content",
        ],
        "G3_vacuum_acceptance": [
            "solve partial V_eff/partial phi_i = 0 for every independent real component, including hidden, PQ, driver, dark-Higgs, and visible fields",
            "identify the unbroken gauge group and every exact discrete remnant at the solution; remove gauge Goldstones only after a rank/Ward check",
            "compute the physical Hessian on the quotient; no tachyonic physical direction is allowed",
            "enumerate all stationary branches in the specified EFT domain and compare renormalized vacuum energies, or demonstrate metastability with a calculated tunnelling rate",
            "evaluate zero-temperature O(4) and finite-temperature O(3) bounce actions with the full multifield potential and integrate the decay/nucleation probability through the derived cosmological history",
            "show that the selected branch yields the required Pati--Salam, electroweak, PQ, dark, and discrete breaking pattern without an excluded defect history",
        ],
        "G2_pole_acceptance": [
            "derive all component mass matrices from the selected vacuum, including scalar CP blocks, fermion Majorana/Dirac blocks, vectors, ghosts, Goldstones, and all mixings",
            "solve det[p^2 1 - M_tree^2 - Pi(p^2;mu)] = 0 for scalar/vector pole masses and det[p slash - M_tree - Sigma(p slash;mu)] = 0 for fermions in the declared scheme",
            "treat unstable poles with a complex-pole or explicitly stated narrow-width prescription",
            "verify gauge-parameter and renormalization-scale stability to the stated perturbative order, with tadpole and threshold counterterms included",
            "publish the full parameter covariance and propagate it to all masses, mixings, decay widths, and threshold scales",
        ],
        "G4_EWSB_acceptance": [
            "derive mu/Bmu and run them to the weak scale before solving the electroweak tadpole equations",
            "compute the loop-corrected Higgs pole and electroweak precision/collider likelihood using the same pole spectrum",
            "include charge/color-breaking directions and vacuum lifetime in the likelihood rather than treating a tree-level stationary point as EWSB closure",
        ],
        "no_shortcut": "Tree-level positive diagonal entries, a local F/D flat branch, or a hand-entered pole table cannot satisfy these requirements.",
    }


def rge_and_threshold_contract() -> dict[str, Any]:
    return {
        "V39_advance_to_preserve": "A declared V39 source and a transient formal-soft mirror had live two-loop SARAH beta systems; their PS-only one-loop coefficients were (2,5,9).",
        "V40_rederivation_rule": "Any new gauge factor, portal, hidden messenger, or selector change invalidates inheritance of those beta functions; regenerate and archive the V40 RGE system from the active source.",
        "required_equations": [
            "d theta_A/d ln(mu) = beta_A(theta, mu) for the coupled gauge, kinetic-mixing, superpotential, soft, and effective-operator parameter vector theta",
            "theta_below(M_k) = Match_k[theta_above(M_k), physical pole data, Wilson coefficients] at every PS, PQ, messenger, dark, and superpartner threshold",
            "Cov(output) = J Cov(microscopic inputs) J^T + Cov(thresholds) + Cov(truncation), with J obtained from the complete piecewise evolution",
        ],
        "G6_acceptance": [
            "live one/two-loop beta expressions and source hashes for the exact V40 field content",
            "derived, not guessed, ultraviolet soft/portal/flavour boundary data from the hidden and UV sectors",
            "physical pole thresholds and Wilson matching at every threshold, including Abelian kinetic mixing when present",
            "numerically stable piecewise integration with scale/scheme variation and covariance propagation",
        ],
        "fail_closed_rule": "A beta-function dump plus a boundary ansatz is a calculational scaffold, not G6 closure.",
    }


def dark_pq_cosmology_contract() -> dict[str, Any]:
    return {
        "irreducible_fact": (
            "If V40 retains the V39 residual Z170, its lightest nontrivially charged state is stable in every "
            "symmetry-preserving completion.  A selector rebuild must instead state its new exact stabilizer and "
            "solve every resulting stable-relic abundance; it cannot delete a remnant carrier by declaration."
        ),
        "component_level_requirements": [
            "derive the D/Dbar, X/driver, PQ, saxion, axino, dark-vector, dark-Higgs, and portal mass/mixing matrices from the accepted vacuum",
            "calculate every annihilation, coannihilation, decay, inverse-decay, and scattering amplitude with spin/statistics/thermal masses, rather than using a one-channel proxy",
            "solve the coupled Boltzmann system dY_i/dx = C_i[Y_j,T]/(H x) for all stable and long-lived components, with derived initial conditions and entropy injection",
            "match direct detection to nucleons and evaluate mass-dependent direct/indirect/collider/BBN/CMB likelihoods with the same spectrum",
            "derive reheaton/inflaton couplings, T_reh, T_max, branching fractions, preheating, and nonthermal dark production from a specified cosmological sector",
        ],
        "PQ_acceptance": [
            "recompute the full all-harmonic gravitational/PQ-breaking operator ring, including Kähler and supergravity dressings, after every V40 addition",
            "calculate the finite-temperature PQ potential and decide restoration/non-restoration from it, rather than inferring it from T_max/f_a alone",
            "compute axion, saxion, and axino abundances jointly using the QCD susceptibility, anharmonicity, entropy production, and all decays",
            "compute isocurvature from the same inflationary history and axion fraction; impose the defect/domain-wall history appropriate to the derived N_DW and PQ timing",
            "use a joint cosmological likelihood for Omega_DM, Delta N_eff, BBN, CMB energy injection, structure formation, and isocurvature",
        ],
        "V40_vector_route": {
            "purpose": "replace the isolated lambda_D-dominated annihilation that fails the V39 PQ-scale running test",
            "required_source_level_terms": [
                "a Higgsed U(1)_D gauge sector with a complete anomaly-free charge table",
                "a vectorlike assignment for the existing stable carrier or an explicitly matched successor carrier",
                "a dark-Higgs/portal sector neutral under the retained Z170 remnant",
                "a visible portal whose allowed operators, kinetic mixing boundary condition, and decays are derived",
            ],
            "nonnegotiable_checks": [
                "U(1)_D perturbativity and all coupled gauge/Yukawa beta functions remain controlled to the V40 UV matching scale",
                "the vector and dark-Higgs do not form an additional stable or long-lived excluded relic",
                "the portal equilibrates or produces the dark sector according to the solved Boltzmann history, not an assumption",
                "the portal does not reintroduce a PQ-quality, proton-decay, discrete-anomaly, or vacuum-selection failure",
            ],
        },
        "fail_closed_rule": "A relic-density number computed from imposed component masses, an imposed axion fraction, or a proxy width never promotes G5.",
    }


def flavour_contract() -> dict[str, Any]:
    return {
        "V39_nonidentifiability_witness": "Both YQQ=0 and YQQ=y Identity_3 are selector-allowed but generate inequivalent observables; the selector alone therefore does not predict flavour.",
        "minimal_UV_flavour_input_set": [
            "an exact flavour group (continuous, finite, modular, or geometric), representations of Q, Qc, Nv, vectorlike states, messengers, and flavons, and every relevant anomaly condition",
            "a complete flavon/messenger superpotential and Kähler potential that derives the alignment and all small expansion parameters",
            "matching formulae Y_ij^(r) = sum_a c_ij,a^(r) product_alpha (<phi_alpha>/M_F)^(n_alpha,a), where c and messenger thresholds are UV outputs rather than fitted matrices",
            "a derived right-neutrino Majorana matrix and the seesaw relation m_nu = -v_u^2 Y_nu^T M_N^(-1) Y_nu in a declared basis",
            "the full flavour-dependent soft matrices and A terms from the same hidden sector, including CP phases and RG threshold corrections",
        ],
        "G8_acceptance": [
            "diagonalize the calculated pole mass matrices to obtain charged-fermion masses, CKM, PMNS, neutrino masses, and CP phases after threshold/RG evolution",
            "test FCNC, EDM, lepton-flavour violation, neutrino, collider, and proton-decay flavour channels using the same Wilsons and covariance",
            "keep a registered distinction between observations used to determine genuinely free UV parameters and withheld observables used for prediction",
            "publish a versioned joint likelihood with experimental correlations, lattice/hadronic uncertainties, and theory truncation/systematic covariance",
            "require completed G7 Wilson/dressing/hadronic matching before calling any proton lifetime or branching fraction an out-of-sample G8 prediction",
        ],
        "fail_closed_rule": "A numerical Yukawa fit, a texture imposed without its flavon vacuum, or a likelihood that reuses its fitted observables as predictions leaves G8 open.",
    }


def report() -> dict[str, Any]:
    no_go = pure_yukawa_scale_no_go()
    vector = vector_portal_feasibility()
    data: dict[str, Any] = {
        "schema": "susy-v40-nonuv-completion-contract-v1",
        "status": STATUS,
        "scope": {
            "covered_gates": ["G2", "G3", "G4", "G5", "G6", "G8"],
            "not_a_substitute_for": ["G1 microscopic anomaly/UV completion", "G7 all-ring baryon-operator protection and matching"],
            "central_principle": "A physical gate is promotable only when its input functions, their vacuum, matching, observables, and uncertainties are derived by one specified V40 theory.",
        },
        "V39_context": v39_context(),
        "V39_pure_yukawa_G5_scale_no_go": no_go,
        "conditional_vector_portal_feasibility_witness": vector,
        "hidden_sector_and_mediation_contract": hidden_mediation_contract(),
        "vacuum_pole_and_EWSB_contract": vacuum_and_pole_contract(),
        "RGE_and_threshold_contract": rge_and_threshold_contract(),
        "dark_PQ_cosmology_contract": dark_pq_cosmology_contract(),
        "flavour_and_joint_likelihood_contract": flavour_contract(),
        "cross_gate_order": [
            "G1: establish the microscopic gauge/discrete/topological completion for every V40 addition",
            "G4: derive hidden-sector mediation, singlet soft terms, mu/Bmu, and flavour alignment",
            "G3: solve the full zero/finite-temperature vacuum and its selection history",
            "G2: derive component matrices and pole spectrum at the accepted vacuum",
            "G6: match/run all physical thresholds with covariance",
            "G5: solve dark/PQ/reheating cosmology from that spectrum and history",
            "G7: complete baryon-operator matching and dressing",
            "G8: evaluate the withheld-observable joint likelihood using all preceding outputs",
        ],
        "gate_decisions": {
            "G2_closed": False,
            "G3_closed": False,
            "G4_closed": False,
            "G5_closed": False,
            "G6_closed": False,
            "G8_closed": False,
            "complete_theory_exists": False,
            "why": (
                "This artifact supplies necessary equations and a feasible dark-sector direction, but it deliberately does not "
                "invent the hidden W/K/f, V40 source, vacuum, component amplitudes, cosmological history, or flavour UV origin."
            ),
        },
        "literature_basis": [
            "https://arxiv.org/abs/0801.3278",
            "https://arxiv.org/abs/0808.3598",
            "https://arxiv.org/abs/0909.2863",
            "https://arxiv.org/abs/0911.1120",
            "https://arxiv.org/abs/1807.06209",
            "https://arxiv.org/abs/1807.06211",
            "https://arxiv.org/abs/1606.07494",
        ],
        "source_manifest": [
            {
                "path": name,
                "exists": (ROOT / name).is_file(),
                "sha256": sha256_file(ROOT / name),
            }
            for name in (
                "susy_v40_nonuv_completion_contract.py",
                "test_susy_v40_nonuv_completion_contract.py",
                "SUSY_V39_COMPLETE_THEORY_AUDIT.json",
                "SUSY_V39_SOFT_BOUNDARY_AUDIT.json",
                "SUSY_V39_G5_SECLUDED_FREEZEOUT_CERTIFICATE.json",
                "SUSY_V39_G7_G8_ARCHITECTURE.json",
            )
        ],
    }
    data["core_sha256"] = canonical_sha(data)
    return data


def markdown(data: Mapping[str, Any]) -> str:
    no_go = data["V39_pure_yukawa_G5_scale_no_go"]
    vec = data["conditional_vector_portal_feasibility_witness"]["tree_level_screen"]
    gates = data["gate_decisions"]
    return f"""# V40 non-UV completion contract

Status: `{data['status']}`

This is a fail-closed completion contract for G2--G6 and G8.  It supplies the
equations and microscopic objects required for a genuine V40 calculation; it
does not turn a chosen benchmark into a prediction.  All covered gates remain
open.

## Exact V39 dark-sector boundary

For the stated V39 isolated beta function
`d lambda_D/d ln(mu)=3 lambda_D^3/(16 pi^2)`, the fitted
`lambda_D={no_go['V39_fitted_lambda_D']:.6f}` has a one-loop pole at
`{no_go['V39_lambda_pole_GeV']:.3e} GeV`, below
`fPQ={FPQ_GEV:.1e} GeV`.  Requiring no pole through `fPQ` bounds it by
`lambda_D<={no_go['lambda_D_max_without_a_pole_below_fPQ']:.6f}`.  With the
same fixed-spectrum `lambda_D^4` annihilation scaling, that can supply only
`{no_go['maximum_proxy_annihilation_fraction_if_PQ_safe']:.3f}` of the V39
target cross section and gives a minimum proxy abundance
`Omega h^2={no_go['minimum_proxy_Omega_h2_if_PQ_safe']:.3f}`.  This excludes
that isolated mechanism, not new dark dynamics.

## Coherent replacement route — conditional only

A Higgsed, anomaly-free vectorlike `U(1)_D` can use
`chi chibar -> V_D V_D` instead of the large Yukawa.  At the illustrative
`m_chi={MCHI_GEV:.0f} GeV`, `m_VD={MVD_GEV:.0f} GeV` point, the tree proxy
needs `alpha_D={vec['alpha_D_needed_in_tree_proxy']:.4f}` and
`g_D={vec['g_D_needed_in_tree_proxy']:.4f}`.  With only one unit-charge Dirac
carrier plus one unit-charge complex dark Higgs, `b_D=5/3` and the one-loop
pole is `{vec['one_loop_U1D_pole_GeV']:.3e} GeV`; it lies above the reduced
Planck scale.  This is a perturbativity feasibility result, not a relic,
direct-detection, or UV-completion result.

If V40 retains the V39 cascade, the dark Higgs and every portal VEV must be
neutral under its exact `Z170`; otherwise the proposed fix changes the
stability problem rather than solving it.  A selector rebuild must state and
audit its replacement stabilizer.  The new `U(1)_D` adds G1 anomaly,
kinetic-mixing, selector, PQ-quality, and baryon-protection obligations.

## Promotion contract

- **G4:** Specify and solve the hidden `W`, `K`, and gauge-kinetic matrix; derive every soft term, singlet mass/tadpole, `mu/Bmu`, phase, messenger threshold, and flavour alignment.
- **G3/G2:** Evaluate the full zero- and finite-temperature effective potential, establish vacuum selection/lifetime, then calculate all component matrices and gauge-consistent pole masses with covariance.
- **G6:** Regenerate V40 RGEs, match every physical threshold, evolve the coupled system including Abelian mixing, and propagate microscopic/threshold/truncation covariance.
- **G5:** Derive component amplitudes, reheating and PQ histories, solve coupled Boltzmann equations, and test the joint dark-matter/axion/BBN/CMB/isocurvature likelihood.
- **G8:** Derive a UV flavour group, flavon/messenger vacuum and soft alignment; reserve withheld observables for a versioned correlated joint likelihood.  G7 matching is a prerequisite for proton-decay predictions.

No positive result in this file closes a gate.  Its purpose is to prevent a
future V40 build from hiding the independent inputs that V39 correctly exposed.

Core SHA-256: `{data['core_sha256']}`
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write and args.check:
        raise SystemExit("choose at most one of --write and --check")
    data = report()
    if args.write:
        JSON_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        MD_PATH.write_text(markdown(data), encoding="utf-8")
        print("SUSY V40 non-UV completion contract: wrote certificates")
        return
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise SystemExit("generated V40 contract is missing; run with --write")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != data:
            raise SystemExit("generated V40 contract JSON is stale; run with --write")
        if MD_PATH.read_text(encoding="utf-8") != markdown(data):
            raise SystemExit("generated V40 contract Markdown is stale; run with --write")
        print("SUSY V40 non-UV completion contract: PASS")
        return
    print(json.dumps(data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
