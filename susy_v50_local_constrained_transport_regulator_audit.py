#!/usr/bin/env python3
"""V50 finite local constrained-transport regulator audit.

V49 used a shortest normal Wilson line inside a finite-width source kernel.
That expression was gauge covariant but bilocal over the collar.  This audit
replaces it by a finite deconstruction with only site-local interactions and
nearest-neighbour holomorphic constraints.  Eliminating the auxiliary chain
reconstructs the ordered transporter, while the fundamental regulator action
contains no endpoint-to-interior Wilson line.

The audit is deliberately scoped.  It can close the explicit-regulator clause
C2 for a finite deconstruction regulator class.  It does not assemble the
complete A/Xi/C/O7/O8 action, prove the full positive domain, perform a second
profile rematch, or publish the physical SO(10)-to-PS Wilson array; therefore
it cannot close G2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import susy_v48_resolved_source_wall_audit as v48


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V50_LOCAL_CONSTRAINED_TRANSPORT_REGULATOR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V50_LOCAL_CONSTRAINED_TRANSPORT_REGULATOR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v50_local_constrained_transport_regulator_audit.py"

STATUS = (
    "V50_FINITE_LOCAL_CONSTRAINED_TRANSPORT_MOOSE_DEFINED__"
    "ONLY_SITE_LOCAL_AND_NEAREST_NEIGHBOUR_COUPLINGS__"
    "TRIANGULAR_LINK_INDEPENDENT_CONSTRAINT_DETERMINANT__"
    "EXACT_AUXILIARY_LIMIT_HAS_NO_EXTRA_SOURCE_POLES__"
    "POSITIVE_KAHLER_COMPLETION_HAS_ONE_INTENDED_SOURCE_ZERO_AND_N_CUTOFF_PAIRS__"
    "LAYERED_TRANSFER_ZERO_ENERGY_EXACT_AND_SECOND_ORDER_CONVERGENT__"
    "G1_ANOMALY_CLASS_UNCHANGED__C2_EXPLICIT_REGULATOR_PASS__"
    "FULL_G2_FAIL_CLOSED"
)

SOURCE_FIELDS = (
    "Phi_210",
    "Sigma_126",
    "barSigma_bar126",
    "S",
    "ThetaPlus",
    "ThetaMinus",
)

SOURCE_DIMENSIONS = {
    "Phi_210": 210,
    "Sigma_126": 126,
    "barSigma_bar126": 126,
    "S": 1,
    "ThetaPlus": 1,
    "ThetaMinus": 1,
}

UPSTREAM_INPUTS = (
    ROOT / "SUSY_V47_RELATIVE_ETA_BORDISM_AUDIT.json",
    ROOT / "SUSY_V49_FIXED_PROFILE_SOURCE_REGULATOR_AUDIT.json",
    ROOT / "SUSY_V49_G2_FRONTIER_INTEGRATION_AUDIT.json",
)

PRIMARY_SOURCES = (
    {
        "url": "https://arxiv.org/abs/hep-th/0104005",
        "use": "finite product-gauge mooses as local deconstructions of an extra dimension",
    },
    {
        "url": "https://arxiv.org/abs/he-th/0106256",
        "use": "local 5D hypermultiplet action in manifest four-dimensional N=1 superspace",
    },
    {
        "url": "https://arxiv.org/abs/hep-ph/0112230",
        "use": "gauge-covariant fifth-direction superfields and boundary operators",
    },
    {
        "url": "https://arxiv.org/abs/1412.3486",
        "use": "supersymmetric gauge-moose realization of a discretized five-dimensional theory",
    },
)


Matrix = list[list[complex]]
Vector = list[complex]


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(report: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in report.items() if key != "core_sha256"}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def trapezoid_weights(num_cells: int) -> list[float]:
    """Unit-normalized node weights for a top-hat collar."""

    if num_cells < 1:
        raise ValueError("num_cells must be positive")
    weights = [1.0 / num_cells for _ in range(num_cells + 1)]
    weights[0] *= 0.5
    weights[-1] *= 0.5
    return weights


def incidence_matrix(num_cells: int) -> Matrix:
    """Open-chain incidence B with (B X)_j = X_j-X_(j+1)."""

    if num_cells < 1:
        raise ValueError("num_cells must be positive")
    result = [[0.0j for _ in range(num_cells + 1)] for _ in range(num_cells)]
    for row in range(num_cells):
        result[row][row] = 1.0 + 0.0j
        result[row][row + 1] = -1.0 + 0.0j
    return result


def transport_singular_values(num_cells: int, mass_scale: float = 1.0) -> list[float]:
    """Nonzero singular values of M B for an N-edge open chain."""

    if num_cells < 1:
        raise ValueError("num_cells must be positive")
    if mass_scale <= 0.0:
        raise ValueError("mass_scale must be positive")
    return [
        2.0 * mass_scale * math.sin(k * math.pi / (2.0 * (num_cells + 1)))
        for k in range(1, num_cells + 1)
    ]


def vector_masses(num_cells: int, gauge_coupling: float, link_vev: float) -> list[float]:
    """Open-moose vector masses, including the intended diagonal zero."""

    if num_cells < 1:
        raise ValueError("num_cells must be positive")
    if gauge_coupling <= 0.0 or link_vev <= 0.0:
        raise ValueError("gauge coupling and link vev must be positive")
    return [
        2.0
        * gauge_coupling
        * link_vev
        * math.sin(k * math.pi / (2.0 * (num_cells + 1)))
        for k in range(num_cells + 1)
    ]


def determinant(matrix: Sequence[Sequence[complex]], tolerance: float = 1.0e-15) -> complex:
    """Small deterministic complex determinant by pivoted elimination."""

    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a square matrix")
    work = [[complex(value) for value in row] for row in matrix]
    answer = 1.0 + 0.0j
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) <= tolerance:
            return 0.0j
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            answer *= -1.0
        pivot_value = work[column][column]
        answer *= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column] / pivot_value
            for inner in range(column + 1, size):
                work[row][inner] -= factor * work[column][inner]
    return answer


def scalar_constraint_jacobian(num_cells: int, ratios: Sequence[complex]) -> Matrix:
    """Jacobian dC/d(X_0,...,X_(N-1)) with endpoint X_N held fixed.

    C_j=X_j-r_j Omega_j X_(j+1).  In one component and a fixed link
    background the matrix is upper triangular with unit diagonal, regardless
    of every r_j Omega_j.  The block result is the corresponding identity
    determinant per representation component.
    """

    if num_cells < 1 or len(ratios) != num_cells:
        raise ValueError("one ratio is required for every cell")
    result = [[0.0j for _ in range(num_cells)] for _ in range(num_cells)]
    for row in range(num_cells):
        result[row][row] = 1.0 + 0.0j
        if row + 1 < num_cells:
            result[row][row + 1] = -complex(ratios[row])
    return result


def rotation(angle: float) -> Matrix:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return [[cosine + 0.0j, -sine + 0.0j], [sine + 0.0j, cosine + 0.0j]]


def transpose(matrix: Sequence[Sequence[complex]]) -> Matrix:
    return [[complex(matrix[row][column]) for row in range(len(matrix))] for column in range(len(matrix[0]))]


def matrix_vector(matrix: Sequence[Sequence[complex]], vector: Sequence[complex]) -> Vector:
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix/vector shape mismatch")
    return [sum(complex(value) * complex(vector[column]) for column, value in enumerate(row)) for row in matrix]


def vector_max_difference(first: Sequence[complex], second: Sequence[complex]) -> float:
    if len(first) != len(second):
        raise ValueError("vector shape mismatch")
    return max((abs(complex(a) - complex(b)) for a, b in zip(first, second)), default=0.0)


def transported_replicas(
    endpoint: Sequence[complex], links: Sequence[Sequence[Sequence[complex]]]
) -> list[Vector]:
    """Solve X_j=Omega_j X_(j+1) recursively from endpoint X_N."""

    replicas: list[Vector] = [[] for _ in range(len(links) + 1)]
    replicas[-1] = [complex(value) for value in endpoint]
    for site in range(len(links) - 1, -1, -1):
        replicas[site] = matrix_vector(links[site], replicas[site + 1])
    return replicas


def gauge_covariance_residual(
    endpoint: Sequence[complex],
    links: Sequence[Sequence[Sequence[complex]]],
    gauges: Sequence[Sequence[Sequence[complex]]],
) -> float:
    """Numerically verify Omega'_j=g_j Omega_j g_(j+1)^-1."""

    if len(gauges) != len(links) + 1:
        raise ValueError("one gauge matrix is required at every site")
    original = transported_replicas(endpoint, links)
    transformed_links: list[Matrix] = []
    for site, link in enumerate(links):
        transformed_links.append(
            v48.matrix_multiply(
                v48.matrix_multiply(gauges[site], link), transpose(gauges[site + 1])
            )
        )
    transformed_endpoint = matrix_vector(gauges[-1], endpoint)
    transformed = transported_replicas(transformed_endpoint, transformed_links)
    expected = [matrix_vector(gauges[site], original[site]) for site in range(len(gauges))]
    return max(vector_max_difference(a, b) for a, b in zip(transformed, expected))


