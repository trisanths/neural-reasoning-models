#!/bin/bash
cd ~/decoupled-reasoner
set -u
.venv/bin/python -m src.norm.cmpwork.runb --procs 2 --items results/norm/compare/h_items.jsonl.gz --out results/norm/compare/h_b.jsonl.gz > logs/cmp/h_b.log 2>&1
.venv/bin/python -m src.norm.cmpwork.runc --ckpt results/norm/train/ckpt_l.pt --items results/norm/compare/h_items.jsonl.gz --out results/norm/compare/h_c_l.jsonl.gz > logs/cmp/h_c_l.log 2>&1
.venv/bin/python -m src.norm.cmpwork.runc --ckpt results/norm/train/ckpt_xs.pt --items results/norm/compare/h_items.jsonl.gz --out results/norm/compare/h_c_xs.jsonl.gz > logs/cmp/h_c_xs.log 2>&1
.venv/bin/python -m src.norm.cmpwork.runa --mode greedy --items results/norm/compare/h_items.jsonl.gz --out results/norm/compare/h_a_greedy.jsonl.gz > logs/cmp/h_a_greedy.log 2>&1
.venv/bin/python -m src.norm.cmpwork.runa --mode sampled --items results/norm/compare/h_items.jsonl.gz --out results/norm/compare/h_a_sampled.jsonl.gz > logs/cmp/h_a_sampled.log 2>&1
echo DONE > logs/cmp/home_done.txt
