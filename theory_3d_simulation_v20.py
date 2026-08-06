#!/usr/bin/env python3
r"""Interactive 3D theory simulation for SO(10) axion v20.

Builds a browser-viewable Three.js scene from the authoritative progress-30
certificate and the exact H–Σ 45 closed formula:

    ΔA_u = diag(−λ_HΣ45 v_R², 0)          on (T10, t2)
    ΔA_v = diag(+λ_HΣ45 v_R², 0, 0)       on (T10bar, t2bar, t4bar)
    ΔB   = 0

Honesty: visualization only. Does **not** claim G1 closed, unique τ_p, or
whole-model validation. Certificate is loaded from disk (no heavy gate chain).
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import webbrowser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "artifacts" / "theory_3d"
OUT_HTML = OUT_DIR / "SO10_THEORY_3D_SIMULATION_V20.html"
OUT_JSON = OUT_DIR / "SO10_THEORY_3D_SIMULATION_V20.json"
CERT_COPY = OUT_DIR / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json"
CERT_MD = OUT_DIR / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.md"

CERT_CANDIDATES = [
    ROOT / ".artifacts" / "progress30" / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json",
    ROOT / ".artifacts" / "progress30" / "next-gen-g1-g6-progress-30" / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json",
    ROOT / "NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json",
]


def load_progress30_certificate() -> dict[str, Any]:
    for path in CERT_CANDIDATES:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    # Minimal fail-closed stub if artifacts are missing.
    return {
        "status": "CERTIFICATE_ARTIFACT_MISSING__FULL_THEORY_STILL_BLOCKED",
        "n_closed_subproblems": 30,
        "n_remaining_blockers": 13,
        "gate_states": {"G1": "OPEN", "G2": "PARTIAL", "G6": "PARTIAL", "G7": "OPEN", "G8": "PARTIAL"},
        "closed_subproblems": {},
        "remaining_blockers": {},
        "next_exact_target": "Restore NEXT_GEN_G1_G6_PROGRESS_30_GATE_V20.json artifact.",
        "verdict": "Certificate file not found; theory remains BLOCKED.",
    }


def _k_color(p: float, a: float, omega: float) -> float:
    return 2.0 * p * a / math.sqrt(3.0) + 2.0 * omega * omega / 3.0


def analytic_hsigma_blocks(*, v_r: float, lambda_hsigma_45: float) -> dict[str, list[float]]:
    """Exact closed H–Σ 45 diagonal shifts (pure math; matches closed-formula module)."""
    shift = float(lambda_hsigma_45) * float(v_r) ** 2
    return {
        "A_u": [-shift, 0.0],
        "A_v": [shift, 0.0, 0.0],
        "B": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "shift": shift,
    }


def mass_scene(
    *,
    p: float,
    a: float,
    omega: float,
    v_r: float,
    lambda_hsigma_45: float,
    lambda_phih_45: float,
    lambda_phisigma_45: float,
) -> dict[str, Any]:
    blocks = analytic_hsigma_blocks(v_r=v_r, lambda_hsigma_45=lambda_hsigma_45)
    kc = _k_color(p, a, omega)
    shift = blocks["shift"]
    masses = {
        "T10": blocks["A_u"][0] + lambda_phih_45 * kc,
        "t2": blocks["A_u"][1] + lambda_phisigma_45 * kc,
        "T10bar": blocks["A_v"][0] - lambda_phih_45 * kc,
        "t2bar": blocks["A_v"][1] - lambda_phisigma_45 * kc,
        "t4bar": blocks["A_v"][2] - lambda_phisigma_45 * kc,
    }
    return {
        "k_color": kc,
        "hsigma_shift": shift,
        "delta_B": 0.0,
        "masses_GeV2": masses,
        "formula": {
            "Delta_A_u": "diag(-λ_HΣ45 v_R^2, 0)",
            "Delta_A_v": "diag(+λ_HΣ45 v_R^2, 0, 0)",
            "Delta_B": "0",
            "independent_of_hu_hd": True,
        },
        "knobs": {
            "p": p,
            "a": a,
            "omega": omega,
            "v_r": v_r,
            "lambda_hsigma_45": lambda_hsigma_45,
            "lambda_phih_45": lambda_phih_45,
            "lambda_phisigma_45": lambda_phisigma_45,
        },
    }


def build_payload(
    *,
    p: float = 0.2,
    a: float = 0.3,
    omega: float = 0.5,
    v_r: float = 1.0,
    lambda_hsigma_45: float = 0.25,
    lambda_phih_45: float = 0.15,
    lambda_phisigma_45: float = 0.1,
) -> dict[str, Any]:
    cert = load_progress30_certificate()
    scene = mass_scene(
        p=p,
        a=a,
        omega=omega,
        v_r=v_r,
        lambda_hsigma_45=lambda_hsigma_45,
        lambda_phih_45=lambda_phih_45,
        lambda_phisigma_45=lambda_phisigma_45,
    )
    closed_keys = sorted(k for k, v in (cert.get("closed_subproblems") or {}).items() if v)
    blocker_keys = sorted(k for k, v in (cert.get("remaining_blockers") or {}).items() if v)
    return {
        "title": "SO(10) axion v20 — interactive theory 3D",
        "honesty": {
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "exact_unique_proton_lifetime": False,
            "G1": "OPEN",
            "G6": "PARTIAL",
            "note": (
                "Visualization of closed subproblems and exact H–Σ 45 mass "
                "shifts. Full theory remains BLOCKED."
            ),
        },
        "certificate": {
            "status": cert.get("status"),
            "n_closed_subproblems": cert.get("n_closed_subproblems", len(closed_keys)),
            "n_remaining_blockers": cert.get("n_remaining_blockers", len(blocker_keys)),
            "gate_states": cert.get("gate_states", {}),
            "closed_keys": closed_keys,
            "blocker_keys": blocker_keys,
            "next_exact_target": cert.get("next_exact_target"),
            "verdict": cert.get("verdict"),
        },
        "fields": [
            {"id": "Phi210", "label": "Φ₂₁₀", "vevs": ["p", "a", "ω"], "role": "GUT"},
            {"id": "Sigma126", "label": "Σ̄₁₂₆", "vevs": ["v_R"], "role": "LR"},
            {"id": "H10", "label": "H₁₀", "vevs": ["h_u", "h_d"], "role": "EW"},
            {"id": "S", "label": "S", "vevs": ["⟨S⟩"], "role": "PQ"},
            {"id": "Phi17", "label": "Φ₁₇", "vevs": ["|Φ₁₇|"], "role": "Z17"},
        ],
        "triplets": [
            {"id": "T10", "parent": "H10", "Y": -1.0 / 3.0},
            {"id": "t2", "parent": "Sigma126", "Y": -1.0 / 3.0},
            {"id": "T10bar", "parent": "H10", "Y": +1.0 / 3.0},
            {"id": "t2bar", "parent": "Sigma126", "Y": +1.0 / 3.0},
            {"id": "t4bar", "parent": "Sigma126", "Y": +1.0 / 3.0, "alias": "T'"},
        ],
        "gates": {
            "G1": "OPEN",
            "G2": "PARTIAL",
            "G3": "PARTIAL",
            "G4": "PARTIAL",
            "G5": "PARTIAL",
            "G6": "PARTIAL",
            "G7": "OPEN",
            "G8": "PARTIAL",
        },
        "scene": scene,
        "hsigma_closed": {
            "operator": "λ_HΣ45 J45[H]:J45[Σ]",
            "merged_on_main": "PR #108 / 08b533e",
            "formula": scene["formula"],
            "note": "Exact closed formula verified on main; theory still BLOCKED.",
        },
    }


def _html(payload: dict[str, Any]) -> str:
    data = json.dumps(payload)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>SO(10) Theory 3D Simulation v20</title>
<style>
  :root {{
    --bg0: #071018; --ink: #e8f1f8; --muted: #8fa3b8;
    --accent: #3ecf8e; --warn: #e0a14a; --open: #e05a5a;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin:0; height:100%; background: radial-gradient(1200px 800px at 20% 10%, #123049, var(--bg0)); color: var(--ink); font-family: "Segoe UI", "IBM Plex Sans", sans-serif; }}
  #app {{ display:grid; grid-template-columns: 320px 1fr; height:100%; }}
  aside {{ padding:18px 16px; border-right:1px solid #1e3348; background: linear-gradient(180deg, #0b1724, #08131d); overflow:auto; }}
  h1 {{ font-size:1.05rem; margin:0 0 6px; }}
  .sub {{ color:var(--muted); font-size:0.78rem; line-height:1.35; margin-bottom:14px; }}
  .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:0.7rem; background:#1a2f42; color:var(--warn); border:1px solid #2b4660; }}
  label {{ display:block; font-size:0.72rem; color:var(--muted); margin:10px 0 4px; }}
  input[type=range] {{ width:100%; }}
  .val {{ float:right; color:var(--accent); font-variant-numeric: tabular-nums; }}
  .panel {{ margin-top:14px; padding-top:10px; border-top:1px solid #1e3348; }}
  .mass {{ display:flex; justify-content:space-between; font-size:0.78rem; padding:3px 0; border-bottom:1px dashed #1a2d40; }}
  .mass b {{ color:var(--accent); }}
  .gates {{ display:grid; grid-template-columns: repeat(4,1fr); gap:6px; margin-top:8px; }}
  .gate {{ text-align:center; font-size:0.65rem; padding:6px 2px; border-radius:8px; background:#122233; border:1px solid #243b52; white-space:pre-line; }}
  .OPEN {{ color:var(--open); }} .PARTIAL {{ color:var(--warn); }}
  #stage {{ position:relative; }}
  canvas {{ display:block; width:100%; height:100%; }}
  #hud {{ position:absolute; left:16px; bottom:14px; right:16px; pointer-events:none; font-size:0.78rem; color:var(--muted); }}
  #hud strong {{ color:var(--ink); }}
</style>
</head>
<body>
<div id="app">
  <aside>
    <h1>SO(10) axion · theory 3D</h1>
    <div class="sub">Exact H–Σ 45 mass split + progress-30 certificate. Theory remains <span class="badge">BLOCKED</span> — not a discovery claim.</div>
    <div class="panel">
      <div style="font-size:0.75rem;color:var(--muted)">Certificate</div>
      <div style="font-size:0.9rem;margin-top:4px"><span id="nClosed">30</span> closed · <span id="nBlock">13</span> blockers</div>
      <div class="gates" id="gateGrid"></div>
    </div>
    <div class="panel">
      <label>λ<sub>HΣ,45</sub> <span class="val" id="v_lamHS">0.25</span></label>
      <input id="lamHS" type="range" min="-1" max="1" step="0.01" value="0.25"/>
      <label>v<sub>R</sub> <span class="val" id="v_vr">1.00</span></label>
      <input id="vr" type="range" min="0.2" max="2.0" step="0.01" value="1.0"/>
      <label>λ<sub>ΦH,45</sub> <span class="val" id="v_lamPH">0.15</span></label>
      <input id="lamPH" type="range" min="-1" max="1" step="0.01" value="0.15"/>
      <label>λ<sub>ΦΣ,45</sub> <span class="val" id="v_lamPS">0.10</span></label>
      <input id="lamPS" type="range" min="-1" max="1" step="0.01" value="0.10"/>
      <label>p <span class="val" id="v_p">0.20</span></label>
      <input id="p" type="range" min="-1" max="1" step="0.01" value="0.2"/>
      <label>a <span class="val" id="v_a">0.30</span></label>
      <input id="a" type="range" min="-1" max="1" step="0.01" value="0.3"/>
      <label>ω <span class="val" id="v_w">0.50</span></label>
      <input id="w" type="range" min="-1" max="1" step="0.01" value="0.5"/>
    </div>
    <div class="panel">
      <div style="font-size:0.75rem;color:var(--muted);margin-bottom:6px">Color-triplet m² shifts</div>
      <div id="massList"></div>
      <div class="sub" style="margin-top:8px">ΔB = 0 · T10 ↔ T10bar opposite H–Σ split · independent of h<sub>u</sub>, h<sub>d</sub></div>
    </div>
  </aside>
  <div id="stage">
    <div id="hud"><strong>Drag</strong> to orbit · scroll to zoom · spheres = fields · pillars = triplet mass shifts · ring = G1–G8</div>
  </div>
</div>
<script type="importmap">
{{"imports": {{
  "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
  "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
}}}}
</script>
<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

const DATA = {data};
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({{ antialias:true, alpha:true }});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(stage.clientWidth, stage.clientHeight);
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(48, stage.clientWidth/stage.clientHeight, 0.1, 200);
camera.position.set(8.5, 5.2, 9.5);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 1.2, 0);

scene.add(new THREE.AmbientLight(0xb8d0e8, 0.55));
const key = new THREE.DirectionalLight(0xffffff, 1.05);
key.position.set(6, 10, 4); scene.add(key);
const rim = new THREE.PointLight(0x3ecf8e, 1.2, 40);
rim.position.set(-4, 3, -3); scene.add(rim);

const floor = new THREE.Mesh(new THREE.CircleGeometry(12, 64), new THREE.MeshStandardMaterial({{ color:0x0b1622, roughness:0.92 }}));
floor.rotation.x = -Math.PI/2; scene.add(floor);
scene.add(new THREE.GridHelper(16, 24, 0x1e3a52, 0x122536));

function makeLabelCanvas(text, color='#e8f1f8') {{
  const c = document.createElement('canvas'); c.width=512; c.height=128;
  const ctx = c.getContext('2d');
  ctx.fillStyle = color; ctx.font = 'bold 48px Segoe UI, sans-serif';
  ctx.textAlign = 'center'; ctx.fillText(text, 256, 72); return c;
}}
function spriteLabel(text, color) {{
  const tex = new THREE.CanvasTexture(makeLabelCanvas(text, color));
  const s = new THREE.Sprite(new THREE.SpriteMaterial({{ map: tex, transparent:true }}));
  s.scale.set(2.2, 0.55, 1); return s;
}}

const fieldGeom = {{
  Phi210: {{ pos:[0, 2.6, 0], color:0x4ea8de, r:0.85 }},
  Sigma126: {{ pos:[-3.2, 1.8, 1.2], color:0x3ecf8e, r:0.7 }},
  H10: {{ pos:[3.2, 1.8, 1.2], color:0xe0a14a, r:0.65 }},
  S: {{ pos:[-2.4, 3.6, -2.2], color:0xc084fc, r:0.45 }},
  Phi17: {{ pos:[2.4, 3.6, -2.2], color:0xf472b6, r:0.4 }},
}};
const fieldMeshes = {{}};
for (const [id, cfg] of Object.entries(fieldGeom)) {{
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(cfg.r, 36, 24),
    new THREE.MeshStandardMaterial({{ color:cfg.color, roughness:0.35, metalness:0.25, emissive:cfg.color, emissiveIntensity:0.18 }})
  );
  mesh.position.set(...cfg.pos); scene.add(mesh);
  const lab = spriteLabel((DATA.fields.find(f=>f.id===id)||{{}}).label || id);
  lab.position.set(cfg.pos[0], cfg.pos[1]+cfg.r+0.55, cfg.pos[2]); scene.add(lab);
  fieldMeshes[id] = mesh;
}}
function bond(a,b,color=0x2a4a66) {{
  const A = new THREE.Vector3(...fieldGeom[a].pos), B = new THREE.Vector3(...fieldGeom[b].pos);
  const dir = new THREE.Vector3().subVectors(B,A), len = dir.length();
  const mid = new THREE.Vector3().addVectors(A,B).multiplyScalar(0.5);
  const cyl = new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.04,len,10), new THREE.MeshStandardMaterial({{ color, transparent:true, opacity:0.55 }}));
  cyl.position.copy(mid); cyl.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), dir.normalize()); scene.add(cyl);
}}
bond('Phi210','Sigma126',0x2f6f8f); bond('Phi210','H10',0x8a6a3a);
bond('Sigma126','H10',0x3a7a5a); bond('S','H10',0x6a4a8a); bond('Phi17','S',0x8a3a6a);

const gateGroup = new THREE.Group();
const gateIds = Object.keys(DATA.gates);
gateIds.forEach((g,i) => {{
  const ang = (i/gateIds.length)*Math.PI*2, r=5.6, st=DATA.gates[g];
  const col = st==='OPEN' ? 0xe05a5a : 0xe0a14a;
  const tor = new THREE.Mesh(new THREE.TorusGeometry(0.28,0.08,10,24), new THREE.MeshStandardMaterial({{ color:col, emissive:col, emissiveIntensity:0.35 }}));
  tor.position.set(Math.cos(ang)*r, 0.35, Math.sin(ang)*r); tor.rotation.x = Math.PI/2; gateGroup.add(tor);
  const lab = spriteLabel(g, st==='OPEN' ? '#e05a5a' : '#e0a14a');
  lab.position.set(Math.cos(ang)*r, 0.95, Math.sin(ang)*r); lab.scale.set(1.3,0.35,1); gateGroup.add(lab);
}});
scene.add(gateGroup);

document.getElementById('nClosed').textContent = DATA.certificate.n_closed_subproblems;
document.getElementById('nBlock').textContent = DATA.certificate.n_remaining_blockers;
const gridEl = document.getElementById('gateGrid');
for (const [g,st] of Object.entries(DATA.gates)) {{
  const d = document.createElement('div'); d.className = 'gate '+st; d.textContent = g+'\\n'+st; gridEl.appendChild(d);
}}

const tripletLayout = [
  {{ id:'T10', x:-1.6, z:3.4, color:0x60a5fa }},
  {{ id:'t2', x:-0.5, z:3.4, color:0x34d399 }},
  {{ id:'T10bar', x:0.6, z:3.4, color:0xfbbf24 }},
  {{ id:'t2bar', x:1.7, z:3.4, color:0xfb7185 }},
  {{ id:'t4bar', x:2.8, z:3.4, color:0xa78bfa }},
];
const pillars = {{}};
for (const t of tripletLayout) {{
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.18,0.22,1,18), new THREE.MeshStandardMaterial({{ color:t.color, emissive:t.color, emissiveIntensity:0.22 }}));
  mesh.position.set(t.x, 0.5, t.z); scene.add(mesh);
  const lab = spriteLabel(t.id); lab.position.set(t.x, 1.4, t.z); lab.scale.set(1.4,0.35,1); scene.add(lab);
  pillars[t.id] = mesh;
}}

function kColor(p,a,w) {{ return 2*p*a/Math.sqrt(3) + 2*w*w/3; }}
function computeMasses(kn) {{
  const shift = kn.lambda_hsigma_45 * kn.v_r * kn.v_r;
  const kc = kColor(kn.p, kn.a, kn.omega);
  return {{
    T10: -shift + kn.lambda_phih_45 * kc,
    t2: kn.lambda_phisigma_45 * kc,
    T10bar: +shift - kn.lambda_phih_45 * kc,
    t2bar: -kn.lambda_phisigma_45 * kc,
    t4bar: -kn.lambda_phisigma_45 * kc,
    k_color: kc, hsigma_shift: shift,
  }};
}}
function fmt(x) {{ return (x>=0?'+':'') + x.toFixed(3); }}
function updateUI(m, kn) {{
  document.getElementById('v_lamHS').textContent = kn.lambda_hsigma_45.toFixed(2);
  document.getElementById('v_vr').textContent = kn.v_r.toFixed(2);
  document.getElementById('v_lamPH').textContent = kn.lambda_phih_45.toFixed(2);
  document.getElementById('v_lamPS').textContent = kn.lambda_phisigma_45.toFixed(2);
  document.getElementById('v_p').textContent = kn.p.toFixed(2);
  document.getElementById('v_a').textContent = kn.a.toFixed(2);
  document.getElementById('v_w').textContent = kn.omega.toFixed(2);
  const list = document.getElementById('massList'); list.innerHTML = '';
  for (const id of ['T10','t2','T10bar','t2bar','t4bar']) {{
    const row = document.createElement('div'); row.className='mass';
    row.innerHTML = `<span>${{id}}</span><b>${{fmt(m[id])}}</b>`; list.appendChild(row);
  }}
  for (const [id, mesh] of Object.entries(pillars)) {{
    const h = Math.max(0.15, Math.min(3.8, Math.abs(m[id])*2.2 + 0.2));
    mesh.scale.y = h; mesh.position.y = h/2;
    mesh.material.emissive.setHex((Math.sign(m[id])||1) > 0 ? 0x3ecf8e : 0xe05a5a);
    mesh.material.emissiveIntensity = 0.15 + Math.min(0.55, Math.abs(m[id])*0.35);
  }}
  fieldMeshes.Sigma126.scale.setScalar(0.85 + 0.35*kn.v_r);
  fieldMeshes.Phi210.scale.setScalar(0.9 + 0.25*Math.min(1.5, Math.abs(m.k_color)));
}}

const knobs = {{ ...DATA.scene.knobs }};
const ids = {{ lamHS:'lambda_hsigma_45', vr:'v_r', lamPH:'lambda_phih_45', lamPS:'lambda_phisigma_45', p:'p', a:'a', w:'omega' }};
for (const [el, key] of Object.entries(ids)) {{
  const node = document.getElementById(el); node.value = knobs[key];
  node.addEventListener('input', () => {{ knobs[key] = parseFloat(node.value); updateUI(computeMasses(knobs), knobs); }});
}}
updateUI(computeMasses(knobs), knobs);

window.addEventListener('resize', () => {{
  camera.aspect = stage.clientWidth/stage.clientHeight; camera.updateProjectionMatrix();
  renderer.setSize(stage.clientWidth, stage.clientHeight);
}});
let t0 = performance.now();
function animate(now) {{
  requestAnimationFrame(animate);
  const t = (now-t0)/1000;
  gateGroup.rotation.y = t*0.08;
  fieldMeshes.Phi210.rotation.y = t*0.25;
  fieldMeshes.S.position.y = 3.6 + 0.12*Math.sin(t*1.3);
  fieldMeshes.Phi17.position.y = 3.6 + 0.12*Math.cos(t*1.1);
  controls.update(); renderer.render(scene, camera);
}}
animate(performance.now());
</script>
</body>
</html>
"""


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_HTML.write_text(_html(payload), encoding="utf-8")
    src = next((p for p in CERT_CANDIDATES if p.exists()), None)
    if src is not None:
        shutil.copy2(src, CERT_COPY)
        md_src = src.with_suffix(".md")
        if md_src.exists():
            shutil.copy2(md_src, CERT_MD)
        else:
            CERT_MD.write_text(
                "# Next-generation G1/G6 30-subproblem progress gate — v20\n\n"
                f"**Status:** `{payload['certificate']['status']}`\n\n"
                f"- Exact subproblems closed: {payload['certificate']['n_closed_subproblems']}\n"
                f"- Remaining blockers: {payload['certificate']['n_remaining_blockers']}\n"
                f"- G1: `OPEN` · G6: `PARTIAL`\n",
                encoding="utf-8",
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--v-r", type=float, default=1.0)
    parser.add_argument("--lambda-hsigma-45", type=float, default=0.25)
    args = parser.parse_args(argv)
    payload = build_payload(v_r=args.v_r, lambda_hsigma_45=args.lambda_hsigma_45)
    write_artifacts(payload)
    print(
        json.dumps(
            {
                "html": str(OUT_HTML),
                "json": str(OUT_JSON),
                "certificate": str(CERT_COPY),
                "honesty": payload["honesty"],
                "n_closed": payload["certificate"]["n_closed_subproblems"],
            },
            indent=2,
        )
    )
    if not args.no_open:
        webbrowser.open(OUT_HTML.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
