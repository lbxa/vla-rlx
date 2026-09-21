# Supplied DTP result analysis

This directory contains a score CSV, statistical analysis, plots, and a historical LaTeX results draft. **The CSV and thesis appendix disagree in 431 of 980 scores.** Outputs here reproduce the supplied CSV only. See [evidence and protocol sources](../docs/reproduction-status.md); original experiment logs are needed to reconcile them.

## Run

Use Python 3.12 and uv. From the repository root:

```sh
uv run --locked --project results python results/main.py
uv run --locked --project results python results/plots.py
uv run --locked --project results python -m unittest discover -s results -p 'test_*.py'
```

[`uv run --project`](https://docs.astral.sh/uv/reference/cli/#uv-run) selects the project environment while script paths remain relative to your working directory; `--locked` prevents lockfile updates. Dependencies are pinned by `uv.lock`. The scripts locate their default input files relative to their own directory, so `cd results` followed by `uv run --locked python main.py` works too.

No robot, GPU, or checkpoint is needed. The first installation may download Python and packages. Defaults write to `reproduced/`, preserving `results.csv`, the historical `results_with_ci.csv`, `Plots/`, and `plots-export/`.

Custom paths are supported:

```sh
uv run --locked --project results python results/main.py --output /tmp/vla-rlx-summary.csv
uv run --locked --project results python results/plots.py --output-dir /tmp/vla-rlx-plots
```

Both commands accept `--input` and `--conditions`; inputs must follow the documented seven-task schema and protocol. Use `--help` for defaults.

## Inputs and validation

`results.csv` contains seven tasks × 20 trial rows, with one DTP score for each of seven methods: 980 scores. Each method–task pair therefore has 20 evaluation scores. The manuscript describes one training run per pair; these are not 20 independently trained policies.

The loader ignores only blank rows and the embedded `MP`, `Gen`, and `Transfer Gap` summary rows. It recomputes all metrics from the trial rows. It rejects missing/duplicate trials, an incomplete task set, missing scores, invalid trial identifiers, and values outside the DTP ladder `{0, 0.25, 0.50, 0.75, 1}`.

`trial_conditions.csv` assigns ID to trials 1–5, DP to 6–10, and OOD to 11–20 **according to the manuscript protocol**. It is not a recovered experiment log. The shared loader validates this table; both analysis scripts select OOD by its condition label. The condition table cannot resolve the discrepancy between the two score sources.

## Metrics and uncertainty

| Output metric | Calculation per task and method | N / observation unit |
| --- | --- | --- |
| `MeanProgress` | Mean DTP across ID + DP + OOD. | 20 evaluation scores |
| `Generalization` | Mean DTP in the documented OOD block. | 10 evaluation scores |
| `TransferGap` | Mean residual-minus-base DTP in the OOD block; residual methods only. | 10 trial-index differences; pairing unverified |

Mean DTP is not binary success rate. If reporting binary success separately, count scores equal to 1 and divide by the number of evaluated rollouts; fractional progress must not be counted as a successful rollout.

`CI_95` is a **half-width**, calculated as `t(0.975, n−1) × sample_std(ddof=1) / sqrt(n)`. Report it as `Mean ± CI_95`, not as an interval endpoint. This preserves the historical calculation. The output adds `N` and `Unit` to make the observations explicit. A sample with fewer than two observations has an undefined half-width; a constant sample yields zero under this formula, which does not establish zero population uncertainty.

Per-task progress intervals are computed across 20 scores; OOD intervals across 10 scores. Per-task transfer-gap intervals use residual-minus-base differences at corresponding trial indices. That paired calculation is conditional on the indices representing meaningfully matched evaluations; the CSV alone does not establish this. The difference of means itself does not require pairing.

The aggregate plots apply the same t formula across **seven task means** (or seven task-level transfer gaps), with equal task weights. Per-task plots use the rollout-level intervals above. These intervals summarize different units and are not interchangeable. All-trial intervals also mix the three deliberately different condition blocks. Independence and sampling assumptions have not been checked against logs; none of these intervals estimates variability across independently trained seeds or establishes broad statistical significance across robot tasks.

## Expected outputs

- `reproduced/results_with_ci.csv`: 119 rows (7 tasks × [7 mean-progress + 7 generalization + 3 transfer-gap rows]). Columns: `Task,Metric,Method,Mean,CI_95,N,Unit`.
- `reproduced/Plots/01_...` through `08_...`: eight figures in PNG, PDF, and SVG, 24 files total.
- For `rubix-stack-v1`, Base has mean progress `0.2875`, half-width `0.1023891474`, and OOD progress `0.125`.

`results_section.tex` is a historical draft for a ClassicThesis document and is not generated by either script. Its introductory protocol wording is corrected to match the documented split, but its remaining numerical claims are not certified by this analysis. The complete manuscript source and its figure macros are maintained separately.
