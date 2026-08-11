#!/usr/bin/env python3
"""Global real Phi self-zero classification as the signed Kahler-square cone.

Let ``q54`` and ``q4125`` be the two live quadratic pair-Casimir residuals
for ``Phi in Lambda^4(R^10)``.  This theorem composes three frozen global
identities with compact subgroup rigidity and proves

    {Phi real : q54(Phi)=q4125(Phi)=0}
      = {0} union R_{>0} SO(10).F union R_{>0} SO(10).(-F),

where

    F = (1/2) omega wedge omega,
    omega=e01+e23+e45+e67+e89,
    ||F||^2=10.

Equivalently, at ``||Phi||^2=10`` the zero locus is exactly
``SO(10).F union SO(10).(-F)``.

Algebraic chain
---------------
The degree-eight conductor gives ``D=0``.  The cubic Cauchy bridge gives
``C=5I3^2-18N^3 <= 0``.  The global sextic syzygy gives
``C=(35/1536)S >= 0``, where

    S=tr(G (G-6NI/5)^2),   G=O_Phi^T O_Phi >= 0.

Thus ``C=S=0``.  For ``N>0``, positivity and ``tr G=24N`` force
``spec(G)={0^(25),(6N/5)^(20)}``.  Hence the identity component of the
stabilizer has dimension 25.

Rigidity dependency
-------------------
The final group-theoretic step uses the classical Dynkin classification of
connected maximal proper subgroups of SO(10), with the elementary recursive
dimension eliminations in SO(9) and SO(8) recorded in the certificate.  It
forces a connected 25-dimensional stabilizer to be conjugate to U(5).
Finally ``(Lambda^4 R^10)^U(5)`` is one-dimensional, spanned by
``omega^2/2``: after complexification the center forces bidegree (2,2), and
Schur's lemma gives the scalar in
``Lambda^2 C^5 tensor Lambda^2(C^5)^*``.

This closes the global zero-locus classification, but not G3.  The projector
zero is non-Morse--Bott: its quadratic kernel has ten transverse directions
in addition to the orbit-cone tangent.  A quantitative quartic
projector-residual versus orbit-distance estimate, and its global operator
integration, remain separate requirements.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE
for source in (HERE, REPO):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

import exact_210_self_invariant_basis_v20 as invariants
import exact_phisigma_casimir_projectors_v20 as projectors
import exact_phi_self_zero_global_sextic_syzygy_v20 as sextic
import exact_phi_zero_cubic_cauchy_bridge_v20 as cubic_bridge
import exact_phi_zero_degree8_conductor_identity_v20 as conductor


STATUS = "EXACT_GLOBAL_REAL_PHI_SELF_ZERO_IS_SIGNED_KAEHLER_CONE__G3_OPEN"
EXPECTED_CORE_SHA256 = "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
FROZEN_SOURCE_SHA256 = {
    HERE / "FROZEN_PHI_SELF_ZERO_GLOBAL_SIGNED_KAEHLER_CLASSIFICATION_SOURCE_V20.py": (
        "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
    ),
    HERE / "FROZEN_PHI_ZERO_DEGREE8_CONDUCTOR_IDENTITY_SOURCE_V20.py": (
        "92c5b244daa40ec423c6292f3816f6c87395ce31fe7aebe73dd264a5596f44df"
    ),
    HERE / "FROZEN_PHI_ZERO_CUBIC_CAUCHY_BRIDGE_SOURCE_V20.py": (
        "01b1bb5f450521506bf6a025650629691ce738325d1f16c5aafc050abe34e1c7"
    ),
    HERE / "FROZEN_PHI_SELF_ZERO_GLOBAL_SEXTIC_SYZYGY_SOURCE_V20.py": (
        "0ad2c69915d0b758342d68c568c9d29c5bd80c0e39c0ab686824eba1a1350a8c"
    ),
}
EXPECTED_DEPENDENCIES = {
    HERE / "exact_phi_zero_degree8_conductor_identity_v20.py": (
        "d8587194b647a49f2b9950aebb920ee7a3c7f28f9f0823d8257676fe70e81fd9"
    ),
    HERE / "exact_phi_zero_cubic_cauchy_bridge_v20.py": (
        "282307be1abfe6d8d59c4e63861dbd5f8b4cf01d488d5df8793c27e029060bb0"
    ),
    HERE / "exact_phi_self_zero_global_sextic_syzygy_v20.py": (
        "5de73274c9def8bbc9628895457065fb1a93536eb611288dd66ffa6e1f8b2766"
    ),
    REPO / "exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py": (
        "48fe7cb8b5f903a786622a6c805542b288efcab9a4fa38df0c7af5249705343a"
    ),
    REPO / "exact_210_self_invariant_basis_v20.py": (
        "e905911f3589a78fb0c510060ca0ff6997d0963305c48f91f7a37cccbcfb4772"
    ),
    HERE / "FROZEN_SIGNED_KAEHLER_FULL126_PHYSICAL_SUBTRACTION_SOURCE_V20.py": (
        "911f9566cbdc957e2ec8bbf90f6d3546505a03e1bd76d66d85267a0536066c1a"
    ),
    HERE / "FROZEN_EXACT_SIGNED_KAEHLER_FULL126_STRONG_OPERATOR_SOURCE_V20.py": (
        "c7ad27cc1566e743f762f675dabfcfb0ccc499c8acf5c5956c2bf768a90eb771"
    ),
    HERE / "FROZEN_SIGNED_KAEHLER_P0_FULL126_KERNEL_RADIAL_STRICTNESS_SOURCE_V20.py": (
        "73819bb79be24a1cc2234c87b90bfb4bc2029e00c41fdedfa491bb89b9f06c4f"
    ),
}

TWO_INDICES = tuple(itertools.combinations(range(10), 2))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _rank_mod(matrix: np.ndarray, prime: int) -> int:
    work = np.asarray(matrix, dtype=np.int64).copy() % prime
    row = 0
    for column in range(work.shape[1]):
        candidates = np.flatnonzero(work[row:, column])
        if not candidates.size:
            continue
        pivot = row + int(candidates[0])
        work[[row, pivot]] = work[[pivot, row]]
        work[row] = work[row] * pow(int(work[row, column]), -1, prime) % prime
        for target in range(work.shape[0]):
            if target != row and work[target, column]:
                work[target] = (
                    work[target] - work[target, column] * work[row]
                ) % prime
        row += 1
        if row == work.shape[0]:
            break
    return row


def _kahler_square_vector() -> np.ndarray:
    vector = np.zeros(210, dtype=np.int64)
    planes = ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))
    index = {indices: position for position, indices in enumerate(projectors.FOUR_INDICES)}
    for left, right in itertools.combinations(planes, 2):
        vector[index[tuple(sorted(left + right))]] = 1
    return vector


def _four_form_operator(vector: np.ndarray) -> np.ndarray:
    matrix = np.zeros((45, 45), dtype=np.int64)
    index = {indices: position for position, indices in enumerate(projectors.FOUR_INDICES)}
    for row, left in enumerate(TWO_INDICES):
        for column, right in enumerate(TWO_INDICES):
            if set(left).intersection(right):
                continue
            sequence = left + right
            inversions = sum(
                sequence[i] > sequence[j]
                for i in range(4)
                for j in range(i + 1, 4)
            )
            matrix[row, column] = (
                -1 if inversions & 1 else 1
            ) * vector[index[tuple(sorted(sequence))]]
    return matrix


def _representative_report() -> dict[str, Any]:
    vector = _kahler_square_vector()
    norm = int(vector @ vector)
    operator = _four_form_operator(vector)
    cubic = int(np.trace((operator @ operator) @ operator))
    orbit = np.column_stack(
        [generator @ vector for generator in invariants.integer_generators()]
    ).astype(np.int64)
    gram = orbit.T @ orbit
    shifted_residual = gram @ (gram - 12 * np.eye(45, dtype=np.int64))
    rank = _rank_mod(gram, 1_000_003)
    if not (
        norm == 10
        and cubic == 60
        and int(np.trace(gram)) == 240
        and rank == 20
        and np.count_nonzero(shifted_residual) == 0
    ):
        raise ArithmeticError("signed Kahler representative normalization drift")
    return {
        "definition": "F=(1/2)omega wedge omega, omega=e01+e23+e45+e67+e89",
        "norm_squared": norm,
        "I3_plus": cubic,
        "I3_minus": -cubic,
        "orbit_Gram_polynomial": "G(G-12I)=0",
        "orbit_Gram_trace": int(np.trace(gram)),
        "orbit_Gram_rank": rank,
        "orbit_Gram_spectrum": "0^25,12^20",
        "exact_residual_projectors_at_signed_representatives": (
            "SU4 formula at (a,b,c)=(1,1,0) and (-1,-1,0)"
        ),
    }


def _subgroup_rigidity_report() -> dict[str, Any]:
    # Dimensions used in the Dynkin maximal-subgroup elimination.
    block_dimensions = {
        "SO1xSO9": 36,
        "SO2xSO8": 29,
        "SO3xSO7": 24,
        "SO4xSO6": 21,
        "SO5xSO5": 20,
    }
    if block_dimensions != {
        f"SO{r}xSO{10-r}": r * (r - 1) // 2 + (10 - r) * (9 - r) // 2
        for r in range(1, 6)
    }:
        raise ArithmeticError("block subgroup dimension drift")
    return {
        "external_classification": (
            "Dynkin classification of connected maximal proper subgroups of "
            "SO(10), with the corresponding SO(9) and SO(8) lists"
        ),
        "primary_reference": (
            "E. B. Dynkin, Maximal subgroups of the classical groups, Trudy "
            "Moskov. Mat. Obshch. 1 (1952), 39-166; AMS Transl. Ser. 2, 6 "
            "(1957), 245-378"
        ),
        "SO10_block_dimensions": block_dimensions,
        "unitary_maximal": {"name": "U(5)", "dimension": 25},
        "SO2xSO8_elimination": (
            "the kernel of H->SO(2) lies in SO(8) and has dimension at "
            "least24, but a proper connected subgroup of SO8 has dimension "
            "at most21"
        ),
        "SO9_elimination": (
            "the full SO9 maximal list leaves only SO8 (dimension28) above "
            "dimension24; inside it H is proper and the SO8 proper connected "
            "maximum is21"
        ),
        "other_blocks": "dimension at most24",
        "simple_absolutely_irreducible_elimination": (
            "the Dynkin list has no proper simple group of dimension >=25 "
            "with a faithful absolutely irreducible real 10D representation"
        ),
        "conclusion": "every connected 25D proper subgroup is conjugate to U(5)",
        "fixed_line_argument": (
            "center weight p-q forces (p,q)=(2,2); Schur on irreducible "
            "Lambda^2(C^5) gives dimension one"
        ),
        "fixed_line": "(Lambda^4 R^10)^U5 = R*(omega^2/2)",
    }


@lru_cache(maxsize=1)
def certificate() -> dict[str, Any]:
    for path, expected in FROZEN_SOURCE_SHA256.items():
        observed = _sha256(path)
        if observed != expected:
            raise ArithmeticError(
                f"frozen source hash drift: {path.name}: {observed}"
            )
    for path, expected in EXPECTED_DEPENDENCIES.items():
        observed = _sha256(path)
        if observed != expected:
            raise ArithmeticError(f"dependency hash drift: {path.name}: {observed}")
    if conductor.EXPECTED_CORE_SHA256 != (
        "3763506628c0aac91fc54fdd1b49f6cdb12114707a13f2359ba3acc2b4836142"
    ):
        raise ArithmeticError("conductor core drift")
    if cubic_bridge.EXPECTED_CORE_SHA256 != (
        "fd32a3fe3ae6dfe537c14f9824c96d829ab6d7a80e57d87c21f93db6f06d1d07"
    ):
        raise ArithmeticError("cubic bridge core drift")
    if sextic.EXPECTED_CORE_SHA256 != (
        "18aa95ddbbdccb4852ccac256310c5d8992eb84d6594ab0a2231afd83beb0955"
    ):
        raise ArithmeticError("sextic core drift")

    conductor_report = conductor.certificate()
    if conductor_report["core_sha256"] != conductor.EXPECTED_CORE_SHA256:
        raise ArithmeticError("live conductor certificate drift")
    for label, report in (
        ("cubic bridge", cubic_bridge.build_report()),
        ("sextic syzygy", sextic.build_report()),
    ):
        binding = report["source_binding"]
        if (
            report["n_failed"]
            or not all(binding["dependency_checks"].values())
            or not binding["core_hash_matches"]
        ):
            raise ArithmeticError(f"live {label} certificate drift")

    representative = _representative_report()
    rigidity = _subgroup_rigidity_report()
    payload = {
        "status": STATUS,
        "zero_case": "N=0 implies Phi=0 for real Phi",
        "positive_norm_chain": [
            "conductor: q54=q4125=0 implies D=0",
            "cubic Cauchy: C=5I3^2-18N^3 <= 0 when D=0",
            "sextic syzygy: C=(35/1536)S >= 0 when q=0,D=0",
            "therefore C=S=0",
            "PSD G, trG=24N: spec G=0^25,(6N/5)^20",
            "stabilizer identity component has dimension25",
            "the stabilizer is proper because Lambda^4(R^10) has no SO10-fixed line",
            "Dynkin rigidity forces U5; its Lambda4 fixed space is R*(omega^2/2)",
        ],
        "representative": representative,
        "subgroup_rigidity": rigidity,
        "global_real_zero_cone": (
            "{0} union {r*g.F:r>0,g in SO10} union "
            "{r*g.(-F):r>0,g in SO10}"
        ),
        "norm10_zero_locus": "SO(10).F union SO(10).(-F)",
        "sheet_separator": "I3=+60 on F and -60 on -F at N=10",
        "converse": (
            "the signed representatives have q54=q4125=0 by the frozen exact "
            "SU4 formulas; equivariance and homogeneity give both cones"
        ),
        "bound_signed_orbit_operator_corollary": {
            "physical_subtraction_core": (
                "b18b4f2ce41c31b0119196ff131a083fcec6289d762b8c8c72b4092affd23db2"
            ),
            "meaning": (
                "all nonzero Phi self-zero points are exactly the already "
                "certified physically safe signed orbit points"
            ),
        },
        "quantitative_warning": {
            "Morse_Bott": False,
            "linearized_source_sha256": (
                "48fe7cb8b5f903a786622a6c805542b288efcab9a4fa38df0c7af5249705343a"
            ),
            "orbit_cone_tangent_dimension": 21,
            "projector_quadratic_kernel_dimension": 31,
            "transverse_quadratic_kernel_dimension": 10,
            "required_local_exponent": "quartic in the ten conductor directions",
            "missing_G3_lemma": (
                "an explicit global P-to-distance bound reaching the signed "
                "orbit strong-operator tube, plus complement operator control"
            ),
        },
        "scope": {
            "global_real_zero_locus_classified": True,
            "signed_zero_boundary_operator_safe": True,
            "quantitative_orbit_distance_bound": False,
            "G3_closed": False,
            "G4_closed": False,
        },
    }
    payload["core_sha256"] = _canonical_sha256(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    arguments = parser.parse_args()
    payload = certificate()
    if not arguments.allow_unfrozen and payload["core_sha256"] != EXPECTED_CORE_SHA256:
        raise ArithmeticError(
            f"core hash drift: {payload['core_sha256']} != {EXPECTED_CORE_SHA256}"
        )
    if arguments.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(STATUS)
        print("norm10 zero locus", payload["norm10_zero_locus"])
        print("G3_closed", payload["scope"]["G3_closed"])
        print("core_sha256", payload["core_sha256"])


if __name__ == "__main__":
    main()
