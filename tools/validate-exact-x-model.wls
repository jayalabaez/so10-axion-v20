#!/usr/bin/env wolframscript

(* External SARAH validation driver for the exact gauged-U(1)_X contract.

   Usage:
     wolframscript -file tools/validate-exact-x-model.wls \
       --repo-root /path/to/repository --sarah-root /path/to/SARAH

   The repository model is staged into SARAH's required directory layout.
   No evidence file is written here: the Python runner records this driver's
   real process exit code and complete output only after an external run. *)

ClearAll[argumentValue, emitCheck, failRemaining, captureEvaluation];

Print["EXACT_X_ENGINE Wolfram " <> ToString[$Version]];
Print[
  "EXACT_X_KERNEL_PATH " <>
    ToString[First[$CommandLine]]
];

argumentValue[flag_String] := Module[{position},
  position = FirstPosition[$ScriptCommandLine, flag];
  If[
    MissingQ[position] || First[position] >= Length[$ScriptCommandLine],
    Missing["NotProvided"],
    $ScriptCommandLine[[First[position] + 1]]
  ]
];

exactXResults = Association[];
emitCheck[name_String, condition_] := Module[{passed = TrueQ[condition]},
  AssociateTo[exactXResults, name -> passed];
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
  If[! KeyExistsQ[exactXResults, #], emitCheck[#, False]] &,
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
Export[
  FileNameJoin[{modelDirectory, "parameters.m"}],
  "ParameterDefinitions = {};\n",
  "Text"
];
Export[
  FileNameJoin[{modelDirectory, "particles.m"}],
  "ParticleDefinitions[GaugeES] = {};\n",
  "Text"
];

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

Get[sarahEntry];
  Print["EXACT_X_STAGE sarah_package_loaded"];
  (* SARAH 4.15.3 calls Susyno's dormant repsWithSizeN helper when an
     SO(N) representation is supplied by dimension.  Freeze the complete
     unambiguous D5 lookup used by this model before Start: these are exact
     representation labels, not substituted anomaly results. *)
  d5Cartan = {
    {2, -1, 0, 0, 0}, {-1, 2, -1, 0, 0},
    {0, -1, 2, -1, -1}, {0, 0, -1, 2, 0}, {0, 0, -1, 0, 2}
  };
  Susyno`LieGroups`repsWithSizeN[d5Cartan, 1] = {{0, 0, 0, 0, 0}};
  Susyno`LieGroups`repsWithSizeN[d5Cartan, 10] = {{1, 0, 0, 0, 0}};
  Susyno`LieGroups`repsWithSizeN[d5Cartan, 16] = {
    {0, 0, 0, 1, 0}, {0, 0, 0, 0, 1}
  };
  Susyno`LieGroups`repsWithSizeN[d5Cartan, 126] = {
    {0, 0, 0, 2, 0}, {0, 0, 0, 0, 2}
  };
  Susyno`LieGroups`repsWithSizeN[d5Cartan, 210] = {{0, 0, 0, 1, 1}};
  Print["EXACT_X_STAGE exact_D5_dimension_map_installed"];
  (* CheckAnomalies only initializes quadratic indices for U(1) and SU(N).
     Its generic SO(N) branch is otherwise symbolic and emits a false mixed
     anomaly.  Both D5 spinor chiralities have the exact index T(16)=2. *)
  SA`Dynkin2[16, 10] = 2;
  SA`Dynkin2[-16, 10] = 2;
  Print["EXACT_X_STAGE exact_D5_spinor_indices_installed"];
  (* The non-SUSY charge initializer in SARAH 4.15.3 sends every non-SU
     representation dimension to TestDim[dim,N], a brute-force SU(N) Young
     tableau search.  For SO(10) dimensions 126 and 210 that is both the
     wrong group and prohibitively slow.  Freeze the exact additive Spin(10)
     center charges for the complete representation set in this model.  A
     nonzero center sum still falls through to SARAH's exact Invariants test
     in CheckLagTermChargeConservation. *)
  exactXSO10CenterCharge[dimension_Integer] := Switch[
    dimension,
    1, 0,
    10, 2, -10, -2,
    16, 1, -16, -1,
    126, 2, -126, -2,
    210, 0, -210, 0,
    _, Missing["UnsupportedSO10Representation", dimension]
  ];
  Print["EXACT_X_STAGE exact_D5_center_map_installed"];
  InitChargeFactors := Block[
    {gaugeIndex, fieldIndex, sign, dimension, factor, bareScalar, bareFermion},
    For[gaugeIndex = 1, gaugeIndex <= Length[Gauge], gaugeIndex++,
      For[fieldIndex = 1, fieldIndex <= Length[Fields], fieldIndex++,
        sign = If[
          Head[SFields[[fieldIndex]] //. A_[{b__}] -> A] === conj,
          -1,
          1
        ];
        bareScalar = SFields[[fieldIndex]] /. conj[x_] -> x //. A_[{b__}] -> A;
        bareFermion = FFields[[fieldIndex]] /. conj[x_] -> x //. A_[{b__}] -> A;
        If[Gauge[[gaugeIndex, 2]] === U[1],
          factor = Fields[[fieldIndex, 3 + gaugeIndex]];
          ChargeFactorField[gaugeIndex, Fields[[fieldIndex, 3]]] = factor;
          ChargeFactorField[gaugeIndex, bareScalar] = sign factor;
          ChargeFactorField[gaugeIndex, bareFermion] = sign factor,
          If[Gauge[[gaugeIndex, 2]] === SO[10],
            dimension = FieldDim[fieldIndex, gaugeIndex];
            factor = exactXSO10CenterCharge[dimension];
            If[MissingQ[factor], Abort[]];
            ChargeFactorField[gaugeIndex, Fields[[fieldIndex, 3]]] = factor;
            ChargeFactorField[gaugeIndex, bareScalar] = sign factor;
            ChargeFactorField[gaugeIndex, bareFermion] = sign factor,
            Abort[]
          ]
        ]
      ]
    ]
  ];
  Print["EXACT_X_STAGE exact_SO10_charge_initializer_installed"];
  (* SARAH calls this broken-group CGC generator unconditionally from
     MakeTerms.  The attested Gauge rows both have their breaking flag False,
     so the exact broken-group CGC set is empty.  Fail closed if that model
     invariant ever changes. *)
  Clear[GenerateCGCsForBrokenGroups];
  GenerateCGCsForBrokenGroups[arguments___] := If[
    AllTrue[Gauge, Length[#] >= 5 && #[[5]] === False &],
    Null,
    Abort[]
  ];
  Print["EXACT_X_STAGE empty_broken_group_CGC_contract_installed"];
  Print["EXACT_X_TOOL SARAH " <> ToString[SA`Version]];
$RecursionLimit = 2000;
Print["EXACT_X_STAGE recursion_budget_2000"];
loadResult = captureEvaluation[
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
  Length[SA`LagTermsNonSUSY] > 0,
  getDynkinLabels[10, SO[10]] === {1, 0, 0, 0, 0},
  getDynkinLabels[16, SO[10]] === {0, 0, 0, 0, 1},
  getDynkinLabels[-16, SO[10]] === {0, 0, 0, 1, 0},
  getDynkinLabels[-126, SO[10]] === {0, 0, 0, 2, 0},
  getDynkinLabels[210, SO[10]] === {0, 0, 0, 1, 1},
  exactXSO10CenterCharge[1] === 0,
  exactXSO10CenterCharge[10] === 2,
  exactXSO10CenterCharge[16] === 1,
  exactXSO10CenterCharge[-16] === -1,
  exactXSO10CenterCharge[126] === 2,
  exactXSO10CenterCharge[-126] === -2,
  exactXSO10CenterCharge[210] === 0
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
  WriteString[$Output,
    "EXACT_X_GAUGE_LOCAL_RESULTS " <>
      ToString[localGaugeResults, InputForm] <> "\n"
  ];
  WriteString[$Output,
    "EXACT_X_GAUGE_GLOBAL_RESULTS " <>
      ToString[globalGaugeResults, InputForm] <> "\n"
  ];
  WriteString[$Output,
    "EXACT_X_GAUGE_GLOBAL_FACTORS " <>
      ToString[
        ({List @@ #,
          SA`ChargeGlobal[#, Global[[1, 2]]] & /@ (List @@ #),
          Times @@ (SA`ChargeGlobal[#, Global[[1, 2]]] & /@ (List @@ #))} & /@
          SA`LagTermsNonSUSY),
        InputForm
      ] <> "\n"
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

allPassed = And @@ Lookup[exactXResults, requiredChecks, False];
Quiet[Check[DeleteDirectory[workRoot, DeleteContents -> True], Null]];
Exit[If[allPassed, 0, 1]];
