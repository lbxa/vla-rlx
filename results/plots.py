"""
Publication-quality plots for Residual RL experimental results.
Generates report-style charts with 95% CI error bars.
"""

import argparse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from analysis import (DATA_DIR, PROVENANCE_NOTICE, calculate_ci, load_trial_data, summarize_results)

# ============================================================================
# STYLE CONFIGURATION
# ============================================================================

# Core semantic palette
PAPER = "#f7f6f2"
INK = "#111111"
MUTED = "#6b6761"
RULE = "#d8d4cc"
GRID = "#e8e4dc"
ACCENT = "#3d78b8"

METHOD_ORDER = ["Base", "RL_TD3", "RL_SAC", "RL_PPO", "Res_TD3", "Res_SAC", "Res_PPO"]
RESIDUAL_METHODS = ["Res_TD3", "Res_SAC", "Res_PPO"]
ALGORITHMS = ["TD3", "SAC", "PPO"]

METHOD_COLORS = {
    "Base": "#191919",
    "RL_TD3": "#c8c3ba",
    "RL_SAC": "#aaa49a",
    "RL_PPO": "#ddd8d0",
    "Res_TD3": "#6fa8dc",
    "Res_SAC": "#3d78b8",
    "Res_PPO": "#1f4e8c",
}

# Method display names
METHOD_LABELS = {
    "Base": "Base",
    "RL_TD3": "RL TD3",
    "RL_SAC": "RL SAC",
    "RL_PPO": "RL PPO",
    "Res_TD3": "Res TD3",
    "Res_SAC": "Res SAC",
    "Res_PPO": "Res PPO",
}

# Task display names (cleaner)
TASK_LABELS = {
    "rubix-stack-v1": "Rubik's Stack",
    "bus-table-easy-v1": "Bus Table\n(Easy)",
    "bus-table-medium-v1": "Bus Table\n(Medium)",
    "bus-table-hard-v1": "Bus Table\n(Hard)",
    "close-bottle-lid-v1": "Close Bottle\nLid",
    "erase-whiteboard-v1": "Erase\nWhiteboard",
    "close-french-press-v1": "Close French\nPress",
}


def setup_style():
    """Configure matplotlib for a neutral technical-report aesthetic."""
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Inter",
                "Helvetica Neue",
                "Arial",
                "DejaVu Sans",
                "sans-serif",
            ],
            "font.size": 10,
            "axes.titlesize": 15,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "axes.titleweight": "normal",
            "figure.dpi": 160,
            "savefig.dpi": 320,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.08,
            "savefig.facecolor": PAPER,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "axes.linewidth": 0.8,
            "axes.edgecolor": RULE,
            "axes.labelcolor": MUTED,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.axisbelow": True,
            "axes.grid": False,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "grid.alpha": 1.0,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "legend.frameon": False,
        }
    )


def style_axis(
    ax: plt.Axes,
    title: str,
    subtitle: str | None = None,
    ylabel: str | None = None,
    xlabel: str | None = None,
    ylim: tuple[float, float] | None = None,
) -> None:
    """Apply shared axis styling used across all figures."""
    title_pad = 24 if subtitle else 14
    ax.set_title(title, loc="left", color=INK, fontweight="normal", pad=title_pad)

    if subtitle:
        ax.text(
            0.0,
            1.01,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=9,
            color=MUTED,
        )

    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, labelpad=8)
    if xlabel:
        ax.set_xlabel(xlabel, color=MUTED, labelpad=8)
    if ylim:
        ax.set_ylim(*ylim)

    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.grid(axis="x", visible=False)

    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(RULE)
        ax.spines[spine].set_linewidth(0.8)

    ax.tick_params(axis="x", colors=MUTED, length=0, pad=8)
    ax.tick_params(axis="y", colors=MUTED, length=0, pad=6)


def add_rule(fig: plt.Figure) -> None:
    """No-op: top divider disabled based on visual feedback."""
    return


