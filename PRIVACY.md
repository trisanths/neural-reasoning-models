# What is public here

This repository was made public on 2026-10-08.

Nothing here is a credential. A scan of all 5,373 blobs reachable from any ref,
plus a prefix sweep for AWS keys, GitHub tokens, OpenAI, Hugging Face, Slack and
Google keys, private key blocks and database connection strings, returns nothing
on any branch. There is no `.env` file in any commit. The Exa key the retrieval
lane uses is read at runtime from SSM Parameter Store at
`/decoupled-reasoner/exa-api-key`;
`decoupled-reasoner/scripts/bootstrap_worker.sh` carries the parameter path and
never the value. GitHub's own secret scanning now runs on this repository as
well, since it is public.

What the scan did find is identifying detail, all of it the author's own. It is
listed here because it is now world-readable, and because removing it from
history is a separate decision from having published.

## Contact details

- `latent-transfer/slide/slide.html` line 204 and the rendered
  `latent-transfer/slide/slide.pdf` carry a contact footer with a berkeley.edu
  address. The slide is a pitch artifact, so the address is deliberate.
  `slide.png`, `slide-4k.png` and `slide.svg` are the same slide with no
  extractable text, and `slide.pptx` is the source.
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

## Scrubbing, if that is wanted later

The slide contact footer is a choice rather than a leak. The wandb run
directories are the only material worth acting on, and they are also the least
load-bearing part of the repository: they are the SDK's own logs from an April
2026 run, not results that anything cites. Dropping
`latent-translation/wandb/` and `latent-translation/.claude/` would remove every
item in the two sections above except the slide footer and the
`judged_ideas.json` path, and would also end the Dependabot pull requests that a
`requirements.txt` captured inside one of those run directories generates.
Automated security fixes are disabled on this repository for that reason; the
alerts are still on.

Removing them from `main` alone does not remove them from history, and they stay
reachable from `history/latent-translation` by design. A clean removal needs
either a filtered rewrite of this repository or a fresh one built from a
filtered tree. Because the repository is already public, a rewrite does not
recall anything that has been fetched, cached or forked in the meantime.
