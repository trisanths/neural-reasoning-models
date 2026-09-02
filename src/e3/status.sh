# Compact one-shot status for the monitor. Every line is a potential event.
# grep -c prints its own 0 and exits 1 when nothing matches, so a trailing
# "|| echo 0" appends a second zero and the count stops comparing equal to
# "0". That produced a false restart alarm the first time; count with a
# helper that returns exactly one number instead.
R=/mnt/nvme/e3eval
RUN=/mnt/nvme/runs/e3-350m
count () {  # count matches of $1 in file $2, 0 if the file is absent
  [ -f "$2" ] || { echo 0; return; }
  grep -c -- "$1" "$2" 2>/dev/null | head -1
}
lines () { [ -f "$1" ] && wc -l < "$1" | tr -d " " || echo 0; }
ALIVE=$(ps -eo comm=,args= | awk "\$1==\"python3\" && /src\.train\.cli/ && /350m-e3-run/ {c++} END{print c+0}")
STEP=$(tail -1 $RUN/loss.jsonl 2>/dev/null | sed -E "s/.*\"step\": ([0-9]+).*/\1/")
LOSS=$(tail -1 $RUN/loss.jsonl 2>/dev/null | sed -E "s/.*\"loss\": ([0-9.]+).*/\1/" | cut -c1-6)
RESTARTS=$(count restarting $RUN/supervise.log)
CURVEN=$(lines $R/curve.jsonl)
AEERR=$(count "cycle error" $R/autoeval.log)
FIN=$(tail -1 $R/logs/finish.log 2>/dev/null)
echo "STAT step=$STEP loss=$LOSS alive=$ALIVE restarts=$RESTARTS curve=$CURVEN aeerr=$AEERR finish=[$FIN]"
[ "$RESTARTS" -gt 0 ] 2>/dev/null && echo "RESTART_ALARM $(grep restarting $RUN/supervise.log | tail -2 | tr "\n" " ")"
if [ "$ALIVE" = "0" ] && ! grep -q "done at step" $RUN/train.log 2>/dev/null; then echo "TRAINER_ABSENT"; fi
[ "$CURVEN" -gt 0 ] 2>/dev/null && python3 -c "
import json
for l in open(\"$R/curve.jsonl\"):
    l=l.strip()
    if not l: continue
    d=json.loads(l)
    m=d.get(\"mmlu_n1000\") or {}
    c=m.get(\"pred_letter_counts\") or []
    tot=sum(c) or 1
    r=d.get(\"retrieval_none_n200\") or {}
    print(\"ROW step=%d tok=%.2fB tpp=%.2f acc=%s ci=%s modal=%.3f issued=%s\" % (
        d[\"step\"], d[\"tokens_seen\"]/1e9, d[\"tokens_per_param\"],
        m.get(\"acc\"), m.get(\"ci95\"), max(c)/tot if c else -1,
        r.get(\"issued_query\")))
"
exit 0
