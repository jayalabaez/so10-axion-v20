#!/usr/bin/env wolframscript

(* External SARAH validation driver for the exact gauged-U(1)_X contract.

   Usage:
     wolframscript -file tools/validate-exact-x-model.wls \
       --repo-root /path/to/repository --sarah-root /path/to/SARAH

   The repository model is staged into SARAH's required directory layout.
   No evidence file is written here: the Python runner records this driver's
   real process exit code and complete output only after an external run. *)

ClearAll[argumentValue, emitCheck, failRemaining, captureEvaluation];

argumentValue[flag_String] := Module[{position},
  position = FirstPosition[$ScriptCommandLine, flag];
  If[
    MissingQ[position] || First[position] >= Length[$ScriptCommandLine],
    Missing["NotProvided"],
    $ScriptCommandLine[[First[position] + 1]]
  ]
];

results = Association[];
emitCheck[name_String, condition_] := Module[{passed = TrueQ[condition]},
  AssociateTo[results, name -> passed];
  Print[
    "EXACT_X_CHECK " <> name <> " " <>
      If[passed, "PASS", "FAIL"]
  ];
  passed
];

requiredChecks = {
  "model_parse_succeeded",
  "model_initialization_succeeded",
  "lagrangian_construction_succeeded",
  "gauge_invariance_check_succeeded",
  "anomaly_check_succeeded"
};

failRemaining[] := Scan[
  If[! KeyExistsQ[results, #], emitCheck[#, False]] &,
  requiredChecks
];

scriptPath = SelectFirst[
  $ScriptCommandLine,
  StringQ[#] && StringEndsQ[ToLowerCase[#], ".wls"] &,
  $InputFileName
];
defaultRepoRoot = ExpandFileName[
  FileNameJoin[{DirectoryName[scriptPath], ".."}]
];
repoArgument = argumentValue["--repo-root"];
repoRoot = ExpandFileName[
  If[MissingQ[repoArgument], defaultRepoRoot, repoArgument]
];
sarahArgument = argumentValue["--sarah-root"];

modelName = "SO10Z17AxionV20";
modelSource = FileNameJoin[{repoRoot, "models", modelName <> ".m"}];

modelText = Quiet[Check[Import[modelSource, "Text"], $Failed]];
heldModel = If[
  StringQ[modelText],
  Quiet[Check[ToExpression[modelText, InputForm, HoldComplete], $Failed]],
  $Failed
];
parseOK = heldModel =!= $Failed;
emitCheck["model_parse_succeeded", parseOK];

If[! parseOK || MissingQ[sarahArgument],
  If[MissingQ[sarahArgument],
    Print["EXACT_X_ERROR required --sarah-root argument was not provided"]
  ];
  failRemaining[];
  Exit[1]
];

sarahRoot = ExpandFileName[sarahArgument];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];
If[! FileExistsQ[sarahEntry],
  Print["EXACT_X_ERROR SARAH.m was not found below --sarah-root"];
  failRemaining[];
  Exit[1]
];

workRoot = CreateDirectory[
  FileNameJoin[{$TemporaryDirectory, "so10-exact-x-" <> CreateUUID[]}]
];
modelDirectory = FileNameJoin[{workRoot, modelName}];
outputDirectory = FileNameJoin[{workRoot, "output"}];
CreateDirectory[modelDirectory];
CreateDirectory[outputDirectory];
CopyFile[
  modelSource,
  FileNameJoin[{modelDirectory, modelName <> ".m"}]
];
Export[FileNameJoin[{modelDirectory, "parameters.m"}], "", "Text"];
Export[FileNameJoin[{modelDirectory, "particles.m"}], "", "Text"];

SetAttributes[captureEvaluation, HoldAll];
captureEvaluation[expression_] := Module[
  {stream, path, completed, content},
  path = FileNameJoin[{workRoot, "capture-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  completed = Block[
    {$Output = {stream}, $Messages = {stream}},
    CheckAbort[expression; True, False]
  ];
  Close[stream];
  content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]];
  {TrueQ[completed], content}
];

loadResult = captureEvaluation[
  Get[sarahEntry];
  Print["EXACT_X_TOOL SARAH " <> ToString[SA`Version]];
  SARAH[InputDirectories] = {workRoot};
  SARAH[OutputDirectory] = outputDirectory;
  Start[modelName]
];

initializationOK = And[
  First[loadResult],
  TrueQ[ModelLoaded],
  TrueQ[AbortStart === False],
  TrueQ[SupersymmetricModel === False],
  ValueQ[SA`LagTermsNonSUSY],
  ListQ[SA`LagTermsNonSUSY],
  Length[SA`LagTermsNonSUSY] > 0
];
emitCheck["model_initialization_succeeded", initializationOK];

lagrangianOK = And[
  initializationOK,
  ValueQ[Lagrangian],
  ValueQ[Potential],
  Lagrangian =!= 0,
  Potential =!= 0
];
emitCheck["lagrangian_construction_succeeded", lagrangianOK];

gaugeOK = False;
If[initializationOK,
  localGaugeResults = Quiet[
    CheckLagTermChargeConservation[#, False] & /@ SA`LagTermsNonSUSY
  ];
  globalGaugeResults = Flatten@Table[
    CheckChargeConservationGlobal[List @@ term, Global[[groupIndex, 2]]],
    {term, SA`LagTermsNonSUSY},
    {groupIndex, 1, Length[Global]}
  ];
  gaugeOK = And[
    Length[localGaugeResults] == Length[SA`LagTermsNonSUSY],
    And @@ (TrueQ /@ localGaugeResults),
    And @@ (TrueQ /@ globalGaugeResults)
  ]
];
emitCheck["gauge_invariance_check_succeeded", gaugeOK];

anomalyOK = False;
If[initializationOK,
  anomalyResult = captureEvaluation[CheckAnomalies];
  anomalyText = Last[anomalyResult];
  anomalyOK = And[
    First[anomalyResult],
    StringContainsQ[anomalyText, "Checking for anomalies"],
    StringFreeQ[anomalyText, "WARNING!"]
  ]
];
emitCheck["anomaly_check_succeeded", anomalyOK];

allPassed = And @@ Lookup[results, requiredChecks, False];
Quiet[Check[DeleteDirectory[workRoot, DeleteContents -> True], Null]];
Exit[If[allPassed, 0, 1]];
