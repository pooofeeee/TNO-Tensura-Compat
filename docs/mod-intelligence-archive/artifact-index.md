# Artifact index

Every regular file in these 16 available project experiment directories is captured. Archives contain regular files only; symlink dependencies are recorded in manifests and backed by Git trees. Raw historical text, absolute paths, failure logs and discarded attempts are unchanged.

| Experiment | Files | References | Compressed bytes | Evidence |
| --- | ---: | ---: | ---: | --- |
| five-defect-repair-final-check | 18 | 1 | 300,919 | [Archive](artifacts/five-defect-repair-final-check.tar.gz) · [SHA-256 manifest](manifests/five-defect-repair-final-check.json) |
| five-defect-repair-recheck | 12 | 0 | 285,715 | [Archive](artifacts/five-defect-repair-recheck.tar.gz) · [SHA-256 manifest](manifests/five-defect-repair-recheck.json) |
| mod-intelligence-ab-validation | 591 | 1 | 1,773,835 | [Archive](artifacts/mod-intelligence-ab-validation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-ab-validation.json) · [Original report](reports/mod-intelligence-ab-validation.md) |
| mod-intelligence-astra-economic-evaluation | 659 | 1 | 1,994,839 | [Archive](artifacts/mod-intelligence-astra-economic-evaluation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-astra-economic-evaluation.json) · [Original report](reports/mod-intelligence-astra-economic-evaluation.md) |
| mod-intelligence-astra-effort-evaluation | 660 | 1 | 1,980,231 | [Archive](artifacts/mod-intelligence-astra-effort-evaluation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-astra-effort-evaluation.json) · [Original report](reports/mod-intelligence-astra-effort-evaluation.md) |
| mod-intelligence-astra-medium-evaluation | 656 | 1 | 1,923,119 | [Archive](artifacts/mod-intelligence-astra-medium-evaluation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-astra-medium-evaluation.json) · [Original report](reports/mod-intelligence-astra-medium-evaluation.md) |
| mod-intelligence-complex-ab-validation | 604 | 1 | 1,788,845 | [Archive](artifacts/mod-intelligence-complex-ab-validation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-complex-ab-validation.json) · [Original report](reports/mod-intelligence-complex-ab-validation.md) |
| mod-intelligence-impact-prototype | 590 | 1 | 1,828,764 | [Archive](artifacts/mod-intelligence-impact-prototype.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-impact-prototype.json) |
| mod-intelligence-real-coding-benchmark | 856 | 1 | 2,360,342 | [Archive](artifacts/mod-intelligence-real-coding-benchmark.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-real-coding-benchmark.json) · [Original report](reports/mod-intelligence-real-coding-benchmark.md) |
| mod-intelligence-v15-validation | 1 | 0 | 5,232 | [Archive](artifacts/mod-intelligence-v15-validation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-v15-validation.json) |
| mod-intelligence-v2-validation | 9 | 0 | 45,795 | [Archive](artifacts/mod-intelligence-v2-validation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-v2-validation.json) |
| mod-intelligence-v3-validation | 18 | 0 | 101,847 | [Archive](artifacts/mod-intelligence-v3-validation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-v3-validation.json) |
| mod-intelligence-v4-validation | 16 | 0 | 53,427 | [Archive](artifacts/mod-intelligence-v4-validation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-v4-validation.json) |
| mod-intelligence-validation | 5 | 0 | 16,484 | [Archive](artifacts/mod-intelligence-validation.tar.gz) · [SHA-256 manifest](manifests/mod-intelligence-validation.json) |
| task-preflight-ab | 1237 | 2 | 3,686,910 | [Archive](artifacts/task-preflight-ab.tar.gz) · [SHA-256 manifest](manifests/task-preflight-ab.json) · [Original report](reports/task-preflight-ab.md) |
| task-preflight-experiment | 7 | 0 | 29,516 | [Archive](artifacts/task-preflight-experiment.tar.gz) · [SHA-256 manifest](manifests/task-preflight-experiment.json) |

[Machine-readable package index](artifact-index.json). Use `python3 docs/mod-intelligence-archive/verify_archive.py` to check every package/member and readable report.

The source catalog is already committed under `docs/benchmarks/external-effects-catalog`; archives do not duplicate symlinked research trees or include third-party JARs. The `mod-intelligence-real-coding-benchmark` archive includes `discarded-attempt1/` and runner authentication-probe diagnostics.

A preexisting, uncommitted change-request draft is preserved separately in [notes/draft-sugar-rush-change.json](notes/draft-sugar-rush-change.json). It remains a draft, not an active manifest or applied change.
