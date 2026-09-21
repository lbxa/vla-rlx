# Reproduction and evidence reconciliation

Audit date: 4 September 2026. Scope: this checkout, its supplied analysis CSV, the sibling manuscript checkout, and the live project page. This is not an audit of raw experiment recordings or proof of physical replication.

## Trial conditions

The manuscript documents the following protocol. [trial_conditions.csv](../results/trial_conditions.csv) transcribes it for both the summary exporter and plots.

| Trial indices | Count per method–task pair | Documented condition |
| --- | --- | --- |
| 1–5 | 5 | ID: in-distribution initialization near the training configuration. |
| 6–10 | 5 | DP: dynamic perturbation, such as an object/arm disturbance during execution or an unstable initial state. |
| 11–20 | 10 | OOD: distribution shifts such as poses, lighting, clutter, or friction. |

**Evidence level: manuscript protocol, not verified raw-log labels.** The supplied CSV records no condition field, timestamp, rollout ID, checkpoint, or seed. The new condition table does not establish which perturbation actually occurred during a given rollout.

Sources at manuscript commit `f4a2b2254045981e9691f4a3acfe64ba99837348`:

- [Methodology.tex](https://github.com/lbxa/vla-rlx-manuscript/blob/f4a2b2254045981e9691f4a3acfe64ba99837348/Chapters/Methodology.tex), section `sec:method:trial_protocol`: defines the three blocks.
- [Results.tex](https://github.com/lbxa/vla-rlx-manuscript/blob/f4a2b2254045981e9691f4a3acfe64ba99837348/Chapters/Results.tex), opening paragraph: repeats the 5–5–10 split.
- [Appendix.tex](https://github.com/lbxa/vla-rlx-manuscript/blob/f4a2b2254045981e9691f4a3acfe64ba99837348/Chapters/Appendix.tex), `sec:appendix:results_monolith`: labels each task's rows ID, DP, and OOD.
- [Discussion.tex](https://github.com/lbxa/vla-rlx-manuscript/blob/f4a2b2254045981e9691f4a3acfe64ba99837348/Chapters/Discussion.tex): reports a single training run per method–task pair and 20 evaluation rollouts.

The [live project page](https://vla.lbxa.net/) agrees with this split in its protocol section, but calls trials 1–10 nominal in its results introduction. The local `results/results_section.tex` had the same nominal wording; it is now qualified to match the documented protocol. The sibling manuscript already uses 5–5–10 and was not edited.

Once original logs are available, verify each task/method/trial against its recording and condition before describing this split as empirically verified. Do not infer the condition from how high or low a score is.

## Score discrepancy: unresolved

Comparing each `(Task, Trial, Method)` in [results.csv](../results/results.csv) with the manuscript appendix yields **140 matching task/trial keys, 980 compared scores, and 431 differing scores**. Both sources contain seven tasks, 20 trials, and seven methods. Neither was selected as the authoritative experimental record, and neither score source was edited.

Examples for `rubix-stack-v1`, trial 1:

| Method | Supplied CSV | Manuscript appendix |
| --- | --- | --- |
| Base | 0.50 | 0.25 |
| RL_TD3 | 0.00 | 0.25 |
| RL_PPO | 0.00 | 0.25 |
| Res_TD3 | 0.50 | 0.75 |
| Res_PPO | 0.50 | 0.75 |

All new analysis outputs use the supplied CSV explicitly. Recomputing its numbers does not establish that it is the final experiment version. The historical prose in `results/results_section.tex` also needs a numerical review after the authoritative records are identified; regenerating figures alone does not update that prose.

Source SHA-256 hashes at inspection:

| Source | SHA-256 |
| --- | --- |
| `results/results.csv` | `31d4824f13696121486f99d01be9bea4fe5f80ad54423e7759d83547275423d6` |
| manuscript `Chapters/Appendix.tex` | `823e1dff2ea86e931f720492e90547dbf91f9d699ec0a3bedaee298c1695be50` |
| manuscript `Chapters/Methodology.tex` | `901eb56736fb5af49d40748e32b97969388660c115c12b110155a3bde3c9534e` |
| manuscript `Chapters/Discussion.tex` | `72157dbf4df36324c4f13968e3ab773a8c5e681ea078f8cdad7305530f170d27` |

## What remains necessary for physical reproduction

| Missing evidence | What it would establish |
| --- | --- |
| Original scoring sheets/logs and recording IDs | Which score table is authoritative; actual per-rollout conditions and DTP assignments. |
| Task/method → checkpoint, code commit, dataset revision, configuration and seed manifest | Which implementation and model produced each result. The later ADRL code cannot automatically be equated with the thesis's residual baselines. |
| Training step and episode logs | Physical interaction budgets for each method, separated from offline training, optimizer updates, and evaluation rollouts. Defaults in development scripts are not experiment records. |
| Trial pairing records | Whether residual-minus-base scores at matching trial numbers justify a paired interval. |
| Current project-page source revision | Where to correct the live results introduction and reconcile numerical claims. This checkout's `website/` describes 12 tasks and 30 trials, which does not match the inspected seven-task page. Its relationship to the deployed source revision has not been established. |

No site deployment, model training, robot motion, or submodule pin update was performed by this documentation/analysis fix.
