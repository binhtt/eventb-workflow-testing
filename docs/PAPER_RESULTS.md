# Mapping the manuscript to the artifact

This mapping was checked against the supplied `IEEE_ACCESS_Agent.pdf` on
2026-11-07. Table numbers identify that manuscript version and may change
in a later revision. The manuscript PDF is not redistributed in this repository.

## Result locations

| Manuscript evidence | Recorded source | Reproduction or inspection |
|---|---|---|
| Table 4: 15 INV, 6 THM, 3 WD; 24 automatically discharged | `proof/SharedWorkflow/Resource.bps`, `.bpo`, `.bpr`; `proof/summary.json` | Native Rodin import/reprove: [RODIN.md](RODIN.md); metadata audit: `python scripts/verify_artifact.py` |
| Table 5: 2,127 states; 49,776 operation attempts | `results/model_conformance.json` | Full reproduction; includes complete finite instances (1,1), (2,1), (3,2) |
| Model/proof bridge: 600 suites, 9,600 identical schedules | `results/proof_bridge.json`, `results/proof_normalization.json` | `verify_bridge.py`, invoked by smoke and full reproduction |
| Table 6: all nine mutants, 150 trials per mutant and method | `results/trials.csv`, `results/per_mutant.csv` | `python code/reproduce.py --mode analysis` |
| Table 7: qualified detections, denominator 550 | `results/trials.csv`, `results/qualified_summary.csv` | Analysis; paper export aggregates across configurations |
| Table 8: E1, requests/capacity (4,2), seed 0, model-derived scheduling | `results/witnesses.json` | Filter the JSON list by method `model_conflicts`, requests 4, capacity 2, mutant `reserve_lost_update`, seed 0; the exporter retains the log through its first failure |
| Figure 4: cumulative first detection, budgets 1 through 16 | `results/trials.csv` | `python scripts/export_paper_results.py`; exports `figure4_detection_curve.csv` |
| Table 9: paired seed-cluster bootstrap intervals | `results/paired_bootstrap.csv` | Analysis; 10,000 bootstrap resamples per budget |
| Table 10: separate reference-only suite timings | `results/standalone_timing.csv`, `results/standalone_timing_summary.csv` | Full reproduction reruns the timing study; absolute timings depend on hardware and load |
| Main replay totals: 9,600 reference, 86,400 mutant | `results/run_summary.json`, `results/costs.csv` | Full reproduction and deterministic result comparison |

## Fault identifiers

| Paper ID | Code identifier | Split |
|---|---|---|
| D1 | `reserve_cached` | Development |
| D2 | `execute_cached` | Development |
| D3 | `release_cached` | Development |
| E1 | `reserve_lost_update` | Reserved evaluation |
| E2 | `release_wrong_key` | Reserved evaluation |
| E3 | `execute_after_release` | Reserved evaluation |
| E4 | `execute_old_epoch` | Reserved evaluation |
| E5 | `transfer_credit` | Reserved evaluation |
| E6 | `ack_old_epoch` | Reserved evaluation |

## Checking modes and denominators

Reference schedules use acceptance/state conformance checks and property
audits. The main mutant-detection schedules use independent property audits
alone. Finite exploration also checks operation acceptance and successor state.

E5 and E6 fail nominal schedules, so they remain in the raw results but are
excluded from the qualified temporal analysis. E2 cannot activate its wrong-key
branch at capacity one. Four evaluation mutants across eleven eligible
mutant/configuration combinations and 50 seeds yield 550 trials per method.
These are not 550 distinct bugs. Budget-16 detection is 550/550 for model-derived
scheduling and 546/550 for random scheduling. At budget four, counts are
485/550 and 480/550, and the paired interval includes zero.

## Export exact table data

```bash
python scripts/verify_artifact.py
python scripts/export_paper_results.py
```

Exports are written to a fresh `outputs/paper-tables/` directory. The command
refuses an existing output directory; use `--output outputs/another-export`
to retain earlier exports. It uses only the Python standard library and does
not modify the recorded experiment files.
