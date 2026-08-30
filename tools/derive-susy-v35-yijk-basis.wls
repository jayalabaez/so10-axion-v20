#!/usr/bin/env wolframscript

(* Live SARAH extraction of the literal 111-component superpotential tensor. *)
ClearAll[v35ArgumentValue, v35Capture, v35AddBasis];
v35ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
SetAttributes[v35Capture, HoldAll];
v35Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v35-yijk-" <> CreateUUID[] <> ".log"}];
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
If[!FileExistsQ[sarahEntry], Print["V35_YIJK_ERROR missing SARAH.m"]; Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v35-yijk-" <> CreateUUID[]}]];
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
  Print["V35_YIJK_ERROR model initialization failed"];
  Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
  Exit[1]
];
rge = v35Capture[CalcRGEs[TwoLoop -> True]];
calculated = First[rge] && ListQ[BetaYijk] && Length[BetaYijk] === 16;
If[!calculated,
  Print["V35_YIJK_ERROR CalcRGEs failed"];
  Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
  Exit[1]
];

rawYijkDownValues = ToString[DownValues[Yijk], InputForm];
rawInvMatSubValues = ToString[SubValues[InvMat], InputForm];
rawEpsTensorDownValues = ToString[DownValues[epsTensor], InputForm];
rawListWtriOne = ToString[listWtriOne, InputForm];
rawListWtri = ToString[listWtri, InputForm];

componentRows = {};
componentExpressions = {};
componentsByField = Table[{}, {Length[Fields]}];
componentId = 0;
For[fieldIndex = 1, fieldIndex <= Length[Fields], fieldIndex++,
  generationDimension = Fields[[fieldIndex, 2]];
  colorDimension = Abs[Fields[[fieldIndex, 4]]];
  leftDimension = Fields[[fieldIndex, 5]];
  rightDimension = Fields[[fieldIndex, 6]];
  Do[
    componentId++;
    componentExpression = LP[[fieldIndex]] /. {
      generation -> generationIndex,
      color4 -> colorIndex
    };
    AppendTo[componentExpressions, componentExpression];
    componentsByField[[fieldIndex]] = Append[componentsByField[[fieldIndex]], componentId];
    AppendTo[componentRows, <|
      "id" -> componentId,
      "field_index" -> fieldIndex,
      "field" -> ToString[Fields[[fieldIndex, 3]], InputForm],
      "generation" -> generationIndex,
      "color_component" -> colorIndex,
      "SU2L_component" -> leftIndex,
      "SU2R_component" -> rightIndex,
      "SARAH_component" -> ToString[componentExpression, InputForm]
    |>],
    {generationIndex, 1, generationDimension},
    {colorIndex, 1, colorDimension},
    {leftIndex, 1, leftDimension},
    {rightIndex, 1, rightDimension}
  ];
];

basisRows = {};
couplingRules = {};
basisId = 0;
v35AddBasis[name_String, indices_List, expression_] := Module[{},
  basisId++;
  AppendTo[basisRows, <|
    "id" -> basisId,
    "parameter" -> name,
    "indices" -> indices,
    "SARAH_parameter" -> ToString[expression, InputForm]
  |>];
  couplingRules = Append[couplingRules, expression -> basisVar[basisId]];
];

