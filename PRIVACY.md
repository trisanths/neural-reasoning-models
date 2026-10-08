# Before this repository is made public

It is private. Nothing here is a credential: a scan of all 5,373 blobs
reachable from any ref, plus a prefix sweep for AWS keys, GitHub tokens,
OpenAI, Hugging Face, Slack and Google keys, private key blocks and database
connection strings, returns nothing on any branch. There is no `.env` file in
any commit. The Exa key the retrieval lane uses is read at runtime from SSM
Parameter Store at `/decoupled-reasoner/exa-api-key`;
`decoupled-reasoner/scripts/bootstrap_worker.sh` carries the parameter path and
never the value.

What the scan did find is identifying detail. None of it is a secret and all of
it is the author's own, so it is listed here rather than removed, because
removing it from history is a different decision from publishing.

## Contact details

- `latent-transfer/slide/slide.html` line 204 and the rendered
  `latent-transfer/slide/slide.pdf` carry a contact footer with a berkeley.edu
  address. The slide is a pitch artifact, so the address is presumably
  deliberate. `slide.png`, `slide-4k.png` and `slide.svg` are the same slide
  with no extractable text, and `slide.pptx` is the source.
- The six `latent-translation/wandb/run-*/files/wandb-metadata.json` files carry
  an `email` field with a gmail address, which is a different address from the
  one on the commits.

## Machine and account identifiers

- The same wandb metadata records the workstation that produced those runs: a
  hostname, a Windows username, a GPU UUID, a disk capacity, and a root path of
  the form `C:\Users\...\latent-space-translation`.
- `latent-translation/wandb/run-*/logs/debug.log` and `debug-internal.log` name
  the Weights and Biases entity the runs were logged to. That is an account
  name, not a key.
- `latent-translation/.claude/settings.local.json` is a committed tool
  allowlist whose entries disclose the working directory the project was
  developed in.

## An unrelated project name

Two judge verdicts inside
`latent-transfer/experiments/ca_depth/panel/judged_ideas.json` quote an
absolute path from the author's laptop. It discloses the account name and the
directory name of a separate, unpublished project.

## If publishing

The slide contact footer is a choice, not a leak. The wandb run directories are
the only material worth acting on, and they are also the least load-bearing
part of the repository: they are the SDK's own logs from an April 2026 run, not
results anything cites. Dropping
`latent-translation/wandb/` and `latent-translation/.claude/` would remove
every item in the two sections above except the slide footer and the
`judged_ideas.json` path, and would also end the Dependabot pull requests that
a `requirements.txt` captured inside one of those run directories generates.
Automated security fixes are currently disabled on this repository for that
reason; the alerts are still on.

Removing them from `main` alone does not remove them from history, and they are
reachable from `history/latent-translation` by design, so a public release that
needs them gone needs either a filtered rewrite or a fresh repository built
from a filtered tree.
