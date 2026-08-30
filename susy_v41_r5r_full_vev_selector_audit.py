#!/usr/bin/env python3
"""Fail-closed V41 all-visible-VEV Z_N^R/type-I selector no-go.

This is deliberately a *source-boundary* calculation.  It asks whether the
smallest Pati--Salam rebuild can simultaneously do three things:

* retain the V39 type-I source ``Sbc Qc Nv + Nv Nv / 2``;
* leave a nontrivial R selector unbroken by every visible scalar VEV,
  including the electroweak bidoublet; and
* have the conventional equal-level, single-axion discrete-R Green--Schwarz
  anomaly arithmetic.

The answer is no for every Z_N^R order.  The program enumerates N=3..96 as a
transparent finite check and also records the order-independent divisibility
proof.  It does *not* turn a formal multi-axion Wess--Zumino counterterm into
a claimed UV completion.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from math import gcd
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
OUTPUT_JSON = ROOT / "SUSY_V41_FULL_VEV_RSYM_NO_GO_AUDIT.json"
OUTPUT_MD = ROOT / "SUSY_V41_FULL_VEV_RSYM_NO_GO_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v41_r5r_full_vev_selector_audit.py"

W_R = 2
SCAN_MIN = 3
SCAN_MAX = 96
STATUS = (
    "V41_ALL_VISIBLE_VEV_ZNR_TYPE_I_SELECTOR_NO_GO__"
    "EQUAL_LEVEL_SINGLE_GS_IMPOSSIBLE_AT_EVERY_PROTECTIVE_ORDER__"
    "MULTI_AXION_OR_NONDECOUPLING_EXOTIC_ESCAPE_REQUIRES_NEW_UV_INPUT__"
    "NO_GATE_PROMOTED"
)


# ``index`` is 2T(R), already multiplied by spectator gauge dimensions and
# family multiplicity.  It is the same doubled-Dynkin convention used by the
# V39/V40 audits.  The table is a minimal rebuilt visible source: the old
# driver, PS/PQ, split-six, Yukawa/mixing, and type-I ingredients are retained
# only when needed for the question at hand.
REPRESENTATIVE_ORDER = 5
FIELDS_R5: dict[str, dict[str, Any]] = {
    "H": {"r": 0, "dim": 4, "index": {"SU2L": 2, "SU2R": 2}},
    "Q": {"r": 1, "dim": 24, "index": {"SU4": 6, "SU2L": 12}},
    "Qc": {"r": 1, "dim": 24, "index": {"SU4": 6, "SU2R": 12}},
    "X": {"r": 2, "dim": 1, "index": {}},
    "Zp": {"r": 2, "dim": 1, "index": {}},
    "Sc": {"r": 0, "dim": 8, "index": {"SU4": 2, "SU2R": 4}},
    "Sbc": {"r": 0, "dim": 8, "index": {"SU4": 2, "SU2R": 4}},
    "SigC": {"r": 2, "dim": 6, "index": {"SU4": 2}},
    "SigBc": {"r": 2, "dim": 6, "index": {"SU4": 2}},
    "PsiBar": {"r": 1, "dim": 8, "index": {"SU4": 2, "SU2L": 4}},
    "Psi": {"r": 1, "dim": 8, "index": {"SU4": 2, "SU2L": 4}},
    "PsiC": {"r": 1, "dim": 8, "index": {"SU4": 2, "SU2R": 4}},
    "PsiCBar": {"r": 1, "dim": 8, "index": {"SU4": 2, "SU2R": 4}},
    "P": {"r": 0, "dim": 1, "index": {}},
    "Pb": {"r": 0, "dim": 1, "index": {}},
    "Nv": {"r": 1, "dim": 3, "index": {}},
    # The old PQ anomalon sector is retained only as neutral-under-R singlet
    # bookkeeping.  Its Z5610/PQ completion is not claimed here.
    "A2": {"r": 1, "dim": 1, "index": {}},
    "A32": {"r": 1, "dim": 1, "index": {}},
    "A15": {"r": 1, "dim": 1, "index": {}},
    "A17": {"r": 1, "dim": 1, "index": {}},
    "A16": {"r": 1, "dim": 1, "index": {}},
}
GAUGINO_DOUBLED_INDEX = {"SU4": 8, "SU2L": 4, "SU2R": 4}
PS_GROUPS = tuple(GAUGINO_DOUBLED_INDEX)

# These are every scalar expectation value required by the explicitly written
# visible vacuum.  X, Zp, SigC, SigBc and all matter/exotics are required to
# have zero scalar VEV on this branch.
VISIBLE_VEVS = ("H", "Sc", "Sbc", "P", "Pb")
ZERO_VEV_FIELDS = ("X", "Zp", "SigC", "SigBc", "Q", "Qc", "Nv")

REBUILT_W: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("X_linear_PS", ("X",)),
    ("X_Sbc_Sc", ("X", "Sbc", "Sc")),
    ("X_H_H", ("X", "H", "H")),
    ("Zp_linear_PQ", ("Zp",)),
    ("Zp_P_Pb", ("Zp", "P", "Pb")),
    ("Sc_Sc_SigC", ("Sc", "Sc", "SigC")),
    ("Sbc_Sbc_SigBc", ("Sbc", "Sbc", "SigBc")),
    ("Q_H_Qc", ("Q", "H", "Qc")),
    ("Q_H_PsiC", ("Q", "H", "PsiC")),
    ("Psi_H_Qc", ("Psi", "H", "Qc")),
    ("Psi_H_PsiC", ("Psi", "H", "PsiC")),
    ("P_PsiBar_Q", ("P", "PsiBar", "Q")),
    ("P_PsiBar_Psi", ("P", "PsiBar", "Psi")),
    ("P_PsiCBar_Qc", ("P", "PsiCBar", "Qc")),
    ("P_PsiCBar_PsiC", ("P", "PsiCBar", "PsiC")),
    ("type_I_Sbc_Qc_Nv", ("Sbc", "Qc", "Nv")),
    ("type_I_Majorana_Nv_Nv", ("Nv", "Nv")),
    ("Pb_A2_A32", ("Pb", "A2", "A32")),
    ("P_A15_A17", ("P", "A15", "A17")),
    ("P_A16_A16", ("P", "A16", "A16")),
)


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def r_charge(fields: Iterable[str], order: int = REPRESENTATIVE_ORDER) -> int:
    return sum(int(FIELDS_R5[name]["r"]) for name in fields) % order


def eta(order: int) -> int:
    """The conventional discrete-R modulus: N for odd N, N/2 for even N."""
    return order if order % 2 else order // 2


def roots_of_type_i_majorana(order: int) -> list[int]:
    """Enumerate r(Nv) satisfying 2 r(Nv)=2 modulo N."""
    return [value for value in range(order) if (2 * value - W_R) % order == 0]


def lifted_branch(order: int, n_charge: int) -> dict[str, int]:
    """A signed lift of all charges imposed by the rebuilt W.

    The signed Qc lift is intentional.  It makes anomaly cancellation between
    vectorlike partners algebraically visible; replacing it by a canonical
    0..N-1 representative only shifts anomaly rows by conventional lattice
    multiples and cannot repair the no-go below.
    """
    q = n_charge
    qc = W_R - q
    return {
        "H": 0,
        "Sc": 0,
        "Sbc": 0,
        "P": 0,
        "Pb": 0,
        "X": W_R,
        "Zp": W_R,
        "SigC": W_R,
        "SigBc": W_R,
        "Nv": n_charge,
        "Q": q,
        "Qc": qc,
        "Psi": q,
        "PsiCBar": q,
        "PsiBar": qc,
        "PsiC": qc,
    }


def doubled_core_rows(order: int, n_charge: int) -> dict[str, int]:
    """2A^R for the core field content, in an exact signed-charge lift."""
    q = n_charge
    return {
        "SU4": 8,
        "SU2L": 12 * (q - 1) + 2,
        "SU2R": 12 * (1 - q) - 6,
    }


def equal_level_single_gs(doubled_rows: Mapping[str, int], order: int) -> bool:
    """Test the usual equal-level one-axion universality in 2A notation.

    The test uses equality modulo 2 eta so that it is exactly equivalent to
    equality of A=2A/2 modulo eta whenever the rows are integral.  A second,
    weaker doubled-row convention is also reported in ``enumerate_orders``;
    neither admits a protective solution.
    """
    modulus = 2 * eta(order)
    values = list(doubled_rows.values())
    return all((value - values[0]) % modulus == 0 for value in values[1:])


def protected_sources(order: int, charges: Mapping[str, int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for driver in ("X", "Zp"):
        for matter in ("Q", "Qc"):
            value = (charges[driver] + 4 * charges[matter]) % order
            rows.append({
                "operator": f"{driver} {matter}^4",
                "R_N": value,
                "W_target": W_R % order,
                "forbidden": value != W_R % order,
            })
    return rows


def enumerate_orders() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for order in range(SCAN_MIN, SCAN_MAX + 1):
        for n_charge in roots_of_type_i_majorana(order):
            charges = lifted_branch(order, n_charge)
            sources = protected_sources(order, charges)
            doubled = doubled_core_rows(order, n_charge)
            weak_modulus = eta(order)
            values = list(doubled.values())
            weaker_doubled_test = all(
                (value - values[0]) % weak_modulus == 0 for value in values[1:]
            )
            rows.append({
                "N": order,
                "eta": weak_modulus,
                "rNv_canonical": n_charge,
                "rQ_lift": charges["Q"],
                "rQc_lift": charges["Qc"],
                "all_required_W_equations_hold": (
                    (charges["Q"] + charges["H"] + charges["Qc"] - W_R) % order == 0
                    and (charges["Sbc"] + charges["Qc"] + charges["Nv"] - W_R) % order == 0
                    and (2 * charges["Nv"] - W_R) % order == 0
                ),
                "all_same_orientation_sources_blocked": all(row["forbidden"] for row in sources),
                "source_rows": sources,
                "core_doubled_rows": doubled,
                "equal_level_single_GS_standard_A_convention": equal_level_single_gs(doubled, order),
                "weaker_doubled_row_mod_eta_convention": weaker_doubled_test,
            })
    protected = [row for row in rows if row["all_same_orientation_sources_blocked"]]
    return {
        "range": [SCAN_MIN, SCAN_MAX],
        "branch_count": len(rows),
        "all_type_I_equations_hold": all(row["all_required_W_equations_hold"] for row in rows),
        "protective_branch_count": len(protected),
        "protective_and_standard_single_GS_count": sum(
            row["all_same_orientation_sources_blocked"] and row["equal_level_single_GS_standard_A_convention"]
            for row in rows
        ),
        "protective_and_even_weaker_doubled_GS_count": sum(
            row["all_same_orientation_sources_blocked"] and row["weaker_doubled_row_mod_eta_convention"]
            for row in rows
        ),
        "rows": rows,
    }


def representative_term_audit() -> dict[str, Any]:
    rows = [
        {"label": label, "fields": list(fields), "R5": r_charge(fields)}
        for label, fields in REBUILT_W
    ]
    forbidden = {
        "X_cubic": ("X", "X", "X"),
        "Zp_cubic": ("Zp", "Zp", "Zp"),
        "X_SigC_SigBc": ("X", "SigC", "SigBc"),
        "Zp_SigC_SigBc": ("Zp", "SigC", "SigBc"),
    }
    return {
        "representative_order": REPRESENTATIVE_ORDER,
        "charges": {name: int(row["r"]) for name, row in FIELDS_R5.items()},
        "required_terms": rows,
        "all_required_terms_allowed": all(row["R5"] == W_R for row in rows),
        "intentionally_absent_terms": {
            label: {"R5": r_charge(fields), "forbidden": r_charge(fields) != W_R}
            for label, fields in forbidden.items()
        },
        "type_I_mechanism": {
            "source": "y_N Sbc Qc Nv + M_N Nv Nv / 2",
            "after_PS_breaking": "<Sbc> mixes the right-handed neutrino in Qc with Nv; Nv has an explicit Majorana mass.",
            "claim_boundary": "A numerical neutrino/flavour fit is not supplied.",
        },
        "rebuilt_visible_superpotential": (
            "W = X(kappa_PS Sbc.Sc - mu_PS^2 + lambda_H H.H) "
            "+ Zp(kappa_PQ P.Pb - mu_PQ^2) + lambda_c Sc.Sc.SigC/2 "
            "+ lambda_b Sbc.Sbc.SigBc/2 + W_Yukawa+mix + y_N Sbc.Qc.Nv "
            "+ M_N Nv.Nv/2 + W_PQ-anomalon."
        ),
    }


def all_visible_vev_proof() -> dict[str, Any]:
    vev_charges = {name: int(FIELDS_R5[name]["r"]) for name in VISIBLE_VEVS}
    sources = protected_sources(REPRESENTATIVE_ORDER, {name: int(row["r"]) for name, row in FIELDS_R5.items()})
    hh = []
    for driver in ("X", "Zp"):
        for matter in ("Q", "Qc"):
            source = r_charge((driver,) + (matter,) * 4)
            hh.append({
                "operator_family": f"{driver} {matter}^4 (H.H)^k",
                "R5_for_every_integer_k": source,
                "forbidden_for_every_k": source != W_R,
            })
    four_fundamental = ("Q", "Psi", "PsiCBar")
    four_antifundamental = ("Qc", "PsiBar", "PsiC")
    return {
        "nonzero_visible_VEVs": list(VISIBLE_VEVS),
        "zero_scalar_VEVs_required": list(ZERO_VEV_FIELDS),
        "R5_of_nonzero_visible_VEVs": vev_charges,
        "residual_R5_stabilizer_order": gcd(REPRESENTATIVE_ORDER, *vev_charges.values()),
        "every_visible_VEV_and_conjugate_is_R5_neutral": all(value == 0 for value in vev_charges.values()),
        "canonical_F_D_flat_branch": [
            "<Sbc.Sc>=mu_PS^2/kappa_PS and equal-conjugate PS D-flat magnitudes",
            "<P.Pb>=mu_PQ^2/kappa_PQ",
            "<X>=<Zp>=<SigC>=<SigBc>=0",
            "<H> is allowed later by electroweak breaking and has R5=0",
            "the rank-one Sc.Sc and Sbc.Sbc antisymmetric-six contractions vanish on the canonical PS branch",
        ],
        "local_driver_sources": sources,
        "all_local_sources_forbidden": all(row["forbidden"] for row in sources),
        "all_order_VEV_dressing_proof": (
            "Every declared scalar VEV and its conjugate has R5=0.  Thus any arbitrary "
            "holomorphic/Kahler VEV dressing adds zero to the source charge.  Each X/Zp Q^4 "
            "or X/Zp Qc^4 source has R5=2+4=1, not W charge two."
        ),
        "electroweak_HH_dressing_test": hh,
        "same_orientation_vectorlike_extension": {
            "SU4_fundamental_matter": list(four_fundamental),
            "SU4_antifundamental_matter": list(four_antifundamental),
            "all_these_matter_fields_have_R5": 1,
            "driver_plus_any_four_has_R5": 1,
            "scope": "This extends only the same-orientation four-matter selector statement; it does not classify mixed-orientation or component operators.",
        },
        "Kahler_direct_check": {
            "X_Q4": r_charge(("X", "Q", "Q", "Q", "Q")),
            "Xdag_Q4": (-int(FIELDS_R5["X"]["r"]) + 4 * int(FIELDS_R5["Q"]["r"])) % REPRESENTATIVE_ORDER,
            "Kahler_target": 0,
            "both_forbidden": True,
            "qualification": "Derivative, soft, mixed-orientation, and full component operator classifications are not completed.",
        },
    }


def direct_core_anomaly() -> dict[str, Any]:
    rows = doubled_core_rows(REPRESENTATIVE_ORDER, 1)
    standard = {group: value // 2 for group, value in rows.items()}
    modulus = eta(REPRESENTATIVE_ORDER)
    gravity = sum(int(row["dim"]) * (int(row["r"]) - 1) for row in FIELDS_R5.values())
    return {
        "convention": (
            "D_G=2 A_G^R=sum_i (2T_G(R_i))(r_i-1)+2C_2(G).  "
            "The standard equal-level one-axion test is equality of A_G^R modulo eta."
        ),
        "eta": modulus,
        "core_doubled_rows_D": rows,
        "core_standard_A": standard,
        "core_standard_A_mod_eta": {group: value % modulus for group, value in standard.items()},
        "equal_level_single_GS_universal": equal_level_single_gs(rows, REPRESENTATIVE_ORDER),
        "gravity_A_PS_bookkeeping": gravity,
        "gravity_A_mod_eta": gravity % modulus,
        "Witten_doublet_counts": {"SU2L": 22, "SU2R": 30},
        "Witten_parities_even": True,
        "meaning": (
            "The R5 operator witness is not an anomaly-complete equal-level one-axion discrete-R gauge symmetry."
        ),
    }


def analytic_no_go() -> dict[str, Any]:
    return {
        "assumptions": [
            "all visible PS/PQ/electroweak VEVs have residual R charge zero",
            "X and Zp are ordinary neutral-product drivers, hence r(X)=r(Zp)=2",
            "Q H Qc, Sbc Qc Nv, and Nv Nv are present",
            "Sc.Sc.SigC and Sbc.Sbc.SigBc retain the split-six source, hence r(SigC)=r(SigBc)=2",
            "P-induced vectorlike mixing terms are present",
            "equal Pati--Salam affine levels and one universal GS axion are required",
        ],
        "charge_reduction": [
            "2 r(Nv)=2; for odd N this gives r(Nv)=1, and for even N there is also the N/2-shifted lift.",
            "r(Qc)=2-r(Nv), r(Q)=r(Nv), while vectorlike partners pair into the same signed lifts.",
            "The sources differ from W charge by 4 r(Q) and 4 r(Qc); a protective residual order cannot divide four.",
        ],
        "core_doubled_anomaly_formula": {
            "SU4": "8",
            "SU2L": "12 (r(Q)-1)+2",
            "SU2R": "12 (1-r(Q))-6",
        },
        "divisibility_obstruction": {
            "doubled_row_differences_mod_eta": [
                "D_SU4-D_SU2L = 6-12(r(Q)-1)",
                "D_SU4-D_SU2R = 14+12(r(Q)-1)",
            ],
            "necessary_condition_in_the_weaker_doubled_row_convention": "eta divides both 6 and 14, hence eta divides 2.",
            "consequence": (
                "No residual order able to forbid four same-charge matter fields (order not dividing four) can pass.  "
                "The standard A_G convention is at least as restrictive."
            ),
        },
        "result": "No minimal all-visible-VEV, type-I, equal-level single-GS Z_N^R architecture exists for any N.",
    }


def escape_boundary() -> dict[str, Any]:
    return {
        "massive_exotic_threshold_no_repair": {
            "statement": (
                "A vectorlike PS-charged pair made massive using only residual-R-neutral VEVs obeys r(F)+r(Fbar)=2. "
                "Its contribution (r(F)-1)+(r(Fbar)-1) to every doubled R-anomaly row vanishes modulo the residual order."
            ),
            "consequence": (
                "Ordinary decoupling anomaly exotics cannot repair the nonuniversal core mismatch while keeping the all-VEV protector exact."
            ),
        },
        "nondecoupling_exotic_escape": {
            "required_new_input": (
                "PS-charged states whose mass is not generated on the protected branch, plus a complete threshold/spectrum construction."
            ),
            "why_not_a_solution_here": "Such states are not in the reconstructed spectrum and would be mass-gap/open-spectrum data, not a closure.",
        },
        "multi_axion_or_nonuniversal_WZ_escape": {
            "required_integer_equations": (
                "For axions a with Z_N^R shifts delta_a and quantized Wess--Zumino levels k_aG, "
                "A_G + sum_a delta_a k_aG = 0 (mod eta), together with the gravitational and product-symmetry rows."
            ),
            "R5_core_residue_target": {"SU4": 4, "SU2L": 1, "SU2R": 2, "gravity": 2},
            "formal_mod5_counterterm_witness": {
                "convention": "all four formal axion shifts delta=1; levels are the negatives of the listed core residues",
                "k_a_SU4": 1,
                "k_a_SU2L": 4,
                "k_a_SU2R": 3,
                "k_a_gravity": 3,
            },
            "why_not_a_solution_here": (
                "No quantized axion-period lattice, kinetic/gauge-coupling realization, Z5610 product anomaly cancellation, "
                "or Spin/bordism calculation is supplied.  The arithmetic witness is only a list of required UV data."
            ),
        },
    }


def build_report() -> dict[str, Any]:
    scan = enumerate_orders()
    report: dict[str, Any] = {
        "schema": "susy-v41-full-visible-vev-rsym-no-go-v1",
        "status": STATUS,
        "scope": (
            "A fail-closed discrete-R source/symmetry audit.  It is not an active SARAH model, "
            "a complete UV completion, a soft/spectrum solution, or a proton-decay computation."
        ),
        "representative_R5_operator_witness": representative_term_audit(),
        "all_visible_VEV_protection": all_visible_vev_proof(),
        "R5_core_anomaly": direct_core_anomaly(),
        "exhaustive_N3_to_N96_enumeration": scan,
        "order_independent_no_go": analytic_no_go(),
        "escape_requirements_not_claimed": escape_boundary(),
        "decision": {
            "type_I_source_present_in_operator_witness": True,
            "all_declared_visible_VEV_same_orientation_source_block": True,
            "equal_level_single_GS_discrete_R_completion_found": False,
            "complete_new_physics_found": False,
            "gates_promoted": [],
        },
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(data: Mapping[str, Any]) -> str:
    terms = data["representative_R5_operator_witness"]
    vevs = data["all_visible_VEV_protection"]
    anomaly = data["R5_core_anomaly"]
    scan = data["exhaustive_N3_to_N96_enumeration"]
    return "\n".join([
        "# V41 full-visible-VEV discrete-R no-go audit",
        "",
        f"Status: `{data['status']}`",
        "",
        "## Outcome",
        "",
        "A clean Z5R operator witness exists: it keeps the type-I source, leaves PS, PQ and electroweak VEVs R-neutral, and forbids every same-orientation X/Zp Q4/Qc4 source even after arbitrary visible-VEV or H.H dressing. It is not a viable discrete gauge-R completion because its equal-level one-axion Pati--Salam anomaly rows are nonuniversal. Exhaustive Z_N^R enumeration and an analytic divisibility proof show that this is not repaired by choosing another order.",
        "",
        "## Rebuilt source and visible vacuum",
        "",
        f"All {len(terms['required_terms'])} required rebuilt-W terms have R5=2: `{terms['all_required_terms_allowed']}`. The Majorana path is `{terms['type_I_mechanism']['source']}`.",
        "",
        f"The only nonzero visible scalar VEVs are `{vevs['nonzero_visible_VEVs']}`, all R5-neutral. Each local driver source has R5 `{[(x['operator'], x['R_N']) for x in vevs['local_driver_sources']]}`. Hence every H.H-dressed family remains R5=1 rather than W charge two.",
        "",
        "## Exhaustive charge result",
        "",
        f"The N={scan['range'][0]}..{scan['range'][1]} scan checks {scan['branch_count']} Majorana roots. It finds {scan['protective_branch_count']} source-protective branches, but {scan['protective_and_standard_single_GS_count']} that also pass the standard equal-level single-GS condition (and {scan['protective_and_even_weaker_doubled_GS_count']} even under the weaker doubled-row convention).",
        "",
        "The analytic core rows are D=(8, 12(r(Q)-1)+2, 12(1-r(Q))-6). Their differences require eta to divide 6 and 14 already in the weaker convention, so eta can be at most two. Such a residual cannot forbid a four-matter same-charge source.",
        "",
        "## Exact boundary",
        "",
        f"For the representative R5 witness the standard anomaly rows are `{anomaly['core_standard_A']}` = `{anomaly['core_standard_A_mod_eta']}` modulo five, so conventional universality is `{anomaly['equal_level_single_GS_universal']}`. Massive vectorlike exotics fed only by R-neutral VEVs cannot change this residual mismatch. A nondecoupling exotic sector or a quantized nonuniversal/multi-axion Wess--Zumino system is new UV input, not a derived repair.",
        "",
        "This blocks promotion of G1 or G7. It does establish a sharper design constraint: an all-visible-VEV, type-I R-selector needs a genuinely specified nonminimal anomaly realization before it can be treated as physics.",
        "",
        "For discrete-R/Green--Schwarz context: [Araki et al.](https://arxiv.org/abs/0705.3075), [Hsieh](https://arxiv.org/abs/1808.02881).",
        "",
        f"Core SHA-256: `{data['core_sha256']}`",
        "",
    ])


def validate(data: Mapping[str, Any]) -> None:
    if data.get("status") != STATUS or canonical_sha(data) != data.get("core_sha256"):
        raise RuntimeError("stale V41 report")
    terms = data["representative_R5_operator_witness"]
    if not terms["all_required_terms_allowed"]:
        raise RuntimeError("rebuilt W term failed the R5 audit")
    vevs = data["all_visible_VEV_protection"]
    if not vevs["every_visible_VEV_and_conjugate_is_R5_neutral"] or not vevs["all_local_sources_forbidden"]:
        raise RuntimeError("all-VEV source protection failed")
    if not all(row["forbidden_for_every_k"] for row in vevs["electroweak_HH_dressing_test"]):
        raise RuntimeError("electroweak dressing loophole was not closed")
    scan = data["exhaustive_N3_to_N96_enumeration"]
    if not scan["all_type_I_equations_hold"] or scan["protective_and_standard_single_GS_count"] != 0:
        raise RuntimeError("enumerated no-go regression")
    if scan["protective_and_even_weaker_doubled_GS_count"] != 0:
        raise RuntimeError("weaker-convention no-go regression")
    if data["R5_core_anomaly"]["equal_level_single_GS_universal"]:
        raise RuntimeError("invalid R5 anomaly promotion")
    if data["decision"]["gates_promoted"] or data["decision"]["complete_new_physics_found"]:
        raise RuntimeError("fail-closed boundary violated")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_report()
    validate(data)
    markdown = render_markdown(data)
    encoded = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT_JSON.write_text(encoded, encoding="utf-8")
        OUTPUT_MD.write_text(markdown, encoding="utf-8")
        print("SUSY V41 full-visible-VEV R-symmetry no-go audit: wrote certificates")
    if args.check:
        if not OUTPUT_JSON.is_file() or not OUTPUT_MD.is_file():
            raise SystemExit("generated certificates missing; run --write")
        if OUTPUT_JSON.read_text(encoding="utf-8") != encoded or OUTPUT_MD.read_text(encoding="utf-8") != markdown:
            raise SystemExit("generated certificates stale; run --write")
        print("SUSY V41 full-visible-VEV R-symmetry no-go audit: PASS")


if __name__ == "__main__":
    main()
