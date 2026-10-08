# Keep the pretrain alive for its 40 hours. The trainer resumes from
# OUT/latest.pt, written every 1000 steps, so a restart costs at most that. It
# stops for good once the log says the run reached its last step.
#
# Liveness is counted off ps with the command name pinned to python3, not off a
# bare pgrep -f. A bare pgrep on this pattern also matches the shell that is
# running the check, and a pgrep matching wrapper shells has cost this project
# a result before.
set -u
RUN=/mnt/nvme/runs/e3-350m
CFG=configs/350m-e3-run.yaml
cd /home/ec2-user/decoupled-reasoner || exit 1

alive () {
  ps -eo comm=,args= | awk '$1=="python3" && /src\.train\.cli/ && /350m-e3-run/ {c++} END{print c+0}'
}

while true; do
  if grep -q "done at step" $RUN/train.log 2>/dev/null; then
    echo "$(date -u +%FT%TZ) pretrain finished, supervisor exiting"
    exit 0
  fi
  n=$(alive)
  if [ "$n" -eq 0 ]; then
    echo "$(date -u +%FT%TZ) trainer absent, restarting with --resume"
    tail -30 $RUN/train.log >> $RUN/train.crashlog 2>/dev/null
    setsid nohup env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      /home/ec2-user/.local/bin/uv run python -m src.train.cli --config $CFG \
      --data /home/ec2-user/data/regime_e3 --out $RUN --resume \
      >> $RUN/train.log 2>&1 < /dev/null &
    disown || true
    sleep 300
  fi
  sleep 120
done
