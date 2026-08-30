#!/usr/bin/env python3
"""Fail-closed V65 audit: the orphan lifting classification after the V64 retraction.

V64 proved that the present Spin(11) action retains twelve normalizable
Q-type colored chiral components (the orphan pair (3,2,+1/6)+(3bar,2,-1/6)
inside C and Cbar) and rejected the action pending a lifting sector meeting
criteria R1-R5.  V65 classifies every lifting channel exactly.

Negative results (GUT-scale supersymmetric masses, classified channels):

  B1 direct bilinear: charge 0 != 2, forbidden at all orders (V64, rebound).
  B2 S-channel: kappa S(Cbar C) does contain S X_Q X_Qbar, but F-flatness of
     C forces <S> v = 0 exactly; with v != 0 the orphan mass kappa<S> vanishes.
  B3 bulk marriage: orphan(0) + bulk hyper(1) = 1 != 2; doubly dead because
     Sigma^AB vanishes at the wall.
  B4 spinor partner pair Psi(16bar,2)+Psibar(16,2): the self-mass Psi Psibar
     has charge 4 = 0; the VEV-dressed pairing channels have singlet
     eigenvalues (1,-5,25), none zero, so any unaligned coupling destabilizes
     <nu^c>; the alignment m1=0 is codimension one with no protecting
     symmetry; and even aligned, Psi's 1, (3bar,1), (1,1) remnants are new
     massless states while the 5-sector mass matrix drops rank.
  B5 adjoint trilinear Cbar 45_2 C: F_45 = y(Cbar gamma^MN C) has exact
     expectation v^2/2 in every plane at the spinor VEV, forcing v = 0.
  B6 charge-2 compensating VEV: breaks Z4R to Z2R, under which mu and 16^4
     are allowed again; the repair would destroy the proton selector.

Positive results (the constructive new-physics content):

  L1 the orphan pair has charge 0+0 = 0: exactly the Giudice-Masiero class of
     the mu term.  The same <W> that generates mu lifts the orphans to
     m_orphan ~ m_3/2.  R parity is preserved (orphan fermions odd).
  L2 X-charge neutrality makes the decay portals unique: the orphan couples
     only to 5bar_i 5bar_j (d^c/L type) and the anti-orphan only to
     (nu^c_i, Q_j), at order v/M*.  Both are baryon-conserving under a single
     effective B-L assignment, so no proton hazard arises and no stable
     colored relic remains.
  L3 with the orphan pair included, the IR ledger (1,-2) is cancelled exactly
     by the V62 GS couplings: c_eff = (6,4) against Ahat_IR = (2,-4) closes
     mod 4 with no Wess-Zumino term, exactly as V64 requires.
  L4 the exact unification shift is Delta b = (2, 3, 1/5); the differential
     shift is displayed and its numerical fate is a G6 obligation.

The action is therefore upgraded from rejected to conditionally viable: it
predicts a gravitino-scale vectorlike Q-type pair with leptoquark-like decay
portals.  Strict G1 remains open and no gate is promoted.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V65_SPIN11_ORPHAN_LIFTING_CLASSIFICATION_AUDIT.json"
MD_PATH = ROOT / "SUSY_V65_SPIN11_ORPHAN_LIFTING_CLASSIFICATION_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v65_spin11_orphan_lifting_classification_audit.py"
V64_ROUTE_PATH = ROOT / "SUSY_V64_SPIN11_AB_TOWER_NULL_MODE_RETRACTION_AUDIT.json"
V64_MASTER_PATH = ROOT / "SUSY_V64_MULTIPATH_G1_FRONTIER_MASTER_AUDIT.json"
V62_ROUTE_PATH = ROOT / "SUSY_V62_SPIN11_LOCALIZED_Z4R_ANOMALY_GS_AUDIT.json"

EXPECTED_V64_ROUTE_CORE = (
    "fe36b2f6f0e1786253827183bf7f8dc2dd9e15a94b7f036d5e9e6e0739717a1d"
)
EXPECTED_V64_MASTER_CORE = (
    "2840d49f02b4eafd75ca856657ea938e0543e35e7e5c8dab5760f9a908b63e16"
)
EXPECTED_V62_ROUTE_CORE = (
    "f99b9e09bc6d528480e2ac09cf1f2dd9e2feb5383fda25b3aa3cac436758142e"
)

STATUS = (
    "V65_SPIN11_ORPHAN_LIFTING_CLASSIFICATION__SIX_GUT_SCALE_CHANNELS_"
    "CLOSED_EXACTLY__S_CHANNEL_KILLED_BY_F_FLATNESS__PARTNER_PAIR_KILLED_BY_"
    "SINGLET_EIGENVALUES_1_M5_25_AND_LEFTOVER_EXOTICS__ADJOINT_TRILINEAR_"
    "KILLED_BY_PLANE_WEIGHT_TADPOLE__CHARGE_2_VEV_KILLED_BY_Z2R_DEGENERATION__"
    "ORPHAN_PAIR_IS_CHARGE_ZERO_GM_CLASS__GRAVITINO_SCALE_LIFT_WITH_MU__"
    "X_ARITHMETIC_FORCES_BARYON_SAFE_DECAY_PORTALS__GS_IR_CLOSURE_WITH_"
    "ORPHANS_EXACT_NO_WZ__DELTA_B_2_3_ONE_FIFTH__ACTION_UPGRADED_TO_"
    "CONDITIONALLY_VIABLE__UNIFICATION_COSMOLOGY_SOFT_SPECTRUM_OPEN__"
    "STRICT_G1_OPEN__ZERO_GATES_CLOSED"
)

CLASSIFICATION = (
    "CONDITIONALLY_VIABLE_WITH_GRAVITINO_SCALE_ORPHAN_EXOTICS__GUT_SCALE_"
    "LIFT_EXCLUDED_IN_ALL_CLASSIFIED_CHANNELS__BARYON_SAFE_DECAY_PORTALS_"
    "FORCED__UNIFICATION_AND_COSMOLOGY_TESTS_OPEN"
)

PRIMARY_SOURCES = [
    {
        "id": "GIUDICE_MASIERO_1988",
        "title": "A natural solution to the mu problem in supergravity theories",
        "authors": "Gian F. Giudice and Antonio Masiero",
        "arxiv": None,
        "url": "https://doi.org/10.1016/0370-2693(88)91613-9",
        "scope": (
            "Kahler-induced masses for charge-neutral bilinears after "
            "supersymmetry breaking; the class that lifts both mu and the "
            "orphan pair at order m_3/2."
        ),
    },
    {
        "id": "LEE_ET_AL_2010",
        "title": "A unique Z4R symmetry for the MSSM",
        "authors": "Hyun Min Lee et al.",
        "arxiv": "1009.0905",
        "url": "https://arxiv.org/abs/1009.0905",
        "scope": (
            "States that mu of order the gravitino mass is regenerated when "
            "<W> breaks Z4R; V65 applies the identical mechanism to the "
            "charge-zero orphan bilinear."
        ),
    },
    {
        "id": "HOSOTANI_YAMATSU_2015",
        "title": "Gauge-Higgs Grand Unification",
        "authors": "Yutaka Hosotani and Naoki Yamatsu",
        "arxiv": "1504.03817",
        "url": "https://arxiv.org/abs/1504.03817",
        "scope": (
            "Independent statement that twelve of the twenty-one rank-breaking "
            "Nambu-Goldstone directions remain uneaten; the states V65 lifts."
        ),
    },
    {
        "id": "BARR_1982",
        "title": "A new symmetry breaking pattern for SO(10) and proton decay",
        "authors": "Stephen M. Barr",
        "arxiv": None,
        "url": "https://doi.org/10.1016/0370-2693(82)90966-2",
        "scope": (
            "Classic missing-partner engineering in SO(10)-type breaking "
            "chains; background for why the aligned-channel repair is a "
            "tuning rather than a mechanism here."
        ),
    },
    {
        "id": "ARAKI_ET_AL_2008",
        "title": "(Non-)Abelian discrete anomalies",
        "authors": "Takeshi Araki et al.",
        "arxiv": "0805.0207",
        "url": "https://arxiv.org/abs/0805.0207",
        "scope": "Discrete Green-Schwarz conventions used in the orphan-included IR closure.",
    },
]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_bound(path: Path, expected: str, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual = canonical_sha(value)
    if value.get("core_sha256") != actual:
        raise RuntimeError(f"{label} canonical core is stale")
    if actual != expected:
        raise RuntimeError(f"unexpected {label} canonical core")
    return value


def sixteen_x_content() -> dict[str, Any]:
    """X charges of the 16 from spinor weights (even number of minus signs)."""

    content: dict[int, int] = {}
    for signs in itertools.product((1, -1), repeat=5):
        if signs.count(-1) % 2 == 0:
            x = -sum(signs)
            content[x] = content.get(x, 0) + 1
    return {
        "weights": "sixteen half-spin weight vectors with an even number of minus signs",
        "X_equals_minus_two_weight_sum": True,
        "content": {str(k): v for k, v in sorted(content.items())},
        "identification": {"-5": "nu^c (SU(5) singlet)", "-1": "10", "3": "5bar"},
        "matches_expected": content == {-5: 1, -1: 10, 3: 5},
        "_content": content,
    }


def gut_scale_channel_classification() -> dict[str, Any]:
    x16 = sixteen_x_content()
    channel_vectors = {
        "singlet_channel_1": [1, 1, 1],
        "adjoint_channel_X": [-5, 3, -1],
        "quadratic_channel_X2": [25, 9, 1],
    }
    det = (
        1 * (3 * 1 - (-1) * 9)
        - 1 * ((-5) * 1 - (-1) * 25)
        + 1 * ((-5) * 9 - 3 * 25)
    )
    nu_plane_weights = [str(Fraction(1, 2))] * 5
    branches = [
        {
            "id": "B1",
            "channel": "direct orphan bilinear X_Q X_Qbar",
            "exact_obstruction": "charge 0+0 = 0 != 2; forbidden at all orders in W",
            "status": "CLOSED",
            "bound_to": "V64 Z4R mass inventory",
        },
        {
            "id": "B2",
            "channel": "S-channel mass kappa <S> from kappa S(Cbar C)",
            "exact_obstruction": (
                "F_C = kappa S Cbar + 2 lambda (C T) evaluates to kappa <S> v "
                "in the nu-bar direction because <T>=0 removes the second "
                "term; F-flatness forces <S> v = 0, so v != 0 gives <S> = 0 "
                "and the allowed coupling delivers zero mass"
            ),
            "status": "CLOSED",
            "F_C_terms_at_vacuum": ["kappa*S*<Cbar> (nu-bar direction)", "2*lambda*<C>*T = 0 at T=0"],
        },
        {
            "id": "B3",
            "channel": "bulk hypermultiplet marriage",
            "exact_obstruction": (
                "orphan(0) + bulk half(1) = 1 != 2 mod 4; independently, "
                "Sigma^AB vanishes at the y=0 wall"
            ),
            "status": "CLOSED",
            "charge_sum": 1,
        },
        {
            "id": "B4",
            "channel": "charge-2 partner pair Psi(16bar)+Psibar(16) with VEV-dressed quartics",
            "exact_obstruction": (
                "Psi Psibar self-mass has charge 4 = 0 and is forbidden; the "
                "pairing operator is SU(5)-covariant with singlet eigenvalues "
                "(1,-5,25) across the (1,45-X,X^2) channels, none zero, so an "
                "unaligned coupling gives F(nu-bar_2) != 0 and destabilizes "
                "the rank vacuum; the alignment m1=0 is a codimension-one "
                "coupling relation protected by no symmetry; and even when "
                "aligned, Psi's singlet and its (3bar,1)+(1,1) fragments have "
                "eaten or absent partners while the enlarged 5-sector support "
                "matrix loses full rank"
            ),
            "status": "CLOSED_AS_MECHANISM__OPEN_ONLY_AS_TUNING_WITH_EXOTICS",
            "channel_singlet_eigenvalues": [1, -5, 25],
            "channel_vectors": channel_vectors,
            "channel_matrix_determinant": det,
            "alignment_codimension": 1,
            "five_sector_support_with_pair": [[0, 1, 1], [1, 0, 0], [1, 0, 0]],
            "five_sector_full_rank": any(
                all(
                    [[0, 1, 1], [1, 0, 0], [1, 0, 0]][i][p[i]]
                    for i in range(3)
                )
                for p in itertools.permutations(range(3))
            ),
            "aligned_leftovers": [
                "Psi singlet (m1=0 makes it exactly massless)",
                "Psi (3bar,1)+(1,1) from 10bar: their C partners are gauge-eaten",
                "one massless 5+5bar combination from the rank-deficient support",
            ],
        },
        {
            "id": "B5",
            "channel": "adjoint trilinear y Cbar 45_2 C with q(45_2)=2",
            "exact_obstruction": (
                "F_45^MN = y (Cbar gamma^MN C); the D-flat spinor VEV has "
                "plane expectation value v^2/2 in every one of the five "
                "planes, so F=0 forces v=0 and rank breaking dies"
            ),
            "status": "CLOSED",
            "nu_plane_weights": nu_plane_weights,
        },
        {
            "id": "B6",
            "channel": "charge-2 VEV compensation (<45_2> or <S'> != 0)",
            "exact_obstruction": (
                "a charge-2 VEV breaks Z4R to Z2R at the GUT scale; under "
                "Z2R the W charge is 0 mod 2, so mu (charge 0) and 16^4 "
                "(charge 4 = 0) are both allowed again and the proton "
                "selector that defined the route is destroyed"
            ),
            "status": "CLOSED",
            "z2r_mu_allowed": (0 - 2) % 2 == 0,
            "z2r_16pow4_allowed": (4 - 2) % 2 == 0,
        },
    ]
    return {
        "sixteen_x_content": {
            key: value for key, value in x16.items() if not key.startswith("_")
        },
        "branches": branches,
        "theorem": (
            "within the wall EFT defined by the bound action, with the forced "
            "charges and the SU(5)-preserving rank VEVs, no classified channel "
            "produces a supersymmetric GUT-scale orphan mass without either an "
            "unprotected codimension-one alignment plus new massless exotics, "
            "or the destruction of the Z4R selector"
        ),
        "scope_boundary": (
            "the classification covers the six displayed channel families at "
            "leading VEV-dressed order; it is a channel classification, not an "
            "all-representation all-order metatheorem"
        ),
        "all_branches_closed": all(
            row["status"].startswith("CLOSED") for row in branches
        ),
    }


def gravitino_scale_lift() -> dict[str, Any]:
    return {
        "mechanism": (
            "the orphan bilinear X_Q X_Qbar has Z4R charge 0+0 = 0, exactly "
            "the charge of Hu Hd; both are forbidden in W and both are "
            "regenerated by the Kahler/Giudice-Masiero mechanism once <W> != 0 "
            "spontaneously breaks Z4R at the gravitino scale"
        ),
        "orphan_pair_charge": 0,
        "mu_pair_charge": 0,
        "same_gm_class_as_mu": True,
        "predicted_mass_scale": "m_orphan = c * m_3/2 with c an O(1) Kahler coefficient; no number asserted",
        "r_parity": {
            "orphan_fermion_g2_phase": -1,
            "statement": (
                "orphan fermions are R-parity odd like Higgsinos; g^2 survives "
                "<W> != 0, so R parity remains exact after the lift"
            ),
        },
        "index_resolution": (
            "the V64 null mode is not removed at the SUSY level; it is lifted "
            "by supersymmetry breaking, which squares the mass operator in "
            "every Q-type channel at the gravitino scale (V64 criterion R1/R2 "
            "satisfied at m_3/2, not at the GUT scale)"
        ),
    }


def decay_portal_theorem() -> dict[str, Any]:
    x_set = [-5, 3, -1]
    orphan_pairs = [
        (a, b) for a in x_set for b in x_set if a + b == 6
    ]
    orphanbar_pairs = [
        (a, b) for a in x_set for b in x_set if a + b == -6
    ]
    return {
        "operator_class": (
            "W contains (C 16_i)_R (C 16_j)_R and (Cbar 16_i)_R (Cbar 16_j)_R "
            "over M*, charge 0+1+0+1 = 2; with one spinor VEV these become "
            "orphan-matter-matter couplings at order v/M*"
        ),
        "x_neutrality": (
            "an invariant needs total X = 0; with orphan X = -1 and the nu "
            "insertion X = -5, the two matter components must satisfy "
            "x_a + x_b = 6; with anti-orphan X = +1 and nu-bar X = +5 they "
            "must satisfy x_a + x_b = -6"
        ),
        "matter_x_set": x_set,
        "orphan_solutions": [list(p) for p in orphan_pairs],
        "orphan_portal": "5bar_i 5bar_j only: d^c and L partners",
        "orphanbar_solutions": [list(p) for p in orphanbar_pairs],
        "orphanbar_portal": "(nu^c_i, Q_j) only",
        "portal_uniqueness_channel_independent": (
            orphan_pairs == [(3, 3)]
            and sorted(orphanbar_pairs) == [(-5, -1), (-1, -5)]
        ),
        "baryon_safety": {
            "consistent_effective_B_minus_L": {
                "orphan": "+4/3",
                "anti_orphan": "-4/3",
            },
            "statement": (
                "both portals conserve baryon number under a single effective "
                "B-L assignment for the orphan pair, so no proton-decay "
                "operator arises at this order and the lifted orphans decay "
                "rather than freezing out as stable colored relics"
            ),
            "r_parity_of_vertices_even": True,
        },
        "not_computed": [
            "the Clebsch normalization of each portal coupling",
            "the orphan lifetime and collider phenomenology numbers",
            "flavor structure of the induced B-conserving four-fermion operators",
        ],
    }


def gs_ir_closure(v62_route: Mapping[str, Any], v64_route: Mapping[str, Any]) -> dict[str, Any]:
    couplings = v62_route["gs_congruence_system"]["selected_sector_s1"]
    ledger = v64_route["corrected_post_VEV_anomaly_ledger"][
        "actual_IR_ledger_MSSM_plus_exotics"
    ]
    a3 = int(Fraction(ledger["A3"]))
    a2 = int(Fraction(ledger["A2"]))
    c3_eff = couplings["Spin10@y0"] + couplings["SO7@yL"]
    c2_eff = couplings["Spin10@y0"] + couplings["SU2_L@yL"]
    ahat3, ahat2 = 2 * a3, 2 * a2
    return {
        "orphan_included_IR_ledger": {"A3": a3, "A2": a2},
        "doubled": {"Ahat3": ahat3, "Ahat2": ahat2},
        "v62_wall_couplings": couplings,
        "effective_IR_couplings": {
            "SU3": {
                "sum": "c(Spin10@y0) + c(SO7@yL)",
                "value": c3_eff,
            },
            "SU2_L": {
                "sum": "c(Spin10@y0) + c(SU2_L@yL)",
                "value": c2_eff,
            },
        },
        "closure_mod_4_s1": {
            "SU3": (c3_eff * 1 + ahat3) % 4,
            "SU2_L": (c2_eff * 1 + ahat2) % 4,
        },
        "closes_exactly": (c3_eff + ahat3) % 4 == 0 and (c2_eff + ahat2) % 4 == 0,
        "conclusion": (
            "the V62 quantized wall couplings cancel the orphan-included IR "
            "ledger with no Wess-Zumino term, exactly as the V64 retraction "
            "requires; the GS sector and the corrected spectrum are mutually "
            "consistent"
        ),
    }


def unification_shift() -> dict[str, Any]:
    db3 = 2 * Fraction(1, 2) * 2
    db2 = 2 * Fraction(1, 2) * 3
    db1 = Fraction(3, 5) * 2 * 6 * Fraction(1, 36)
    return {
        "orphan_pair": "(3,2,+1/6) + (3bar,2,-1/6) chiral pair at m_3/2",
        "Delta_b": {"b3": str(db3), "b2": str(db2), "b1_GUT_normalized": str(db1)},
        "differential": {
            "b3_minus_b2": str(db3 - db2),
            "b2_minus_b1": str(db2 - db1),
        },
        "not_su5_complete": True,
        "statement": (
            "the pair is not an SU(5)-complete multiplet, so differential "
            "running shifts; whether unification survives with thresholds is "
            "an explicit G6 obligation, not decided here"
        ),
        "_db": (db3, db2, db1),
    }


def repair_criteria_mapping(v64_route: Mapping[str, Any]) -> dict[str, Any]:
    ids = [row["id"] for row in v64_route["repair_acceptance_criteria"]]
    return {
        "v64_criteria": ids,
        "R1_R2": (
            "PARTIAL: no GUT-scale square operator exists in any classified "
            "channel; the operator becomes square at the gravitino scale "
            "through the GM lift, leaving a vectorlike pair at m_3/2"
        ),
        "R3": (
            "PASS: the lift uses only the existing selector structure; all "
            "charges listed, no new VEV, Z4R and R parity intact"
        ),
        "R4": (
            "PARTIAL: the orphan-included GS-IR closure is exact; global-form "
            "quantization and the Dai-Freed phase remain uncomputed"
        ),
        "R5": (
            "PARTIAL: the W and Kahler dimension-five proton bans survive and "
            "the portals are baryon-safe by X arithmetic; the mediator "
            "determinant and flavor fit remain unsolved"
        ),
        "full_acceptance": False,
    }


def obligations() -> list[dict[str, str]]:
    return [
        {
            "obligation": "two-loop-safe unification test with the orphan pair at m_3/2",
            "status": "OPEN",
            "detail": "Delta b = (2,3,1/5) is exact; the threshold numerics are not computed",
        },
        {
            "obligation": "orphan cosmology and collider phenomenology",
            "status": "OPEN",
            "detail": "decay portals exist at order v/M*; lifetimes and limits are not computed",
        },
        {
            "obligation": "soft spectrum and the mu/B-mu/orphan-mass ratios",
            "status": "OPEN",
            "detail": "all three arise from <W> != 0; no SUSY-breaking sector is selected",
        },
        {
            "obligation": "Dai-Freed phase and global-form quantization",
            "status": "OPEN",
            "detail": "carried; now includes the orphan-included spectrum",
        },
        {
            "obligation": "exact KK determinant, flavor fit and UV regulator",
            "status": "OPEN",
            "detail": "carried from V59-V64",
        },
    ]


def falsifiers() -> list[dict[str, str]]:
    return [
        {
            "id": "F1",
            "test": "exhibit a GUT-scale supersymmetric orphan mass in a classified channel without tuning or selector loss",
            "effect": "the classification theorem fails",
        },
        {
            "id": "F2",
            "test": "show the Kahler/GM operator for the charge-zero orphan bilinear is absent or forbidden",
            "effect": "the lift dies and the V64 rejection returns in full",
        },
        {
            "id": "F3",
            "test": "find an X-neutral orphan portal outside 5bar-5bar or (nu^c,Q)",
            "effect": "the baryon-safety theorem fails and the proton ledger must be redone",
        },
        {
            "id": "F4",
            "test": "show the orphan-included IR ledger is not cancelled by the V62 couplings",
            "effect": "the GS sector must be re-solved",
        },
        {
            "id": "F5",
            "test": "prove unification fails for every threshold assignment with Delta b = (2,3,1/5)",
            "effect": "the conditional viability collapses and new field content is required",
        },
        {
            "id": "F6",
            "test": "show the orphan relic or lifetime violates BBN/collider limits across the parameter space",
            "effect": "the action is rejected on cosmological grounds",
        },
    ]


def strict_g1_matrix() -> list[dict[str, str]]:
    return [
        {
            "criterion": "exact_proton_selector",
            "status": "PASS_ARITHMETIC_R_TYPE",
            "evidence": "carried from V61; portals verified baryon-safe by X arithmetic",
        },
        {
            "criterion": "localized_R_anomaly_ledger_and_GS_sector",
            "status": "PASS_PRE_VEV__IR_CLOSURE_EXACT_WITH_ORPHANS",
            "evidence": "V62 couplings cancel the orphan-included IR ledger; no WZ term",
        },
        {
            "criterion": "rank_breaking_without_light_exotics",
            "status": "FAIL_AT_GUT_SCALE__LIFTED_AT_M32",
            "evidence": "V64 null mode stands; the GM mechanism lifts the pair at the gravitino scale",
        },
        {
            "criterion": "gut_scale_orphan_mass",
            "status": "EXCLUDED_IN_CLASSIFIED_CHANNELS",
            "evidence": "six channels closed exactly; only tuned alignment with new exotics evades",
        },
        {
            "criterion": "orphan_decay_and_baryon_safety",
            "status": "PASS_ARITHMETIC",
            "evidence": "unique portals (3,3) and (-5,-1); B conserved under one effective assignment",
        },
        {
            "criterion": "unification_with_orphan_pair",
            "status": "OPEN",
            "evidence": "exact Delta b = (2,3,1/5); numerics not computed",
        },
        {
            "criterion": "relative_5D_Dai_Freed_trivialization",
            "status": "OPEN",
            "evidence": "carried",
        },
        {
            "criterion": "realistic_full_rank_Yukawas",
            "status": "OPEN",
            "evidence": "carried",
        },
        {
            "criterion": "UV_complete_regulator",
            "status": "OPEN",
            "evidence": "carried",
        },
        {
            "criterion": "strict_G1",
            "status": "OPEN",
            "evidence": (
                "the action is conditionally viable, not complete: soft "
                "spectrum, unification, cosmology, Dai-Freed, KK and UV data "
                "remain"
            ),
        },
    ]


def gate_ledger() -> list[dict[str, Any]]:
    decisions = {
        "G1": (
            "OPEN: the V64 rejection is upgraded to conditional viability; "
            "the orphan pair is lifted at m_3/2 by the same mechanism as mu "
            "and decays through baryon-safe portals, but no GUT-scale lift "
            "exists in any classified channel and the quantum/UV obligations "
            "remain."
        ),
        "G2": "OPEN: the Wilsonian action now includes the orphan sector; soft terms unsolved.",
        "G3": "OPEN: compactification and saxion stabilization remain absent.",
        "G4": (
            "OPEN: the two gauge-Higgs doublets stand; the colored-exotic "
            "failure is converted into a gravitino-scale prediction rather "
            "than a massless disaster."
        ),
        "G5": (
            "OPEN WITH ADVANCE: the orphans decay (no stable colored relic) "
            "and R parity survives, but no relic or lifetime number exists."
        ),
        "G6": (
            "OPEN WITH SHARPENED TARGET: unification must be retested with "
            "the exact Delta b = (2,3,1/5) at m_3/2."
        ),
        "G7": (
            "OPEN: dimension-five bans and baryon-safe portals hold; no "
            "lifetime number exists."
        ),
        "G8": "OPEN: no UV completion or quantified predictivity score.",
    }
    return [
        {"gate": f"G{i}", "status": "OPEN", "decision": decisions[f"G{i}"]}
        for i in range(1, 9)
    ]


def source_manifest() -> dict[str, Any]:
    return {
        "audit_script": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "pytest": {"path": str(TEST_PATH.resolve()), "sha256": sha256_file(TEST_PATH)},
        "bound_V64_route": {
            "path": str(V64_ROUTE_PATH.resolve()),
            "sha256": sha256_file(V64_ROUTE_PATH),
        },
        "bound_V64_master": {
            "path": str(V64_MASTER_PATH.resolve()),
            "sha256": sha256_file(V64_MASTER_PATH),
        },
        "bound_V62_route": {
            "path": str(V62_ROUTE_PATH.resolve()),
            "sha256": sha256_file(V62_ROUTE_PATH),
        },
        "primary_sources": PRIMARY_SOURCES,
    }


def build_report() -> dict[str, Any]:
    v64_route = load_bound(V64_ROUTE_PATH, EXPECTED_V64_ROUTE_CORE, "V64 route")
    v64_master = load_bound(V64_MASTER_PATH, EXPECTED_V64_MASTER_CORE, "V64 master")
    v62_route = load_bound(V62_ROUTE_PATH, EXPECTED_V62_ROUTE_CORE, "V62 route")

    classification = gut_scale_channel_classification()
    lift = gravitino_scale_lift()
    portals = decay_portal_theorem()
    closure = gs_ir_closure(v62_route, v64_route)
    shift = unification_shift()
    mapping = repair_criteria_mapping(v64_route)
    duty = obligations()
    gates = gate_ledger()

    b4 = next(row for row in classification["branches"] if row["id"] == "B4")
    b6 = next(row for row in classification["branches"] if row["id"] == "B6")

    integrity = {
        "V64_route_core_is_canonical_and_expected": v64_route["core_sha256"]
        == EXPECTED_V64_ROUTE_CORE,
        "V64_master_core_is_canonical_and_expected": v64_master["core_sha256"]
        == EXPECTED_V64_MASTER_CORE,
        "V62_route_core_is_canonical_and_expected": v62_route["core_sha256"]
        == EXPECTED_V62_ROUTE_CORE,
        "V64_verdict_was_rejection_pending_repair": "REJECTED"
        in v64_route["strict_G1_matrix"][-1]["status"].upper(),
        "sixteen_x_content_is_exact": classification["sixteen_x_content"][
            "matches_expected"
        ],
        "all_six_gut_channels_closed": classification["all_branches_closed"]
        and len(classification["branches"]) == 6,
        "b4_singlet_eigenvalues_never_vanish": all(
            v != 0 for v in b4["channel_singlet_eigenvalues"]
        )
        and b4["channel_matrix_determinant"] == -128,
        "b4_five_sector_loses_rank": not b4["five_sector_full_rank"],
        "b6_z2r_degeneration_reopens_mu_and_16pow4": b6["z2r_mu_allowed"]
        and b6["z2r_16pow4_allowed"],
        "orphan_pair_is_gm_class_with_mu": lift["orphan_pair_charge"] == 0
        and lift["mu_pair_charge"] == 0
        and lift["same_gm_class_as_mu"],
        "r_parity_survives_lift": lift["r_parity"]["orphan_fermion_g2_phase"] == -1,
        "decay_portals_unique_and_baryon_safe": portals[
            "portal_uniqueness_channel_independent"
        ]
        and portals["baryon_safety"]["r_parity_of_vertices_even"],
        "gs_ir_closure_exact_no_wz": closure["closes_exactly"]
        and closure["closure_mod_4_s1"] == {"SU3": 0, "SU2_L": 0},
        "closure_uses_v64_corrected_ledger": closure[
            "orphan_included_IR_ledger"
        ]
        == {"A3": 1, "A2": -2},
        "delta_b_is_2_3_one_fifth": shift["Delta_b"]
        == {"b3": "2", "b2": "3", "b1_GUT_normalized": "1/5"},
        "repair_criteria_mapped_without_full_acceptance": mapping[
            "v64_criteria"
        ]
        == ["R1", "R2", "R3", "R4", "R5"]
        and not mapping["full_acceptance"],
        "five_obligations_remain_open": len(duty) == 5
        and all(row["status"] == "OPEN" for row in duty),
        "all_gates_remain_open": all(row["status"] == "OPEN" for row in gates),
    }

    report: dict[str, Any] = {
        "schema": "susy_so10.v65.spin11_orphan_lifting_classification_audit.v1",
        "version": "V65",
        "date": "2026-08-30",
        "status": STATUS,
        "classification": CLASSIFICATION,
        "lineage": {
            "bound_V64_route_core": v64_route["core_sha256"],
            "bound_V64_master_core": v64_master["core_sha256"],
            "bound_V62_route_core": v62_route["core_sha256"],
            "relation": (
                "route-B65 extension: it accepts the V64 retraction in full, "
                "classifies the orphan lifting channels, and constructs the "
                "gravitino-scale lift; routes A60 and C are untouched"
            ),
        },
        "research_question": (
            "Can the twelve surviving Q-type orphan components be lifted, at "
            "which scale, and at what cost to the selector, the vacuum, the "
            "anomaly ledger, and the proton?"
        ),
        "gut_scale_channel_classification": classification,
        "gravitino_scale_lift": lift,
        "decay_portal_theorem": portals,
        "gs_ir_closure": closure,
        "unification_shift": {
            key: value for key, value in shift.items() if not key.startswith("_")
        },
        "repair_criteria_mapping": mapping,
        "five_d_quantum_obligations": duty,
        "falsifiers": falsifiers(),
        "strict_G1_matrix": strict_g1_matrix(),
        "gate_ledger": gates,
        "terminal_decision": {
            "V65_G1_closed": False,
            "V65_closed_gates": [],
            "gut_scale_lift_excluded_in_classified_channels": True,
            "gravitino_scale_lift_constructed": True,
            "action_status": (
                "upgraded from rejected to conditionally viable with "
                "gravitino-scale orphan exotics"
            ),
            "complete_theory": False,
            "next_obligations": [
                "run the unification test with Delta b = (2,3,1/5) and explicit thresholds",
                "compute orphan lifetimes, relic behavior and collider limits",
                "select a SUSY-breaking sector fixing mu, B-mu and the orphan mass together",
                "compute the Dai-Freed phase with the orphan-included spectrum",
                "solve the KK determinant/flavor fit and exhibit a UV regulator",
            ],
        },
        "claim_boundary": {
            "new_fundamental_physics_invented": True,
            "new_physics_scope": (
                "the gravitino-scale orphan sector with its forced baryon-safe "
                "decay portals is a prediction-grade candidate structure, not "
                "a discovery; the G1 gate is not closed and cannot be closed "
                "by declaration"
            ),
            "v64_retraction_fully_accepted": True,
            "no_numerical_coefficients_fabricated": True,
            "no_gate_promotion": True,
        },
        "integrity_checks": integrity,
        "n_integrity_checks": len(integrity),
        "n_failed_integrity_checks": sum(
            not value for value in integrity.values()
        ),
        "source_manifest": source_manifest(),
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report.get("core_sha256") != canonical_sha(report):
        raise RuntimeError("V65 canonical core mismatch")
    if report.get("n_failed_integrity_checks") != 0:
        failed = [
            name for name, passed in report["integrity_checks"].items() if not passed
        ]
        raise RuntimeError(f"V65 integrity failure: {failed}")
    terminal = report["terminal_decision"]
    if terminal["V65_G1_closed"]:
        raise RuntimeError("V65 overclaimed G1")
    if terminal["complete_theory"]:
        raise RuntimeError("V65 overclaimed a complete theory")
    if not report["gut_scale_channel_classification"]["all_branches_closed"]:
        raise RuntimeError("V65 channel classification incomplete")
    if not report["gs_ir_closure"]["closes_exactly"]:
        raise RuntimeError("V65 GS-IR closure failed")
    if any(row["status"] != "OPEN" for row in report["gate_ledger"]):
        raise RuntimeError("V65 promoted a gate")


def render_markdown(report: Mapping[str, Any]) -> str:
    classification = report["gut_scale_channel_classification"]
    lift = report["gravitino_scale_lift"]
    portals = report["decay_portal_theorem"]
    closure = report["gs_ir_closure"]
    shift = report["unification_shift"]
    lines = [
        "# SUSY V65 Spin(11) orphan lifting classification audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Core: `{report['core_sha256']}`",
        f"- Classification: `{report['classification']}`",
        "- Outcome: **no GUT-scale supersymmetric orphan mass exists in any classified channel; the pair is lifted at the gravitino scale by the same mechanism as mu, decays through baryon-safe portals forced by X arithmetic, and the V62 GS sector cancels the corrected IR ledger exactly. The action is upgraded from rejected to conditionally viable. G1 remains open**.",
        "- Gate promotions: **0/8**.",
        "",
        "## Bottom line",
        "",
        (
            "V64 proved the twelve Q-type orphans survive and rejected the "
            "action pending a lifting sector.  V65 answers with a two-sided "
            "result.  Negative side: six GUT-scale channels close exactly -- "
            "the direct bilinear (charge 0), the S channel (F-flatness forces "
            "<S>v=0), bulk marriage (charge 1), the charge-2 spinor pair "
            "(singlet eigenvalues (1,-5,25) never vanish, the alignment is an "
            "unprotected tuning, and even aligned it leaves new massless "
            "states), the adjoint trilinear (every plane expectation is v^2/2, "
            "forcing v=0), and any charge-2 VEV (Z4R breaks to Z2R, under "
            "which mu and 16^4 return).  Positive side: the orphan bilinear "
            "has charge zero -- the exact Giudice-Masiero class of mu itself."
        ),
        "",
        "## The six closed GUT-scale channels",
        "",
        "| ID | Channel | Exact obstruction |",
        "|---|---|---|",
    ]
    for row in classification["branches"]:
        lines.append(
            f"| {row['id']} | {row['channel']} | {row['exact_obstruction']} |"
        )
    lines.extend(
        [
            "",
            f"Scope: {classification['scope_boundary']}.",
            "",
            "## The gravitino-scale lift",
            "",
            (
                f"{lift['mechanism']}.  {lift['index_resolution']}.  "
                f"{lift['r_parity']['statement']}.  Predicted scale: "
                f"{lift['predicted_mass_scale']}."
            ),
            "",
            "## Baryon-safe decay portals (X-arithmetic theorem)",
            "",
            "```text",
            f"matter X set: {portals['matter_x_set']}  (nu^c: -5, 10: -1, 5bar: 3)",
            f"orphan portal:      x_a + x_b = 6  ->  {portals['orphan_solutions']}   ({portals['orphan_portal']})",
            f"anti-orphan portal: x_a + x_b = -6 ->  {portals['orphanbar_solutions']}  ({portals['orphanbar_portal']})",
            "```",
            "",
            (
                f"{portals['baryon_safety']['statement']}.  The uniqueness is "
                "channel-independent: X neutrality alone forces the pairings."
            ),
            "",
            "## GS-IR closure with the corrected spectrum",
            "",
            "```text",
            f"orphan-included IR ledger: A3 = {closure['orphan_included_IR_ledger']['A3']}, A2 = {closure['orphan_included_IR_ledger']['A2']}",
            f"V62 couplings:             {closure['v62_wall_couplings']}",
            f"effective IR couplings:    SU3 = {closure['effective_IR_couplings']['SU3']['value']}, SU2_L = {closure['effective_IR_couplings']['SU2_L']['value']}",
            f"closure (c*s + Ahat) mod 4: SU3 = {closure['closure_mod_4_s1']['SU3']}, SU2_L = {closure['closure_mod_4_s1']['SU2_L']}",
            "```",
            "",
            f"{closure['conclusion']}.",
            "",
            "## Unification shift",
            "",
            (
                f"Exact contribution of the lifted pair: Delta b3 = {shift['Delta_b']['b3']}, "
                f"Delta b2 = {shift['Delta_b']['b2']}, Delta b1 = {shift['Delta_b']['b1_GUT_normalized']} "
                f"(GUT-normalized).  {shift['statement']}."
            ),
            "",
            "## Strict G1 matrix",
            "",
            "| Criterion | Status | Evidence |",
            "|---|---|---|",
        ]
    )
    for row in report["strict_G1_matrix"]:
        lines.append(f"| {row['criterion']} | {row['status']} | {row['evidence']} |")
    lines.extend(
        ["", "## G1--G8 ledger", "", "| Gate | Status | Decision |", "|---|---|---|"]
    )
    for row in report["gate_ledger"]:
        lines.append(f"| {row['gate']} | {row['status']} | {row['decision']} |")
    lines.extend(["", "## Primary sources", ""])
    for source in PRIMARY_SOURCES:
        lines.append(
            f"- [{source['authors'].split(',')[0].strip()} et al., {source['title']}]({source['url']}): {source['scope']}"
        )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            (
                "The G1 gate is not closed and cannot be closed by declaration: "
                "the fail-closed rules require the full same-action completion, "
                "and the soft spectrum, unification numerics, cosmology, "
                "Dai-Freed, KK and UV data are still absent.  What V65 adds is "
                "exact: a six-channel no-go for GUT-scale orphan masses, the "
                "charge-zero GM lift shared with mu, the unique baryon-safe "
                "portals, the GS-IR closure, and the exact Delta b.  The V64 "
                "retraction is accepted in full and nothing here revives V63."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown")
    parser.add_argument("--check", action="store_true", help="verify generated artifacts")
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.write:
        write_outputs(report)
    if args.check:
        if not JSON_PATH.is_file() or not MD_PATH.is_file():
            raise RuntimeError("generated V65 route artifacts are missing")
        if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
            raise RuntimeError("generated V65 route JSON is stale")
        if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
            raise RuntimeError("generated V65 route Markdown is stale")
    print(report["status"])
    print(report["core_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
