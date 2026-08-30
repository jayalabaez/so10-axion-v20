#!/usr/bin/env wolframscript

(* Genuine SARAH 4.15.3 Start[] audit for the V36 Z66 redesign. *)
ClearAll[v36ArgumentValue, v36Emit, v36Capture];
v36ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
checks = Association[];
v36Emit[name_String, condition_] := Module[{ok = TrueQ[condition]},
  AssociateTo[checks, name -> ok];
  Print["V36_Z66_SARAH_CHECK " <> name <> " " <> If[ok, "PASS", "FAIL"]];
  ok
];
SetAttributes[v36Capture, HoldAll];
v36Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v36-z66-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}},
    CheckAbort[heldExpr; True, False]
  ];
  Close[stream];
  content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]];
  {TrueQ[ok], content}
];

repoRoot = ExpandFileName[v36ArgumentValue["--repo-root"]];
sarahRoot = ExpandFileName[v36ArgumentValue["--sarah-root"]];
modelName = "PSZ4RZ66SUSYV36";
sourceDir = FileNameJoin[{repoRoot, "models", modelName}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];
parse = And @@ (Function[path,
  text = Quiet[Check[Import[path, "Text"], $Failed]];
  StringQ[text] && Quiet[Check[ToExpression[text, InputForm, HoldComplete]; True, False]]
] /@ FileNames["*.m", sourceDir]);
v36Emit["model_parse_succeeded", parse];
If[!parse || !FileExistsQ[sarahEntry], Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v36-z66-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
Scan[CopyFile[#, FileNameJoin[{modelDir, FileNameTake[#]}]] &, FileNames["*.m", sourceDir]];
Get[sarahEntry];
Print["V36_Z66_SARAH_ENGINE " <> ToString[$Version]];
Print["V36_Z66_SARAH_TOOL SARAH " <> ToString[SA`Version]];
$RecursionLimit = 4000;
load = v36Capture[
  SARAH[InputDirectories] = {work};
  SARAH[OutputDirectory] = outDir;
  Start[modelName]
];
initialized = First[load] && TrueQ[ModelLoaded] && TrueQ[AbortStart === False] &&
  TrueQ[SupersymmetricModel] && Length[Gauge] === 3 && Length[Fields] === 20;
v36Emit["model_initialization_succeeded", initialized];
count = If[initialized && ListQ[SuperPotential], Length[SuperPotential], -1];
Print["V36_Z66_SARAH_SPTERMS " <> ToString[count]];
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
  {Pb,A2,A32}, {P,A15,A17}, {P,A16,A16}, {Pb,A17,A17},
  {A16,A17}
}];
v36Emit["processed_W_exactly_34_terms", count === 34];
v36Emit["processed_W_full_structural_multiset_exact", actual === expected];
v36Emit["z66_global_loaded", initialized && Length[Global] === 1 && Global[[1,1]] === Z[66]];
rMap = Association[Rule @@@ V36Z4RCharges];
v36Emit["all_processed_W_terms_have_Z4R_charge_2", initialized && And @@
  (Mod[Total[Lookup[rMap, #]], 4] === 2 & /@ SuperPotential[[All,2]])];
oddFields = {A2,A32,A15,A17,A16};
v36Emit["all_processed_W_terms_preserve_residual_Z2", initialized && And @@
  (EvenQ[Count[#, Alternatives @@ oddFields]] & /@ SuperPotential[[All,2]])];
v36Emit["dangerous_P_A32_absent", initialized &&
  FreeQ[actual, canonical[{P,A32}]]];
v36Emit["processed_component_superpotential_nonzero", initialized &&
  ValueQ[Superpotential] && Superpotential =!= 0 && ValueQ[WCouplings] &&
  Length[WCouplings] === 34];
v36Emit["Start_log_free_of_source_errors", initialized && And @@
  (StringFreeQ[Last[load], #] & /@ {
    "ModelFile::", "Extract::", "Part::", "Dot::dotsh",
    "not invariant", "does not conserve"
  })];
continuous = If[initialized, v36Capture[CheckAnomalies], {False, "not initialized"}];
v36Emit["continuous_gauge_anomaly_check_succeeded", First[continuous] &&
  StringFreeQ[Last[continuous], "WARNING!"]];

all = And @@ Values[checks];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[all, 0, 1]];