Scan[(v35AddBasis[ToString[#, InputForm], {}, #]) &, {
  lambdaPX, lambdaPcX, YXX, lambdaSb, lambdaS, lambdaH,
  kappaPS, lambdaSigma, kappaX
}];
Do[v35AddBasis["lambdaPQ", {i}, lambdaPQ[i]], {i, 1, 3}];
Do[v35AddBasis["lambdaPcQ", {i}, lambdaPcQ[i]], {i, 1, 3}];
Do[v35AddBasis["YXQ", {i}, YXQ[i]], {i, 1, 3}];
Do[v35AddBasis["YQX", {i}, YQX[i]], {i, 1, 3}];
Do[v35AddBasis["yNX", {i}, yNX[i]], {i, 1, 3}];
Do[v35AddBasis["YQQ", {i, j}, YQQ[i, j]], {i, 1, 3}, {j, 1, 3}];
Do[v35AddBasis["yNQ", {i, j}, yNQ[i, j]], {i, 1, 3}, {j, 1, 3}];

allowedFieldTriples = {
  {12, 8, 9}, {12, 8, 2}, {12, 11, 10}, {12, 11, 3},
  {9, 1, 10}, {9, 1, 3}, {2, 1, 10}, {2, 1, 3},
  {6, 10, 13}, {6, 3, 13}, {7, 6, 6}, {7, 5, 5},
  {4, 6, 5}, {4, 7, 7}, {4, 1, 1}, {4, 4, 4}
};

sparseAssociation = Association[];
errors = {};
examinedComponentTriples = 0;
For[tripleIndex = 1, tripleIndex <= Length[allowedFieldTriples], tripleIndex++,
  fieldTriple = allowedFieldTriples[[tripleIndex]];
  componentTriples = Tuples[componentsByField[[#]] & /@ fieldTriple];
  For[componentTripleIndex = 1,
      componentTripleIndex <= Length[componentTriples],
      componentTripleIndex++,
    ids = componentTriples[[componentTripleIndex]];
    examinedComponentTriples++;
    rows = componentRows[[ids]];
    expression = Yijk @@ componentExpressions[[ids]] /. {
      lef1 -> rows[[1]]["SU2L_component"],
      lef2 -> rows[[2]]["SU2L_component"],
      lef3 -> rows[[3]]["SU2L_component"],
      rig1 -> rows[[1]]["SU2R_component"],
      rig2 -> rows[[2]]["SU2R_component"],
      rig3 -> rows[[3]]["SU2R_component"]
    };
    expression = FullSimplify[expression /. couplingRules /. Yijk[__] -> 0];
    If[expression =!= 0,
      foundBasisIds = DeleteDuplicates[
        Cases[expression, basisVar[n_Integer] :> n, {0, Infinity}]
      ];
      If[Length[foundBasisIds] =!= 1,
        errors = Append[errors,
          "nonunique basis in " <> ToString[ids, InputForm] <> ": " <>
          ToString[expression, InputForm]
        ],
        foundBasisId = First[foundBasisIds];
        coefficient = FullSimplify[expression / basisVar[foundBasisId]];
        If[!FreeQ[coefficient, basisVar | Yijk | epsTensor | Delta | InvMat],
          errors = Append[errors,
            "unresolved coefficient in " <> ToString[ids, InputForm] <> ": " <>
            ToString[coefficient, InputForm]
          ],
          Scan[
            Function[permutation,
              key = StringRiffle[ToString /@ Append[permutation, foundBasisId], ":"];
              If[KeyExistsQ[sparseAssociation, key],
                If[FullSimplify[sparseAssociation[key]["coefficient"] - coefficient] =!= 0,
                  errors = Append[errors, "inconsistent duplicate " <> key]
                ],
                AssociateTo[sparseAssociation, key -> <|
                  "i" -> permutation[[1]],
                  "j" -> permutation[[2]],
                  "k" -> permutation[[3]],
                  "basis_id" -> foundBasisId,
                  "coefficient" -> coefficient
                |>]
              ]
            ],
            DeleteDuplicates[Permutations[ids]]
          ]
        ]
      ]
    ];
  ];
];

sparseInternalRows = Values[sparseAssociation];
sparseExportRows = Map[
  Function[row, <|
    "i" -> row["i"], "j" -> row["j"], "k" -> row["k"],
    "basis_id" -> row["basis_id"],
    "coefficient_exact" -> ToString[row["coefficient"], InputForm],
    "coefficient_numeric" -> N[row["coefficient"], 17]
  |>],
  sparseInternalRows
];

gramRows = Table[
  gramValue = FullSimplify[Total[
    (# ["coefficient"] Conjugate[# ["coefficient"]]) & /@
      Select[sparseInternalRows, # ["basis_id"] === currentBasisId &]
  ]];
  <|
    "basis_id" -> currentBasisId,
    "parameter" -> basisRows[[currentBasisId]]["parameter"],
    "indices" -> basisRows[[currentBasisId]]["indices"],
    "diagonal_exact" -> ToString[gramValue, InputForm],
    "diagonal_numeric" -> N[gramValue, 17]
  |>,
  {currentBasisId, 1, basisId}
];

expectedTensorGram = <|
  "lambdaPX" -> 48, "lambdaPQ" -> 48,
  "lambdaPcX" -> 48, "lambdaPcQ" -> 48,
  "YXX" -> 96, "YXQ" -> 96, "YQX" -> 96, "YQQ" -> 96,
  "yNX" -> 48, "yNQ" -> 48,
  "lambdaSb" -> 36, "lambdaS" -> 36,
  "lambdaH" -> 12, "kappaPS" -> 48,
  "lambdaSigma" -> 18, "kappaX" -> 4
|>;
gramMatches = And @@ Map[
  Function[row,
    ToExpression[row["diagonal_exact"], InputForm] === expectedTensorGram[row["parameter"]]
  ],
  gramRows
];

payload = <|
  "schema" -> "susy-v35-live-sarah-yijk-component-basis-v1",
  "engine" -> ToString[$Version],
  "tool" -> ("SARAH " <> ToString[SA`Version]),
  "model" -> modelName,
  "model_initialized" -> initialized,
  "two_loop_RGE_calculation_succeeded" -> calculated,
  "visible_complex_chiral_component_count" -> componentId,
  "dimensionless_coupling_component_count" -> basisId,
  "component_rows" -> componentRows,
  "coupling_basis_rows" -> basisRows,
  "allowed_field_triples" -> allowedFieldTriples,
  "examined_component_triples" -> examinedComponentTriples,
  "sparse_tensor_entry_count" -> Length[sparseExportRows],
  "sparse_tensor_rows" -> sparseExportRows,
  "Gram_diagonal_rows" -> gramRows,
  "expected_Gram_by_parameter" -> expectedTensorGram,
  "all_Gram_diagonals_match_reference" -> gramMatches,
  "Yijk_downvalues_sha256" -> IntegerString[
    Hash[rawYijkDownValues, "SHA256"], 16, 64
  ],
  "InvMat_subvalues_sha256" -> IntegerString[
    Hash[rawInvMatSubValues, "SHA256"], 16, 64
  ],
  "epsTensor_downvalues_sha256" -> IntegerString[
    Hash[rawEpsTensorDownValues, "SHA256"], 16, 64
  ],
  "listWtriOne_count" -> Length[listWtriOne],
  "listWtri_count" -> Length[listWtri],
  "listWtriOne_sha256" -> IntegerString[Hash[rawListWtriOne, "SHA256"], 16, 64],
  "listWtri_sha256" -> IntegerString[Hash[rawListWtri, "SHA256"], 16, 64],
  "SA_NonZeroEntries_input_form" -> ToString[SA`NonZeroEntries, InputForm],
  "epsilon2_matrix_input_form" -> ToString[
    Table[epsTensor[i, j], {i, 1, 2}, {j, 1, 2}], InputForm
  ],
  "InvMat1_4x4x6_input_form" -> ToString[
    Table[InvMat[1][i, j, k], {i, 1, 4}, {j, 1, 4}, {k, 1, 6}], InputForm
  ],
  "InvMat2_4x4x6_input_form" -> ToString[
    Table[InvMat[2][i, j, k], {i, 1, 4}, {j, 1, 4}, {k, 1, 6}], InputForm
  ],
  "InvMat3_6x6_input_form" -> ToString[
    Table[InvMat[3][i, j], {i, 1, 6}, {j, 1, 6}], InputForm
  ],
  "extraction_errors" -> errors,
  "extraction_passed" -> (Length[errors] === 0 && componentId === 111 &&
    basisId === 42 && gramMatches)
|>;

Export[outputPath, payload, "RawJSON"];
Print["V35_YIJK_COMPONENTS " <> ToString[componentId]];
Print["V35_YIJK_BASIS " <> ToString[basisId]];
Print["V35_YIJK_SPARSE_ENTRIES " <> ToString[Length[sparseExportRows]]];
Print["V35_YIJK_ERRORS " <> ToString[Length[errors]]];
Print["V35_YIJK_STATUS " <> If[payload["extraction_passed"], "PASS", "FAIL"]];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[payload["extraction_passed"], 0, 1]];
