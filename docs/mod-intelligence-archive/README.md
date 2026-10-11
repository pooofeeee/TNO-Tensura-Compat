# Mod Intelligence project archive

Historical cut-off: **2026-10-11**, repository `pooofeeee/TNO-Tensura-Compat`, branch
`feat/mod-intelligence-v1`. Last previously committed tooling state:
[`e0918e7`](https://github.com/pooofeeee/TNO-Tensura-Compat/commit/e0918e782355756f718a1adcff1f346a26230327).
This archive also preserves and commits the completed Task Preflight experiment,
which was uncommitted at the cut-off. It is an external wrapper, **not V5**.

The project began to make completed mod research usable during coding without
rescanning JARs or repeating research. It evolved from verified retrieval into
impact/context, bounded change plans, adaptive projections, and experiments aimed
at reducing Astra Medium's repeated reasoning while preserving correctness.
**No measured token, billing, allowance or reasoning-usage savings have been
established.** Faster runs, fewer calls and smaller byte outputs are distinct
observations, not substitutes for usage telemetry.

## Reading map

- [Origin, versions and chronology](history.md): V1, integrity repairs, V1.5,
  V2.0, target-resolution prototype, V3, V4 and Task Preflight.
- [Every recorded experiment and benchmark](experiments.md): methods, outcomes,
  numerical results and limits, including failed/discarded setup.
- [Architecture and decision register](architecture-and-decisions.md): what each
  layer owns, why designs were chosen, and what remains manual.
- [Validation and future work](validation-and-future.md): test evolution,
  remaining risks and evidence needed before expanding or adopting a workflow.
- [Artifact index](artifact-index.md): original reports, complete compressed
  experiment workspaces, SHA-256 manifests and source-tree references.
- [Commit ledger](commits.json): exact commit IDs, UTC author dates and subjects.

## Current disposition

V1–V4 are implemented and validated. Task Preflight is implemented and validated
as a small deterministic experiment around unchanged planners. Research and
production are preserved. Experimental coding solutions exist only in archived
isolated workspaces; they are not production changes. This archive does not
activate a default workflow, implement a router, or authorize further research.

The latest fresh coding A/B experiment used the repository Sugar Rush offline
preview API and CLI. Both arms passed 40 tests in all three Python modes. The
wrapper removed a restoration decision but not a retrieval call in that run:
output truncation caused a duplicate preflight. Its observed 8 versus 10
operations and 77.5 versus 82.6 seconds do not establish a usage benefit.

## Completeness, provenance and restoration

This is a complete capture of the **available project records identified in the
repository and its project-specific execution directories**, not an invented
transcript of undocumented decisions. Original reports, manifests, scripts,
responses, event logs, tests, solutions and frozen source exports are retained
byte-for-byte in per-experiment archives. Readable report copies are provided
alongside them. Historic failures, contradictory scope assumptions and abandoned
setup attempts are preserved rather than rewritten into successes.

The archive omits no regular file in the inventoried experiment directories.
Catalog/docs symlinks are recorded as references rather than dereferenced or
packaged as potentially unsafe links. Their backing Git trees remain in this
repository. Third-party JARs and unrelated research attachments are not part of
this tooling archive. The original external Astra audit attachment was not found
among available attachments; its five reported findings, independent
reproductions and repair evidence are preserved. Full chat transcripts and actual
model-usage telemetry were not exported; their absence is explicit.

Run `python3 docs/mod-intelligence-archive/verify_archive.py` after cloning to
verify archives, all member hashes and readable copies. To inspect a workspace,
extract its `.tar.gz` into a scratch directory; members contain relative regular
file paths only. Consult its manifest for original symlink targets and Git tree
references. Historical scripts often contain `/workspace/mod-intelligence-v1`
absolute paths; relocate those paths in a scratch copy before replay. Restoring
files is not a request to rerun research, consume model calls or apply a solution.

Source documents elsewhere in `docs/` remain the implementation references. Some
historical documents described `run/` artifacts as ignored/local; the archive
now publishes those exact artifacts without altering the original text. Test
counts and measurements belong to their recorded snapshot, not a universal
claim about all versions or future coding tasks.