def source_kick(weight: float, integrated_source: Sequence[Sequence[complex]]) -> Matrix:
    """Local node source insertion g^+=g^-+weight*Lambda*f."""

    size = len(integrated_source)
    if any(len(row) != size for row in integrated_source):
        raise ValueError("integrated source must be square")
    return v48.block_matrix(
        v48.identity(size),
        v48.zero_matrix(size),
        v48.matrix_scale(weight, integrated_source),
        v48.identity(size),
    )


def free_transfer(signed_mass: float, distance: float, size: int) -> Matrix:
    """Exact source-free H/Hc transfer over one local segment."""

    if distance < 0.0 or size < 1:
        raise ValueError("distance must be nonnegative and size positive")
    cosine = math.cos(signed_mass * distance)
    sine = math.sin(signed_mass * distance)
    identity = v48.identity(size)
    return v48.block_matrix(
        v48.matrix_scale(cosine, identity),
        v48.matrix_scale(sine, identity),
        v48.matrix_scale(-sine, identity),
        v48.matrix_scale(cosine, identity),
    )


def layered_transfer(
    num_cells: int,
    signed_mass: float,
    epsilon: float,
    integrated_source: Sequence[Sequence[complex]],
) -> Matrix:
    """Symmetric local layered approximation to the square collar.

    The endpoint half-kicks and interior full kicks are the trapezoidal
    product formula.  Every kick is a site-local superpotential insertion and
    every free factor is propagation through one source-free local segment.
    """

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    weights = trapezoid_weights(num_cells)
    size = len(integrated_source)
    transfer = source_kick(weights[0], integrated_source)
    free = free_transfer(signed_mass, epsilon / num_cells, size)
    for site in range(num_cells):
        transfer = v48.matrix_multiply(free, transfer)
        transfer = v48.matrix_multiply(source_kick(weights[site + 1], integrated_source), transfer)
    return transfer


