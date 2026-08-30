#!/usr/bin/env wolframscript

(* Genuine SARAH 4.15.3 Start[] audit for the V33 Z33 EFT source. *)
ClearAll[v33ArgumentValue, v33Emit, v33Capture];
v33ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
checks = Association[];
v33Emit[name_String, condition_] := Module[{ok = TrueQ[condition]},
  AssociateTo[checks, name -> ok];
  Print["V33_Z33_SARAH_CHECK " <> name <> " " <> If[ok, "PASS", "FAIL"]];
  ok
];
SetAttributes[v33Capture, HoldAll];
v33Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v33-z33-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}}, CheckAbort[heldExpr; True, False]];
  Close[stream]; content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]]; {TrueQ[ok], content}
];

repoRoot = ExpandFileName[v33ArgumentValue["--repo-root"]];
sarahRoot = ExpandFileName[v33ArgumentValue["--sarah-root"]];
modelName = "PSZ4RZ33SUSYV33";
sourceDir = FileNameJoin[{repoRoot, "models", modelName}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];
parse = And @@ (Function[path,
  text = Quiet[Check[Import[path, "Text"], $Failed]];
  StringQ[text] && Quiet[Check[ToExpression[text, InputForm, HoldComplete]; True, False]]
] /@ FileNames["*.m", sourceDir]);
v33Emit["model_parse_succeeded", parse];
If[!parse || !FileExistsQ[sarahEntry], Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v33-z33-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
Scan[CopyFile[#, FileNameJoin[{modelDir, FileNameTake[#]}]] &, FileNames["*.m", sourceDir]];
Get[sarahEntry];
Print["V33_Z33_SARAH_ENGINE " <> ToString[$Version]];
Print["V33_Z33_SARAH_TOOL SARAH " <> ToString[SA`Version]];
$RecursionLimit = 3000;
load = v33Capture[
  SARAH[InputDirectories] = {work};
  SARAH[OutputDirectory] = outDir;
  Start[modelName]
];
initialized = First[load] && TrueQ[ModelLoaded] && TrueQ[AbortStart === False] &&
  TrueQ[SupersymmetricModel] && Length[Gauge] === 3 && Length[Fields] === 13;
v33Emit["model_initialization_succeeded", initialized];
count = If[initialized && ListQ[SuperPotential], Length[SuperPotential], -1];
Print["V33_Z33_SARAH_SPTERMS " <> ToString[count]];
canonical[term_List] := Sort[ToString[#, InputForm] & /@ term];
actual = If[initialized && ListQ[SuperPotential], Sort[canonical /@ SuperPotential[[All,2]]], {}];
expected = Sort[canonical /@ {
  {X}, {X,Sbc,Sc}, {X,X,X}, {X,H,H}, {X,Sig6,Sig6},
  {Sc,Sc,Sig6}, {Sbc,Sbc,Sig6}, {Q,H,Qc}, {Q,H,PsiC},
  {Psi,H,Qc}, {Psi,H,PsiC}, {P,PsiBar,Q}, {P,PsiBar,Psi},
  {P,PsiCBar,Qc}, {P,PsiCBar,PsiC}, {Sbc,Qc,Nv}, {Sbc,PsiC,Nv}, {Nv,Nv}
}];
v33Emit["processed_W_exactly_18_terms", count === 18];
v33Emit["processed_W_full_structural_multiset_exact", actual === expected];
v33Emit["z33_global_loaded", initialized && Length[Global] === 1 && Global[[1,1]] === Z[33]];
v33Emit["processed_component_superpotential_nonzero", initialized &&
  ValueQ[Superpotential] && Superpotential =!= 0 && ValueQ[WCouplings] &&
  Length[WCouplings] === 18];
v33Emit["Start_log_free_of_source_errors", initialized && And @@
  (StringFreeQ[Last[load], #] & /@ {"ModelFile::", "Extract::", "Part::", "Dot::dotsh", "not invariant", "does not conserve"})];
continuous = If[initialized, v33Capture[CheckAnomalies], {False, "not initialized"}];
v33Emit["continuous_gauge_anomaly_check_succeeded", First[continuous] && StringFreeQ[Last[continuous], "WARNING!"]];

all = And @@ Values[checks];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[all, 0, 1]];
