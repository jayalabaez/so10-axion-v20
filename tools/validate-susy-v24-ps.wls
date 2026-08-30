#!/usr/bin/env wolframscript

(* Genuine SARAH 4.15.3 Start[] audit for the V24 SUSY PS source. *)
ClearAll[v24ArgumentValue, v24Emit, v24Capture, v24CheckLedger];
Print["V24_PS_SARAH_ENGINE Wolfram " <> ToString[$Version]];
v24ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
v24CheckLedger = Association[];
v24Emit[checkName_String, condition_] := Module[{ok = TrueQ[condition]},
  AssociateTo[v24CheckLedger, checkName -> ok];
  Print["V24_PS_SARAH_CHECK " <> checkName <> " " <> If[ok, "PASS", "FAIL"]];
  ok
];
SetAttributes[v24Capture, HoldAll];
v24Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v24-ps-sarah-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}}, CheckAbort[heldExpr; True, False]];
  Close[stream]; content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]]; {TrueQ[ok], content}
];

repoRoot = ExpandFileName[v24ArgumentValue["--repo-root"]];
sarahRoot = ExpandFileName[v24ArgumentValue["--sarah-root"]];
modelName = "PSZ4RZ11SUSYV24";
sourceDir = FileNameJoin[{repoRoot, "models", modelName}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];

parse = And @@ (Function[path,
  text = Quiet[Check[Import[path, "Text"], $Failed]];
  StringQ[text] && Quiet[Check[ToExpression[text, InputForm, HoldComplete]; True, False]]
] /@ {
  FileNameJoin[{sourceDir, modelName <> ".m"}],
  FileNameJoin[{sourceDir, "parameters.m"}],
  FileNameJoin[{sourceDir, "particles.m"}]
});
v24Emit["model_parse_succeeded", parse];
If[! parse || ! FileExistsQ[sarahEntry], Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v24-ps-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
Scan[CopyFile[#, FileNameJoin[{modelDir, FileNameTake[#]}]] &, FileNames["*.m", sourceDir]];

Get[sarahEntry];
Print["V24_PS_SARAH_TOOL SARAH " <> ToString[SA`Version]];
$RecursionLimit = 3000;
load = v24Capture[
  SARAH[InputDirectories] = {work};
  SARAH[OutputDirectory] = outDir;
  Start[modelName]
];
initialized = And[
  First[load], TrueQ[ModelLoaded], TrueQ[AbortStart === False],
  TrueQ[SupersymmetricModel], Length[Gauge] === 3, Length[Fields] === 13
];
v24Emit["model_initialization_succeeded", initialized];
v24SPTerms = If[initialized && ListQ[SuperPotential], Length[SuperPotential], -1];
Print["V24_PS_SARAH_SPTERMS " <> ToString[v24SPTerms]];
v24CanonicalFields[term_List] := Sort[ToString[#, InputForm] & /@ term];
v24ActualStructures = If[initialized && ListQ[SuperPotential],
  Sort[v24CanonicalFields /@ SuperPotential[[All,2]]], {}];
v24ExpectedStructures = Sort[v24CanonicalFields /@ {
  {X}, {X,Sbc,Sc}, {X,X,X}, {X,H,H}, {X,Sig6,Sig6},
  {Sc,Sc,Sig6}, {Sbc,Sbc,Sig6},
  {Q,H,Qc}, {Q,H,PsiC}, {Psi,H,Qc}, {Psi,H,PsiC},
  {P,PsiBar,Q}, {P,PsiBar,Psi}, {P,PsiCBar,Qc}, {P,PsiCBar,PsiC},
  {Sbc,Qc,Nv}, {Sbc,PsiC,Nv}, {Nv,Nv}
}];
v24Emit["processed_W_exactly_18_terms", initialized && v24SPTerms === 18];
v24Emit["processed_W_full_structural_multiset_exact", initialized && v24ActualStructures === v24ExpectedStructures];
v24Emit["processed_W_contains_sextet_interactions", initialized && And @@ (
  MemberQ[v24ActualStructures, v24CanonicalFields[#]] & /@ {
    {X,Sig6,Sig6}, {Sc,Sc,Sig6}, {Sbc,Sbc,Sig6}
  })];
v24Emit["processed_W_contains_Yukawa_PQ_seesaw_interactions", initialized && And @@ (
  MemberQ[v24ActualStructures, v24CanonicalFields[#]] & /@ {
    {Q,H,Qc}, {P,PsiBar,Psi}, {Sbc,Qc,Nv}
  })];
v24Emit["processed_component_superpotential_nonzero", initialized &&
  ValueQ[Superpotential] && Superpotential =!= 0 &&
  ValueQ[WCouplings] && Length[WCouplings] === 18 &&
  And @@ (MemberQ[WCouplings, #] & /@ {lambdaSigma,lambdaS,lambdaSb,YQQ,lambdaPX,yNQ})];
v24Emit["z11_global_loaded", initialized && Length[Global] === 1 && Global[[1,1]] === Z[11]];
v24Emit["Start_reported_model_ready", initialized && StringContainsQ[Last[load], "is ready!"]];
v24Emit["Start_log_free_of_model_source_errors_and_Dot_dotsh", initialized &&
  And @@ (StringFreeQ[Last[load], #] & /@ {
    "ModelFile::", "Extract::", "Part::", "Dot::dotsh", "not invariant", "does not conserve"
  })];

continuous = If[initialized, v24Capture[CheckAnomalies], {False, "not initialized"}];
continuousOK = First[continuous] && StringFreeQ[Last[continuous], "WARNING!"];
v24Emit["continuous_gauge_anomaly_check_succeeded", continuousOK];

(* Independent Susyno singlet counts for the nontrivial normalized cubics. *)
inv = Susyno`LieGroups`Invariants;
su4 = Susyno`LieGroups`SU4;
su2 = Susyno`LieGroups`SU2;
countY = Length[inv[su4, {{1,0,0},{0,0,1}}]] *
  Length[inv[su2, {{1},{1}}]] * Length[inv[su2, {{1},{1}}]];
countS = Length[inv[su4, {{0,0,1},{0,0,1},{0,1,0}}]] *
  Length[inv[su2, {{1},{1}}]];
countSb = Length[inv[su4, {{1,0,0},{1,0,0},{0,1,0}}]] *
  Length[inv[su2, {{1},{1}}]];
v24Emit["unique_renormalizable_tensor_channels", countY === 1 && countS === 1 && countSb === 1];

all = And @@ Values[v24CheckLedger];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[all, 0, 1]];
