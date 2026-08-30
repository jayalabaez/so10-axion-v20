#!/usr/bin/env wolframscript

(* Genuine SARAH 4.15.3 Start[] audit for the V37 Z5610 redesign. *)
ClearAll[v37ArgumentValue, v37Emit, v37Capture];
v37ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
checks = Association[];
v37Emit[name_String, condition_] := Module[{ok = TrueQ[condition]},
  AssociateTo[checks, name -> ok];
  Print["V37_Z5610_SARAH_CHECK " <> name <> " " <> If[ok, "PASS", "FAIL"]];
  ok
];
SetAttributes[v37Capture, HoldAll];
v37Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v37-z5610-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}},
    CheckAbort[heldExpr; True, False]
  ];
  Close[stream];
  content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]];
  {TrueQ[ok], content}
];

repoRoot = ExpandFileName[v37ArgumentValue["--repo-root"]];
sarahRoot = ExpandFileName[v37ArgumentValue["--sarah-root"]];
modelName = "PSZ4RZ5610SUSYV37";
sourceDir = FileNameJoin[{repoRoot, "models", modelName}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];
parse = And @@ (Function[path,
  text = Quiet[Check[Import[path, "Text"], $Failed]];
  StringQ[text] && Quiet[Check[ToExpression[text, InputForm, HoldComplete]; True, False]]
] /@ FileNames["*.m", sourceDir]);
v37Emit["model_parse_succeeded", parse];
If[!parse || !FileExistsQ[sarahEntry], Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v37-z5610-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
Scan[CopyFile[#, FileNameJoin[{modelDir, FileNameTake[#]}]] &, FileNames["*.m", sourceDir]];
Get[sarahEntry];
Print["V37_Z5610_SARAH_ENGINE " <> ToString[$Version]];
Print["V37_Z5610_SARAH_TOOL SARAH " <> ToString[SA`Version]];
$RecursionLimit = 4000;
load = v37Capture[
  SARAH[InputDirectories] = {work};
  SARAH[OutputDirectory] = outDir;
  Start[modelName]
];
initialized = First[load] && TrueQ[ModelLoaded] && TrueQ[AbortStart === False] &&
  TrueQ[SupersymmetricModel] && Length[Gauge] === 3 && Length[Fields] === 20;
v37Emit["model_initialization_succeeded", initialized];

count = If[initialized && ListQ[SuperPotential], Length[SuperPotential], -1];
Print["V37_Z5610_SARAH_SPTERMS " <> ToString[count]];
canonical[term_List] := Sort[ToString[#, InputForm] & /@ term];
actual = If[initialized && ListQ[SuperPotential], Sort[canonical /@ SuperPotential[[All,2]]], {}];
expected = Sort[canonical /@ {
  {X}, {X}, {Zp}, {Zp},
  {X,Sbc,Sc}, {X,P,Pb}, {Zp,Sbc,Sc}, {Zp,P,Pb},
  {X,X,X}, {X,X,Zp}, {X,Zp,Zp}, {Zp,Zp,Zp},
  {X,H,H}, {X,Sig6,Sig6}, {Zp,H,H}, {Zp,Sig6,Sig6},
  {Sc,Sc,Sig6}, {Sbc,Sbc,Sig6},
  {Q,H,Qc}, {Q,H,PsiC}, {Psi,H,Qc}, {Psi,H,PsiC},
  {P,PsiBar,Q}, {P,PsiBar,Psi},
  {P,PsiCBar,Qc}, {P,PsiCBar,PsiC},
  {Sbc,Qc,Nv}, {Sbc,PsiC,Nv}, {Nv,Nv},
  {Pb,A2,A32}, {P,A15,A17}, {P,A16,A16}
}];
v37Emit["processed_W_exactly_32_terms", count === 32];
v37Emit["processed_W_full_structural_multiset_exact", actual === expected];
v37Emit["z5610_global_loaded", initialized && Length[Global] === 1 && Global[[1,1]] === Z[5610]];

rMap = Association[Rule @@@ V37Z4RCharges];
v37Emit["all_processed_W_terms_have_Z4R_charge_2", initialized && And @@
  (Mod[Total[Lookup[rMap, #]], 4] === 2 & /@ SuperPotential[[All,2]])];
h85Map = Association[Rule @@@ V37Z85Charges];
v37Emit["all_processed_W_terms_have_Z85_charge_0", initialized && And @@
  (Mod[Total[Lookup[h85Map, #]], 85] === 0 & /@ SuperPotential[[All,2]])];

removed = canonical /@ {{Pb,A17,A17}, {A16,A17}};
v37Emit["removed_V36_anomalon_terms_absent", initialized &&
  And @@ (FreeQ[actual, #] & /@ removed)];
v37Emit["dangerous_P_A32_absent", initialized &&
  FreeQ[actual, canonical[{P,A32}]]];
v37Emit["retained_three_term_anomalon_mass_sector_present", initialized && And @@
  (MemberQ[actual, canonical[#]] & /@ {{Pb,A2,A32}, {P,A15,A17}, {P,A16,A16}})];

v37Emit["processed_component_superpotential_nonzero", initialized &&
  ValueQ[Superpotential] && Superpotential =!= 0 && ValueQ[WCouplings] &&
  Length[WCouplings] === 32];
v37Emit["Start_log_free_of_source_errors", initialized && And @@
  (StringFreeQ[Last[load], #] & /@ {
    "ModelFile::", "Extract::", "Part::", "Dot::dotsh",
    "not invariant", "does not conserve"
  })];
continuous = If[initialized, v37Capture[CheckAnomalies], {False, "not initialized"}];
v37Emit["continuous_gauge_anomaly_check_succeeded", First[continuous] &&
  StringFreeQ[Last[continuous], "WARNING!"]];

all = And @@ Values[checks];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[all, 0, 1]];
