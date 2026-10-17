#!/usr/bin/env python3
"""Assemble REPORT.txt from REPORT_head.txt, report_static.txt, REPORT_mid.txt, REPORT_tail.txt and placeholder fills."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sections(text):
    """Split on lines like 'N. TITLE' / 'Nb. TITLE' followed by a dashed line; return {key: block}."""
    lines = text.splitlines(keepends=True)
    idx = [i for i in range(len(lines) - 1)
           if re.match(r"^\d+b?\. ", lines[i]) and re.match(r"^-{5,}", lines[i + 1])]
    out = {}
    for k, i in enumerate(idx):
        j = idx[k + 1] if k + 1 < len(idx) else len(lines)
        key = lines[i].split(".")[0]
        out[key] = "".join(lines[i:j]).rstrip() + "\n\n"
    return out


head = open(os.path.join(HERE, "REPORT_head.txt"), encoding="utf-8").read()
st = sections(open(os.path.join(HERE, "report_static.txt"), encoding="utf-8").read())
mid = sections(open(os.path.join(HERE, "REPORT_mid.txt"), encoding="utf-8").read())
tail = sections(open(os.path.join(HERE, "REPORT_tail.txt"), encoding="utf-8").read())
order = [("1", st), ("2", mid), ("3", st), ("4", mid), ("5", mid), ("6", mid), ("7", mid), ("8", tail), ("8b", st),
         ("9", st), ("10", tail), ("11", st), ("12", tail), ("13", st), ("14", tail), ("15", tail), ("16", tail)]
body = head + "".join(src[k] for k, src in order)
fills = json.load(open(os.path.join(HERE, "fills.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "fills.json")) else {}
for k, v in fills.items():
    body = body.replace(k, v)
left = re.findall(r"\[\[[A-Z0-9_]+\]\]", body)
open(os.path.join(HERE, "REPORT.txt"), "w", encoding="utf-8").write(body)
print("written", len(body), "chars; unfilled placeholders:", left)