def add_value_labels(
    ax: plt.Axes,
    bars,
    values: list[float],
    errors: list[float] | None = None,
    fmt: str = "score",
) -> None:
    """Place small value labels above bars and optional error bars."""
    if errors is None:
        errors = [0.0] * len(values)

    y_min, y_max = ax.get_ylim()
    offset = (y_max - y_min) * 0.018

    for bar, value, error in zip(bars, values, errors):
        if fmt == "gap":
            label = f"{value:+.2f}"
        elif fmt == "percent":
            label = f"{value:+.0f}%"
        else:
            label = f"{value:.2f}"

        x = bar.get_x() + (bar.get_width() / 2)
        y = bar.get_height() + error + offset
        ax.text(x, y, label, ha="center", va="bottom", fontsize=8, color=INK)


def save_plot(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    """Save plot to PNG/PDF/SVG and close figure."""
    if stem.startswith(("04_", "05_")):
        units = "rollout scores (n=20 all trials; n=10 OOD)"
    elif stem.startswith("08_"):
        units = "OOD rollout scores (n=10)"
    else:
        units = "task means (n=7)"
    fig.text(
        0.01, -0.015,
        f"Supplied CSV; not reconciled with thesis appendix. 95% t intervals across {units}.\n"
        "Conditions follow the manuscript protocol; variation across training runs is not estimated.",
        ha="left", va="top", fontsize=7, color=MUTED,
    )
    for ext in ("png", "pdf", "svg"):
        fig.savefig(output_dir / f"{stem}.{ext}")
    plt.close(fig)
    print(f"✓ Saved: {stem}")


def load_and_process_data(
    input_path: Path = DATA_DIR / "results.csv",
    conditions_path: Path = DATA_DIR / "trial_conditions.csv",
):
    """Use the same validated data and statistics as the CSV exporter."""
    trials = load_trial_data(input_path, conditions_path)
    return summarize_results(trials).rename(columns={"CI_95": "CI"}), trials


def plot_overall_comparison(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 1: Overall performance comparison across all tasks.
    Shows Mean Progress averaged across all 7 tasks.
    """
    fig, ax = plt.subplots(figsize=(9.5, 5.6), constrained_layout=True)

    mp_data = df_stats[df_stats["Metric"] == "MeanProgress"]

    agg_means = []
    agg_cis = []
    for method in METHOD_ORDER:
        method_data = mp_data[mp_data["Method"] == method]
        means = method_data["Mean"].values
        agg_means.append(np.mean(means))
        agg_cis.append(calculate_ci(means))

    x = np.arange(len(METHOD_ORDER))

    bars = ax.bar(
        x,
        agg_means,
        width=0.64,
        color=[METHOD_COLORS[m] for m in METHOD_ORDER],
        edgecolor=RULE,
        linewidth=0.6,
        zorder=2,
    )

    ax.errorbar(
        x,
        agg_means,
        yerr=agg_cis,
        fmt="none",
        color=MUTED,
        ecolor=MUTED,
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=3,
    )

    style_axis(
        ax,
        title="Overall task progress",
        subtitle="Mean progress across seven real-world manipulation tasks.",
        ylabel="Mean task progress",
        ylim=(0, 1.08),
    )
    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS[m] for m in METHOD_ORDER], rotation=20, ha="right")

    baseline = agg_means[0]
    ax.axhline(
        y=baseline,
        color=INK,
        linestyle=(0, (3, 3)),
        linewidth=1.0,
        alpha=0.45,
        zorder=1,
    )
    ax.text(
        len(METHOD_ORDER) - 0.35,
        baseline + 0.012,
        "base policy",
        ha="right",
        va="bottom",
        fontsize=8,
        color=MUTED,
    )

    add_value_labels(ax, bars, agg_means, errors=agg_cis, fmt="score")
    add_rule(fig)
    save_plot(fig, output_dir, "01_overall_mean_progress")


def plot_generalization_comparison(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 2: Generalization scores (OOD performance, trials 11-20).
    """
    fig, ax = plt.subplots(figsize=(9.5, 5.6), constrained_layout=True)

    gen_data = df_stats[df_stats["Metric"] == "Generalization"]

    agg_means = []
    agg_cis = []
    for method in METHOD_ORDER:
        method_data = gen_data[gen_data["Method"] == method]
        means = method_data["Mean"].values
        agg_means.append(np.mean(means))
        agg_cis.append(calculate_ci(means))

    x = np.arange(len(METHOD_ORDER))

    bars = ax.bar(
        x,
        agg_means,
        width=0.64,
        color=[METHOD_COLORS[m] for m in METHOD_ORDER],
        edgecolor=RULE,
        linewidth=0.6,
        zorder=2,
    )

    ax.errorbar(
        x,
        agg_means,
        yerr=agg_cis,
        fmt="none",
        color=MUTED,
        ecolor=MUTED,
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=3,
    )

    style_axis(
        ax,
        title="Generalization under distribution shift",
        subtitle="OOD performance on trials 11–20.",
        ylabel="Generalization score ($J_{gen}$)",
        ylim=(0, 1.08),
    )
    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS[m] for m in METHOD_ORDER], rotation=20, ha="right")

    baseline = agg_means[0]
    ax.axhline(
        y=baseline,
        color=INK,
        linestyle=(0, (3, 3)),
        linewidth=1.0,
        alpha=0.45,
        zorder=1,
    )
    ax.text(
        len(METHOD_ORDER) - 0.35,
        baseline + 0.012,
        "base policy",
        ha="right",
        va="bottom",
        fontsize=8,
        color=MUTED,
    )

    add_value_labels(ax, bars, agg_means, errors=agg_cis, fmt="score")
    add_rule(fig)
    save_plot(fig, output_dir, "02_generalization_comparison")


