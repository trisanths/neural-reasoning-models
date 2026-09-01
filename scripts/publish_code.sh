#!/usr/bin/env bash
# Publish a snapshot of the current worktree to S3 so a fresh worker can get the
# code without GitHub credentials. Run this on a box that has the repo.
#
# The archive holds tracked plus untracked-but-not-ignored files, minus the big
# generated trees (data, results, runs, logs) and minus the virtualenv. It is
# named by the HEAD commit, and a sidecar manifest records whether the worktree
# had uncommitted changes at the time, so a worker can tell exactly what it has.
#
# usage: bash scripts/publish_code.sh
set -euo pipefail

BUCKET="${BUCKET:-s3://decoupled-reasoner-009398924577}"
REGION="${AWS_REGION:-us-east-1}"
REPO="${REPO:-$HOME/decoupled-reasoner}"

cd "$REPO"
SHA=$(git rev-parse HEAD)
SHORT=$(git rev-parse --short=7 HEAD)
DIRTY=clean
[ -n "$(git status --porcelain)" ] && DIRTY=dirty

TAR="${TMPDIR:-/tmp}/repo-$SHORT.tar.gz"
LIST="${TMPDIR:-/tmp}/repo-$SHORT.files"
KEY="code/repo-$SHORT.tar.gz"

rm -f "$TAR" "$LIST"
git ls-files -c -o --exclude-standard -z > "$LIST"

# GNU tar applies --exclude only to members named after it, so the excludes have
# to come before -T.
nice -n 19 ionice -c3 tar \
  --exclude='data/*' --exclude='results/*' --exclude='runs/*' --exclude='logs/*' \
  --exclude='*__pycache__*' --exclude='.venv/*' --exclude='.pytest_cache/*' \
  --exclude='*.pt' --exclude='*.bin' --exclude='*.idx' --exclude='*.safetensors' \
  --null -T "$LIST" -czf "$TAR"

NFILES=$(tar tzf "$TAR" | wc -l)
BYTES=$(stat -c %s "$TAR")

aws s3 cp "$TAR" "$BUCKET/$KEY" --region "$REGION" --quiet

cat > "${TMPDIR:-/tmp}/repo-$SHORT.manifest.json" <<JSON
{
  "key": "$KEY",
  "commit": "$SHA",
  "commit_short": "$SHORT",
  "worktree": "$DIRTY",
  "files": $NFILES,
  "bytes": $BYTES,
  "published_utc": "$(date -u +%FT%TZ)",
  "published_from": "$(hostname)"
}
JSON
aws s3 cp "${TMPDIR:-/tmp}/repo-$SHORT.manifest.json" \
  "$BUCKET/code/repo-$SHORT.manifest.json" --region "$REGION" --quiet

# The pointer a fresh worker reads when it is not told a specific snapshot.
printf '%s\n' "$KEY" > "${TMPDIR:-/tmp}/LATEST"
aws s3 cp "${TMPDIR:-/tmp}/LATEST" "$BUCKET/code/LATEST" --region "$REGION" --quiet

# A fresh box has no code yet, so the bootstrap script has to sit next to the
# snapshot rather than inside it. Keep the S3 copy in step with the repo copy.
aws s3 cp "$REPO/scripts/bootstrap_worker.sh" "$BUCKET/code/bootstrap_worker.sh" \
  --region "$REGION" --quiet

rm -f "$LIST"
echo "published $KEY  commit $SHORT ($DIRTY)  $NFILES files  $BYTES bytes"
