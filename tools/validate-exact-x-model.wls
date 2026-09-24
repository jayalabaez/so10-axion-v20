#!/usr/bin/env wolframscript

(* External SARAH validation driver for the exact gauged-U(1)_X contract.

   Usage:
     wolframscript -file tools/validate-exact-x-model.wls \
       --repo-root /path/to/repository --sarah-root /path/to/SARAH

   The repository model is staged into SARAH's required directory layout.
   No evidence file is written here: the Python runner records this driver's
   real process exit code and complete output only after an external run.

   SARAH 4.15.3 compatibility (exact, fail-closed).  SARAH's non-SUSY path was
   written for SU(N) x U(1) models; three of its routines are wrong or never
   terminate for an SO(10) gauge factor.  They are replaced below by exact
   equivalents that use SARAH's own bundled Susyno Lie-algebra engine:

   1. InitChargeFactors sends every non-U(1) representation to TestDim, a
      brute-force SU(N) Young-tableau search.  For SO(10) that is the wrong
      group (it matched the 210 to Lambda^4 of SU(10)) and never terminates
      for the 126.  The replacement keeps SARAH's U(1) rule and gives each
      SO(10) irrep a distinct power of ten, so a term's charge-factor sum
      vanishes only when every irrep is paired with its conjugate (which
      always contains a singlet); every other term reaches SARAH's exact
      Susyno Invariants test in CheckLagTermChargeConservation.
   2. GenerateQuadraticAndCubicDynkins initializes quadratic indices only for
      U(1) and SU(N), so CheckAnomalies reports a false SO(10)^2 x U(1)_X
      anomaly.  The SO(10) indices are supplied by Susyno's DynkinIndex.
   3. Any remaining TestDim call aborts the run instead of hanging.
   4. SA`ChargeGlobal[conj[p], Z[N]] returns p's own phase.  That is right
      only for N = 2; for Z17 the conjugate field carries the inverse phase.
      The replacement returns 1/phase for Z[N] (identical for Z2) and keeps
      SARAH's sign flip for U(1) globals.
   5. MakeIndexStructureRGEnonSUSY calls getDynkinLabels[dim, N] with the
      bare integer N of the gauge factor, which selects the SU(N) path.
      For this model's only rank-10 factor, SO(10), N = 10 is routed to the
      Susyno SO(10) lookup.
   6. GenerateCGCsForBrokenGroups appends to an uninitialized global `sign`;
      unset, `sign = Join[sign, {...}]` recurses without bound.  SARAH's
      routine is run unchanged with `sign` localized to {}.

   After Start, every registered Lagrangian term is re-verified independently
   (U(1)_X charge sum, Z17 phase product, exact Susyno SO(10) invariant count)
   and the anomaly sums are recomputed from the field table.

   Symbol hygiene: nothing in Global` may exist before SARAH loads under a
   name that SARAH pre-declares in Susyno`LieGroups` (notably conj).  If it
   did, SARAH's code would bind to the Global` symbol while the model file,
   read later, binds to Susyno's, and every conj[...] field would silently
   drop out of its Lagrangian term.  The parse check therefore runs in a
   private context and driver-level pattern names carry the exactX prefix. *)

ClearAll[exactXArgument, exactXEmitCheck, exactXFailRemaining, exactXCapture];

exactXT0 = AbsoluteTime[];
exactXStage[label_String] := Print[
  "EXACT_X_STAGE " <> label <> " t=" <>
    ToString[NumberForm[AbsoluteTime[] - exactXT0, {8, 2}]] <> "s"
];

exactXArgument[flag_String] := Module[{position},
  position = FirstPosition[$ScriptCommandLine, flag];
  If[
    MissingQ[position] || First[position] >= Length[$ScriptCommandLine],
    Missing["NotProvided"],
    $ScriptCommandLine[[First[position] + 1]]
  ]
];

