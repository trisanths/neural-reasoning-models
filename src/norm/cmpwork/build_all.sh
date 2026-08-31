#!/bin/bash
# Rebuild every report, every table and the document from the record files.
cd ~/decoupled-reasoner
set -eu
P=.venv/bin/python
$P -m src.norm.cmpwork.report --stem main --items results/norm/compare/items.jsonl.gz \
   --out results/norm/compare/report_main.json
$P -m src.norm.cmpwork.report --stem h --items results/norm/compare/h_items.jsonl.gz \
   --out results/norm/compare/report_home.json
$P -m src.norm.cmpwork.report --stem d --items results/norm/compare/d_items.jsonl.gz \
   --keys split,depth --out results/norm/compare/report_depth.json
$P -m src.norm.cmpwork.report --stem n --items results/norm/compare/n_items.jsonl.gz \
   --keys split,depth --out results/norm/compare/report_depth_narrow.json
$P -m src.norm.cmpwork.xreport --items results/norm/compare/x_items.jsonl.gz --stem x \
   --out results/norm/compare/report_transpose.json > /dev/null
$P -m src.norm.cmpwork.tables
$P scripts/norm_compare_md.py
# every report must be newer than the records it read
for r in results/norm/compare/report_*.json; do
  for f in results/norm/compare/*.jsonl.gz; do
    if [ "$f" -nt "$r" ]; then echo "STALE: $r is older than $f"; exit 1; fi
  done
done
echo "reports are newer than every record file"
