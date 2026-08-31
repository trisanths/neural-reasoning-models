#!/bin/bash
cd ~/decoupled-reasoner
set -u
# wait for the greedy pass over the twelve shape set, then its sampled companion
while pgrep -f "cmpwork.runa --mode greedy$" > /dev/null; do sleep 20; done
.venv/bin/python -m src.norm.cmpwork.runa --mode sampled --cap 20 \
  --out results/norm/compare/a_sampled.jsonl.gz > logs/cmp/a_sampled.log 2>&1
# then the transposed set
while pgrep -f "x_items.jsonl.gz --out results/norm/compare/x_a_greedy" > /dev/null; do sleep 20; done
.venv/bin/python -m src.norm.cmpwork.runa --mode sampled --limit 500 \
  --items results/norm/compare/x_items.jsonl.gz \
  --out results/norm/compare/x_a_sampled.jsonl.gz > logs/cmp/x_a_sampled.log 2>&1
echo DONE > logs/cmp/sampled_done.txt
