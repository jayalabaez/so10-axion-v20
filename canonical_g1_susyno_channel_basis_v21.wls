#!/usr/bin/env wolframscript
(* Independent constructive representation-channel basis for canonical G1.

   SARAH 4.15.3 contains Renato Fonseca's exact Susyno plethysm routines in
   LieGroups_SARAH.m, but the relevant block is enclosed in a dormant comment.
   This driver loads the trusted source and evaluates exactly that block, then
   decomposes every charge-neutral scalar monomial through degree six into
   symmetric-power irreps.  Each singlet channel and every multiplicity-copy
   label is emitted.  Component Clebsches are deliberately left to canonical
   G2; G1 needs a constructive invariant-space basis and exact normalization
   convention, not its 486-component expansion. *)

ClearAll[argumentValue];
argumentValue[flag_String] := Module[{position},
  position = FirstPosition[$ScriptCommandLine, flag];
  If[MissingQ[position] || First[position] >= Length[$ScriptCommandLine],
    Missing["NotProvided"], $ScriptCommandLine[[First[position] + 1]]]
];

repoArgument = argumentValue["--repo-root"];
repoRoot = ExpandFileName[If[MissingQ[repoArgument], Directory[], repoArgument]];
sarahArgument = argumentValue["--sarah-root"];
If[MissingQ[sarahArgument],
  Print["G1_SUSYNO_ERROR missing --sarah-root"];
  Exit[2]
];
sarahRoot = ExpandFileName[sarahArgument];
outputArgument = argumentValue["--output"];
outputPath = ExpandFileName[If[MissingQ[outputArgument],
  FileNameJoin[{repoRoot, "CANONICAL_G1_SUSYNO_CHANNEL_BASIS_V21.json"}],
  outputArgument
]];
checkMode = MemberQ[$ScriptCommandLine, "--check"];

lieSourcePath = FileNameJoin[{sarahRoot, "Susyno", "LieGroups_SARAH.m"}];
frontierPath = FileNameJoin[{repoRoot, "CANONICAL_G1_SCALAR_RING_DIM6_FRONTIER_V21.json"}];
If[!FileExistsQ[lieSourcePath] || !FileExistsQ[frontierPath],
  Print["G1_SUSYNO_ERROR required input missing"];
  Exit[2]
];

Get[lieSourcePath];
lieText = Import[lieSourcePath, "Text"];
startMarker = "(* XXXXXXXXXXXXXXXXXXXXXXXXXXXXX THE SYMMETRY TO TENSOR PRODUCTS";
endMarker = "(* XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX LISTING ALL REPS";
startPosition = First@First@StringPosition[lieText, startMarker];
endPosition = First@First@StringPosition[lieText, endMarker];
dormantBlock = StringTrim@StringTake[lieText, {startPosition, endPosition - 1}];
If[StringEndsQ[dormantBlock, "*)"], dormantBlock = StringDrop[dormantBlock, -2]];
ToExpression[dormantBlock];

frontier = Import[frontierPath, "RawJSON"];
rows = frontier["exact_character_census"]["rows"];
fieldOrder = {"P", "H", "Hb", "D", "Db"};
fieldReps = <|
  "P" -> {0, 0, 0, 1, 1},
  "H" -> {1, 0, 0, 0, 0},
  "Hb" -> {1, 0, 0, 0, 0},
  "D" -> {0, 0, 0, 2, 0},
  "Db" -> {0, 0, 0, 0, 2}
|>;
zeroRep = {0, 0, 0, 0, 0};

