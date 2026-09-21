# VLA-RLX

Research code and result analysis for **Real-World Reinforcement Learning for Vision-Language Robotic Manipulation**, Lucas Barbosa's undergraduate honours thesis (UNSW Sydney, 2025; supervisor: Will Midgley).

The research question is whether a learned action-space residual can improve a frozen vision-language-action policy on a low-cost SO-101 arm. The reported study compares a base policy, TD3/SAC/PPO trained without the base, and their residual variants across seven tabletop manipulation tasks using discretized task progress (DTP).

[Project page](https://vla.lbxa.net/) · [Thesis source](https://github.com/lbxa/vla-rlx-manuscript) · [Protocol and evidence status](docs/reproduction-status.md)

**Reproduction status:** the CPU-only path below recomputes the supplied CSV and figures. Full robot-experiment reproduction is incomplete. The CSV differs from the thesis appendix in **431 of 980 scores**, so these outputs must not be presented as reconciled thesis results. No scores have been changed to resolve this discrepancy.

## Start here: reproduce the supplied results analysis

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/getting-started/installation/). This path needs neither robot hardware nor a GPU, submodules, checkpoints, or model downloads. The first run needs network access to install the dependencies pinned in `results/uv.lock`.

From the repository root:

```sh
uv run --locked --project results python results/main.py
uv run --locked --project results python results/plots.py
uv run --locked --project results python -m unittest discover -s results -p 'test_*.py'
```

The scripts validate 140 task/trial rows (seven tasks × 20 trials, with seven method scores each). Expected outputs:

- `results/reproduced/results_with_ci.csv`: 119 metric rows, including means, 95% t interval half-widths, observation counts, and observation units.
- `results/reproduced/Plots/`: eight figures, each in PNG, PDF, and SVG format.
- Console output identifying the unresolved provenance and interval assumptions.

For a numerical check, `rubix-stack-v1 / Base / MeanProgress` is **0.2875**, with a 95% t interval half-width of approximately **0.102389** over **20 evaluation scores**. This is mean progress, not a 28.75% binary success rate. The [analysis README](results/README.md) defines all metrics, interval assumptions, input validation, and output options. Existing CSVs and plot directories are preserved by the default commands.

## Where to inspect the implementation

The parent repository combines forked robot/model libraries with analysis and presentation files. It does not claim authorship of the upstream libraries.

| Component | Files to inspect | Role and status |
| --- | --- | --- |
| Analysis | [analysis.py](results/analysis.py), [main.py](results/main.py), [plots.py](results/plots.py) | Shared score validation, documented condition mapping, summary statistics, and plotting. |
| Front/top camera integration | [data configuration](gr00t/gr00t/experiment/data_config.py), [modality mapping](gr00t/examples/SO-100/so100_fronttop__modality.json) | Fork-specific `So100FrontTopCamDataConfig` and `so100_fronttop` mapping, present at the pinned GR00T revision. |
| Model serving and robot client | [inference service](gr00t/scripts/inference_service.py), [SO-100/SO-101 client](gr00t/examples/SO-100/eval_lerobot.py) | Native GR00T serving and observation/action conversion for robot control. These are integration entry points, not a complete seven-method evaluation harness. |
| LeRobot GR00T integration | [policy](lerobot/src/lerobot/policies/groot/modeling_groot.py), [training script](lerobot/src/lerobot/scripts/lerobot_gr00t_modal_train.py) | Policy integration and remote training configuration. Dataset/model names in scripts are not a versioned release manifest. |
| ADRL development | [implementation at `4edaa6d`](https://github.com/lbxa/lerobot/tree/4edaa6d30122929f6336b25e93176d0be796521f/src/lerobot/policies/adrl) | Gated distributional SAC residual actor, critic, buffer, configuration, and training loop. Present in the current local checkout, **absent from the parent's pinned LeRobot revision**. Its relationship to the reported TD3/SAC/PPO runs has not been established. |
| Robot hardware | [SO-101 documentation](so101/README.md) | Upstream hardware and assembly resources, included as a submodule. |
| Website | [website status](website/README.md) | This checkout contains a 12-task presentation; it does not match the seven-task project page inspected on 4 September 2026. Its relationship to the deployed source revision has not been established. |

## Pinned dependencies

The following gitlink revisions are recorded by the parent repository, independently of which branch a local submodule has checked out:

| Submodule | Repository | Pinned commit |
| --- | --- | --- |
| `gr00t` | [lbxa/gr00t](https://github.com/lbxa/gr00t) | `8810e55cace8b16b8b33680a842fe4290ca511a2` |
| `lerobot` | [lbxa/lerobot](https://github.com/lbxa/lerobot) | `4b83fecacfbfc93ee2ff5fb8826c2b59f946539d` |
| `so101` | [lbxa/so101](https://github.com/lbxa/so101) | `aec17bbc256d1a7342d53aaa4950595d4c30b40d` |

For a fresh checkout with GitHub SSH access:

```sh
git clone --recurse-submodules git@github.com:lbxa/vla-rlx.git
cd vla-rlx
git submodule status
```

The submodule URLs in [.gitmodules](.gitmodules) use SSH. For a fresh clone over HTTPS:

```sh
git -c url.https://github.com/.insteadOf=git@github.com: clone --recurse-submodules https://github.com/lbxa/vla-rlx.git
```

Inspect recorded pins with `git ls-tree HEAD gr00t lerobot so101`. A leading `+` in `git submodule status` means the local checkout differs from the parent pin. At the documentation audit, local GR00T was `a7af7bee6b641cc7698883cdf13e133d0016058e` and local LeRobot was `4edaa6d30122929f6336b25e93176d0be796521f`; these existing checkouts and the parent pins were left unchanged.

## Hardware evaluation and asset availability

Physical evaluation requires the SO-101 arm, calibration, front/top cameras, task objects, a compatible CUDA inference/training environment, and task-specific checkpoints and normalization metadata. Start by inspecting the pinned [GR00T setup](gr00t/README.md), [SO-100/SO-101 integration](gr00t/examples/SO-100/README.md), and [LeRobot documentation](lerobot/README.md).

This repository does **not yet provide a verified end-to-end command** for rerunning all seven reported methods. In particular:

- The analysis CSV is available, but original per-rollout logs/video IDs and condition annotations have not been located in the inspected sources.
- No complete, versioned manifest maps each result to a dataset revision, base checkpoint, residual checkpoint, training configuration, seed, and evaluation command. Availability of assets named by scripts has not been verified.
- The manuscript reports one training run per method–task pair and 20 evaluation rollouts. Exact training interaction budgets remain unverified; an evaluation rollout count is not a training budget.
- The historical [inference fix note](INFERENCE_FIX_SUMMARY.md) references an adapter that is absent at the inspected revisions. Native GR00T and LeRobot checkpoint formats must be matched to their respective loaders.

See the [evidence reconciliation record](docs/reproduction-status.md) for the documented trial table, source revisions, concrete discrepancies, and the records needed to complete physical reproduction.

## Research status and citation

The citation below follows the **undergraduate honours thesis** citation on the project page. Any subsequent submission, acceptance, or publication status has not been verified in this repository audit.

```bibtex
@misc{barbosa2025realworldrl,
  author = {Barbosa, Lucas},
  title = {Real-World Reinforcement Learning for Vision-Language Robotic Manipulation},
  year = {2025},
  howpublished = {Undergraduate Honours thesis, UNSW Sydney},
  note = {Supervisor: Will Midgley}
}
```