def plot_transfer_gap(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 3: Transfer Gap - the explicit benefit of Residual RL over baseline.
    """
    fig, ax = plt.subplots(figsize=(6.8, 5.2), constrained_layout=True)

    methods = RESIDUAL_METHODS
    tg_data = df_stats[df_stats["Metric"] == "TransferGap"]

    agg_means = []
    agg_cis = []
    for method in methods:
        method_data = tg_data[tg_data["Method"] == method]
        means = method_data["Mean"].values
        agg_means.append(np.mean(means))
        agg_cis.append(calculate_ci(means))

    x = np.arange(len(methods))
    colors = [METHOD_COLORS[m] for m in methods]

    bars = ax.bar(
        x,
        agg_means,
        width=0.56,
        color=colors,
        edgecolor=RULE,
        linewidth=0.6,
        zorder=2,
    )
    ax.errorbar(
        x,
        agg_means,
        yerr=agg_cis,
        fmt="none",
        color=MUTED,
        ecolor=MUTED,
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=3,
    )

    top = max(np.array(agg_means) + np.array(agg_cis))
    style_axis(
        ax,
        title="Residual transfer gap",
        subtitle="Improvement over the frozen base policy in OOD trials.",
        ylabel="Transfer gap ($\\Delta_{gen}$)",
        ylim=(0, max(0.2, top + 0.08)),
    )
    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS[m] for m in methods])
    ax.axhline(y=0, color=RULE, linewidth=0.8, zorder=1)

    add_value_labels(ax, bars, agg_means, errors=agg_cis, fmt="gap")
    add_rule(fig)
    save_plot(fig, output_dir, "03_transfer_gap")


def plot_per_task_breakdown(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 4: Per-task breakdown showing Base vs Best Residual RL.
    """
    fig, ax = plt.subplots(figsize=(9.5, 5.6), constrained_layout=True)

    tasks = list(TASK_LABELS.keys())
    mp_data = df_stats[df_stats["Metric"] == "MeanProgress"]

    base_means = []
    base_cis = []
    best_res_means = []
    best_res_cis = []

    for task in tasks:
        task_data = mp_data[mp_data["Task"] == task]

        # Base performance
        base_row = task_data[task_data["Method"] == "Base"].iloc[0]
        base_means.append(base_row["Mean"])
        base_cis.append(base_row["CI"])

        # Best residual method
        res_data = task_data[task_data["Method"].str.startswith("Res_")]
        best_idx = res_data["Mean"].idxmax()
        best_row = res_data.loc[best_idx]
        best_res_means.append(best_row["Mean"])
        best_res_cis.append(best_row["CI"])

    x = np.arange(len(tasks))
    width = 0.34

    ax.bar(
        x - width / 2,
        base_means,
        width,
        label="Base",
        color=METHOD_COLORS["Base"],
        edgecolor=RULE,
        linewidth=0.6,
        zorder=2,
    )
    ax.bar(
        x + width / 2,
        best_res_means,
        width,
        label="Best residual",
        color=ACCENT,
        edgecolor=RULE,
        linewidth=0.6,
        zorder=2,
    )

    ax.errorbar(
        x - width / 2,
        base_means,
        yerr=base_cis,
        fmt="none",
        color=MUTED,
        ecolor=MUTED,
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=3,
    )
    ax.errorbar(
        x + width / 2,
        best_res_means,
        yerr=best_res_cis,
        fmt="none",
        color=MUTED,
        ecolor=MUTED,
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=3,
    )

    top = max(max(base_means), max(np.array(best_res_means) + np.array(best_res_cis)))
    style_axis(
        ax,
        title="Per-task improvement",
        subtitle="Frozen base policy compared against the best residual policy per task.",
        ylabel="Mean task progress",
        ylim=(0, max(1.05, top + 0.12)),
    )
    ax.set_xticks(x)
    ax.set_xticklabels([TASK_LABELS[t] for t in tasks], rotation=22, ha="right")
    ax.legend(loc="upper left", frameon=False, fontsize=8)

    y_min, y_max = ax.get_ylim()
    y_offset = (y_max - y_min) * 0.015
    for i, (base, best, ci) in enumerate(zip(base_means, best_res_means, best_res_cis)):
        if base > 0:
            improvement = ((best - base) / base) * 100
            if improvement >= 5:
                ax.text(
                    x[i] + width / 2,
                    best + ci + y_offset,
                    f"+{improvement:.0f}%",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color=ACCENT,
                )

    add_rule(fig)
    save_plot(fig, output_dir, "04_per_task_breakdown")


def plot_residual_rl_methods_comparison(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 5: Comparison of the three Residual RL algorithms across tasks.
    """
    fig, axes = plt.subplots(
        1, 2, figsize=(13, 5.6), sharey=True, constrained_layout=True
    )

    tasks = list(TASK_LABELS.keys())
    methods = RESIDUAL_METHODS
    colors = [METHOD_COLORS[m] for m in methods]
    y_top = 0.0

    for ax, metric, title in zip(
        axes,
        ["MeanProgress", "Generalization"],
        ["Residual methods: mean progress", "Residual methods: OOD progress"],
    ):
        metric_data = df_stats[df_stats["Metric"] == metric]

        x = np.arange(len(tasks))
        width = 0.25

        for i, (method, color) in enumerate(zip(methods, colors)):
            means = []
            cis = []
            for task in tasks:
                row = metric_data[
                    (metric_data["Task"] == task) & (metric_data["Method"] == method)
                ].iloc[0]
                means.append(row["Mean"])
                cis.append(row["CI"])

            offset = (i - 1) * width
            ax.bar(
                x + offset,
                means,
                width,
                label=METHOD_LABELS[method],
                color=color,
                edgecolor=RULE,
                linewidth=0.5,
                zorder=2,
            )
            ax.errorbar(
                x + offset,
                means,
                yerr=cis,
                fmt="none",
                color=MUTED,
                ecolor=MUTED,
                elinewidth=0.9,
                capsize=3,
                capthick=0.9,
                zorder=3,
            )
            y_top = max(y_top, max(np.array(means) + np.array(cis)))

        style_axis(
            ax,
            title=title,
            ylabel="Score" if metric == "MeanProgress" else None,
            ylim=(0, max(1.2, y_top + 0.08)),
        )
        ax.set_xticks(x)
        ax.set_xticklabels([TASK_LABELS[t] for t in tasks], rotation=22, ha="right")

    axes[0].legend(loc="upper left", frameon=False, fontsize=8)
    add_rule(fig)
    save_plot(fig, output_dir, "05_residual_rl_comparison")


def plot_rl_vs_residual_rl(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 6: Direct comparison of RL vs Residual RL (same algorithm).
    Shows that residual RL consistently outperforms pure RL.
    """
    fig, ax = plt.subplots(figsize=(9.5, 5.6), constrained_layout=True)

    gen_data = df_stats[df_stats["Metric"] == "Generalization"]

    x = np.arange(len(ALGORITHMS))
    width = 0.35

    rl_means = []
    rl_cis = []
    res_means = []
    res_cis = []

    for alg in ALGORITHMS:
        rl_method = f"RL_{alg}"
        res_method = f"Res_{alg}"

        rl_data = gen_data[gen_data["Method"] == rl_method]["Mean"].values
        res_data = gen_data[gen_data["Method"] == res_method]["Mean"].values

        rl_means.append(np.mean(rl_data))
        rl_cis.append(calculate_ci(rl_data))
        res_means.append(np.mean(res_data))
        res_cis.append(calculate_ci(res_data))

    ax.bar(
        x - width / 2,
        rl_means,
        width,
        label="Pure RL",
        color=METHOD_COLORS["RL_SAC"],
        edgecolor=RULE,
        linewidth=0.6,
        zorder=2,
    )
    bars2 = ax.bar(
        x + width / 2,
        res_means,
        width,
        label="Residual RL",
        color=ACCENT,
        edgecolor=RULE,
        linewidth=0.6,
        zorder=2,
    )

    ax.errorbar(
        x - width / 2,
        rl_means,
        yerr=rl_cis,
        fmt="none",
        color=MUTED,
        ecolor=MUTED,
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=3,
    )
    ax.errorbar(
        x + width / 2,
        res_means,
        yerr=res_cis,
        fmt="none",
        color=MUTED,
        ecolor=MUTED,
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=3,
    )

    top = max(
        max(np.array(rl_means) + np.array(rl_cis)),
        max(np.array(res_means) + np.array(res_cis)),
    )
    style_axis(
        ax,
        title="Residual learning beats training from scratch",
        subtitle="Matched algorithm comparison between pure RL and residual RL.",
        ylabel="Generalization score ($J_{gen}$)",
        ylim=(0, max(0.95, top + 0.12)),
    )
    ax.set_xticks(x)
    ax.set_xticklabels(ALGORITHMS)
    ax.legend(loc="upper left", frameon=False)

    y_offset = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.018
    for bar, rl_mean, res_mean, res_ci in zip(bars2, rl_means, res_means, res_cis):
        ax.text(
            bar.get_x() + (bar.get_width() / 2),
            bar.get_height() + res_ci + y_offset,
            f"{(res_mean - rl_mean):+.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
            color=ACCENT,
        )

    add_rule(fig)
    save_plot(fig, output_dir, "06_rl_vs_residual_rl")


def plot_summary_hero(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 7: Hero summary plot - single striking visualization.
    Shows the key finding: Residual RL dramatically improves over baseline.
    """
    fig, ax = plt.subplots(figsize=(6.8, 5.2), constrained_layout=True)

    # Compare Base, Best Pure RL, Best Residual RL on Generalization
    gen_data = df_stats[df_stats["Metric"] == "Generalization"]

    categories = ["Base", "Best RL\n(SAC)", "Best Residual\n(SAC)"]
    methods = ["Base", "RL_SAC", "Res_SAC"]

    means = []
    cis = []
    for method in methods:
        data = gen_data[gen_data["Method"] == method]["Mean"].values
        means.append(np.mean(data))
        cis.append(calculate_ci(data))

    x = np.arange(len(categories))
    colors_hero = [
        METHOD_COLORS["Base"],
        METHOD_COLORS["RL_SAC"],
        METHOD_COLORS["Res_SAC"],
    ]

    bars = ax.bar(
        x,
        means,
        width=0.6,
        color=colors_hero,
        edgecolor=RULE,
        linewidth=0.6,
        zorder=2,
    )
    ax.errorbar(
        x,
        means,
        yerr=cis,
        fmt="none",
        color=MUTED,
        ecolor=MUTED,
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=3,
    )

    top = max(np.array(means) + np.array(cis))
    style_axis(
        ax,
        title="Summary OOD comparison",
        subtitle="Base policy, best pure RL, and best residual RL.",
        ylabel="Generalization score ($J_{gen}$)",
        ylim=(0, max(0.95, top + 0.14)),
    )
    ax.set_xticks(x)
    ax.set_xticklabels(categories)

    ax.axhline(
        y=means[0],
        color=INK,
        linestyle=(0, (3, 3)),
        alpha=0.45,
        linewidth=1.0,
        zorder=1,
    )
    ax.text(
        2.35,
        means[0] + 0.01,
        "base policy",
        ha="right",
        va="bottom",
        fontsize=8,
        color=MUTED,
    )

    add_value_labels(ax, bars, means, errors=cis, fmt="score")
    add_rule(fig)
    save_plot(fig, output_dir, "07_hero_summary")


def plot_task_difficulty_analysis(df_stats: pd.DataFrame, output_dir: Path):
    """
    Plot 8: Bus Table difficulty progression showing Res-RL maintains performance.
    """
    fig, ax = plt.subplots(figsize=(6.8, 5.2), constrained_layout=True)

    tasks = ["bus-table-easy-v1", "bus-table-medium-v1", "bus-table-hard-v1"]
    difficulty_labels = ["Easy", "Medium", "Hard"]

    gen_data = df_stats[df_stats["Metric"] == "Generalization"]

    methods = ["Base", "Res_SAC"]
    colors_diff = [METHOD_COLORS["Base"], METHOD_COLORS["Res_SAC"]]
    markers = ["o", "s"]

    x = np.arange(len(tasks))
    y_top = 0.0

    for method, color, marker in zip(methods, colors_diff, markers):
        means = []
        cis = []
        for task in tasks:
            row = gen_data[
                (gen_data["Task"] == task) & (gen_data["Method"] == method)
            ].iloc[0]
            means.append(row["Mean"])
            cis.append(row["CI"])

        label = "Base" if method == "Base" else "Res SAC"
        means_arr = np.array(means)
        cis_arr = np.array(cis)
        y_top = max(y_top, max(means_arr + cis_arr))

        ax.plot(
            x,
            means_arr,
            marker=marker,
            color=color,
            linewidth=1.8,
            markersize=5,
            label=label,
            zorder=3,
        )
        ax.errorbar(
            x,
            means_arr,
            yerr=cis_arr,
            fmt="none",
            color=color,
            linewidth=1.0,
            capsize=3,
            capthick=1.0,
            alpha=0.9,
            zorder=2,
        )
        ax.fill_between(
            x, means_arr - cis_arr, means_arr + cis_arr, color=color, alpha=0.12
        )

    style_axis(
        ax,
        title="Robustness to task difficulty",
        subtitle="Bus Table easy, medium, and hard OOD performance.",
        xlabel="Task difficulty",
        ylabel="Generalization score ($J_{gen}$)",
        ylim=(0, max(0.95, y_top + 0.14)),
    )
    ax.set_xticks(x)
    ax.set_xticklabels(difficulty_labels)
    ax.legend(loc="upper right", frameon=False)

    add_rule(fig)
    save_plot(fig, output_dir, "08_task_difficulty")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DATA_DIR / "results.csv")
    parser.add_argument("--conditions", type=Path, default=DATA_DIR / "trial_conditions.csv")
    parser.add_argument("--output-dir", type=Path, default=DATA_DIR / "reproduced/Plots")
    args = parser.parse_args()
    df_stats, _ = load_and_process_data(args.input, args.conditions)
    print(PROVENANCE_NOTICE)
    print(f"Input: {args.input.resolve()}; conditions: {args.conditions.resolve()}")
    setup_style()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("Generating Publication-Quality Plots")
    print("=" * 60 + "\n")

    # Generate all plots
    plot_overall_comparison(df_stats, output_dir)
    plot_generalization_comparison(df_stats, output_dir)
    plot_transfer_gap(df_stats, output_dir)
    plot_per_task_breakdown(df_stats, output_dir)
    plot_residual_rl_methods_comparison(df_stats, output_dir)
    plot_rl_vs_residual_rl(df_stats, output_dir)
    plot_summary_hero(df_stats, output_dir)
    plot_task_difficulty_analysis(df_stats, output_dir)

    print("\n" + "=" * 60)
    print(f"All plots saved to: {output_dir.absolute()}")
    print("Formats: PNG + PDF + SVG")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
