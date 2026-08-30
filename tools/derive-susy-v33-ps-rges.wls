#!/usr/bin/env wolframscript

(* Live SARAH derivation probe for the V33 Pati--Salam campaign. *)
ClearAll[v33ArgumentValue, v33Capture];
v33ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
SetAttributes[v33Capture, HoldAll];
v33Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v33-ps-rge-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}},
    CheckAbort[heldExpr; True, False]
  ];
  Close[stream];
  content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]];
  {TrueQ[ok], content}
];

repoRoot = ExpandFileName[v33ArgumentValue["--repo-root"]];
sarahRoot = ExpandFileName[v33ArgumentValue["--sarah-root"]];
outputPath = ExpandFileName[v33ArgumentValue["--output"]];
softMirror = MemberQ[$ScriptCommandLine, "--soft-mirror"];
softMirrorSourceSHA256 = Missing["NotApplicable"];
modelArgument = v33ArgumentValue["--model"];
modelName = If[MissingQ[modelArgument], "PSZ4RZ11SUSYV24", modelArgument];
sourceDir = FileNameJoin[{repoRoot, "models", modelName}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];
If[!FileExistsQ[sarahEntry], Print["V33_PS_RGE_ERROR missing SARAH.m"]; Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v33-ps-rge-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
Scan[CopyFile[#, FileNameJoin[{modelDir, FileNameTake[#]}]] &, FileNames["*.m", sourceDir]];
If[softMirror,
  modelPath = FileNameJoin[{modelDir, modelName <> ".m"}];
  modelText = Import[modelPath, "Text"];
  modelText = StringReplace[modelText, {
    "AddSoftTerms = False;" -> "AddSoftTerms = True;",
    "AddSoftScalarMasses = False;" -> "AddSoftScalarMasses = True;",
    "AddSoftGauginoMasses = False;" -> "AddSoftGauginoMasses = True;"
  }];
  softMirrorSourceSHA256 = IntegerString[Hash[modelText, "SHA256"], 16, 64];
  Export[modelPath, modelText, "Text"];
];

Get[sarahEntry];
$RecursionLimit = 5000;
SARAH[InputDirectories] = {work};
SARAH[OutputDirectory] = outDir;
load = v33Capture[Start[modelName]];
initialized = First[load] && TrueQ[ModelLoaded] && TrueQ[AbortStart === False];
If[!initialized,
  Print["V33_PS_RGE_ERROR model initialization failed"];
  Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
  Exit[1]
];

rge = v33Capture[CalcRGEs[TwoLoop -> True]];
calculated = First[rge] && ListQ[BetaGauge] && Length[BetaGauge] === 3 &&
  ListQ[BetaYijk] && Length[BetaYijk] > 0;

payload = <|
  "schema" -> "susy-v33-live-sarah-rge-attestation-v1",
  "engine" -> ToString[$Version],
  "tool" -> ("SARAH " <> ToString[SA`Version]),
  "model" -> modelName,
  "mode" -> If[softMirror, "formal_soft_mirror", "declared_source"],
  "model_initialized" -> initialized,
  "two_loop_RGE_calculation_succeeded" -> calculated,
  "source_soft_terms_enabled" -> TrueQ[AddSoftTerms],
  "soft_mirror_source_sha256" -> If[softMirror, softMirrorSourceSHA256, Null],
  "beta_counts" -> <|
    "gauge" -> If[ListQ[BetaGauge], Length[BetaGauge], -1],
    "trilinear_superpotential" -> If[ListQ[BetaYijk], Length[BetaYijk], -1],
    "bilinear_superpotential" -> If[ListQ[BetaMuij], Length[BetaMuij], -1],
    "linear_superpotential" -> If[ListQ[BetaLi], Length[BetaLi], -1],
    "soft_trilinear" -> If[ListQ[BetaTijk], Length[BetaTijk], -1],
    "soft_bilinear" -> If[ListQ[BetaBij], Length[BetaBij], -1],
    "soft_linear" -> If[ListQ[BetaLSi], Length[BetaLSi], -1],
    "soft_scalar_mass" -> If[ListQ[Betam2ij], Length[Betam2ij], -1],
    "gaugino_mass" -> If[ListQ[BetaMi], Length[BetaMi], -1]
  |>,
  "one_loop_gauge_coefficients_input_form" -> If[
    ListQ[BetaGauge] && Length[BetaGauge] === 3,
    ToString[#[[2]], InputForm] & /@ BetaGauge,
    {}
  ],
  "beta_gauge_input_form" -> (ToString[#, InputForm] & /@ If[ListQ[BetaGauge], BetaGauge, {}]),
  "beta_superpotential_input_form" -> (ToString[#, InputForm] & /@ Join[
    If[ListQ[BetaYijk], BetaYijk, {}],
    If[ListQ[BetaMuij], BetaMuij, {}],
    If[ListQ[BetaLi], BetaLi, {}]
  ]),
  "soft_beta_expression_sha256" -> IntegerString[
    Hash[ToString[{
      If[ListQ[BetaTijk], BetaTijk, {}], If[ListQ[BetaBij], BetaBij, {}],
      If[ListQ[BetaLSi], BetaLSi, {}], If[ListQ[Betam2ij], Betam2ij, {}],
      If[ListQ[BetaMi], BetaMi, {}]
    }, InputForm], "SHA256"], 16, 64],
  "boundary" -> If[softMirror,
    "This formal mirror turns on the standard SARAH soft completion and derives its beta system, but no mediation boundary or microscopic SUSY-breaking source is supplied.",
    "The declared source explicitly disables soft terms; this attests supersymmetric gauge and superpotential RGEs, not a mediation boundary or pole spectrum."
  ]
|>;

Export[outputPath, payload, "RawJSON"];
Print["V33_PS_RGE_ENGINE " <> ToString[$Version]];
Print["V33_PS_RGE_TOOL SARAH " <> ToString[SA`Version]];
Print["V33_PS_RGE_GAUGE_COUNT " <> ToString[payload["beta_counts"]["gauge"]]];
Print["V33_PS_RGE_SUPERPOTENTIAL_COUNT " <>
  ToString[payload["beta_counts"]["trilinear_superpotential"] +
    payload["beta_counts"]["bilinear_superpotential"] +
    payload["beta_counts"]["linear_superpotential"]]];
Print["V33_PS_RGE_SOFT_ENABLED " <> ToString[payload["source_soft_terms_enabled"]]];
Print["V33_PS_RGE_STATUS " <> If[calculated, "PASS", "FAIL"]];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[calculated, 0, 1]];
