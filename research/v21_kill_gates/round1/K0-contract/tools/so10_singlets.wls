#!/usr/bin/env wolframscript
(* Count SO(10) singlets in products of irreps with Susyno (SARAH's bundled copy).
   Usage: wolframscript -file so10_singlets.wls <input.txt> <output.txt>
   input: one line per query: "<id> r1 r2 r3 ..." with signed dimensions in {1, 10, -10, 16, -16, 126, -126, 210}.
   output: "<id> <number of singlets>" per line. *)
susynoFile = "C:/Users/jayal/Downloads/So10Theory2/external-tools/SARAH-4.15.3/Susyno/LieGroups_SARAH.m";
Get[susynoFile];
so10 = CartanMatrix["SO", 10];
labels = <|1 -> {0, 0, 0, 0, 0}, 10 -> {1, 0, 0, 0, 0}, -10 -> {1, 0, 0, 0, 0},
  16 -> {0, 0, 0, 0, 1}, -16 -> {0, 0, 0, 1, 0}, 126 -> {0, 0, 0, 0, 2}, -126 -> {0, 0, 0, 2, 0},
  210 -> {0, 0, 0, 1, 1}, 45 -> {0, 1, 0, 0, 0}, 54 -> {2, 0, 0, 0, 0}, 120 -> {0, 0, 1, 0, 0}|>;
(* sanity: dimensions *)
Print["DIMS ", ToString[Table[{k, DimR[so10, labels[k]]}, {k, Keys[labels]}], InputForm]];
args = $ScriptCommandLine;
inFile = args[[-2]]; outFile = args[[-1]];
lines = Select[StringSplit[Import[inFile, "Text"], "\n"], StringLength[#] > 0 &];
out = {};
Do[
  parts = StringSplit[line];
  id = parts[[1]];
  reps = ToExpression /@ Rest[parts];
  reps = DeleteCases[reps, 1];
  count = If[reps === {}, 1,
    Module[{red},
      red = ReduceRepProduct[so10, labels /@ reps];
      Total[Cases[red, {{0, 0, 0, 0, 0}, m_} :> m]]
    ]];
  AppendTo[out, id <> " " <> ToString[count]];
  , {line, lines}];
Export[outFile, StringRiffle[out, "\n"], "Text"];
Print["DONE ", Length[out]];
