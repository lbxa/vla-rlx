"""Shared analysis of the supplied DTP scores; provenance is in README.md."""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = Path(__file__).resolve().parent
METHODS = ["Base", "RL_TD3", "RL_SAC", "RL_PPO", "Res_TD3", "Res_SAC", "Res_PPO"]
TASKS = {
    "rubix-stack-v1", "bus-table-easy-v1", "bus-table-medium-v1",
    "bus-table-hard-v1", "close-bottle-lid-v1", "erase-whiteboard-v1",
    "close-french-press-v1",
}
PROVENANCE_NOTICE = (
    "Input scores are not reconciled with the thesis appendix. "
    "Conditions follow the manuscript protocol, not verified raw logs. "
    "95% t intervals do not measure variation across independent training runs. "
    "Transfer-gap intervals assume matching trial numbers are paired. See results/README.md."
)


def calculate_ci(data: np.ndarray, confidence: float = 0.95) -> float:
    """Student-t interval half-width; undefined for fewer than two observations."""
    n = len(data)
    if n < 2:
        return np.nan
    se = np.std(data, ddof=1) / np.sqrt(n)
    return stats.t.ppf((1 + confidence) / 2, df=n - 1) * se


def load_trial_data(
    input_path: Path = DATA_DIR / "results.csv",
    conditions_path: Path = DATA_DIR / "trial_conditions.csv",
) -> pd.DataFrame:
    """Validate the seven-task table and attach the documented 5–5–10 protocol.

    Summary rows in the original CSV are retained on disk but never used as data.
    Condition labels are a transcription of the manuscript, not raw-log metadata.
    """
    df = pd.read_csv(input_path)
    required = {"Task", "Trial", *METHODS}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing score columns: {sorted(required - set(df.columns))}")
    summary = df["Task"].isin(["MP", "Gen", "Transfer Gap"]) & df["Trial"].isna()
    df = df.loc[~(df.isna().all(axis=1) | summary), ["Task", "Trial", *METHODS]].copy()
    trials = pd.to_numeric(df["Trial"], errors="raise")
    if trials.isna().any() or not trials.between(1, 20).all() or not (trials % 1 == 0).all():
        raise ValueError("Trial identifiers must be integers from 1 to 20")
    df["Trial"] = trials.astype(int)
    if set(df["Task"]) != TASKS:
        raise ValueError("Expected exactly the seven documented tasks")
    if df.duplicated(["Task", "Trial"]).any():
        raise ValueError("Duplicate task/trial rows")
    if not df.groupby("Task")["Trial"].count().eq(20).all():
        raise ValueError("Each task must contain all 20 trials")
    scores = df[METHODS].apply(pd.to_numeric, errors="raise")
    if not scores.isin([0.0, 0.25, 0.5, 0.75, 1.0]).all().all():
        raise ValueError("DTP scores must be one of 0, 0.25, 0.5, 0.75, 1; missing scores are invalid")
    df[METHODS] = scores.astype(float)

    conditions = pd.read_csv(conditions_path)
    if list(conditions.columns) != ["Trial", "Condition"]:
        raise ValueError("Condition table must have Trial,Condition columns")
    conditions = conditions.sort_values("Trial").reset_index(drop=True)
    if conditions["Trial"].tolist() != list(range(1, 21)):
        raise ValueError("Condition table must list each trial 1–20 exactly once")
    if conditions["Condition"].tolist() != ["ID"] * 5 + ["DP"] * 5 + ["OOD"] * 10:
        raise ValueError("Condition table disagrees with the documented ID/DP/OOD 5–5–10 protocol")
    return df.merge(conditions, on="Trial", validate="many_to_one", sort=False)


def summarize_results(df_trials: pd.DataFrame) -> pd.DataFrame:
    """Compute progress and OOD metrics using the historical interval convention.

    Transfer-gap intervals use trial-index differences; pairing remains unverified.
    N counts scores or trial-index differences, never independent training runs.
    """
    rows = []
    for task, group in df_trials.groupby("Task", sort=False):
        group = group.sort_values("Trial")
        ood = group[group["Condition"] == "OOD"]
        for method in METHODS:
            metrics = [
                ("MeanProgress", group[method].to_numpy(), "evaluation_rollout"),
                ("Generalization", ood[method].to_numpy(), "evaluation_rollout"),
            ]
            if method.startswith("Res_"):
                metrics.append((
                    "TransferGap", (ood[method] - ood["Base"]).to_numpy(),
                    "trial_index_difference_pairing_unverified",
                ))
            for metric, values, unit in metrics:
                rows.append({
                    "Task": task, "Metric": metric, "Method": method,
                    "Mean": np.mean(values), "CI_95": calculate_ci(values),
                    "N": len(values), "Unit": unit,
                })
    return pd.DataFrame(rows)