exactXResults = Association[];
exactXEmitCheck[exactXCheckName_String, exactXCondition_] := Module[
  {exactXPassed = TrueQ[exactXCondition]},
  AssociateTo[exactXResults, exactXCheckName -> exactXPassed];
  Print[
    "EXACT_X_CHECK " <> exactXCheckName <> " " <>
      If[exactXPassed, "PASS", "FAIL"]
  ];
  exactXPassed
];

exactXRequiredChecks = {
  "model_parse_succeeded",
  "model_initialization_succeeded",
  "lagrangian_construction_succeeded",
  "gauge_invariance_check_succeeded",
  "anomaly_check_succeeded"
};

exactXFailRemaining[] := Scan[
  If[! KeyExistsQ[exactXResults, #], exactXEmitCheck[#, False]] &,
  exactXRequiredChecks
];

exactXScriptPath = SelectFirst[
  $ScriptCommandLine,
  StringQ[#] && StringEndsQ[ToLowerCase[#], ".wls"] &,
  $InputFileName
];
exactXDefaultRepoRoot = ExpandFileName[
  FileNameJoin[{DirectoryName[exactXScriptPath], ".."}]
];
exactXRepoArgument = exactXArgument["--repo-root"];
exactXRepoRoot = ExpandFileName[
  If[MissingQ[exactXRepoArgument], exactXDefaultRepoRoot, exactXRepoArgument]
];
exactXSarahArgument = exactXArgument["--sarah-root"];

exactXModelName = "SO10Z17AxionV20";
exactXModelSource = FileNameJoin[{exactXRepoRoot, "models", exactXModelName <> ".m"}];

exactXModelText = Quiet[Check[Import[exactXModelSource, "Text"], $Failed]];
(* Parse in a private context so no model symbol (e.g. conj) enters Global`
   before SARAH defines its own. *)
exactXHeldModel = If[
  StringQ[exactXModelText],
  Block[{$Context = "ExactXModelParse`", $ContextPath = {"System`"}},
    Quiet[Check[ToExpression[exactXModelText, InputForm, HoldComplete], $Failed]]
  ],
  $Failed
];
exactXParseOK = exactXHeldModel =!= $Failed;
exactXEmitCheck["model_parse_succeeded", exactXParseOK];

If[! exactXParseOK || MissingQ[exactXSarahArgument],
  If[MissingQ[exactXSarahArgument],
    Print["EXACT_X_ERROR required --sarah-root argument was not provided"]
  ];
  exactXFailRemaining[];
  Exit[1]
];

exactXSarahRoot = ExpandFileName[exactXSarahArgument];
exactXSarahEntry = FileNameJoin[{exactXSarahRoot, "SARAH.m"}];
If[! FileExistsQ[exactXSarahEntry],
  Print["EXACT_X_ERROR SARAH.m was not found below --sarah-root"];
  exactXFailRemaining[];
  Exit[1]
];

exactXWorkRoot = CreateDirectory[
  FileNameJoin[{$TemporaryDirectory, "so10-exact-x-" <> CreateUUID[]}]
];
exactXModelDirectory = FileNameJoin[{exactXWorkRoot, exactXModelName}];
exactXOutputDirectory = FileNameJoin[{exactXWorkRoot, "output"}];
CreateDirectory[exactXModelDirectory];
CreateDirectory[exactXOutputDirectory];
CopyFile[
  exactXModelSource,
  FileNameJoin[{exactXModelDirectory, exactXModelName <> ".m"}]
];
(* SARAH requires both files; the contract defines no particle or parameter
   metadata beyond the model file, so each holds an explicit empty list. *)
Export[
  FileNameJoin[{exactXModelDirectory, "parameters.m"}],
  "ParameterDefinitions = {};\n",
  "Text"
];
Export[
  FileNameJoin[{exactXModelDirectory, "particles.m"}],
  "ParticleDefinitions[GaugeES] = {};\n",
  "Text"
];

SetAttributes[exactXCapture, HoldAll];
exactXCapture[exactXExpression_] := Module[
  {exactXStream, exactXPath, exactXCompleted, exactXContent},
  exactXPath = FileNameJoin[{exactXWorkRoot, "capture-" <> CreateUUID[] <> ".log"}];
  exactXStream = OpenWrite[exactXPath, CharacterEncoding -> "UTF-8"];
  exactXCompleted = Block[
    {$Output = {exactXStream}, $Messages = {exactXStream}},
    CheckAbort[exactXExpression; True, False]
  ];
  Close[exactXStream];
  exactXContent = Quiet[Check[Import[exactXPath, "Text"], ""]];
  If[StringLength[exactXContent] > 0, Print[exactXContent]];
  {TrueQ[exactXCompleted], exactXContent}
];

(* Load SARAH and its bundled Susyno engine before installing the exact
   SO(10) routines, so the definitions below bind to SARAH's own symbols. *)
exactXLoad = exactXCapture[Get[exactXSarahEntry]];
Print["EXACT_X_TOOL SARAH " <> ToString[SA`Version]];
exactXStage["sarah_loaded"];

(* Start[] loads SARAH's bundled Susyno (InitSusyno) before any hook below
   is evaluated; the Cartan matrix is therefore resolved lazily. *)
exactXSO10 := SusynoForm[SO[10]];
exactXSusynoReady := MatrixQ[exactXSO10, IntegerQ] && Dimensions[exactXSO10] === {5, 5};

(* 3. No SU(N) factor exists in this model: any TestDim call is a defect. *)
exactXTestDimCalls = {};
Clear[TestDim];
TestDim[exactXTestDimArguments___] := (
  AppendTo[exactXTestDimCalls, {exactXTestDimArguments}];
  Print[
    "EXACT_X_ERROR SARAH invoked its SU(N) Young-tableau search TestDim" <>
      ToString[{exactXTestDimArguments}, InputForm] <>
      " for a model without SU(N) factors"
  ];
  Print["EXACT_X_ERROR_STACK ", ToString[DeleteDuplicates[Stack[]], InputForm]];
  Abort[]
);

(* 2. Exact SO(10) quadratic Dynkin indices (Susyno normalization T(10)=1),
   keyed like SARAH's SA`Dynkin2[signed dimension, N]. *)
SA`Dynkin2[dimension_Integer, 10] /; exactXSusynoReady :=
  SA`Dynkin2[dimension, 10] = If[
    Abs[dimension] === 1,
    0,
    DynkinIndex[exactXSO10, getDynkinLabels[dimension, SO[10]]]
  ];

(* 1. Exact charge factors: SARAH's U(1) rule, and a distinct power of ten
   per SO(10) irrep.  Terms have at most four fields, so a zero sum forces
   every irrep to be paired with its conjugate. *)
exactXIrrepWeights = Association[];
exactXIrrepWeight[labels_List] := Lookup[
  exactXIrrepWeights,
  Key[labels],
  exactXIrrepWeights[labels] = 10^(Length[exactXIrrepWeights] + 1)
];
InitChargeFactors := Block[
  {groupIndex, fieldIndex, sign, dimension, factor, bareScalar, bareFermion},
  For[groupIndex = 1, groupIndex <= Length[Gauge], groupIndex++,
    For[fieldIndex = 1, fieldIndex <= Length[Fields], fieldIndex++,
      sign = If[Head[SFields[[fieldIndex]] //. A_[{b__}] -> A] === conj, -1, 1];
      bareScalar = SFields[[fieldIndex]] /. conj[x_] -> x //. A_[{b__}] -> A;
      bareFermion = FFields[[fieldIndex]] /. conj[x_] -> x //. A_[{b__}] -> A;
      Which[
        Gauge[[groupIndex, 2]] === U[1],
          factor = Fields[[fieldIndex, 3 + groupIndex]],
        Gauge[[groupIndex, 2]] === SO[10],
          dimension = FieldDim[fieldIndex, groupIndex];
          factor = If[
            Abs[dimension] === 1,
            0,
            exactXIrrepWeight[getDynkinLabels[dimension, SO[10]]]
          ],
        True,
          Print["EXACT_X_ERROR unsupported gauge factor ", Gauge[[groupIndex, 2]]];
          Abort[]
      ];
      ChargeFactorField[groupIndex, Fields[[fieldIndex, 3]]] = factor;
      ChargeFactorField[groupIndex, bareScalar] = sign factor;
      ChargeFactorField[groupIndex, bareFermion] = sign factor
    ]
  ]
];
(* 5. The non-SUSY RGE index builder passes the bare integer N of a gauge
   factor to getDynkinLabels, which is SARAH's SU(N) Young-tableau path.
   With SO(10) as the only rank-10 factor, N = 10 means SO(10). *)
getDynkinLabels[dimension_, 10] /; And[
    MemberQ[Gauge[[All, 2]], SO[10]],
    FreeQ[Gauge[[All, 2]], SU[10]]
  ] := getDynkinLabels[dimension, SO[10]];

(* 6. GenerateCGCsForBrokenGroups appends to a global `sign` that it never
   initializes (sign = Join[sign, {...}]).  With `sign` unset that assignment
   is self-referential and recurses without bound; stock SARAH only escapes
   because its InitChargeFactors leaks a scalar `sign`.  Run SARAH's routine
   unchanged, with `sign` localized to an empty list. *)
DownValues[GenerateCGCsForBrokenGroups] = Prepend[
  DownValues[GenerateCGCsForBrokenGroups],
  HoldPattern[GenerateCGCsForBrokenGroups[exactXArguments___]] :>
    Internal`InheritedBlock[{GenerateCGCsForBrokenGroups},
      DownValues[GenerateCGCsForBrokenGroups] =
        Rest[DownValues[GenerateCGCsForBrokenGroups]];
      Block[{sign = {}}, GenerateCGCsForBrokenGroups[exactXArguments]]
    ]
];
Print["EXACT_X_CONTEXT sign=", Context[sign]];

(* 4. Conjugated fields carry the inverse Z[N] phase. *)
SA`ChargeGlobal[conj[p_], x_] := Block[{position},
  position = Position[Global, x][[1, 1]];
  Which[
    Global[[position, 1]] === U[1], -SA`ChargeGlobal[p, x],
    MatchQ[Global[[position, 1]], Z[_Integer]], 1/SA`ChargeGlobal[p, x],
    True, SA`ChargeGlobal[p, x]
  ]
];
exactXStage["exact_SO10_routines_installed"];


exactXStartLimit = 3600;
exactXLoadResult = exactXCapture[
  SARAH[InputDirectories] = {exactXWorkRoot};
  SARAH[OutputDirectory] = exactXOutputDirectory;
  If[
    TimeConstrained[Start[exactXModelName]; True, exactXStartLimit, False] =!= True,
    Print["EXACT_X_ERROR SARAH Start exceeded ", exactXStartLimit, " s"];
    Abort[]
  ]
];
exactXStage["sarah_start_returned"];

(* Independent expectations read from the evaluated model definitions. *)
exactXTermCount[expression_] := Which[
  Head[Expand[expression]] === Plus, Length[Expand[expression]],
  Expand[expression] === 0, 0,
  True, 1
];
exactXExpectedTerms = exactXTermCount[LagHC] + exactXTermCount[LagNoHC];
exactXFieldRow[name_] := Module[{position = Position[Fields[[All, 3]], name, {1}, 1]},
  If[position === {}, Missing["UnknownField", name], Fields[[position[[1, 1]]]]]
];
exactXExpectedLabels = <|
  1 -> {0}, 10 -> {1, 0, 0, 0, 0}, 16 -> {0, 0, 0, 0, 1},
  -16 -> {0, 0, 0, 1, 0}, -126 -> {0, 0, 0, 2, 0},
  (* the four-form; SO(10) also has a symmetric 210' = (3,0,0,0,0) *)
  210 -> {0, 0, 0, 1, 1}
|>;
exactXSO10Index = FirstPosition[Gauge[[All, 2]], SO[10], {Missing[]}, {1}][[1]];
exactXXIndex = FirstPosition[Gauge[[All, 2]], U[1], {Missing[]}, {1}][[1]];
exactXFieldLabels = If[
  IntegerQ[exactXSO10Index] && ListQ[Fields],
  Association @ Table[
    row[[3]] -> getDynkinLabels[row[[3 + exactXSO10Index]], SO[10]],
    {row, Fields}
  ],
  <||>
];
Scan[
  Print[
    "EXACT_X_FIELD ", #[[3]],
    " SO10=", #[[3 + exactXSO10Index]],
    " labels=", ToString[exactXFieldLabels[#[[3]]], InputForm],
    " T=", ToString[SA`Dynkin2[#[[3 + exactXSO10Index]], 10], InputForm],
    " X=", #[[3 + exactXXIndex]],
    " Z17=", ToString[SA`ChargeGlobal[#[[3]], Z17], InputForm],
    " generations=", #[[2]]
  ] &,
  If[ListQ[Fields] && IntegerQ[exactXSO10Index] && IntegerQ[exactXXIndex], Fields, {}]
];
exactXLabelsExact = And @@ KeyValueMap[
  Function[{name, labels},
    With[{dimension = exactXFieldRow[name][[3 + exactXSO10Index]]},
      KeyExistsQ[exactXExpectedLabels, dimension] &&
        (labels === exactXExpectedLabels[dimension] ||
          (Abs[dimension] === 1 && MatchQ[labels, {0} | {0, 0, 0, 0, 0}]))
    ]
  ],
  exactXFieldLabels
];

exactXInitializationOK = And[
  First[exactXLoad],
  First[exactXLoadResult],
  exactXSusynoReady,
  exactXTestDimCalls === {},
  TrueQ[ModelLoaded],
  TrueQ[AbortStart === False],
  TrueQ[SupersymmetricModel === False],
  ValueQ[SA`LagTermsNonSUSY],
  ListQ[SA`LagTermsNonSUSY],
  Length[SA`LagTermsNonSUSY] > 0,
  Length[exactXFieldLabels] === Length[Fields],
  TrueQ[exactXLabelsExact]
];
exactXEmitCheck["model_initialization_succeeded", exactXInitializationOK];

Print[
  "EXACT_X_LAGRANGIAN registered_terms=", Length[SA`LagTermsNonSUSY],
  " expected_terms=", exactXExpectedTerms
];
exactXLagrangianOK = And[
  exactXInitializationOK,
  ValueQ[Lagrangian],
  ValueQ[Potential],
  Lagrangian =!= 0,
  Potential =!= 0,
  Length[SA`LagTermsNonSUSY] === exactXExpectedTerms
];
exactXEmitCheck["lagrangian_construction_succeeded", exactXLagrangianOK];

(* Independent per-term audit with SARAH's own field table and Susyno. *)
exactXTermAudit[term_] := Module[
  {entries, conjugated, names, rows, xSum, phase, reps, invariantCount},
  entries = List @@ term;
  (* SARAH's own test (CheckLagTermChargeConservation); a pattern such as
     bar[_] must not be used here because SARAH gives bar definitions. *)
  conjugated = (Head[#] === conj || Head[#] === bar) & /@ entries;
  names = RE /@ entries;
  rows = exactXFieldRow /@ names;
  If[AnyTrue[rows, MissingQ], Return[<|"term" -> term, "valid" -> False|>]];
  xSum = Total[MapThread[If[#2, -1, 1] #1[[3 + exactXXIndex]] &, {rows, conjugated}]];
  phase = Simplify[Times @@ MapThread[
    With[{charge = SA`ChargeGlobal[#1[[3]], Z17]}, If[#2, 1/charge, charge]] &,
    {rows, conjugated}
  ]];
  reps = DeleteCases[
    MapThread[
      With[{labels = getDynkinLabels[#1[[3 + exactXSO10Index]], SO[10]]},
        Which[
          MatchQ[labels, {0} | {0, 0, 0, 0, 0}], Nothing,
          #2, ConjugateIrrep[exactXSO10, labels],
          True, labels
        ]
      ] &,
      {rows, conjugated}
    ],
    Nothing
  ];
  invariantCount = If[reps === {}, 1, Length[Invariants[exactXSO10, reps]]];
  <|
    "term" -> term,
    "x_sum" -> xSum,
    "z17_phase" -> phase,
    "so10_reps" -> reps,
    "so10_invariants" -> invariantCount,
    "sarah_local" -> TrueQ[Quiet[CheckLagTermChargeConservation[term, False]]],
    "sarah_global" -> TrueQ[CheckChargeConservationGlobal[entries, Z17]],
    "valid" -> True
  |>
];

exactXGaugeOK = False;
If[exactXLagrangianOK,
  exactXAudits = Table[exactXTermAudit[term], {term, SA`LagTermsNonSUSY}];
  Scan[
    Print[
      "EXACT_X_TERM ", ToString[#["term"], InputForm],
      " X_sum=", ToString[#["x_sum"], InputForm],
      " Z17_phase=", ToString[#["z17_phase"], InputForm],
      " SO10_invariants=", #["so10_invariants"],
      " sarah_local=", #["sarah_local"],
      " sarah_global=", #["sarah_global"]
    ] &,
    exactXAudits
  ];
  exactXGaugeOK = And[
    Length[exactXAudits] === exactXExpectedTerms,
    AllTrue[exactXAudits, TrueQ[#["valid"]] &],
    AllTrue[exactXAudits, #["x_sum"] === 0 &],
    AllTrue[exactXAudits, #["z17_phase"] === 1 &],
    AllTrue[exactXAudits, IntegerQ[#["so10_invariants"]] && #["so10_invariants"] >= 1 &],
    AllTrue[exactXAudits, #["sarah_local"] &],
    AllTrue[exactXAudits, #["sarah_global"] &]
  ]
];
exactXEmitCheck["gauge_invariance_check_succeeded", exactXGaugeOK];

exactXAnomalyOK = False;
If[exactXInitializationOK,
  exactXAnomalyResult = exactXCapture[CheckAnomalies];
  exactXAnomalyText = Last[exactXAnomalyResult];
  (* SARAH appends the type tag F to every fermion row of Fields. *)
  exactXFermionRows = Select[Fields, Last[#] === F &];
  Print[
    "EXACT_X_ANOMALY_FERMIONS ",
    ToString[{#[[3]], #[[2]], #[[3 + exactXSO10Index]], #[[3 + exactXXIndex]]} & /@
      exactXFermionRows, InputForm]
  ];
  exactXMultiplicity[row_] := row[[2]] Abs[row[[3 + exactXSO10Index]]];
  exactXAnomalySums = <|
    "X^3" -> Total[(#[[3 + exactXXIndex]]^3 exactXMultiplicity[#]) & /@ exactXFermionRows],
    "X_gravity^2" -> Total[(#[[3 + exactXXIndex]] exactXMultiplicity[#]) & /@ exactXFermionRows],
    "SO10^2_X" -> Total[
      (#[[3 + exactXXIndex]] #[[2]] SA`Dynkin2[#[[3 + exactXSO10Index]], 10]) & /@
        exactXFermionRows
    ]
  |>;
  KeyValueMap[Print["EXACT_X_ANOMALY ", #1, " = ", ToString[#2, InputForm]] &, exactXAnomalySums];
  exactXAnomalyOK = And[
    First[exactXAnomalyResult],
    StringContainsQ[exactXAnomalyText, "Checking for anomalies"],
    StringFreeQ[exactXAnomalyText, "WARNING!"],
    Length[exactXFermionRows] === Length[FermionFields],
    AllTrue[Values[exactXAnomalySums], # === 0 &]
  ]
];
exactXEmitCheck["anomaly_check_succeeded", exactXAnomalyOK];

exactXAllPassed = And @@ Lookup[exactXResults, exactXRequiredChecks, False];
Quiet[Check[DeleteDirectory[exactXWorkRoot, DeleteContents -> True], Null]];
exactXStage["done"];
Exit[If[exactXAllPassed, 0, 1]];
