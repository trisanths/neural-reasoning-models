#!/bin/bash
cd ~/decoupled-reasoner
while pgrep -f "h_items.jsonl.gz --out results/norm/compare/h_a_greedy" > /dev/null; do sleep 15; done
.venv/bin/python -m src.norm.cmpwork.runa --mode sampled --cap 20 \
  --items results/norm/compare/h_items.jsonl.gz \
  --out results/norm/compare/h_a_sampled.jsonl.gz > logs/cmp/h_a_sampled.log 2>&1
echo DONE > logs/cmp/hs_done.txt