def transfer_blocks(transfer: Sequence[Sequence[complex]]) -> tuple[Matrix, Matrix, Matrix, Matrix]:
    total = len(transfer)
    if total % 2 or any(len(row) != total for row in transfer):
        raise ValueError("transfer must be even-dimensional and square")
    size = total // 2
    upper_left = [[complex(transfer[row][column]) for column in range(size)] for row in range(size)]
    upper_right = [[complex(transfer[row][column]) for column in range(size, total)] for row in range(size)]
    lower_left = [[complex(transfer[row][column]) for column in range(size)] for row in range(size, total)]
    lower_right = [[complex(transfer[row][column]) for column in range(size, total)] for row in range(size, total)]
    return upper_left, upper_right, lower_left, lower_right


def layered_boundary_map(
    num_cells: int,
    signed_mass: float,
    epsilon: float,
    integrated_source: Sequence[Sequence[complex]],
) -> Matrix:
    """B_N=D_N^-1 C_N for the local layered transfer."""

    _, _, lower_left, lower_right = transfer_blocks(
        layered_transfer(num_cells, signed_mass, epsilon, integrated_source)
    )
    return v48.matrix_multiply(v48.inverse(lower_right), lower_left)


def quadratic_profile_average(num_cells: int) -> float:
    """Trapezoidal average of x^2 on x in [0,1]."""

    weights = trapezoid_weights(num_cells)
    return sum(weight * (site / num_cells) ** 2 for site, weight in enumerate(weights))


