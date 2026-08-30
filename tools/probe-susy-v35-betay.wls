#!/usr/bin/env wolframscript

(* V35 feasibility probe for literal component preparation of SARAH BetaY. *)
ClearAll[v35ArgumentValue, v35Capture];
v35ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
SetAttributes[v35Capture, HoldAll];
v35Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v35-betay-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}},
    CheckAbort[heldExpr; True, False]
  ];
  Close[stream];
  content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]];
  {TrueQ[ok], content}
];

repoRoot = ExpandFileName[v35ArgumentValue["--repo-root"]];
sarahRoot = ExpandFileName[v35ArgumentValue["--sarah-root"]];
outputPath = ExpandFileName[v35ArgumentValue["--output"]];
modelName = "PSZ4RZ33SUSYV33";
sourceDir = FileNameJoin[{repoRoot, "models", modelName}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];
If[!FileExistsQ[sarahEntry], Print["V35_BETAY_ERROR missing SARAH.m"]; Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v35-betay-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
Scan[CopyFile[#, FileNameJoin[{modelDir, FileNameTake[#]}]] &, FileNames["*.m", sourceDir]];

Get[sarahEntry];
$RecursionLimit = 6000;
SARAH[InputDirectories] = {work};
SARAH[OutputDirectory] = outDir;
load = v35Capture[Start[modelName]];
initialized = First[load] && TrueQ[ModelLoaded] && TrueQ[AbortStart === False];
If[!initialized,
  Print["V35_BETAY_ERROR model initialization failed"];
  Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
  Exit[1]
];

rge = v35Capture[CalcRGEs[TwoLoop -> True]];
calculated = First[rge] && ListQ[BetaYijk] && Length[BetaYijk] === 16;
If[!calculated,
  Print["V35_BETAY_ERROR CalcRGEs failed"];
  Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
  Exit[1]
];

rawYijkDownValues = ToString[DownValues[Yijk], InputForm];
rawInvMatDownValues = ToString[DownValues[InvMat], InputForm];
rawInvMatSubValues = ToString[SubValues[InvMat], InputForm];
invMat1 = Table[InvMat[1][i, j, k], {i, 1, 4}, {j, 1, 4}, {k, 1, 6}];
invMat2 = Table[InvMat[2][i, j, k], {i, 1, 4}, {j, 1, 4}, {k, 1, 6}];
invMat3 = Table[InvMat[3][i, j], {i, 1, 6}, {j, 1, 6}];
rawEpsTensorDownValues = ToString[DownValues[epsTensor], InputForm];
rawBeta = ToString[BetaYijk, InputForm];
allSuperpotentialBetas = Join[BetaYijk, BetaMuij, BetaLi];
prepare = v35Capture[
  PrepareRGEs[
    OnlyDiagonal -> False,
    BetaFunctions -> {BetaYijk},
    ComplexPhases -> True
  ]
];
prepared = First[prepare] && ListQ[AllEquations] && Length[AllEquations] > 0;
preparedStrings = If[prepared, ToString[#, InputForm] & /@ AllEquations, {}];

parameterDimensions = Association @@ Map[
  Function[row,
    With[{parameter = If[Head[row[[1]]] === Symbol, row[[1]], Head[row[[1]]]]},
      ToString[parameter, InputForm] ->
        (getDimParameter[parameter] /. {} -> {1})
    ]
  ],
  BetaYijk
];

payload = <|
  "schema" -> "susy-v35-live-sarah-betay-feasibility-probe-v1",
  "engine" -> ToString[$Version],
  "tool" -> ("SARAH " <> ToString[SA`Version]),
  "model" -> modelName,
  "model_initialized" -> initialized,
  "two_loop_RGE_calculation_succeeded" -> calculated,
  "BetaYijk_count" -> Length[BetaYijk],
  "parameter_dimensions" -> parameterDimensions,
  "Yijk_downvalues_sha256" -> IntegerString[Hash[rawYijkDownValues, "SHA256"], 16, 64],
  "Yijk_downvalues_input_form" -> rawYijkDownValues,
  "InvMat_downvalues_sha256" -> IntegerString[Hash[rawInvMatDownValues, "SHA256"], 16, 64],
  "InvMat_downvalues_input_form" -> rawInvMatDownValues,
  "InvMat_subvalues_sha256" -> IntegerString[Hash[rawInvMatSubValues, "SHA256"], 16, 64],
  "InvMat_subvalues_input_form" -> rawInvMatSubValues,
  "InvMat1_4x4x6_input_form" -> ToString[invMat1, InputForm],
  "InvMat2_4x4x6_input_form" -> ToString[invMat2, InputForm],
  "InvMat3_6x6_input_form" -> ToString[invMat3, InputForm],
  "epsTensor_downvalues_sha256" -> IntegerString[
    Hash[rawEpsTensorDownValues, "SHA256"], 16, 64
  ],
  "epsTensor_downvalues_input_form" -> rawEpsTensorDownValues,
  "SA_NonZeroEntries_input_form" -> ToString[SA`NonZeroEntries, InputForm],
  "listWtriOne_input_form" -> ToString[listWtriOne, InputForm],
  "listWtri_input_form" -> ToString[listWtri, InputForm],
  "LP_input_form" -> ToString[LP, InputForm],
  "Fields_input_form" -> ToString[Fields, InputForm],
  "ListFields_input_form" -> ToString[ListFields, InputForm],
  "raw_BetaYijk_sha256" -> IntegerString[Hash[rawBeta, "SHA256"], 16, 64],
  "raw_superpotential_sector_boundaries" -> <|
    "trilinear" -> Length[BetaYijk],
    "bilinear" -> Length[BetaMuij],
    "linear" -> Length[BetaLi]
  |>,
  "raw_superpotential_unresolved_epsTensor_counts" -> <|
    "one_loop" -> Count[allSuperpotentialBetas[[All, 2]], _epsTensor, Infinity],
    "two_loop" -> Count[allSuperpotentialBetas[[All, 3]], _epsTensor, Infinity],
    "total" -> Count[allSuperpotentialBetas[[All, {2, 3}]], _epsTensor, Infinity]
  |>,
  "PrepareRGEs_succeeded" -> prepared,
  "prepared_equation_count" -> Length[preparedStrings],
  "prepared_equation_input_form" -> preparedStrings,
  "prepared_equations_sha256" -> IntegerString[
    Hash[ToString[If[prepared, AllEquations, {}], InputForm], "SHA256"], 16, 64
  ],
  "unresolved_symbol_counts" -> <|
    "epsTensor" -> If[prepared, Count[AllEquations, _epsTensor, Infinity], -1],
    "InvMat" -> If[prepared, Count[AllEquations, _InvMat, Infinity], -1],
    "Delta" -> If[prepared, Count[AllEquations, _Delta, Infinity], -1],
    "sum" -> If[prepared, Count[AllEquations, _sum, Infinity], -1],
    "MatMul" -> If[prepared, Count[AllEquations, _MatMul, Infinity], -1],
    "trace" -> If[prepared, Count[AllEquations, _trace, Infinity], -1],
    "ScalarProd" -> If[prepared, Count[AllEquations, _ScalarProd, Infinity], -1]
  |>,
  "prepare_log" -> Last[prepare]
|>;

Export[outputPath, payload, "RawJSON"];
Print["V35_BETAY_PREPARED_COUNT " <> ToString[payload["prepared_equation_count"]]];
Print["V35_BETAY_UNRESOLVED " <> ToString[payload["unresolved_symbol_counts"], InputForm]];
Print["V35_BETAY_STATUS " <> If[prepared, "PASS", "FAIL"]];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[prepared, 0, 1]];
