#!/usr/bin/env wolframscript
(* Stage-2a "model", method (c): independent Susyno (R. Fonseca, bundled with SARAH 4.15.3) count of SO(10)
   invariants in products of SYMMETRIC powers of irreps (bosonic fields).  For each query the number of singlets in
   Sym^k1(R1) x Sym^k2(R2) x ... is NumberOfInvariantsInProduct[cm, {Plethysms[cm, R1, {k1}], ...}].
   Usage: wolframscript -file susyno_count_v22.wls <input.txt> <output.txt>
   input line: "<id> <rep>:<power> <rep>:<power> ..." with rep in {10, 45, 210, 126, -126, 54, 16, -16}.
   Dynkin labels exactly as in the v21 K0 tool so10_singlets.wls (Susyno convention): 126bar_H = -126 = {0,0,0,2,0}. *)
susynoFile = "C:/Users/jayal/Downloads/So10Theory2/external-tools/SARAH-4.15.3/Susyno/LieGroups_SARAH.m";
Get[susynoFile];
(* The plethysm section of Fonseca's Susyno (Adams operations, S_n characters, Plethysms,
   NumberOfInvariantsInProduct) ships COMMENTED OUT in SARAH's LieGroups_SARAH.m (in 4.15.3: the block between a
   lone "(*" line and a lone "*)" line that encloses the definition "Plethysms[cm_,weight_,partition_]").  It is
   located programmatically and evaluated here, unmodified, from the file text inside the package context (the
   external file is not edited). *)
srcLines = StringReplace[#, "\r" -> ""] & /@ ReadList[susynoFile, String, NullRecords -> True];
openPos = Flatten[Position[StringTrim /@ srcLines, "(*"]];
closePos = Flatten[Position[StringTrim /@ srcLines, "*)"]];
defPos = First[Flatten[Position[srcLines, s_String /; StringStartsQ[s, "Plethysms[cm_,weight_,partition_]"]]]];
blkOpen = Max[Select[openPos, # < defPos &]];
blkClose = Min[Select[closePos, # > defPos &]];
Print["PLETHYSM_BLOCK lines ", blkOpen, " .. ", blkClose, " (definition at ", defPos, ")"];
Begin["Susyno`LieGroups`"];
ToExpression[StringRiffle[srcLines[[blkOpen + 1 ;; blkClose - 1]], FromCharacterCode[10]]];
End[];
Print["PLETHYSM_SECTION_LOADED ", ValueQ[Susyno`LieGroups`Plethysms[1, 1, 1]] || Length[DownValues[Susyno`LieGroups`Plethysms]] > 0];
so10 = CartanMatrix["SO", 10];
(* sanity: Sym^2(45) must contain 4 irreps 1+54+210+770 *)
Print["SYM2_45 ", ToString[Plethysms[so10, {0, 1, 0, 0, 0}, {2}], InputForm]];
labels = <|1 -> {0, 0, 0, 0, 0}, 10 -> {1, 0, 0, 0, 0}, 16 -> {0, 0, 0, 0, 1}, -16 -> {0, 0, 0, 1, 0},
  126 -> {0, 0, 0, 0, 2}, -126 -> {0, 0, 0, 2, 0}, 210 -> {0, 0, 0, 1, 1}, 45 -> {0, 1, 0, 0, 0},
  54 -> {2, 0, 0, 0, 0}, 120 -> {0, 0, 1, 0, 0}|>;
Print["DIMS ", ToString[Table[{k, DimR[so10, labels[k]]}, {k, Keys[labels]}], InputForm]];
args = $ScriptCommandLine;
inFile = args[[-2]]; outFile = args[[-1]];
lines = Select[StringSplit[Import[inFile, "Text"], "\n"], StringLength[StringTrim[#]] > 0 &];
out = {};
Do[
  parts = StringSplit[line];
  id = parts[[1]];
  facs = Map[ToExpression[StringSplit[#, ":"]] &, Rest[parts]];
  facs = Select[facs, #[[1]] =!= 1 &];
  t0 = AbsoluteTime[];
  count = If[facs === {}, 1,
    Module[{polys},
      polys = Map[If[#[[2]] == 1, {{labels[#[[1]]], 1}}, Plethysms[so10, labels[#[[1]]], {#[[2]]}]] &, facs];
      NumberOfInvariantsInProduct[so10, polys]
    ]];
  AppendTo[out, id <> " " <> ToString[count]];
  Print["Q ", id, " ", count, " t=", Round[AbsoluteTime[] - t0, 0.01]];
  Export[outFile, StringRiffle[out, "\n"], "Text"];
  , {line, lines}];
Print["DONE ", Length[out]];