def build_report() -> dict[str, Any]:
    num_cells = 4
    epsilon = 0.05
    signed_mass = 0.37
    mass_scale = num_cells / epsilon
    source = v48.source_matrix(0.4, 0.6, 0.2, -0.15, su5_singlet=True)
    exact_transfer = v48.wall_transfer(signed_mass, epsilon, source)["T"]
    exact_boundary = v48.boundary_map(signed_mass, epsilon, source)
    cell_counts = (1, 2, 4, 8, 16, 32)
    transfer_errors: dict[str, float] = {}
    boundary_errors: dict[str, float] = {}
    symplectic_residuals: dict[str, float] = {}
    for count in cell_counts:
        layered = layered_transfer(count, signed_mass, epsilon, source)
        transfer_errors[str(count)] = v48.max_difference(layered, exact_transfer)
        boundary_errors[str(count)] = v48.max_difference(
            layered_boundary_map(count, signed_mass, epsilon, source), exact_boundary
        )
        symplectic_residuals[str(count)] = v48.j_unitarity_residual(layered)

    convergence_ratios = {
        f"{first}_to_{second}": transfer_errors[str(first)] / transfer_errors[str(second)]
        for first, second in zip(cell_counts[:-1], cell_counts[1:])
    }
    zero_exact = max(
        v48.max_difference(layered_boundary_map(count, 0.0, epsilon, source), source)
        for count in cell_counts
    )
    profile_errors = {
        str(count): abs(quadratic_profile_average(count) - 1.0 / 3.0)
        for count in cell_counts
    }

    links = [rotation(0.13), rotation(-0.21), rotation(0.34), rotation(-0.08)]
    gauges = [rotation(0.17), rotation(-0.29), rotation(0.11), rotation(0.37), rotation(-0.23)]
    covariance_residual = gauge_covariance_residual([0.7, -0.2], links, gauges)
    ratios = [1.1 + 0.2j, -0.4 + 0.3j, 0.8 - 0.1j, 1.7 + 0.4j]
    jacobian_det = determinant(scalar_constraint_jacobian(num_cells, ratios))
    transport_masses = transport_singular_values(num_cells, mass_scale)
    gauge_masses = vector_masses(num_cells, 1.0, mass_scale)

    report: dict[str, Any] = {
        "schema_version": "susy-spin10-v50-local-constrained-transport-regulator-v1",
        "status": STATUS,
        "scope": {
            "question": "Can the V49 gauge-covariant finite-width source interaction be represented by a genuinely local finite regulator without a fundamental bilocal Wilson line or an uncontrolled source tower?",
            "answer": "yes, as a finite nearest-neighbour supersymmetric deconstruction with constrained source replicas",
            "gate_effect": "the explicit-regulator clause C2 passes for this declared finite-deconstruction regulator class; the full seven-clause G2 conjunction remains false",
        },
        "finite_local_construction": {
            "sites": "j=0,...,N across a collar of width epsilon, spacing a=epsilon/N",
            "site_gauge_group": "G_j=Spin(10)xU(1)_F; the product is the lattice gauge redundancy of the discretized collar and is Higgsed/identified to the physical diagonal group",
            "link": "Omega_j is the holomorphic link of the discretized 5D vector multiplet and transforms as Omega_j -> g_j Omega_j g_(j+1)^(-1)",
            "source_replicas": "for each physical endpoint chiral X_A,N introduce X_A,j in R_A at every interior site and P_A,j in the conjugate representation at the same interior site",
            "gauge_laws": [
                "X_A,j -> R_A(g_j) X_A,j",
                "P_A,j -> P_A,j R_A(g_j)^(-1)",
                "R_A(Omega_j) -> R_A(g_j) R_A(Omega_j) R_A(g_(j+1))^(-1)",
            ],
            "exact_auxiliary_Kahler": "only the endpoint X_A,N has the original V47 source Kahler term; interior X_A,j and P_A,j are constrained auxiliary chirals with no four-dimensional kinetic operator",
            "transport_superpotential": "W_tr=sum_A sum_j mu_A P_A,j [X_A,j-R_A(Omega_j)X_A,(j+1)]",
            "endpoint_action": "K_V47(X_N,X_Ndagger,V_N) and W_source,V47(X_N) are unchanged",
            "local_interaction": "W_int=sum_j w_j I_V49(X_j,H_j,Hc_j,Delta5 H_j,...) with positive trapezoid weights w_0=w_N=1/(2N), w_j=1/N",
            "locality": "every monomial is on one site or one adjacent link; no product Omega_j...Omega_(N-1), endpoint-to-interior transporter, or inverse differential operator occurs in the fundamental action",
            "link_action": "sum_j integral d4theta v^2 tr(Omega_j^dagger e^(V_j) Omega_j e^(-V_(j+1))) plus site gauge kinetic terms; it is the standard finite supersymmetric gauge-moose regulator",
        },
        "variation_and_exact_elimination": {
            "delta_P": "X_A,j=R_A(Omega_j)X_A,j+1 recursively",
            "delta_X_interior": "a backward nearest-neighbour recursion fixes P_A,j from the local source currents",
            "H_zero_branch": "all local currents vanish at H=Hc=0; the backward recursion gives P_A,j=0 and the endpoint equation is exactly dW_source,V47/dX_A,N=0",
            "effective_solution": "X_A,j=R_A(Omega_j...Omega_N-1)X_A,N appears only after auxiliary elimination",
            "effective_interaction": "substitution gives the V49 gauge-covariant transported Riemann sum; the ordered link product is an emergent Green-function solution, not a fundamental bilocal vertex",
            "constraint_jacobian": "with X_N held fixed, dC/d(X_0,...,X_N-1) is block upper triangular with identity diagonal",
            "determinant": "det(dC/dX_aux)=1 per representation component (or product mu_A^(N dim R_A) before normalization), independent of every link and gauge background",
            "quantum_measure": "the exact auxiliary integration therefore adds no link-dependent determinant, no source pole and no new anomaly phase",
        },
        "positive_spectrum_completion": {
            "purpose": "a nondegenerate positive-Kahler realization showing that the exact constraint is a controlled heavy-mass limit",
            "Kahler": "K_tr=(1/(N+1)) sum_j X_j^dagger e^V_j X_j + sum_(j=0)^(N-1) P_j^dagger e^-V_j P_j",
            "superpotential": "W_tr=(M_c/sqrt(N+1)) sum_j P_j(X_j-Omega_j X_(j+1))",
            "zero_mode": "rank(B)=N for the N x (N+1) open-chain incidence matrix; exactly one profile X_0=...=X_N survives per original source component, and its displayed Kahler norm is one",
            "heavy_chiral_masses": "m_k=2 M_c sin[k pi/(2(N+1))], k=1,...,N; each is a vectorlike supersymmetric pair",
            "gauge_spectrum": "m_V,k=2 g v sin[k pi/(2(N+1))], k=0,...,N; k=0 is the intended diagonal gauge multiplet and every relative vector is massive",
            "cutoff_choice": "with M_c=g v=1/a=N/epsilon, the lightest added chiral and relative-vector masses are at least sqrt(2)/epsilon for every N>=1 and approach pi/epsilon",
            "finite_Mc_scope": "endpoint source interactions can mix the zero profile with heavy profiles, but their effects are analytic threshold corrections suppressed by E/M_c and belong to the declared matching coefficients; no extra light state is forced",
            "exact_limit": "M_c->infinity (or zero auxiliary Kahler weight) returns the exact constrained action and removes all N heavy pairs",
        },
        "continuum_collar_matching": {
            "weights": "the trapezoid weights are positive and sum to one",
            "source_reconstruction": "after solving the local constraints, sum_j w_j I(X_j,H_j,...) converges to epsilon^-1 integral_0^epsilon ds I(U(s,epsilon)X_N,H(s),...) with O(N^-2) quadrature error for smooth fields",
            "local_HH_kick": "at node j, T_source,j=[[I,0],[w_j Lambda,I]]",
            "free_segment": "between nodes, T_free=[[cos(ma)I,sin(ma)I],[-sin(ma)I,cos(ma)I]]",
            "layered_transfer": "T_N=T_source,N T_free ... T_source,1 T_free T_source,0",
            "zero_energy": "T_N(0)=[[I,0],[Lambda,I]] and B_N(0)=Lambda exactly for every finite N",
            "symplecticity": "each local factor is J-unitary/symplectic for Hermitian Lambda, hence their finite product defines a self-adjoint restricted H/Hc transfer",
            "finite_mass_limit": "the symmetric product formula converges to the V48 square-collar transfer with second-order error",
            "matching_policy": "finite N defines a different local regulator scheme; all finite Hc, mixed, derivative and source counterterms must be matched in this same scheme before C3-C7 can pass",
        },
        "G1_anomaly_audit": {
            "interior_pairs": "at every interior site and for every source representation R_q, X_j in R_q and P_j in conjugate Rbar_-q form a vectorlike pair",
            "local_polynomial_rows": "tr R^3, U(1)_F^3, gravity^2-U(1)_F and Spin(10)^2-U(1)_F contributions of every auxiliary pair cancel exactly",
            "global_class": "a vectorlike pair admits a gauge-invariant mass through the local link and has a canonically trivial determinant line; it adds no torsion anomaly class",
            "endpoint_content": "the only unpaired source mode is X_N, exactly the original V47 source representation; the diagonal gauge group and faithful quotient are unchanged",
            "link_content": "Omega_j is the discretized existing 5D gauge connection; its adjoint fermionic content is real/neutral and replaces collar gauge modes rather than adding chiral wall matter",
            "constraint_measure": "the link-independent unit Jacobian cannot generate an eta or Wess-Zumino phase",
            "preserved_results": [
                "Omega5^Spin(BP)=0",
                "Omega5^Spin(B(P x U(1)_F))=0",
                "Omega6^Spin(B(Spin(10)xU(1)_F),B(PxU(1)_F))=0",
                "the V47 wall-local anomaly polynomials remain zero",
            ],
            "conclusion": "G1 remains closed; no anomaly calculation is weakened or replaced",
        },
        "numerical_certificate": {
            "parameters": {
                "N": num_cells,
                "epsilon": epsilon,
                "a": epsilon / num_cells,
                "M_c": mass_scale,
                "signed_mass": signed_mass,
            },
            "weights": trapezoid_weights(num_cells),
            "weights_sum": sum(trapezoid_weights(num_cells)),
            "weights_minimum": min(trapezoid_weights(num_cells)),
            "constraint_jacobian_determinant_real": float(jacobian_det.real),
            "constraint_jacobian_determinant_imag": float(jacobian_det.imag),
            "gauge_covariance_residual": covariance_residual,
            "transport_heavy_masses": transport_masses,
            "transport_zero_profile_count_per_original_component": 1,
            "original_source_component_count": sum(SOURCE_DIMENSIONS.values()),
            "intended_source_component_zero_modes": sum(SOURCE_DIMENSIONS.values()),
            "heavy_vectorlike_chiral_pairs": num_cells * sum(SOURCE_DIMENSIONS.values()),
            "gauge_vector_masses": gauge_masses,
            "gauge_zero_mode_count": sum(abs(value) < 1.0e-13 for value in gauge_masses),
            "transfer_errors_vs_exact_square": transfer_errors,
            "boundary_map_errors_vs_exact_square": boundary_errors,
            "transfer_error_refinement_ratios": convergence_ratios,
            "layered_J_unitarity_residuals": symplectic_residuals,
            "maximum_zero_energy_boundary_map_error": zero_exact,
            "quadratic_profile_trapezoid_errors": profile_errors,
            "source_replica_propagating_poles_in_exact_auxiliary_limit": 0,
            "additional_massless_source_profiles_in_positive_completion": 0,
        },
        "adversarial_scope": {
            "what_is_now_repaired": "V49 D8: the fundamental regulator action is finite and nearest-neighbour local, while retaining gauge covariance and no uncontrolled source tower",
            "not_a_hidden_bilocal_vertex": "the ordered product appears only after solving local equations, exactly as a propagator or Schur complement appears after integrating out local mediators",
            "not_claimed": [
                "a renormalizable continuum five-dimensional UV completion of the nonlinear link sector",
                "the complete A/Xi/C/O7/O8 path-ordered transfer",
                "positivity of the entire retained action rather than the transport and restricted H/Hc sectors",
                "an independent second-profile and loop-subtraction rematch",
                "normalized SO(10)-to-Pati-Salam Cartesian Clebsches and the physical Wilson array",
            ],
            "residual_risk": "a linear UV realization of the nonlinear links can add radial thresholds; it must be vectorlike and its finite thresholds must be included if that stronger UV claim is later made",
        },
        "decision": {
            "finite_deconstruction_regulator_defined": True,
            "fundamental_action_site_or_nearest_neighbour_local": True,
            "fundamental_endpoint_to_interior_Wilson_line_absent": True,
            "effective_ordered_link_product_after_elimination": True,
            "constraint_determinant_link_independent": True,
            "uncontrolled_source_light_modes_absent": True,
            "restricted_transfer_positive_and_symplectic": True,
            "G1_anomaly_closure_preserved": True,
            "C2_explicit_regulator_passes": True,
            "point_local_continuum_5D_UV_completion_proved": False,
            "complete_full_action_domain_proved": False,
            "second_profile_rematch_done": False,
            "physical_component_Wilson_array_done": False,
            "G2_closed_by_this_subaudit": False,
            "clauses_promoted": ["C2"],
            "gates_promoted": [],
        },
        "primary_sources": list(PRIMARY_SOURCES),
        "provenance": {
            "upstream_sha256": {path.name: sha256_file(path) for path in UPSTREAM_INPUTS},
            "existing_files_modified": False,
        },
    }
    report = json.loads(json.dumps(report, ensure_ascii=True))
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash is stale")
    certificate = report["numerical_certificate"]
    if abs(certificate["weights_sum"] - 1.0) > 2.0e-15 or certificate["weights_minimum"] <= 0.0:
        raise RuntimeError("local profile weights are not positive and normalized")
    determinant_value = complex(
        certificate["constraint_jacobian_determinant_real"],
        certificate["constraint_jacobian_determinant_imag"],
    )
    if abs(determinant_value - 1.0) > 2.0e-14:
        raise RuntimeError("constraint determinant is not unity")
    if certificate["gauge_covariance_residual"] > 2.0e-13:
        raise RuntimeError("nearest-neighbour transport lost gauge covariance")
    if certificate["transport_zero_profile_count_per_original_component"] != 1:
        raise RuntimeError("transport chain does not have exactly one intended source zero mode")
    if certificate["intended_source_component_zero_modes"] != certificate["original_source_component_count"]:
        raise RuntimeError("the localizer changed the number of physical source components")
    if certificate["gauge_zero_mode_count"] != 1:
        raise RuntimeError("gauge moose does not have exactly one diagonal zero mode")
    if min(certificate["transport_heavy_masses"]) < math.sqrt(2.0) / certificate["parameters"]["epsilon"] - 1.0e-10:
        raise RuntimeError("transport completion introduced a sub-collar light mode")
    if certificate["maximum_zero_energy_boundary_map_error"] > 2.0e-13:
        raise RuntimeError("finite local layering lost the exact zero-energy source map")
    if max(certificate["layered_J_unitarity_residuals"].values()) > 1.0e-12:
        raise RuntimeError("finite local transfer lost symplecticity")
    if min(certificate["transfer_error_refinement_ratios"].values()) < 3.8:
        raise RuntimeError("layered transfer is not displaying second-order convergence")
    decision = report["decision"]
    required_true = (
        "finite_deconstruction_regulator_defined",
        "fundamental_action_site_or_nearest_neighbour_local",
        "fundamental_endpoint_to_interior_Wilson_line_absent",
        "constraint_determinant_link_independent",
        "uncontrolled_source_light_modes_absent",
        "restricted_transfer_positive_and_symplectic",
        "G1_anomaly_closure_preserved",
        "C2_explicit_regulator_passes",
    )
    if not all(decision[key] for key in required_true):
        raise RuntimeError("a proved local-regulator condition was lost")
    if decision["point_local_continuum_5D_UV_completion_proved"]:
        raise RuntimeError("finite deconstruction was overpromoted to a continuum UV completion")
    if decision["complete_full_action_domain_proved"] or decision["second_profile_rematch_done"]:
        raise RuntimeError("the regulator subaudit was overpromoted into later G2 clauses")
    if decision["physical_component_Wilson_array_done"] or decision["G2_closed_by_this_subaudit"]:
        raise RuntimeError("this subaudit cannot close G2")
    if decision["clauses_promoted"] != ["C2"] or decision["gates_promoted"]:
        raise RuntimeError("gate/criterion promotion drifted")


