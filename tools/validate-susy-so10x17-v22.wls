#!/usr/bin/env wolframscript

(* Genuine SARAH 4.15.3 initialization audit for the V22 SUSY scaffold. *)

ClearAll[argumentValue, emit, capture];
Print["V22_SARAH_ENGINE Wolfram " <> ToString[$Version]];
Print["V22_SARAH_KERNEL_PATH " <> ToString[First[$CommandLine]]];
argumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
results = Association[];
emit[name_String, condition_] := Module[{ok = TrueQ[condition]},
  AssociateTo[results, name -> ok]; Print["V22_SARAH_CHECK " <> name <> " " <> If[ok, "PASS", "FAIL"]]; ok
];
SetAttributes[capture, HoldAll];
capture[expression_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v22-sarah-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}}, CheckAbort[expression; True, False]];
  Close[stream]; content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]]; {TrueQ[ok], content}
];

repoRoot = ExpandFileName[argumentValue["--repo-root"]];
sarahRoot = ExpandFileName[argumentValue["--sarah-root"]];
modelName = "SO10X17SUSYV22";
modelSource = FileNameJoin[{repoRoot, "models", modelName, modelName <> ".m"}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];

text = Quiet[Check[Import[modelSource, "Text"], $Failed]];
held = If[StringQ[text], Quiet[Check[ToExpression[text, InputForm, HoldComplete], $Failed]], $Failed];
emit["model_parse_succeeded", held =!= $Failed];
If[held === $Failed || ! FileExistsQ[sarahEntry], Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "so10-v22-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
CopyFile[modelSource, FileNameJoin[{modelDir, modelName <> ".m"}]];
Export[FileNameJoin[{modelDir, "parameters.m"}], "ParameterDefinitions = {};\n", "Text"];
Export[FileNameJoin[{modelDir, "particles.m"}], "ParticleDefinitions[GaugeES] = {};\n", "Text"];

Get[sarahEntry];
Print["V22_SARAH_TOOL SARAH " <> ToString[SA`Version]];
d5 = {{2,-1,0,0,0},{-1,2,-1,0,0},{0,-1,2,-1,-1},{0,0,-1,2,0},{0,0,-1,0,2}};
Susyno`LieGroups`repsWithSizeN[d5, 1] = {{0,0,0,0,0}};
Susyno`LieGroups`repsWithSizeN[d5, 10] = {{1,0,0,0,0}};
Susyno`LieGroups`repsWithSizeN[d5, 16] = {{0,0,0,1,0},{0,0,0,0,1}};
Susyno`LieGroups`repsWithSizeN[d5, 120] = {{0,0,1,0,0}};
Susyno`LieGroups`repsWithSizeN[d5, 126] = {{0,0,0,2,0},{0,0,0,0,2}};
Susyno`LieGroups`repsWithSizeN[d5, 210] = {{0,0,0,1,1}};
Scan[(SA`Dynkin2[#[[1]], 10] = #[[2]]; SA`Dynkin2[-#[[1]], 10] = #[[2]]) &,
  {{10,1},{16,2},{120,28},{126,35},{210,56}}];

$RecursionLimit = 3000;
load = capture[
  SARAH[InputDirectories] = {work}; SARAH[OutputDirectory] = outDir; Start[modelName]
];
initialized = And[First[load], TrueQ[ModelLoaded], TrueQ[AbortStart === False],
  TrueQ[SupersymmetricModel], getDynkinLabels[10,SO[10]] === {1,0,0,0,0},
  getDynkinLabels[120,SO[10]] === {0,0,1,0,0},
  MemberQ[{{0,0,0,2,0},{0,0,0,0,2}}, getDynkinLabels[126,SO[10]]],
  getDynkinLabels[210,SO[10]] === {0,0,0,1,1}];
emit["model_initialization_succeeded", initialized];
emit["supersymmetric_potential_constructed", initialized && ValueQ[SuperPotential] && SuperPotential =!= 0];

anomaly = If[initialized, capture[CheckAnomalies], {False, "not initialized"}];
anomalyOK = First[anomaly] && StringContainsQ[Last[anomaly], "Checking for anomalies"] &&
  StringFreeQ[Last[anomaly], "WARNING!"];
emit["sarah_anomaly_check_succeeded", anomalyOK];

modelCheck = If[initialized, capture[CheckModel[]], {False, "not initialized"}];
emit["sarah_model_check_completed_without_abort", First[modelCheck]];

all = And @@ Values[results];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[all, 0, 1]];
