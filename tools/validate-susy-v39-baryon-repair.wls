#!/usr/bin/env wolframscript

(* Genuine SARAH 4.15.3 source and continuous-gauge audit for the V39 repair. *)
ClearAll[v39ArgumentValue, v39Emit, v39Capture];
v39ArgumentValue[flag_String] := Module[{p = FirstPosition[$ScriptCommandLine, flag]},
  If[MissingQ[p] || First[p] >= Length[$ScriptCommandLine], Missing["NotProvided"],
    $ScriptCommandLine[[First[p] + 1]]]
];
checks = Association[];
v39Emit[name_String, condition_] := Module[{ok = TrueQ[condition]},
  AssociateTo[checks, name -> ok];
  Print["V39_BARYON_REPAIR_SARAH_CHECK " <> name <> " " <> If[ok, "PASS", "FAIL"]];
  ok
];
SetAttributes[v39Capture, HoldAll];
v39Capture[heldExpr_] := Module[{path, stream, ok, content},
  path = FileNameJoin[{$TemporaryDirectory, "v39-baryon-repair-" <> CreateUUID[] <> ".log"}];
  stream = OpenWrite[path, CharacterEncoding -> "UTF-8"];
  ok = Block[{$Output = {stream}, $Messages = {stream}},
    CheckAbort[heldExpr; True, False]
  ];
  Close[stream];
  content = Quiet[Check[Import[path, "Text"], ""]];
  If[StringLength[content] > 0, Print[content]];
  {TrueQ[ok], content}
];

repoRoot = ExpandFileName[v39ArgumentValue["--repo-root"]];
sarahRoot = ExpandFileName[v39ArgumentValue["--sarah-root"]];
modelName = "PSZ4RZ5610Z3SUSYV39";
sourceDir = FileNameJoin[{repoRoot, "models", modelName}];
sarahEntry = FileNameJoin[{sarahRoot, "SARAH.m"}];
parse = And @@ (Function[path,
  text = Quiet[Check[Import[path, "Text"], $Failed]];
  StringQ[text] && Quiet[Check[ToExpression[text, InputForm, HoldComplete]; True, False]]
] /@ FileNames["*.m", sourceDir]);
v39Emit["model_parse_succeeded", parse];
If[!parse || !FileExistsQ[sarahEntry], Exit[1]];

work = CreateDirectory[FileNameJoin[{$TemporaryDirectory, "v39-baryon-repair-" <> CreateUUID[]}]];
modelDir = CreateDirectory[FileNameJoin[{work, modelName}]];
outDir = CreateDirectory[FileNameJoin[{work, "output"}]];
Scan[CopyFile[#, FileNameJoin[{modelDir, FileNameTake[#]}]] &, FileNames["*.m", sourceDir]];
Get[sarahEntry];
Print["V39_BARYON_REPAIR_SARAH_ENGINE " <> ToString[$Version]];
Print["V39_BARYON_REPAIR_SARAH_TOOL SARAH " <> ToString[SA`Version]];
$RecursionLimit = 4000;
load = v39Capture[
  SARAH[InputDirectories] = {work};
  SARAH[OutputDirectory] = outDir;
  Start[modelName]
];
initialized = First[load] && TrueQ[ModelLoaded] && TrueQ[AbortStart === False] &&
  TrueQ[SupersymmetricModel] && Length[Gauge] === 3 && Length[Fields] === 21;
v39Emit["model_initialization_succeeded", initialized];

count = If[initialized && ListQ[SuperPotential], Length[SuperPotential], -1];
Print["V39_BARYON_REPAIR_SARAH_SPTERMS " <> ToString[count]];
canonical[term_List] := Sort[ToString[#, InputForm] & /@ term];
actual = If[initialized && ListQ[SuperPotential], Sort[canonical /@ SuperPotential[[All,2]]], {}];
expected = Sort[canonical /@ {
  {X}, {X}, {Zp}, {Zp},
  {X,Sbc,Sc}, {X,P,Pb}, {Zp,Sbc,Sc}, {Zp,P,Pb},
  {X,X,X}, {X,X,Zp}, {X,Zp,Zp}, {Zp,Zp,Zp},
  {X,H,H}, {X,SigC,SigBc}, {Zp,H,H}, {Zp,SigC,SigBc},
  {Sc,Sc,SigC}, {Sbc,Sbc,SigBc},
  {Q,H,Qc}, {Q,H,PsiC}, {Psi,H,Qc}, {Psi,H,PsiC},
  {P,PsiBar,Q}, {P,PsiBar,Psi},
  {P,PsiCBar,Qc}, {P,PsiCBar,PsiC},
  {Sbc,Qc,Nv}, {Sbc,PsiC,Nv}, {Nv,Nv},
  {Pb,A2,A32}, {P,A15,A17}, {P,A16,A16}
}];
v39Emit["processed_W_exactly_32_terms", count === 32];
v39Emit["processed_W_full_structural_multiset_exact", actual === expected];
v39Emit["z5610_and_z3_globals_loaded", initialized && Length[Global] === 2 &&
  Global[[1,1]] === Z[5610] && Global[[2,1]] === Z[3]];

rMap = Association[Rule @@@ V39Z4RCharges];
z3Map = Association[Rule @@@ V39Z3Charges];
v39Emit["all_processed_W_terms_have_Z4R_charge_2", initialized && And @@
  (Mod[Total[Lookup[rMap, #]], 4] === 2 & /@ SuperPotential[[All,2]])];
v39Emit["all_processed_W_terms_have_Z3_charge_0", initialized && And @@
  (Mod[Total[Lookup[z3Map, #]], 3] === 0 & /@ SuperPotential[[All,2]])];

forbidden = {{X,Q,Q,Q,Q}, {X,Qc,Qc,Qc,Qc}, {Zp,Q,Q,Q,Q}, {Zp,Qc,Qc,Qc,Qc}};
v39Emit["four_local_driver_dressed_four_matter_sources_Z3_forbidden", initialized && And @@
  (Mod[Total[Lookup[z3Map, #]], 3] =!= 0 & /@ forbidden)];
v39Emit["split_six_replacement_terms_present", initialized && And @@
  (MemberQ[actual, canonical[#]] & /@ {
    {X,SigC,SigBc}, {Zp,SigC,SigBc}, {Sc,Sc,SigC}, {Sbc,Sbc,SigBc}
  })];
v39Emit["old_single_six_terms_absent", initialized && And @@
  (FreeQ[actual, #] & /@ (canonical /@ {
    {X,Sig6,Sig6}, {Zp,Sig6,Sig6}, {Sc,Sc,Sig6}, {Sbc,Sbc,Sig6}
  }))];
v39Emit["processed_component_superpotential_nonzero", initialized &&
  ValueQ[Superpotential] && Superpotential =!= 0 && ValueQ[WCouplings] &&
  Length[WCouplings] === 32];
v39Emit["Start_log_free_of_source_errors", initialized && And @@
  (StringFreeQ[Last[load], #] & /@ {
    "ModelFile::", "Extract::", "Part::", "Dot::dotsh",
    "not invariant", "does not conserve"
  })];
continuous = If[initialized, v39Capture[CheckAnomalies], {False, "not initialized"}];
v39Emit["continuous_gauge_anomaly_check_succeeded", First[continuous] &&
  StringFreeQ[Last[continuous], "WARNING!"]];

all = And @@ Values[checks];
Quiet[Check[DeleteDirectory[work, DeleteContents -> True], Null]];
Exit[If[all, 0, 1]];