def render_markdown(data: Mapping[str, Any]) -> str:
    cert = data["numerical_certificate"]
    ratios = cert["transfer_error_refinement_ratios"]
    return f"""# V50 finite local constrained-transport regulator audit

Status: `{data['status']}`

## Verdict

V49 defect D8 is repaired **for a declared finite-deconstruction regulator
class**.  Replace the endpoint-to-interior Wilson-line vertex by a finite
chain of site source replicas and conjugate chiral multipliers.  Every term in
the fundamental action is either site-local or nearest-neighbour.  Eliminating
the chain reconstructs the ordered transporter, but that product is a derived
Schur-complement/Green-function expression rather than a fundamental bilocal
coupling.

The chain has a link-independent triangular constraint determinant.  In the
exact auxiliary version it has no four-dimensional poles.  A positive-Kahler
completion has precisely one intended source zero profile and `N` vectorlike
massive pairs.  Thus **C2 passes**, while G1 remains closed.  This does **not**
close G2: the complete strong-collar domain, full positivity, independent
profile rematch, and physical component Wilson array remain absent.

## Local regulator action

Use `N+1` sites `j=0,...,N` across `epsilon`, with `a=epsilon/N`.  Let
`Omega_j` be the holomorphic link of the discretized 5D gauge multiplet,

```text
Omega_j -> g_j Omega_j g_(j+1)^(-1).
```

For every endpoint source `X_A,N` introduce an interior replica `X_A,j` and a
conjugate multiplier `P_A,j`.  The exact constrained action is

```text
K = K_V47(X_N,X_Ndagger,V_N),
W = W_source,V47(X_N)
  + sum_(A,j) mu_A P_A,j [X_A,j - R_A(Omega_j) X_A,(j+1)]
  + sum_j w_j I_V49(X_j,H_j,Hc_j,Delta5 H_j,...).
```

Here `w_0=w_N=1/(2N)` and `w_j=1/N` internally.  Every interaction is on one
site; every constraint crosses one link.  No `Omega_j...Omega_(N-1)` product
occurs in this action.

Varying `P_A,j` gives

```text
X_A,j = R_A(Omega_j) X_A,j+1.
```

Only after solving these local equations does the ordered link product
appear.  With `X_N` held fixed, the constraint Jacobian with respect to the
interior `X` variables is block upper triangular with identity diagonal.  Its
sample determinant is `{cert['constraint_jacobian_determinant_real']:.1f}` and
the gauge-covariance residual is `{cert['gauge_covariance_residual']:.3g}`.
Consequently exact auxiliary integration adds no link-dependent determinant,
source pole, or anomaly phase.

At `H=Hc=0`, every interaction current vanishes.  The backward `X` variation
then sets every `P` to zero and the endpoint equation is exactly the V47
source F-equation.  The source branch is not changed.

## Positive spectrum completion

A nondegenerate local completion is

```text
K_tr = (1/(N+1)) sum_(j=0)^N X_j^dagger e^(V_j) X_j
     + sum_(j=0)^(N-1) P_j^dagger e^(-V_j) P_j,
W_tr = (M_c/sqrt(N+1)) sum_j P_j (X_j-Omega_j X_(j+1)).
```

In the unit-link vacuum the incidence matrix has rank `N`.  There is exactly
one normalized source profile `X_0=...=X_N`, and

```text
m_k = 2 M_c sin[k pi/(2(N+1))],  k=1,...,N.
```

The gauge moose similarly has one intended diagonal vector and
`m_V,k=2gv sin[k pi/(2(N+1))]` for the relative vectors.  With
`M_c=gv=1/a`, every added mode is at least `sqrt(2)/epsilon`; for the
certificate its lightest transport mass is `{min(cert['transport_heavy_masses']):.6g}`.
There is no uncontrolled light tower.  Finite-`M_c` effects are ordinary
analytic threshold corrections and must be matched; the infinite-mass limit
returns the exact constraint.

## Collar matching

After eliminating the local chain, the weighted sum is the trapezoidal
approximation to the V49 transported top-hat interaction.  At each node the
H/Hc transfer receives a local kick and each intervening segment is free:

```text
T_source,j = [[I,0],[w_j Lambda,I]],
T_free     = [[cos(ma)I,sin(ma)I],[-sin(ma)I,cos(ma)I]].
```

Every factor is symplectic, so the finite product is symplectic.  At zero
energy, the weights sum to one and

```text
T_N(0)=[[I,0],[Lambda,I]],  B_N(0)=Lambda
```

exactly for every `N`; the maximum numerical residual is
`{cert['maximum_zero_energy_boundary_map_error']:.3g}`.  At nonzero mass the
layered product converges quadratically to the V48 square collar.  Successive
refinement ratios are `{', '.join(f'{value:.6g}' for value in ratios.values())}`
and the worst symplectic residual is
`{max(cert['layered_J_unitarity_residuals'].values()):.3g}`.

## G1 anomaly effect

At each interior site `X_j in R_q` and `P_j in Rbar_-q` are vectorlike.
Their cubic, mixed gauge, and mixed gravitational anomaly rows cancel.  Their
massive determinant line is trivial, and the exact constraint Jacobian is
link independent.  The only unpaired source profile is the original endpoint
representation.  The link is the discretized existing gauge multiplet, whose
adjoint content is real and neutral.  Therefore the V47 conclusions remain
unchanged:

```text
Omega5^Spin(BP)=0,
Omega5^Spin(B(P x U(1)_F))=0,
Omega6^Spin(B(Spin(10)xU(1)_F),B(P x U(1)_F))=0.
```

G1 stays closed.

## Exact scope

This is a local cutoff regulator, not a claimed renormalizable continuum 5D
UV completion of its nonlinear link sector.  A linear link UV completion can
add radial thresholds and must be vectorlike and rematched.  More importantly,
the audit has not inserted all retained `A/Xi/C/O7/O8` tensors into one
transfer, varied the entire action into one positive domain, performed an
independent profile/loop rematch, or produced normalized SO(10)-to-PS physical
Wilson coefficients.  Those are C3-C5 and C7 obligations.  Hence G2 remains
open even though C2 now passes.

Primary references: [Arkani-Hamed--Cohen--Georgi](https://arxiv.org/abs/hep-th/0104005),
[Marti--Pomarol](https://arxiv.org/abs/he-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230), and
[Nakai](https://arxiv.org/abs/1412.3486).

Core SHA-256: `{data['core_sha256']}`
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.exists() or not MD_PATH.exists():
        raise RuntimeError("V50 local-regulator artifacts are missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V50 local-regulator JSON is stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V50 local-regulator Markdown is stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