ClearAll[plethysmFor];
plethysmFor[field_String, n_Integer] := plethysmFor[field, n] = Module[{items},
  items = Plethysms[SO10, fieldReps[field], {n}];
  SortBy[items, {ToString[#[[1]], InputForm] &, Last}]
];

ClearAll[singletMultiplicity];
singletMultiplicity[irreps_List] := Module[{decomposition, hits},
  If[Length[irreps] == 0, Return[1]];
  If[Length[irreps] == 1, Return[If[First[irreps] === zeroRep, 1, 0]]];
  decomposition = ReduceRepProduct[SO10, irreps];
  hits = Cases[decomposition, {rep_, multiplicity_} /; rep === zeroRep :> multiplicity];
  Total[hits]
];

ClearAll[channelRows];
channelRows[row_Association] := Module[
  {counts, active, decompositions, choices, channels = {}, irreps,
   singletCopies, sourceCopyTuples, fields, choice, copyTuple, singletIndex},
  counts = row["counts"];
  active = Select[fieldOrder, counts[#] > 0 &];
  decompositions = plethysmFor[#, counts[#]] & /@ active;
  choices = If[Length[decompositions] == 0, {{}}, Tuples[decompositions]];
  Do[
    choice = choices[[choiceIndex]];
    irreps = If[Length[choice] == 0, {}, choice[[All, 1]]];
    singletCopies = singletMultiplicity[irreps];
    If[singletCopies > 0,
      sourceCopyTuples = If[Length[choice] == 0, {{}},
        Tuples[Range /@ choice[[All, 2]]]
      ];
      Do[
        copyTuple = sourceCopyTuples[[copyIndex]];
        Do[
          AppendTo[channels, <|
            "basis_index" -> (Length[channels] + 1),
            "plethysm_irreps" -> AssociationThread[active, irreps],
            "plethysm_copy_indices" -> AssociationThread[active, copyTuple],
            "final_singlet_copy_index" -> singletIndex
          |>],
          {singletIndex, 1, singletCopies}
        ],
        {copyIndex, 1, Length[sourceCopyTuples]}
      ]
    ],
    {choiceIndex, 1, Length[choices]}
  ];
  channels
];

resultRows = Table[
  channels = channelRows[row];
  <|
    "count_tuple" -> row["count_tuple"],
    "degree" -> row["degree"],
    "monomial" -> row["monomial"],
    "upper_bound_character_multiplicity" -> row["so10_singlet_multiplicity"],
    "constructive_channel_count" -> Length[channels],
    "channels" -> channels
  |>,
  {row, rows}
];

allMatch = And @@ (#["upper_bound_character_multiplicity"] ===
    #["constructive_channel_count"] & /@ resultRows);
totalChannels = Total[#["constructive_channel_count"] & /@ resultRows];
degreeTotals = Association@Table[
  ToString[degree] -> Total[Select[resultRows, #["degree"] === degree &][[All,
    "constructive_channel_count"]]],
  {degree, 1, 6}
];

report = <|
  "schema" -> "canonical_g1_susyno_channel_basis_v1",
  "model_contract_id" -> "gauged_u1x_phi17_v20",
  "status" -> If[allMatch,
    "EXACT_SUSYNO_CONSTRUCTIVE_CHANNEL_BASIS_DIM6_COMPLETE",
    "SUSYNO_CHANNEL_BASIS_MISMATCH"],
  "scope" -> "derivative-free scalar polynomial operator ring through engineering dimension six",
  "trusted_source" -> <|
    "path" -> "Susyno/LieGroups_SARAH.m",
    "version" -> "SARAH-4.15.3",
    "dormant_plethysm_block_sha256" -> Hash[dormantBlock, "SHA256", "HexString"]
  |>,
  "construction" -> <|
    "method" -> "exact D5 symmetric-power plethysms followed by exact irrep-product singlet reduction",
    "field_order" -> fieldOrder,
    "field_D5_Dynkin_labels" -> fieldReps,
    "basis_direction_count" -> totalChannels,
    "basis_direction_count_by_degree" -> degreeTotals,
    "all_sector_lower_bounds_equal_character_upper_bounds" -> allMatch
  |>,
  "normalization_conventions" -> <|
    "representation_metric" -> "positive unit invariant Hermitian form on each compact Spin(10) irrep",
    "isotypic_embeddings" -> "orthonormal; ordered by D5 Dynkin label then exact plethysm copy index",
    "singlet_Hom_basis" -> "orthonormal; deterministic Susyno reduction order; first nonzero weight-lex coefficient positive real",
    "Hermitian_conjugation" -> "D5 chirality 4<->5, H<->Hb, D<->Db, S<->Sb, X<->Xb; conjugate sectors paired by equal ordered basis index",
    "component_projection_boundary" -> "component Clebsch expansion is canonical G2, not silently claimed by this G1 channel basis"
  |>,
  "rows" -> resultRows,
  "n_checks" -> 4,
  "n_failed" -> If[allMatch && Length[resultRows] == 168 && totalChannels == 891 &&
    degreeTotals["5"] == 119 && degreeTotals["6"] == 721, 0, 1]
|>;
report["checks"] = <|
  "all_168_sectors_constructed" -> (Length[resultRows] == 168),
  "all_sector_lower_bounds_equal_character_upper_bounds" -> allMatch,
  "all_891_complex_directions_have_channel_labels" -> (totalChannels == 891),
  "degree_five_six_channel_counts_are_119_and_721" ->
    (degreeTotals["5"] == 119 && degreeTotals["6"] == 721)
|>;
report["rows_sha256"] = Hash[ExportString[resultRows, "RawJSON", "Compact" -> True],
  "SHA256", "HexString"];
report["core_sha256"] = Hash[ExportString[KeyDrop[report, {"core_sha256"}],
  "RawJSON", "Compact" -> True], "SHA256", "HexString"];

If[report["n_failed"] =!= 0,
  Print["G1_SUSYNO_ERROR constructive channel mismatch"];
  Exit[1]
];
If[checkMode,
  If[!FileExistsQ[outputPath] || Import[outputPath, "RawJSON"] =!= report,
    Print["G1_SUSYNO_ERROR frozen channel report drifted"];
    Exit[1]
  ],
  jsonText = StringReplace[
    ExportString[report, "RawJSON", "Compact" -> False],
    {"\r\n" -> "\n", "\r" -> "\n"}
  ];
  If[!StringEndsQ[jsonText, "\n"], jsonText = jsonText <> "\n"];
  jsonStream = OpenWrite[outputPath, BinaryFormat -> True];
  BinaryWrite[jsonStream, ToCharacterCode[jsonText, "UTF-8"], "Byte"];
  Close[jsonStream]
];
Print["G1_SUSYNO_CHANNEL_BASIS_PASS ", report["core_sha256"]];
Exit[0];
